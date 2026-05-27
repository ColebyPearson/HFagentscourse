"""
HF Agents Course — Unit 1 first agent.

A smolagents CodeAgent named *Alfred* with a non-trivial toolkit:
- DuckDuckGo web search (smolagents default tool)
- Visit + read a webpage (smolagents default tool)
- get_current_time_in_timezone  — timezone-aware clock
- convert_currency              — FX conversion via the (open) exchangerate.host API
- final_answer                  — terminal tool that closes the loop

The agent uses `InferenceClientModel` (HF Inference Providers) so the only
secret you need on the Space is HF_TOKEN.

Deployment:
    1. Set Space secret `HF_TOKEN` (a token with inference permission).
    2. Push `app.py`, `requirements.txt`, and `prompts.yaml`.
    3. The Gradio UI is launched by `GradioUI(agent).launch()`.
"""
from __future__ import annotations

import datetime
import os

import pytz
import requests
import yaml

from smolagents import (
    CodeAgent,
    DuckDuckGoSearchTool,
    GradioUI,
    InferenceClientModel,
    VisitWebpageTool,
    tool,
)
from smolagents.default_tools import FinalAnswerTool


# ----- Tools ----------------------------------------------------------------

@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """Return the current local time for an IANA timezone.

    Args:
        timezone: An IANA timezone name, e.g. 'America/New_York', 'Asia/Tokyo',
            'Europe/London', 'UTC'.
    """
    try:
        tz = pytz.timezone(timezone)
    except pytz.UnknownTimeZoneError:
        return (
            f"Unknown timezone '{timezone}'. Use an IANA name "
            "(e.g. 'America/New_York', 'Asia/Tokyo', 'UTC')."
        )
    now = datetime.datetime.now(tz)
    return now.strftime("%Y-%m-%d %H:%M:%S %Z (UTC%z)")


@tool
def convert_currency(amount: float, source: str, target: str) -> str:
    """Convert `amount` from currency `source` to currency `target` using
    a live FX rate from the open exchangerate.host API.

    Args:
        amount:  Numeric amount in the source currency.
        source:  3-letter ISO currency code, e.g. 'USD'.
        target:  3-letter ISO currency code, e.g. 'EUR'.

    Returns:
        Human-readable conversion string, e.g. "100 USD = 92.35 EUR @ 0.9235".
    """
    src, tgt = source.upper(), target.upper()
    try:
        r = requests.get(
            "https://api.exchangerate.host/convert",
            params={"from": src, "to": tgt, "amount": amount},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
    except Exception as exc:  # noqa: BLE001
        return f"FX lookup failed: {exc}"

    if not data.get("success", True) or "result" not in data:
        return f"FX lookup returned no result for {src}->{tgt}: {data}"

    rate = data.get("info", {}).get("rate")
    result = data["result"]
    rate_str = f" @ {rate:.4f}" if rate else ""
    return f"{amount} {src} = {result:.2f} {tgt}{rate_str}"


# ----- Model + Prompts ------------------------------------------------------

MODEL_ID = os.environ.get("AGENT_MODEL_ID", "Qwen/Qwen2.5-Coder-32B-Instruct")

model = InferenceClientModel(
    max_tokens=2096,
    temperature=0.5,
    model_id=MODEL_ID,
    custom_role_conversions=None,
)

# Optional: prompts.yaml override. If absent we use smolagents' built-in defaults.
prompt_templates = None
prompts_path = os.path.join(os.path.dirname(__file__), "prompts.yaml")
if os.path.exists(prompts_path):
    with open(prompts_path, "r", encoding="utf-8") as fh:
        prompt_templates = yaml.safe_load(fh)


# ----- Agent ----------------------------------------------------------------

final_answer = FinalAnswerTool()

agent = CodeAgent(
    model=model,
    tools=[
        DuckDuckGoSearchTool(),
        VisitWebpageTool(),
        get_current_time_in_timezone,
        convert_currency,
        final_answer,
    ],
    max_steps=6,
    verbosity_level=1,
    prompt_templates=prompt_templates,
    name="Alfred",
    description=(
        "Alfred is a butler agent who can search the web, read webpages, "
        "tell you the current time in any timezone, and convert currencies."
    ),
)


if __name__ == "__main__":
    GradioUI(agent).launch()
