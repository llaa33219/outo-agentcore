import re
from pathlib import Path

def parse_agent_md(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Agent file not found: {path}")

    content = path.read_text().strip()
    if not content:
        return {"role": None, "instructions": ""}

    result = {}

    frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
    if frontmatter_match:
        frontmatter_text = frontmatter_match.group(1)
        body = frontmatter_match.group(2)

        for line in frontmatter_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                if key == 'temperature':
                    result[key] = float(value)
                elif key == 'max_output_tokens':
                    result[key] = int(value)
                else:
                    result[key] = value
    else:
        body = content

    heading_match = re.match(r'^#\s+(.+?)\n+(.*)', body, re.DOTALL)
    if heading_match:
        result["role"] = heading_match.group(1).strip()
        result["instructions"] = heading_match.group(2).strip()
    else:
        result["role"] = None
        result["instructions"] = body.strip()

    return result