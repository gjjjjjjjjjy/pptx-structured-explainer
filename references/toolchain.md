# Cross-platform PPTX Toolchain

## Contents

1. Capability selection
2. Python dependencies
3. Rendering dependencies
4. Recommended command sequence
5. Capability boundaries

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
