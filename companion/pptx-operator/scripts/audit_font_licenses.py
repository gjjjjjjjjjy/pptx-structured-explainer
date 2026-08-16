#!/usr/bin/env python3
"""Audit native PPTX text runs against the verified redistributable-font allowlist."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

from defusedxml import ElementTree as ET

from cli_compat import configure_utf8_stdio
from font_licenses import APPROVED_FONT_LICENSES, is_approved_font, license_record
from font_policy import A_NS


configure_utf8_stdio()

HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
LATIN_RE = re.compile(r"[A-Za-z0-9]")
AUDITED_PART = re.compile(
    r"ppt/(?:slides/slide|notesSlides/notesSlide|charts/chart|diagrams/data)\d+\.xml"
)


def font_value(properties, name: str) -> str | None:
    if properties is None:
        return None
    element = properties.find(f"{{{A_NS}}}{name}")
    return element.get("typeface") if element is not None else None


def audit(deck: Path) -> dict:
    issues = []
    checked_runs = 0
    approved_runs = 0
    used = {}
    with zipfile.ZipFile(deck) as package:
        part_names = sorted(name for name in package.namelist() if AUDITED_PART.fullmatch(name))
        for part_name in part_names:
            root = ET.fromstring(package.read(part_name))
            for paragraph_index, paragraph in enumerate(root.findall(f".//{{{A_NS}}}p"), 1):
                paragraph_properties = paragraph.find(f"{{{A_NS}}}pPr/{{{A_NS}}}defRPr")
                paragraph_latin = font_value(paragraph_properties, "latin")
                paragraph_ea = font_value(paragraph_properties, "ea")
                for run in list(paragraph):
                    if run.tag not in {f"{{{A_NS}}}r", f"{{{A_NS}}}fld"}:
                        continue
                    text = "".join(node.text or "" for node in run.findall(f".//{{{A_NS}}}t"))
                    has_han = bool(HAN_RE.search(text))
                    has_latin = bool(LATIN_RE.search(text))
                    if not has_han and not has_latin:
                        continue
                    properties = run.find(f"{{{A_NS}}}rPr")
                    if properties is not None and properties.find(f"{{{A_NS}}}sym") is not None:
                        continue
                    latin = font_value(properties, "latin") or paragraph_latin
                    east_asian = font_value(properties, "ea") or paragraph_ea
                    required = []
                    if has_han:
                        required.extend((("east_asian", east_asian), ("latin_for_han", latin)))
                    elif has_latin:
                        required.append(("latin", latin))
                    checked_runs += 1
                    run_issues = []
                    for role, font in required:
                        if not font:
                            run_issues.append(f"{role} font is implicit or missing")
                            continue
                        record = license_record(font)
                        used.setdefault(font, record)
                        if not is_approved_font(font):
                            run_issues.append(
                                f"{role} font {font!r} has no verified commercial-use and redistribution license"
                            )
                    if run_issues:
                        issues.append(
                            {
                                "part": part_name,
                                "paragraph": paragraph_index,
                                "text": text[:120],
                                "latin": latin,
                                "east_asian": east_asian,
                                "reasons": run_issues,
                            }
                        )
                    else:
                        approved_runs += 1
    return {
        "file": str(deck.resolve()),
        "policy": "verified commercial use and redistribution; unknown fonts fail closed",
        "approved_families": sorted(
            {record["family"] for record in APPROVED_FONT_LICENSES.values()}
        ),
        "checked_runs": checked_runs,
        "approved_runs": approved_runs,
        "issue_count": len(issues),
        "used_fonts": used,
        "issues": issues,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck", type=Path)
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when any run is unverified.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        report = audit(args.deck)
    except (OSError, zipfile.BadZipFile) as exc:
        print(f"FAIL: cannot audit presentation: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"file={report['file']}")
        print(
            f"checked_runs={report['checked_runs']} approved_runs={report['approved_runs']} "
            f"issues={report['issue_count']}"
        )
        for issue in report["issues"][:30]:
            print(
                f"FAIL part={issue['part']} text={issue['text']!r} "
                f"reason={'; '.join(issue['reasons'])}"
            )
        print("PASS" if report["issue_count"] == 0 else "FAIL")
    if args.strict and report["issue_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
