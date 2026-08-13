# Custom and Hybrid SVG

## Contents

1. Use cases
2. Compatibility subset
3. Art direction
4. Mechanism diagrams
5. Validation

## Use cases

Choose custom mode for diagrams whose teaching value depends on a specific visual mechanism rather than generic topology:

- causal and padding masks;
- Attention score calculation;
- tensor dimensions and reshaping;
- KV Cache write/read lifecycle;
- layered Transformer blocks;
- code execution with loops and state;
- performance timelines with measured regions.

Choose hybrid mode when automatic layout can establish the main components but a custom overlay is needed for repeated cells, focus regions, curved paths, or formula mapping.

## Compatibility subset

Use static SVG 1.1-compatible features. Prefer:

- `g`, `rect`, `circle`, `ellipse`, `line`, `polyline`, `polygon`, `path`, and `text`;
- gradients, clip paths, masks, markers, and simple filters;
- inline styles and local `defs`.

Avoid scripts, animation, external CSS, `foreignObject`, external images, web fonts, and URLs outside local fragment references such as `url(#gradient)`.

## Art direction

Establish a visual hierarchy:

1. primary process or calculation;
2. highlighted mechanism;
3. adjacent explanation;
4. legend and boundary condition.

Use semantic color consistently. A future position blocked by a causal mask should use the same color everywhere. A cached state should retain one color from write through reuse. Do not use different colors merely to decorate neighboring nodes.

## Mechanism diagrams

For a Mask diagram, show actual token positions, the matrix, visible and blocked cells, the operation that consumes the matrix, and the consequence for the current token. For KV Cache, show Prefill creation, per-layer K/V state, Decode read, current-token append, and the next iteration.

Use small concrete values before general formulas. Explain all visual encodings directly on the page.

## Validation

Run strict validation. Then render at 2× scale and inspect:

- text clipping and wrapping;
- cell and connector alignment;
- contrast and font size;
- whether the visual sequence matches the explanation sequence;
- whether all external resources are absent;
- whether PowerPoint still renders the SVG after embedding.
