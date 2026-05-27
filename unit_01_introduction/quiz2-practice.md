# Unit 1 — Practice Quiz 2 (Thought–Action–Observation, ReAct, Code Agents)

> Self-graded practice for the second half of Unit 1.
> Covers: Thought-Action-Observation cycle, ReAct vs CoT, agent action types (JSON/Code/Function-calling), stop-and-parse, Code Agents, Observations.
> Format: 15 multiple-choice questions. Answers + explanations at the bottom.

---

### Q1. The Thought-Action-Observation cycle is best described as:

A. A one-shot prompt → answer flow.
B. A loop the agent runs until its objective is fulfilled: the LLM **thinks**, the runtime **acts** (calls a tool), the result is **observed** (appended to the prompt), repeat.
C. Three separate models stacked sequentially.
D. A training procedure for instruction tuning.

---

### Q2. Within the cycle, "Action" specifically refers to:

A. The user typing.
B. The agent calling a tool with concrete arguments — emitted by the LLM as JSON or as a code block, parsed and executed by the runtime.
C. Logging to disk.
D. The LLM finishing its sentence.

---

### Q3. What is the role of an Observation in the loop?

A. The LLM's private memory.
B. Real-world feedback (tool output, error, system signal) that gets **appended to the running prompt** so the next Thought is conditioned on it.
C. A persisted database row.
D. The user's reaction shown in the UI.

---

### Q4. ReAct vs Chain-of-Thought (CoT) — which is the cleanest distinction?

A. ReAct uses code; CoT uses JSON.
B. ReAct only works on math; CoT only works on text.
C. CoT is pure internal reasoning (no tools). ReAct **interleaves** reasoning steps with **acting** (tool calls) and observing tool results.
D. They're the same thing.

---

### Q5. Recent "thinking" models like DeepSeek-R1 or OpenAI o1 differ from ReAct/CoT prompting in that:

A. They have no transformer attention.
B. They cannot use tools.
C. They were **trained** to think step-by-step using structured tokens like `<think>...</think>` — it's a training-level technique, not just a prompt.
D. They are smaller than 1B parameters.

---

### Q6. The three agent action styles taught in the unit are:

A. JSON Agent, Code Agent, Function-calling Agent (a fine-tuned JSON sub-type).
B. Reflex agent, BDI agent, hybrid agent.
C. CNN agent, RNN agent, transformer agent.
D. RAG agent, search agent, memory agent.

---

### Q7. What is the **stop-and-parse** approach?

A. The user pressing Ctrl-C.
B. The LLM is prompted to emit its action in a strict format (JSON or code block), **stop** generating right after, then an external parser reads the action and dispatches to the correct tool with the correct arguments.
C. A regex applied to user input.
D. A debugger feature in smolagents.

---

### Q8. Why might a **Code Agent** be more expressive than a JSON Agent?

A. JSON is impossible to parse.
B. Code naturally supports loops, conditionals, function composition, and direct library use — so multi-step logic in a single action is straightforward.
C. Code is always faster than JSON.
D. JSON cannot represent strings.

---

### Q9. Which is **not** an advantage of Code Agents from the unit?

A. Expressiveness (loops, conditionals).
B. Modularity / reusability of generated functions.
C. Direct integration with external libraries and APIs.
D. They eliminate the need to sandbox LLM-generated code.

---

### Q10. Function-calling agents (e.g. OpenAI tool-calling) are best characterized as:

A. A completely different paradigm with no relation to JSON agents.
B. A subcategory of JSON agents where the model has been **fine-tuned** to emit a structured tool-call message as the assistant turn.
C. Code agents that emit Python in disguise.
D. Agents without tools.

---

### Q11. In a ReAct trace like the unit's example, which line ends the loop?

```
Thought: I need to find the latest weather in Paris.
Action: Search["weather in Paris"]
Observation: It's 18°C and cloudy.
Thought: Now that I know the weather...
Action: Finish["It's 18°C and cloudy in Paris."]
```

