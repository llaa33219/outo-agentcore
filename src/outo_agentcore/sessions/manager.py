import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class SessionData:
    session_id: str
    created_at: str
    messages: list[dict] = field(default_factory=list)
    agent_name: str = "main"


class SessionLoadError(Exception):
    pass


class SessionManager:
    def __init__(self, sessions_dir: Path):
        self._dir = sessions_dir
        self._dir.mkdir(parents=True, exist_ok=True)

    def create(self, agent_name: str = "main", session_id: str | None = None) -> SessionData:
        return SessionData(
            session_id=session_id or uuid.uuid4().hex,
            created_at=datetime.now(timezone.utc).isoformat(),
            messages=[],
            agent_name=agent_name,
        )

    def load(self, session_id: str) -> SessionData | None:
        path = self._dir / f"{session_id}.json"
        if not path.exists():
            return None

        try:
            with open(path) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise SessionLoadError(f"Session file is corrupted: {path}") from e

        try:
            return SessionData(**data)
        except (KeyError, TypeError) as e:
            raise SessionLoadError(f"Session file has invalid format: {path}") from e

    def save(self, session: SessionData) -> None:
        path = self._dir / f"{session.session_id}.json"
        with open(path, "w") as f:
            json.dump(asdict(session), f, indent=2)

    def list_sessions(self) -> list[SessionData]:
        sessions = []
        for path in self._dir.glob("*.json"):
            try:
                with open(path) as f:
                    data = json.load(f)
                sessions.append(SessionData(**data))
            except (json.JSONDecodeError, KeyError):
                continue

        sessions.sort(key=lambda s: s.created_at, reverse=True)
        return sessions
