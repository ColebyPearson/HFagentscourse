# Unit 2.1 — Practice Quiz 1 (Why smolagents, Code Agents, Tool-Calling vs JSON)

> Self-graded practice for the first half of the smolagents unit.
> Covers: smolagents design philosophy, model integrations, CodeAgent ReAct loop, Code Actions vs JSON Actions, ToolCallingAgent, basic instrumentation.
> Format: 15 multiple-choice questions. Answers + explanations at the bottom.

---

### Q1. What does the course list as the **headline strengths** of smolagents?

A. Heavy DSL, opinionated config, single-vendor lock-in.
B. Simplicity, flexible LLM support, code-first, deep HF Hub integration.
C. Forced JSON tool calls, mandatory cloud-only execution.
D. C++ runtime, GPU-only inference.

---

### Q2. Within smolagents, every agent inherits from which **core abstraction**?

A. `OpenAIAssistant`
B. `MultiStepAgent` — both `CodeAgent` and `ToolCallingAgent` are subclasses; each step = one thought + one tool call + observation.
C. `Pipeline`
D. `Chain`

---

### Q3. What's the **default** agent type in smolagents, and why?

A. ToolCallingAgent — JSON is the universal standard.
B. CodeAgent — research (the Executable-Code-Actions paper) shows code-based actions outperform JSON-based actions for multi-step problems, and code natively supports loops/composition.
C. ReActAgent — only supports OpenAI models.
D. PipelineAgent — wraps `transformers.pipeline`.

---

### Q4. Which is **not** a model integration class shipped with smolagents?

A. `TransformersModel`
B. `InferenceClientModel`
C. `LiteLLMModel`
D. `LangChainCloudModel`

---

### Q5. In a CodeAgent, the LLM emits Python code as its action. How is that code actually run?

A. `subprocess.run("python tmp.py")` with no sandbox.
B. Sent to the user's browser via WebAssembly.
C. Through a restricted Python executor with allow-listed imports (`additional_authorized_imports=[...]` on `CodeAgent`) — sandboxed by default for safety.
D. Compiled to C and linked dynamically.

---

### Q6. What does setting `additional_authorized_imports=['datetime']` do?

A. Restricts the LLM to only use `datetime`.
B. Adds `datetime` to the safe-list of importable modules in the sandbox, **on top of** the built-in safe list. Without this, `import datetime` would be blocked.
C. Forces the agent to use only Python's stdlib.
D. Nothing — `datetime` is always allowed.

---

### Q7. In the unit's "Alfred party" example, the agent runs:

```python
agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=InferenceClientModel())
agent.run("Search for best music recommendations...")
```

What is the trace likely to contain on a successful run?

A. A JSON tool-call envelope.
B. Lines like `Executing parsed code: results = web_search(query="best music for a Batman party")` then a printed observation, repeating until `final_answer(...)`.
C. A binary dump.
D. Nothing — the agent emits the answer in one shot.

---

### Q8. How is a `ToolCallingAgent` structurally different from a `CodeAgent`?

A. It generates JSON-formatted tool-call envelopes (`[{"name": "web_search", "arguments": {...}}, ...]`) that the runtime parses and executes — same Think→Act→Observe loop, different action format.
B. It can only run on Anthropic models.
C. It bypasses tools entirely.
D. It uses gRPC instead of Python.

---

### Q9. The course advises picking `ToolCallingAgent` over `CodeAgent` when:

A. You always prefer JSON.
B. The system is simple and doesn't need variables/composition between calls (and your provider has native tool-calling).
C. You need to do multi-agent orchestration.
D. You want maximum reasoning power.

---

### Q10. Which is the **most accurate** mental model of `CodeAgent.run()`'s while-loop?

A. `SystemPromptStep` → `TaskStep` → loop: `write_memory_to_messages()` → call Model → parse code → execute → log `ActionStep` → repeat until `final_answer` or `max_steps`.
B. `model.generate(user)` once and return.
C. A daemon that runs forever.
D. `for tool in tools: tool.run(query)`.

---

### Q11. The `InferenceClientModel(model_id='Qwen/Qwen2.5-Coder-32B-Instruct', provider='together')` line means:

