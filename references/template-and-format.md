# Template and Output Format

## Contents

1. Required user confirmation
2. Supplied template analysis
3. No-template choices
4. Template report
5. Output formats
6. Existing presentation as template

## Required user confirmation

Before producing the Markdown manuscript or SVG style, confirm:

- supplied `.pptx` or `.potx` template, if any;
- slide ratio or custom dimensions;
- mandatory cover, agenda, section, and closing layouts;
- logo, header, footer, page number, confidentiality, and brand requirements;
- fonts, theme colors, and corporate or institutional design rules;
- target Office version and platform;
- editable-content requirement;
- speaker notes, transitions, animations, GIF, audio, or video requirements;
- required deliverables: `.pptx`, PDF, SVG review files, or other formats.

## Supplied template analysis

Use the companion `pptx-operator` skill to inspect and render the template. Record:

- exact width, height, and ratio;
- slide masters and layouts;
- layout names and representative pages;
- placeholder type, position, and usable dimensions;
- title and body fonts and sizes;
- major/minor East Asian theme fonts, `Hans` supplemental fonts, and whether each candidate is visible to the target renderer;
- theme and accent colors;
- fixed master elements;
- content-safe region after fixed elements;
- external image, font, audio, or video dependencies;
- example or placeholder content that must be removed.

Do not duplicate master logos, footers, or page numbers on normal slides.

## No-template choices

Offer a concise choice, not an open-ended design interview:

- ratio: default 16:9;
- character: technical, business, academic, formal, minimal, or user-specified;
- background: light content pages, dark content pages, or dark cover/light body;
- color: supplied brand colors or a proposed palette;
- density: presentation-led or information-complete;
- logo/footer/section needs;
- compatibility target;
- notes and animation needs.

Create one representative style sample after these choices are confirmed.

For a Chinese deck with no supplied template, default Chinese and Latin title/body text to `Source Han Sans SC` when it is visible to the target renderer. Use `Source Han Serif SC` only when the user confirms a serif/Song-style visual direction. Retain a template or fallback font only when authoritative terms permit commercial use and redistribution; otherwise replace it and report the change before production.

## Template report

Report template findings in a compact form:

```text
Ratio: 16:9
Title font: ...
Body font: ...
Target renderer: PowerPoint / LibreOffice / other
Title Chinese font: ... (template/system, renderer-visible: yes/no)
Body Chinese font: ... (template/system, renderer-visible: yes/no)
Fixed elements: logo, footer, page number, confidentiality label
Available layouts: cover, section, single-column, two-column, closing
Safe content area: ...
Recommended use: full-width layout for architecture and complex process diagrams
Immutable elements confirmed: ...
```

## Output formats

Confirm:

```text
Primary file: editable .pptx
Review file: PDF
Visual approval files: SVG or PNG contact sheet
Speaker notes: yes / no
Animations and GIF: yes / no
Older Office compatibility: yes / no
Font embedding: yes / no
```

Default to editable `.pptx`. Treat PDF as a review or distribution artifact, not a substitute for PowerPoint.

## Existing presentation as template

Treat an existing deck as both content and template. Confirm whether to:

- preserve the current visual system exactly;
- alter master or theme colors;
- add new slides using a named existing layout;
- preserve user-created diagrams exactly;
- match new SVGs to the existing illustration style;
- normalize legacy fonts and spacing.

Default to preserving masters, branding, confirmed diagrams, notes, and unaffected slides.

For Chinese decks, do not report Arial as the Chinese font. Record Latin and East Asian fonts separately, identify the target rendering backend, and select only fonts that are both visible to that backend and verified for commercial use and redistribution. When targeting LibreOffice, split mixed-script text and require the chosen approved CJK font in both `a:latin` and `a:ea` on Han runs.
