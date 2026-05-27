"""
Bonus Unit 1 — Fine-tune an LLM for function-calling using LoRA.

Base model:  HuggingFaceTB/SmolLM2-1.7B-Instruct  (ungated; ChatML chat template)
Dataset:     Jofthomas/hermes-function-calling-thinking-V1  (Hermes-style
             multi-turn conversations using <think>...</think>, <tool_call>...
             </tool_call>, and <tool_response>...</tool_response> markers)

Why not Gemma-2-2b-it? The agents-course bonus unit canonically uses
google/gemma-2-2b-it, but it's a manually-gated model. SmolLM2-1.7B-Instruct
is functionally equivalent for the lesson (the function-calling adapter
mechanics are identical) and avoids the manual approval step.

Output:      LoRA adapter pushed to VoicesColeby/smollm2-1.7b-fc-lora.

Runs on a single 16 GB GPU (RTX 5060 Ti) at ~30-60 min for 200 steps.

Lessons applied (from HF Audio / smol-course / context-course):
- PYTHONUTF8=1 on Windows (set by the parent runner).
- Explicit LoRA target_modules (PEFT 0.18+ requires it for SmolLM3-style archs).
- hub_model_id set explicitly so push_to_hub lands at the intended repo.
- bf16 on Ampere+/Ada+ for speed.
- 4-bit NF4 quant via bitsandbytes for memory.
"""
from __future__ import annotations

import os
import warnings

import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
)
from trl import SFTConfig, SFTTrainer

warnings.filterwarnings("ignore", category=UserWarning, module="bitsandbytes")

# --- Config -----------------------------------------------------------------

BASE_MODEL = "HuggingFaceTB/SmolLM2-1.7B-Instruct"
DATASET_ID = "Jofthomas/hermes-function-calling-thinking-V1"
OUTPUT_DIR = r"C:\Repos\HF Agents Course\bonus_01_function_calling\train\runs\fc_lora"
HUB_REPO = "VoicesColeby/smollm2-1.7b-fc-lora"

MAX_SEQ_LEN = 2048
MAX_STEPS = 200          # ~30-60 min on a 16 GB Ampere/Ada GPU
PER_DEVICE_BATCH = 1
GRAD_ACCUM = 4           # effective batch ~4
LEARNING_RATE = 2e-4
LR_SCHEDULER = "cosine"
WARMUP_RATIO = 0.05

LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
# PEFT 0.18+ requires explicit target modules. These are SmolLM2/Llama-style
# linear projection names that show up in `print(model)`.
LORA_TARGET_MODULES = [
    "q_proj", "k_proj", "v_proj", "o_proj",
    "gate_proj", "up_proj", "down_proj",
]


# --- Dataset preparation ----------------------------------------------------

ROLE_MAP = {"human": "user", "model": "assistant", "system": "system", "tool": "tool"}


def normalize_conversation(example: dict) -> dict:
    """Hermes uses `human`/`model`/`tool`/`system`. Map to OpenAI-style roles
    expected by the SmolLM2 chat template, and stitch the `tool` turns into
    the prior assistant turn as tool_responses to keep ChatML simple.
    """
    msgs = []
    for m in example["conversations"]:
        role = ROLE_MAP.get(m["role"], m["role"])
        if role == "tool":
            # ChatML on SmolLM2 has no canonical tool role — fold the tool
            # output into the next assistant turn's preamble. We treat
            # consecutive tool outputs as their own assistant-side observation
            # message tagged with <tool_response> markers (already present in
            # the dataset content).
            msgs.append({"role": "user", "content": m["content"]})
        else:
            msgs.append({"role": role, "content": m["content"]})
    return {"messages": msgs}


def main() -> None:
    print(f"== Loading dataset {DATASET_ID} ==")
    raw = load_dataset(DATASET_ID, split="train")
    print(f"  total examples: {len(raw)}")

    # Keep a small slice for a single epoch -> fast training. 4000 is plenty
    # for the LoRA to learn the <think>/<tool_call>/<tool_response> idiom.
    ds = raw.shuffle(seed=42).select(range(min(len(raw), 4000)))
    ds = ds.map(normalize_conversation, remove_columns=ds.column_names)
    print(f"  using:           {len(ds)} examples")
    print(f"  sample msgs:     {[m['role'] for m in ds[0]['messages']]}")

    print(f"\n== Loading tokenizer {BASE_MODEL} ==")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"\n== Loading model {BASE_MODEL} (4-bit NF4) ==")
    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb,
        device_map="auto",
        torch_dtype=torch.bfloat16,
    )
    model.config.use_cache = False
    model = prepare_model_for_kbit_training(model)

    print("\n== Wrapping with LoRA ==")
    lora = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        target_modules=LORA_TARGET_MODULES,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora)
    model.print_trainable_parameters()

    print(f"\n== Configuring SFTTrainer (max_steps={MAX_STEPS}) ==")
    cfg = SFTConfig(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=PER_DEVICE_BATCH,
        gradient_accumulation_steps=GRAD_ACCUM,
        max_steps=MAX_STEPS,
        learning_rate=LEARNING_RATE,
        lr_scheduler_type=LR_SCHEDULER,
        warmup_ratio=WARMUP_RATIO,
        logging_steps=10,
        save_steps=100,
        save_total_limit=2,
        bf16=True,
        gradient_checkpointing=True,
        max_length=MAX_SEQ_LEN,
        packing=False,
        report_to="none",
        push_to_hub=True,
        hub_model_id=HUB_REPO,         # <-- explicit, learned the hard way
        hub_strategy="end",
        dataset_text_field=None,        # use messages-style formatting
    )

    trainer = SFTTrainer(
        model=model,
        args=cfg,
        train_dataset=ds,
        processing_class=tokenizer,
    )

    print("\n== Training ==")
    trainer.train()

    print("\n== Saving final adapter locally ==")
    trainer.save_model(OUTPUT_DIR)

    print("\n== Pushing to Hub ==")
    trainer.push_to_hub(commit_message="LoRA adapter for function-calling")

    print(f"\nDone. Adapter -> https://huggingface.co/{HUB_REPO}")


if __name__ == "__main__":
    main()
