from pathlib import Path
from outo_agentcore.sessions.manager import SessionManager

def cmd_sessions(args):
    sessions_dir = Path.home() / ".outoac" / "sessions"
    session_mgr = SessionManager(sessions_dir)
    sessions = session_mgr.list_sessions()[:args.limit]

    if not sessions:
        print("No sessions found.")
        return

    print(f"{'Session ID':<36} {'Agent':<15} {'Created':<25} {'Messages'}")
    print("-" * 90)
    for s in sessions:
        print(f"{s.session_id:<36} {s.agent_name:<15} {s.created_at:<25} {len(s.messages)}")