# Existing Deck Editing Workflow

## Contents

1. Inventory
2. Establish render reliability
3. Reconstruct the explanation chain
4. Check teaching and experiment closure
5. Confirm boundaries
6. Preserve and edit safely
7. Sample-first rule
8. Recovery and overwrite

## Inventory

Use the best PPT/PPTX capability supplied by the current environment. When no dedicated skill exists, use `python-pptx` for inventory and LibreOffice for rendering as described in `toolchain.md`. Do not rely only on user screenshots. Inventory:

- slide number and visible title;
- slide layout and master;
- native text, pictures, SVG, charts, tables, media, GIF, and notes;
- whole-slide images and text trapped in images;
- external relationships and local paths;
- repeated visual systems and semantic colors;
- user-created diagrams and pages previously confirmed by the user.

Run `scripts/inventory_pptx.py` for a first structural pass, then inspect rendered pages.

## Establish render reliability

Never infer that source content is missing merely because a fallback render looks empty, truncated, or garbled. First compare three evidence surfaces:

1. native text and object extraction from the PPTX package;
2. a full-resolution render from the available renderer;
3. the user's screenshot or a Microsoft PowerPoint render when exact Office fidelity matters.

Classify each observation:

- **confirmed source issue**: extraction and a reliable render agree;
- **renderer discrepancy**: extraction contains content that the render omits, substitutes, or misplaces;
- **unverified visual issue**: only a fallback renderer shows the problem;
- **content-structure issue**: numbering, duplicated notes, terminology order, or factual wording is evident from native text and does not depend on visual rendering.

When a discrepancy exists, change renderer, inspect the deck in Microsoft PowerPoint, or ask the user for a screenshot of the affected page. Do not describe an apparently empty card, table, diagram, or page as unfinished until verified. State which renderer produced every visual review.

## Reconstruct the explanation chain

For each slide, answer visibly in the review report:

- What prerequisite does it assume?
- What new relationship does it explain?
- What evidence or example supports it?
- Which next slide uses its conclusion?

Flag:

- terms appearing before explanation;
- code preceding architecture or process;
- metrics used before definition;
- result tables preceding controlled variables;
- repeated pages;
- abrupt transitions;
- conclusions without evidence or limitations.

Propose reordering, merging, or splitting, but do not apply those structural changes before user confirmation.

Also compare visible slide content with speaker notes. Flag notes copied from another slide, notes that explain a different mechanism, and claims in notes that are absent from the page. Do not treat repeated notes as intentional without checking their subjects.

## Check teaching and experiment closure

For instructional decks, verify that the learner can move through this executable chain:

```text
concept → concrete example → formal mechanism → code location → command → observable output → completion criterion
```

Do not require every slide to contain every stage. Require the complete lesson or experiment section to provide the chain. Flag an experiment page when it lists filenames or tools but omits the working directory, command, expected output, success criterion, or deliverable.

Check duration against scope. Distinguish material that must be explained in class from optional derivations, appendix content, and post-class reading. A technically correct derivation can still be misplaced when it consumes time needed for the lesson's stated hands-on outcome.

## Confirm boundaries

Create a change map:

| Slide | Action | Preserved elements | Proposed changes |
|---|---|---|---|
| 1 | unchanged | all | none |
| 5 | terminology annotation | existing diagram | add first-use explanations |
| 8 | redraw diagram | title, template | replace unreadable diagram after approval |
| 10 | new slide | template | add controlled experiment workflow |

Use explicit actions: unchanged, text-only, terminology annotation, diagram redraw, new, reorder, delete, or merge.

## Preserve and edit safely

- Work on a copy.
- Modify only confirmed slides and elements.
- Preserve user-created diagrams unless replacement is explicit.
- Preserve notes, animations, GIF timing, master relationships, and unaffected slide XML.
- Do not replace an entire slide just to change one label.
- Do not copy an entire legacy media directory into a new deck; duplicate filenames can silently replace newer screenshots.
- Give imported media unique relationship targets when combining packages.
- Use native PowerPoint elements for new text and simple graphics.

## Sample-first rule

If a change introduces a new visual system or redraws an existing diagram, create one sample. Show the rendered sample and state exactly what remains editable. Continue batch edits only after approval.

Small literal corrections that preserve the visual system do not require a style sample.

## Recovery and overwrite

Maintain one named recovery copy. Avoid ambiguous sequences such as `final`, `final2`, and `final-final`.

Before overwriting:

1. show a contact sheet or changed-slide renders;
2. report the exact changed and unchanged pages;
3. validate structure and portability;
4. request user approval when required by the environment or task.

After overwriting, report the canonical file path and keep the recovery copy outside the user's delivery folder unless requested.
