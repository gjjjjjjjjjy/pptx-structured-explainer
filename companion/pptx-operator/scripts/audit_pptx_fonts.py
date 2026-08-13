#!/usr/bin/env python3
"""Audit native PPTX text for Han runs that rely on unsafe Latin-font fallback."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

from defusedxml import ElementTree as ET

from font_policy import A_NS, template_font_candidates


HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
LATIN_RE = re.compile(r"[A-Za-z0-9]")
RISKY_CJK_FONTS = {"arial", "calibri", "liberation sans", "times new roman", "courier new"}


def font_value(properties, name: str) -> str | None:
    if properties is None:
        return None
    element = properties.find(f"{{{A_NS}}}{name}")
    return element.get("typeface") if element is not None else None


def audit(deck: Path, require_explicit: bool, libreoffice_safe: bool) -> dict:
    theme = template_font_candidates(deck)
    theme_cjk = set(theme["title_cjk"] + theme["body_cjk"])
    rows = []
    counts = {"han_runs": 0, "explicit_ea": 0, "theme_inherited": 0, "risky": 0}
    with zipfile.ZipFile(deck) as package:
        slide_names = sorted(
            name for name in package.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)
        )
        for slide_index, name in enumerate(slide_names, 1):
            root = ET.fromstring(package.read(name))
            for paragraph in root.findall(f".//{{{A_NS}}}p"):
                paragraph_properties = paragraph.find(f"{{{A_NS}}}pPr/{{{A_NS}}}defRPr")
                paragraph_ea = font_value(paragraph_properties, "ea")
                paragraph_latin = font_value(paragraph_properties, "latin")
                for run in list(paragraph):
                    if run.tag not in {f"{{{A_NS}}}r", f"{{{A_NS}}}fld"}:
                        continue
                    text = "".join(node.text or "" for node in run.findall(f".//{{{A_NS}}}t"))
                    if not HAN_RE.search(text):
                        continue
                    counts["han_runs"] += 1
                    run_properties = run.find(f"{{{A_NS}}}rPr")
                    east_asian = font_value(run_properties, "ea") or paragraph_ea
                    latin = font_value(run_properties, "latin") or paragraph_latin
                    reason = None
                    status = "explicit_ea"
                    if east_asian and east_asian.casefold() not in RISKY_CJK_FONTS:
                        if libreoffice_safe and LATIN_RE.search(text):
                            status = "risky"
                            reason = "Han and Latin glyphs share one run; split them for LibreOffice"
                        elif libreoffice_safe and (
                            not latin
                            or latin.casefold() in RISKY_CJK_FONTS
                            or latin.casefold() != east_asian.casefold()
                        ):
                            status = "risky"
                            reason = "LibreOffice-safe Han runs require the same reliable CJK font in a:latin and a:ea"
                        else:
                            counts["explicit_ea"] += 1
                    elif east_asian:
                        status = "risky"
                        reason = f"East Asian typeface is not a reliable CJK font: {east_asian}"
                    elif latin and latin.casefold() in RISKY_CJK_FONTS:
                        status = "risky"
                        reason = f"Han text has Latin typeface {latin} but no explicit a:ea"
                    elif theme_cjk and not require_explicit:
                        status = "theme_inherited"
                        counts["theme_inherited"] += 1
                    else:
                        status = "risky"
                        reason = "Han text has no explicit DrawingML a:ea typeface"
                    if status == "risky":
                        counts["risky"] += 1
                        rows.append(
                            {
                                "slide": slide_index,
                                "text": text[:120],
                                "latin": latin,
                                "east_asian": east_asian,
                                "reason": reason,
                            }
                        )
    return {"file": str(deck.resolve()), "theme_cjk": sorted(theme_cjk), **counts, "issues": rows}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck", type=Path)
    parser.add_argument("--require-explicit-east-asian", action="store_true")
    parser.add_argument(
        "--libreoffice-safe",
        action="store_true",
        help="Also require script-split runs and a CJK a:latin typeface for Han runs.",
    )
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when risky Han runs are found.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        report = audit(args.deck, args.require_explicit_east_asian, args.libreoffice_safe)
    except (OSError, zipfile.BadZipFile) as exc:
        print(f"FAIL: cannot audit presentation: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"file={report['file']}")
        print(
            f"han_runs={report['han_runs']} explicit_ea={report['explicit_ea']} "
            f"theme_inherited={report['theme_inherited']} risky={report['risky']}"
        )
        for issue in report["issues"][:20]:
            print(f"FAIL slide={issue['slide']} text={issue['text']!r} reason={issue['reason']}")
        print("PASS" if report["risky"] == 0 else "FAIL")
    if args.strict and report["risky"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
