#!/usr/bin/env python3
"""Select explicit Latin and Simplified Chinese fonts from a PPTX template and target renderer."""

from __future__ import annotations

import argparse
import json
import platform
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from defusedxml import ElementTree as ET


A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
THEME_TOKENS = {"+mj-ea", "+mn-ea", "+mj-lt", "+mn-lt", ""}
CJK_PREFERENCES = {
    "Darwin": ["PingFang SC", "Hiragino Sans GB", "Heiti SC", "Noto Sans CJK SC", "Source Han Sans SC"],
    "Windows": ["Microsoft YaHei", "DengXian", "SimHei", "Noto Sans CJK SC", "Source Han Sans SC"],
    "Linux": ["Noto Sans CJK SC", "Noto Sans SC", "Source Han Sans SC", "WenQuanYi Micro Hei"],
}
LATIN_PREFERENCES = ["Arial", "Calibri", "Liberation Sans", "Noto Sans"]


def clean_font_name(value: str | None) -> str:
    return " ".join((value or "").strip().split())


def installed_font_families() -> tuple[dict[str, str], str]:
    families: dict[str, str] = {}
    fc_list = shutil.which("fc-list")
    if fc_list:
        result = subprocess.run(
            [fc_list, "--format=%{family}\n"], capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                for alias in line.split(","):
                    name = clean_font_name(alias)
                    if name:
                        families.setdefault(name.casefold(), name)
            if families:
                return families, "fontconfig"

    if sys.platform == "win32":
        try:
            import winreg

            key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                for index in range(winreg.QueryInfoKey(key)[1]):
                    display_name = winreg.EnumValue(key, index)[0]
                    name = re.sub(r"\s*\([^)]*\)\s*$", "", display_name).strip()
                    if name:
                        families.setdefault(name.casefold(), name)
        except OSError:
            pass
        if families:
            return families, "windows-registry"

    font_directories = [
        Path("/System/Library/Fonts"),
        Path("/Library/Fonts"),
        Path.home() / "Library/Fonts",
        Path("/usr/share/fonts"),
        Path("/usr/local/share/fonts"),
        Path.home() / ".local/share/fonts",
    ]
    for directory in font_directories:
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if path.suffix.lower() in {".ttf", ".ttc", ".otf"}:
                name = clean_font_name(re.sub(r"[-_](Regular|Medium|Bold).*$", "", path.stem, flags=re.I))
                if name:
                    families.setdefault(name.casefold(), name)
    return families, "font-file-scan"


def find_soffice() -> Path | None:
    for value in (
        shutil.which("soffice"),
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "/usr/bin/libreoffice",
        "/usr/local/bin/soffice",
    ):
        if value and Path(value).is_file():
            return Path(value).resolve()
    return None


def resolve_wrapper_target(path: Path) -> Path:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return path
    match = re.search(r'exec\s+"\$\{SCRIPT_DIR\}/([^"\n]+soffice)"', text)
    if not match:
        return path
    return (path.parent / match.group(1)).resolve()


def font_file_families(directory: Path, require_han: bool) -> dict[str, str]:
    try:
        from fontTools.ttLib import TTCollection, TTFont
    except ImportError as exc:
        raise RuntimeError("fontTools is required to inspect renderer-bundled fonts") from exc

    families = {}
    for path in directory.rglob("*") if directory.exists() else []:
        if path.suffix.lower() not in {".ttf", ".ttc", ".otf"}:
            continue
        fonts = []
        try:
            if path.suffix.lower() == ".ttc":
                fonts = list(TTCollection(path, lazy=True).fonts)
            else:
                fonts = [TTFont(path, lazy=True)]
            for font in fonts:
                codepoints = set()
                for table in font["cmap"].tables:
                    codepoints.update(table.cmap)
                has_han = any(
                    0x3400 <= codepoint <= 0x4DBF or 0x4E00 <= codepoint <= 0x9FFF
                    for codepoint in codepoints
                )
                if require_han and not has_han:
                    continue
                names = font["name"]
                for name_id in (16, 1):
                    for record in names.names:
                        if record.nameID != name_id:
                            continue
                        try:
                            family = clean_font_name(record.toUnicode())
                        except Exception:
                            continue
                        if family:
                            families.setdefault(family.casefold(), family)
                    if families:
                        break
        except Exception:
            continue
        finally:
            for font in fonts:
                try:
                    font.close()
                except Exception:
                    pass
    return families


def renderer_font_families(renderer: str) -> tuple[dict[str, str], str]:
    if renderer != "libreoffice":
        return installed_font_families()
    soffice = find_soffice()
    if soffice is None:
        return {}, "libreoffice-not-found"
    target = resolve_wrapper_target(soffice)
    if "libreoffice-headless" not in str(target):
        return installed_font_families()
    try:
        contents = target.parents[1]
        directory = contents / "Resources" / "fonts" / "truetype"
        # Use the renderer's complete private font set. CJK selection still comes
        # from known CJK candidates, while Latin selection must see Latin fonts too.
        families = font_file_families(directory, require_han=False)
    except (IndexError, RuntimeError):
        families = {}
    return families, f"libreoffice-bundled:{target}"


def _theme_group_fonts(group) -> list[str]:
    values = []
    east_asian = group.find(f"{{{A_NS}}}ea")
    if east_asian is not None:
        values.append(east_asian.get("typeface", ""))
    for font in group.findall(f"{{{A_NS}}}font"):
        if font.get("script") in {"Hans", "Hant"}:
            values.append(font.get("typeface", ""))
    return [clean_font_name(value) for value in values if clean_font_name(value) not in THEME_TOKENS]


def template_font_candidates(template: Path | None) -> dict[str, list[str]]:
    result = {"title_cjk": [], "body_cjk": [], "title_latin": [], "body_latin": []}
    if template is None:
        return result
    try:
        package = zipfile.ZipFile(template)
    except (OSError, zipfile.BadZipFile):
        return result
    with package:
        theme_names = sorted(
            name for name in package.namelist() if name.startswith("ppt/theme/theme") and name.endswith(".xml")
        )
        for name in theme_names:
            try:
                root = ET.fromstring(package.read(name))
            except Exception:
                continue
            for group_name, prefix in (("majorFont", "title"), ("minorFont", "body")):
                group = root.find(f".//{{{A_NS}}}{group_name}")
                if group is None:
                    continue
                result[f"{prefix}_cjk"].extend(_theme_group_fonts(group))
                latin = group.find(f"{{{A_NS}}}latin")
                if latin is not None:
                    value = clean_font_name(latin.get("typeface"))
                    if value and value not in THEME_TOKENS:
                        result[f"{prefix}_latin"].append(value)
    return {key: list(dict.fromkeys(values)) for key, values in result.items()}


def _pick(candidates: list[str], installed: dict[str, str]) -> tuple[str | None, str | None]:
    for candidate in candidates:
        resolved = installed.get(candidate.casefold())
        if resolved:
            return resolved, candidate
    return None, None


def recommend_fonts(template: Path | None = None, renderer: str = "system") -> dict:
    installed, source = renderer_font_families(renderer)
    template_fonts = template_font_candidates(template)
    system = platform.system()
    cjk_defaults = CJK_PREFERENCES.get(system, CJK_PREFERENCES["Linux"])

    title_cjk, title_match = _pick(template_fonts["title_cjk"], installed)
    body_cjk, body_match = _pick(template_fonts["body_cjk"], installed)
    fallback_source = "system" if renderer in {"system", "powerpoint"} else "renderer"
    title_source = "template" if title_cjk else fallback_source
    body_source = "template" if body_cjk else fallback_source
    if not title_cjk:
        title_cjk, title_match = _pick(cjk_defaults, installed)
    if not body_cjk:
        body_cjk, body_match = _pick(cjk_defaults, installed)
    if not title_cjk:
        title_cjk = body_cjk
    if not body_cjk:
        body_cjk = title_cjk

    title_latin, _ = _pick(template_fonts["title_latin"] + LATIN_PREFERENCES, installed)
    body_latin, _ = _pick(template_fonts["body_latin"] + LATIN_PREFERENCES, installed)
    return {
        "template": str(template.resolve()) if template else None,
        "platform": system,
        "renderer": renderer,
        "installed_font_source": source,
        "installed_font_count": len(installed),
        "template_candidates": template_fonts,
        "selection": {
            "title_cjk": title_cjk,
            "body_cjk": body_cjk,
            "title_latin": title_latin or "Arial",
            "body_latin": body_latin or "Arial",
            "title_cjk_source": title_source if title_cjk else None,
            "body_cjk_source": body_source if body_cjk else None,
        },
        "rule": (
            "Choose fonts visible to the target renderer. For LibreOffice, split mixed-script runs "
            "and write the selected CJK font to both a:latin and a:ea on Han runs; never rely on Arial fallback."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", type=Path, help="PPTX/POTX whose theme fonts take priority when installed.")
    parser.add_argument(
        "--renderer",
        choices=("system", "powerpoint", "libreoffice"),
        default="system",
        help="Select only fonts visible to the target renderer.",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = recommend_fonts(args.template, renderer=args.renderer)
    selection = report["selection"]
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(
            f"platform={report['platform']} renderer={report['renderer']} "
            f"installed_source={report['installed_font_source']}"
        )
        print(f"title_cjk={selection['title_cjk'] or 'NOT FOUND'} source={selection['title_cjk_source']}")
        print(f"body_cjk={selection['body_cjk'] or 'NOT FOUND'} source={selection['body_cjk_source']}")
        print(f"title_latin={selection['title_latin']}")
        print(f"body_latin={selection['body_latin']}")
        print(report["rule"])
    if not selection["title_cjk"] or not selection["body_cjk"]:
        print(
            "FAIL: no reliable Simplified Chinese font is visible to the selected renderer; "
            "install/configure Noto Sans CJK SC for that renderer or choose a backend with CJK fonts.",
            file=sys.stderr,
        )
        raise SystemExit(2)


if __name__ == "__main__":
    main()
