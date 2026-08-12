# Self-contained PPTX Operations

## Contents

1. Capability map
2. Environment check
3. Inspect
4. Create
5. Edit text safely
6. Render and verify
7. Boundaries

## Capability map

Use the bundled tools when the host environment has no dedicated PPT skill:

| Need | Tool |
|---|---|
| dependency check | `scripts/check_environment.py` |
| slide/object inventory | `scripts/inventory_pptx.py` |
| create editable deck | `scripts/create_pptx.py` |
| exact text replacement | `scripts/replace_text.py` |
| embedded-media audit | `scripts/audit_media.py` |
| PDF and PNG fallback render | `scripts/render_pptx.py` |
| thumbnail overview | `scripts/make_contact_sheet.py` |

## Environment check

```bash
python scripts/check_environment.py
python -m pip install -r requirements.txt
```

LibreOffice is optional for creation and editing, but required for bundled fallback rendering.

## Inspect

```bash
python scripts/inventory_pptx.py source.pptx --json
python scripts/audit_media.py source.pptx
```

Inspect full-resolution rendered pages before proposing visual edits. Compare extracted source content with rendered output.

## Create

Create a JSON specification with dimensions in inches:

```json
{
  "layout": "wide",
  "theme": {"font": "Arial"},
  "slides": [
    {
      "background": "FFFFFF",
      "elements": [
        {"type": "text", "x": 0.7, "y": 0.5, "w": 12, "h": 0.7, "text": "Title", "font_size": 32, "bold": true},
        {"type": "shape", "shape": "rounded_rectangle", "x": 0.8, "y": 1.7, "w": 4, "h": 2, "fill": "EEF2FF", "line": "A5B4FC", "text": "Editable card", "font_size": 20}
      ]
    }
  ]
}
```

Run:

```bash
python scripts/create_pptx.py deck.json --output deck.pptx
```

Supported elements: `text`, `shape`, `line`, `image`, and `table`. Prefer SVG or images only for complex artwork; ordinary text, cards, and tables remain native PowerPoint objects.

## Edit text safely

Create `replacements.json`:

```json
{
  "Old title": "New title",
  "TTFT": "TTFT（首 Token 延迟）"
}
```

Run on a copy:

```bash
python scripts/replace_text.py source.pptx replacements.json --output reviewed.pptx
```

The script preserves unaffected shapes and formatting. When a replaced phrase spans multiple differently formatted runs, it collapses that paragraph into the first run and reports `mixed_format_paragraphs_collapsed`. Review those paragraphs visually. Do not use this operation for global redesign, chart data, equations, SmartArt, animation, or master changes.

## Render and verify

```bash
python scripts/render_pptx.py deck.pptx --output-dir rendered
python scripts/make_contact_sheet.py rendered --output contact-sheet.png
python scripts/audit_media.py deck.pptx
```

Treat LibreOffice output as a fallback preview. Use Microsoft PowerPoint for final fidelity when available.

## Boundaries

This public operation layer supports deterministic common operations. It does not reproduce every proprietary PowerPoint automation feature. For complex existing decks:

- preserve the source and work on a copy;
- avoid round-tripping untouched slides through broad rewriting tools;
- do not claim animations, SmartArt, charts, notes, equations, masters, or embedded objects are preserved without testing them;
- use a platform-native presentation application when the requested change depends on those features.
