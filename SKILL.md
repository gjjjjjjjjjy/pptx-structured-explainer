---
name: pptx-structured-explainer
description: Design, revise, and validate professional knowledge-explanation presentations from a topic, Markdown, documents, code repositories, or existing PPT/PPTX/POTX files. Use when Codex must first understand the subject, audience, knowledge dependencies, outline, titles, template, and output format; produce a user-confirmed Markdown slide manuscript and unified SVG visual style; then create or edit a coherent, progressively explained, editable, image-rich PowerPoint with necessary first-use terminology explanations, preserved user artwork, embedded media, speaker notes when requested, and full structural, visual, and portability QA.
---

# Structured Explainer PPTX

Create presentations only after resolving the knowledge structure and obtaining the required user confirmations. Use the companion `pptx-operator` skill for all PowerPoint reading, editing, rendering, and validation operations. Use the companion `svg-diagram-engine` skill for structured, custom, or hybrid SVG diagrams and their validation. If either companion is unavailable for a task that needs it, stop before the relevant file operation and tell the user to run this repository's installer.

## Core constraints

- Explain from prerequisite concepts to mechanisms, evidence, limitations, and conclusions.
- Use professional, precise language. Avoid excessive everyday wording and extended metaphor chains.
- Use examples when they materially improve understanding; never replace the formal explanation with analogies.
- Use canonical domain terminology for slide titles, component names, process nodes, legends, and implementation labels. Do not invent metaphorical pseudo-terms such as “understanding tower”, “writer module”, “feature card”, or “parameter knob”. A short analogy may appear only as secondary explanatory text beside the standard term, and must never replace or rename the real concept.
- Do not compress a key knowledge point into a few summary sentences. For every key point, explain the problem it solves, the inputs and outputs, the internal steps, the implementation location, and a concrete verification method. Use multiple slides when one page cannot carry this chain legibly.
- Explain only professional terms necessary for the current knowledge chain. Attach the explanation at the term's first appearance, preferably inside or next to the relevant SVG/PPT element.
- At the first appearance of an abbreviation or foreign-language technical term, show its expanded or source form when applicable and a concise audience-language explanation of its role. Do not assume that a short label is self-explanatory or invent an expansion that is not canonical.
- Make visuals encode relationships: sequence, hierarchy, comparison, data flow, architecture, or evidence. Do not add decorative images merely to satisfy a visual quota.
- Explain every non-decorative visual encoding in place. State what boxes, circles, cells, colors, lines, sizes, and shaded regions represent; never leave the audience to infer a symbol's semantic meaning.
- Keep titles, ordinary text, tables, charts, shapes, and simple diagrams editable in PowerPoint. Never deliver whole-slide raster images as editable slides.
- For Chinese native text, inspect the supplied template and fonts visible to the target renderer. Keep Arial only for Latin-only runs. For LibreOffice, split mixed-script runs and assign a renderer-visible CJK font explicitly to Han runs; never rely on fallback.
- Require non-negative native transform extents. Reverse-direction connectors must use normalized bounds plus `flipH`/`flipV`; a negative connector width or height can trigger PowerPoint file repair.
- Embed every SVG, image, screenshot, audio, video, and GIF inside the `.pptx` package. Never use linked-media relationships, local file paths, or web URLs as media sources in the delivered deck; the presentation must remain complete after being copied to another computer.
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
6. Present the SVG drawing-mode choices, record the user's selection, then produce one representative SVG style sample and confirm the unified visual language.
7. Batch-generate all SVG diagrams and provide a thumbnail overview for review.
8. Build the editable PowerPoint, render it, validate it, and perform portability QA.

Do not skip directly to PPT generation unless the user explicitly asks to bypass a confirmation gate.

### Existing presentation

