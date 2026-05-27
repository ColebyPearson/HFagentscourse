# Unit 2.1 — Final Quiz Prep (Multi-Agent, Vision/Browser, Comprehensive)

> Self-graded practice mirroring the certifying smolagents final quiz.
> Covers: multi-agent orchestration, manager/`managed_agents`, planning intervals, `final_answer_checks`, vision agents (start-of-run vs dynamic), browser automation, plus integration questions touching all of Unit 2.1.
> Format: 15 multiple-choice questions. Answers + explanations at the bottom.

---

### Q1. A smolagents multi-agent hierarchy is created by:

A. Spawning subprocesses.
B. Passing other agents as the `managed_agents=[...]` parameter to a manager `CodeAgent`. The manager treats each managed agent as if it were a tool (it can `web_agent("Find X")`).
C. Using `multiprocessing.Pool`.
D. Manually copying agent state.

---

### Q2. The unit cites two main benefits of splitting work across multiple agents:

A. Free GPU credits.
B. Each agent stays focused on its sub-task (better performance) and memories are isolated, so input tokens per step shrink (cheaper, lower latency).
C. They become deterministic.
D. They can train themselves.

---

### Q3. The `planning_interval=4` parameter means:

A. Trains for 4 epochs.
B. Every 4 steps, the agent inserts a dedicated planning step where the LLM reflects on what it's done and updates its strategy — useful for long-horizon tasks.
C. Times out after 4 seconds.
D. Limits memory to 4 messages.

---

### Q4. The `final_answer_checks=[check_reasoning_and_plot]` parameter does what?

A. Disables the final answer.
B. After the agent emits `final_answer(...)`, each callback runs against the proposed answer; raising stops the agent (forces another step). It's a programmatic guardrail / verifier — in the unit's example, a VLM checks the saved map.
C. Auto-tweets the answer.
D. Logs the answer to a database.

---

### Q5. Which model + role pairing matches the unit's worked example?

A. `web_agent` is a `CodeAgent` with `Qwen/Qwen2.5-Coder-32B-Instruct` (via `together`); `manager_agent` uses `deepseek-ai/DeepSeek-R1` for stronger planning.
B. Both agents use GPT-3.5.
C. The manager uses no LLM.
D. The web agent is a `ToolCallingAgent` and the manager is a Python script.

---

### Q6. Calling `manager_agent.visualize()` does what?

A. Opens a browser.
B. Prints a tree showing the manager, its authorized imports, its tools, its managed agents, and each managed agent's tools — handy for debugging.
C. Renders a 3D plot.
D. Generates a PDF report.

---

### Q7. Two ways smolagents passes images into a vision agent are:

A. Base64 strings only.
B. (i) At launch via `agent.run(prompt, images=[PIL.Image, ...])` (stored as `task_images`); (ii) dynamically during execution via a `step_callback` that sets `step_log.observations_images = [...]` (e.g. for browser screenshots).
C. Through a separate VLM service.
D. Only via URLs.

---

### Q8. The browser-automation example uses which libraries?

A. Playwright + Puppeteer.
B. Helium + Selenium (`pip install "smolagents[all]" helium selenium python-dotenv`).
C. requests + BeautifulSoup.
D. urllib only.

---

### Q9. Which tools were defined for the browser-vision agent in the unit?

A. `web_search`, `fetch`, `parse`.
B. `search_item_ctrl_f` (Ctrl-F text search on current page, jump to nth match), `go_back` (browser back), `close_popups` (Esc dismiss).
C. `click`, `type`, `screenshot` only.
D. A single `automate_browser` macro.

---

### Q10. The `save_screenshot` callback used with the browser agent is registered via:

A. A decorator.
B. `CodeAgent(..., step_callbacks=[save_screenshot])` — it runs at the end of each step, captures the browser PNG, and attaches it as `step_log.observations_images`.
C. A signal handler.
D. A cron job.

---

### Q11. In the multi-agent worked example (Batman locations + supercar factories + map), the **manager** is the one that:

