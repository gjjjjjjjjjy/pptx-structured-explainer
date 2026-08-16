#!/usr/bin/env python3
"""Audit embedded media, external media, paths, and relationship targets."""

from __future__ import annotations

import argparse
import base64
import binascii
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath

from defusedxml import ElementTree as ET

from cli_compat import configure_utf8_stdio


configure_utf8_stdio()

REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
DRAWING_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
OFFICE_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
XLINK_NS = "http://www.w3.org/1999/xlink"
DATA_IMAGE_RE = re.compile(
    r"^data:image/(?P<mime>png|jpe?g|webp);base64,(?P<data>[A-Za-z0-9+/=\s]+)$", re.I
)
CSS_URL_RE = re.compile(r"url\(([^)]+)\)", re.I)
LOCAL_PATTERNS = [
    re.compile(rb"/Users/", re.I),
    re.compile(rb"[A-Z]:\\", re.I),
    re.compile(rb"/(?:private/)?tmp/", re.I),
    re.compile(rb"file:(?://)?", re.I),
]


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def audit_svg(data: bytes, name: str, errors: list[str]) -> tuple[int, int]:
    embedded_images = 0
    external_references = 0
    try:
        root = ET.fromstring(data)
    except Exception as exc:
        errors.append(f"invalid embedded SVG {name}: {exc}")
        return embedded_images, external_references
    for element in root.iter():
        href = element.get("href") or element.get(f"{{{XLINK_NS}}}href")
        if href and not href.startswith("#"):
            match = DATA_IMAGE_RE.fullmatch(href)
            if local_name(element.tag) == "image" and match:
                try:
                    payload = base64.b64decode(
                        re.sub(r"\s+", "", match.group("data")), validate=True
                    )
                except (binascii.Error, ValueError):
                    payload = b""
                mime = match.group("mime").casefold()
                valid_signature = (
                    mime == "png" and payload.startswith(b"\x89PNG\r\n\x1a\n")
                    or mime in {"jpg", "jpeg"} and payload.startswith(b"\xff\xd8")
                    or mime == "webp"
                    and payload.startswith(b"RIFF")
                    and payload[8:12] == b"WEBP"
                )
                if payload and valid_signature:
                    embedded_images += 1
                else:
                    errors.append(f"invalid embedded image bytes inside {name}")
            else:
                external_references += 1
                errors.append(f"external reference inside {name}: {href[:120]}")
        for value in element.attrib.values():
            for target in CSS_URL_RE.findall(value):
                target = target.strip(" \"'")
                if target and not target.startswith("#"):
                    external_references += 1
                    errors.append(f"external CSS reference inside {name}: {target[:120]}")
    return embedded_images, external_references


def normalize_target(rel_path: str, target: str) -> str:
    source_dir = PurePosixPath(rel_path).parent.parent
    parts = []
    for part in (source_dir / target).parts:
        if part == "..":
            if parts:
                parts.pop()
        elif part not in (".", "/"):
            parts.append(part)
    return "/".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck", type=Path)
    args = parser.parse_args()

    errors = []
    embedded = linked = embedded_svg_blips = 0
    external_media = external_hyperlinks = 0
    svg_files = svg_embedded_images = svg_external_references = 0
    try:
        archive = zipfile.ZipFile(args.deck)
    except (OSError, zipfile.BadZipFile) as exc:
        print(f"FAIL: cannot open presentation package: {exc}")
        raise SystemExit(1) from exc

    with archive as zf:
        names = set(zf.namelist())
        for name in sorted(names):
            data = zf.read(name)
            if name.endswith((".xml", ".rels")):
                for pattern in LOCAL_PATTERNS:
                    if pattern.search(data):
                        errors.append(f"local path pattern in {name}: {pattern.pattern!r}")

            if name.startswith("ppt/slides/slide") and name.endswith(".xml"):
                root = ET.fromstring(data)
                for blip in root.iter():
                    if local_name(blip.tag) not in {"blip", "svgBlip"}:
                        continue
                    if blip.get(f"{{{OFFICE_REL_NS}}}embed"):
                        embedded += 1
                        if local_name(blip.tag) == "svgBlip":
                            embedded_svg_blips += 1
                    if blip.get(f"{{{OFFICE_REL_NS}}}link"):
                        linked += 1
                        errors.append(f"linked DrawingML image in {name}")

            if name.endswith(".rels"):
                root = ET.fromstring(data)
                for rel in root.findall(f"{{{REL_NS}}}Relationship"):
                    target = rel.get("Target", "")
                    mode = rel.get("TargetMode", "")
                    rel_type = rel.get("Type", "")
                    if mode.lower() == "external":
                        if rel_type.endswith("/hyperlink"):
                            external_hyperlinks += 1
                        else:
                            external_media += 1
                            errors.append(
                                f"external non-hyperlink relationship in {name}: "
                                f"type={rel_type} target={target}"
                            )
                        continue
                    if target and not target.startswith("/"):
                        resolved = normalize_target(name, target)
                        if resolved and resolved not in names:
                            errors.append(
                                f"missing relationship target in {name}: {target} -> {resolved}"
                            )

            if name.startswith("ppt/media/") and name.lower().endswith(".svg"):
                svg_files += 1
                embedded_count, external_count = audit_svg(data, name, errors)
                svg_embedded_images += embedded_count
                svg_external_references += external_count

        media = sorted(n for n in names if n.startswith("ppt/media/") and not n.endswith("/"))

    print(f"file={args.deck.resolve()}")
    print(
        f"embedded_blips={embedded} linked_blips={linked} "
        f"embedded_svg_blips={embedded_svg_blips} "
        f"external_media={external_media} external_hyperlinks={external_hyperlinks}"
    )
    print(
        f"media_files={len(media)} svg_files={svg_files} "
        f"svg_embedded_images={svg_embedded_images} "
        f"svg_external_references={svg_external_references}"
    )
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)
    print("PASS: no linked media, local paths, or missing relationship targets")


if __name__ == "__main__":
    main()
