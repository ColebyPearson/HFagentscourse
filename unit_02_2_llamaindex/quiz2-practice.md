# Unit 2.2 — Practice Quiz 2 (Tools, Agents, Workflows, AgentWorkflow)

> Self-graded practice for the second half of the LlamaIndex unit.
> Covers: `FunctionTool`, `QueryEngineTool`, `ToolSpec`s (Gmail, MCP), utility tools (`OnDemandToolLoader`, `LoadAndSearchToolSpec`), agent types (Function-Calling, ReAct, Custom), `AgentWorkflow`, multi-agent workflows, `@step` workflows with `Event`s, `Context` state.
> Format: 15 multiple-choice questions. Answers + explanations at the bottom.

---

### Q1. The four main tool flavors in LlamaIndex are:

A. WebTool, FileTool, SQLTool, ShellTool.
B. `FunctionTool`, `QueryEngineTool`, `ToolSpec`s, Utility Tools (`OnDemandToolLoader`, `LoadAndSearchToolSpec`).
C. RESTTool, GraphQLTool, gRPCTool, RPCTool.
D. Tools have no flavors.

---

### Q2. `FunctionTool.from_defaults(get_weather, name="my_weather_tool", description="...")` builds the LLM-visible interface from:

A. Hand-written JSON only.
B. The function's name, docstring, type hints (auto-extracted) — plus any explicit `name` / `description` you pass in to override.
C. A YAML config file.
D. Environment variables.

---

### Q3. What is a `QueryEngineTool`?

A. A tool that builds a query engine.
B. A wrapper that exposes a `QueryEngine` (from your `VectorStoreIndex`) as a tool an agent can call — needs `name` and `description` so the LLM knows when to use it.
C. A tool only used for SQL.
D. A debugging utility.

---

### Q4. A `ToolSpec` is best described as:

A. A static config file.
B. A community-curated **bundle of related tools** (e.g. `GmailToolSpec`) callable via `.to_tool_list()` — like a professional toolkit for a specific service.
C. A test harness.
D. A type alias.

---

### Q5. MCP integration in LlamaIndex uses:

A. A custom protocol.
B. `BasicMCPClient("http://127.0.0.1:8000/sse")` + `McpToolSpec(client=mcp_client)` from `llama-index-tools-mcp`.
C. A LangChain bridge.
D. Not supported.

---

### Q6. The point of `OnDemandToolLoader` / `LoadAndSearchToolSpec` is to:

A. Speed up startup.
B. Wrap an API or data loader as a tool that **loads + indexes + queries on the fly** in a single tool call — so large or noisy data sources don't overflow the context window.
C. Replace the LLM.
D. Increase logging.

---

### Q7. LlamaIndex supports **three** main agent types. Which set matches the unit?

