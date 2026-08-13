#!/usr/bin/env python3
"""Write explicit East Asian fonts into native PPTX runs containing Han characters."""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

from defusedxml import minidom

from font_policy import recommend_fonts, renderer_font_families


HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
CJK_SEGMENT_RE = re.compile(r"([\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff00-\uffef]+)")
TITLE_PLACEHOLDERS = {"title", "ctrTitle", "subTitle"}
PATCHABLE = (
    re.compile(r"ppt/slides/slide\d+\.xml"),
    re.compile(r"ppt/charts/chart\d+\.xml"),
    re.compile(r"ppt/diagrams/data\d+\.xml"),
)


def direct_child(node, name: str):
    for child in node.childNodes:
        if child.nodeType == child.ELEMENT_NODE and child.tagName == name:
            return child
    return None


def run_text(run) -> str:
    return "".join(
        child.firstChild.data
        for child in run.getElementsByTagName("a:t")
        if child.firstChild is not None
    )


def is_title_run(run) -> bool:
    ancestor = run.parentNode
    while ancestor is not None:
        if getattr(ancestor, "tagName", None) == "p:sp":
            placeholders = ancestor.getElementsByTagName("p:ph")
            return bool(placeholders and placeholders[0].getAttribute("type") in TITLE_PLACEHOLDERS)
        ancestor = ancestor.parentNode
    return False


def ensure_run_properties(document, run):
    properties = direct_child(run, "a:rPr")
    if properties is not None:
        return properties
    properties = document.createElement("a:rPr")
    text_node = direct_child(run, "a:t")
    if text_node is not None:
        run.insertBefore(properties, text_node)
    else:
        run.appendChild(properties)
    return properties


def set_east_asian_font(document, properties, font: str) -> None:
    east_asian = direct_child(properties, "a:ea")
    if east_asian is None:
        east_asian = document.createElement("a:ea")
        insert_before = None
        for tag in ("a:cs", "a:sym", "a:hlinkClick", "a:hlinkMouseOver"):
            insert_before = direct_child(properties, tag)
            if insert_before is not None:
                break
        if insert_before is not None:
            properties.insertBefore(east_asian, insert_before)
        else:
            properties.appendChild(east_asian)
    east_asian.setAttribute("typeface", font)
    properties.setAttribute("lang", "zh-CN")


def set_latin_font(document, properties, font: str) -> None:
    latin = direct_child(properties, "a:latin")
    if latin is None:
        latin = document.createElement("a:latin")
        east_asian = direct_child(properties, "a:ea")
        if east_asian is not None:
            properties.insertBefore(latin, east_asian)
        else:
            properties.appendChild(latin)
    latin.setAttribute("typeface", font)


def set_text(run, value: str) -> None:
    text_nodes = run.getElementsByTagName("a:t")
    if not text_nodes:
        return
    text_node = text_nodes[0]
    while text_node.firstChild is not None:
        text_node.removeChild(text_node.firstChild)
    text_node.appendChild(run.ownerDocument.createTextNode(value))
    if value[:1].isspace() or value[-1:].isspace():
        text_node.setAttribute("xml:space", "preserve")
    elif text_node.hasAttribute("xml:space"):
        text_node.removeAttribute("xml:space")


def script_segments(value: str) -> list[tuple[str, bool]]:
    parts = []
    for part in CJK_SEGMENT_RE.split(value):
        if part:
            parts.append((part, bool(HAN_RE.search(part))))
    return parts


