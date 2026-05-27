# Unit 1 — Final Quiz Prep (smolagents tutorial + comprehensive)

> Self-graded practice mirroring the certifying Unit 1 final quiz.
> Covers: the smolagents `CodeAgent` template, `@tool` decorator, `InferenceClientModel`, deploying as a HF Space, plus integration questions touching all of Unit 1.
> Format: 15 multiple-choice questions. Answers + explanations at the bottom.

---

### Q1. Which import is **required** to build the Unit 1 tutorial agent?

A. `from langchain import Agent`
B. `from smolagents import CodeAgent, InferenceClientModel, tool`
C. `from openai import Agent`
D. `from transformers import AutoAgent`

---

### Q2. In a smolagents `@tool`-decorated function, which of these is **required** for the tool description to be auto-built correctly?

```python
@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """A tool that fetches the current local time in a specified timezone.
    Args:
        timezone: A string representing a valid timezone (e.g., 'America/New_York').
    """
    ...
```

A. Type hints on **both** the argument(s) and the return.
B. A docstring that describes the tool and lists each argument under an `Args:` block.
C. A sensible function name.
D. **All of the above** — smolagents uses `inspect` to read them, and missing any one degrades the tool description.

---

### Q3. What is `FinalAnswerTool()` / `final_answer` in the template?

A. A placeholder that does nothing.
B. The terminal tool that signals the CodeAgent's loop is done and returns the final response to the user — **must not** be removed from the `tools=[...]` list.
C. The model itself.
D. A required prompt template.

---

### Q4. The Unit 1 template uses `InferenceClientModel(... model_id='Qwen/Qwen2.5-Coder-32B-Instruct', ...)`. Where is that model actually executing?

A. Locally on your laptop CPU.
B. On the Hugging Face **Inference Providers** (serverless API), authenticated via the `HF_TOKEN` you set on the Space.
C. In your browser via WebGPU.
D. In a Colab GPU you started.

---

### Q5. Where do you set the `HF_TOKEN` secret for a duplicated HF Space?

A. In `app.py` as a hardcoded string.
B. In the Space's **Settings → Variables and Secrets → New Secret**, with name `HF_TOKEN`.
C. In `requirements.txt`.
D. Hugging Face does not support secrets.

---

### Q6. Why does the template store the system prompt in a separate `prompts.yaml` file?

A. To bypass HF Hub size limits.
B. So it's easy to customize / version / reuse across agents — the `prompt_templates` dict is loaded with `yaml.safe_load` and passed to `CodeAgent(prompt_templates=...)`.
C. YAML executes faster than Python strings.
D. It's the only way to define a system prompt.

---

### Q7. Why is the `max_steps=6` parameter on `CodeAgent` important?

A. It limits the number of tools you can register.
B. It caps how many Thought→Action→Observation iterations the agent runs before giving up — guards against infinite loops and runaway cost.
C. It sets the max prompt length.
D. It's purely cosmetic.

---

### Q8. The user asks the agent "what time is it in Tokyo?" and the registered tools are `get_current_time_in_timezone` and `final_answer`. What does the agent's first **action** likely look like (CodeAgent style)?

A. A JSON blob with `"action": "tokyo"`.
B. A Python code block that calls `get_current_time_in_timezone(timezone="Asia/Tokyo")`, prints the result, then on a subsequent step calls `final_answer(...)`.
C. A direct natural-language response, no tool call.
D. A SQL query.

---

### Q9. After your duplicated Space is configured and `app.py` is updated, what's the **fastest** way to test the agent without leaving the HF UI?

A. Clone the repo locally and run it on your laptop only.
B. Push to `main` and use the auto-generated Gradio UI on the Space itself (the template ends with `GradioUI(agent).launch()`).
C. SSH into HF infrastructure.
D. Email Hugging Face support.

---

### Q10. Which is the most accurate summary of how a CodeAgent **executes** code from the LLM?

A. The code is sent to the user's browser to run.
B. smolagents parses the code block from the LLM's assistant turn, runs it in a restricted Python executor (with the registered tools available as functions), captures stdout, and appends the result as an Observation.
C. It compiles to C++ first.
D. It writes the code to disk and runs `subprocess.run("python file.py")` with no sandboxing.

---

### Q11. Recall: the **agency-spectrum** row for a CodeAgent that loops Thought→Action→Observation until it emits `final_answer` is:

