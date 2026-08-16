#!/usr/bin/env python3
"""Install the explainer, PPT operator, and SVG diagram skills as one bundle."""

from __future__ import annotations

import argparse
import filecmp
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
EXPLAINER_FILES = ("SKILL.md", "agents", "assets", "references", "scripts", "tests", "LICENSE")
COMPANION_NAMES = ("pptx-operator", "svg-diagram-engine")
REQUIREMENTS = REPO_ROOT / "requirements.txt"
BUNDLED_FONT_DIR = REPO_ROOT / "assets" / "fonts" / "source-han-sans-sc"
BUNDLED_FONT_FILES = (
    "SourceHanSansSC-Regular.otf",
    "SourceHanSansSC-Bold.otf",
)


def configure_utf8_stdio() -> None:
    """Keep Windows consoles and redirected logs from failing on Unicode paths."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="backslashreplace")
            except (AttributeError, ValueError):
                pass


configure_utf8_stdio()


def default_codex_dir() -> Path:
    codex_root = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    return codex_root / "skills"


def copy_item(source: Path, destination: Path) -> None:
    if source.is_dir():
        shutil.copytree(
            source,
            destination,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
        )
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def prepare_destination(
    destination: Path, backup_directory: Path, force: bool, dry_run: bool
) -> Path | None:
    if not destination.exists():
        return None
    if not force:
        raise FileExistsError(
            f"destination already exists: {destination}; rerun with --force to replace it safely"
        )
    backup = backup_directory / destination.name
    if not dry_run:
        backup_directory.mkdir(parents=True, exist_ok=True)
        destination.rename(backup)
    return backup


def install_bundle(skills_dir: Path, force: bool, dry_run: bool) -> None:
    explainer_destination = skills_dir / "pptx-structured-explainer"
    companion_destinations = [skills_dir / name for name in COMPANION_NAMES]
    suffix = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_directory = skills_dir.parent / f"{skills_dir.name}-backups" / suffix
    backups = []
    for destination in (explainer_destination, *companion_destinations):
        backup = prepare_destination(
            destination,
            backup_directory=backup_directory,
            force=force,
            dry_run=dry_run,
        )
        if backup:
            backups.append(backup)

    print(f"skills_dir={skills_dir}")
    print(f"install={explainer_destination}")
    for destination in companion_destinations:
        print(f"install={destination}")
    for backup in backups:
        print(f"backup={backup}")
    if dry_run:
        return

    skills_dir.mkdir(parents=True, exist_ok=True)
    explainer_destination.mkdir(parents=True, exist_ok=True)
    for relative in EXPLAINER_FILES:
        copy_item(REPO_ROOT / relative, explainer_destination / relative)
    for name, destination in zip(COMPANION_NAMES, companion_destinations):
        shutil.copytree(
            REPO_ROOT / "companion" / name,
            destination,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
        )
        shutil.copy2(REPO_ROOT / "LICENSE", destination / "LICENSE")


def install_dependencies() -> None:
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS)],
        check=True,
    )


def user_font_directory() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Fonts"
    if sys.platform == "win32":
        local_app_data = os.environ.get("LOCALAPPDATA")
        base = Path(local_app_data) if local_app_data else Path.home() / "AppData" / "Local"
        return base / "Microsoft" / "Windows" / "Fonts"
    return Path.home() / ".local" / "share" / "fonts"


def register_windows_font(path: Path) -> None:
    import ctypes
    import winreg

    style = "Bold" if "Bold" in path.stem else "Regular"
    key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
        winreg.SetValueEx(
            key,
            f"Source Han Sans SC {style} (OpenType)",
            0,
            winreg.REG_SZ,
            str(path),
        )
    # Register for the current desktop session; the HKCU entry above makes it
    # persistent for future sign-ins without requiring administrator rights.
    loaded = ctypes.windll.gdi32.AddFontResourceExW(str(path), 0, 0)
    if loaded == 0:
        print(
            f"WARN: font registration is persistent but the current Windows session did not load it: {path}; "
            "restart PowerPoint or sign in again"
        )
    message_result = ctypes.c_ulong()
    ctypes.windll.user32.SendMessageTimeoutW(
        0xFFFF,
        0x001D,
        0,
        0,
        0x0002,
        1000,
        ctypes.byref(message_result),
    )


def install_bundled_fonts(dry_run: bool) -> None:
    destination = user_font_directory()
    print(f"font_dir={destination}")
    for filename in BUNDLED_FONT_FILES:
        source = BUNDLED_FONT_DIR / filename
        if not source.is_file():
            raise FileNotFoundError(f"bundled font is missing: {source}")
        target = destination / filename
        print(f"install_font={target}")
        if dry_run:
            continue
        destination.mkdir(parents=True, exist_ok=True)
        if not target.exists() or not filecmp.cmp(source, target, shallow=False):
            shutil.copy2(source, target)
        else:
            print(f"font_up_to_date={target}")
        if sys.platform == "win32":
            register_windows_font(target)
    if not dry_run and sys.platform not in {"darwin", "win32"}:
        fc_cache = shutil.which("fc-cache")
        if fc_cache:
            subprocess.run([fc_cache, "-f", str(destination)], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        choices=("claude", "codex", "both"),
        default="both",
        help="installation target (default: both)",
    )
    parser.add_argument(
        "--claude-dir",
        type=Path,
        default=Path.home() / ".claude" / "skills",
        help="override Claude Code skills directory",
    )
    parser.add_argument(
        "--codex-dir",
        type=Path,
        default=default_codex_dir(),
        help="override Codex skills directory",
    )
    parser.add_argument("--force", action="store_true", help="replace existing skills after backup")
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="install Python dependencies into the current interpreter environment",
    )
    parser.add_argument(
        "--install-fonts",
        action="store_true",
        help="install bundled Source Han Sans SC Regular/Bold into the current user's font directory",
    )
    parser.add_argument("--dry-run", action="store_true", help="show paths without writing")
    args = parser.parse_args()

    targets = []
    if args.target in ("claude", "both"):
        targets.append(args.claude_dir.expanduser().resolve())
    if args.target in ("codex", "both"):
        targets.append(args.codex_dir.expanduser().resolve())

    try:
        if args.install_deps and not args.dry_run:
            install_dependencies()
        if args.install_fonts:
            install_bundled_fonts(dry_run=args.dry_run)
        for skills_dir in dict.fromkeys(targets):
            install_bundle(skills_dir, force=args.force, dry_run=args.dry_run)
    except (OSError, FileExistsError, subprocess.CalledProcessError) as exc:
        print(f"INSTALL FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    print("INSTALL COMPLETE" if not args.dry_run else "DRY RUN COMPLETE")


if __name__ == "__main__":
    main()
