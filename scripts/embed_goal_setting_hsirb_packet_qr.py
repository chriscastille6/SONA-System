#!/usr/bin/env python3
"""
Embed goal-setting anonymous sign-up QR on the recruitment flyer (HSIRB packet page 8).

- Adds sign-up QR + no-login instructions
- Writes updated full packet + standalone recruitment PDF

Usage:
    python scripts/embed_goal_setting_hsirb_packet_qr.py
    python scripts/embed_goal_setting_hsirb_packet_qr.py /path/to/HSIRB_Application.pdf
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import fitz

FLYER_PAGE_INDEX = 7
SIGNUP_URL = "https://bayoupal.nicholls.edu/hsirb/studies/signup/decision-making/"
DEFAULT_PACKET = Path.home() / "Downloads" / "HSIRB_Application_A_Study_in_Decision_Making_65b73c-4.pdf"


def _qr_path(repo_root: Path) -> Path:
    path = repo_root / "apps/studies/assets/irb/goal-setting/materials/goal_setting_signup_qr.png"
    if not path.exists():
        raise FileNotFoundError(f"QR PNG missing; run: python manage.py generate_goal_setting_signup_qr ({path})")
    return path


def patch_flyer_page(page: fitz.Page, qr_png: Path) -> None:
    """Place sign-up QR + anonymous booking copy on the recruitment flyer page."""
    # Cover lower-right whitespace for QR block
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


def patch_packet(packet_path: Path, qr_png: Path, output_path: Path) -> None:
    doc = fitz.open(packet_path)
    if doc.page_count <= FLYER_PAGE_INDEX:
        raise ValueError(f"Packet has only {doc.page_count} pages")
    patch_flyer_page(doc[FLYER_PAGE_INDEX], qr_png)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_path)
    doc.close()


def export_flyer_page(packet_path: Path, qr_png: Path, flyer_output: Path) -> None:
    """Save patched flyer as a standalone single-page PDF."""
    doc = fitz.open(packet_path)
    page = doc[FLYER_PAGE_INDEX]
    patch_flyer_page(page, qr_png)
    flyer = fitz.open()
    flyer.insert_pdf(doc, from_page=FLYER_PAGE_INDEX, to_page=FLYER_PAGE_INDEX)
    flyer_output.parent.mkdir(parents=True, exist_ok=True)
    flyer.save(flyer_output)
    flyer.close()
    doc.close()


def main():
    parser = argparse.ArgumentParser(description="Embed goal-setting sign-up QR in HSIRB flyer")
    parser.add_argument("packet", nargs="?", default=str(DEFAULT_PACKET))
    parser.add_argument("--output", help="Output full packet path")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    packet_path = Path(args.packet).expanduser()
    if not packet_path.exists():
        raise SystemExit(f"Packet not found: {packet_path}")

    qr_png = _qr_path(repo_root)
    materials_pdf = (
        repo_root / "apps/studies/assets/irb/goal-setting/materials/pdf"
    )
    repo_packet_out = materials_pdf / "HSIRB_Application_A_Study_in_Decision_Making_with_signup_qr.pdf"
    repo_flyer_out = materials_pdf / "Recruitment_main_study_20260312.pdf"
    output_path = Path(args.output) if args.output else repo_packet_out

    patch_packet(packet_path, qr_png, output_path)
    export_flyer_page(packet_path, qr_png, repo_flyer_out)

    beside_input = packet_path.with_name(packet_path.stem + "_with_signup_qr.pdf")
    if output_path.resolve() != beside_input.resolve():
        shutil.copy2(output_path, beside_input)

    print(f"QR image: {qr_png}")
    print(f"Recruitment flyer: {repo_flyer_out}")
    print(f"Full packet: {output_path}")
    print(f"Copy beside input: {beside_input}")


if __name__ == "__main__":
    main()
