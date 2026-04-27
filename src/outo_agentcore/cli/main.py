import argparse
import sys

def main():
    parser = argparse.ArgumentParser(
        prog="outoac",
        description="outo-agentcore: CLI multi-agent tool"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # setup command
    setup_parser = subparsers.add_parser("setup", help="Configure providers and agents")
    setup_parser.add_argument("--base-url", help="Provider base URL")
    setup_parser.add_argument("--api-key", help="Provider API key")
    setup_parser.add_argument("--model", help="Default model name")
    setup_parser.add_argument("--provider-name", default="default", help="Provider name")
    setup_parser.add_argument("--agent-md", help="Path to main agent markdown file")
    setup_parser.add_argument("--sub-agents", nargs="*", help="Sub-agent names")

    # chat command (will be added later)
    chat_parser = subparsers.add_parser("chat", help="Start a chat session")
    chat_parser.add_argument("message", help="Message to send")
    chat_parser.add_argument("--session", "-s", help="Session ID to continue")
    chat_parser.add_argument("--agent", "-a", default="main", help="Agent name to use")
    chat_parser.add_argument("--debug", action="store_true", help="Enable debug output")

    # sessions command
    sessions_parser = subparsers.add_parser("sessions", help="List sessions")
    sessions_parser.add_argument("--limit", type=int, default=10, help="Max sessions to show")

    args = parser.parse_args()

    if args.command == "setup":
        from outo_agentcore.cli.cmd_setup import cmd_setup
        cmd_setup(args)
    elif args.command == "chat":
        from outo_agentcore.cli.cmd_chat import cmd_chat
        cmd_chat(args)
    elif args.command == "sessions":
        from outo_agentcore.cli.cmd_sessions import cmd_sessions
        cmd_sessions(args)

if __name__ == "__main__":
    main()