"""
HF Agents Course — Unit 3 use case: "Alfred at the Gala".

A smolagents `CodeAgent` (Qwen 2.5-Coder-32B via HF Inference Providers) with:
- guest_info_retriever — BM25 over `agents-course/unit3-invitees`.
- web_search + visit_webpage — for live info about guests / topics.
- fireworks_weather — pulls a tiny weather feature from open-meteo for
  Gotham (40.71°N, 74.01°W) and returns a textual go/no-go for fireworks.
- hub_stats — looks up an AI builder's top downloaded model on the HF Hub.
- final_answer — terminal tool.

Wrapped in a Gradio chat UI.
"""
from __future__ import annotations

import os
from typing import Any

import datasets
import gradio as gr
import requests
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from smolagents import (
    CodeAgent,
    DuckDuckGoSearchTool,
    InferenceClientModel,
    Tool,
    VisitWebpageTool,
    tool,
)
from smolagents.default_tools import FinalAnswerTool


# ----- Guest retriever (BM25 over the official dataset) ---------------------

def _build_guest_docs() -> list[Document]:
    ds = datasets.load_dataset("agents-course/unit3-invitees", split="train")
    return [
        Document(
            page_content="\n".join([
                f"Name: {g['name']}",
                f"Relation: {g['relation']}",
                f"Description: {g['description']}",
                f"Email: {g['email']}",
            ]),
            metadata={"name": g["name"]},
        )
        for g in ds
    ]


class GuestInfoRetrieverTool(Tool):
    name = "guest_info_retriever"
    description = (
        "Retrieves detailed information about gala guests by name or relation. "
        "Returns up to 3 matching dossiers (name, relation, description, email)."
    )
    inputs = {
        "query": {
            "type": "string",
            "description": "Name or relation to search for, e.g. 'Ada Lovelace' or 'mathematician'.",
        }
    }
    output_type = "string"

    def __init__(self, docs: list[Document]):
        super().__init__()
        self.retriever = BM25Retriever.from_documents(docs)

    def forward(self, query: str) -> str:
        results = self.retriever.invoke(query)
        if not results:
            return "No matching guest information found."
        return "\n\n".join(doc.page_content for doc in results[:3])


# ----- Custom tools ---------------------------------------------------------

@tool
def fireworks_weather(latitude: float = 40.71, longitude: float = -74.01) -> str:
    """Tiny weather check for the gala's outdoor fireworks. Defaults to Gotham
    coordinates (lat 40.71, lon -74.01). Uses the free open-meteo API; no key.

    Args:
        latitude:  Latitude in decimal degrees.
        longitude: Longitude in decimal degrees.

    Returns:
        Human-readable verdict including temperature, windspeed, and a
        go / no-go recommendation for the fireworks.
    """
    try:
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude, "longitude": longitude,
                "current_weather": "true",
            }, timeout=15,
        )
        r.raise_for_status()
        cw = r.json().get("current_weather", {})
    except Exception as exc:  # noqa: BLE001
        return f"Weather lookup failed: {exc}"

    temp_c = cw.get("temperature")
    wind = cw.get("windspeed")
    code = cw.get("weathercode")
    # open-meteo WMO weather codes: 0=clear, 1-3=mostly clear/partly cloudy,
    # 45/48=fog, 51-67=rain, 80-82=showers, 95-99=thunderstorm
    bad = (code in {45, 48} or (51 <= code <= 67) or
           (80 <= code <= 82) or (95 <= code <= 99) or
           (wind is not None and wind > 35))
    verdict = ("🚫 NO-GO: weather/wind unsafe for fireworks."
               if bad else "✅ GO: clear-enough skies for fireworks.")
    return (
        f"Current weather (lat={latitude}, lon={longitude}): "
        f"{temp_c}°C, wind {wind} km/h, WMO code {code}.  →  {verdict}"
    )


@tool
def hub_stats(author: str) -> str:
    """Look up the **most downloaded** model on the HF Hub for a given author
    or organization. Useful when Alfred needs talking points about an AI
    builder guest.

    Args:
        author: HF Hub username or org id (e.g. 'facebook', 'google', 'meta-llama').

    Returns:
        Top model id and download count, or an error string.
    """
    try:
        from huggingface_hub import list_models
        models = list(list_models(author=author, sort="downloads", limit=1))
    except Exception as exc:  # noqa: BLE001
        return f"Hub stats lookup failed: {exc}"
    if not models:
        return f"No public models found for author {author!r}."
    m = models[0]
    return (
        f"Top model for {author!r}: {m.id} "
        f"({getattr(m, 'downloads', '?'):,} downloads)"
    )


# ----- Agent factory --------------------------------------------------------

def build_agent() -> CodeAgent:
    docs = _build_guest_docs()
    guest_tool = GuestInfoRetrieverTool(docs)
    model_id = os.environ.get("AGENT_MODEL_ID", "Qwen/Qwen2.5-Coder-32B-Instruct")
    model = InferenceClientModel(model_id=model_id, max_tokens=2048, temperature=0.4)
    return CodeAgent(
        model=model,
        tools=[
            guest_tool,
            DuckDuckGoSearchTool(),
            VisitWebpageTool(),
            fireworks_weather,
            hub_stats,
            FinalAnswerTool(),
        ],
        max_steps=8,
        verbosity_level=1,
        name="Alfred-Gala",
        description=(
            "Alfred, butler at Wayne Manor, helping host this evening's gala. "
            "Knows the guest list (via guest_info_retriever), the weather "
            "(fireworks_weather), and basic AI-Hub stats for any AI-builder "
            "guests (hub_stats). Can also search the web when needed."
        ),
    )


AGENT = None  # lazy-initialized so the Space can boot before BM25 indexing


def respond(message: str, _history: list[Any] | None = None) -> str:
    global AGENT  # noqa: PLW0603
    if AGENT is None:
        AGENT = build_agent()
    return str(AGENT.run(message)).strip()


with gr.Blocks(title="Alfred — Unit 3 Gala Agent") as demo:
    gr.Markdown("# 🎩 Alfred — Unit 3 Gala Agent")
    gr.Markdown(
        "Agentic-RAG demo over the `agents-course/unit3-invitees` dataset, "
        "with optional web search, a weather check for the fireworks, and "
        "HF Hub stats lookup for AI-builder guests."
    )
    gr.ChatInterface(
        fn=respond,
        type="messages",
        examples=[
            "Tell me about our guest named 'Lady Ada Lovelace'.",
            "Which mathematicians are on the guest list?",
            "Is the weather good enough for fireworks tonight?",
            "What's the top model for the 'facebook' org on the Hub?",
        ],
        title=None,
    )


if __name__ == "__main__":
    demo.launch()
