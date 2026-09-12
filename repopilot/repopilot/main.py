#!/usr/bin/env python3
"""
RepoPilot — CLI tool for developer workflows.

Entry point that wires up all subcommands.
Each teammate owns one file under repopilot/commands/.
"""

import argparse
import sys

from repopilot.commands import setup, env, clean, logs


def main():
    parser = argparse.ArgumentParser(
        prog="repopilot",
        description="RepoPilot — automate repetitive developer terminal tasks.",
    )
    parser.add_argument(
        "--version", action="version", version="%(prog)s 0.1.0"
    )

    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        description="Available subcommands. Run 'repopilot <command> --help' for details.",
    )

    # Each module exposes register(subparsers) and handle(args)
    setup.register(subparsers)
    env.register(subparsers)
    clean.register(subparsers)
    logs.register(subparsers)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    # Dispatch to the handler set by each module's register()
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\nAborted.", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        # Exit code 2 = internal / unexpected error
        print(f"Error: unexpected internal error: {exc}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
