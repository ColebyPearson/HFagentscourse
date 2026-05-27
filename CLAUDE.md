# HuggingFace AI Agents Course

## Project Overview
Hands-on work for the HuggingFace AI Agents Course — agent theory, smolagents/LlamaIndex/LangGraph frameworks, Agentic RAG, GAIA benchmark final project, plus three bonus units (function-calling fine-tune, observability, Pokémon agent).

Course URL: https://huggingface.co/learn/agents-course/unit0/introduction
GitHub source: https://github.com/huggingface/agents-course

## Certification
- **Fundamentals**: complete Unit 1.
- **Completion (Certificate of Excellence)**: Unit 1 + one use case + final challenge (GAIA leaderboard).

## Per-unit hands-on targets
- **Unit 1** — first smolagents-based agent.
- **Unit 2.1/2.2/2.3** — framework comparisons; small example agents.
- **Unit 3** — Agentic RAG "Gala Agent" (Gradio Space, optional).
- **Unit 4** — Agent that submits answers to the GAIA Level-1 benchmark + leaderboard PR.
- **Bonus 1** — Fine-tune `google/gemma-2-2b-it` (or similar) for function-calling using TRL.
- **Bonus 2** — Trace + evaluate the agent with Phoenix / OpenTelemetry / `evaluate`.
- **Bonus 3** — Pokémon battle agent using smolagents + showdown API.

## Reference stack
- `smolagents`, `llama-index`, `langgraph`, `langchain-core`
- `transformers`, `trl`, `peft`, `bitsandbytes` (Bonus 1)
- `huggingface_hub`, `datasets`, `gradio`
- `phoenix-evals` / `arize-phoenix` / `opentelemetry` (Bonus 2)

## Reference hardware
RTX 5060 Ti / 16 GB (same box as HF Audio, HF Smol Course, HF Context Course). Same lessons apply: `PYTHONUTF8=1` on Windows for TRL, explicit LoRA `target_modules` for PEFT 0.18+, `bitsandbytes` 0.49+ works on Windows, set `hub_model_id` explicitly so push lands at the intended repo.
