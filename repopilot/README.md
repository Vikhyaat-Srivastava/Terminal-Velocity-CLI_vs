# RepoPilot

> CLI tool for developer workflows — setup, env, clean, logs.

Built for the **"Terminal Velocity"** track (Track 4) at the *Can You Hack It?* hackathon.

---

## Install

```bash
cd repopilot
pip install -e .
```

This registers the `repopilot` command in your PATH.

---

## Commands

### `repopilot env switch <name>`

Reads `.env.<name>` from the repo root, plus optional `.nvmrc` / `.python-version`, and
prints shell commands to stdout. **Must be wrapped in `eval`** (see Shell Wrapper below).

```bash
eval "$(repopilot env switch staging)"
```

Options:
- `--shell {auto,bash,zsh,powershell,pwsh,fish}` — override target shell syntax (default: `auto`)

### `repopilot env list`

Lists available `.env.*` files in the repo. Marks the active one with `*`.

```bash
repopilot env list
```

### `repopilot env current`

Prints the currently active environment name (from `REPOPILOT_ACTIVE_ENV`).

```bash
repopilot env current
```

---

## Shell Wrapper (Required for `env switch`)

A child process **cannot** change its parent shell's environment. You need a thin wrapper
that `eval`s stdout.

### Bash / Zsh (`~/.bashrc` or `~/.zshrc`)

```bash
repopilot() {
    if [ "$1" = "env" ] && [ "$2" = "switch" ]; then
        local cmds
        cmds="$(command repopilot "$@")" || return $?
        eval "$cmds"
    else
        command repopilot "$@"
    fi
}
```

### PowerShell (`$PROFILE`)

```powershell
function repopilot {
    if ($args[0] -eq 'env' -and $args[1] -eq 'switch') {
        $cmds = & (Get-Command -CommandType Application repopilot) @args
        if ($LASTEXITCODE -eq 0 -and $cmds) {
            Invoke-Expression ($cmds -join "`n")
        }
    } else {
        & (Get-Command -CommandType Application repopilot) @args
    }
}
```

### Fish (`~/.config/fish/functions/repopilot.fish`)

```fish
function repopilot
    if test "$argv[1]" = "env" -a "$argv[2]" = "switch"
        set -l cmds (command repopilot $argv)
        and eval $cmds
    else
        command repopilot $argv
    end
end
```

---

## Testing

```bash
cd repopilot
pip install pytest
python -m pytest tests/ -v
```

---

## Architecture

```
repopilot/
├── main.py              ← entry point, imports commands/*.py
├── commands/
│   ├── __init__.py
│   └── env.py           ← env switch / list / current
├── tests/
│   └── test_env.py      ← 15 edge-case tests
├── setup.py             ← pip install -e .
└── README.md
```

Each teammate owns one `commands/*.py` module. `main.py` imports all four and calls
`register(subparsers)` to wire them into a single CLI.

**Exit codes:** `0` = success, `1` = user error, `2` = internal error.

---

## License

Hackathon project — no license yet.
