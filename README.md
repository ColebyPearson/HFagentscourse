# HuggingFace AI Agents Course

Working through the [HuggingFace AI Agents Course](https://huggingface.co/learn/agents-course/unit0/introduction) — theory + practice of AI agents using smolagents, LlamaIndex, and LangGraph, capped by a GAIA-benchmark final project.

## Course Units

| Unit | Topic | Quizzes | Hands-on |
|------|-------|:---:|:---:|
| 0 | Welcome / Onboarding / Discord 101 | — | — |
| Live 1 | How the course works / Q&A | — | — |
| 1 | Introduction to Agents (Thought-Action-Observation, ReAct, tools, smolagents tutorial) | 3 | ✅ first agent |
| 2 | Frameworks intro | — | — |
| 2.1 | smolagents (code agents, tool calling, retrieval, multi-agent, vision) | 3 | — |
| 2.2 | LlamaIndex (components, tools, agents, workflows) | 2 | — |
| 2.3 | LangGraph (building blocks, document-analysis graph) | 1 | — |
| 3 | Use Case — Agentic RAG (Gala Agent over guest stories) | — | ✅ |
| 4 | Final Project — GAIA benchmark + leaderboard | — | ✅ certificate |
| Bonus 1 | Fine-tuning an LLM for Function-Calling | — | ✅ fine-tune |
| Bonus 2 | Agent Observability and Evaluation | 1 | — |
| Bonus 3 | Agents in Games — Pokémon Battle Agent | — | ✅ |

## Certification

| Level | Requirement |
|-------|-------------|
| **Fundamentals** | Complete Unit 1 |
| **Completion (Certificate of Excellence)** | Complete Unit 1 + one use case + the final challenge (GAIA leaderboard) |

## Structure

- `unit_*/` — per-unit work (agent code, hands-on artifacts, fine-tuned model links).
- `notebooklm/unit_*.txt` — concatenated unit text from the official `.mdx` source, formatted for [NotebookLM](https://notebooklm.google.com/) (audio overviews + flashcards).
- `_source/` — shallow clone of [`huggingface/agents-course`](https://github.com/huggingface/agents-course), gitignored.

## Setup

```bash
pip install -r requirements.txt
```

You'll need an HF account + `HF_TOKEN`, and (for some hands-ons) an LLM provider — the course defaults to HF Inference Providers, which is OpenAI-API-compatible and free up to a quota.
