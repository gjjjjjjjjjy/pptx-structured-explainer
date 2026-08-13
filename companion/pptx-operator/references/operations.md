# PowerPoint Operations

## Contents

1. Creation
2. Existing-deck editing
3. Text and formatting
4. Images and SVG
5. Charts and tables
6. Notes and media
7. OOXML fallback

## Creation

Set the presentation dimensions and theme before placing content. Define reusable functions for titles, body text, captions, connectors, cards, tables, and semantic colors. Use a consistent safe area and measure every element against the actual slide dimensions.

Prefer native objects:

- text boxes for titles, prose, code, labels, and terminology;
- shapes and connectors for simple diagrams;
- tables and charts for supported data displays;
- embedded SVG only for complex vector relationships;
- bitmap images only for screenshots, photographs, textures, or animation frames.

Native connector geometry must use non-negative `cx` and `cy` extents. When the end point lies left of or above the start point, normalize the bounding box and encode direction with `flipH` and/or `flipV`. Never write a negative connector width or height; PowerPoint may classify it as out of bounds and launch file repair.

## Existing-deck editing

Render and inventory the source first. Establish the exact slide and element boundary before modifying anything. Work on a copy and keep one recovery copy.

Use `python-pptx` for edits it can preserve reliably. Use targeted OOXML work when the deck contains unsupported or preservation-sensitive content such as complex groups, animations, some SVG/EMF assets, embedded objects, or advanced chart features.

## Text and formatting

Preserve paragraph and run formatting. Replace only the relevant run text when possible. Replacing a complete text frame can collapse multiple runs and remove emphasis, fonts, spacing, bullets, and language metadata.

Use real list paragraphs instead of literal bullet characters. Keep code in an editable monospaced text box. Leave sufficient width for font substitution and verify line wrapping after rendering.

For Chinese native text, inspect the template font scheme and fonts visible to the target renderer before generation. On Windows, query both machine/user font registration and the Windows font directories; resolve localized family aliases such as `微软雅黑`/`Microsoft YaHei`, `等线`/`DengXian`, and `宋体`/`SimSun`. For PowerPoint, set Latin and East Asian typefaces separately. For LibreOffice compatibility, split mixed-script text: Latin-only runs may use Arial, while Han runs must carry the chosen CJK font in both `a:latin` and `a:ea` plus `lang="zh-CN"`. Do not depend on font fallback or assume that a bundled renderer can see every system font.

## Images and SVG

Embed all visual media in the package. Maintain the source aspect ratio. Crop only when the removed region is irrelevant. Do not cover an old element with a picture patch; edit or redraw the underlying object.

SVG is suitable for complex vector artwork but its internal text is not equivalent to a native PowerPoint text box. Keep labels native when users need to edit them frequently.

## Charts and tables

Use native charts and tables whenever possible. Preserve data labels, units, axes, legends, and source notes. Do not convert a supported native chart into a screenshot merely for visual consistency.

## Notes and media

Store speaker scripts in notes rather than hidden slide objects. Preserve existing notes and animations. Confirm that GIF, audio, and video parts are embedded and test playback in the target presentation application when playback matters.

## OOXML fallback

A PPTX is an OPC ZIP package. When editing XML directly, preserve:

- `[Content_Types].xml` registrations;
- presentation-to-slide order;
- slide, layout, master, notes, chart, and media relationships;
- unique relationship identifiers;
- XML namespaces and extension lists.

After rebuilding, run the package validator and render the output. A ZIP that opens with a generic library is not necessarily accepted by PowerPoint.
