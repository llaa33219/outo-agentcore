import pytest
from pathlib import Path
from outo_agentcore.parser.agent_md import parse_agent_md

def test_simple_markdown(tmp_path):
    md_file = tmp_path / "agent.md"
    md_file.write_text("# Research Agent\n\nYou are a research specialist.")

    result = parse_agent_md(md_file)
    assert result["role"] == "Research Agent"
    assert "research specialist" in result["instructions"]

def test_with_frontmatter(tmp_path):
    md_file = tmp_path / "agent.md"
    md_file.write_text("---\nmodel: gpt-4o\ntemperature: 0.7\nprovider: default\n---\n# Writer\n\nWrite well.")

    result = parse_agent_md(md_file)
    assert result["model"] == "gpt-4o"
    assert result["temperature"] == 0.7
    assert result["provider"] == "default"
    assert result["role"] == "Writer"

def test_no_frontmatter(tmp_path):
    md_file = tmp_path / "agent.md"
    md_file.write_text("# Helper\n\nHelp users.")

    result = parse_agent_md(md_file)
    assert result["role"] == "Helper"
    assert "model" not in result

def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        parse_agent_md(Path("/nonexistent/agent.md"))

def test_empty_file(tmp_path):
    md_file = tmp_path / "empty.md"
    md_file.write_text("")

    result = parse_agent_md(md_file)
    assert result["role"] is None
    assert result["instructions"] == ""

def test_no_heading(tmp_path):
    md_file = tmp_path / "noheading.md"
    md_file.write_text("Just some instructions\nwithout a heading.")

    result = parse_agent_md(md_file)
    assert result["role"] is None
    assert "Just some instructions" in result["instructions"]

def test_multiline_instructions(tmp_path):
    md_file = tmp_path / "multi.md"
    md_file.write_text("# Agent\n\nLine 1\nLine 2\nLine 3")

    result = parse_agent_md(md_file)
    assert "Line 1" in result["instructions"]
    assert "Line 2" in result["instructions"]
    assert "Line 3" in result["instructions"]