A. Visits webpages.
B. Owns the `additional_authorized_imports=['geopandas','plotly','shapely','json','pandas','numpy']` so it can build the spatial plot — while delegating web research to `web_agent`.
C. Calls DuckDuckGo directly.
D. Calls the VLM.

---

### Q12. Which of the following is the **closest** to the contract between a manager and a managed agent?

A. The manager directly mutates the managed agent's memory.
B. The managed agent appears in the manager's tool list with its `name` and `description`. The manager invokes it via `web_agent("...task...")`; the managed agent runs its own Think→Act→Observe loop and returns a single string/object back to the manager.
C. They share a single LLM call.
D. The managed agent calls the manager recursively.

---

### Q13. Recall: which is the **biggest practical reason** to switch from `DuckDuckGoSearchTool` to `GoogleSearchTool(provider="serper")` mid-project?

A. Cost.
B. Rate limits — DuckDuckGo's free endpoint rate-limits aggressively; switching to Serper/Serpapi avoids 429s for any non-trivial multi-step run.
C. Ethical concerns.
D. Better UI.

---

### Q14. The Unit 2.1 unit summary calls out two distinctive smolagents abstractions you should leave with. Which pair?

A. `CodeAgent` (code-first ReAct loop, default in smolagents) + Hub-native tool sharing (`@tool` / `Tool` subclass, `push_to_hub`, `from_space`, `from_langchain`, `from_mcp`).
B. `Pipeline` + `Trainer`.
C. `Agent.run_async` + `Agent.train`.
D. `LangChain` + `LangGraph` adapters only.

---

### Q15. To earn the **Unit 2.1 completion** (smolagents framework), you must:

A. Push 5 agents to the Hub.
B. Pass the Unit 2.1 final quiz (hosted on the HF course site) — and the unit assumes you've worked through the Code Agents, Tool-Calling, Tools, Retrieval, Multi-Agent, and Vision sections.
C. Build a multi-agent system live in a Hugging Face Space.
D. Submit to GAIA.

---

## Answer Key + Explanations

| Q | Ans | Why |
|---|-----|-----|
| 1 | **B** | `managed_agents=[web_agent]` is the multi-agent API; the manager calls each managed agent like a tool. |
| 2 | **B** | Verbatim from the "Splitting the task between two agents" subsection. |
| 3 | **B** | `planning_interval` triggers explicit planning steps; it's how the unit improved the single-agent baseline before splitting. |
| 4 | **B** | `final_answer_checks` is the verifier hook. The worked example uses a VLM (GPT-4o) to grade the saved map before accepting. |
| 5 | **A** | The unit explicitly pairs `web_agent`/Qwen 32B Coder (via Together) with `manager_agent`/DeepSeek-R1 for heavier planning. |
| 6 | **B** | `visualize()` prints the hierarchical tree (imports, tools, managed agents) — handy when you forget which tools are wired where. |
| 7 | **B** | The unit names both modes: `task_images` at start, or `observations_images` set by a `step_callback`. |
| 8 | **B** | The browser example uses Helium (high-level wrapper on Selenium) and Selenium. |
| 9 | **B** | Those three are defined verbatim. There's also `save_screenshot` (a callback, not a tool). |
| 10 | **B** | Registered via the `step_callbacks=[...]` kwarg; the callback receives `step_log` and the `agent`. |
| 11 | **B** | The manager owns the plotting imports because it's the one building the final map; the web agent's `additional_authorized_imports=[]` keeps it lean. |
| 12 | **B** | Managed agents are "tools that happen to be agents" — they appear in the manager's tool list and return final answers as observations. |
| 13 | **B** | The unit explicitly calls out DDG's rate limit as the reason `GoogleSearchTool(provider="serper")` (or `serpapi`) is used in non-trivial examples. |
| 14 | **A** | Code-first ReAct + Hub-native tools is the unit's whole identity — that's what differentiates smolagents from JSON-first frameworks. |
| 15 | **B** | The final quiz on the HF course site is the cert mechanism; nothing else is required for this specific sub-unit. |

**Pass mark:** ≥ 12 / 15. If you missed Q1 / Q4 / Q12, re-read "Multi-Agent Systems" before sitting the real quiz.
