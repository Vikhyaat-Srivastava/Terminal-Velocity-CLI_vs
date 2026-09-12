"""
repopilot clean — clean stale branches and build artifacts.
"""

import os
import shutil
import sys


def register(subparsers):
    parser = subparsers.add_parser(
        "clean",
        help="Clean build artifacts and temporary files.",
        description="Removes standard build and temporary directories like node_modules, __pycache__, dist, build, etc."
    )
    parser.add_argument(
        "--dir", "-d",
        default=".",
        metavar="PATH",
        help="Target directory to clean (defaults to current directory).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be deleted without actually deleting.",
    )
    parser.set_defaults(func=handle)


def handle(args):
    target_dir = os.path.abspath(args.dir)
    if not os.path.isdir(target_dir):
        print(f"Error: directory '{args.dir}' does not exist or is not a directory. Run 'repopilot clean --help' for usage.", file=sys.stderr)
        sys.exit(1)

    artifacts = ["node_modules", "__pycache__", "dist", "build", "target", ".pytest_cache", ".ruff_cache", "venv"]
    found = []

    for root, dirs, files in os.walk(target_dir):
        for name in artifacts:
            if name in dirs:
                found.append(os.path.join(root, name))
                dirs.remove(name)  # Don't recurse into directories we are going to delete

    if not found:
        print("  [OK] Workspace is clean. No artifacts found.")
        sys.exit(0)

    print("\n  RepoPilot Clean -- Found Artifacts")
    print("  " + "-" * 40)
    for path in found:
        rel_path = os.path.relpath(path, target_dir)
        print(f"  - {rel_path}")
    print("  " + "-" * 40 + "\n")

    if args.dry_run:
        sys.exit(0)

    try:
        answer = input("  Delete these artifacts? [y/N] ").strip().lower()
    except EOFError:
        answer = "n"
        
    if answer in ("y", "yes"):
        for path in found:
            try:
                shutil.rmtree(path)
                print(f"  [OK] Deleted {os.path.relpath(path, target_dir)}")
            except OSError as e:
                print(f"  [FAIL] Could not delete {os.path.relpath(path, target_dir)}: {e}")
                sys.exit(1)
        print("\n  Clean complete.")
    else:
        print("  Aborted.")