A. Simple processor (☆☆☆)
B. Router (★☆☆)
C. Tool caller (★★☆)
D. Multi-step agent (★★★)

---

### Q12. Pick the **most accurate** statement about the relationship between Tools and Actions.

A. They're identical.
B. Tools are external resources / functions; Actions are the steps the agent takes — and a single Action may compose multiple tools (or no tool at all, in the case of `final_answer`).
C. Tools can only be HTTP APIs; everything else is an Action.
D. Actions are physical only; tools are digital only.

---

### Q13. You want to add a DuckDuckGo web-search capability to your agent. The smallest correct change to the template is:

A. Train a new model.
B. `from smolagents import DuckDuckGoSearchTool` (already in the template's imports) and add `DuckDuckGoSearchTool()` (or `DuckDuckGoSearchTool` instance) to the `tools=[final_answer, DuckDuckGoSearchTool()]` list.
C. Re-write the system prompt by hand.
D. Switch to LangGraph.

---

### Q14. Pick the statement that is **false** about the Unit 1 agent.

A. The system prompt embeds the available tool descriptions.
B. The LLM cannot truly *see* tool source code; it only sees their textual descriptions.
C. The agent will autonomously train itself between conversations.
D. The loop terminates when the agent calls `final_answer(...)` or hits `max_steps`.

---

### Q15. To earn the **Certificate of Fundamentals** for Unit 1, you must:

A. Push 10 models to the Hub.
B. Pass the Unit 1 quiz hosted in the `agents-course/unit_1_quiz` Space — and click **Submit** so the score is saved.
C. Complete the GAIA leaderboard challenge.
D. Pay a fee.

---

## Answer Key + Explanations

| Q | Ans | Why |
|---|-----|-----|
| 1 | **B** | The template imports `CodeAgent`, `InferenceClientModel`, `tool` (plus `DuckDuckGoSearchTool`, `load_tool`) from `smolagents`. No LangChain/OpenAI/transformers `Agent`. |
| 2 | **D** | The unit lists all three (type hints + Args-style docstring + meaningful function name); smolagents uses `inspect` so each one feeds the auto-built description. |
| 3 | **B** | `final_answer` is the terminal tool — the loop exits when the LLM calls it. The template comment explicitly says "don't remove final_answer". |
| 4 | **B** | `InferenceClientModel` hits HF's Inference Providers serverless API. The Space needs the `HF_TOKEN` secret to authenticate. |
| 5 | **B** | Spaces secrets live under **Settings → Variables and Secrets → New Secret**. Hardcoding tokens in source is a no-no. |
| 6 | **B** | `prompts.yaml` separates prompt from code → easy to swap / version / reuse. The template loads it with `yaml.safe_load` and passes the dict to `CodeAgent(prompt_templates=...)`. |
| 7 | **B** | `max_steps` is the runtime's safety hatch — without it a misbehaving model could spin forever and rack up calls. |
| 8 | **B** | A CodeAgent emits Python. `get_current_time_in_timezone(timezone="Asia/Tokyo")` first → result observed → `final_answer(...)` next step. |
| 9 | **B** | The template ends with `GradioUI(agent).launch()`, so the Space exposes a chat UI for free. Push to main, wait for build, click around. |
| 10 | **B** | CodeAgent uses a restricted Python executor with the registered tools as callables, captures output, appends as observation. Not subprocess, not browser, not C++. |
| 11 | **D** | A multi-step agent (iterates Thought→Action→Observation until done) is ★★★. The "Tool caller" rung is one-shot. |
| 12 | **B** | The unit explicitly says "Actions are not the same as Tools — an Action can use multiple Tools." `final_answer` is an action that doesn't call an external tool either. |
| 13 | **B** | `DuckDuckGoSearchTool` is already imported. Just instantiate it and add it to `tools=[...]`. That's the smolagents "add a tool" minimum diff. |
| 14 | **C** | Agents don't train between conversations — that's continual learning / fine-tuning, an entirely separate process. A, B, D are all true. |
| 15 | **B** | The Unit 1 quiz Space gates the certificate; you must click **Submit** so the score is saved. (Other certs need more — Excellence requires Unit 1 + a use case + the GAIA challenge.) |

**Pass mark:** ≥ 12 / 15 to feel confident going into the certifying quiz. If you missed Q3, Q7, Q11, or Q14, re-read the smolagents tutorial section before sitting the real quiz.
