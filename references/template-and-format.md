# Template and Output Format

## Contents

1. Required user confirmation
2. Supplied template analysis
3. No-template choices
4. Template report
5. Output formats
6. Existing presentation as template
7. Font compatibility policy

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

Use the best available PPT/PPTX toolchain to inspect and render the template. If no dedicated skill exists, use the bundled inventory and rendering scripts. Record:

- exact width, height, and ratio;
- slide masters and layouts;
- layout names and representative pages;
- placeholder type, position, and usable dimensions;
- title and body fonts and sizes;
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

## Template report

Report template findings in a compact form:

```text
Ratio: 16:9
Title font: ...
Body font: ...
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

## Font compatibility policy

Record the target platform, selected fonts, fallback fonts, and actual renderer in the template report. Never infer that a font is portable merely because it exists on the authoring machine.

For Chinese presentations targeting Windows PowerPoint:

- Prefer `Microsoft YaHei` (`微软雅黑`) for modern sans-serif body text and `Microsoft YaHei UI` only for compact UI-like labels.
- Use `DengXian` (`等线`) only when the target Windows/Office estate is known to include it.
- Use `SimSun` (`宋体`) for formal serif body text and `SimHei` (`黑体`) only when matching a legacy template.
- Prefer `Arial`, `Calibri`, or `Cambria` for Latin text; use `Cambria Math` for equations when PowerPoint-native equations are unavailable.
- For cross-platform SVG/PDF review, use `Noto Sans CJK SC` or `Source Han Sans SC` as the Chinese fallback. Do not silently write these into the PPTX when Windows PowerPoint is the delivery target unless the font will be installed or embedded there.

When preserving an existing deck, keep its confirmed theme fonts unless they cause missing glyphs, overflow, or a stated compatibility failure. Normalize fonts only inside the confirmed change boundary.

Before selecting a font:

1. Inventory the source theme and run-level fonts.
2. Check whether each selected font exists on the authoring renderer and target Windows environment.
3. Use an explicit East Asian font in generated OOXML or library calls; setting only a Latin font is insufficient for Chinese text.
4. Render a Chinese test string containing titles, punctuation, digits, Latin terms, and mathematical symbols.
5. Label missing Chinese, tofu boxes, changed line breaks, and substituted metrics as renderer or font discrepancies.

For delivery, report:

```text
Target platform: Windows PowerPoint ...
Chinese title font: ...
Chinese body font: ...
Latin font: ...
Equation font: ...
Review fallback font: ...
Font embedding: yes / no
Renderer used: ...
Known substitution risk: ...
```

Do not embed a font without confirming that its license permits document embedding. If exact typography is required and embedding is unavailable, deliver the font requirement explicitly and keep a PDF review artifact produced on the target platform.
