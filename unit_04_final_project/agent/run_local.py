"""
Run the Unit 4 GAIA agent locally against the official scoring API's
question set, collect answers, but DO NOT POST /submit.

Improvements over v1:
  - The guidance is PREPENDED to each task string. (In smolagents,
    CodeAgent(description=...) is sub-agent metadata and does NOT become
    the system prompt, so v1's SYSTEM_HINT never reached the model.)
  - Hard instruction to return a concrete short value, never a narration.
  - The 5 file-bearing questions are unanswerable through this scoring
    API (the /files/{task_id} endpoint returns 404 "No file path
    associated"), so by default we skip them to save inference quota
    instead of letting the agent hallucinate. Pass --include-files to
    attempt them anyway.

  PYTHONUTF8=1 python run_local.py [--include-files] [--only N]
"""
from __future__ import annotations

import json
import os
import sys
import time
from typing import Any

import requests
from smolagents import (
    CodeAgent,
    DuckDuckGoSearchTool,
    InferenceClientModel,
    VisitWebpageTool,
    tool,
)
from smolagents.default_tools import FinalAnswerTool, PythonInterpreterTool


API = "https://agents-course-unit4-scoring.hf.space"
QUESTIONS_URL = f"{API}/questions"
FILE_URL = f"{API}/files"

ALLOWED_IMPORTS = [
    "math", "datetime", "json", "re", "statistics", "itertools", "functools",
    "collections", "string", "decimal", "fractions", "calendar", "csv",
    "pandas", "numpy",
]

# Prepended to every task. This is what actually reaches the model.
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


@tool
def download_task_file(task_id: str) -> str:
    """Download the auxiliary file associated with a GAIA task_id (if any).

    Returns the absolute path to ./task_files/<task_id>.bin so the agent
    can open it with the appropriate Python library, or a message if no
    file is mapped on the scoring server.

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


def main() -> None:
    include_files = "--include-files" in sys.argv
    only = None
    if "--only" in sys.argv:
        only = int(sys.argv[sys.argv.index("--only") + 1])

    print("== fetching questions ==")
    r = requests.get(QUESTIONS_URL, timeout=30)
    r.raise_for_status()
    questions = r.json()
    print(f"   got {len(questions)} questions")

    print("\n== building agent ==")
    agent = build_agent()

    answers, transcript = [], []
    attempted = 0
    for i, q in enumerate(questions, 1):
        tid = q["task_id"]
        prompt = q["question"]
        has_file = q.get("file_name") not in (None, "")

        if has_file and not include_files:
            # Unanswerable via this API (files 404). Record an empty answer
            # so the task_id is still present in the submission payload.
            print(f"\n[{i:2d}/{len(questions)}] {tid}  SKIP (file question, not served by API)")
            answers.append({"task_id": tid, "submitted_answer": ""})
            transcript.append({"task_id": tid, "question": prompt, "answer": "",
                               "seconds": 0.0, "had_file": True, "skipped": True})
            continue

        if only is not None and attempted >= only:
            break
        attempted += 1

        print(f"\n[{i:2d}/{len(questions)}] {tid} (file={has_file})")
        print(f"  Q: {prompt[:200]}")
        t0 = time.time()
        try:
            ans = run_one(agent, q)
        except Exception as exc:  # noqa: BLE001
            ans = f"AGENT_ERROR: {exc}"
        dt = time.time() - t0
        print(f"  A ({dt:.1f}s): {ans[:300]}")
        answers.append({"task_id": tid, "submitted_answer": ans})
        transcript.append({"task_id": tid, "question": prompt, "answer": ans,
                           "seconds": round(dt, 1), "had_file": has_file,
                           "skipped": False})

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gaia_run_local.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"answers": answers, "transcript": transcript}, f, indent=2)
    print(f"\n== Done. Wrote {out} ({len(answers)} answers). NOT POSTed. ==")


if __name__ == "__main__":
    main()
