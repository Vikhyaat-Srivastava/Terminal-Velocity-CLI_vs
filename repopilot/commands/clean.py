"""repopilot clean - Find and delete local git branches already merged."""

from __future__ import annotations

import sys

from repopilot.errors import print_error
from repopilot.git_utils import (
    current_branch,
    delete_branch,
    ensure_git,
    is_inside_work_tree,
    merged_branches,
)


def _parse_protected(protect_arg) -> set[str]:
    """Parse protected branches from arguments.

    Supports list of strings, comma-separated strings, or single string.
    """
    if protect_arg is None:
        return {"main", "master", "dev"}
    if isinstance(protect_arg, str):
        protect_arg = [protect_arg]
    protected: set[str] = set()
    for item in protect_arg:
        for part in str(item).split(","):
            val = part.strip()
            if val:
                protected.add(val)
    return protected


def register(subparsers):
    """Register the 'clean' subcommand parser."""
    parser = subparsers.add_parser(
        "clean",
        help="Find and delete local git branches that are already merged.",
        description=(
            "Find and delete local git branches that are already merged "
            "(stale branch cleanup)."
        ),
    )
    parser.add_argument(
        "--protect",
        nargs="*",
        default=["main", "master", "dev"],
        help="Protected branches that should not be deleted (default: main master dev).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without deleting.",
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Skip the confirmation prompt before deleting.",
    )
    parser.set_defaults(func=handle)
    return parser


def handle(args) -> int:
    """Handle the 'repopilot clean' command."""
    try:
        # 1. Confirm git is available and we're in a repo
        ensure_git()

        if not is_inside_work_tree():
            print_error("Not a git repository", "clean")
            sys.exit(1)

        # 2. Get current branch (never delete this one)
        branch = current_branch()
        if branch is None:
            print_error("Failed to determine current branch (detached HEAD?)", "clean")
            sys.exit(2)

        # 3. Get merged branches
        raw_merged = merged_branches()

        # 4. Filter out protected branches and current branch
        protected = _parse_protected(getattr(args, "protect", None))
        candidates = [
            b for b in raw_merged
            if b not in protected and b != branch
        ]

        # 5. Handle --dry-run
        if getattr(args, "dry_run", False):
            for b in candidates:
                print(b)
            return 0

        # 6. Nothing to do
        if not candidates:
            print("No merged branches to clean.")
            return 0

        # 7. Confirmation prompt unless --force
        if not getattr(args, "force", False):
            print("Merged branches eligible for deletion:")
            for b in candidates:
                print(f"  {b}")
            try:
                response = input("Delete these branches? [y/N]: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nAborted.")
                return 0

            if response not in ("y", "yes"):
                print("Aborted.")
                return 0

        # 8. Delete each branch
        for b in candidates:
            if b == branch:
                # Defensive: should never reach here
                print_error(
                    f"Cannot delete the currently checked-out branch '{branch}'",
                    "clean",
                )
                sys.exit(1)

            ok, msg = delete_branch(b)
            if ok:
                print(msg)
            else:
                print(f"Failed to delete {b}: {msg}")

        return 0

    except SystemExit:
        raise
    except Exception as exc:
        print_error(f"Unexpected internal error: {exc}", "clean")
        sys.exit(2)
