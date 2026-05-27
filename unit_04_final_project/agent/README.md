---
title: GAIA Unit 4 Agent
emoji: 🦇
colorFrom: indigo
colorTo: red
sdk: gradio
sdk_version: 5.0.0
app_file: app.py
hf_oauth: true
hf_oauth_expiration_minutes: 480
pinned: false
license: apache-2.0
tags:
- agent
- smolagents
- agents-course
- unit-4
- gaia
---

# Unit 4 — GAIA Level-1 Final Project

Gradio Space that fetches the 20 official GAIA-Level-1 questions from
`agents-course-unit4-scoring.hf.space`, runs a smolagents `CodeAgent` on
each, and submits the answers to the Students leaderboard.

## Agent

`CodeAgent` (Qwen 2.5-Coder-32B via HF Inference Providers) with:

| Tool | Purpose |
|------|---------|
| `web_search` (DDG) | Fetch external information. |
| `visit_webpage` | Read & strip a specific URL. |
| `python_interpreter` | Run sandboxed Python for math / parsing. |
| `download_task_file` | Pull files associated with a `task_id`. |
| `final_answer` | Emit the short, exact-match answer. |

`additional_authorized_imports` covers stdlib + `pandas` / `numpy` for
Level-1 spreadsheet-y questions.

## Output format reminder

The submit endpoint compares answers as **EXACT MATCH**. The agent's
system hint enforces:

- No `"FINAL ANSWER:"` prefix.
- Numbers as digits, no units unless asked.
- Lists comma-separated.
- Dates as the question requests.

## Deploy

```bash
# After cloning the Space repo:
huggingface-cli login
# upload via HfApi.upload_file or git push
```

Then click **Sign in with Hugging Face**, then **🚀 Run + Submit**. The
score and per-question transcript appear inline.

## Scoring tier

| Score | Status |
|-------|--------|
| < 30% | Try again — debug failure cases in the transcript. |
| ≥ 30% | 🎓 **Certificate of Excellence eligible** — claim at https://huggingface.co/spaces/agents-course/Unit4-Final-Certificate |
