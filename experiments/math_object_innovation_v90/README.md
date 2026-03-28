# v90: lab-followup unsafe earliest-error residual law

## Question

`v88` and `v89` showed that the toy lab-followup transfer frontier prefers one
merged residual-default region over all mixed score blocks, and that this
object is already locally saturated on the current literal-width axis.

The next question is explanatory:

> is there a score-free symbolic law on the whole unsafe block that explains
> why one merged residual region is optimal?

## Method

Bounded domain:

- reuse the residual-consistent unique-behavior frontier from `v26`
- restrict to the full unsafe block:
  - holdout scores `0,1,2,3,4`
- keep the original holdout order:
  - `h1 = (0,0,1)`
  - `h2 = (0,1,0)`
  - `h3 = (0,1,1)`
  - `h4 = (1,1,0)`
  - `h5 = (1,1,1)`
- define error bits:
  - `e_i(x) := 1` iff the controller errs on holdout state `h_i`

Language:

- signed conjunctions over `e1` to `e5`
- widths `1` through `4`

Search:

- exact all-positive witness languages on the unsafe block
- exact residual-default witness languages on the unsafe block
- direct check of the hand-coded score-free earliest-error presentation

## Main bounded result

The whole unsafe block admits an exact score-free earliest-error residual law.

Exact hand-coded residual-default language:

- default:
  - `h1`
- certify `h2` by:
  - `not e1 and e2`
- certify `h3` by:
  - `not e1 and not e2 and e3`
- certify `h4` by:
  - `not e1 and not e2 and not e3 and e4`
- certify `h5` by:
  - `not e1 and not e2 and not e3 and not e4`

Exact bounded metrics:

- unsafe behavior count:
  - `163`
- label counts:
  - `h1`: `101`
  - `h2`: `40`
  - `h3`: `14`
  - `h4`: `6`
  - `h5`: `2`
- smallest exact all-positive cost:
  - `5`
- smallest exact residual-default cost:
  - `4`
- cost-minimal residual default labels in the searched grammar:
  - `h1`
  - `h2`
  - `h3`
  - `h4`
  - `h5`

So the merged residual-default presentation saves exactly one formula and one
schema over the best exact all-positive presentation, and it does so without
using score at all. The `h1` default is the natural earliest-error
presentation, not the only cost-minimal residual default in the searched
grammar.

## Why it matters

This explains the `v88` transfer object semantically.

The merged residual region is not arbitrary. On the bounded unsafe block, the
first-refuter label is already organized by a score-free earliest-error law.

That is why:

- one merged residual region is enough
- score partitioning does not improve schema count
- widening strict certificates did not move the object in `v89`

So the lab-followup transfer frontier now has a direct explanatory law rather
than only an empirical residual-budget optimum.

## Status

Survivor. This is an exact score-free residual-default law on the bounded
unsafe block of the lab-followup frontier.

## Next

- compare this explanatory law against a richer certificate language
- or search for an analogous score-free law on the refill frontier
