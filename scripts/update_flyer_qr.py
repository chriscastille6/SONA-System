#!/usr/bin/env python3
"""
Replace the QR code in an EI study flyer PDF with a QR code that links to the study.

Usage:
    python scripts/update_flyer_qr.py [input_flyer.pdf] [output_flyer.pdf]
    python scripts/update_flyer_qr.py  # uses defaults: Flyer_EI_Study.pdf -> output
    python scripts/update_flyer_qr.py Flyer_EI_Study.pdf out.pdf --qr-image my_qr.png  # custom QR

Use --url to generate a QR from a URL, or --qr-image to use your own QR image.
"""

import argparse
import shutil
import sys
from pathlib import Path

# EI study page on bayoupal platform
DEFAULT_STUDY_URL = "https://bayoupal.nicholls.edu/platform/studies/study.html?id=local-study-001"


def generate_qr_png(url: str, size_px: int = 300, path: Path | None = None) -> Path:
    """Generate a QR code image for the given URL. Returns path to PNG."""
    import qrcode
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((size_px, size_px))
    out = path or Path("/tmp/ei_study_qr.png")
    img.save(out)
    return out


def find_qr_image_xref(doc) -> int | None:
    """
    Find the xref of an image that looks like a QR code (square, small-to-medium).
    Returns the first matching image xref on the first page, or None.
    """
    page = doc[0]
    # full=True gives (xref, smask, width, height, bpc, colorspace, ...)
    images = page.get_images(full=True)
    for item in images:
        xref = item[0]
        width = item[2]
        height = item[3]
        # QR codes are square; in a flyer often ~100–400 px
        if width == height and 50 <= width <= 600:
            return xref
    # Fallback: first square-ish image (aspect ratio near 1)
    for item in images:
        xref = item[0]
        w, h = item[2], item[3]
        if w and h and 0.8 <= w / h <= 1.25 and 40 <= min(w, h) <= 600:
            return xref
    return None


def replace_qr_in_pdf(
    input_pdf: Path,
    output_pdf: Path,
    *,
    study_url: str | None = None,
    qr_image_path: Path | None = None,
    qr_size_px: int = 300,
) -> None:
    """Replace the QR code image in the flyer PDF. Use qr_image_path for custom QR, else study_url to generate."""
    import fitz  # PyMuPDF

    if qr_image_path is not None:
        if not qr_image_path.exists():
            raise SystemExit(f"Error: QR image not found: {qr_image_path}")
        qr_path = qr_image_path
        cleanup_qr = False
    else:
        url = study_url or DEFAULT_STUDY_URL
        qr_path = generate_qr_png(url, size_px=qr_size_px)
        cleanup_qr = True

    doc = fitz.open(input_pdf)
    xref = find_qr_image_xref(doc)
    if xref is None:
        doc.close()
        raise SystemExit(
            "Could not find a square QR-sized image in the first page. "
            "Ensure the flyer has a QR code on page 1."
        )

    try:
        page = doc[0]
        page.replace_image(xref=xref, filename=str(qr_path))
        doc.save(output_pdf)
    finally:
        doc.close()
        if cleanup_qr and qr_path.exists() and str(qr_path).startswith("/tmp"):
            qr_path.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(
        description="Replace flyer QR code. Use --qr-image for custom QR, or --url to generate."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default=None,
        help="Input flyer PDF (default: Flyer_EI_Study.pdf in project root)",
    )
    parser.add_argument(
        "output",
        nargs="?",
        default=None,
        help="Output PDF (default: Flyer_EI_Study_Updated.pdf)",
    )
    parser.add_argument(
        "--url",
        default=None,
        help="Study URL to generate QR from (ignored if --qr-image is set)",
    )
    parser.add_argument(
        "--qr-image",
        type=Path,
        default=None,
        help="Path to your custom QR code image (PNG). Use this instead of --url.",
    )
    parser.add_argument(
        "--qr-size",
        type=int,
        default=300,
        help="QR image size in pixels when generating from URL (default: 300)",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    if args.input:
        input_pdf = Path(args.input)
    else:
        # Prefer Flyer_EI_Study.pdf (exact EI layout), then Flyer_Template.pdf
        for candidate in [
            root / "Flyer_EI_Study.pdf",
            root / "Flyer_Template.pdf",
            root / "uploads" / "Flyer_Template.pdf",
            Path("Flyer_EI_Study.pdf"),
        ]:
            if candidate.exists():
                input_pdf = candidate
                break
        else:
            input_pdf = root / "Flyer_EI_Study.pdf"
    if not input_pdf.exists():
        print(f"Error: Input file not found: {input_pdf}", file=sys.stderr)
        sys.exit(1)

    output_pdf = Path(args.output) if args.output else (input_pdf.parent / "Flyer_EI_Study_Updated.pdf")

    print(f"Input:  {input_pdf}")
    print(f"Output: {output_pdf}")
    if args.qr_image:
        print(f"QR:    {args.qr_image} (custom image)")
    else:
        print(f"URL:   {args.url or DEFAULT_STUDY_URL} (generating QR)")

    replace_qr_in_pdf(
        input_pdf,
        output_pdf,
        study_url=args.url or DEFAULT_STUDY_URL,
        qr_image_path=args.qr_image,
        qr_size_px=args.qr_size,
    )
    print(f"Done. Updated flyer saved to: {output_pdf}")


if __name__ == "__main__":
    main()
