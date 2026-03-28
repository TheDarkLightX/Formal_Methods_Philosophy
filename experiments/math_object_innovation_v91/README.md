# v91: refill maximal score-free merged-subunion boundary

## Question

`v90` found an exact score-free earliest-error law on the whole unsafe block of
the lab-followup frontier.

The next honest comparison is the refill side:

> does the hard refill frontier admit an analogous score-free law on its whole
> nontrivial score union, or at least on the largest merged score subunion in
> the current hard-frontier witness grammar?

## Method

Bounded domain:

- reuse the hard refill frontier from `v29` to `v46`
- same `130` residual-consistent viable behaviors
- nontrivial refill scores:
  - `7`
  - `8`
  - `9`
  - `10`
  - `11`
  - `12`
- same `v42` feature surface with `8` score-free features:
  - `(err[6] AND err[10] AND err[12])`
  - `err[3]`
  - `(err[9] AND err[10] AND err[12])`
  - `err[6]`
  - `err[8]`
  - `err[9]`
  - `err[10]`
  - `err[12]`

Language:

- signed conjunction atoms over those `8` features
- widths `1` through `4`

Search:

- enumerate all nonempty merged score subunions of `7,8,9,10,11,12`
- for each subunion:
  - search the smallest exact all-positive presentation
  - search the smallest exact residual-default presentation

## Main bounded result

The refill frontier does not admit a whole-block score-free law in this
grammar.

Exact feasibility counts:

- residual-default feasible merged subunions:
  - `13`
- size profile:
  - size `1`: `6`
  - size `2`: `6`
  - size `3`: `1`
- all-positive feasible merged subunions:
  - `10`
- all-positive size profile:
  - size `1`: `6`
  - size `2`: `4`

So:

- no merged score subunion of size `4`, `5`, or `6` is exact
- the full nontrivial union fails
- every exact size-`3` or larger object needs residual-default witnessing

Unique maximal exact merged subunion:

- scores:
  - `(9,10,12)`
- rows:
  - `17`
- labels:
  - `10`
- exact all-positive presentation:
  - impossible
- best exact residual-default cost:
  - `10`
- best default label:
  - `(1, 0, 1, 1)`

Best exact residual-default language on `(9,10,12)`:

- default:
  - `(1, 0, 1, 1)`
- certify `(0, 0, 0, 1)` by:
  - `err[3] and err[8]`
- certify `(0, 0, 1, 0)` by:
  - `err[3] and err[9] and not err[12]`
  - `err[6] and err[9] and not err[10]`
- certify `(0, 0, 1, 1)` by:
  - `err[3] and err[12]`
- certify `(0, 1, 0, 0)` by:
  - `err[6] and not err[9] and not err[10]`
- certify `(0, 1, 1, 0)` by:
  - `err[6] and err[10]`
- certify `(1, 0, 0, 0)` by:
  - `not err[3] and not (err[9] AND err[10] AND err[12]) and not err[6] and err[9]`
- certify `(1, 0, 0, 1)` by:
  - `err[8] and err[12]`
- certify `(1, 0, 1, 0)` by:
  - `not err[3] and (err[9] AND err[10] AND err[12]) and not err[6] and not err[8]`
- certify `(1, 1, 1, 0)` by:
  - `not err[6] and not err[9] and not err[10]`

## Why it matters

This is the clean contrast with `v90`.

The lab-followup frontier admits a whole unsafe-block score-free explanatory
law.

The refill frontier does not.

In the same style of search, refill only admits sparse exact merged islands,
and the unique maximal island is:

- non-contiguous in score
- still residual-default
- still not all-positive exact

So the refill witness-language line still needs score partitioning or richer
languages. A single merged score-free law does not explain the whole nontrivial
frontier in the current grammar.

## Status

Survivor. This is an exact maximal merged-subunion boundary for score-free
residual-default refill witnesses in the searched grammar.

## Next

- test a richer score-free certificate language on the refill frontier
- or search for the largest refill merged subunion that becomes exact under a
  small semantic grammar rather than wider conjunctions
