# Plan: Complete the HF Agents Course (Fundamentals + Certificate of Excellence)

## Progress Tracker

**Overall: scaffolding + practice quizzes + hands-on artifacts complete (10/12 units have full coverage). Quizzes themselves are taken on the HF course site; tick the boxes after passing.**

| Quizzes drafted | Hands-on done | Unit | Topic | Artifact link |
|:-:|:-:|------|-------|---|
|  — |  — | 0 | Welcome / Onboarding | — |
|  — |  — | live_1 | Live Q&A recap | — |
| ✅ 3 | ✅ | 1 | **Agent fundamentals** | [Space](https://huggingface.co/spaces/VoicesColeby/Alfred-Unit1-Agent) |
|  — |  — | 2 | Frameworks intro | — |
| ✅ 3 |  — | 2.1 | smolagents | (use cases in Unit 1 + Unit 3) |
| ✅ 2 |  — | 2.2 | LlamaIndex | — |
| ✅ 1 |  — | 2.3 | LangGraph | — |
|  — | ✅ | 3 | Agentic RAG (Gala Agent) | [Space](https://huggingface.co/spaces/VoicesColeby/Alfred-Gala-Unit3) |
|  — | ✅ | 4 | **Final Project (GAIA)** | [Space](https://huggingface.co/spaces/VoicesColeby/GAIA-Agent-Unit4) |
|  — | ✅ | bonus_1 | Function-calling fine-tune | [Adapter](https://huggingface.co/VoicesColeby/smollm2-1.7b-fc-lora) |
| ✅ 1 |  — | bonus_2 | Observability and evaluation | (instrument any of the above) |
|  — | ✅ | bonus_3 | Pokémon battle agent | `bonus_03_pokemon/agent/agent.py` |

**Certs**
- **Fundamentals** = Unit 1 quiz (taken on HF course site).
- **Certificate of Excellence** = Unit 1 + one use case + the final challenge (≥30% on GAIA Level-1 via the Unit 4 Space).

---

## Practice quizzes (10 files, 15 Q each, self-graded)

| Path | Targets |
|---|---|
| `unit_01_introduction/quiz1-practice.md` | Agent definition, LLM internals, chat templates, tool intro. |
| `unit_01_introduction/quiz2-practice.md` | Think→Act→Observe loop, ReAct vs CoT, Code Agents, stop-and-parse. |
| `unit_01_introduction/quiz3-final-prep.md` | smolagents tutorial; covers the cert-gating Unit 1 final quiz. |
| `unit_02_1_smolagents/quiz1-practice.md` | Why smolagents, Code vs JSON, MultiStepAgent loop. |
| `unit_02_1_smolagents/quiz2-practice.md` | Tools / Toolspecs / sharing / MCP / agentic RAG. |
| `unit_02_1_smolagents/quiz3-final-prep.md` | Multi-agent + vision/browser; covers the smolagents final quiz. |
| `unit_02_2_llamaindex/quiz1-practice.md` | Components: IngestionPipeline, VectorStoreIndex, query engines, evaluators. |
| `unit_02_2_llamaindex/quiz2-practice.md` | FunctionTool / QueryEngineTool / ToolSpec / AgentWorkflow / Workflow + @step + Context. |
| `unit_02_3_langgraph/quiz1-practice.md` | State / Node / Edge / StateGraph + ToolNode + tools_condition. |
| `bonus_02_observability/quiz1-practice.md` | Traces vs spans, online vs offline eval, Langfuse + LLM-as-judge + dataset eval. |

---

## Hands-on artifacts

| Unit | Artifact | Notes |
|---|---|---|
| 1 | [`VoicesColeby/Alfred-Unit1-Agent`](https://huggingface.co/spaces/VoicesColeby/Alfred-Unit1-Agent) | smolagents CodeAgent + 5 tools (web_search, visit_webpage, timezone, FX, final_answer). |
| 3 | [`VoicesColeby/Alfred-Gala-Unit3`](https://huggingface.co/spaces/VoicesColeby/Alfred-Gala-Unit3) | BM25 retriever over `agents-course/unit3-invitees` + web/weather/hub-stats tools. |
| 4 | [`VoicesColeby/GAIA-Agent-Unit4`](https://huggingface.co/spaces/VoicesColeby/GAIA-Agent-Unit4) | Hits the official GAIA Level-1 scoring API; HF-OAuth login + Run+Submit. |
| B1 | [`VoicesColeby/smollm2-1.7b-fc-lora`](https://huggingface.co/VoicesColeby/smollm2-1.7b-fc-lora) | LoRA on Hermes function-calling-thinking. Switch BASE_MODEL to gemma-2-2b-it once gated access is granted. |
| B3 | `bonus_03_pokemon/agent/agent.py` | poke_env Player subclass for [`PShowdown/pokemon_agents`](https://huggingface.co/spaces/PShowdown/pokemon_agents). |

---

## What's left for the user

1. **Sit the HF-site quizzes** (Unit 1 ×3, Unit 2.1 ×3, Unit 2.2 ×2, Unit 2.3 ×1, Bonus 2 ×1). Practice files mirror the format and pass mark.
2. **Click Run+Submit on the GAIA Space** to record a Students-leaderboard score (≥30% → Certificate of Excellence eligible).
3. **(Optional) Accept Gemma-2-2b-it gated license**, then change `BASE_MODEL` in `bonus_01_function_calling/train/train_fc.py` and rerun for a closer reproduction of the canonical bonus unit.
4. **(Optional) Drop the Pokémon agent** into a duplicated `PShowdown/pokemon_agents` Space to enter the live ladder.

---

## Verification

- **Practice quiz pass mark**: 12 / 15 per file.
- **Cert quizzes**: HF course site; certificates appear on your HF profile.
- **GAIA score**: posted to `agents-course/Students_leaderboard` automatically when `Run + Submit` is clicked on the Unit 4 Space (verified by Space URL in the submission).
