"""
Quick smoke test: load the base + LoRA adapter and generate one
function-calling response using the same chat template the model
saw at training time.
"""
from __future__ import annotations

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

BASE = "HuggingFaceTB/SmolLM2-1.7B-Instruct"
ADAPTER = "VoicesColeby/smollm2-1.7b-fc-lora"

SYSTEM = (
    "You are a function-calling AI model. You are provided with function "
    "signatures within <tools></tools> XML tags. You may call one or more "
    "functions to assist with the user query. Do not make assumptions about "
    "what values to plug into functions. Here are the available tools:\n"
    '<tools>[{"type": "function", "function": {"name": "get_stock_price", '
    '"description": "Get the current stock price for a company.", '
    '"parameters": {"type": "object", "properties": {"company": '
    '{"type": "string", "description": "Company name."}}, '
    '"required": ["company"]}}}]</tools>\n'
    "For each function call return a json object with function name and "
    "arguments within <tool_call></tool_call> XML tags. Show your reasoning "
    "inside <think>...</think> first."
)
USER = "What is the current stock price of Apple?"


def main() -> None:
    tok = AutoTokenizer.from_pretrained(BASE)
    base = AutoModelForCausalLM.from_pretrained(
        BASE, torch_dtype=torch.bfloat16, device_map="auto"
    )
    model = PeftModel.from_pretrained(base, ADAPTER)
    model.eval()

    msgs = [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": USER}]
    prompt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    inputs = tok(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        out = model.generate(
            **inputs, max_new_tokens=256, do_sample=False, temperature=0.0,
            pad_token_id=tok.eos_token_id,
        )
    print(tok.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=False))


if __name__ == "__main__":
    main()
