---
title: Alfred - Gala Agent (Unit 3)
emoji: 🎩
colorFrom: indigo
colorTo: green
sdk: gradio
sdk_version: 5.0.0
app_file: app.py
pinned: false
license: apache-2.0
tags:
- agent
- smolagents
- agents-course
- unit-3
- rag
---

# Unit 3 — Gala Agent ("Alfred at the Wayne Gala")

Agentic-RAG smolagents `CodeAgent` over the official
[`agents-course/unit3-invitees`](https://huggingface.co/datasets/agents-course/unit3-invitees)
dataset. Implements the full multi-tool build from the unit in a single
`app.py`:

| Tool | What it does |
|------|--------------|
| `guest_info_retriever` | BM25 retrieval over the invitees dataset. |
| `web_search` (DDG) | Public web search for live context. |
| `visit_webpage` | Fetch + strip a specific URL. |
| `fireworks_weather` | Open-Meteo current weather for Gotham → go / no-go. |
| `hub_stats` | Most-downloaded model on the HF Hub for a given author/org. |
| `final_answer` | Terminal tool. |

## Sample prompts

- *"Tell me about our guest named 'Lady Ada Lovelace'."* → BM25 hit on the dataset.
- *"Which mathematicians are on the guest list?"* → BM25 filter on `relation`.
- *"Is the weather good enough for fireworks tonight?"* → `fireworks_weather`.
- *"What's the top model for the 'facebook' org on the Hub?"* → `hub_stats`.
- *"What's Ada Lovelace known for outside our database?"* → web_search + visit_webpage.

## Deploy

```bash
huggingface-cli upload VoicesColeby/Alfred-Gala-Unit3 . --repo-type space --include "*.py" "*.txt" "*.md"
```

Set `HF_TOKEN` as a Space secret (so the agent can use HF Inference Providers).