def patch_xml(
    data: bytes, title_font: str, body_font: str, title_latin: str, body_latin: str
) -> tuple[bytes, int]:
    document = minidom.parseString(data)
    changed = 0
    for run in list(document.getElementsByTagName("a:r")):
        value = run_text(run)
        if not HAN_RE.search(value):
            continue
        title = is_title_run(run)
        cjk_font = title_font if title else body_font
        latin_font = title_latin if title else body_latin
        segments = script_segments(value)
        if len(segments) > 1:
            parent = run.parentNode
            for segment, is_cjk in segments:
                clone = run.cloneNode(deep=True)
                set_text(clone, segment)
                properties = ensure_run_properties(document, clone)
                if is_cjk:
                    set_latin_font(document, properties, cjk_font)
                    set_east_asian_font(document, properties, cjk_font)
                else:
                    set_latin_font(document, properties, latin_font)
                parent.insertBefore(clone, run)
            parent.removeChild(run)
            changed += 1
            continue
        properties = ensure_run_properties(document, run)
        set_latin_font(document, properties, cjk_font)
        set_east_asian_font(document, properties, cjk_font)
        changed += 1

    for run in list(document.getElementsByTagName("a:fld")):
        if not HAN_RE.search(run_text(run)):
            continue
        title = is_title_run(run)
        cjk_font = title_font if title else body_font
        properties = ensure_run_properties(document, run)
        current_ea = direct_child(properties, "a:ea")
        current_latin = direct_child(properties, "a:latin")
        if (
            current_ea is not None
            and current_ea.getAttribute("typeface") == cjk_font
            and current_latin is not None
            and current_latin.getAttribute("typeface") == cjk_font
        ):
            continue
        set_latin_font(document, properties, cjk_font)
        set_east_asian_font(document, properties, cjk_font)
        changed += 1
    return document.toxml(encoding="UTF-8"), changed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--template", type=Path, help="Use this template's installed fonts before system defaults.")
    parser.add_argument(
        "--renderer",
        choices=("system", "powerpoint", "libreoffice"),
        default="system",
    )
    parser.add_argument("--title-font")
    parser.add_argument("--body-font")
    parser.add_argument("--allow-uninstalled", action="store_true")
    args = parser.parse_args()
    input_path = args.input.resolve()
    output_path = args.output.resolve()
    if input_path == output_path:
        parser.error("input and output must be different files")
    policy = recommend_fonts(args.template or input_path, renderer=args.renderer)
    title_font = args.title_font or policy["selection"]["title_cjk"]
    body_font = args.body_font or policy["selection"]["body_cjk"]
    title_latin = policy["selection"]["title_latin"]
    body_latin = policy["selection"]["body_latin"]
    if not title_font or not body_font:
        parser.error("no reliable CJK font was found; install one or pass explicit fonts")
    if not args.allow_uninstalled:
        installed, source = renderer_font_families(args.renderer)
        missing = [font for font in (title_font, body_font) if font.casefold() not in installed]
        if missing:
            parser.error(
                "selected font is not visible to "
                f"{args.renderer} ({source}): {', '.join(dict.fromkeys(missing))}"
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    changed_parts = 0
    changed_runs = 0
    try:
        source = zipfile.ZipFile(input_path)
    except (OSError, zipfile.BadZipFile) as exc:
        print(f"FAIL: cannot open presentation: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    with source, zipfile.ZipFile(output_path, "w") as destination:
        for info in source.infolist():
            data = source.read(info.filename)
            if any(pattern.fullmatch(info.filename) for pattern in PATCHABLE):
                try:
                    patched, changes = patch_xml(
                        data, title_font, body_font, title_latin, body_latin
                    )
                except Exception as exc:
                    print(f"FAIL: cannot patch {info.filename}: {exc}", file=sys.stderr)
                    raise SystemExit(1) from exc
                if changes:
                    data = patched
                    changed_parts += 1
                    changed_runs += changes
            destination.writestr(info, data)
    print(f"input={input_path}")
    print(f"output={output_path}")
    print(f"title_cjk={title_font}")
    print(f"body_cjk={body_font}")
    print(f"title_latin={title_latin}")
    print(f"body_latin={body_latin}")
    print(f"changed_parts={changed_parts} changed_han_runs={changed_runs}")


if __name__ == "__main__":
    main()
