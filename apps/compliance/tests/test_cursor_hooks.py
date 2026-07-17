"""Smoke tests for Cursor beforeSubmitPrompt / beforeReadFile hooks (no Django DB)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from django.test import SimpleTestCase

ROOT = Path(__file__).resolve().parents[3]
PROMPT_HOOK = ROOT / ".cursor" / "hooks" / "block_pii_prompt.py"
READ_HOOK = ROOT / ".cursor" / "hooks" / "block_sensitive_file_read.py"


def _run_hook(script: Path, payload: dict) -> dict:
    proc = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
    )
    self_assert = proc.returncode == 0
    assert self_assert, proc.stderr
    return json.loads(proc.stdout)


class PromptHookTests(SimpleTestCase):
    def test_allows_synthetic_prompt(self):
        out = _run_hook(
            PROMPT_HOOK,
            {"prompt": "Add a unit test using synthetic participant UUIDs only."},
        )
        self.assertTrue(out.get("continue"))

    def test_blocks_email(self):
        out = _run_hook(
            PROMPT_HOOK,
            {"prompt": "Debug login for student@example.edu"},
        )
        self.assertFalse(out.get("continue"))
        self.assertIn("email", out.get("user_message", "").lower())

    def test_blocks_deepseek(self):
        out = _run_hook(
            PROMPT_HOOK,
            {"prompt": "Wire the qualitative coder to DeepSeek."},
        )
        self.assertFalse(out.get("continue"))
        self.assertIn("JML 25-109", out.get("user_message", ""))

    def test_blocks_public_ai_with_student_data(self):
        out = _run_hook(
            PROMPT_HOOK,
            {"prompt": "Upload the gradebook CSV to ChatGPT for cleaning."},
        )
        self.assertFalse(out.get("continue"))


class ReadHookTests(SimpleTestCase):
    def test_denies_identifiable_path(self):
        out = _run_hook(
            READ_HOOK,
            {"file_path": "/workspace/data/identifiable/roster.csv"},
        )
        self.assertEqual(out.get("permission"), "deny")

    def test_allows_normal_source(self):
        out = _run_hook(
            READ_HOOK,
            {"file_path": "/workspace/apps/compliance/principles.py", "content": "PRINCIPLES = {}"},
        )
        self.assertEqual(out.get("permission"), "allow")
