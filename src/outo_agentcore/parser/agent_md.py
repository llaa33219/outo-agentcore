import re
from pathlib import Path

def parse_agent_md(path: Path) -> dict:
    """Parse agent markdown file.

    Returns dict with keys: role, instructions, model, provider, temperature (if in frontmatter)
    """
    if not path.exists():
        raise FileNotFoundError(f"Agent file not found: {path}")

    content = path.read_text().strip()
    if not content:
        return {"role": None, "instructions": ""}

    result = {}

    # Check for YAML frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
    if frontmatter_match:
        frontmatter_text = frontmatter_match.group(1)
        body = frontmatter_match.group(2)

        # Parse simple YAML (key: value)
        for line in frontmatter_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                # Type conversion
                if key == 'temperature':
                    result[key] = float(value)
                else:
                    result[key] = value
    else:
        body = content

    # Extract first heading as role (handles optional blank line after heading)
    heading_match = re.match(r'^#\s+(.+?)\n+(.*)', body, re.DOTALL)
    if heading_match:
        result["role"] = heading_match.group(1).strip()
        result["instructions"] = heading_match.group(2).strip()
    else:
        result["role"] = None
        result["instructions"] = body.strip()

    return result