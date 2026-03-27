## v55, direct delta-certificate frontier

### Structural target

Upgrade the `v54` certificate comparison from a relabeling result to a direct
symbolic-state compiler by deriving the certificate features from the raw patch
delta formulas themselves.

### Bounded domain

- Keep the exact five residual patch formulas from `v49`, as exposed through the
  exact `v53` explanation-fiber packaging
- Raw symbolic inputs per patch:
  - `core` conjunction
  - `patch` conjunction
- Direct delta features derived from the symbolic inputs:
  - `has_add`
  - `has_drop`
  - `has_flip`
- Target labels:
  - `FLIP_BUNDLE`
  - `ADD_BUNDLE`
  - `ADD_BUNDLE + DROP_BUNDLE`
- Certificate atom grammar:
  - conjunctions of `1` to `3` signed literals over the three direct delta
    features

### Question

`v54` showed that once the exact `v53` fibers are already known, a positive
certificate language plus a residual default class has exact cost `2`.

This cycle asks whether the same residual family split can be recovered
directly from the raw symbolic patch deltas, without taking the fiber labels as
input features.

### Strongest claim

On the exact five residual patch formulas:

- the smallest exact all-positive direct certificate language has cost:
  - `3`
- a direct positive-certificate plus residual-default language has cost:
  - `2`

The best direct residual-default language is:

- certify `ADD_BUNDLE + DROP_BUNDLE` by:
  - `has_drop`
- certify `FLIP_BUNDLE` by:
  - `has_flip`
- treat `ADD_BUNDLE` as the residual default class

So the same exact residual family split can be compiled directly from symbolic
patch-state deltas. That is stronger than `v54`, because it no longer depends
on the precomputed fiber labels as features.

### Claim tier

- `tier = symbolic_state_compiler`
- `oracle_dependent = true`
