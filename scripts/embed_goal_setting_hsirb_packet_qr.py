#!/usr/bin/env python3
"""
Embed goal-setting anonymous sign-up QR on the main-study recruitment flyer.

Preferred flyer path (current packet):
  scripts/generate_goal_setting_flyer.py already embeds the QR into
  Recruitment_main_study_20260312.pdf, which rebuild_goal_setting_hsirb_packet.py
  inserts as Appendix A2.

This script remains for regenerating the with_signup_qr packet variant from the
repo full packet (or an explicit source), by locating the main-study flyer page
and ensuring the QR/sign-up block is present.

Usage:
    python scripts/embed_goal_setting_hsirb_packet_qr.py
    python scripts/embed_goal_setting_hsirb_packet_qr.py path/to/packet.pdf
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import fitz

REPO_ROOT = Path(__file__).resolve().parent.parent
MATERIALS_PDF = REPO_ROOT / "apps/studies/assets/irb/goal-setting/materials/pdf"
DEFAULT_PACKET = MATERIALS_PDF / "HSIRB_Application_A_Study_in_Decision_Making_full_packet.pdf"
DEFAULT_OUTPUT = MATERIALS_PDF / "HSIRB_Application_A_Study_in_Decision_Making_with_signup_qr.pdf"
SIGNUP_URL = "https://bayoupal.nicholls.edu/hsirb/studies/signup/decision-making/"


def _qr_path() -> Path:
    path = REPO_ROOT / "apps/studies/assets/irb/goal-setting/materials/goal_setting_signup_qr.png"
    if not path.exists():
        raise FileNotFoundError(
            f"QR PNG missing; run: python manage.py generate_goal_setting_signup_qr ({path})"
        )
    return path


def find_main_flyer_page(doc: fitz.Document) -> int:
    """Return 0-based index of the main-study recruitment flyer content page."""
    for i in range(doc.page_count):
        text = doc[i].get_text()
        lowered = text.lower()
        if "you are invited to participate" not in lowered:
            continue
        if "pilot session" in lowered or "pilot study" in lowered:
            continue
        if "a study in decision making" not in lowered:
            continue
        # Prefer the participant flyer (not appendix title pages).
        if "what will i do" in lowered or "sign up for a session" in lowered:
            return i
    raise ValueError(
        "Could not locate main-study recruitment flyer page in packet. "
        "Regenerate flyers with scripts/generate_goal_setting_flyer.py and rebuild the packet."
    )


def patch_flyer_page(page: fitz.Page, qr_png: Path) -> None:
    """Place sign-up QR + anonymous booking copy on the recruitment flyer page."""
    text = page.get_text()
    if "Sign up for a session" in text and len(page.get_images()) >= 2:
        # Flyer already includes the ReportLab sign-up block from generate_goal_setting_flyer.py.
        return

    qr_rect = fitz.Rect(382, 518, 538, 674)
    page.draw_rect(qr_rect, color=(1, 1, 1), fill=(1, 1, 1))
    page.insert_image(fitz.Rect(398, 528, 522, 652), filename=str(qr_png))

    signup_rect = fitz.Rect(42, 528, 378, 670)
    signup_text = (
        "Sign up for a session\n\n"
        "Scan the QR code to choose an open time slot.\n"
        "No account or login required.\n"
        "You receive a booking reference and PIN only.\n\n"
        f"{SIGNUP_URL}"
    )
    page.insert_textbox(
        signup_rect,
        signup_text,
        fontsize=9.5,
        fontname="helv",
        color=(0.12, 0.16, 0.22),
        align=fitz.TEXT_ALIGN_LEFT,
    )


def patch_packet(packet_path: Path, qr_png: Path, output_path: Path) -> int:
    doc = fitz.open(packet_path)
    flyer_index = find_main_flyer_page(doc)
    patch_flyer_page(doc[flyer_index], qr_png)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_path)
    page_count = doc.page_count
    doc.close()
    return flyer_index


def export_flyer_page(packet_path: Path, qr_png: Path, flyer_output: Path, flyer_index: int) -> None:
    """Save patched flyer as a standalone single-page PDF."""
    doc = fitz.open(packet_path)
    page = doc[flyer_index]
    patch_flyer_page(page, qr_png)
    flyer = fitz.open()
    flyer.insert_pdf(doc, from_page=flyer_index, to_page=flyer_index)
    flyer_output.parent.mkdir(parents=True, exist_ok=True)
    flyer.save(flyer_output)
    flyer.close()
    doc.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Embed goal-setting sign-up QR in HSIRB flyer")
    parser.add_argument(
        "packet",
        nargs="?",
        default=str(DEFAULT_PACKET),
        help="Source HSIRB packet PDF (default: repo full packet)",
    )
    parser.add_argument("--output", help="Output with_signup_qr packet path")
    parser.add_argument(
        "--update-standalone-flyer",
        action="store_true",
        help="Also overwrite Recruitment_main_study_20260312.pdf from the patched flyer page",
    )
    args = parser.parse_args()

    packet_path = Path(args.packet).expanduser()
    if not packet_path.exists():
        raise SystemExit(f"Packet not found: {packet_path}")

    qr_png = _qr_path()
    output_path = Path(args.output) if args.output else DEFAULT_OUTPUT
    flyer_index = patch_packet(packet_path, qr_png, output_path)

    if args.update_standalone_flyer:
        repo_flyer_out = MATERIALS_PDF / "Recruitment_main_study_20260312.pdf"
        export_flyer_page(packet_path, qr_png, repo_flyer_out, flyer_index)
        print(f"Recruitment flyer: {repo_flyer_out}")

    print(f"QR image: {qr_png}")
    print(f"Flyer page (1-based): {flyer_index + 1}")
    print(f"Full packet: {output_path}")


if __name__ == "__main__":
    main()
