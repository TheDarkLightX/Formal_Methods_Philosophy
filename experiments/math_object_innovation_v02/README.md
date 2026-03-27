# Math Object Innovation v02

## Structural target

Obligation-targeted witness routing.

The v01 cycle found a strong bounded policy:

- proposer chooses the surviving candidate with maximal singleton closure
- verifier chooses the failing obligation with maximal closure gain

This cycle asks whether that coupled `x,y` policy can be compressed into a single obligation-space controller plus a witness router.

## Core idea

At state `C`, define the uncovered obligations:

- `U(C) := Y \\ Psi(C)`

and the witness set for an uncovered obligation `y`:

- `W(C,y) := { x in C | not Spec(x,y) }`

Then define the route key:

- `RouteKey(y | C) := min_{x in W(C,y)} (-|Psi({x})|, x)`

and the target key:

- `TargetKey(y | C) := (RouteKey(y | C), -DeltaPsi(y | C), |C ∩ Phi({y})|, y)`

where:

- `DeltaPsi(y | C) := |Psi(C ∩ Phi({y}))| - |Psi(C)|`

The controller chooses the `y` with minimal `TargetKey`.

After that, the router chooses the witness `x` realizing `RouteKey(y | C)`.

## Why this matters

If the factorization is exact, then:

- the formal side can optimize over obligation space directly
- the existential engine only needs to synthesize a witness for a chosen obligation

That is a different neuro-symbolic role split than standard CEGIS.

## Bounded domain

- exhaustive `4x4` boolean relations
- random `5x5` holdout

## Files

- `run_cycle.py`: exact factorization and bounded optimality checks
- `test_cycle.py`: focused equivalence and regression checks
- `generated/report.json`: replayed metrics and strongest claim

## Claim discipline

This cycle does not claim a literature-level theorem or a general algorithmic breakthrough.

It aims to establish a bounded, replayable result:

- the coupled closure policy compresses into a pure obligation controller plus a witness router,
- and the routed policy keeps the exact `4x4` step-optimality result from the coupled formulation while exposing a separate check-optimality gap against the unrestricted obligation-only optimum.
