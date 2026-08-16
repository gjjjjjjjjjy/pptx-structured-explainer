#!/usr/bin/env python3
"""Render an SVG to PNG using an available local backend."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

from cli_compat import configure_utf8_stdio


configure_utf8_stdio()

CODEX_NODE = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
CODEX_NODE_MODULES = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules"


WINDOWS_POWERPOINT_SVG_SCRIPT = r'''
param(
    [Parameter(Mandatory=$true)][string]$InputPath,
    [Parameter(Mandatory=$true)][string]$OutputPath,
    [Parameter(Mandatory=$true)][double]$SlideWidth,
    [Parameter(Mandatory=$true)][double]$SlideHeight,
    [Parameter(Mandatory=$true)][int]$PixelWidth,
    [Parameter(Mandatory=$true)][int]$PixelHeight
)
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$powerPoint = $null
$presentation = $null
$slide = $null
$shape = $null
try {
    $powerPoint = New-Object -ComObject PowerPoint.Application
    $powerPoint.DisplayAlerts = 1
    $presentation = $powerPoint.Presentations.Add($false)
    $presentation.PageSetup.SlideWidth = $SlideWidth
    $presentation.PageSetup.SlideHeight = $SlideHeight
    $slide = $presentation.Slides.Add(1, 12)
    $shape = $slide.Shapes.AddPicture($InputPath, $false, $true, 0, 0, $SlideWidth, $SlideHeight)
    $slide.Export($OutputPath, "PNG", $PixelWidth, $PixelHeight)
    if (-not (Test-Path -LiteralPath $OutputPath)) {
        throw "PowerPoint Slide.Export did not create the requested PNG"
    }
}
finally {
    if ($null -ne $shape) {
        try { [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($shape) } catch {}
    }
    if ($null -ne $slide) {
        try { [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($slide) } catch {}
    }
    if ($null -ne $presentation) {
        try { $presentation.Close() } catch {}
        try { [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($presentation) } catch {}
    }
    if ($null -ne $powerPoint) {
        try { $powerPoint.Quit() } catch {}
        try { [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($powerPoint) } catch {}
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
'''


def svg_size(path: Path) -> tuple[int, int]:
    root = ET.parse(path).getroot()
    values = root.attrib.get("viewBox", "").replace(",", " ").split()
    if len(values) != 4:
        raise ValueError("SVG must provide a numeric viewBox")
    width, height = float(values[2]), float(values[3])
    if width <= 0 or height <= 0:
        raise ValueError("SVG viewBox must have positive width and height")
    return round(width), round(height)


def find_powershell() -> str | None:
    if sys.platform != "win32":
        return None
    for name in ("powershell.exe", "pwsh.exe", "powershell", "pwsh"):
        executable = shutil.which(name)
        if executable:
            return executable
    return None


def has_windows_powerpoint() -> bool:
    powershell = find_powershell()
    if not powershell:
        return False
    probe = (
        "$t=[type]::GetTypeFromProgID('PowerPoint.Application'); "
        "if ($null -eq $t) { exit 1 } else { exit 0 }"
    )
    result = subprocess.run(
        [powershell, "-NoProfile", "-NonInteractive", "-Command", probe],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    return result.returncode == 0


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
        "powerpoint": find_powershell() if has_windows_powerpoint() else None,
    }
    if requested != "auto":
        if requested == "cairosvg":
            return requested, None
        if not candidates.get(requested):
            raise RuntimeError(f"requested backend is unavailable: {requested}")
        return requested, candidates[requested]
    for name in ("resvg", "rsvg", "sharp", "powerpoint"):
        if candidates[name]:
            return name, candidates[name]
    try:
        import cairosvg  # noqa: F401
    except ImportError as exc:
        raise RuntimeError(
            "no non-browser SVG backend is available; install resvg, librsvg, Sharp, or CairoSVG, "
            "or install desktop PowerPoint on Windows"
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
    elif backend == "powerpoint":
        render_with_windows_powerpoint(
            input_path,
            output_path,
            width,
            height,
            scale,
            powershell=executable,
        )
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


def render_with_windows_powerpoint(
    input_path: Path,
    output_path: Path,
    width: int,
    height: int,
    scale: float,
    powershell: str | None = None,
) -> None:
    powershell = powershell or find_powershell()
    if not powershell:
        raise RuntimeError("PowerShell or Windows PowerPoint COM is unavailable")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # SVG viewBox units are treated as 96 dpi pixels; PowerPoint slide sizes use points.
    slide_width = width * 72 / 96
    slide_height = height * 72 / 96
    with tempfile.TemporaryDirectory(prefix="svg-powerpoint-") as temp_name:
        script_path = Path(temp_name) / "render-svg.ps1"
        script_path.write_text(WINDOWS_POWERPOINT_SVG_SCRIPT, encoding="utf-8-sig")
        command = [
            powershell,
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script_path),
            "-InputPath",
            str(input_path.resolve()),
            "-OutputPath",
            str(output_path.resolve()),
            "-SlideWidth",
            str(slide_width),
            "-SlideHeight",
            str(slide_height),
            "-PixelWidth",
            str(round(width * scale)),
            "-PixelHeight",
            str(round(height * scale)),
        ]
        result = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    if result.returncode != 0:
        detail = result.stdout.strip() or "no Windows PowerPoint SVG diagnostic output"
        raise RuntimeError(
            f"Windows PowerPoint SVG export failed with exit code {result.returncode}: {detail}"
        )
    if not output_path.is_file() or output_path.stat().st_size == 0:
        raise RuntimeError("Windows PowerPoint SVG export completed without a non-empty PNG")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--scale", type=float, default=1.0)
    parser.add_argument(
        "--backend",
        choices=("auto", "resvg", "rsvg", "sharp", "powerpoint", "cairosvg"),
        default="auto",
    )
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
