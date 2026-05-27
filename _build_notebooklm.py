"""Build notebooklm/<slug>.txt and <slug>/README.md from the cloned source.

The agents-course toctree mixes regular units, bonus units, sub-units
(unit2 has smolagents / llama-index / langgraph), and a Live recap. We
walk the top-level toctree entries and assign each one a stable slug
based on its title.

Re-run any time the upstream course updates (after `git -C _source pull`).
"""
from __future__ import annotations
import re
from pathlib import Path
import yaml

ROOT = Path(__file__).parent
SRC = ROOT / "_source" / "units" / "en"
NLM = ROOT / "notebooklm"
NLM.mkdir(exist_ok=True)

toc = yaml.safe_load((SRC / "_toctree.yml").read_text(encoding="utf-8"))

FRONTMATTER = re.compile(r"^---\n.*?\n---\n", re.DOTALL)
IMPORTS = re.compile(r"^import\s+.*$", re.MULTILINE)


def slugify(title: str) -> str:
    """Title → stable folder-friendly slug.

    Examples:
      "Unit 0. Welcome to the course"      -> unit_00_welcome
      "Live 1. How the course works..."    -> live_01
      "Unit 1. Introduction to Agents"     -> unit_01_introduction
      "Unit 2. Frameworks for AI Agents"   -> unit_02_frameworks
      "Unit 2.1 The smolagents framework"  -> unit_02_1_smolagents
      "Unit 2.2 The LlamaIndex framework"  -> unit_02_2_llamaindex
      "Unit 2.3 The LangGraph framework"   -> unit_02_3_langgraph
      "Unit 3. Use Case for Agentic RAG"   -> unit_03_agentic_rag
      "Unit 4. Final Project - Create..."  -> unit_04_final_project
      "Bonus Unit 1. Fine-tuning..."       -> bonus_01_function_calling
    """
    overrides = {
        "Unit 0. Welcome to the course": "unit_00_welcome",
        "Live 1. How the course works and Q&A": "live_01",
        "Unit 1. Introduction to Agents": "unit_01_introduction",
        "Unit 2. Frameworks for AI Agents": "unit_02_frameworks",
        "Unit 2.1 The smolagents framework": "unit_02_1_smolagents",
        "Unit 2.2 The LlamaIndex framework": "unit_02_2_llamaindex",
        "Unit 2.3 The LangGraph framework": "unit_02_3_langgraph",
        "Unit 3. Use Case for Agentic RAG": "unit_03_agentic_rag",
        "Unit 4. Final Project - Create, Test, and Certify Your Agent": "unit_04_final_project",
        "Bonus Unit 1. Fine-tuning an LLM for Function-calling": "bonus_01_function_calling",
        "Bonus Unit 2. Agent Observability and Evaluation": "bonus_02_observability",
        "Bonus Unit 3. Agents in Games with Pokemon": "bonus_03_pokemon",
    }
    return overrides.get(title, re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_"))


def clean(text: str) -> str:
    text = FRONTMATTER.sub("", text, count=1)
    text = IMPORTS.sub("", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"


def find_source(local: str) -> Path | None:
    for ext in (".mdx", ".md"):
        p = SRC / f"{local}{ext}"
        if p.exists():
            return p
    return None


unit_url_base = "https://huggingface.co/learn/agents-course/"


for unit in toc:
    title = unit["title"]
    sections = unit["sections"]
    slug = slugify(title)
    folder = ROOT / slug
    folder.mkdir(exist_ok=True)

    # notebooklm/<slug>.txt
    parts = [f"# {title}\n"]
    for s in sections:
        local = s["local"]
        sec_title = s["title"]
        path = find_source(local)
        if not path:
            parts.append(f"\n\n## {sec_title}\n\n[missing source: {local}.md(x)]\n")
            continue
        parts.append(f"\n\n## {sec_title}\n\n{clean(path.read_text(encoding='utf-8'))}")
    (NLM / f"{slug}.txt").write_text("".join(parts), encoding="utf-8")

    # <slug>/README.md
    lines = [
        f"# {title}",
        "",
        f"Official chapter URL base: {unit_url_base}{sections[0]['local'].split('/', 1)[0]}/",
        f"NotebookLM source: [`notebooklm/{slug}.txt`](../notebooklm/{slug}.txt)",
        "",
        "## Chapters (in order)",
        "",
    ]
    for s in sections:
        lines.append(f"- **{s['title']}** — {unit_url_base}{s['local']}")
    has_quiz = any("quiz" in s["local"].lower() for s in sections)
    is_lecture = not has_quiz and slug not in ("unit_00_welcome", "live_01")
    lines += ["", "## Status", "", "- [ ] Read all chapters (or listen via NotebookLM)"]
    if any(s["local"].endswith(("/tutorial", "/hands-on", "/fine-tuning",
                                "/building_your_pokemon_agent",
                                "/launching_agent_battle",
                                "/monitoring-and-evaluating-agents-notebook",
                                "/document_analysis_agent", "/first_graph",
                                "/agent", "/invitees", "/tools",
                                "/code_agents", "/tool_calling_agents",
                                "/retrieval_agents", "/multi_agent_systems",
                                "/vision_agents", "/workflows", "/agents")) for s in sections):
        lines.append("- [ ] Hands-on artifact (in this folder)")
    if has_quiz:
        for s in sections:
            if "quiz" in s["local"].lower():
                lines.append(f"- [ ] {s['title']} (≥ 70% on the HF course site)")
    lines.append("")
    (folder / "README.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"{slug}: {len(sections)} chapter(s) -> notebooklm/{slug}.txt + {slug}/README.md")
