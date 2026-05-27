# Unit 2.1 — Practice Quiz 2 (Tools, Default Toolbox, Sharing, Retrieval Agents)

> Self-graded practice for the middle of the smolagents unit.
> Covers: `@tool` decorator vs `Tool` subclass, default toolbox, sharing/importing tools (Hub, HF Spaces, LangChain, MCP), agentic RAG with smolagents.
> Format: 15 multiple-choice questions. Answers + explanations at the bottom.

---

### Q1. The two ways to define a tool in smolagents are:

A. JSON manifest file + REST endpoint.
B. `@tool` decorator on a typed Python function with a good docstring, **or** subclass `Tool` with `name` / `description` / `inputs` / `output_type` / `forward()`.
C. Only the `@tool` decorator.
D. Only YAML.

---

### Q2. When subclassing `Tool`, the dictionary `inputs = {"query": {"type": "string", "description": "..."}}` is used to:

A. Cache previous calls.
B. Generate the structured tool description injected into the LLM system prompt (name, args with types/descriptions, output type).
C. Validate Python imports.
D. Trigger fine-tuning.

---

### Q3. Which of the following is part of the smolagents **default toolbox**?

A. `PythonInterpreterTool`
B. `FinalAnswerTool`
C. `DuckDuckGoSearchTool`, `GoogleSearchTool`, `VisitWebpageTool`, `UserInputTool`
D. All of the above.

---

### Q4. Pushing a custom `Tool` instance to the Hub uses:

A. `git push tool`
B. `tool.push_to_hub("username/repo", token=HF_TOKEN)` — and later `load_tool("username/repo", trust_remote_code=True)` to import.
C. `transformers-cli upload`
D. There's no API for this.

---

### Q5. The `trust_remote_code=True` flag on `load_tool(...)` is **important** because:

A. It's required for paid Hub repos.
B. The Hub tool may contain arbitrary Python that will execute in your process — you must explicitly opt in to running it. Only set this for sources you trust.
C. It enables vision support.
D. It's purely cosmetic.

---

### Q6. You want to wrap a Gradio Space as a tool your agent can call. The right API is:

A. Manually scrape its UI.
B. `Tool.from_space("user/space-name", name="...", description="...")` — uses `gradio_client` under the hood to call the Space's predict endpoint.
C. `Space.connect("...")` from `huggingface_hub`.
D. There's no way to do this.

---

### Q7. To import a LangChain tool into smolagents:

A. Rewrite it from scratch.
B. `Tool.from_langchain(langchain_tool_instance)` — after `pip install -U langchain-community` (and any keys, e.g. `SERPAPI_API_KEY` for SerpAPI).
C. `lc.bridge.smol()`
D. Not supported.

---

### Q8. To pull in tools from an MCP server, you use:

A. `ToolCollection.from_mcp(server_parameters, trust_remote_code=True)` inside a `with` block; then `CodeAgent(tools=[*tool_collection.tools], ...)`.
B. `mcp install agent`
C. `smolagents.mcp.start_server()`
D. Not supported.

---

### Q9. Which statement about Agentic RAG (vs vanilla RAG) is most accurate?

A. Agentic RAG removes the LLM.
B. Agentic RAG lets the agent autonomously reformulate the query, perform multiple retrieval rounds, critique results, and decide when to stop — unlike one-shot RAG that retrieves once on the raw user query.
C. Agentic RAG is slower and always worse.
D. Agentic RAG uses no embeddings.

---

### Q10. In the unit's `PartyPlanningRetrieverTool` example, the retriever is:

A. A fine-tuned dense embedding model.
B. `BM25Retriever` over LangChain `Document` objects, with `RecursiveCharacterTextSplitter` for chunking — wired into a smolagents `Tool` subclass exposing a `query` input.
C. A SQL database.
D. A graph database.

---

### Q11. Which is **not** in the list of "enhanced retrieval capabilities" the unit calls out for agentic RAG?

A. Query reformulation / decomposition / expansion.
B. Reranking with a cross-encoder.
C. Multi-step retrieval + source integration + result validation.
D. Bypassing the LLM and answering directly from chunks.

---

### Q12. The `@tool` decorator extracts the description from the function's docstring. Which docstring structure is **expected** for arg descriptions?

A. Numpy style `Parameters\n----------\n` block.
B. A Google-style `Args:` block with `arg_name: description` lines — smolagents parses these into the tool's structured argument descriptions.
C. Free-form text only.
D. JSON schema embedded in a comment.

---

### Q13. You define both `description` and a docstring on a `Tool` subclass. Which one is the **primary source** for the agent's system prompt?

A. The Python docstring.
B. The class-level `description = "..."` attribute (and the structured `inputs` dict for args). The agent injects those into the system prompt.
C. Both are concatenated.
D. Neither.

---

### Q14. After `tool.push_to_hub("user/my_tool", token=HF_TOKEN)`, the Hub repo will:

A. Contain only weights.
B. Hold a `tool.py` + `requirements.txt` + a Gradio Space wrapper so anyone can `load_tool(...)` it or even open it interactively in the browser.
C. Be private by default.
D. Auto-delete after 24h.

---

### Q15. **Best practice** for tool descriptions on a smolagents tool that the LLM will see:

A. Leave them blank; the LLM will figure it out.
B. Be precise and concrete (what it does, what each argument means, valid value ranges/enums, return shape). The unit even shows enumerating valid values for `occasion` in the docstring as a way to reduce hallucinated args.
C. Always make them very long, regardless of relevance.
D. Use only emojis.

---

## Answer Key + Explanations

| Q | Ans | Why |
|---|-----|-----|
| 1 | **B** | Verbatim from the Tools section. |
| 2 | **B** | `inputs` is structured arg metadata; combined with `name` + `description` + `output_type` it builds the LLM-visible interface description. |
| 3 | **D** | All four are listed as the default toolbox in the unit. |
| 4 | **B** | `tool.push_to_hub("user/repo", token=...)` is shown in the "Sharing a Tool to the Hub" subsection. |
| 5 | **B** | Hub tools are arbitrary Python downloaded and exec'd in your process — opt-in required, only for sources you trust. |
| 6 | **B** | `Tool.from_space("user/space", name=, description=)` wraps the Space via `gradio_client`. |
| 7 | **B** | The course shows `Tool.from_langchain(load_tools(["serpapi"])[0])` after installing langchain-community + setting `SERPAPI_API_KEY`. |
| 8 | **A** | The unit demonstrates `ToolCollection.from_mcp(StdioServerParameters(...), trust_remote_code=True)` as a context manager. |
| 9 | **B** | Agentic RAG = agent owning the retrieval loop. Multi-step queries, query rewriting, criticism, fallback. |
| 10 | **B** | The example uses BM25 + LangChain `Document` + `RecursiveCharacterTextSplitter`, wrapped in a `Tool` subclass. |
| 11 | **D** | Bypassing the LLM is *not* in the agentic-RAG list — the LLM stays in the loop to reason about retrieval results. |
| 12 | **B** | Google-style `Args:` is the convention; the unit's `suggest_menu` and `catering_service_tool` both use it. |
| 13 | **B** | For `Tool` subclasses the class attributes are authoritative. (For `@tool` functions the docstring is the source.) |
| 14 | **B** | The Hub tool repo is a small Python package + an auto-generated Gradio Space. |
| 15 | **B** | Precise descriptions + enumerated valid args = fewer hallucinations. The `suggest_menu` example is built around this. |

**Pass mark:** ≥ 12 / 15. Review "Tools" and "Sharing and Importing Tools" if you missed Q4, Q6, Q7, or Q8.
