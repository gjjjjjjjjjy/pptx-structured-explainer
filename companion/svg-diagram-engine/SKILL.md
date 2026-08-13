---
name: svg-diagram-engine
description: Design, generate, validate, render, and review professional SVG diagrams for presentations and technical explanations. Use for flowcharts, task trees, architecture, data flow, timelines, comparisons, matrices, model structures, Attention/Mask calculations, code paths, or any diagram that must remain sharp and portable. Support deterministic structured JSON for weaker models and custom or hybrid SVG art direction for stronger multimodal models.
---

# SVG Diagram Engine

Generate diagrams through one of three user-selectable modes, then apply the same validation and preview pipeline.

## Select the mode

Before drawing, present the following choices to the user and ask which mode to use. Recommend one mode in one sentence, but do not silently lock the user into it:

1. **Structured（稳定模式）** — constrained JSON plus deterministic layout; best for routine flowcharts, task trees, timelines, comparisons, matrices, weak models, and large batches.
2. **Hybrid（混合模式）** — deterministic base layout plus a bounded custom SVG mechanism layer; best when stable geometry and one knowledge-specific visual must coexist.
3. **Custom（精绘模式）** — directly authored SVG with full composition control; best for model mechanisms, mathematical processes, architecture, and high-polish representative pages.

Also allow **Mixed by diagram（逐图选择）**, meaning each diagram in one deck may use a different mode. Recommend this for a deck containing both routine and mechanism-heavy pages. If the user has explicitly delegated visual decisions, select modes using the rules below and report the selection before generating the representative sample.

When a visual explanation would help the choice, show or render `assets/examples/drawing-mode-selector.svg`. Use this concise choice prompt:

```text
请选择绘图模式：
A. Structured（稳定模式）
B. Hybrid（稳定底图 + 局部精绘）
C. Custom（完整精绘）
D. 逐图选择（推荐用于完整 PPT）
```

### Structured mode

Use for weaker models, routine diagrams, or repeated batches. Emit a small JSON specification rather than raw SVG coordinates. Let `scripts/diagram_render.py` calculate layout, text wrapping, node sizes, connectors, and theme styles.

Supported structured templates:

- `task-tree`
- `flow`
- `comparison`
- `timeline`
- `matrix`

Read [references/structured-spec.md](references/structured-spec.md) before authoring JSON.

### Custom mode

Use when a capable model must explain a mechanism visually, such as a causal Mask, Attention calculation, tensor shape change, KV Cache lifecycle, or layered model architecture. Write the SVG directly, using gradients, masks, clip paths, curves, repeated cells, semantic highlighting, and detailed annotations when they improve understanding.

Read [references/custom-mode.md](references/custom-mode.md) before producing custom SVG.

### Hybrid mode

Use structured mode to establish the main layout, then add a custom SVG layer for mechanism-specific detail. Preserve stable typography, spacing, and connectors from the structured base. Do not replace a clear standard diagram with decorative freeform artwork.

## Required workflow

1. Identify the relationship: sequence, hierarchy, comparison, matrix, architecture, state transition, or calculation.
2. Confirm canvas dimensions, safe area, template colors, and target language.
3. Present `structured`, `hybrid`, `custom`, and mixed-by-diagram choices; record the user's selection or explicit delegation.
4. Generate the source JSON or SVG.
5. Run `scripts/svg_validate.py`.
6. Render a PNG with `scripts/svg_render.py`.
7. Inspect the full-resolution preview for clipping, overlap, line routing, text size, terminology, and visual semantics.
8. Revise the source, not the PNG.
9. Preserve both the source SVG and preview PNG.
10. Hand the validated SVG to `pptx-operator` for embedding in the PowerPoint package.

## Structured quick start

```bash
python scripts/diagram_render.py input.json output.svg
python scripts/svg_validate.py output.svg
python scripts/svg_render.py output.svg output.png
```

Use `assets/examples/task-tree.json` as a minimal example.

Rendering is browser-free. `auto` tries `resvg`, `rsvg-convert`, Sharp, then CairoSVG. Use `--backend sharp` or another explicit backend when reproducible backend selection matters.

## Custom quick start

Create the SVG with a complete `viewBox` and an explicit background, then run:

```bash
python scripts/svg_validate.py custom.svg --strict
python scripts/svg_render.py custom.svg custom.png --scale 2
```

## Content and visual rules

- Make the diagram explain one primary relationship.
- Use canonical technical terms as visible labels.
- Explain necessary new terms at first appearance, adjacent to the corresponding element.
- Give every color, line, shaded region, cell state, and connector a clear semantic role.
- Keep body text at least 18 px on a 1600×900 canvas unless the user approves a denser technical plate.
- Use paths and decorative effects only when they clarify structure or focus.
- Avoid `script`, `foreignObject`, external images, web fonts, and linked resources. If an SVG must contain a raster image, embed PNG/JPEG/WebP bytes as a validated base64 `data:image/...` URI; never use a local path, HTTP URL, or ordinary relative file reference.
- Use an explicit fallback font stack containing common Chinese and Latin fonts.
- When a PPT template is available, obtain the renderer-visible Chinese title/body font from `pptx-operator/scripts/font_policy.py --renderer <target>` and put that font first in the SVG font stack. Do not use Arial as the primary family for Chinese SVG text.
- Keep critical labels as PowerPoint-native text later when frequent editing is required.
- Never flatten a whole slide into SVG merely to simplify implementation.

## Weak-model reliability

Require a weak model to emit only supported JSON fields. Reject coordinates and raw SVG in structured mode. If validation fails, repair the JSON or choose a simpler template; do not ask the weak model to patch arbitrary XML.

## Strong-model freedom

Allow a capable model to compose full SVG in custom mode. It may use gradients, clipping, masks, patterns, Bézier paths, matrices, nested groups, and visual callouts. Still require deterministic validation, rendered inspection, and PowerPoint compatibility. Artistic freedom never bypasses content accuracy or QA.

## Delivery

Report:

- selected mode and template;
- whether the mode was chosen by the user or selected under delegated authority;
- SVG and PNG preview paths;
- canvas dimensions;
- validation result and rendering backend;
- any external assets or fonts, which should normally be none;
- whether the SVG will remain a single vector object or be redrawn with native PowerPoint elements.
