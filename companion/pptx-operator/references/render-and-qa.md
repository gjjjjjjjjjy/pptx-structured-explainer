# Rendering and QA

## Contents

1. Rendering backends
2. Structural checks
3. Visual checks
4. Portability

## Rendering backends

Use Microsoft PowerPoint for the final review when the deck depends on PowerPoint-specific fonts, animation, GIF timing, SVG behavior, audio, or video. On macOS the bundled renderer prefers Microsoft PowerPoint; otherwise it can automate LibreOffice-based PDF and PNG generation. LibreOffice output is a useful automated preview but may differ from PowerPoint.

Record the backend used. Do not claim PowerPoint-equivalent playback when only a static LibreOffice render was tested.

## Structural checks

Verify:

- the file is a readable ZIP package;
- `[Content_Types].xml` and the presentation part exist;
- internal relationship targets resolve to package parts;
- every slide referenced by the presentation exists;
- no linked image or external non-hyperlink media remains;
- no absolute local path is embedded in XML or relationships.

## Visual checks

Inspect every slide for clipped text, overlap, alignment, margins, image distortion, protruding screenshot corners, font substitution, missing glyphs, ambiguous arrow direction, weak contrast, unreadable projection size, and unexplained visual encodings.

Inspect changed slides individually at full resolution and inspect a contact sheet for whole-deck consistency.

## Portability

Copy the final deck to an unrelated temporary directory and render that copy. The output must not depend on the source working directory or original asset paths. Test animation and media playback in slideshow mode when those features are part of the deliverable.
