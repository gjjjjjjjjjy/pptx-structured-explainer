#!/usr/bin/env python3
"""Validate a presentation SVG for portability, safety, and basic readability."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from defusedxml import ElementTree as ET


SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
FORBIDDEN_TAGS = {"script", "foreignObject", "iframe", "audio", "video"}
URL_RE = re.compile(r"url\(([^)]+)\)", re.I)


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def number(value: str | None) -> float | None:
    if value is None:
        return None
    match = re.match(r"^\s*(-?\d+(?:\.\d+)?)", value)
    return float(match.group(1)) if match else None


def check_bounds(element, width: float, height: float, warnings: list[str]) -> None:
    tag = local_name(element.tag)
    attrs = element.attrib
    points: list[tuple[float, float]] = []
    if tag in {"rect", "image", "text", "use"}:
        x = number(attrs.get("x")) or 0
        y = number(attrs.get("y")) or 0
        w = number(attrs.get("width")) or 0
        h = number(attrs.get("height")) or 0
        points.extend([(x, y), (x + w, y + h)])
    elif tag == "circle":
        cx = number(attrs.get("cx")) or 0
        cy = number(attrs.get("cy")) or 0
        radius = number(attrs.get("r")) or 0
        points.extend([(cx - radius, cy - radius), (cx + radius, cy + radius)])
    elif tag == "ellipse":
        cx = number(attrs.get("cx")) or 0
        cy = number(attrs.get("cy")) or 0
        rx = number(attrs.get("rx")) or 0
        ry = number(attrs.get("ry")) or 0
        points.extend([(cx - rx, cy - ry), (cx + rx, cy + ry)])
    elif tag == "line":
        points.extend(
            [
                (number(attrs.get("x1")) or 0, number(attrs.get("y1")) or 0),
                (number(attrs.get("x2")) or 0, number(attrs.get("y2")) or 0),
            ]
        )
    if points and any(x < -2 or y < -2 or x > width + 2 or y > height + 2 for x, y in points):
        warnings.append(f"<{tag}> has a simple coordinate outside the viewBox")


def validate(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        root = ET.parse(path).getroot()
    except Exception as exc:  # defusedxml provides the important parser hardening.
        return [f"cannot parse SVG: {exc}"], warnings

    if local_name(root.tag) != "svg":
        errors.append("root element must be <svg>")
        return errors, warnings
    if not root.tag.startswith(f"{{{SVG_NS}}}"):
        errors.append("SVG namespace is missing or invalid")

    view_box = root.attrib.get("viewBox", "").replace(",", " ").split()
    if len(view_box) != 4:
        errors.append("viewBox must contain four numbers")
        return errors, warnings
    try:
        min_x, min_y, width, height = map(float, view_box)
    except ValueError:
        errors.append("viewBox contains a non-numeric value")
        return errors, warnings
    if min_x != 0 or min_y != 0:
        warnings.append("a 0 0 width height viewBox is preferred for slide handoff")
    if width <= 0 or height <= 0:
        errors.append("viewBox width and height must be positive")
        return errors, warnings

    ids: set[str] = set()
    for element in root.iter():
        tag = local_name(element.tag)
        if tag in FORBIDDEN_TAGS:
            errors.append(f"forbidden element: <{tag}>")
        element_id = element.attrib.get("id")
        if element_id:
            if element_id in ids:
                errors.append(f"duplicate id: {element_id}")
            ids.add(element_id)

        href = element.attrib.get("href") or element.attrib.get(f"{{{XLINK_NS}}}href")
        if href and not href.startswith("#"):
            errors.append(f"external href is not portable: {href[:80]}")
        for key, value in element.attrib.items():
            if key.lower().startswith("on"):
                errors.append(f"event handler attribute is forbidden: {key}")
            for target in URL_RE.findall(value):
                target = target.strip(" \"'")
                if not target.startswith("#"):
                    errors.append(f"external CSS URL is not portable: {target[:80]}")

        if tag == "text":
            size = number(element.attrib.get("font-size"))
            style = element.attrib.get("style", "")
            if size is None:
                match = re.search(r"font-size\s*:\s*(\d+(?:\.\d+)?)", style)
                size = float(match.group(1)) if match else None
            if size is not None and size < 16:
                warnings.append(f"text smaller than 16 px: {size:g} px")
        check_bounds(element, width, height, warnings)

    if not any(local_name(element.tag) == "title" for element in root.iter()):
        warnings.append("add a <title> element for accessibility")
    return list(dict.fromkeys(errors)), list(dict.fromkeys(warnings))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures.")
    args = parser.parse_args()

    errors, warnings = validate(args.input)
    for message in warnings:
        print(f"WARN: {message}")
    for message in errors:
        print(f"FAIL: {message}")
    if errors or (warnings and args.strict):
        print(f"RESULT: FAIL ({len(errors)} errors, {len(warnings)} warnings)")
        sys.exit(1)
    print(f"RESULT: PASS ({len(warnings)} warnings)")


if __name__ == "__main__":
    main()
