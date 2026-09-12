# RepoPilot

> One CLI to rule your repo workflows — setup, env, clean, and logs.

Built for the **"Can You Hack It?"** hackathon · Track 4: Terminal Velocity

---

## The Problem

Developers waste hours on repetitive terminal tasks: grepping through massive log files, switching environments, cleaning stale branches, bootstrapping projects. Aliases help but don't travel across machines or teammates. RepoPilot packages four common workflows into one installable CLI with clear help and consistent error handling.

## Install

```bash
pip install -e .
```

After install, `repopilot` is available globally:

```bash
repopilot --help
```

## Subcommands

| Command | What it does |
|---------|-------------|
| `repopilot setup` | Scaffold and bootstrap a new project |
| `repopilot env` | Switch or inspect environment configs |
| `repopilot clean` | Remove stale branches, caches, build artifacts |
| `repopilot logs` | Filter and summarize logs from files, Docker, or journalctl |

---

## `repopilot logs` — Usage

Filter logs from any source using pure regex and timestamp parsing. Optionally append an LLM-generated summary via a local Ollama instance.

### Quick Examples

```bash
# Show all lines from a log file
repopilot logs --file /var/log/app.log

# Filter errors from the last hour
repopilot logs --file app.log --level error --since 1h

# Grep a Docker container's logs for a pattern
repopilot logs --docker my-api --grep "timeout|refused"

# Read journalctl for a systemd unit, warnings only
repopilot logs --journalctl nginx --level warn

# Count how many errors in the last 30 minutes
repopilot logs --file app.log --level error --since 30m --count

# Combine filters and get an LLM summary
repopilot logs --file app.log --level error --since 30m --summarize
```

### Log Sources (mutually exclusive, pick one)

| Flag | Description |
|------|-------------|
| `--file, -f PATH` | Read from a local log file |
| `--docker, -d CONTAINER` | Read from a Docker container's logs |
| `--journalctl, -j [UNIT]` | Read from systemd journal (optionally filter by unit) |

### Filters (all optional, stack freely)

| Flag | Description |
|------|-------------|
| `--level, -l LEVEL` | Keep lines matching a log level (`error`, `warn`, `info`, `debug`) |
| `--since, -s DURATION` | Keep lines newer than a relative duration (`10m`, `1h`, `2d`) or ISO timestamp |
| `--grep, -g PATTERN` | Keep lines matching a regex pattern |
| `--count, -c` | Print count of matching lines instead of the lines themselves |

### Summarize (optional)

| Flag | Description |
|------|-------------|
| `--summarize` | Append an LLM-generated summary after the filtered output |

Requires a local [Ollama](https://ollama.com) instance running llama3 at `http://localhost:11434`. If Ollama is unreachable, filtering still works — summarization is skipped with a warning.

### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | User error — bad input, missing file, container not found |
| `2` | Internal error — unexpected crash |

All errors print to **stderr** in the format:
```
Error: <what went wrong>. Run 'repopilot logs --help' for usage.
```

---

## Architecture

```
repopilot/
├── main.py              # Entry point — imports and registers all subcommands
├── commands/
│   ├── __init__.py      # Empty — makes commands/ a package
│   ├── setup.py         # Project scaffolding
│   ├── env.py           # Environment switching
│   ├── clean.py         # Cleanup workflows
│   └── logs.py          # Log filtering + optional LLM summary
└── pyproject.toml       # pip install -e . config
```

Each teammate owns one file under `commands/`. The shared contract:
- Every module exposes `register(subparsers)` which adds its subcommand.
- Exit codes: `0` success, `1` user error, `2` internal error.
- Errors go to stderr, data goes to stdout.

## Design Note

**Problem:** Scanning logs is the most frequent yet most tedious terminal task — piping `grep | grep | tail` chains that nobody remembers and nobody shares.

**Key design choices:**
- Filtering is pure scripting (regex + timestamp math). No network calls, no API keys, instant results.
- Summarization is opt-in and layered on top. The core workflow never depends on an LLM.
- Ollama (local, free, private) over cloud APIs — no tokens, no latency, no data leaving the machine.

**Limitations:**
- Timestamp parsing covers ISO-8601, syslog, and JSON `@timestamp` — custom formats may not be recognized.
- `--summarize` quality depends on the local model and context window; logs are sampled to the last 100 lines.
- `--journalctl` only works on systemd-based Linux distributions.

## Team

Built in 24 hours at **Can You Hack It?** by The Programming Club.

## License

MIT
