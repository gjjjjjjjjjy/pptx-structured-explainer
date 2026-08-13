#!/usr/bin/env python3
"""Render a PPTX/POTX to slide PNGs and a contact sheet using LibreOffice."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def find_soffice() -> str | None:
    candidates = [
        shutil.which("soffice"),
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "/usr/bin/libreoffice",
        "/usr/local/bin/soffice",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    return None


def has_powerpoint() -> bool:
    return sys.platform == "darwin" and Path("/Applications/Microsoft PowerPoint.app").is_dir()


def export_with_powerpoint(deck: Path, pdf_path: Path) -> None:
    script = r'''
on run argv
    set inputPath to item 1 of argv
    set outputPath to item 2 of argv
    tell application "Microsoft PowerPoint"
        activate
        open POSIX file inputPath
        set currentPresentation to active presentation
        save currentPresentation in (POSIX file outputPath) as save as PDF
        close currentPresentation saving no
    end tell
end run
'''
    subprocess.run(
        ["osascript", "-e", script, str(deck), str(pdf_path)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def export_with_libreoffice(deck: Path, pdf_path: Path, soffice: str) -> None:
    with tempfile.TemporaryDirectory(prefix="pptx-render-") as temp_name:
        temp_dir = Path(temp_name)
        profile_dir = temp_dir / "libreoffice-profile"
        profile_dir.mkdir()
        result = subprocess.run(
            [
                soffice,
                f"-env:UserInstallation={profile_dir.resolve().as_uri()}",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(temp_dir),
                str(deck),
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if result.returncode != 0:
            detail = result.stdout.strip() or "no LibreOffice diagnostic output"
            raise RuntimeError(
                f"LibreOffice conversion failed with exit code {result.returncode}: {detail}"
            )
        pdf_candidates = list(temp_dir.glob("*.pdf"))
        if len(pdf_candidates) != 1:
            raise RuntimeError("LibreOffice did not produce exactly one PDF")
        shutil.copy2(pdf_candidates[0], pdf_path)


def pdf_to_pngs(pdf_path: Path, output_dir: Path, dpi: int) -> list[Path]:
    pdftoppm = shutil.which("pdftoppm")
    if pdftoppm:
        prefix = output_dir / "slide"
        subprocess.run(
            [pdftoppm, "-png", "-r", str(dpi), str(pdf_path), str(prefix)],
            check=True,
        )
        return sorted(output_dir.glob("slide-*.png"))

    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError(
            "PDF rasterization requires pdftoppm (Poppler) or PyMuPDF."
        ) from exc

    document = fitz.open(pdf_path)
    scale = dpi / 72
    pages = []
    digits = max(2, len(str(len(document))))
    for index, page in enumerate(document, 1):
        destination = output_dir / f"slide-{index:0{digits}d}.png"
        pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
        pixmap.save(destination)
        pages.append(destination)
    return pages


def make_contact_sheet(pages: list[Path], destination: Path, columns: int = 4) -> bool:
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return False

    opened = [Image.open(page).convert("RGB") for page in pages]
    if not opened:
        return False
    thumb_width = 420
    ratio = thumb_width / opened[0].width
    thumb_height = round(opened[0].height * ratio)
    label_height = 34
    gap = 18
    rows = (len(opened) + columns - 1) // columns
    canvas = Image.new(
        "RGB",
        (
            gap + columns * (thumb_width + gap),
            gap + rows * (thumb_height + label_height + gap),
        ),
        "white",
    )
    draw = ImageDraw.Draw(canvas)
    for index, image in enumerate(opened, 1):
        row, column = divmod(index - 1, columns)
        x = gap + column * (thumb_width + gap)
        y = gap + row * (thumb_height + label_height + gap)
        thumbnail = image.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
        canvas.paste(thumbnail, (x, y + label_height))
        draw.text((x, y + 6), f"Slide {index}", fill="black")
        image.close()
    canvas.save(destination, quality=92)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=144)
    parser.add_argument(
        "--backend",
        choices=("auto", "powerpoint", "libreoffice"),
        default="auto",
        help="PDF export backend; auto prefers Microsoft PowerPoint on macOS",
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    deck = args.deck.resolve()
    output_dir = args.output_dir.resolve()
    if not deck.is_file():
        parser.error(f"presentation does not exist: {deck}")
    if output_dir.exists() and any(output_dir.iterdir()) and not args.force:
        parser.error("output directory is not empty; use --force or choose another directory")
    output_dir.mkdir(parents=True, exist_ok=True)
    if args.force:
        for old_page in output_dir.glob("slide-*.png"):
            old_page.unlink()
        for old_file in (output_dir / "contact-sheet.jpg", output_dir / f"{deck.stem}.pdf"):
            if old_file.exists():
                old_file.unlink()

    soffice = find_soffice()
    if args.backend == "powerpoint" or (args.backend == "auto" and has_powerpoint()):
        if not has_powerpoint():
            parser.error("Microsoft PowerPoint is not installed in /Applications")
        backend = "Microsoft PowerPoint"
    elif args.backend == "libreoffice" or (args.backend == "auto" and soffice):
        if not soffice:
            parser.error("LibreOffice executable was not found")
        backend = "LibreOffice"
    else:
        print("FAIL: no supported rendering backend found", file=sys.stderr)
        print("Install Microsoft PowerPoint on macOS or LibreOffice.", file=sys.stderr)
        raise SystemExit(2)

    pdf_path = output_dir / f"{deck.stem}.pdf"
    if backend == "Microsoft PowerPoint":
        export_with_powerpoint(deck, pdf_path)
    else:
        export_with_libreoffice(deck, pdf_path, soffice)

    pages = pdf_to_pngs(pdf_path, output_dir, args.dpi)
    contact_sheet = output_dir / "contact-sheet.jpg"
    contact_created = make_contact_sheet(pages, contact_sheet)

    print(f"backend={backend}")
    print(f"pdf={pdf_path}")
    print(f"slides={len(pages)}")
    for page in pages:
        print(page)
    if contact_created:
        print(f"contact_sheet={contact_sheet}")
    else:
        print("contact_sheet=not-created (install Pillow)")


if __name__ == "__main__":
    main()
