"""
repopilot logs — search and filter project logs.
"""

import os
import sys


def register(subparsers):
    parser = subparsers.add_parser(
        "logs",
        help="Search and filter project logs.",
        description="Search through .log files in the project directory."
    )
    parser.add_argument(
        "--dir", "-d",
        default=".",
        metavar="PATH",
        help="Target directory to search for logs (defaults to current directory).",
    )
    parser.add_argument(
        "--tail", "-n",
        type=int,
        default=10,
        metavar="N",
        help="Show the last N lines of log files (default: 10)",
    )
    parser.add_argument(
        "--grep", "-g",
        metavar="PATTERN",
        help="Filter log lines containing this pattern",
    )
    parser.set_defaults(func=handle)


def handle(args):
    target_dir = os.path.abspath(args.dir)
    if not os.path.isdir(target_dir):
        print(f"Error: directory '{args.dir}' does not exist or is not a directory. Run 'repopilot logs --help' for usage.", file=sys.stderr)
        sys.exit(1)

    log_files = []
    for root, dirs, files in os.walk(target_dir):
        # Ignore common build dirs to save time
        if any(ignore in root for ignore in ['node_modules', '.git', '__pycache__', 'venv']):
            continue
        for file in files:
            if file.endswith('.log'):
                log_files.append(os.path.join(root, file))

    if not log_files:
        print(f"  No .log files found in {args.dir}")
        sys.exit(0)

    for log_file in log_files:
        rel_path = os.path.relpath(log_file, target_dir)
        print(f"\n  ==> {rel_path} <==")
        try:
            with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
                
            if args.grep:
                filtered = [line.strip() for line in lines if args.grep in line]
                if not filtered:
                    print(f"  (no lines matched '{args.grep}')")
                for line in filtered[-args.tail:]:
                    print(f"  {line}")
            else:
                for line in lines[-args.tail:]:
                    print(f"  {line.strip()}")
        except Exception as e:
            print(f"  [FAIL] Could not read log file: {e}")
