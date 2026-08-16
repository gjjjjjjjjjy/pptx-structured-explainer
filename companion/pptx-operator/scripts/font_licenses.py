#!/usr/bin/env python3
"""Conservative allowlist for fonts with verified commercial-use and redistribution terms."""

from __future__ import annotations


APPROVED_FONT_LICENSES = {
    "source han sans sc": {
        "family": "Source Han Sans SC",
        "license": "SIL Open Font License 1.1",
        "source": "https://github.com/adobe-fonts/source-han-sans/blob/release/LICENSE.txt",
    },
    "思源黑体": {
        "family": "Source Han Sans SC",
        "license": "SIL Open Font License 1.1",
        "source": "https://github.com/adobe-fonts/source-han-sans/blob/release/LICENSE.txt",
    },
    "source han serif sc": {
        "family": "Source Han Serif SC",
        "license": "SIL Open Font License 1.1",
        "source": "https://github.com/adobe-fonts/source-han-serif/blob/release/LICENSE.txt",
    },
    "思源宋体": {
        "family": "Source Han Serif SC",
        "license": "SIL Open Font License 1.1",
        "source": "https://github.com/adobe-fonts/source-han-serif/blob/release/LICENSE.txt",
    },
    "noto sans cjk sc": {
        "family": "Noto Sans CJK SC",
        "license": "SIL Open Font License 1.1",
        "source": "https://github.com/notofonts/noto-cjk/blob/main/Sans/LICENSE",
    },
    "noto sans sc": {
        "family": "Noto Sans SC",
        "license": "SIL Open Font License 1.1",
        "source": "https://github.com/notofonts/noto-cjk/blob/main/Sans/LICENSE",
    },
    "noto serif cjk sc": {
        "family": "Noto Serif CJK SC",
        "license": "SIL Open Font License 1.1",
        "source": "https://github.com/notofonts/noto-cjk/blob/main/Serif/LICENSE",
    },
    "noto serif sc": {
        "family": "Noto Serif SC",
        "license": "SIL Open Font License 1.1",
        "source": "https://github.com/notofonts/noto-cjk/blob/main/Serif/LICENSE",
    },
    "ibm plex sans sc": {
        "family": "IBM Plex Sans SC",
        "license": "SIL Open Font License 1.1",
        "source": "https://github.com/IBM/plex/blob/master/LICENSE.txt",
    },
    "ibm plex sans": {
        "family": "IBM Plex Sans",
        "license": "SIL Open Font License 1.1",
        "source": "https://github.com/IBM/plex/blob/master/LICENSE.txt",
    },
    "ibm plex mono": {
        "family": "IBM Plex Mono",
        "license": "SIL Open Font License 1.1",
        "source": "https://github.com/IBM/plex/blob/master/LICENSE.txt",
    },
    "inter": {
        "family": "Inter",
        "license": "SIL Open Font License 1.1",
        "source": "https://github.com/rsms/inter/blob/master/LICENSE.txt",
    },
}


def license_record(font: str | None) -> dict[str, str] | None:
    return APPROVED_FONT_LICENSES.get((font or "").strip().casefold())


def is_approved_font(font: str | None) -> bool:
    return license_record(font) is not None


def approved_candidates(fonts: list[str]) -> list[str]:
    return [font for font in fonts if is_approved_font(font)]
