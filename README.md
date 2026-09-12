# RepoPilot

**CLI tools for developer workflows.** Clean stale branches, fast.

RepoPilot removes the repetitive git housekeeping that slows you down. No dependencies beyond Python 3.8+ and git.

---

## Installation

```bash
# From source (recommended for now)
pip install .

# Or editable install for development
pip install -e .
```

After installation, the `repopilot` command is available globally.

---

## Quick Start

```bash
# See what merged branches would be deleted (safe — changes nothing)
repopilot clean --dry-run

# Delete merged branches (asks for confirmation)
repopilot clean

# Skip confirmation
repopilot clean --force

# Protect specific branches from deletion
repopilot clean --protect main staging release
```

---

## Commands

### `repopilot clean`

Find and delete local git branches that have already been merged into the current branch.

```
usage: repopilot clean [-h] [--protect [PROTECT ...]] [--dry-run] [--force]

options:
  --protect [PROTECT ...]  Protected branches (default: main master dev)
  --dry-run                Show what would be deleted without deleting
  --force, -f              Skip the confirmation prompt
```

**Behaviour:**
- The currently checked-out branch is **never** deleted.
- Protected branches (`main`, `master`, `dev` by default) are **never** deleted.
- `--protect` accepts space-separated or comma-separated branch names.
- Without `--force`, you get a confirmation prompt listing every branch before deletion.

**Exit codes:**

| Code | Meaning |
|------|---------|
| 0 | Success, dry-run, or user aborted cleanly |
| 1 | User error (not a git repo, tried to delete current branch) |
| 2 | Internal error (git command failed, unexpected crash) |

---

## Why RepoPilot?

Every developer accumulates stale branches. `git branch --merged` tells you which ones are safe to remove, but you still have to eyeball the list, avoid deleting `main`, and run `git branch -d` on each one. RepoPilot wraps that entire workflow into one safe command with sane defaults.

---

## Requirements

- **Python** 3.8+
- **Git** (any recent version)
- No third-party dependencies — stdlib only.

---

## License

MIT
