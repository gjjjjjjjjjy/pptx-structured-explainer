# SVG and Layout Workflow

## Contents

1. Representative style sample
2. SVG semantic rules
3. Terminology in diagrams
4. Batch generation
5. Final PowerPoint conversion
6. Layout and screenshot rules
7. Optional generated architecture illustrations

## Representative style sample

Choose a content-rich representative page containing most of these elements:

- title and one primary conclusion;
- process, architecture, or comparison relationship;
- professional terms with adjacent explanations;
- one highlight or evidence element;
- template logo/footer boundaries;
- code, data, or screenshot integration if applicable.

The sample must establish:

- background and palette;
- title, body, label, and annotation hierarchy;
- node and card families;
- arrows, connectors, branches, and loops;
- semantic color mapping;
- border, radius, spacing, and safe margins;
- screenshot and code treatment;
- terminology explanation style.

Obtain approval of this one unified style. Do not request page-by-page SVG approval afterward.

## SVG semantic rules

Select the visual form from the relationship:

| Relationship | Preferred visual |
|---|---|
| execution order | process flow |
| state over time | timeline |
| two alternatives | side-by-side comparison |
| system components | architecture diagram |
| hierarchy | tree or nested structure |
| repeated parameter combinations | matrix or table |
| performance evidence | native chart and numeric callouts |
| experiment procedure | step cards plus real evidence screenshot |
| code interaction | editable code plus call chain |
| input/output | data-flow diagram |

Every arrow must have an unambiguous source, destination, and meaning. Use labels for transformations or state changes when the relation is not obvious.

Use the same color for the same semantic entity across the deck. Do not assign colors merely to make adjacent cards different.

## Terminology in diagrams

Place the term and concise explanation together:

```text
Prefill
一次处理完整输入并建立历史状态
```

```text
D4
模型深度为 4，包含 4 个 Transformer Block
```

Use a subtitle, small adjacent annotation, or node description. Avoid a detached glossary that forces cross-referencing.

Explain only necessary first-use terms. Keep the explanation to one line or one sentence. If it needs more room, create a dedicated concept page.

## Batch generation

After sample approval:

1. lock dimensions and safe area;
2. lock typography and semantic colors;
3. define reusable SVG node and connector components;
4. generate all diagrams;
5. render a contact sheet with slide numbers;
6. conduct one whole-deck review for density, consistency, and ordering;
7. revise the SVG sources rather than patching raster previews.

## Final PowerPoint conversion

Treat SVG as complex vector artwork and visual specification, not a whole-slide screenshot.

Keep these native in PowerPoint:

- title and ordinary prose;
- terminology labels when practical;
- simple cards, arrows, and connectors;
- tables and supported charts;
- code and command text;
- captions and conclusions.

Embed SVG for complex diagrams when the user accepts that internal SVG text is not edited like a normal PowerPoint text box. Never rasterize a diagram that can remain vector.

## Layout and screenshot rules

- Preserve image aspect ratio.
- Crop only irrelevant margins; retain commands, parameters, headers, and evidence.
- Keep a rectangular screenshot inset inside a rounded frame. Do not let its square corners protrude past the rounded boundary.
- Use a true screenshot only for real terminal output, monitoring, application UI, photographs, or evidence.
- Put explanations, labels, metrics, and conclusions around the screenshot as native PowerPoint elements.
- Do not paste image patches over existing text. Edit or redraw the underlying PowerPoint element.
- Split pages instead of shrinking important text below readable projection size.

## Optional generated architecture illustrations

When the user explicitly requests a refined non-SVG architecture diagram, concept illustration, cinematic system visual, or presentation artwork, use an available image-generation tool instead of forcing the result into SVG or basic PowerPoint shapes.

Use generated raster artwork only when it materially improves one of these outcomes:

- spatial depth or a polished hero architecture visual;
- a complex conceptual relationship that would look crude as simple cards;
- consistent high-quality illustration across section covers or selected focal pages;
- a visual metaphor that supplements, but does not replace, the formal explanation.

Before generation, specify exact slide ratio, safe area, palette, viewing direction, component hierarchy, required empty regions, and whether the image must avoid embedded text. Prefer text-free or minimally labeled artwork, then place titles, node labels, formulas, metrics, and conclusions as native PowerPoint text and shapes.

For architecture diagrams, verify every generated component and connector against the confirmed knowledge structure. Do not accept plausible-looking invented modules, reversed arrows, unreadable pseudo-text, unsupported claims, or decorative connections. Redraw critical data-flow arrows and labels natively when semantic precision matters.

Embed the final PNG or other supported raster asset at sufficient resolution for the target slide size. Preserve aspect ratio and keep one editable source prompt or generation specification with the working files. Report which elements are intentionally rasterized and therefore not directly editable.

Do not use generated artwork for real experimental evidence, terminal output, charts, tables, code, citations, or screenshots. These must remain faithful to actual source data or execution evidence.
