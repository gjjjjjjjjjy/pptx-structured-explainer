# Content and Language Rules

## Contents

1. Audience and outcome
2. Knowledge structure
3. Slide titles
4. Professional language
5. Examples and analogies
6. Terminology boundaries
7. Content density
8. Key-point depth and implementation

## Audience and outcome

Confirm the audience's role, prior knowledge, likely misconceptions, available time, and the decision or understanding expected at the end. Do not infer an advanced audience merely from a technical topic.

State the final learning or communication outcome in observable terms: explain a mechanism, compare alternatives, interpret a chart, execute a procedure, or make a decision.

## Knowledge structure

For each candidate slide, record:

- what the audience already knows;
- the one new relationship introduced;
- the evidence or visual needed;
- which later slide depends on it.

Remove or move a slide when it requires terminology or mechanisms that have not been introduced. Split a slide when it introduces more than one independent core relationship.

Prefer the following domain-neutral progression:

1. problem and scope;
2. prerequisite definitions;
3. system or component structure;
4. process and state changes;
5. mechanism and causal explanation;
6. measurement or evaluation method;
7. evidence, example, experiment, or case;
8. interpretation, boundary, and conclusion.

## Slide titles

Use titles that communicate a question, mechanism, comparison, task, or conclusion.

Good patterns:

- Why does ordinary inference repeat computation?
- How does KV Cache reuse historical K/V?
- Training and inference update different state.
- Cache benefit increases with context length.
- Run a controlled Cache / No Cache comparison.

Avoid titles that do not reveal content:

- Introduction
- Technical details
- Experimental section
- Other issues
- Related concepts

Keep a title to one line where the template permits. Do not put multiple independent claims in one title.

## Professional language

Use direct technical language and explicit relationships. Prefer “A causes B under condition C” over promotional or vague phrases.

Avoid:

- excessive conversational fillers;
- entertainment-oriented wording;
- unsupported superlatives;
- anthropomorphic descriptions that obscure mechanism;
- long metaphor chains;
- repeating the same conclusion in title, body, footer, and notes.

### Canonical terms before analogies

Use the standard name from the field, paper, specification, library, or repository as the visible primary label. This applies especially to titles, architecture components, calculation stages, code-flow nodes, legends, and assessment questions.

Do not coin presentation-specific substitute terms such as “understanding tower”, “writer”, “feature card”, “parameter knob”, or similar labels that could be mistaken for real technical concepts. Use `Encoder`, `Decoder`, `Embedding`, `trainable parameters`, `gradient`, and other canonical terms directly.

When an analogy materially helps a beginner, place it only in secondary explanatory text and map it immediately to the canonical term. Remove the analogy once the formal mechanism is introduced. Never use a metaphor as a section title, component name, or code/architecture label.

Define a mechanism formally after any simplified introduction.

## Examples and analogies

Use examples to make inputs, outputs, state transitions, or measurement calculations concrete. Keep them close to the formal explanation.

One short analogy may introduce an intuition, but immediately map it to the real entities. Never use an analogy as the only explanation. Do not continue an analogy across multiple slides unless the user explicitly wants a narrative presentation and technical accuracy remains intact.

## Terminology boundaries

Explain a term at first appearance only when it is required for the current knowledge chain. The explanation should answer:

- What is it?
- What role does it play here?
- Why is it needed in this concrete input or execution state?

For an abbreviation or foreign-language technical term, show the canonical expansion or source form when applicable and a concise explanation in the audience's language. If the label is not literally an acronym, state its source term instead of inventing an expansion.

An expansion and a gloss are two different things, and an acronym needs both at first use:

| Part | Answers | Example form |
|---|---|---|
| Expansion | What do the letters stand for? | `<ACRONYM>` → `<Expanded Form>` |
| Gloss | What is it and what does it do here? | one line in the audience's language |

Shipping only the gloss is the common failure: the audience can follow the current slide but cannot recognise the term in a paper, a CLI flag, or a metrics dashboard. Do not hide the expansion in speaker notes — notes are not visible to the audience during or after the talk. Put it on the slide at first use.

Do not expand a term that is not an acronym — product names, library names, and ordinary technical words take a gloss alone — and do not invent an expansion you cannot source.

Do not branch into every related term. A KV Cache page may require Prefill, Decode, Token, Key, and Value; it does not automatically require a survey of every positional encoding or inference scheduler.

If a term requires more than one or two sentences, give it a dedicated slide instead of an oversized annotation.

Do not repeat full definitions on every slide. Use the established term normally after first explanation, unless its meaning changes in the new context.

## Content density

Aim for one primary relationship per slide. Use a second relationship only when it directly supports the first.

When a page is dense, apply this order:

1. remove duplication;
2. move detailed explanation to speaker notes;
3. convert prose to an appropriate relationship diagram;
4. split the page;
5. reduce font size only as a last resort.

Do not use a diagram when a short paragraph or table communicates the idea more clearly.

## Key-point depth and implementation

Classify a point as key when later slides, code execution, interpretation, or the final learning outcome depends on it. A key point is not complete until the audience can answer all six questions:

1. What concrete problem does it solve?
2. What are its inputs and outputs?
3. What happens internally, step by step?
4. Where does the mathematical or algorithmic result come from?
5. Where and in what order is it implemented in code?
6. How can the learner tell that the implementation is correct?

Use a short intuition only as the entry layer. Follow it with the real entities, operations, and implementation. If the complete chain does not fit legibly, split it into “intuition”, “mechanism/calculation”, and “code/verification” slides instead of deleting the mechanism.

For a mathematical point, use a small worked example before general notation. Show the operand values, operation, intermediate values, normalization or activation, final output, and how these correspond to the formula. Avoid presenting a formula without showing how data flows through it.

For a mechanism introduced to handle a specific condition, show the condition with a representative input or state, then show the transformation and its effect on downstream processing. Do not introduce a corrective mechanism without first showing the condition it corrects.

For a code point, name the actual file and function. Show call order, loops and branches, important state changes, input/output objects, and an observable check. Do not merely list filenames or paste an unexplained code block.

For a model point, show both the outer data flow and the internal repeated unit. Label which component reads which state, which path is residual or cross-component, and which output is consumed next. A conceptual metaphor must be explicitly mapped to the model component it represents.
