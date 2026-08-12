#!/usr/bin/env python3
"""Render a PPTX/POTX deck to PDF and per-slide PNG files with LibreOffice."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


MACOS_LIBREOFFICE = Path("/Applications/LibreOffice.app/Contents/MacOS/soffice")


def find_office() -> str | None:
    for command in ("libreoffice", "soffice"):
        resolved = shutil.which(command)
        if resolved:
            return resolved
    if MACOS_LIBREOFFICE.exists():
        return str(MACOS_LIBREOFFICE)
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("deck", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=150)
    args = parser.parse_args()

    deck = args.deck.expanduser().resolve()
    if not deck.is_file():
        parser.error(f"presentation not found: {deck}")
    if args.dpi <= 0:
        parser.error("--dpi must be greater than zero")

    try:
        import fitz
    except ImportError:
        print(
            "PyMuPDF is required. Run: python -m pip install -r requirements.txt",
            file=sys.stderr,
        )
        sys.exit(4)

    office = find_office()
    if not office:
        print("LibreOffice/soffice was not found. Install LibreOffice or use a platform PPT renderer.", file=sys.stderr)
        sys.exit(2)

    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="pptx-render-") as temporary:
        temp_dir = Path(temporary)
        command = [office, "--headless", "--convert-to", "pdf", "--outdir", str(temp_dir), str(deck)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=180)
        if result.returncode != 0:
            print(result.stdout, file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            sys.exit(result.returncode)

        pdf = temp_dir / f"{deck.stem}.pdf"
        if not pdf.is_file():
            print(f"renderer did not create the expected PDF: {pdf}", file=sys.stderr)
            sys.exit(3)

        delivered_pdf = output_dir / pdf.name
        shutil.copy2(pdf, delivered_pdf)
        with fitz.open(pdf) as document:
            slide_count = len(document)
            scale = args.dpi / 72
            matrix = fitz.Matrix(scale, scale)
            for index, page in enumerate(document, 1):
                image = page.get_pixmap(matrix=matrix, alpha=False)
                image.save(output_dir / f"slide-{index:03d}.png")

    print(f"renderer={office}")
    print(f"slides={slide_count}")
    print(f"pdf={delivered_pdf}")
    print(f"png_dir={output_dir}")


if __name__ == "__main__":
    main()
