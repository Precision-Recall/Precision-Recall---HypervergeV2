"""
Multi-Agent Financial Analysis System — Main Entry Point.

Usage:
    python main.py                          # Interactive REPL mode
    python main.py --query "your question"  # Single query mode
"""

import sys
import os
import json
import argparse
import textwrap

# Ensure the agent_system directory is on the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.gateway import create_gateway_agent
from tools.call_limiter import reset_call_counts


# ─── ANSI Colors ────────────────────────────────────────────────────
class C:
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    CYAN    = "\033[36m"
    YELLOW  = "\033[33m"
    GREEN   = "\033[32m"
    MAGENTA = "\033[35m"
    RED     = "\033[31m"
    BLUE    = "\033[34m"
    RESET   = "\033[0m"


def _truncate(text: str, max_len: int = 200) -> str:
    """Truncate long strings for display."""
    if not isinstance(text, str):
        text = str(text)
    if len(text) > max_len:
        return text[:max_len] + "..."
    return text


def _format_args(args: dict) -> str:
    """Format tool arguments for readable printing."""
    parts = []
    for k, v in args.items():
        val_str = json.dumps(v) if isinstance(v, (list, dict)) else str(v)
        parts.append(f"{C.DIM}{k}={C.RESET}{_truncate(val_str, 80)}")
    return ", ".join(parts)


def run_query(agent, query: str) -> str:
    """Run a query through the gateway agent with streaming tool call updates."""
    reset_call_counts()

    final_response = ""
    step_count = 0

    print(f"\n{C.BLUE}{'─' * 70}{C.RESET}")
    print(f"{C.BOLD}{C.BLUE}  QUERY:{C.RESET} {query}")
    print(f"{C.BLUE}{'─' * 70}{C.RESET}\n")

    for event in agent.stream({"messages": [("user", query)]}, stream_mode="updates"):
        for node_name, node_data in event.items():
            messages = node_data.get("messages", [])

            for msg in messages:
                msg_type = msg.type if hasattr(msg, "type") else type(msg).__name__

                # ── AI message with tool calls ──
                if msg_type == "ai" and hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tc in msg.tool_calls:
                        step_count += 1
                        tool_name = tc.get("name", "unknown")
                        tool_args = tc.get("args", {})

                        print(f"  {C.YELLOW}⚡ Step {step_count}{C.RESET} "
                              f"{C.DIM}[{node_name}]{C.RESET}")
                        print(f"    {C.CYAN}🔧 TOOL CALL:{C.RESET} "
                              f"{C.BOLD}{tool_name}{C.RESET}")
                        if tool_args:
                            print(f"    {C.DIM}   args: {_format_args(tool_args)}{C.RESET}")
                        print()

                # ── Tool response ──
                elif msg_type == "tool":
                    tool_name = msg.name if hasattr(msg, "name") else "unknown"
                    content = msg.content if hasattr(msg, "content") else str(msg)

                    # Parse content for display
                    display = _truncate(content, 300)

                    print(f"    {C.GREEN}✅ RESULT:{C.RESET} {C.DIM}{tool_name}{C.RESET}")
                    print(f"    {C.DIM}   {display}{C.RESET}")
                    print()

                # ── Final AI message (no tool calls) ──
                elif msg_type == "ai" and hasattr(msg, "content") and msg.content:
                    if not (hasattr(msg, "tool_calls") and msg.tool_calls):
                        final_response = msg.content

    print(f"{C.BLUE}{'─' * 70}{C.RESET}")
    print(f"  {C.DIM}Total tool steps: {step_count}{C.RESET}")
    print(f"{C.BLUE}{'─' * 70}{C.RESET}\n")

    return final_response


def interactive_mode(agent):
    """Run the agent in interactive REPL mode."""
    print(f"\n{C.BOLD}{'=' * 70}{C.RESET}")
    print(f"{C.BOLD}  Financial Analysis Multi-Agent System{C.RESET}")
    print(f"  {C.CYAN}Gateway{C.RESET} → {C.YELLOW}Temporal Reasoner{C.RESET} | "
          f"{C.MAGENTA}Cross-Entity Agent{C.RESET}")
    print(f"{C.BOLD}{'=' * 70}{C.RESET}")
    print()
    print(f"  {C.DIM}Available companies: 3M, ACTIVISIONBLIZZARD{C.RESET}")
    print(f"  {C.DIM}Available years: 2015-2023 (varies by company){C.RESET}")
    print(f"  {C.DIM}Type 'quit' or 'exit' to stop.{C.RESET}")
    print()

    while True:
        try:
            query = input(f"{C.BOLD}📊 Ask > {C.RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not query:
            continue
        if query.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        try:
            response = run_query(agent, query)
            print(f"{C.GREEN}{C.BOLD}💡 ANSWER:{C.RESET}")
            # Wrap long responses nicely
            for line in response.split("\n"):
                print(f"  {line}")
            print()
        except Exception as e:
            print(f"{C.RED}❌ Error: {e}{C.RESET}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Multi-Agent Financial Analysis System"
    )
    parser.add_argument(
        "--query", "-q",
        type=str,
        default=None,
        help="Single query to run (omit for interactive mode)",
    )
    args = parser.parse_args()

    print(f"\n{C.BOLD}🚀 Initializing agents...{C.RESET}")
    agent = create_gateway_agent()
    print(f"{C.GREEN}✅ Agents ready.{C.RESET}\n")

    if args.query:
        response = run_query(agent, args.query)
        print(f"\n{C.GREEN}{C.BOLD}💡 ANSWER:{C.RESET}")
        print(response)
    else:
        interactive_mode(agent)


if __name__ == "__main__":
    main()
