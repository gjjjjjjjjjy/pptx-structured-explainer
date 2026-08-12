# Content and Language Rules

## Contents

1. Audience and outcome
2. Knowledge structure
3. Slide titles
4. Professional language
5. Examples and analogies
6. Terminology boundaries
7. Content density

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

Define a mechanism formally after any simplified introduction.

## Examples and analogies

Use examples to make inputs, outputs, state transitions, or measurement calculations concrete. Keep them close to the formal explanation.

One short analogy may introduce an intuition, but immediately map it to the real entities. Never use an analogy as the only explanation. Do not continue an analogy across multiple slides unless the user explicitly wants a narrative presentation and technical accuracy remains intact.

## Terminology boundaries

Explain a term at first appearance only when it is required for the current knowledge chain. The explanation should answer:

- What is it?
- What role does it play here?

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
