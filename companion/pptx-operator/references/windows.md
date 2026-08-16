# Windows Operation

Use native Windows Python rather than WSL when Microsoft PowerPoint COM automation is required. WSL may invoke `powershell.exe`, but the skill intentionally enables the COM backend only when `sys.platform == "win32"` so Windows paths, user fonts, registry access, and Office automation share one environment.

## Requirements

- Windows 10 or Windows 11;
- Python 3.10 or later available as `python`;
- Windows PowerShell 5.1 or PowerShell 7;
- desktop Microsoft PowerPoint for the `powerpoint` rendering backend;
- LibreOffice only when the fallback backend is desired.

## Install from PowerShell

```powershell
git clone https://github.com/gjjjjjjjjjy/pptx-structured-explainer.git
Set-Location .\pptx-structured-explainer
python .\install.py --target both --install-deps --install-fonts
```

The font installer copies the bundled Source Han Sans SC Regular/Bold files into `%LOCALAPPDATA%\Microsoft\Windows\Fonts`, registers them under `HKCU\Software\Microsoft\Windows NT\CurrentVersion\Fonts`, attempts to load them into the current desktop session, and broadcasts `WM_FONTCHANGE`. Administrator rights are not required. Close PowerPoint before replacing an older installed font file. If a non-interactive session cannot load the font immediately, the persistent registration still applies after PowerPoint restarts or the user signs in again.

## Diagnose and render

```powershell
python .\companion\pptx-operator\scripts\render_pptx.py --diagnose
python .\companion\pptx-operator\scripts\render_pptx.py `
  .\deck.pptx `
  --output-dir .\rendered `
  --backend auto `
  --force
```

On Windows, `auto` prefers registered desktop PowerPoint and uses PowerShell COM automation to export PDF. It falls back to LibreOffice when PowerPoint is unavailable. PDF pages are converted with Poppler when installed and otherwise with the bundled Python dependency PyMuPDF.

The PowerPoint backend creates a UTF-8-BOM temporary `.ps1` script so Chinese input and output paths work under Windows PowerShell 5.1. The script opens the deck read-only, exports PDF using `ppSaveAsPDF`, closes the presentation, releases COM objects, and quits PowerPoint.

All bundled Python command-line entry points explicitly configure UTF-8 output. Chinese slide text, filenames, and audit findings therefore remain printable in Windows PowerShell, redirected log files, and CI environments whose legacy locale would otherwise default to `cp1252`.

PowerPoint COM requires an interactive desktop user session. Do not run the PowerPoint backend as a Windows service, in Session 0, or under a user account without an initialized Office profile. Use LibreOffice for unattended service execution.

## Font and portability checks

```powershell
python .\companion\pptx-operator\scripts\font_policy.py `
  --template .\deck.pptx `
  --renderer powerpoint
python .\companion\pptx-operator\scripts\apply_cjk_fonts.py `
  .\deck.pptx .\deck-open-fonts.pptx `
  --template .\deck.pptx `
  --renderer powerpoint
python .\companion\pptx-operator\scripts\audit_pptx_fonts.py `
  .\deck-open-fonts.pptx `
  --require-explicit-east-asian `
  --strict
python .\companion\pptx-operator\scripts\audit_font_licenses.py `
  .\deck-open-fonts.pptx `
  --strict
```

## SVG preview

```powershell
python .\companion\svg-diagram-engine\scripts\svg_validate.py `
  .\diagram.svg `
  --strict
python .\companion\svg-diagram-engine\scripts\svg_render.py `
  .\diagram.svg .\diagram.png `
  --backend auto
```

On Windows, SVG `auto` tries resvg, librsvg, Sharp, and then desktop PowerPoint before CairoSVG. The PowerPoint fallback creates a temporary blank presentation, inserts the SVG, exports the slide as PNG, and releases all COM objects.

## Regression tests

```powershell
python .\tests\run_harness.py
python .\tests\run_harness.py --render-backend powerpoint
```

The ordinary harness works without Office. The second command is the real end-to-end Windows test and requires desktop PowerPoint in the current interactive session.
