import sys
import os
# Auto-add root repository folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from repopilot.commands.setup import _scan, _resolve
from repopilot.commands import env


class TestCommonUserScenarios(unittest.TestCase):

    def setUp(self):
        """Create temporary test directory."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary test directory."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # Scenario 1: Standard Language Manifest (Python, Node.js, Go, Rust)
    # -------------------------------------------------------------------------
    def test_standard_manifest_python_node(self):
        """Test detection of standard requirements.txt and package.json files."""
        # Create requirements.txt and package.json
        with open(os.path.join(self.test_dir, "requirements.txt"), "w") as f:
            f.write("requests\npytest\n")
        with open(os.path.join(self.test_dir, "package.json"), "w") as f:
            f.write('{"name": "my-app"}\n')

        detected = _scan(self.test_dir)
        plan = _resolve(detected, self.test_dir)

        # Verify both projects are detected with exact expected install commands
        commands = [item[1] for item in plan]
        self.assertIn("pip install -r requirements.txt", commands)
        self.assertIn("npm install", commands)

    # -------------------------------------------------------------------------
    # Scenario 2: Custom Build Scripts (.ps1, .bat, .sh)
    # -------------------------------------------------------------------------
    def test_custom_build_scripts(self):
        """Test auto-detection of custom shell and batch scripts."""
        ps1_file = os.path.join(self.test_dir, "setup.ps1")
        with open(ps1_file, "w") as f:
            f.write('Write-Host "Installing..."\n')

        detected = _scan(self.test_dir)
        plan = _resolve(detected, self.test_dir)

        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0][0], "PowerShell Script")
        self.assertEqual(plan[0][1], f"powershell {os.path.join('.', 'setup.ps1')}")

    # -------------------------------------------------------------------------
    # Scenario 3: Documentation Text Files (Ollama LLM Resolution)
    # -------------------------------------------------------------------------
    @patch("urllib.request.urlopen")
    def test_documentation_text_file(self, mock_urlopen):
        """Test LLM extraction of setup commands from an English README.txt file."""
        readme_file = os.path.join(self.test_dir, "README.txt")
        with open(readme_file, "w") as f:
            f.write("Welcome! To install dependencies, run cargo build in your terminal.\n")

        # Mock Ollama API response
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"choices": [{"message": {"content": "cargo build"}}]}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        detected = _scan(self.test_dir)
        plan = _resolve(detected, self.test_dir)

        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0][0], "README.txt (LLM-resolved)")
        self.assertEqual(plan[0][1], "cargo build")

    # -------------------------------------------------------------------------
    # Scenario 4: Environment Switching (.env.staging)
    # -------------------------------------------------------------------------
    def test_environment_file_parsing(self):
        """Test parsing of .env.staging environment key-values."""
        env_file = os.path.join(self.test_dir, ".env.staging")
        with open(env_file, "w") as f:
            f.write("DB_HOST=staging.db.internal\nPORT=8080\n")

        from pathlib import Path
        parsed = env.parse_env_file(Path(env_file))
        self.assertEqual(parsed.get("DB_HOST"), "staging.db.internal")
        self.assertEqual(parsed.get("PORT"), "8080")


if __name__ == "__main__":
    unittest.main()
