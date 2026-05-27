# Plan: Complete the HF Agents Course (Fundamentals + Certificate of Excellence)

## Progress Tracker

**Overall: 0/12 units complete. Scaffold pushed; per-unit work follows.**

| Done | Unit | Topic | Quizzes | Hands-on |
|:----:|------|-------|:---:|:---:|
| ☐ | 0 | Welcome / Onboarding | — | — |
| ☐ | live_1 | How the course works (Q&A live recap) | — | — |
| ☐ | 1 | **Agent fundamentals** (ReAct, tools, smolagents tutorial) | quiz1, quiz2, final | ✅ first agent |
| ☐ | 2 | Frameworks intro | — | — |
| ☐ | 2.1 | smolagents framework | quiz1, quiz2, final | — |
| ☐ | 2.2 | LlamaIndex framework | quiz1, quiz2 | — |
| ☐ | 2.3 | LangGraph framework | quiz1 | — |
| ☐ | 3 | Agentic RAG (Gala Agent — Gradio) | — | ✅ |
| ☐ | 4 | **Final Project (GAIA benchmark)** | — | ✅ for cert |
| ☐ | bonus_1 | Fine-tuning for function-calling | — | ✅ fine-tune |
| ☐ | bonus_2 | Observability and evaluation | quiz | — |
| ☐ | bonus_3 | Pokémon battle agent | — | ✅ |

**Certs**
- **Fundamentals** = complete Unit 1.
- **Certificate of Excellence** = Unit 1 + one use case + the final challenge (GAIA leaderboard submission).

---

## Workflow per unit

1. **Read** chapters online or via `notebooklm/unit_*.txt`.
2. **Hands-on artifact** (where applicable) lands in `unit_*/`.
3. **Practice quiz** drafted in `unit_*/practice_quiz.md` mirroring the HF-site quizzes.
4. **Real quiz** taken on the HF course site; PLAN updated.

---

## Recommended order

### Unit 0 + Live 1 (intro / setup)
Skim. Confirm HF account + HF_TOKEN. No artifact.

### Unit 1 — Agent Fundamentals (cert-critical)
The substantive theory unit. Read all 14 chapters (Thought / Action / Observation cycle, ReAct, dummy agent library, smolagents tutorial). Build the **first agent** under `unit_1/`. Draft practice quizzes for *quiz1*, *quiz2*, *final-quiz*. Pass the three HF-site quizzes → **Fundamentals certificate**.

### Unit 2 — Frameworks
Quick intro chapter (no quiz). Then dive into one or more sub-units:

- **2.1 smolagents** — most aligned with Unit 1 tutorial; small CodeAgent + ToolCallingAgent example under `unit_2_1_smolagents/`. Draft *quiz1*, *quiz2*, *final*.
- **2.2 LlamaIndex** — components / tools / agents / workflows. Small RAG-ish agent under `unit_2_2_llamaindex/`. Draft *quiz1*, *quiz2*.
- **2.3 LangGraph** — building blocks + a document-analysis graph. Small example under `unit_2_3_langgraph/`. Draft *quiz1*.

### Unit 3 — Agentic RAG (Gala Agent)
The chapter walks through a guest-story RAG agent that recommends actions at a gala. Build the Gradio Space; optionally deploy.

### Unit 4 — Final Project (GAIA)
Build an agent (we already have smolagents installed) that solves the GAIA Level-1 benchmark, submits to the leaderboard. **Required for the Certificate of Excellence.**

### Bonus Unit 1 — Fine-tune for function-calling
Pick a small base (e.g. `google/gemma-2-2b-it` or `Qwen/Qwen2.5-3B-Instruct`); fine-tune with TRL on a function-calling dataset (`Salesforce/xlam-function-calling-60k` or `NousResearch/hermes-function-calling-v1`). Push adapter to Hub.

### Bonus Unit 2 — Observability
Trace one of the agents above with Phoenix / OpenTelemetry; evaluate with `evaluate` or `phoenix-evals`. Draft quiz.

### Bonus Unit 3 — Pokémon battle agent
smolagents agent against the Pokémon Showdown API.

---

## Verification

Real-quiz scores go on the HF site; certificates appear on your HF profile. GAIA leaderboard submission is via a PR on `agents-course/student-leaderboard` (or equivalent — check the unit's `get-your-certificate.mdx`).
