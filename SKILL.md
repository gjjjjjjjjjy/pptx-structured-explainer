---
name: pptx-structured-explainer
description: Design, revise, and validate professional knowledge-explanation presentations from a topic, Markdown, documents, code repositories, or existing PPT/PPTX/POTX files. Use when Codex must first understand the subject, audience, knowledge dependencies, outline, titles, template, and output format; produce a user-confirmed Markdown slide manuscript and unified SVG visual style; then create or edit a coherent, progressively explained, editable, image-rich PowerPoint with necessary first-use terminology explanations, preserved user artwork, embedded media, speaker notes when requested, and full structural, visual, and portability QA.
---

# Structured Explainer PPTX

Create presentations only after resolving the knowledge structure and obtaining the required user confirmations. Prefer a capable PPT/PPTX skill supplied by the current agent environment. If none exists, use this skill's bundled self-contained operation layer for inspection, editable creation, exact text replacement, rendering, media audit, and visual review. Read [references/pptx-operations.md](references/pptx-operations.md) before operating on PPTX files and [references/toolchain.md](references/toolchain.md) before choosing a renderer.

## Core constraints

- Explain from prerequisite concepts to mechanisms, evidence, limitations, and conclusions.
- Use professional, precise language. Avoid excessive everyday wording and extended metaphor chains.
- Use examples when they materially improve understanding; never replace the formal explanation with analogies.
- Explain only professional terms necessary for the current knowledge chain. Attach the explanation at the term's first appearance, preferably inside or next to the relevant SVG/PPT element.
- Make visuals encode relationships: sequence, hierarchy, comparison, data flow, architecture, or evidence. Do not add decorative images merely to satisfy a visual quota.
- Keep titles, ordinary text, tables, charts, shapes, and simple diagrams editable in PowerPoint. Never deliver whole-slide raster images as editable slides.
- Embed all SVG, images, screenshots, audio, video, and GIF media. Never retain local file links.
- Preserve a user's confirmed diagrams, template, brand elements, notes, animations, and unaffected slides unless the user explicitly authorizes replacement.
- Do not expose hidden chain-of-thought. Present only the concise knowledge structure, dependencies, rationale, and decisions needed for user review.

## Select the workflow

### New presentation

Follow all confirmation gates in order:

1. Confirm purpose, audience, prior knowledge, duration, setting, required evidence/examples, and desired outcome.
2. Propose and confirm the outline and core knowledge points.
3. Confirm the PPT template, slide ratio, branding, editability, compatibility, notes/animation needs, and delivery formats.
4. Propose and confirm the slide titles.
5. Draft and confirm the complete Markdown slide manuscript.
6. Produce one representative SVG style sample and confirm the unified visual language.
7. Batch-generate all SVG diagrams and provide a thumbnail overview for review.
8. Build the editable PowerPoint, render it, validate it, and perform portability QA.

Do not skip directly to PPT generation unless the user explicitly asks to bypass a confirmation gate.

### Existing presentation

1. Read and render the actual PPT with the best available PPT toolchain.
2. Compare extracted native text/object inventory with the rendered pages. Treat mismatches as renderer uncertainty, not source defects.
3. Inventory slides, editable text, pictures, GIFs, notes, layouts, masters, media relationships, and existing visual conventions.
4. Reconstruct the visible teaching/explanation chain: what the audience knows before each slide, what the slide adds, and what later slides depend on.
5. Report confirmed gaps, abrupt terminology, repetition, ordering problems, and pages that are whole-slide pictures. Label renderer-dependent observations separately.
6. Confirm the exact change boundary: unchanged, text-only edit, terminology annotation, redrawn diagram, new slide, reordered slide, or deletion.
7. Create one sample when the requested edit changes the visual system. Obtain approval before batch edits.
8. Modify only the confirmed scope. Preserve all other slide XML, assets, notes, and user-created diagrams.
9. Run content, structure, visual, media-embedding, and moved-file tests before overwriting the source.

Read [references/existing-deck-workflow.md](references/existing-deck-workflow.md) before editing an existing deck.
Read [references/toolchain.md](references/toolchain.md) before choosing tools or running bundled scripts.
Read [references/pptx-operations.md](references/pptx-operations.md) when the environment does not provide another PPT/PPTX skill or when using the bundled public scripts.

## Build the knowledge chain

Before writing slide titles, derive a concise visible structure such as:

```text
problem and goal
→ necessary concepts
→ components or architecture
→ operating process
→ key mechanism
→ observable metrics or evidence
→ example / experiment
→ limitations and conclusion
```

Adapt the sequence to the domain. Enforce these common dependencies:

- concept before mechanism;
- structure before code;
- metric definition before result table;
- control variables before experiment result;
- correctness before performance;
- observed result before causal interpretation;
- conclusion together with applicable conditions and limitations.

Ask the user to confirm the outline and major knowledge points. Then convert the confirmed outline into meaningful slide titles. Prefer question, mechanism, comparison, task, or conclusion titles; avoid vague titles such as “Introduction,” “Other,” or “Related content.”

