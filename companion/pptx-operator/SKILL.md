---
name: pptx-operator
description: Create, inspect, edit, render, and validate PowerPoint PPTX/POTX presentations while preserving templates, editable content, notes, media, and unaffected slides. Use whenever a task opens, creates, modifies, converts, diagnoses, previews, or verifies a .pptx or .potx file, including template-based decks, speaker notes, embedded media, structural checks, and visual QA.
---

# PPTX Operator

Operate on PowerPoint files with a render-and-verify workflow. Prefer native PowerPoint objects for content that users must edit. Preserve package structure and unaffected content when modifying an existing deck.

## Choose the operation

- **Inspect**: run the inventory and media audit, extract visible text, then render every slide.
- **Create**: use `python-pptx` for native text, shapes, tables, charts, notes, and embedded images; set the slide dimensions before layout work.
- **Edit**: work on a copy. Use `python-pptx` only when it preserves the affected feature; use targeted OOXML edits when it does not.
- **Render**: use the bundled rendering entry point, then inspect full-resolution pages and a contact sheet.
- **Validate**: run package validation and media audit after every material change.

Read [references/operations.md](references/operations.md) before creating or editing a presentation. Read [references/render-and-qa.md](references/render-and-qa.md) before delivery.

## Required safety rules

- Never overwrite the source presentation during construction or diagnosis.
- Preserve masters, layouts, notes, animations, GIFs, charts, diagrams, and unaffected slide XML unless the user authorizes their replacement.
- Do not replace a whole slide to correct one label.
- Do not set an entire text frame through a convenience property when run-level formatting must survive; edit the relevant runs and paragraphs.
- Keep titles, ordinary text, code, simple shapes, tables, and supported charts native and editable.
- Embed images, SVGs, GIFs, audio, and video inside the package. Ordinary citation hyperlinks may remain external; linked media may not.
- Use real screenshots only for terminal output, application interfaces, photographs, or other evidence that should remain a picture.
- Preserve aspect ratios and keep rectangular screenshots inside their frames.
- Do not infer visual correctness from XML alone. Render and inspect the result.
- Reject negative DrawingML transform extents. PowerPoint can treat a connector with negative width or height as an out-of-bounds object and repair the file. Represent reverse direction with a non-negative extent plus `flipH`/`flipV`.

## Inspect first

Run:

```bash
python scripts/inventory_pptx.py deck.pptx
python scripts/font_policy.py --template deck.pptx --renderer libreoffice
python scripts/audit_pptx_fonts.py deck.pptx --libreoffice-safe
python scripts/audit_media.py deck.pptx
python scripts/validate_pptx.py deck.pptx
python scripts/render_pptx.py deck.pptx --output-dir rendered
```

The inventory recursively visits grouped shapes. Treat it as structural evidence, not a substitute for rendered-slide inspection.

For an existing presentation, record:

- slide size, masters, layouts, and placeholders;
- editable text, groups, pictures, SVGs, charts, tables, notes, and media;
- whole-slide images and text trapped inside pictures;
- external relationships and missing package parts;
- slides and elements that must remain unchanged.

## Create and edit

Use native objects whenever the format supports them. For template-derived work, create slides from existing layouts and preserve fixed master elements instead of recreating them on each slide.

Native connector geometry must use non-negative `cx` and `cy`. When the end point lies left of or above the start point, normalize the bounding box and encode direction with `flipH` and/or `flipV`.

For Chinese or mixed Chinese/Latin decks, select fonts from the template and the target renderer before creating native text. Keep Arial only for Latin-only runs. Write explicit DrawingML font metadata and `zh-CN` language metadata for every native run containing Han characters; LibreOffice does not reliably recover Chinese glyphs from an Arial-only run. For a LibreOffice target, split mixed Chinese/Latin runs and assign the chosen CJK font to both `a:latin` and `a:ea` on the Han runs. Use:

```bash
python scripts/font_policy.py --template template.pptx --renderer libreoffice
python scripts/apply_cjk_fonts.py draft.pptx draft-cjk.pptx \
  --template template.pptx --renderer libreoffice
python scripts/audit_pptx_fonts.py draft-cjk.pptx --libreoffice-safe --strict
```

Read [references/font-compatibility.md](references/font-compatibility.md) before creating, normalizing, or diagnosing Chinese native text.

When an existing deck contains negative connector extents, repair a copy and validate it again:

```bash
python scripts/normalize_connectors.py input.pptx output.pptx
python scripts/validate_pptx.py output.pptx
```

When direct OOXML editing is necessary:

1. unpack the PPTX into a temporary directory;
2. change only the required XML or relationship part;
3. preserve namespace prefixes and relationship identifiers;
4. rebuild the ZIP with `[Content_Types].xml` at the package root;
5. validate relationships and render the rebuilt file.

Do not manually duplicate slide XML without also updating presentation order, relationships, content types, notes, and any dependent parts.

## Visual verification

After each batch of changes:

1. validate the package;
2. audit embedded media;
3. render all changed slides at full resolution;
4. inspect the entire deck as a contact sheet;
5. copy the final file to an unrelated temporary directory and render the moved copy.

Fix clipping, overlap, font substitution, unreadable text, broken media, distorted images, ambiguous connectors, negative transform extents, inconsistent spacing, and placeholder residue before delivery.

When LibreOffice is a target or QA backend, treat an unsplit mixed-script run or a Han run whose `a:latin` and `a:ea` are not both the selected CJK font as a release failure. If `font_policy.py --renderer libreoffice` reports that no CJK font is visible, stop before building or rendering; do not assume host system fonts are visible inside a bundled LibreOffice runtime.

## Delivery report

Report:

- the output file and recovery-copy paths;
- changed and preserved slides;
- intentionally non-editable elements;
- structural validation result;
- embedded and linked media counts;
- rendering backend and rendered page count;
- moved-file test result.