1. Read and render the actual PPT with the `pptx-operator` skill.
2. Inventory slides, editable text, pictures, GIFs, notes, layouts, masters, media relationships, and existing visual conventions.
3. Reconstruct the visible teaching/explanation chain: what the audience knows before each slide, what the slide adds, and what later slides depend on.
4. Report gaps, abrupt terminology, repetition, ordering problems, and pages that are whole-slide pictures.
5. Confirm the exact change boundary: unchanged, text-only edit, terminology annotation, redrawn diagram, new slide, reordered slide, or deletion.
6. Create one sample when the requested edit changes the visual system. Obtain approval before batch edits.
7. Modify only the confirmed scope. Preserve all other slide XML, assets, notes, and user-created diagrams.
8. Run content, structure, visual, media-embedding, and moved-file tests before overwriting the source.

Read [references/existing-deck-workflow.md](references/existing-deck-workflow.md) before editing an existing deck.

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

## Explain key mechanisms through implementation

For each key knowledge point, build a visible explanation chain:

```text
concrete input or failure case
→ purpose of the mechanism
→ internal steps and state changes
→ mathematical or algorithmic calculation
→ code execution path
→ observable output and verification
```

Do not stop at a metaphor, definition, or one-sentence conclusion. A beginner-oriented deck may reduce notation density, but it must still show how the result is produced.

- For mathematical mechanisms, draw a calculation flow with actual small values. Label every intermediate value, operation, dimension when necessary, and final result; then map each step to the formal expression.
- For code mechanisms, show an execution flowchart using real repository filenames, functions, important inputs/outputs, branches, loops, and state updates. Keep the essential code or pseudocode editable beside the flow.
- For model structures, draw a concrete architecture pictogram: components, nesting, data direction, repeated blocks, inputs/outputs, and the role of each connection. Do not substitute a row of generic cards for the architecture.
- For each implementation page, include a verification cue such as expected shape, example output, metric trend, assertion, test name, or stopping condition.
- When a mechanism exists because of an upstream condition or constraint, show that trigger before the mechanism. Use a concrete before/after example when useful, and explain what changes or fails if the mechanism is omitted.

Read [references/content-and-language.md](references/content-and-language.md) for the required depth test and [references/svg-and-layout.md](references/svg-and-layout.md) for calculation, code-flow, and model-structure visuals.

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

Use `pptx-operator/scripts/font_policy.py --template template.pptx --renderer <target>` to resolve title/body Chinese fonts against fonts actually visible to the target renderer. If no reliable Chinese font is visible, stop before building the deck and request renderer font configuration instead of silently using Arial. A bundled LibreOffice runtime may not see the host system font library.

If no template is supplied, confirm a minimal choice set: ratio, visual character, light/dark tendency, brand or preferred colors, content density, logo/footer, compatibility target, and output formats. Default to editable `.pptx`, 16:9, and PDF only as a review artifact unless the user states otherwise.

Do not design SVGs before the final template size and content-safe area are known.

Read [references/template-and-format.md](references/template-and-format.md) for the full checklist and reporting format.

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

Choose the SVG production mode before drawing the representative sample:

- **Structured mode** for weaker models, repeated diagrams, or predictable flow/tree/comparison/timeline/matrix layouts. The model emits constrained JSON and `svg-diagram-engine` calculates coordinates, wrapping, connectors, and theme styles.
- **Custom mode** for mechanism diagrams whose topology, visual hierarchy, or visual polish cannot be expressed by a standard layout. A capable model authors static SVG directly under the same validation rules.
- **Hybrid mode** for a deterministic structured base with a small custom explanatory overlay. Preserve the generated geometry and keep enhancement local.

Present these three modes to the user as an explicit choice. Also offer **Mixed by diagram（逐图选择）** for decks that combine routine diagrams with complex mechanisms. Recommend one option based on the confirmed manuscript, but let the user override it. Only choose without a reply when the user has explicitly delegated visual decisions; in that case, state the chosen mode before creating the representative sample.

Do not ask a weak model to improvise hundreds of raw coordinates. Do not force a strong model into generic cards when a custom mechanism diagram would explain the content more accurately.

Create one representative SVG page that demonstrates:

- title and type hierarchy;
- node, card, arrow, connector, and annotation styles;
- necessary term + adjacent explanation;
- highlight and conclusion treatment;
- template logo/footer/safe-area behavior;
- code, data, or screenshot integration if relevant.

