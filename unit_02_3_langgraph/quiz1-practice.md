# Unit 2.3 — Practice Quiz (LangGraph)

> Self-graded practice for the LangGraph unit.
> Covers: control vs freedom, State / Node / Edge / StateGraph, conditional routing, the email-sorting graph, ReAct via `ToolNode` + `tools_condition`, `add_messages` reducer, Langfuse tracing.
> Format: 15 multiple-choice questions. Answers + explanations at the bottom.

---

### Q1. What is LangGraph?

A. A vector database.
B. A framework (from LangChain) for managing the **control flow** of LLM applications as a directed graph of nodes and edges, with explicit state.
C. A fine-tuning library.
D. An IDE.

---

### Q2. On the control-vs-freedom spectrum, where does LangGraph sit relative to smolagents?

A. Same place.
B. LangGraph favors **control** — explicit graph, predictable transitions, state you design. smolagents favors **freedom** — let the LLM emit code and decide each step.
C. LangGraph is "more free".
D. They aren't comparable.

---

### Q3. The four core building blocks of LangGraph are:

A. Documents, Indexes, Queries, Responses.
B. State, Nodes, Edges, StateGraph (compiled into an executable graph).
C. Loaders, Splitters, Embedders, Retrievers.
D. Models, Prompts, Tools, Agents.

---

### Q4. **State** in LangGraph is:

A. A reserved framework class you can't change.
B. A user-defined `TypedDict` (or pydantic-like) shape that flows through the graph; each node returns a partial dict that is merged into the running state.
C. A global variable.
D. Always a JSON string.

---

### Q5. A **Node** is:

A. An LLM provider.
B. A Python function `(state) -> partial_state_dict` — can call an LLM, run a tool, do plain Python, or ask a human; its return value updates state.
C. A connection between functions.
D. A persistence layer.

---

### Q6. To express "after `classify_email`, go to `handle_spam` or `draft_response` depending on a flag", you use:

A. `add_edge("classify_email", "handle_spam")` only.
B. `add_conditional_edges("classify_email", route_email, {"spam": "handle_spam", "legitimate": "draft_response"})`.
C. A regex.
D. A separate graph.

---

### Q7. The special `START` and `END` nodes are:

A. User-defined.
B. Built into LangGraph: `START` is the entry point your first edge connects from; `END` marks terminal states the graph can exit through.
C. Equivalent to `pass`.
D. Deprecated.

---

### Q8. To build and execute the graph, the typical sequence is:

A. `StateGraph(SomeState)` → `add_node` / `add_edge` / `add_conditional_edges` → `builder.compile()` → `graph.invoke({...initial state...})`.
B. `StateGraph().run(state)`.
C. `Graph.start()`.
D. `LangGraph.execute(json_config)`.

---

### Q9. The `add_messages` reducer (used in the document-analysis graph) does what?

A. Replaces the message list with the latest message.
B. **Appends** new messages onto the existing list instead of overwriting — used via `Annotated[list[AnyMessage], add_messages]` in the State TypedDict.
C. Deduplicates messages.
D. Hashes messages.

---

### Q10. In the document-analysis graph, the `ToolNode(tools)` prebuilt does:

A. Returns metadata only.
B. Wraps your tool list as a node — when reached, it runs whichever tool the LLM's most recent message asked for and appends the tool result to the state's messages.
C. Re-prompts the user.
D. Connects to MCP.

---

### Q11. `tools_condition` is a prebuilt routing function that:

A. Routes to a random node.
B. Reads the latest assistant message — if it includes a tool call, route to the `tools` node; otherwise route to `END`. This is what closes the ReAct loop.
C. Always routes to `END`.
D. Times the call out.

---

### Q12. The minimal LangGraph ReAct shape from the document-analysis example is:

A. `START → assistant → END`.
B. `START → assistant → tools_condition → (tools → assistant) loop, or END`.
C. `START → tools → assistant → END`.
D. `START → tools → END`.

---

### Q13. `llm.bind_tools(tools, parallel_tool_calls=False)` does:

A. Trains the LLM on tool examples.
B. Returns a wrapped LLM that, on invocation, can emit structured tool calls; `parallel_tool_calls=False` forces one tool call per step (simpler ReAct flow).
C. Disables tools.
D. Compiles the tools.

---

### Q14. To visualize a compiled graph, you call:

A. `print(graph)`.
B. `graph.get_graph().draw_mermaid_png()` — produces a Mermaid PNG of the nodes/edges (the unit displays it in the notebook).
C. `viz.graphviz(graph)`.
D. Not supported.

---

### Q15. The unit demonstrates wiring **Langfuse** (tracing) into a LangGraph run via:

A. A new graph.
B. The `langfuse.langchain.CallbackHandler()` instance passed as `config={"callbacks": [langfuse_handler]}` to `compiled_graph.invoke(...)` — once the env vars are set, every node call shows up as a trace.
C. A magic comment.
D. Manual print statements.

---

## Answer Key + Explanations

| Q | Ans | Why |
|---|-----|-----|
| 1 | **B** | LangGraph is purpose-built for orchestrating control flow in LLM apps. |
| 2 | **B** | The unit explicitly positions LangGraph as the "control" end of the spectrum vs smolagents' "freedom" end. |
| 3 | **B** | State, Nodes, Edges, StateGraph — verbatim from the "Building Blocks" section. |
| 4 | **B** | User-defined `TypedDict`; each node returns a partial update that's merged. |
| 5 | **B** | The unit's definition: a node takes the state, does work, returns state updates. |
| 6 | **B** | `add_conditional_edges(source, routing_fn, {return_value: target_node})`. |
| 7 | **B** | `START` and `END` are built-in. The first edge typically starts at `START`; terminal nodes connect to `END`. |
| 8 | **A** | Build → compile → invoke is the canonical lifecycle. |
| 9 | **B** | `add_messages` is the reducer that appends new messages; `Annotated[list, add_messages]` is the magic syntax. |
| 10 | **B** | `ToolNode` reads the last message's tool calls, runs them, appends results — the document-analysis graph uses it verbatim. |
| 11 | **B** | `tools_condition` looks for tool calls in the latest message and either routes to `tools` or terminates. |
| 12 | **B** | The classic ReAct cycle in LangGraph is exactly that: assistant ↔ tools loop closed by `tools_condition`. |
| 13 | **B** | `bind_tools` returns a tool-aware LLM; `parallel_tool_calls=False` simplifies the loop. |
| 14 | **B** | The unit's visualization recipe. (`xray=True` digs into nested graphs.) |
| 15 | **B** | Verbatim from "Step 6": Langfuse `CallbackHandler()` in `config={"callbacks": [...]}`. |

**Pass mark:** ≥ 12 / 15. If you missed Q9–Q12 you're still fuzzy on the document-analysis ReAct pattern — re-read "The ReAct Pattern: How I Assist Mr. Wayne".
