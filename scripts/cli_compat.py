"""Cross-platform command-line stream configuration."""

from __future__ import annotations

import sys


def configure_utf8_stdio() -> None:
    """Keep Windows consoles and redirected logs from failing on Unicode text."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="backslashreplace")
        except (AttributeError, ValueError):
            pass