A. The first `Action:` line.
B. The `Observation:` line.
C. The terminal `Action: Finish[...]` (a.k.a. `final_answer`) — that's the agent's signal it's done.
D. Loops never end.

---

### Q12. An agent gets the observation `"Error: 401 Unauthorized"` from a tool. The correct behavior is:

A. Ignore it and return a guess.
B. Add it to memory and let the next Thought decide (retry with different args, surface a question to the user, or give up cleanly).
C. Crash the entire program.
D. Re-train the model.

---

### Q13. Which of the following is the closest **pseudo-code** for the agent runtime?

A. `print(llm(messages))`
B. `while not done: t = think(messages); a = act(t); o = observe(a); messages.append(o)`
C. `for token in stream: yield token`
D. `tools.run_all()`

---

### Q14. Why is **executing LLM-generated code** a security concern?

A. Python is slow.
B. The LLM may produce code that exfiltrates data, deletes files, or executes prompt-injected instructions; sandboxing (e.g. smolagents' `LocalPythonExecutor` / E2B / Docker sandbox) is required for safety.
C. It always uses too much memory.
D. JSON is safer because LLMs can't write JSON.

---

### Q15. Where do "tool calls" actually appear in the conversation history that the LLM sees?

A. They are encrypted and hidden from the LLM.
B. The tool description goes in the system prompt; the LLM emits the action as part of its assistant turn; the runtime appends the tool result as an `Observation` (often as a new message) — so on the **next** decoding pass the LLM sees its own action and the resulting observation in context.
C. They live in a totally separate model.
D. They are sent to the user instead.

---

## Answer Key + Explanations

| Q | Ans | Why |
|---|-----|-----|
| 1 | **B** | The unit literally describes the cycle as a while-loop continuing until the objective is fulfilled. |
| 2 | **B** | Action = the LLM emitting a structured tool invocation (JSON or code) that the runtime parses + executes. |
| 3 | **B** | Observations are appended to the running prompt — they are how the agent "learns" from the environment between thoughts. |
| 4 | **C** | CoT keeps reasoning internal; ReAct interleaves Thought → Action → Observation so the model can ground each step in real feedback. |
| 5 | **C** | "Thinking" models are trained, not just prompted, to think — they emit special `<think>...</think>` regions. The course flags this explicitly as a *training-level* technique. |
| 6 | **A** | The Actions table names JSON Agent, Code Agent, and Function-calling Agent (a fine-tuned JSON sub-type). |
| 7 | **B** | Stop-and-parse: emit action in fixed format, halt generation, parse externally, dispatch. This is what makes the cycle deterministic. |
| 8 | **B** | The "Code Agents" subsection explicitly cites expressiveness via native control flow as the key win over JSON. |
| 9 | **D** | The unit specifically warns that executing LLM-generated code is risky — frameworks like smolagents add sandboxing exactly because the code path does **not** eliminate the need to sandbox. |
| 10 | **B** | The unit places function-calling under the JSON family, distinguished by the model being fine-tuned on a per-call structured output schema. |
| 11 | **C** | `Finish[...]` (or `final_answer(...)` in smolagents) is the terminal action; that's what signals the runtime the loop is over. |
| 12 | **B** | Treat errors as just another Observation. The next Thought can retry, ask the user, or give up. That's the whole point of feedback in the loop. |
| 13 | **B** | The cycle is literally that while-loop, with the LLM's thought driving the next step. |
| 14 | **B** | Prompt injection, data exfiltration, destructive file ops — all real. Sandbox the code-execution path before letting it touch your machine or your data. |
| 15 | **B** | Tool description in the system prompt; action in the assistant turn; result appended as an observation message. On the next pass the model sees its own action + the result and reasons forward. |

**Pass mark:** ≥ 12 / 15. If you missed Q7 / Q11 / Q13 you're still fuzzy on the loop mechanics — re-read "Actions" + "Observe" + "Dummy Agent Library".
