# Rendering and QA

## Contents

1. Rendering backends
2. Structural checks
3. Visual checks
4. Portability

## Rendering backends

Use Microsoft PowerPoint for the final review when the deck depends on PowerPoint-specific fonts, animation, GIF timing, SVG behavior, audio, or video. On macOS the bundled renderer prefers Microsoft PowerPoint; otherwise it can automate LibreOffice-based PDF and PNG generation. LibreOffice output is a useful automated preview but may differ from PowerPoint.

Record the backend used. Do not claim PowerPoint-equivalent playback when only a static LibreOffice render was tested.

LibreOffice does not reliably supply Chinese glyph fallback for native text declared only as Arial or another Latin font. Before LibreOffice rendering, resolve fonts with `font_policy.py --renderer libreoffice`, split mixed-script runs, and require `audit_pptx_fonts.py --libreoffice-safe --strict` to pass. A title that retains English words but loses Chinese text is a font/rendering failure, not a text-extraction failure. A privately bundled LibreOffice may expose only its bundled fonts; if it has no CJK font, stop and install/configure a renderer-visible CJK font or use PowerPoint.

## Structural checks

Verify:

- the file is a readable ZIP package;
- `[Content_Types].xml` and the presentation part exist;
- internal relationship targets resolve to package parts;
- every slide referenced by the presentation exists;
- no linked image or external non-hyperlink media remains;
- packaged SVG files contain no local, HTTP, or relative image reference; raster content inside SVG uses a validated base64 data URI;
- no absolute local path is embedded in XML or relationships.
- every Han run has the renderer-visible CJK font in both `a:latin` and `a:ea`, and mixed Han/Latin text is split into separate runs when LibreOffice compatibility is required.
- all DrawingML transform extents are non-negative; reverse-direction connectors use `flipH`/`flipV` rather than negative `cx` or `cy`.

## Visual checks

Inspect every slide for clipped text, overlap, alignment, margins, image distortion, protruding screenshot corners, font substitution, missing glyphs, ambiguous arrow direction, weak contrast, unreadable projection size, and unexplained visual encodings.

Inspect changed slides individually at full resolution and inspect a contact sheet for whole-deck consistency.

## Portability

Copy the final deck to an unrelated temporary directory and render that copy. The output must not depend on the source working directory or original asset paths. Test animation and media playback in slideshow mode when those features are part of the deliverable.
