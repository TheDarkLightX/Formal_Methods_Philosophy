# Math Object Innovation v01

## Structural target

Counterexample scheduling in Galoisized CEGIS.

The earlier loop work showed:

- plain CEGIS, Concept-Lattice CEGIS, and BOC-max share the same candidate trajectory under the same scheduler,
- the real leverage is on the obligation side.

This cycle asks a narrower question:

> once the loop state is represented as a current candidate set `C`, can the verifier choose counterexamples in a structurally better way than an arbitrary failing obligation?

## Bounded domain

The discovery domain is finite boolean relations:

- `Spec : X × Y -> {0,1}`
- exhaustive domains:
  - `|X| = 3, |Y| = 3`
  - `|X| = 3, |Y| = 4`
  - `|X| = 4, |Y| = 4`
- random holdout domains:
  - `|X| = 5, |Y| = 5`
  - `|X| = 6, |Y| = 6`

The proposer is fixed to:

- choose the smallest surviving candidate index

The verifier may choose among currently failing uncovered obligations.

## Schedulers compared

- `smallest`: choose the smallest failing obligation
- `cut`: minimize next candidate count
- `closure`: maximize next closure gain, then minimize next candidate count
- `live`: minimize next live burden `|C'| + |U'|`, then smaller uncovered set
- `optimal`: bounded dynamic-programming optimum on the finite domain

## Main question

Does the closure-aware scheduler recover bounded optimal verifier play, or at least a large fraction of it?

## Files

- `run_cycle.py`: exhaustive and random scheduler analysis
- `test_cycle.py`: focused regression checks
- `generated/report.json`: replayed metrics and strongest claim

## Claim discipline

This cycle does not claim a literature-level theorem or a general algorithmic breakthrough.

It aims to establish a bounded, replayable result:

- a closure-aware counterexample scheduler appears to be the real leverage point inside the Galoisized loop family,
- and its strength can be measured exactly against bounded optimum on finite domains.
