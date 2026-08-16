#!/usr/bin/env python3
"""Validate a presentation SVG for portability, safety, and basic readability."""

from __future__ import annotations

import argparse
import base64
import binascii
import re
import sys
from pathlib import Path

from defusedxml import ElementTree as ET

from cli_compat import configure_utf8_stdio


configure_utf8_stdio()

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
FORBIDDEN_TAGS = {"script", "foreignObject", "iframe", "audio", "video"}
URL_RE = re.compile(r"url\(([^)]+)\)", re.I)
EMBEDDED_IMAGE_RE = re.compile(
    r"^data:image/(?P<mime>png|jpe?g|webp);base64,(?P<data>[A-Za-z0-9+/=\s]+)$", re.I
)
APPROVED_FONT_FAMILIES = {
    "source han sans sc",
    "思源黑体",
    "source han serif sc",
    "思源宋体",
    "noto sans cjk sc",
    "noto sans sc",
    "noto serif cjk sc",
    "noto serif sc",
    "ibm plex sans sc",
    "ibm plex sans",
    "ibm plex mono",
    "inter",
}
GENERIC_FONT_FAMILIES = {"sans-serif", "serif", "monospace"}


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


def embedded_image_error(href: str) -> str | None:
    match = EMBEDDED_IMAGE_RE.fullmatch(href)
    if not match:
        return "only PNG, JPEG, or WebP base64 data URIs are allowed for embedded SVG images"
    try:
        payload = base64.b64decode(re.sub(r"\s+", "", match.group("data")), validate=True)
    except (binascii.Error, ValueError):
        return "embedded SVG image has invalid base64 data"
    if not payload:
        return "embedded SVG image payload is empty"
    mime = match.group("mime").casefold()
    valid_signature = (
        mime == "png" and payload.startswith(b"\x89PNG\r\n\x1a\n")
        or mime in {"jpg", "jpeg"} and payload.startswith(b"\xff\xd8")
        or mime == "webp" and payload.startswith(b"RIFF") and payload[8:12] == b"WEBP"
    )
    if not valid_signature:
        return "embedded SVG image bytes do not match the declared media type"
    return None


def declared_font_family(element) -> str | None:
    value = element.attrib.get("font-family")
    if value:
        return value
    style = element.attrib.get("style", "")
    match = re.search(r"(?:^|;)\s*font-family\s*:\s*([^;]+)", style, re.I)
    return match.group(1).strip() if match else None


def check_font_license(value: str) -> list[str]:
    errors = []
    families = [part.strip().strip("\"'").casefold() for part in value.split(",")]
    explicit = [family for family in families if family and family not in GENERIC_FONT_FAMILIES]
    if not any(family in APPROVED_FONT_FAMILIES for family in explicit):
        errors.append(f"font stack has no verified redistributable family: {value}")
    for family in explicit:
        if family not in APPROVED_FONT_FAMILIES:
            errors.append(f"font family has no verified commercial-use and redistribution license: {family}")
    return errors


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
    parent_map = {child: parent for parent in root.iter() for child in parent}
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
            if tag == "image" and href.startswith("data:image/"):
                error = embedded_image_error(href)
                if error:
                    errors.append(error)
            else:
                errors.append(f"external href is not portable: {href[:80]}")
        for key, value in element.attrib.items():
            if key.lower().startswith("on"):
                errors.append(f"event handler attribute is forbidden: {key}")
            for target in URL_RE.findall(value):
                target = target.strip(" \"'")
                if not target.startswith("#"):
                    errors.append(f"external CSS URL is not portable: {target[:80]}")

        if tag == "text":
            font_family = declared_font_family(element)
            ancestor = parent_map.get(element)
            while not font_family and ancestor is not None:
                font_family = declared_font_family(ancestor)
                ancestor = parent_map.get(ancestor)
            if not font_family:
                errors.append("text has no explicit or inherited font-family license declaration")
            else:
                errors.extend(check_font_license(font_family))
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