After the user approves this single style sample, batch-generate all SVG diagrams consistently. Do not require page-by-page approval. Provide a complete thumbnail/contact sheet for one overall review.

Use SVG for complex diagrams and visual review, not as an excuse to flatten the whole presentation. In the final PPT, keep normal text and simple shapes native; embed SVG only for complex vector relationships whose editability tradeoff is acceptable.

Read [references/svg-and-layout.md](references/svg-and-layout.md) and the installed `svg-diagram-engine` instructions before creating the style sample or final diagrams. Validate every SVG and render it to PNG for visual review before inserting it into PowerPoint.

## Explain necessary terminology in place

At first appearance, show the professional term together with a short explanation. When the term is an abbreviation, the expansion is part of the explanation, not an optional extra:

```text
<TERM>
<short explanation of what it is and its role here>
```

```text
<ACRONYM> (<Expanded Form>)
<short explanation of what it is and its role here>
```

Never show a bare acronym with only a translated gloss. A gloss tells the audience what the term measures or does; the expansion tells them what the letters stand for. Without the expansion they cannot connect the label to the literature, API parameter, CLI flag, or log field they will meet later. Write the expansion once, at first use, then use the short form freely.

Use one line or one concise sentence. Explain what it is and its role in the current visual. Do not expand into adjacent topics unless the audience cannot understand the page without them.

Explain a term only if all relevant conditions hold:

1. It is necessary to the current page's core relationship.
2. It is new to the intended audience or first appears here.
3. Not understanding it would block the next reasoning step.

Prefer a subtitle inside the SVG node or a small adjacent annotation. Avoid detached glossary bars that make viewers search for the corresponding element.

## Build editable PowerPoint

- Use native text boxes for titles, prose, labels, code, captions, and term explanations.
- Choose native-text fonts from the template, operating system, and target renderer. For LibreOffice, split mixed Chinese/Latin text into runs; set the CJK font in both `a:latin` and `a:ea` on Han runs, and keep Arial only on Latin-only runs.
- Use native shapes and connectors for simple processes, cards, comparisons, and annotations.
- Use native tables and charts whenever PowerPoint supports the required form.
- Use embedded SVG for complex vector diagrams and embedded images only for real screenshots, photographs, complex backgrounds, or animations.
- Package every visual asset under the PPTX media parts. A picture that merely renders from an external or local link does not satisfy delivery requirements.
- Preserve image aspect ratio. Keep rectangular screenshots inset within rounded containers rather than allowing corners to protrude.
- Keep code in editable monospaced text unless the request explicitly requires a real terminal screenshot.
- Preserve notes and create speaker notes when requested; never put hidden script text on the slide.
- Use the existing template master rather than recreating master logos or footers on every slide.

## Validate and deliver

Run all checks in [references/qa-and-portability.md](references/qa-and-portability.md). At minimum:

1. Verify content, knowledge order, titles, terminology, examples, data, and code.
2. Run the PPTX structural validator with the original file as baseline for template-derived decks.
3. Render with Microsoft PowerPoint when available; inspect every slide for overflow, overlap, cropping, spacing, and font substitution.
4. For Chinese decks targeting LibreOffice, first run `font_policy.py --renderer libreoffice`, then run `audit_pptx_fonts.py deck.pptx --libreoffice-safe --strict`; an unsplit mixed run or Arial-only Han run is a release failure.
5. Audit media: all visual media must use embedded relationships; reject external targets and absolute local paths.
6. Copy the presentation to an unrelated temporary directory, open it there, and render again.
7. Work on a copy. Do not overwrite the user's source until the user approves the reviewed version.
8. Keep one intentional recovery copy, not a trail of ambiguous “final-v2-final” files.

Use the bundled scripts:

```bash
python scripts/inventory_pptx.py deck.pptx
python scripts/audit_media.py deck.pptx
```

Report what changed, what remained untouched, which elements are intentionally non-editable, validation evidence, and the final file path.
