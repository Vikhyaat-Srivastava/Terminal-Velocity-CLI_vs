"""
Unit tests for commands/env.py — covers 15 edge cases.

Run with:
    python -m pytest tests/test_env.py -v
"""

import os
import sys
import tempfile
import textwrap
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest

# Ensure the repopilot package root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from commands.env import (
    parse_env_file,
    detect_shell,
    format_export_command,
    handle_switch,
    handle_list,
    handle_current,
    user_error,
    find_repo_root,
)


# ======================================================================
# Fixtures
# ======================================================================

@pytest.fixture
def tmp_repo(tmp_path):
    """Create a temporary repo root with a .git directory."""
    (tmp_path / ".git").mkdir()
    return tmp_path


def write_env(tmp_repo, name, content):
    """Write a .env.<name> file into the tmp repo."""
    path = tmp_repo / f".env.{name}"
    path.write_text(textwrap.dedent(content), encoding="utf-8")
    return path


# ======================================================================
# parse_env_file tests
# ======================================================================

class TestParseBasic:
    """Test 1: Simple KEY=value parsing."""

    def test_parse_basic(self, tmp_repo):
        f = write_env(tmp_repo, "dev", "APP_NAME=repopilot\nPORT=3000\n")
        result = parse_env_file(f)
        assert result == {"APP_NAME": "repopilot", "PORT": "3000"}


class TestParseQuotedSpaces:
    """Test 2: Double-quoted values with spaces."""

    def test_parse_quoted_spaces(self, tmp_repo):
        f = write_env(tmp_repo, "dev", 'GREETING="Hello World"\n')
        result = parse_env_file(f)
        assert result["GREETING"] == "Hello World"


class TestParseSingleQuotes:
    """Test 3: Single-quoted values preserve literals."""

    def test_parse_single_quotes(self, tmp_repo):
        f = write_env(tmp_repo, "dev", "SECRET='$VAR is literal'\n")
        result = parse_env_file(f)
        assert result["SECRET"] == "$VAR is literal"


class TestParseEmptyValue:
    """Test 4: KEY= produces an empty string."""

    def test_parse_empty_value(self, tmp_repo):
        f = write_env(tmp_repo, "dev", "EMPTY_KEY=\n")
        result = parse_env_file(f)
        assert result["EMPTY_KEY"] == ""


class TestParseInlineComment:
    """Test 5: Inline comment after whitespace is stripped."""

    def test_parse_inline_comment(self, tmp_repo):
        f = write_env(tmp_repo, "dev", "HOST=localhost # dev server\n")
        result = parse_env_file(f)
        assert result["HOST"] == "localhost"


class TestParseHashInQuotes:
    """Test 6: '#' inside quotes is preserved."""

    def test_parse_hash_in_quotes(self, tmp_repo):
        f = write_env(tmp_repo, "dev", 'URL="https://example.com#anchor"\n')
        result = parse_env_file(f)
        assert result["URL"] == "https://example.com#anchor"


class TestParseMultiline:
    """Test 7: Multiline double-quoted values."""

    def test_parse_multiline(self, tmp_repo):
        content = 'CERT="line1\nline2"\n'
        f = write_env(tmp_repo, "dev", content)
        result = parse_env_file(f)
        assert result["CERT"] == "line1\nline2"


class TestParseExportPrefix:
    """Test 8: 'export KEY=val' is handled."""

    def test_parse_export_prefix(self, tmp_repo):
        f = write_env(tmp_repo, "dev", "export DB_HOST=db.local\n")
        result = parse_env_file(f)
        assert result["DB_HOST"] == "db.local"


class TestParseEmptyFile:
    """Test 9: Empty file returns empty dict, no crash."""

    def test_parse_empty_file(self, tmp_repo):
        f = write_env(tmp_repo, "dev", "")
        result = parse_env_file(f)
        assert result == {}

    def test_parse_comments_only(self, tmp_repo):
        f = write_env(tmp_repo, "dev", "# just a comment\n# another\n")
        result = parse_env_file(f)
        assert result == {}


# ======================================================================
# handle_switch tests
# ======================================================================

class TestSwitchMissingEnv:
    """Test 10: Switching to a nonexistent env → exit code 1."""

    def test_switch_missing_env(self, tmp_repo):
        with mock.patch("commands.env.find_repo_root", return_value=tmp_repo):
            args = SimpleNamespace(name="nonexistent", shell="bash")
            captured_stderr = StringIO()
            with mock.patch("sys.stderr", captured_stderr):
                code = handle_switch(args)
            assert code == 1
            assert "not found" in captured_stderr.getvalue()


class TestSwitchTraversal:
    """Test 11: Path traversal attack → exit code 1."""

    def test_switch_traversal(self, tmp_repo):
        args = SimpleNamespace(name="../../etc/passwd", shell="bash")
        captured_stderr = StringIO()
        with mock.patch("sys.stderr", captured_stderr):
            code = handle_switch(args)
        assert code == 1
        assert "Invalid environment name" in captured_stderr.getvalue()


