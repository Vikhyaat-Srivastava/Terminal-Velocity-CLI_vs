# Design Note — RepoPilot

## The Problem

Developers accumulate stale local branches. After a feature merges, the branch lingers. After a few weeks, `git branch` prints 30 lines and you can't tell which ones matter. You run `git branch --merged`, eyeball the list, carefully avoid deleting `main`, and type `git branch -d feature-x` six times. It's a two-minute chore that happens often enough to be annoying but not often enough that anyone writes a proper script for it.

## Key Design Choices

**1. Git plumbing only, no dependencies.**
RepoPilot shells out to `git branch --merged`, `git branch --show-current`, and `git branch -d`. No parsing `.git/` internals, no libgit2, no third-party libraries. If git works, repopilot works. This also means it respects any git configuration the user already has (aliases, hooks, worktrees).

**2. Safe defaults.**
`main`, `master`, and `dev` are protected out of the box. The current branch is unconditionally excluded — even if it somehow ends up in the merged list. Without `--force`, the user sees the full list and must confirm. These aren't configurable-away; the worst case is "nothing was deleted."

**3. `--dry-run` is first-class.**
The most common use is "show me what's stale." Dry-run prints one branch per line with no decoration, so it pipes cleanly into `wc -l`, `xargs`, or other tools.

**4. Confirmation prompt by default.**
Deleting branches is low-risk (they're merged, so no work is lost), but surprising deletions erode trust. The prompt lists every branch and requires `y` or `yes`. `--force` skips it for scripting.

## Limitations

- **Local branches only.** RepoPilot does not touch remote-tracking branches. Run `git fetch --prune` separately.
- **No regex for `--protect`.** Protection is by exact branch name. Glob or regex patterns are not supported.
- **Merged into current branch.** `git branch --merged` is relative to HEAD. Branches merged into `main` but not into your current feature branch won't appear.

## Architecture

```
repopilot/
├── __init__.py          # version
├── __main__.py          # python -m repopilot
├── cli.py               # argparse, subcommand dispatch
├── errors.py            # shared error formatting
├── git_utils.py         # git plumbing helpers
└── commands/
    ├── __init__.py
    └── clean.py          # the clean subcommand
```

Adding a new subcommand: create `commands/foo.py` with `register(subparsers)` and `handle(args)`, import and register it in `cli.py`.
