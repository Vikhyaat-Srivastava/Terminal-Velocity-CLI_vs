"""
repopilot env — manage project environment variables.
"""

import os
import sys


def register(subparsers):
    parser = subparsers.add_parser(
        "env",
        help="Manage project environment variables.",
        description="View or set environment variables in the project's .env file."
    )
    parser.add_argument(
        "--dir", "-d",
        default=".",
        metavar="PATH",
        help="Target directory to look for .env (defaults to current directory).",
    )
    parser.add_argument(
        "set_var",
        nargs="?",
        metavar="KEY=VALUE",
        help="Set an environment variable (e.g., API_KEY=123)",
    )
    parser.set_defaults(func=handle)


def handle(args):
    target_dir = os.path.abspath(args.dir)
    env_path = os.path.join(target_dir, ".env")
    
    if args.set_var:
        if "=" not in args.set_var:
            print("Error: Invalid format for setting variable. Use KEY=VALUE. Run 'repopilot env --help' for usage.", file=sys.stderr)
            sys.exit(1)
        key, value = args.set_var.split("=", 1)
        _set_env(env_path, key, value)
    else:
        _list_env(env_path)


def _list_env(env_path):
    if not os.path.exists(env_path):
        print(f"No .env file found at {env_path}")
        return
        
    print(f"\n  Environment Variables ({env_path})")
    print("  " + "-" * 40)
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                print(f"  {line}")
    print("  " + "-" * 40 + "\n")


def _set_env(env_path, key, value):
    lines = []
    updated = False
    
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith(f"{key}="):
                    lines.append(f"{key}={value}\n")
                    updated = True
                else:
                    lines.append(line)
                    
    if not updated:
        if lines and not lines[-1].endswith("\n"):
            lines[-1] += "\n"
        lines.append(f"{key}={value}\n")
        
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
        
    print(f"  [OK] Set {key} in {os.path.basename(env_path)}")
