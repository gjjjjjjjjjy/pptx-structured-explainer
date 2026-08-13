# QA and Portability

## Contents

1. Content QA
2. Structural QA
3. Visual QA
4. Media audit
5. Portability test
6. Delivery report

## Content QA

Check:

- outline and final slide order agree;
- each slide has one primary relationship;
- titles communicate the page purpose or conclusion;
- prerequisites precede dependent mechanisms;
- necessary professional terms are explained at first appearance;
- every acronym carries its expansion on the slide at first use, not only a gloss and not only in the speaker notes;
- definitions are concise and do not branch into unnecessary topics;
- examples support rather than replace formal explanations;
- data, units, formulas, commands, and code match source evidence;
- conclusions state applicable conditions and limitations;
- speaker notes match the visible slide when notes are requested.

## Structural QA

Use the companion `pptx-operator` skill's package validator and media audit. When the active environment provides a stronger Office schema validator, run that as an additional check and use the original deck as the baseline for template-derived work.

Check slide count, relationships, content types, charts, media, notes, layouts, and masters. Treat any broken or unreferenced relationship as a release blocker.

## Visual QA

Render every slide. Prefer Microsoft PowerPoint for the final pass when available, particularly for Chinese typography, GIF, SVG, and animations.

Inspect:

- overflow and clipped text;
- overlaps and hidden objects;
- distorted or cropped images;
- screenshot corners protruding beyond rounded frames;
- inconsistent margins, alignment, spacing, radii, and semantic colors;
- unreadable projection sizes;
- arrows with ambiguous direction;
- diagrams too dense to explain;
- terminology annotations too far from the corresponding term;
- logo, footer, page number, and confidentiality collisions;
- font substitution and missing glyphs.

For Chinese native text, resolve fonts against the intended backend. For LibreOffice, run the PPTX font audit with `--libreoffice-safe --strict`. LibreOffice showing only the English words of a mixed-language title is a blocking font/rendering failure even when OOXML text extraction still returns the Chinese characters. If the backend exposes no CJK font, stop instead of treating a structurally valid `a:ea` declaration as sufficient.

Render changed pages at full resolution, then inspect a whole-deck contact sheet for consistency.

## Media audit

Run:

```bash
python scripts/audit_media.py deck.pptx
```

Require:

- every image, SVG, screenshot, GIF, audio, and video asset be physically stored inside the `.pptx` package;
- every raster image used inside an SVG be embedded as a validated base64 data URI rather than a local, HTTP, or relative path;
- all DrawingML picture references use `r:embed`;
- no `r:link` picture references;
- no `TargetMode="External"` media relationships;
- no HTTP/HTTPS media targets or other web-hosted assets;
- no absolute local paths such as `/Users/...`, `C:\...`, temporary directories, or workspace paths;
- no negative DrawingML transform extents; reverse connectors use normalized bounds and `flipH`/`flipV`;
- all referenced targets exist in the package;
- GIF and other media are present under the package media directory.

Do not assume a picture is embedded merely because it is visible on the original computer.

## Portability test

1. Copy the final `.pptx` to an unrelated temporary directory.
2. Open that copied file from the temporary directory.
3. Render or export all slides from the moved copy.
4. Verify images, SVG, GIF poster frames, fonts, audio/video placeholders, and slide count.
5. When animation playback matters, test it in slideshow mode on the target application.

The test must not rely on the source working directory or original asset paths.

## Delivery report

Report:

- changed slides and preserved slides;
- content or ordering decisions approved by the user;
- deliberately non-editable items such as real screenshots or embedded complex SVG;
- structure validation result;
- embedded versus linked media counts;
- moved-file test result;
- canonical output path and recovery path, if retained.
