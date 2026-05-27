# Bonus Unit 2 — Practice Quiz (Observability + Evaluation)

> Self-graded practice for the observability bonus unit.
> Covers: traces / spans, key metrics, online vs offline evaluation, instrumenting smolagents with OpenTelemetry + Langfuse / Arize Phoenix, user feedback, LLM-as-judge, dataset-based offline evaluation (e.g. GSM8K).
> Format: 15 multiple-choice questions. Answers + explanations at the bottom.

---

### Q1. What is **observability** for AI agents?

A. Logging error messages.
B. Understanding what's happening inside the agent via external signals — logs, metrics, and traces of every model call / tool call / decision step.
C. Adding more print statements.
D. The UI styling.

---

### Q2. Why is observability **especially** important for AI agents (vs traditional software)?

A. They're written in different languages.
B. They're non-deterministic, multi-step, and call external services with token costs — black-box behavior is the default. Observability is how you turn the box transparent.
C. They run faster.
D. They have no errors.

---

### Q3. In OpenTelemetry / Langfuse terminology, a **trace** vs a **span** is:

A. They're synonyms.
B. A **trace** = one complete agent task (end-to-end), composed of multiple **spans** (individual sub-steps like an LLM call or a tool call).
C. A span is the parent of a trace.
D. Spans don't exist.

---

### Q4. Which of the following is **not** a typical agent observability metric?

A. Latency.
B. Cost per run (tokens × price).
C. Request errors / failed tool calls.
D. Lines of code in the agent.

---

### Q5. **Online evaluation** is best described as:

A. Running unit tests in CI.
B. Measuring agent performance on real, live traffic in production — drift monitoring, real-user satisfaction, A/B and shadow tests.
C. Pre-deployment benchmarks.
D. Running on a GPU.

---

### Q6. **Offline evaluation** is best described as:

A. Disconnecting from the internet.
B. Running the agent on a curated test dataset with known expected outputs (e.g. GSM8K) — repeatable, comparable, often part of CI/CD.
C. Manual review only.
D. Streaming evaluation.

---

### Q7. The mature workflow the unit recommends combines online + offline as:

A. Offline only.
B. Online only.
C. A loop: offline eval → deploy → online metrics → harvest new failure cases → add to offline test set → iterate.
D. Random sampling.

---

### Q8. To instrument a smolagent for OpenTelemetry export to Langfuse, the unit uses:

A. A custom logger.
B. `pip install langfuse 'smolagents[telemetry]' openinference-instrumentation-smolagents`, set `LANGFUSE_*` env vars, then `SmolagentsInstrumentor().instrument()`.
C. `logging.basicConfig(level=DEBUG)`.
D. Manual `print()` calls.

---

### Q9. The unit instructs you to **verify** your instrumentation by:

A. Reading the source code.
B. Running a trivial agent (e.g. `agent.run("1+1=")`) and checking that the trace appears in your observability dashboard with the expected spans.
C. Posting to Twitter.
D. Running 100 prompts at once.

---

### Q10. To attach `user_id`, `session_id`, `tags`, and other metadata to a trace, the unit uses:

A. URL params.
B. `with langfuse.start_as_current_span(name="...") as span: ...; span.update_trace(user_id=..., session_id=..., tags=[...], metadata={...})`, plus `langfuse.flush()` at the end of short-lived runs.
C. A REST PUT.
D. SQL UPDATE.

---

### Q11. To capture **user feedback** (👍 / 👎) on a Gradio chat into Langfuse, you:

A. Save it in localStorage.
B. Capture the trace_id during the `respond(...)` call, then in the `chatbot.like` handler call `langfuse.create_score(value=1_or_0, name="user-feedback", trace_id=trace_id)`.
C. Write to disk.
D. Not supported.

---

### Q12. **LLM-as-a-Judge** evaluation works by:

A. Asking the user.
B. Sending the agent's output to a separate LLM with an evaluation template (e.g. "Is this toxic? Is this correct? Is this helpful?") and logging the judge's verdict alongside the original trace.
C. A regex over outputs.
D. Hand-grading.

---

### Q13. For **offline dataset evaluation**, the unit shows:

A. A local CSV.
B. `load_dataset("openai/gsm8k", ...)` → `langfuse.create_dataset(...)` + `langfuse.create_dataset_item(...)` per row → loop items inside `item.run(run_name=...)` to link each agent run to its dataset item.
C. A SQL query.
D. Manual review only.

---

### Q14. A practical reason to swap a smolagent's model **after** running it on GSM8K is:

A. The model is broken.
B. Offline runs reveal accuracy / cost / latency trade-offs — Langfuse's side-by-side comparison views let you compare runs across different models, tools, or prompts on the same dataset.
C. It's required.
D. It's cosmetic.

---

### Q15. Which is the **best** one-line summary of this bonus unit?

A. Observability is optional fluff.
B. To take an agent from demo to production you need: tracing (every span captured), online metrics (latency / cost / errors / feedback / LLM-as-judge), and offline evaluation on curated datasets — together they form the feedback loop.
C. Just use logs.
D. Evaluation is impossible.

---

## Answer Key + Explanations

| Q | Ans | Why |
|---|-----|-----|
| 1 | **B** | Verbatim from "What is Observability?". |
| 2 | **B** | Non-determinism + multi-step + external calls = black box without tracing. |
| 3 | **B** | Trace = whole run; spans = sub-steps. Hierarchy. |
| 4 | **D** | LOC isn't an observability metric. Latency / cost / errors / feedback / accuracy are. |
| 5 | **B** | Live traffic, drift monitoring, A/B / shadow tests. |
| 6 | **B** | Curated dataset + known outputs + repeatable. GSM8K is the unit's example. |
| 7 | **C** | The unit literally describes this loop: offline → deploy → online → harvest → back into offline. |
| 8 | **B** | The exact recipe in Steps 0 + 1. |
| 9 | **B** | Step 2 = "Test your instrumentation". |
| 10 | **B** | The unit's "Additional Attributes" subsection shows exactly this pattern, including the `langfuse.flush()` call. |
| 11 | **B** | The Gradio chat snippet shows `create_score(value=1 or 0, name="user-feedback", trace_id=...)`. |
| 12 | **B** | Judge LLM + evaluation template + log score — verbatim from the LLM-as-Judge subsection. |
| 13 | **B** | Verbatim from the "Dataset Evaluation" subsection. |
| 14 | **B** | Langfuse's dataset-run comparison view is exactly for this. |
| 15 | **B** | The unit's "Final Thoughts" enumerates all six and ties them together. |

**Pass mark:** ≥ 12 / 15. If you missed Q7, Q12, or Q14, re-read the "Combining the two" and "Online Evaluation" subsections.
