#!/usr/bin/env python3
"""Validate the core package structure and internal relationships of a PPTX/POTX."""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path, PurePosixPath

from defusedxml import ElementTree as ET


REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def object_label(parent_map, transform) -> str:
    current = transform
    while current in parent_map:
        current = parent_map[current]
        kind = local_name(current.tag)
        if kind not in {"cxnSp", "sp", "pic", "graphicFrame", "grpSp"}:
            continue
        object_id = None
        object_name = None
        for element in current.iter():
            if local_name(element.tag) == "cNvPr":
                object_id = element.get("id")
                object_name = element.get("name")
                break
        details = [f"kind={'connector' if kind == 'cxnSp' else kind}"]
        if object_id:
            details.append(f"id={object_id}")
        if object_name:
            details.append(f"name={object_name!r}")
        return " ".join(details)
    return "kind=unknown"


def validate_transform_extents(part_name: str, root) -> list[str]:
    """Reject geometry PowerPoint repairs even when the XML is otherwise valid."""
    errors = []
    parent_map = {child: parent for parent in root.iter() for child in parent}
    for transform in root.findall(f".//{{{A_NS}}}xfrm"):
        label = object_label(parent_map, transform)
        for element_name in ("ext", "chExt"):
            extent = transform.find(f"{{{A_NS}}}{element_name}")
            if extent is None:
                continue
            for axis in ("cx", "cy"):
                raw = extent.get(axis)
                if raw is None:
                    continue
                try:
                    value = int(raw)
                except ValueError:
                    errors.append(
                        f"invalid transform extent: {part_name} {label} {element_name}.{axis}={raw!r}"
                    )
                    continue
                if value < 0:
                    errors.append(
                        f"negative transform extent: {part_name} {label} {element_name}.{axis}={value}; "
                        "PowerPoint may repair or discard this object"
                    )
    return errors


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
    try:
        zf = zipfile.ZipFile(args.deck)
    except (OSError, zipfile.BadZipFile) as exc:
        print(f"FAIL: cannot open package: {exc}")
        raise SystemExit(1) from exc

    with zf:
        names_list = zf.namelist()
        names = set(names_list)
        for duplicate in sorted({name for name in names_list if names_list.count(name) > 1}):
            errors.append(f"duplicate ZIP member: {duplicate}")

        for required in ("[Content_Types].xml", "_rels/.rels", "ppt/presentation.xml"):
            if required not in names:
                errors.append(f"missing required package part: {required}")

        for name in sorted(n for n in names if n.endswith(".rels")):
            try:
                root = ET.fromstring(zf.read(name))
            except Exception as exc:
                errors.append(f"invalid relationships XML {name}: {exc}")
                continue
            for rel in root.findall(f"{{{REL_NS}}}Relationship"):
                if rel.get("TargetMode", "").lower() == "external":
                    continue
                target = rel.get("Target", "")
                if not target or target.startswith("/"):
                    continue
                resolved = normalize_target(name, target)
                if resolved not in names:
                    errors.append(f"missing target: {name} -> {target} ({resolved})")

        for name in sorted(
            n for n in names if n.startswith("ppt/") and n.endswith(".xml")
        ):
            try:
                root = ET.fromstring(zf.read(name))
            except Exception as exc:
                errors.append(f"invalid presentation XML {name}: {exc}")
                continue
            errors.extend(validate_transform_extents(name, root))

        slide_count = 0
        if "ppt/presentation.xml" in names and "ppt/_rels/presentation.xml.rels" in names:
            try:
                rel_root = ET.fromstring(zf.read("ppt/_rels/presentation.xml.rels"))
                rel_targets = {
                    rel.get("Id"): normalize_target(
                        "ppt/_rels/presentation.xml.rels", rel.get("Target", "")
                    )
                    for rel in rel_root.findall(f"{{{REL_NS}}}Relationship")
                    if rel.get("TargetMode", "").lower() != "external"
                }
                pres_root = ET.fromstring(zf.read("ppt/presentation.xml"))
                for slide_id in pres_root.findall(f".//{{{P_NS}}}sldId"):
                    slide_count += 1
                    rel_id = slide_id.get(f"{{{R_NS}}}id")
                    target = rel_targets.get(rel_id)
                    if not target:
                        errors.append(f"presentation slide id has no relationship: {rel_id}")
                    elif target not in names:
                        errors.append(f"presentation references missing slide: {target}")
            except Exception as exc:
                errors.append(f"cannot parse presentation slide list: {exc}")

    print(f"file={args.deck.resolve()}")
    print(f"slides={slide_count} package_parts={len(names)}")
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)
    print("PASS: core package parts and internal relationships are consistent")


if __name__ == "__main__":
    main()
