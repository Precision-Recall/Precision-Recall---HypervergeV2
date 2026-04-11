"""
Skill loader — reads SKILL.md files with YAML frontmatter.
Inspired by Claude Code's skill system: skills are external markdown files
with structured metadata that get loaded into agent prompts dynamically.

Benefits:
- Skills are editable without touching Python code
- Only relevant skills are loaded per agent (reduces context window)
- YAML frontmatter provides structured metadata for routing
"""

import os
import yaml
from pathlib import Path

SKILLS_DIR = Path(__file__).parent / "skills"


def _parse_skill(filepath: Path) -> dict:
    """Parse a SKILL.md file with YAML frontmatter."""
    text = filepath.read_text()

    if not text.startswith("---"):
        return {"name": filepath.parent.name, "description": "", "content": text}

    # Split YAML frontmatter from content
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {"name": filepath.parent.name, "description": "", "content": text}

    meta = yaml.safe_load(parts[1]) or {}
    content = parts[2].strip()

    return {
        "name": meta.get("name", filepath.parent.name),
        "description": meta.get("description", ""),
        "content": content,
        **meta,
    }


def load_all_skills() -> dict[str, dict]:
    """Load all SKILL.md files from the skills directory.
    
    Returns dict keyed by skill name.
    """
    skills = {}
    if not SKILLS_DIR.exists():
        return skills

    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_file = skill_dir / "SKILL.md"
        if skill_file.exists():
            skill = _parse_skill(skill_file)
            skills[skill["name"]] = skill

    return skills


def load_skills_for_agent(agent_name: str) -> list[dict]:
    """Load only skills relevant to a specific agent.
    
    Matches by agent name appearing in the skill name or description.
    """
    all_skills = load_all_skills()
    
    # Mapping: agent → skill names
    AGENT_SKILLS = {
        "temporal-reasoner": [
            "temporal-reasoner",
            "year-range-retriever",
            "metric-trend-extractor",
            "narrative-diff",
            "timeline-synthesizer",
            "pivot-detector",
            "quarter-drill-down",
        ],
        "cross-entity": [
            "cross-entity",
            "multi-company-retriever",
            "metric-comparator",
            "terminology-normalizer",
            "sector-peer-finder",
            "cross-temporal-benchmarker",
        ],
    }

    skill_names = AGENT_SKILLS.get(agent_name, list(all_skills.keys()))
    return [all_skills[name] for name in skill_names if name in all_skills]


def skills_to_prompt(skills: list[dict]) -> str:
    """Convert loaded skills into a prompt section.
    
    Only includes the content (not the full markdown), keeping context window small.
    """
    if not skills:
        return ""

    sections = []
    for skill in skills:
        sections.append(f"### {skill['name']}\n{skill['description']}\n\n{skill['content']}")

    return "\n\n---\n\n".join(sections)
