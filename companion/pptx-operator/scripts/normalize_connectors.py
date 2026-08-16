#!/usr/bin/env python3
"""Normalize negative native connector extents without overwriting the source PPTX."""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

from defusedxml import minidom

from cli_compat import configure_utf8_stdio


configure_utf8_stdio()

SLIDE_PART = re.compile(r"ppt/(?:slides|slideLayouts|slideMasters)/[^/]+\.xml")


def direct_child(node, tag_name: str):
    for child in node.childNodes:
        if child.nodeType == child.ELEMENT_NODE and child.tagName == tag_name:
            return child
    return None


def toggle_flag(node, name: str) -> None:
    enabled = node.getAttribute(name).casefold() in {"1", "true"}
    if enabled:
        node.removeAttribute(name)
    else:
        node.setAttribute(name, "1")


def normalize_connector(connector) -> bool:
    shape_properties = direct_child(connector, "p:spPr")
    transform = direct_child(shape_properties, "a:xfrm") if shape_properties else None
    offset = direct_child(transform, "a:off") if transform else None
    extent = direct_child(transform, "a:ext") if transform else None
    if offset is None or extent is None:
        return False

    changed = False
    for axis, size_axis, flip in (("x", "cx", "flipH"), ("y", "cy", "flipV")):
        try:
            origin = int(offset.getAttribute(axis))
            size = int(extent.getAttribute(size_axis))
        except ValueError:
            continue
        if size >= 0:
            continue
        offset.setAttribute(axis, str(origin + size))
        extent.setAttribute(size_axis, str(-size))
        toggle_flag(transform, flip)
        changed = True
    return changed


def patch_xml(data: bytes) -> tuple[bytes, int]:
    document = minidom.parseString(data)
    changed = sum(
        1
        for connector in document.getElementsByTagName("p:cxnSp")
        if normalize_connector(connector)
    )
    return document.toxml(encoding="UTF-8"), changed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    input_path = args.input.resolve()
    output_path = args.output.resolve()
    if input_path == output_path:
        parser.error("input and output must be different files")

    try:
        source = zipfile.ZipFile(input_path)
    except (OSError, zipfile.BadZipFile) as exc:
        print(f"FAIL: cannot open presentation: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    changed_parts = 0
    changed_connectors = 0
    with source, zipfile.ZipFile(output_path, "w") as destination:
        for info in source.infolist():
            data = source.read(info.filename)
            if SLIDE_PART.fullmatch(info.filename):
                patched, changes = patch_xml(data)
                if changes:
                    data = patched
                    changed_parts += 1
                    changed_connectors += changes
            destination.writestr(info, data)

    print(f"input={input_path}")
    print(f"output={output_path}")
    print(f"changed_parts={changed_parts} normalized_connectors={changed_connectors}")


if __name__ == "__main__":
    main()
