#!/usr/bin/env python3
"""Render an SVG to PNG using an available local backend."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree as ET


CODEX_NODE = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
CODEX_NODE_MODULES = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules"


def svg_size(path: Path) -> tuple[int, int]:
    root = ET.parse(path).getroot()
    values = root.attrib.get("viewBox", "").replace(",", " ").split()
    if len(values) != 4:
        raise ValueError("SVG must provide a numeric viewBox")
    width, height = float(values[2]), float(values[3])
    if width <= 0 or height <= 0:
        raise ValueError("SVG viewBox must have positive width and height")
    return round(width), round(height)


def find_sharp() -> tuple[str, str] | None:
    nodes = [str(CODEX_NODE)] if CODEX_NODE.exists() else []
    system_node = shutil.which("node")
    if system_node:
        nodes.append(system_node)
    module_paths = []
    if os.environ.get("NODE_PATH"):
        module_paths.extend(os.environ["NODE_PATH"].split(os.pathsep))
    if CODEX_NODE_MODULES.exists():
        module_paths.append(str(CODEX_NODE_MODULES))
    for directory in (Path.cwd(), Path(__file__).resolve().parent):
        for parent in (directory, *directory.parents):
            candidate = parent / "node_modules"
            if candidate.exists():
                module_paths.append(str(candidate))
    for node in nodes:
        for modules in dict.fromkeys(module_paths):
            if (Path(modules) / "sharp").exists():
                return node, modules
        probe = subprocess.run(
            [node, "-e", "process.stdout.write(require.resolve('sharp'))"],
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
            check=False,
        )
        if probe.returncode == 0:
            resolved = Path(probe.stdout.strip()).resolve()
            for parent in resolved.parents:
                if parent.name == "node_modules":
                    return node, str(parent)
    return None


def choose_backend(requested: str):
    candidates = {
        "resvg": shutil.which("resvg"),
        "rsvg": shutil.which("rsvg-convert"),
        "sharp": find_sharp(),
    }
    if requested != "auto":
        if requested == "cairosvg":
            return requested, None
        if not candidates.get(requested):
            raise RuntimeError(f"requested backend is unavailable: {requested}")
        return requested, candidates[requested]
    for name in ("resvg", "rsvg", "sharp"):
        if candidates[name]:
            return name, candidates[name]
    try:
        import cairosvg  # noqa: F401
    except ImportError as exc:
        raise RuntimeError(
            "no non-browser SVG backend is available; install resvg, librsvg, Sharp, or CairoSVG"
        ) from exc
    return "cairosvg", None


def render(input_path: Path, output_path: Path, scale: float, requested_backend: str) -> str:
    width, height = svg_size(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    backend, executable = choose_backend(requested_backend)
    if backend == "resvg":
        command = [executable, "--zoom", str(scale), str(input_path), str(output_path)]
        subprocess.run(command, check=True)
    elif backend == "rsvg":
        command = [executable, "--zoom", str(scale), "--output", str(output_path), str(input_path)]
        subprocess.run(command, check=True)
    elif backend == "sharp":
        node, node_modules = executable
        helper = Path(__file__).with_name("svg_render_sharp.cjs")
        environment = dict(os.environ)
        environment["NODE_PATH"] = node_modules
        command = [node, str(helper), str(input_path), str(output_path), str(round(width * scale)), str(round(height * scale))]
        subprocess.run(command, check=True, env=environment)
    else:
        import cairosvg

        cairosvg.svg2png(
            url=str(input_path),
            write_to=str(output_path),
            output_width=round(width * scale),
            output_height=round(height * scale),
        )
    if not output_path.exists() or output_path.stat().st_size == 0:
        raise RuntimeError("renderer did not create a PNG")
    return backend


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--scale", type=float, default=1.0)
    parser.add_argument("--backend", choices=("auto", "resvg", "rsvg", "sharp", "cairosvg"), default="auto")
    args = parser.parse_args()
    if args.scale <= 0:
        parser.error("--scale must be positive")
    try:
        backend = render(args.input, args.output, args.scale, args.backend)
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"backend={backend}")
    print(f"output={args.output.resolve()}")


if __name__ == "__main__":
    main()
