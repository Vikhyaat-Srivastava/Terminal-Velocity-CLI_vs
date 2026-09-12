# RepoPilot 🚀

**One command to set up any repo.** RepoPilot scans your project, detects dependency files, and runs the right install commands — so you don't have to remember whether it's `npm install`, `pip install -r requirements.txt`, or `go mod tidy`.

Built for the **"Can You Hack It?"** hackathon — Track 4: Terminal Velocity.

---

## Install

```bash
# Clone and install (one command)
git clone https://github.com/<your-org>/repopilot.git && cd repopilot && pip install -e .
```

Or from a local checkout:

```bash
pip install -e .
```

That's it. The `repopilot` command is now available globally.

---

## Usage

### `repopilot setup`

Scan the current repo, detect dependencies, and run install commands.

```bash
# Interactive (asks for confirmation before running)
repopilot setup

# Skip confirmation
repopilot setup --yes

# See what would run, without executing anything
repopilot setup --dry-run

# Scan a different directory
repopilot setup --dir /path/to/repo
```

**What it detects:**

| File              | Project Type       | Command                              |
|-------------------|--------------------|--------------------------------------|
| requirements.txt  | Python (pip)       | `pip install -r requirements.txt`    |
| pyproject.toml    | Python (pyproject) | `pip install -e .`                   |
| setup.py          | Python (setup.py)  | `pip install -e .`                   |
| package.json      | Node.js            | `npm install`                        |
| go.mod            | Go                 | `go mod tidy`                        |
| pom.xml           | Java (Maven)       | `mvn install`                        |
| build.gradle      | Java (Gradle)      | `gradle build`                       |
| Gemfile           | Ruby               | `bundle install`                     |
| Cargo.toml        | Rust               | `cargo build`                        |
| composer.json     | PHP (Composer)     | `composer install`                   |
| Dockerfile        | Docker             | `docker build -t <dirname> .`        |

**LLM fallback (optional):** If a `Makefile`, `CMakeLists.txt`, or other ambiguous file is found, RepoPilot can ask a local Ollama LLM for the right command. This requires [Ollama](https://ollama.ai) running at `localhost:11434` with the `llama3` model. If Ollama isn't running, the tool works fine without it — ambiguous files are simply skipped.

### Other subcommands (coming soon)

```bash
repopilot env     # Manage project environment variables
repopilot clean   # Clean stale branches and build artifacts
repopilot logs    # Search and filter project logs
```

---

## Architecture

```
repopilot/
├── pyproject.toml          # Package config, console_scripts entry
├── README.md
└── repopilot/
    ├── __init__.py
    ├── main.py             # Entry point — wires subparsers
    └── commands/
        ├── __init__.py
        ├── setup.py        # ← Scan + detect + install
        ├── env.py          # (stub)
        ├── clean.py        # (stub)
        └── logs.py         # (stub)
```

Each teammate owns one `commands/*.py` file. `main.py` calls `register(subparsers)` from each, so work merges cleanly.

---

## Exit Codes

| Code | Meaning                          |
|------|----------------------------------|
| 0    | Success                          |
| 1    | User error (bad input, not found)|
| 2    | Internal error (unexpected crash)|

---

## License

MIT
