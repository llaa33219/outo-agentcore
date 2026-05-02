from __future__ import annotations

import json
import urllib.request
from typing import Any


def get_max_output_tokens(model: str, configured_tokens: int | None) -> int:
    if configured_tokens and configured_tokens > 0:
        return configured_tokens
    try:
        url = f"https://lcw-api.blp.sh/context-window?model={model}"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read())
            if data.get("success"):
                return data["data"]["maxOutputTokens"]
    except Exception:
        pass
    return 4000
