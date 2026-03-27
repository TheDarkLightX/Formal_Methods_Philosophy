## v62, shared role semantics frontier

### Structural target

Unify the `v59` structure-preserving slot roles and the `v60` minimal
label-only quotient family under one exact semantic partition.

### Bounded domain

- Keep the same primitive edit features from the five residual patch formulas
- Keep the exact `v59` basis-faithful slot roles:
  - `slot_a`
  - `slot_b`
  - `other`
- Keep the exact `v60` minimal `label_only` quotient family
- Primitive metadata features:
  - `has_AB`
  - `has_MIX`

### Question

`v61` showed that the `v59` slot roles admit a two-feature support-profile
explanation.

This cycle asks whether that same semantic explanation also controls the
minimal `label_only` quotients from `v60`, so that both exact objectives are
governed by one shared role law.

### Strongest claim

On the same primitive edit features:

- define the support-profile partition by:
  - `ADD_ANCHOR` iff `has_AB`
  - `MIX_DISCRIM` iff `not has_AB and has_MIX`
  - `OTHER` iff `not has_MIX`
- this partition exactly matches the `v59` structure-preserving slot roles:
  - `ADD_ANCHOR = slot_a`
  - `MIX_DISCRIM = slot_b`
  - `OTHER = other`
- the exact minimal `label_only` quotients from `v60` are exactly the singleton
  cross product:
  - choose one primitive from `ADD_ANCHOR`
  - choose one primitive from `MIX_DISCRIM`

So the same two-feature support-profile law controls both:

- the smallest exact structure-preserving quotient
- the family of smallest exact predictive quotients

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
