## v59, role-slot compiler frontier

### Structural target

Upgrade the `v58` role template from a descriptive basis grammar to a direct
symbolic compiler over slot features.

### Bounded domain

- Keep the same five residual patch formulas from `v49`
- Keep the raw primitive edit features from `v57`
- Search all ordered disjoint nonempty slot pairs `(A, B)` over the primitive
  features
- Require both:
  - the pair-product `A x B` matches the exact `v57` all-positive basis family
  - the induced slot booleans
    - `slot_a := any(feature in A)`
    - `slot_b := any(feature in B)`
    admit an exact label compiler

### Question

`v58` showed that the six primitive bases collapse to one exact two-slot
template, unique up to slot swap.

This cycle asks whether those slots are only a descriptive grammar over bases,
or whether they also compile the residual labels directly.

### Claim tier

- `tier = symbolic_state_compiler`
- `oracle_dependent = true`