A. Hardcode the answer to "Qwen".
B. Use the HF Inference Providers routing to send requests to the **together.ai** provider hosting the Qwen 32B Coder model, authenticated via `HF_TOKEN`.
C. Download the 32B model locally.
D. Use the `transformers` pipeline.

---

### Q12. Pushing an agent to the Hub uses:

A. `huggingface-cli upload-agent`
B. `agent.push_to_hub("username/AlfredAgent")` — and `Agent.from_hub("...", trust_remote_code=True)` to download.
C. `git push agent`
D. There's no such API.

---

### Q13. Why does the unit recommend wiring `SmolagentsInstrumentor` + Langfuse (or any OTel exporter) into your agent **early**?

A. It's required by HF for cert.
B. Agents are inherently non-deterministic and multi-step — observability (traces of each thought / action / observation, latencies, token counts) is the only practical way to debug or evaluate them in production.
C. It speeds up inference.
D. It encrypts your token.

---

### Q14. The unit's "agency-spectrum" placement for a CodeAgent that loops Thought→Action→Observation until it emits `final_answer` is:

A. ☆☆☆ Simple processor.
B. ★☆☆ Router.
C. ★★☆ Tool caller (one-shot).
D. ★★★ Multi-step agent — and a multi-agent setup (e.g. manager + web_agent) is also ★★★.

---

### Q15. **Best practice** when the LLM-generated code may touch the filesystem, network, or user data:

A. Disable the sandbox for speed.
B. Use smolagents' default restricted executor, keep `additional_authorized_imports` minimal, run in an E2B / Docker sandbox if you need wider imports, and treat tool outputs as untrusted input (prompt-injection surface).
C. Ask the LLM to promise not to do anything malicious.
D. Run as root.

---

## Answer Key + Explanations

| Q | Ans | Why |
|---|-----|-----|
| 1 | **B** | Verbatim from the "Why use smolagents?" section. |
| 2 | **B** | `MultiStepAgent` is the base class; `CodeAgent` and `ToolCallingAgent` both subclass it. |
| 3 | **B** | Code-first is the design point — and the [Executable Code Actions](https://arxiv.org/abs/2402.01030) paper is cited in the unit as the empirical basis. |
| 4 | **D** | The shipped classes are `TransformersModel`, `InferenceClientModel`, `LiteLLMModel`, `OpenAIServerModel`, `AzureOpenAIServerModel`. There is no `LangChainCloudModel`. |
| 5 | **C** | Sandboxed restricted Python executor by default. You can also bolt on E2B / Docker sandboxes for stronger isolation. |
| 6 | **B** | `additional_authorized_imports` extends the safe-list; without it, common modules like `datetime` or `pandas` would be blocked. |
| 7 | **B** | A CodeAgent emits Python; the runtime prints `Executing parsed code:` followed by the code block and its captured stdout as the observation. |
| 8 | **A** | Same loop, different action serialization (JSON vs Python). |
| 9 | **B** | The unit explicitly says ToolCallingAgent is fine when you don't need code-style composition (looping queries, working with rich objects in-step). |
| 10 | **A** | Verbatim from the "How Does a Code Agent Work?" section. |
| 11 | **B** | `InferenceClientModel` hits HF Inference Providers; the `provider=...` kwarg routes the call to that provider. |
| 12 | **B** | `push_to_hub` and `from_hub(trust_remote_code=True)` are the canonical APIs. Shared agents also become first-class Spaces. |
| 13 | **B** | Traces show every thought + action + observation; without that, debugging an agent feels like guessing. The unit deliberately pulls Bonus 2 forward as a teaser. |
| 14 | **D** | Multi-step (and multi-agent) agents are the ★★★ end of the agency spectrum. |
| 15 | **B** | Defense in depth: sandbox, minimal imports, isolation, and treat tool outputs as adversarial. The unit explicitly flags prompt injection + harmful code execution as risks. |

**Pass mark:** ≥ 12 / 15. Review the "How Does a Code Agent Work?" and "Writing actions as code snippets or JSON blobs" sections if you missed Q5, Q8, or Q10.
