#!/usr/bin/env python3
"""
CLI for FERPA screening — used by Cursor hooks and one-off audits.

Examples:
  echo "student emily@my.nicholls.edu" | python scripts/ferpa_screen_cli.py
  python scripts/ferpa_screen_cli.py --cursor-prompt < /tmp/hook.json
  echo "Emily Johnson emily.johnson@my.nicholls.edu roster" | ./scripts/ferpa_screen.sh --synthesize
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.ferpa_guard import (  # noqa: E402
    screen_text,
    strip_synthetic_opt_in,
    synthesize_if_needed,
    synthesize_text,
)

REDACTED_DIR = ROOT / ".cursor" / "ferpa-redacted"
REDACTED_FILE = REDACTED_DIR / "latest.txt"


def _read_stdin_text() -> str:
    if sys.stdin.isatty():
        return ""
    return sys.stdin.read()


def _scan_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _collect_prompt_text(hook_input: dict) -> str:
    chunks: list[str] = []
    prompt = hook_input.get("prompt") or ""
    if prompt:
        chunks.append(str(prompt))

    for attachment in hook_input.get("attachments") or []:
        file_path = attachment.get("file_path")
        if not file_path:
            continue
        chunks.append(_scan_file(Path(file_path)))

    return "\n\n".join(part for part in chunks if part.strip())


def _write_redacted_copy(text: str) -> Path:
    REDACTED_DIR.mkdir(parents=True, exist_ok=True)
    REDACTED_FILE.write_text(text, encoding="utf-8")
    return REDACTED_FILE


def _copy_to_clipboard(text: str) -> bool:
    if sys.platform != "darwin":
        return False
    try:
        subprocess.run(["pbcopy"], input=text, text=True, check=True, timeout=5)
        return True
    except (OSError, subprocess.SubprocessError):
        return False


def _blocked_user_message(
    verdict,
    *,
    synthetic: str,
    redacted_path: Path,
    copied_to_clipboard: bool,
    opted_in: bool,
) -> str:
    details = "; ".join(f"{f.kind}: {f.snippet or f.detail}" for f in verdict.findings[:5])
    clipboard_note = (
        "A synthetic/redacted version was copied to your clipboard."
        if copied_to_clipboard
        else "Copy the synthetic version from the file below."
    )

    if opted_in:
        lead = (
            "You asked to use a synthetic dataset. The original prompt was not sent externally."
        )
    else:
        lead = (
            "Possible FERPA-protected student data was detected. "
            "Your original prompt was not sent to an external AI server."
        )

    return (
        f"{lead}\n\n"
        "Use a synthetic dataset instead?\n"
        "• YES → paste the redacted version below as your next message and send again\n"
        "• NO → edit your message to remove real student identifiers, then resend\n\n"
        f"{clipboard_note}\n"
        f"Saved to: {redacted_path}\n\n"
        f"{verdict.summary}\n"
        f"{details}\n\n"
        "--- synthetic preview ---\n"
        f"{synthetic[:1200]}"
        f"{'…' if len(synthetic) > 1200 else ''}"
    )


def cursor_prompt_response(hook_input: dict) -> tuple[dict, int]:
    combined = _collect_prompt_text(hook_input)
    prompt_only = str(hook_input.get("prompt") or "")
    _, opted_in = strip_synthetic_opt_in(prompt_only)

    verdict = screen_text(combined, destination="external")
    if not verdict.blocked:
        return {"continue": True}, 0

    synthetic, synthetic_verdict = synthesize_if_needed(combined)
    redacted_path = _write_redacted_copy(synthetic)
    copied = _copy_to_clipboard(synthetic)

    if not synthetic_verdict.blocked:
        return (
            {
                "continue": False,
                "user_message": _blocked_user_message(
                    verdict,
                    synthetic=synthetic,
                    redacted_path=redacted_path,
                    copied_to_clipboard=copied,
                    opted_in=opted_in,
                ),
            },
            0,
        )

    return (
        {
            "continue": False,
            "user_message": (
                "FERPA-protected data was detected and could not be auto-redacted to a "
                "safe synthetic version. Edit the prompt manually before sending.\n\n"
                f"{verdict.summary}"
            ),
        },
        0,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="FERPA screening CLI")
    parser.add_argument(
        "--cursor-prompt",
        action="store_true",
        help="Read Cursor beforeSubmitPrompt hook JSON from stdin",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a JSON verdict on stdout",
    )
    parser.add_argument(
        "--synthesize",
        action="store_true",
        help="Print a synthetic/redacted version instead of screening JSON",
    )
    args = parser.parse_args()

    if args.cursor_prompt:
        raw = _read_stdin_text()
        hook_input = json.loads(raw) if raw.strip() else {}
        payload, code = cursor_prompt_response(hook_input)
        print(json.dumps(payload))
        return code

    text = _read_stdin_text()
    if not text.strip() and len(sys.argv) > 1 and not sys.argv[-1].startswith("-"):
        text = " ".join(sys.argv[1:])

    if args.synthesize:
        synthetic = synthesize_text(text)
        print(synthetic)
        return 0

    verdict = screen_text(text, destination="external")
    if args.json:
        print(json.dumps(verdict.to_dict(), indent=2))
    else:
        print(verdict.summary)
        for finding in verdict.findings:
            print(f"- [{finding.kind}] {finding.detail}: {finding.snippet}")

    return 2 if verdict.blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
