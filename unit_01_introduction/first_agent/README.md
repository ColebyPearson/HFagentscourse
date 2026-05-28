---
title: Alfred - HF Agents Course Unit 1
emoji: 🦇
colorFrom: indigo
colorTo: yellow
sdk: gradio
sdk_version: 5.0.0
app_file: app.py
python_version: "3.12"
pinned: false
license: apache-2.0
tags:
- agent
- smolagents
- agents-course
- unit-1
---

# Unit 1 — First Agent ("Alfred")

A working smolagents `CodeAgent` with five tools:

| Tool | Source |
|------|--------|
| `web_search` | `DuckDuckGoSearchTool()` (smolagents default) |
| `visit_webpage` | `VisitWebpageTool()` (smolagents default) |
| `get_current_time_in_timezone` | `@tool`-decorated, custom (pytz) |
| `convert_currency` | `@tool`-decorated, custom (exchangerate.host) |
| `final_answer` | `FinalAnswerTool()` (terminal) |

Run locally:

```bash
pip install -r requirements.txt
export HF_TOKEN=hf_...
python app.py
```

Deploying to a Space:

1. Create a new Gradio Space (or duplicate `agents-course/First_agent_template`).
2. Copy `app.py` + `requirements.txt` into the Space repo.
3. **Settings → Variables and Secrets → New Secret**: `HF_TOKEN` = your inference-enabled token.
4. Push. The Space will build, and its UI is launched by `GradioUI(agent).launch()`.

## Sample prompts that exercise each tool

- "What time is it right now in Tokyo and Paris?" → `get_current_time_in_timezone`
- "Convert 500 USD to EUR and to JPY." → `convert_currency`
- "What is smolagents and why does HuggingFace recommend it?" → `web_search` + `visit_webpage`
- "What's the time in New York and how many EUR is 1000 USD worth right now?" → mixed multi-step

## Notes / lessons applied

- `InferenceClientModel(model_id=...)` defaults to Qwen 2.5-Coder-32B. Override with the `AGENT_MODEL_ID` env var if you want a different one.
- `max_steps=6` is the safety hatch for the ReAct loop.
- The `final_answer` tool is **kept** in the tools list — without it the loop has no terminal action.
- The agent is shippable as-is to a Space (Gradio UI bundled via `GradioUI(agent).launch()`).
