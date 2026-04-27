import asyncio
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolResult:
    content: str


class BashTool:
    name = "bash"
    description = "Execute a bash command and return its output."

    def to_schema(self) -> dict[str, Any]:
        return {
            "name": "bash",
            "description": "Execute a bash command and return its output.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The bash command to execute",
                    },
                },
                "required": ["command"],
            },
        }

    async def execute(self, command: str) -> ToolResult:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        output = stdout.decode() + stderr.decode()
        return ToolResult(content=output)