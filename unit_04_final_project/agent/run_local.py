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
        max_steps=8,
        verbosity_level=1,
        name="GAIAAgent",
    )


def _build_prompt(q: dict[str, Any]) -> str:
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
    return prompt


def run_one(agent: CodeAgent, q: dict[str, Any], cooldown: float = 45.0) -> str:
    """Run one question. HF Inference Providers' free tier throttles bursts
    (the CodeAgent fires many calls per question); on a 402/429 we cool down
    and retry the whole question once with a fresh agent."""
    prompt = _build_prompt(q)
    try:
        return str(agent.run(prompt)).strip()
    except Exception as exc:  # noqa: BLE001
        msg = str(exc)
        if "402" in msg or "429" in msg or "rate" in msg.lower():
            print(f"   …throttled ({'402' if '402' in msg else '429'}); cooling down {cooldown:.0f}s and retrying once")
            time.sleep(cooldown)
            try:
                return str(build_agent().run(prompt)).strip()
            except Exception as exc2:  # noqa: BLE001
                return f"AGENT_ERROR: {exc2}"
        return f"AGENT_ERROR: {exc}"


def main() -> None:
    include_files = "--include-files" in sys.argv
    only = None
    if "--only" in sys.argv:
        only = int(sys.argv[sys.argv.index("--only") + 1])

    resume = "--resume" in sys.argv
    gap = 15.0  # seconds between questions to stay under the burst-rate throttle
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gaia_run_local.json")

    print("== fetching questions ==")
    r = requests.get(QUESTIONS_URL, timeout=30)
    r.raise_for_status()
    questions = r.json()
    print(f"   got {len(questions)} questions")

    # Resume: keep prior good (non-error, non-empty) answers so we don't
    # re-burn quota on questions that already succeeded.
    prior: dict[str, dict] = {}
    if resume and os.path.exists(out):
        with open(out, "r", encoding="utf-8") as f:
            for t in json.load(f).get("transcript", []):
                prior[t["task_id"]] = t
        good = sum(1 for t in prior.values()
                   if t.get("answer") and not t["answer"].startswith("AGENT_ERROR")
                   and not t.get("skipped"))
        print(f"   resume: {good} prior good answers retained")

    print("\n== building agent ==")
    agent = build_agent()

    answers, transcript = [], []
    attempted = 0
    for i, q in enumerate(questions, 1):
        tid = q["task_id"]
        prompt = q["question"]
        has_file = q.get("file_name") not in (None, "")

        if has_file and not include_files:
            print(f"\n[{i:2d}/{len(questions)}] {tid}  SKIP (file question, not served by API)")
            answers.append({"task_id": tid, "submitted_answer": ""})
            transcript.append({"task_id": tid, "question": prompt, "answer": "",
                               "seconds": 0.0, "had_file": True, "skipped": True})
            continue

        # Resume: reuse a prior good answer.
        p = prior.get(tid)
        if (resume and p and p.get("answer")
                and not p["answer"].startswith("AGENT_ERROR") and not p.get("skipped")):
            print(f"\n[{i:2d}/{len(questions)}] {tid}  REUSE -> {p['answer'][:80]!r}")
            transcript.append(p)
            answers.append({"task_id": tid, "submitted_answer": p["answer"]})
            continue

        if only is not None and attempted >= only:
            break
        if attempted > 0:
            time.sleep(gap)  # throttle between live questions
        attempted += 1

        print(f"\n[{i:2d}/{len(questions)}] {tid} (file={has_file})")
        print(f"  Q: {prompt[:200]}")
        t0 = time.time()
        ans = run_one(agent, q)
        dt = time.time() - t0
        print(f"  A ({dt:.1f}s): {ans[:300]}")
        answers.append({"task_id": tid, "submitted_answer": ans})
        transcript.append({"task_id": tid, "question": prompt, "answer": ans,
                           "seconds": round(dt, 1), "had_file": has_file,
                           "skipped": False})
        # Checkpoint after every question so a mid-run throttle doesn't lose progress.
        with open(out, "w", encoding="utf-8") as f:
            json.dump({"answers": answers, "transcript": transcript}, f, indent=2)

    with open(out, "w", encoding="utf-8") as f:
        json.dump({"answers": answers, "transcript": transcript}, f, indent=2)
    nonerr = sum(1 for t in transcript if t["answer"] and not t["answer"].startswith("AGENT_ERROR") and not t.get("skipped"))
    print(f"\n== Done. Wrote {out}. {nonerr} concrete answers, NOT POSTed. ==")


if __name__ == "__main__":
    main()