Read [references/content-and-language.md](references/content-and-language.md) when designing the outline, titles, terminology, examples, or prose.

## Confirm the template and delivery format

Ask whether the user provides a `.pptx` or `.potx` template. If so, inspect:

- dimensions and ratio;
- masters and available layouts;
- title/body placeholders and safe content area;
- fonts and theme colors;
- cover, section, content, and closing layouts;
- logo, page number, footer, confidentiality, and brand elements;
- external media or font dependencies.

Summarize the findings and confirm which elements are immutable.

If no template is supplied, confirm a minimal choice set: ratio, visual character, light/dark tendency, brand or preferred colors, content density, logo/footer, compatibility target, and output formats. Default to editable `.pptx`, 16:9, and PDF only as a review artifact unless the user states otherwise.

Do not design SVGs before the final template size and content-safe area are known.

Read [references/template-and-format.md](references/template-and-format.md) for the full checklist, Windows-compatible font policy, fallback rules, and reporting format.

## Draft the Markdown manuscript

Create the entire content manuscript before drawing final slides. Use this block per slide:

```markdown
## Slide N: [meaningful title]

### Objective
[What the audience should understand after this slide]

### Content
[Concise professional explanation]

### Key conclusion
[One sentence]

### Required terminology
- Term: explanation tied to this slide

### Visual specification
[Relationship to draw, direction, labels, and evidence]

### Evidence / example / code
[Only when necessary]

### Speaker notes
[Optional]
```

Exclude “Required terminology” when there is no new necessary term. Do not add glossary content merely because a word is technical.

Obtain user approval of the Markdown manuscript before visual production.

## Confirm one SVG style, then batch-generate

Create one representative SVG page that demonstrates:

- title and type hierarchy;
- node, card, arrow, connector, and annotation styles;
- necessary term + adjacent explanation;
- highlight and conclusion treatment;
- template logo/footer/safe-area behavior;
- code, data, or screenshot integration if relevant.

After the user approves this single style sample, batch-generate all SVG diagrams consistently. Do not require page-by-page approval. Provide a complete thumbnail/contact sheet for one overall review.

Use SVG for complex diagrams and visual review, not as an excuse to flatten the whole presentation. In the final PPT, keep normal text and simple shapes native; embed SVG only for complex vector relationships whose editability tradeoff is acceptable.

Read [references/svg-and-layout.md](references/svg-and-layout.md) before creating the style sample or final diagrams.

## Explain necessary terminology in place

At first appearance, show the professional term together with a short explanation, for example:

```text
TTFT
首 Token 延迟：从提交 Prompt 到生成第一个 Token 的耗时
```

Use one line or one concise sentence. Explain what it is and its role in the current visual. Do not expand into adjacent topics unless the audience cannot understand the page without them.

Explain a term only if all relevant conditions hold:

1. It is necessary to the current page's core relationship.
2. It is new to the intended audience or first appears here.
3. Not understanding it would block the next reasoning step.

Prefer a subtitle inside the SVG node or a small adjacent annotation. Avoid detached glossary bars that make viewers search for the corresponding element.

## Build editable PowerPoint

- Use native text boxes for titles, prose, labels, code, captions, and term explanations.
- Use native shapes and connectors for simple processes, cards, comparisons, and annotations.
- Use native tables and charts whenever PowerPoint supports the required form.
- Use embedded SVG for complex vector diagrams and embedded images only for real screenshots, photographs, complex backgrounds, or animations.
- Preserve image aspect ratio. Keep rectangular screenshots inset within rounded containers rather than allowing corners to protrude.
- Keep code in editable monospaced text unless the request explicitly requires a real terminal screenshot.
- Preserve notes and create speaker notes when requested; never put hidden script text on the slide.
- Use the existing template master rather than recreating master logos or footers on every slide.

## Validate and deliver

Run all checks in [references/qa-and-portability.md](references/qa-and-portability.md). At minimum:

1. Verify content, knowledge order, titles, terminology, examples, data, and code.
2. Run the strongest structural validator available, using the original file as baseline for template-derived decks when supported.
3. Render with Microsoft PowerPoint when available; otherwise render with LibreOffice. Inspect every slide for overflow, overlap, cropping, spacing, and font substitution.
4. Audit media: all visual media must use embedded relationships; reject external targets and absolute local paths.
5. Copy the presentation to an unrelated temporary directory, open it there, and render again.
6. Work on a copy. Do not overwrite the user's source until the user approves the reviewed version.
7. Keep one intentional recovery copy, not a trail of ambiguous “final-v2-final” files.

Use the bundled scripts:

```bash
python scripts/check_environment.py
python scripts/inventory_pptx.py deck.pptx
python scripts/audit_media.py deck.pptx
python scripts/render_pptx.py deck.pptx --output-dir rendered
python scripts/make_contact_sheet.py rendered --output contact-sheet.png
```

For creation and conservative text editing:

```bash
python scripts/create_pptx.py deck.json --output deck.pptx
python scripts/replace_text.py source.pptx replacements.json --output reviewed.pptx
```

Report what changed, what remained untouched, which elements are intentionally non-editable, validation evidence, and the final file path.
