#!/usr/bin/env python3
"""Audit embedded media, external media, paths, and relationship targets."""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath

from defusedxml import ElementTree as ET


REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
DRAWING_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
OFFICE_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
LOCAL_PATTERNS = [
    re.compile(rb"/Users/", re.I),
    re.compile(rb"[A-Z]:\\", re.I),
    re.compile(rb"/(?:private/)?tmp/", re.I),
    re.compile(rb"file:(?://)?", re.I),
]


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
    embedded = linked = external_media = external_hyperlinks = 0
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
                for blip in root.findall(f".//{{{DRAWING_NS}}}blip"):
                    if blip.get(f"{{{OFFICE_REL_NS}}}embed"):
                        embedded += 1
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

        media = sorted(n for n in names if n.startswith("ppt/media/") and not n.endswith("/"))

    print(f"file={args.deck.resolve()}")
    print(
        f"embedded_blips={embedded} linked_blips={linked} "
        f"external_media={external_media} external_hyperlinks={external_hyperlinks}"
    )
    print(f"media_files={len(media)}")
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)
    print("PASS: no linked media, local paths, or missing relationship targets")


if __name__ == "__main__":
    main()

