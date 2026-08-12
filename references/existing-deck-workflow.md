# Existing Deck Editing Workflow

## Contents

1. Inventory
2. Reconstruct the explanation chain
3. Confirm boundaries
4. Preserve and edit safely
5. Sample-first rule
6. Recovery and overwrite

## Inventory

Use the `pptx` skill to extract and render the actual presentation. Do not rely only on user screenshots. Inventory:

- slide number and visible title;
- slide layout and master;
- native text, pictures, SVG, charts, tables, media, GIF, and notes;
- whole-slide images and text trapped in images;
- external relationships and local paths;
- repeated visual systems and semantic colors;
- user-created diagrams and pages previously confirmed by the user.

Run `scripts/inventory_pptx.py` for a first structural pass, then inspect rendered pages.

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
