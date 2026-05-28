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
            return "No file is mapped for this task on the scoring server; answer from the question text alone if possible."
        r.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        return f"Download failed: {exc}"
    path = os.path.abspath(os.path.join("task_files", f"{task_id}.bin"))
    with open(path, "wb") as fh:
        fh.write(r.content)
    return path


# ----- Agent factory --------------------------------------------------------

# NOTE: In smolagents, CodeAgent(description=...) is sub-agent metadata and
# is NOT injected as a system prompt. To reliably steer the model we PREPEND
# this guidance to every task string in run_one().
GUIDANCE = """You are a GAIA benchmark agent. Your answer is graded by EXACT STRING MATCH against a short ground-truth, so formatting is critical.

RULES:
- Your final_answer MUST be the bare value only — a name, number, word, or comma-separated list. NEVER a sentence, never an explanation, never "I will look this up".
- No "FINAL ANSWER:" prefix. No trailing period. No units unless the question explicitly asks for them.
- Numbers as digits (e.g. 42, not "forty-two"). Lists comma-separated in the exact order requested.
- READ THE QUESTION LITERALLY. If it is a riddle or reversed/encoded text, decode it first and answer exactly what it asks.
- Use web_search + visit_webpage to find and VERIFY facts. If one search query fails or times out, reformulate and try again (vary keywords, try the Wikipedia page directly).
- If after genuine effort you still cannot verify the answer, return your single best concrete guess in the correct format anyway — a wrong short value scores the same as a narration (zero), but a right guess scores.

QUESTION:
"""


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
    )


# ----- Runner ---------------------------------------------------------------

def run_one(agent: CodeAgent, q: dict[str, Any]) -> str:
    task_id = q["task_id"]
    question = q["question"]
    has_file = q.get("file_name") not in (None, "")
    prompt = f"{GUIDANCE}task_id: {task_id}\n{question}"
    if has_file:
        prompt += (
            f"\n\n(There may be a file named {q['file_name']!r}. Try "
            f"download_task_file({task_id!r}); if it reports no file is "
            f"mapped, answer from the text if you can, else give your best guess.)"
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
