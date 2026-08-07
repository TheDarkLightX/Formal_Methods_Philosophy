---
name: design-story-rule-math-metaphors
description: Design, audit, or refine story-driven visual metaphors and playable rule-games for mathematics, formal methods, proofs, algorithms, and technical tutorials. Use when an explanation should be child-simple without becoming false, when a metaphor must predict examples or scale to harder cases, or when a tutorial needs the sequence story, rules, play, prediction, formula, proof bridge, and stated limits.
---

# Design Story-Rule Math Metaphors

Build metaphors as small, falsifiable models rather than decorative comparisons. Preserve the tutorial's story voice while giving each imagined world exact rules that map back to the mathematics.

## Core standard

Use this teaching ladder:

```text
story creates meaning
  -> rules define the imagined world
  -> play builds intuition
  -> prediction tests the intuition
  -> notation compresses the rules
  -> proof explains why the result must hold
  -> a boundary states where the metaphor stops
```

Treat play as a conjecture generator, not as proof. Require the exact mathematical bridge before presenting a conclusion as established.

Do not claim a structural isomorphism unless there is a proved bijective structure-preserving map with a structure-preserving inverse. Otherwise call the construction a metaphor, analogy, representation, or partial model.

## Workflow

### 1. Extract the mathematical contract

Write the deep structure before inventing imagery:

```text
objects and their types:
allowed operations:
relations or order:
invariants:
normalization:
target output:
hypotheses:
edge and failure cases:
```

Include nouns and verbs. A metaphor that preserves the objects but changes the operation is unsafe.

### 2. Generate competing worlds

Generate at least three candidate metaphors when the choice materially affects understanding. Prefer familiar systems whose mechanisms match the mathematics. Do not restrict candidates to physical play when music, maps, recipes, games, machines, light, or bookkeeping preserve more structure.

### 3. Build the mapping ledger

For each candidate, map every important element:

| Mathematics | Story world | Required correspondence |
|---|---|---|
| object | game piece | same relevant state |
| operation | legal move | same composition rule |
| invariant | quantity that cannot change | preserved under every legal move |
| output | score or visible result | same success condition |
| hypothesis | rule of the world | stated before the prediction |

Reject a candidate if an essential row has no faithful correspondence.

### 4. Apply the STRONG gate

- **Structure:** Preserve the relevant objects, relations, and operations.
- **Translation:** Translate the picture into mathematics and back without inventing facts.
- **Reason:** Show the mechanism, not merely a resemblance.
- **Outcome:** Predict ordinary, negative, and boundary cases correctly.
- **Nonclaims:** State what the picture does not model.
- **Growth:** Extend naturally to the next important level of the lesson.

Treat Structure, Outcome, and Nonclaims as mandatory gates. Do not average away a failure in one of them with vivid storytelling.

### 5. Run the break test

Try to make the metaphor predict something false. Test:

1. one matching example;
2. one nonmatching example;
3. the smallest or degenerate case;
4. a larger-dimensional or many-object case;
5. reversal, composition, or iteration when relevant;
6. loss of information, conservation, sign, phase, order, and normalization when relevant.

Repair or replace the metaphor if its natural prediction disagrees with the mathematics.

### 6. Run the generative test

Ask a question whose answer has not yet been stated. Keep the metaphor only if its rules help derive the right prediction. Then verify the prediction mathematically.

A metaphor passes this test by generating a correct conjecture. It does not independently prove the conjecture.

### 7. Write the story-game

Use these seven beats:

1. **Scene:** Let named characters encounter a concrete problem.
2. **Invention:** Introduce the machine, room, board, or game.
3. **Rule card:** State three to five exact rules before play begins.
4. **First round:** Demonstrate one simple case.
5. **Prediction round:** Ask the reader or characters to predict a new case.
6. **Mathematical reveal:** Map the pieces and moves to notation and formulas.
7. **Boundary:** State where the imagined physics diverges from the mathematics.

Keep the story continuous with the surrounding tutorial. Avoid switching into third-person production notes or a detached glossary.

## Fourier metaphor family

Prefer a compatible family of metaphors rather than forcing one image to explain everything:

- **Indicator and counting:** Use a property scanner that emits one token for a match and zero for a nonmatch. Summing tokens exactly counts matches.
- **Finite character cancellation:** Use equal-length arrows added head to tail. Alignment gives a large vector; evenly spaced roots of unity close a polygon and sum to zero.
- **Frequency extraction:** Use a spin lock. Multiply by the reverse test rotation. A matching frequency becomes stationary and survives averaging; a mismatch keeps rotating and averages to zero over the declared complete period.
- **Fourier transform:** Use a wave recipe that records frequency, magnitude, and phase. Do not use an ingredient list that omits phase if exact reconstruction matters.
- **Convolution:** Use a glow stamp. Every source point places a shifted copy of the kernel, scaled by the source value; all copies add. An asymmetric kernel produces a directional glow.
- **Positive normalized kernel:** Use a spotlight whose brightness is nonnegative and whose total light is fixed. Concentration narrows where that fixed light falls.
- **Majorant and minorant:** Use a roof and floor only when the required pointwise inequalities hold everywhere in the stated domain.
- **Verification:** Use an inspector who checks declared rules and receipts, not an oracle who guarantees unstated properties.

## Common metaphor failures

- Do not say opposite waves destroy energy when only their represented amplitudes sum to zero.
- Do not equate opposite phase with orthogonality. Opposite copies of the same wave have a negative inner product, not zero inner product.
- Do not say every mismatched frequency averages to zero without specifying an orthogonal basis and the correct complete interval or measure.
- Do not describe Fourier coefficients as physical ingredients unless the signal model really is their linear combination. Preserve phase when reconstruction is claimed.
- Do not describe a color predicate using holes that distinguish only shape.
- Do not describe convolution as one uncontrolled physical smear. Preserve shifting, scaling, summation, and kernel orientation.
- Do not let a game rule silently become a theorem hypothesis. State it before play.
- Do not claim that a child has proved or invented a theorem merely by following an analogy.

## Output contract

For each important metaphor, produce:

```text
title
story scene
rule card
worked round
prediction round
mapping ledger
exact formula or definition
proof bridge
boundary sentence
```

For short explanations, compress the format but retain the exact mapping and boundary.

## Validation

Before finalizing tutorial content:

1. Check every formula and declared domain independently of the metaphor.
2. Verify that each story rule corresponds to an explicit mathematical hypothesis or operation.
3. Confirm that the prediction round has the stated answer, including edge cases.
4. Search for false physical claims and hidden conservation assumptions.
5. Confirm that the boundary sentence is visible near the metaphor.
6. Render the tutorial and inspect the story, rule card, formulas, diagrams, and navigation in context.
