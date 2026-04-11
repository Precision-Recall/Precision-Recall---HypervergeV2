"""
Skill loader for the forensic engine.
Same pattern as agent_system/skill_loader.py — reads SKILL.md files
with YAML frontmatter and injects them into the system prompt at startup.
"""

import yaml
from pathlib import Path

SKILLS_DIR = Path(__file__).parent / "skills"


def _parse_skill(filepath: Path) -> dict:
    """Parse a SKILL.md file with YAML frontmatter."""
    text = filepath.read_text()
    if not text.startswith("---"):
        return {"name": filepath.parent.name, "description": "", "content": text}

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {"name": filepath.parent.name, "description": "", "content": text}

    meta = yaml.safe_load(parts[1]) or {}
    content = parts[2].strip()
    return {"name": meta.get("name", filepath.parent.name), "description": meta.get("description", ""), "content": content}


def load_all_skills() -> dict[str, dict]:
    """Load all SKILL.md files. Returns dict keyed by skill name."""
    skills = {}
    if not SKILLS_DIR.exists():
        return skills
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_file = skill_dir / "SKILL.md"
        if skill_file.exists():
            skill = _parse_skill(skill_file)
            skills[skill["name"]] = skill
    return skills


def skills_to_prompt(skills: list[dict]) -> str:
    """Convert loaded skills into a prompt section."""
    if not skills:
        return ""
    sections = []
    for skill in skills:
        sections.append(f"### {skill['name']}\n{skill['description']}\n\n{skill['content']}")
    return "\n\n---\n\n".join(sections)
