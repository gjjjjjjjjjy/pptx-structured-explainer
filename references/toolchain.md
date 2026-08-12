# Cross-platform PPTX Toolchain

## Contents

1. Capability selection
2. Python dependencies
3. Rendering dependencies
4. Recommended command sequence
5. Capability boundaries
6. Optional installable renderers

## Capability selection

Use capabilities in this order:

1. A dedicated PPT/PPTX skill in the current agent environment, when available.
2. Microsoft PowerPoint automation for final-fidelity rendering and slideshow checks.
3. The bundled Python scripts plus LibreOffice for a portable fallback.

Do not invent the name or behavior of a platform-specific skill. Inspect the current environment first. Keep the design and confirmation workflow in `SKILL.md` regardless of the execution backend.

## Python dependencies

Install the public Python dependencies with:

```bash
python -m pip install -r requirements.txt
```

The scripts use:

- `python-pptx` for structural inventory;
- `lxml` for the OOXML backend required by `python-pptx`;
- `defusedxml` for safe OOXML relationship parsing;
- `Pillow` for contact-sheet generation;
- `PyMuPDF` for converting rendered PDF pages to PNG.

## Rendering dependencies

`scripts/render_pptx.py` requires LibreOffice or Apache OpenOffice and searches for `libreoffice`, `soffice`, or the standard macOS LibreOffice application path. LibreOffice is not a substitute for a final Microsoft PowerPoint compatibility check when animations, GIF playback, embedded fonts, or exact Office typography matter.

Always compare the LibreOffice render with the native object/text inventory. Missing text or objects in the fallback render are evidence of a compatibility discrepancy until verified in Microsoft PowerPoint; they are not evidence that the source slide is incomplete.

## Recommended command sequence

```bash
python scripts/inventory_pptx.py deck.pptx --json
python scripts/audit_media.py deck.pptx
python scripts/render_pptx.py deck.pptx --output-dir rendered
python scripts/make_contact_sheet.py rendered --output contact-sheet.png
```

Inspect the full-resolution slide PNGs as well as the contact sheet. Repeat the media audit and rendering after every material edit.

## Capability boundaries

- `python-pptx` does not preserve or expose every PowerPoint feature reliably; avoid round-tripping complex existing decks through it unless the requested change requires it and the result is fully tested.
- LibreOffice rendering may differ from Microsoft PowerPoint in fonts, line breaking, SVG, animation, audio/video, and GIF behavior.
- Equations, EMF, grouped drawings, Chinese fonts, and theme-dependent text can be present in the PPTX while appearing incomplete in a fallback render.
- A successful render is execution evidence, not proof that every relationship, animation, or editable object remains semantically intact.
- Native PowerPoint text and simple shapes remain preferable, but generating sophisticated editable decks may require a platform-specific presentation library or application automation.

## Optional installable renderers

When the supplied environment cannot render the deck reliably, inspect the operating system and available software, then propose or install an appropriate renderer after obtaining any required system or network approval. Prefer official binaries, packages, containers, and repositories; do not build a large office suite from source unless the user explicitly requests it.

Use this order for Windows-targeted PPTX work:

1. **Microsoft PowerPoint on Windows**: use COM automation for the highest-fidelity PDF/image export when Office is installed and desktop automation is allowed.
2. **ONLYOFFICE Docs / DocumentServer**: use the official Community Edition or official Docker image for headless PPTX conversion and server-side review. Repository: `https://github.com/ONLYOFFICE/DocumentServer`.
3. **ONLYOFFICE Desktop Editors**: use the official Windows, macOS, or Linux release for local visual review when a server deployment is unnecessary. Repository: `https://github.com/ONLYOFFICE/DesktopEditors`.
4. **LibreOffice**: retain as the portable fallback and label Chinese font, equation, SVG, animation, and line-break differences as renderer discrepancies.

Before installing ONLYOFFICE:

- check whether Docker, a supported Windows installer, or the Desktop Editors package is the smaller deployment;
- prefer prebuilt official releases over cloning and compiling the repository;
- record the edition and license (`AGPL-3.0` for the Community Edition; proprietary terms may apply to other editions);
- install the presentation's required Chinese fonts or configure documented substitutes;
- render a representative Chinese/font/formula test slide before relying on it for batch QA;
- preserve the original PPTX and compare ONLYOFFICE output with native object/text inventory.

Do not treat browser-only `pptx-to-html` projects, Markdown presentation tools, or PPTX generators as fidelity renderers. They may be useful for creation or review prototypes, but they do not replace an Office-compatible layout engine.

Aspose.Slides and Syncfusion may be used when the user supplies or approves an appropriate commercial or temporary license. Never deliver evaluation-watermarked output as a final artifact.
