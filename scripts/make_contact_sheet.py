#!/usr/bin/env python3
"""Create a numbered contact sheet from rendered slide PNG files."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("rendered_dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--columns", type=int, default=4)
    parser.add_argument("--thumb-width", type=int, default=400)
    args = parser.parse_args()

    if args.columns <= 0 or args.thumb_width <= 0:
        parser.error("--columns and --thumb-width must be greater than zero")
    slides = sorted(args.rendered_dir.glob("slide-*.png"))
    if not slides:
        parser.error(f"no slide-*.png files found in {args.rendered_dir}")

    with Image.open(slides[0]) as sample:
        thumb_height = round(args.thumb_width * sample.height / sample.width)
    label_height = 32
    gap = 18
    cell_width = args.thumb_width + gap
    cell_height = thumb_height + label_height + gap
    rows = math.ceil(len(slides) / args.columns)
    sheet = Image.new("RGB", (cell_width * args.columns + gap, cell_height * rows + gap), "#ECEFF3")
    draw = ImageDraw.Draw(sheet)

    for index, slide_path in enumerate(slides, 1):
        with Image.open(slide_path) as source:
            thumb = ImageOps.contain(source.convert("RGB"), (args.thumb_width, thumb_height))
        column = (index - 1) % args.columns
        row = (index - 1) // args.columns
        x = gap + column * cell_width
        y = gap + row * cell_height
        sheet.paste(thumb, (x, y))
        draw.text((x, y + thumb_height + 6), f"Slide {index}", fill="#1F2937")

    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)
    print(f"slides={len(slides)}")
    print(f"contact_sheet={output}")


if __name__ == "__main__":
    main()
