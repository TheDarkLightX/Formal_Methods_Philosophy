## v56, direct delta basis frontier

### Structural target

Minimize the direct symbolic feature basis needed for the exact `v55` residual
family compiler.

### Bounded domain

- Keep the same five residual patch formulas from `v49`
- Keep the same direct symbolic delta features from `v55`:
  - `has_add`
  - `has_drop`
  - `has_flip`
- Target labels:
  - `FLIP_BUNDLE`
  - `ADD_BUNDLE`
  - `ADD_BUNDLE + DROP_BUNDLE`
- Search all nonempty feature subsets
- Certificate atom grammar:
  - conjunctions of signed literals over the chosen subset

### Question

`v55` showed that the residual family split is directly compilable from the
three direct delta features.

This cycle asks whether that direct compiler still survives on a smaller exact
feature basis.

### Strongest claim

On the exact five residual patch formulas:

- the smallest exact all-positive basis has size:
  - `2`
- the smallest exact positive-cover plus residual-default basis also has size:
  - `2`
- the exact minimal bases are:
  - `has_add`, `has_drop`
  - `has_drop`, `has_flip`
- no singleton feature basis is exact

So the direct residual family compiler sharpens again. The `has_add` coordinate
is not necessary, but neither is `has_flip`. The indispensable coordinate on
this bounded residual domain is `has_drop`.

### Claim tier

- `tier = symbolic_state_compiler`
- `oracle_dependent = true`
