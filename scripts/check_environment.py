#!/usr/bin/env python3
"""Check whether the public PPTX operation toolchain is available."""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path


PACKAGES = {
    "pptx": "python-pptx",
    "defusedxml": "defusedxml",
    "lxml.etree": "lxml",
    "PIL": "Pillow",
    "fitz": "PyMuPDF",
}


def is_available(module: str) -> bool:
    try:
        return importlib.util.find_spec(module) is not None
    except (ImportError, ModuleNotFoundError):
        return False


def main() -> None:
    packages = {name: is_available(module) for module, name in PACKAGES.items()}
    office = shutil.which("libreoffice") or shutil.which("soffice")
    mac_office = Path("/Applications/LibreOffice.app/Contents/MacOS/soffice")
    if not office and mac_office.exists():
        office = str(mac_office)
    result = {
        "python": sys.executable,
        "packages": packages,
        "libreoffice": office,
        "can_inspect_create_edit": packages["python-pptx"] and packages["lxml"],
        "can_audit_media": packages["defusedxml"],
        "can_make_contact_sheet": packages["Pillow"],
        "can_render_with_fallback": bool(office and packages["PyMuPDF"]),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not all(packages.values()):
        print("Install missing Python packages with: python -m pip install -r requirements.txt", file=sys.stderr)


if __name__ == "__main__":
    main()