class TestSwitchBashOutput:
    """Test 12: Bash switch emits 'export KEY=...' to stdout only."""

    def test_switch_bash_output(self, tmp_repo):
        write_env(tmp_repo, "staging", "API_KEY=secret123\n")
        with mock.patch("commands.env.find_repo_root", return_value=tmp_repo):
            args = SimpleNamespace(name="staging", shell="bash")
            captured_stdout = StringIO()
            captured_stderr = StringIO()
            with mock.patch("sys.stdout", captured_stdout), \
                 mock.patch("sys.stderr", captured_stderr):
                code = handle_switch(args)
            assert code == 0
            stdout_lines = captured_stdout.getvalue().strip().splitlines()
            # Should have export commands for API_KEY and REPOPILOT_ACTIVE_ENV
            assert any("export API_KEY=" in line for line in stdout_lines)
            assert any("REPOPILOT_ACTIVE_ENV" in line for line in stdout_lines)
            # Stderr should have the human message
            assert "Switched to environment" in captured_stderr.getvalue()
            # Stdout must NOT have the human message
            assert "Switched to" not in captured_stdout.getvalue()


class TestSwitchPowershell:
    """Test 13: PowerShell switch emits '$env:KEY = ...' syntax."""

    def test_switch_powershell(self, tmp_repo):
        write_env(tmp_repo, "prod", "DB=postgres\n")
        with mock.patch("commands.env.find_repo_root", return_value=tmp_repo):
            args = SimpleNamespace(name="prod", shell="powershell")
            captured_stdout = StringIO()
            captured_stderr = StringIO()
            with mock.patch("sys.stdout", captured_stdout), \
                 mock.patch("sys.stderr", captured_stderr):
                code = handle_switch(args)
            assert code == 0
            stdout = captured_stdout.getvalue()
            assert "$env:DB = 'postgres'" in stdout
            assert "$env:REPOPILOT_ACTIVE_ENV = 'prod'" in stdout


# ======================================================================
# handle_list tests
# ======================================================================

class TestListExcludesSamples:
    """Test 14: .env.example and .env.sample are excluded from listing."""

    def test_list_excludes_samples(self, tmp_repo):
        write_env(tmp_repo, "dev", "A=1\n")
        write_env(tmp_repo, "staging", "B=2\n")
        write_env(tmp_repo, "example", "C=3\n")  # should be excluded
        write_env(tmp_repo, "sample", "D=4\n")   # should be excluded

        with mock.patch("commands.env.find_repo_root", return_value=tmp_repo):
            args = SimpleNamespace()
            captured_stdout = StringIO()
            with mock.patch("sys.stdout", captured_stdout):
                code = handle_list(args)
            assert code == 0
            output = captured_stdout.getvalue()
            assert "dev" in output
            assert "staging" in output
            assert "example" not in output
            assert "sample" not in output


# ======================================================================
# handle_current tests
# ======================================================================

class TestCurrentUnset:
    """Test 15: No REPOPILOT_ACTIVE_ENV → graceful message."""

    def test_current_unset(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            args = SimpleNamespace()
            captured_stdout = StringIO()
            with mock.patch("sys.stdout", captured_stdout):
                code = handle_current(args)
            assert code == 0
            assert "No active environment" in captured_stdout.getvalue()

    def test_current_set(self):
        with mock.patch.dict(os.environ, {"REPOPILOT_ACTIVE_ENV": "staging"}):
            args = SimpleNamespace()
            captured_stdout = StringIO()
            with mock.patch("sys.stdout", captured_stdout):
                code = handle_current(args)
            assert code == 0
            assert "staging" in captured_stdout.getvalue()


# ======================================================================
# Shell detection & formatting tests
# ======================================================================

class TestDetectShell:
    """Supplemental: shell auto-detection logic."""

    def test_explicit_override(self):
        assert detect_shell("fish") == "fish"

    def test_windows_default(self):
        with mock.patch.dict(os.environ, {}, clear=True), \
             mock.patch("commands.env.os.name", "nt"):
            assert detect_shell("auto") == "powershell"

    def test_shell_env_bash(self):
        with mock.patch.dict(os.environ, {"SHELL": "/bin/bash"}, clear=True):
            assert detect_shell("auto") == "bash"


class TestFormatExport:
    """Supplemental: format_export_command covers quoting."""

    def test_bash_with_spaces(self):
        cmd = format_export_command("GREETING", "hello world", "bash")
        assert cmd == "export GREETING='hello world'"

    def test_powershell_with_single_quote(self):
        cmd = format_export_command("MSG", "it's working", "powershell")
        assert cmd == "$env:MSG = 'it''s working'"

    def test_fish_format(self):
        cmd = format_export_command("KEY", "value", "fish")
        assert cmd == "set -gx KEY value"
