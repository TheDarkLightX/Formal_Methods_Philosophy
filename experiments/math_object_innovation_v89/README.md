# v89: lab-followup widened-certificate saturation boundary

## Question

`v88` found the first transfer-side residual-budget law:

- on the toy lab-followup MPRD frontier,
- one merged residual-default region over all mixed score blocks
- was the exact schema-first optimum

The next question is whether that optimum is only a `1..4` certificate-grammar
artifact.

> if strict certificates widen from the `1..4` literal grammar to the full
> `1..5` literal grammar, while residual-default witnesses stay in `1..4`,
> does any rung of the `v88` ladder move?

## Method

Reuse the exact `v88` transfer frontier:

- residual-consistent unique-behavior frontier from `v26`
- mixed score blocks:
  - `1, 2, 3, 4`
- same partition-aware residual-budget search

Language split:

- residual-default witness regions stay in the `1..4` literal grammar
- strict certificate regions widen from `1..4` literals in `v88` to `1..5`
  literals here

Objective:

- minimize shared schema count
- then exact total cost

## Main bounded result

Nothing moves.

Exact widened transfer ladder:

- budget `0`:
  - shared schemas `5`
  - total cost `5`
  - partition:
    - `(1,2,3,4)`
  - residual regions:
    - none
- budget `1`:
  - shared schemas `4`
  - total cost `4`
  - partition:
    - `(1,2,3,4)`
  - residual regions:
    - `(1,2,3,4)`
- budget `2`:
  - shared schemas `4`
  - total cost `5`
  - partition:
    - `(1)`
    - `(2,3,4)`
  - residual regions:
    - both regions
- budget `3`:
  - shared schemas `4`
  - total cost `7`
  - partition:
    - `(1)`
    - `(2)`
    - `(3,4)`
  - residual regions:
    - all three regions
- budget `4`:
  - shared schemas `6`
  - total cost `10`
  - partition:
    - `(1)`
    - `(2)`
    - `(3)`
    - `(4)`
  - residual regions:
    - all four regions

Compared with `v88`:

- schema gain:
  - `0, 0, 0, 0, 0`
- cost gain:
  - `0, 0, 0, 0, 0`

## Why it matters

This closes the smallest remaining grammar question on the lab-followup
transfer object.

The merged residual region from `v88` is not merely a `1..4` strict
certificate artifact.

On this bounded frontier:

- widening strict certificates to the full `1..5` literal grammar does not
  change any residual budget
- the whole transfer ladder is already locally saturated on this literal-width
  axis

So the next honest move is not one more literal. It is:

- a richer certificate language,
- or a semantic explanation of why one merged residual region is optimal here

## Status

Survivor. This is an exact saturation boundary on the bounded lab-followup
transfer frontier.

## Next

- compare the transfer ladder against a richer certificate language
- or search for a semantic invariant explaining the merged residual region