A. SyncAgent, AsyncAgent, BatchAgent.
B. Function-Calling Agent (uses the LLM's native tool API), ReAct Agent (works with any chat/text LLM), Advanced Custom Agents (subclasses of `BaseWorkflowAgent`).
C. SmallAgent, MediumAgent, LargeAgent.
D. SyncAgent, RAGAgent, ToolAgent.

---

### Q8. The simplest way to create an agent from a list of Python functions is:

A. `Agent(functions)`
B. `AgentWorkflow.from_tools_or_functions([FunctionTool.from_defaults(my_fn)], llm=llm)` — picks Function-Calling if the LLM supports it, otherwise ReAct.
C. `LlamaIndex.spawn(fns)`
D. `Pipeline.agent_from_fns(...)`

---

### Q9. Agents in LlamaIndex are stateless by default. To remember earlier turns you:

A. Persist messages by hand.
B. Build a `Context(agent)` once, then pass it: `await agent.run(msg, ctx=ctx)` — the context tracks prior interactions for memory.
C. Use `pickle.dump(agent)`.
D. It's not possible.

---

### Q10. `AgentWorkflow(agents=[a, b, c], root_agent="a")` is:

A. A single agent loop.
B. A multi-agent system where the root agent receives the user message; each agent can answer directly or **hand off** to another agent better suited to the sub-task.
C. A linear pipeline.
D. A REST server.

---

### Q11. A LlamaIndex `Workflow` (manual flavor) is built by:

A. Writing a DAG in YAML.
B. Subclassing `Workflow`, decorating methods with `@step`, and emitting/consuming `Event` subclasses (`StartEvent` → custom events → `StopEvent`). Type hints on each step's `ev` argument are how the framework routes events.
C. Calling `Workflow.compile(...)`.
D. Subprocess orchestration.

---

### Q12. To connect two steps that pass data, you:

A. Use global variables.
B. Define a custom `class ProcessingEvent(Event): intermediate_result: str` and have step one return it while step two takes it as its `ev: ProcessingEvent` argument.
C. Write to disk.
D. Use Redis.

---

### Q13. To create a **loop** in a workflow you:

A. Use `while True`.
B. Use Python's union operator in type hints (`-> ProcessingEvent | LoopEvent`) so a step can re-emit a `LoopEvent` that re-triggers the same step on input (`ev: StartEvent | LoopEvent`).
C. Use recursion.
D. Loops aren't supported.

---

### Q14. To share state across steps in a workflow:

A. Pass a global dict.
B. Add a `ctx: Context` parameter to each `@step` and use `await ctx.store.set("key", value)` / `await ctx.store.get("key")`. The same `Context` is also used by `AgentWorkflow` for multi-agent state.
C. Pickle between calls.
D. Use thread-locals.

---

### Q15. The unit's mental model: when should you reach for a manual `Workflow` (steps + events) vs an `AgentWorkflow` (agents + handoff)?

A. They're identical; pick whichever.
B. Manual `Workflow` when you want **explicit step-by-step control** and the route through the graph is mostly deterministic; `AgentWorkflow` when you want LLMs to autonomously coordinate, hand off, and self-organize across multiple specialist agents.
C. Always use `AgentWorkflow`.
D. Always use `Workflow`.

---

## Answer Key + Explanations

| Q | Ans | Why |
|---|-----|-----|
| 1 | **B** | The "Using Tools in LlamaIndex" section enumerates exactly these four flavors. |
| 2 | **B** | `FunctionTool.from_defaults` reads name/docstring/types; `name=` and `description=` override the auto-derived strings. |
| 3 | **B** | `QueryEngineTool.from_defaults(query_engine, name=..., description=...)` is the canonical pattern. |
| 4 | **B** | A `ToolSpec` is a curated collection — e.g. `GmailToolSpec`. `.to_tool_list()` returns the individual `Tool`s. |
| 5 | **B** | The unit walks through `BasicMCPClient` + `McpToolSpec` after installing `llama-index-tools-mcp`. |
| 6 | **B** | Utility tools wrap loaders so big API outputs are indexed + queried in-tool instead of dumped into the prompt. |
| 7 | **B** | Function-Calling, ReAct, Advanced Custom — verbatim from the agents intro. |
| 8 | **B** | `AgentWorkflow.from_tools_or_functions(...)` is the one-liner the unit recommends. |
| 9 | **B** | `Context(agent)` is the memory mechanism. Stateless by default. |
| 10 | **B** | The unit specifies a `root_agent` receives the message; each agent can answer or hand off. |
| 11 | **B** | Verbatim from "Creating Workflows": `@step` methods, `StartEvent` / custom events / `StopEvent`, type hints control routing. |
| 12 | **B** | Custom `Event` subclasses with typed fields are the data conduit between steps. |
| 13 | **B** | Type-hint unions are how you express loops/branches; the unit's `LoopEvent` example shows it. |
| 14 | **B** | `ctx.store.get/set` is the canonical state API. `AgentWorkflow` uses the same `Context`. |
| 15 | **B** | Manual workflows for deterministic step-by-step; `AgentWorkflow` when you want emergent multi-agent routing. |

**Pass mark:** ≥ 12 / 15. If you missed Q11–Q14 you're still fuzzy on the workflow primitives — re-read "Creating Workflows" + "State Management".
