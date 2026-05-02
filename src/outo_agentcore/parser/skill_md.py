import re
from pathlib import Path
from outo_agentcore.core.skill import Skill


def parse_skill_md(skill_dir: Path) -> Skill:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError(f"SKILL.md not found in: {skill_dir}")

    content = skill_md.read_text().strip()
    if not content:
        raise ValueError(f"SKILL.md is empty: {skill_md}")

    frontmatter = {}
    instructions = content

    frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
    if frontmatter_match:
        frontmatter_text = frontmatter_match.group(1)
        instructions = frontmatter_match.group(2).strip()

        for line in frontmatter_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                frontmatter[key] = value

    name = frontmatter.get("name")
    if not name:
        name = skill_dir.name

    description = frontmatter.get("description")
    if not description:
        raise ValueError(f"SKILL.md missing required 'description' field: {skill_md}")

    allowed_tools_raw = frontmatter.get("allowed-tools", "")
    allowed_tools = [t.strip() for t in allowed_tools_raw.split() if t.strip()] if allowed_tools_raw else []

    metadata = {}
    for key, value in frontmatter.items():
        if key not in ("name", "description", "version", "license", "compatibility", "allowed-tools"):
            metadata[key] = value

    return Skill(
        name=name,
        description=description,
        instructions=instructions,
        path=skill_dir,
        version=frontmatter.get("version"),
        license=frontmatter.get("license"),
        compatibility=frontmatter.get("compatibility"),
        metadata=metadata,
        allowed_tools=allowed_tools,
    )


def discover_skills(skills_dir: Path) -> list[Skill]:
    if not skills_dir.exists():
        return []

    skills = []
    for item in sorted(skills_dir.iterdir()):
        if item.is_dir() and (item / "SKILL.md").exists():
            try:
                skills.append(parse_skill_md(item))
            except (ValueError, FileNotFoundError):
                pass
    return skills
