"""
HF Agents Course — Unit 4 Final Project: GAIA Level-1 agent + submission UI.

This Space exposes a Gradio UI that:
  1. Authenticates the user via the gradio_oauth log-in.
  2. Fetches the 20 GAIA-Level-1 evaluation questions from the official
     course scoring API.
  3. Runs a smolagents CodeAgent on each question (with web search,
     webpage visiting, Python interpreter, and file download tools).
  4. Submits the answers and prints the score returned by the API.

Scoring API: https://agents-course-unit4-scoring.hf.space (see /docs).
"""
from __future__ import annotations

import os
from typing import Any

import gradio as gr
import requests
from smolagents import (
    CodeAgent,
    DuckDuckGoSearchTool,
    InferenceClientModel,
    VisitWebpageTool,
    tool,
)
from smolagents.default_tools import FinalAnswerTool, PythonInterpreterTool


API_URL = "https://agents-course-unit4-scoring.hf.space"
QUESTIONS_URL = f"{API_URL}/questions"
SUBMIT_URL = f"{API_URL}/submit"
FILE_URL = f"{API_URL}/files"

# Allowed Python imports inside the CodeAgent sandbox. Wide-enough to cover
# most GAIA Level-1 questions (date arithmetic, basic table manipulation,
# JSON parsing, regex, etc.) without enabling network or fs access beyond
# what our tools already wrap.
ALLOWED_IMPORTS = [
    "math", "datetime", "json", "re", "statistics", "itertools", "functools",
    "collections", "string", "decimal", "fractions", "calendar", "csv",
    "pandas", "numpy",
]


# ----- Custom tools ---------------------------------------------------------

@tool
def download_task_file(task_id: str) -> str:
    """Download the auxiliary file associated with a GAIA task_id (if any).

    The official Unit 4 scoring API exposes /files/{task_id}. Some questions
    reference an attached image, spreadsheet, audio, PDF, etc. The bytes are
    saved to ./task_files/<task_id>.bin and the absolute path is returned so
    the agent can open / parse it with normal Python.

    Args:
        task_id: The GAIA task identifier (as supplied in each question).
    """
    os.makedirs("task_files", exist_ok=True)
    try:
        r = requests.get(f"{FILE_URL}/{task_id}", timeout=30)
        if r.status_code == 404:
            return "No file attached to this task."
        r.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        return f"Download failed: {exc}"
    path = os.path.abspath(os.path.join("task_files", f"{task_id}.bin"))
    with open(path, "wb") as fh:
        fh.write(r.content)
    return path


# ----- Agent factory --------------------------------------------------------

SYSTEM_HINT = (
    "You are a careful, persistent GAIA benchmark agent. For each question:\n"
    "  1. Plan: identify exactly what fact / list / number is being asked.\n"
    "  2. Act:  use the tools (web search, visit_webpage, python_interpreter,\n"
    "          download_task_file) to gather and verify the answer.\n"
    "  3. Answer: call final_answer(...) with the SHORT, EXACT-MATCH answer\n"
    "          - just the value, no preamble.\n"
    "          - no 'FINAL ANSWER:' prefix.\n"
    "          - numbers as digits, no units unless asked; lists\n"
    "            comma-separated; dates as the question requests.\n"
)


def build_agent() -> CodeAgent:
    model_id = os.environ.get("AGENT_MODEL_ID", "Qwen/Qwen2.5-Coder-32B-Instruct")
    model = InferenceClientModel(model_id=model_id, max_tokens=2048, temperature=0.0)
    return CodeAgent(
        model=model,
        tools=[
            DuckDuckGoSearchTool(),
            VisitWebpageTool(),
            PythonInterpreterTool(),
            download_task_file,
            FinalAnswerTool(),
        ],
        additional_authorized_imports=ALLOWED_IMPORTS,
        max_steps=12,
        verbosity_level=1,
        name="GAIAAgent",
        description=SYSTEM_HINT,
    )


# ----- Runner ---------------------------------------------------------------

def run_one(agent: CodeAgent, q: dict[str, Any]) -> str:
    task_id = q["task_id"]
    question = q["question"]
    has_file = q.get("file_name") not in (None, "")
    prompt = f"task_id: {task_id}\nQuestion: {question}"
    if has_file:
        prompt += (
            f"\n\nThis task has an attached file named {q['file_name']!r}. "
            f"Call download_task_file({task_id!r}) to fetch it, then open it "
            f"with the appropriate Python library."
        )
    return str(agent.run(prompt)).strip()


def run_and_submit(profile: gr.OAuthProfile | None) -> tuple[str, str]:
    if profile is None:
        return "❌ Not logged in. Click 'Sign in with Hugging Face' first.", ""
    username = profile.username

    space_id = os.environ.get("SPACE_ID")
    agent_code_url = (
        f"https://huggingface.co/spaces/{space_id}/tree/main" if space_id else ""
    )

    try:
        r = requests.get(QUESTIONS_URL, timeout=30)
        r.raise_for_status()
        questions = r.json()
    except Exception as exc:  # noqa: BLE001
        return f"Failed to fetch questions: {exc}", ""

    agent = build_agent()
    answers, transcript_rows = [], []
    for q in questions:
        try:
            answer = run_one(agent, q)
        except Exception as exc:  # noqa: BLE001
            answer = f"AGENT_ERROR: {exc}"
        answers.append({"task_id": q["task_id"], "submitted_answer": answer})
        transcript_rows.append(
            f"- **{q['task_id']}** — {q['question'][:120]}…\n   →  `{answer[:200]}`"
        )

    payload = {
        "username": username,
        "agent_code": agent_code_url,
        "answers": answers,
    }
    try:
        resp = requests.post(SUBMIT_URL, json=payload, timeout=120)
        resp.raise_for_status()
        result = resp.json()
    except Exception as exc:  # noqa: BLE001
        return f"Submit failed: {exc}", "\n".join(transcript_rows)

    summary = (
        f"### Score: **{result.get('score', '?')}**  "
        f"({result.get('correct_count', '?')} / {result.get('total_attempted', '?')})\n\n"
        f"{result.get('message', '')}"
    )
    return summary, "\n".join(transcript_rows)


# ----- Gradio UI ------------------------------------------------------------

with gr.Blocks(title="GAIA Unit 4 Agent — VoicesColeby") as demo:
    gr.Markdown("# 🦇 GAIA Unit 4 — Final Project Agent")
    gr.Markdown(
        "smolagents `CodeAgent` (Qwen2.5-Coder-32B via HF Inference Providers) "
        "with web_search, visit_webpage, python_interpreter, download_task_file, "
        "and final_answer. Click **Run + Submit** below to evaluate against the "
        "20 GAIA-Level-1 questions and post the score to the Students leaderboard."
    )
    gr.LoginButton()
    run_btn = gr.Button("🚀 Run + Submit", variant="primary")
    score_md = gr.Markdown(label="Score")
    transcript = gr.Markdown(label="Per-question answers")
    run_btn.click(fn=run_and_submit, inputs=None, outputs=[score_md, transcript])


if __name__ == "__main__":
    demo.launch(debug=False)
