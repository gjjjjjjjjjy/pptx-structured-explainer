#!/usr/bin/env python3
"""Combine rendered diagram PNGs into a compact visual review sheet."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from cli_compat import configure_utf8_stdio


configure_utf8_stdio()

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--columns", type=int, default=2)
    args = parser.parse_args()
    if args.columns < 1:
        parser.error("--columns must be at least 1")

    thumb_width, thumb_height, caption_height, gutter = 720, 405, 46, 24
    rows = math.ceil(len(args.inputs) / args.columns)
    sheet = Image.new(
        "RGB",
        (gutter + args.columns * (thumb_width + gutter), gutter + rows * (thumb_height + caption_height + gutter)),
        "#E9EEF5",
    )
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=18)
    for index, path in enumerate(args.inputs):
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_width, thumb_height), Image.Resampling.LANCZOS)
        column, row = index % args.columns, index // args.columns
        x = gutter + column * (thumb_width + gutter)
        y = gutter + row * (thumb_height + caption_height + gutter)
        tile = Image.new("RGB", (thumb_width, thumb_height), "white")
        tile.paste(image, ((thumb_width - image.width) // 2, (thumb_height - image.height) // 2))
        sheet.paste(tile, (x, y))
        draw.text((x, y + thumb_height + 10), path.stem, fill="#172033", font=font)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.output)
    print(f"output={args.output.resolve()}")


if __name__ == "__main__":
    main()
