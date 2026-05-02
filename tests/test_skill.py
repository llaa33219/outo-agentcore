import pytest
from pathlib import Path
from outo_agentcore.core.skill import Skill
from outo_agentcore.parser.skill_md import parse_skill_md, discover_skills


def test_skill_defaults():
    skill = Skill(
        name="test",
        description="A test skill",
        instructions="Do something",
        path=Path("/tmp/test")
    )
    assert skill.name == "test"
    assert skill.description == "A test skill"
    assert skill.instructions == "Do something"
    assert skill.version is None
    assert skill.license is None
    assert skill.compatibility is None
    assert skill.metadata == {}
    assert skill.allowed_tools == []


def test_skill_with_optional_fields():
    skill = Skill(
        name="code-review",
        description="Code review guidelines",
        instructions="Check security...",
        path=Path("/tmp/code-review"),
        version="1.0",
        license="MIT",
        compatibility="Claude Code",
        metadata={"author": "team"},
        allowed_tools=["Read", "Bash"]
    )
    assert skill.version == "1.0"
    assert skill.license == "MIT"
    assert skill.compatibility == "Claude Code"
    assert skill.metadata == {"author": "team"}
    assert skill.allowed_tools == ["Read", "Bash"]


def test_parse_skill_md_basic(tmp_path):
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: my-skill
description: A basic skill for testing
---

# Instructions

Do this when you need to test.
""")

    skill = parse_skill_md(skill_dir)
    assert skill.name == "my-skill"
    assert skill.description == "A basic skill for testing"
    assert "Do this when you need to test." in skill.instructions
    assert skill.path == skill_dir


def test_parse_skill_md_all_fields(tmp_path):
    skill_dir = tmp_path / "full-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: full-skill
description: A skill with all fields
version: 2.0.1
license: Apache-2.0
compatibility: Any platform
allowed-tools: Bash(git:*) Read Write
custom-field: custom-value
---

# Full Skill Instructions

Complete instructions here.
""")

    skill = parse_skill_md(skill_dir)
    assert skill.name == "full-skill"
    assert skill.description == "A skill with all fields"
    assert skill.version == "2.0.1"
    assert skill.license == "Apache-2.0"
    assert skill.compatibility == "Any platform"
    assert skill.allowed_tools == ["Bash(git:*)", "Read", "Write"]
    assert skill.metadata == {"custom-field": "custom-value"}


def test_parse_skill_md_name_from_dir(tmp_path):
    skill_dir = tmp_path / "auto-named"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
description: Name comes from directory
---

Instructions here.
""")

    skill = parse_skill_md(skill_dir)
    assert skill.name == "auto-named"


def test_parse_skill_md_missing_description(tmp_path):
    skill_dir = tmp_path / "no-desc"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: no-desc
---

Instructions here.
""")

    with pytest.raises(ValueError, match="missing required 'description'"):
        parse_skill_md(skill_dir)


def test_parse_skill_md_no_frontmatter(tmp_path):
    skill_dir = tmp_path / "no-fm"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""# Instructions

Just instructions, no frontmatter.
""")

    with pytest.raises(ValueError, match="missing required 'description'"):
        parse_skill_md(skill_dir)


def test_parse_skill_md_missing_file(tmp_path):
    skill_dir = tmp_path / "empty-dir"
    skill_dir.mkdir()

    with pytest.raises(FileNotFoundError):
        parse_skill_md(skill_dir)


def test_parse_skill_md_empty_file(tmp_path):
    skill_dir = tmp_path / "empty-file"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("")

    with pytest.raises(ValueError, match="empty"):
        parse_skill_md(skill_dir)


def test_discover_skills(tmp_path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()

    skill1 = skills_dir / "skill-1"
    skill1.mkdir()
    (skill1 / "SKILL.md").write_text("""---
name: skill-1
description: First skill
---
Instructions 1.
""")

    skill2 = skills_dir / "skill-2"
    skill2.mkdir()
    (skill2 / "SKILL.md").write_text("""---
name: skill-2
description: Second skill
---
Instructions 2.
""")

    skills = discover_skills(skills_dir)
    assert len(skills) == 2
    assert skills[0].name == "skill-1"
    assert skills[1].name == "skill-2"


def test_discover_skills_with_invalid(tmp_path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()

    valid = skills_dir / "valid"
    valid.mkdir()
    (valid / "SKILL.md").write_text("""---
name: valid
description: Valid skill
---
Instructions.
""")

    invalid = skills_dir / "invalid"
    invalid.mkdir()
    (invalid / "SKILL.md").write_text("No description here.")

    skills = discover_skills(skills_dir)
    assert len(skills) == 1
    assert skills[0].name == "valid"


def test_discover_skills_nonexistent_dir():
    skills = discover_skills(Path("/nonexistent/skills"))
    assert skills == []


def test_discover_skills_empty_dir(tmp_path):
    skills_dir = tmp_path / "empty"
    skills_dir.mkdir()

    skills = discover_skills(skills_dir)
    assert skills == []


def test_discover_skills_skips_files(tmp_path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()

    (skills_dir / "not-a-skill.md").write_text("Just a file")

    skill = skills_dir / "real-skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text("""---
name: real-skill
description: A real skill
---
Instructions.
""")

    skills = discover_skills(skills_dir)
    assert len(skills) == 1
    assert skills[0].name == "real-skill"
