# Bonus Unit 1. Fine-tuning an LLM for Function-calling

Official chapter URL base: https://huggingface.co/learn/agents-course/bonus-unit1/
NotebookLM source: [`notebooklm/bonus_01_function_calling.txt`](../notebooklm/bonus_01_function_calling.txt)

## Chapters (in order)

- **Introduction** — https://huggingface.co/learn/agents-course/bonus-unit1/introduction
- **What is Function Calling?** — https://huggingface.co/learn/agents-course/bonus-unit1/what-is-function-calling
- **Let's Fine-Tune your model for Function-calling** — https://huggingface.co/learn/agents-course/bonus-unit1/fine-tuning
- **Conclusion** — https://huggingface.co/learn/agents-course/bonus-unit1/conclusion

## Hands-on artifact

LoRA adapter trained on the Hermes function-calling-thinking dataset.

| | |
|--|--|
| Base model | `HuggingFaceTB/SmolLM2-1.7B-Instruct` (ungated) |
| Dataset | [`Jofthomas/hermes-function-calling-thinking-V1`](https://huggingface.co/datasets/Jofthomas/hermes-function-calling-thinking-V1) |
| Method | 4-bit NF4 + LoRA r=16, α=32, dropout=0.05 |
| Steps | 200 (~30–60 min on RTX 5060 Ti / 16 GB) |
| Output | [`VoicesColeby/smollm2-1.7b-fc-lora`](https://huggingface.co/VoicesColeby/smollm2-1.7b-fc-lora) |

### Why not Gemma-2-2b-it like the official bonus?

The canonical agents-course bonus unit uses `google/gemma-2-2b-it`, but
that repo is **manually gated** — the Hub requires clicking "agree" on
the license page. To avoid blocking on a manual approval step, this
artifact uses `HuggingFaceTB/SmolLM2-1.7B-Instruct` (ungated, ChatML
chat template). The training mechanics are identical: change
`BASE_MODEL` in `train/train_fc.py` and re-run if/when Gemma access is
granted.

### Run it yourself

```powershell
$env:PYTHONUTF8 = "1"          # Windows: avoid TRL cp1252 .jinja read errors
pip install -r ..\requirements.txt
python train\train_fc.py
```

Smoke test inference once the adapter is on the Hub:

```powershell
python train\infer.py
```

### Lessons re-applied from earlier courses

- `PYTHONUTF8=1` on Windows so TRL's `.jinja` reads don't fail with cp1252.
- Explicit `LORA_TARGET_MODULES = [...]` — PEFT 0.18+ requires it.
- `hub_model_id=HUB_REPO` explicitly set on the `SFTConfig`, else
  `push_to_hub` lands at the basename of `output_dir`.
- `gradient_checkpointing=True` + `use_cache=False` on the model for memory.
- `bf16=True` is fine on RTX 5060 Ti (Ada / sm_89).

## Status

- [x] Read all chapters (notebooklm + per-section MDX)
- [ ] Run `train/train_fc.py` (currently in flight)
- [ ] Verify `VoicesColeby/smollm2-1.7b-fc-lora` on the Hub
- [ ] Quick smoke test via `train/infer.py`
