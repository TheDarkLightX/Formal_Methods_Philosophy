## v61, semantic slot frontier

### Structural target

Explain the `v59` slot roles semantically, using the smallest exact metadata
language over primitive edit features.

### Bounded domain

- Keep the primitive edit features from the same five residual patch formulas
- Keep the exact `v59` role assignment:
  - `slot_a`
  - `slot_b`
  - `other`
- Primitive metadata features:
  - kind flags:
    - `is_add`
    - `is_drop`
    - `is_flip`
  - residual label-support flags:
    - `has_AB`
    - `has_MIX`
    - `has_FLIP`
  - primitive frequency flags:
    - `count_1`
    - `count_2`
- Search all nonempty metadata-feature subsets
- Certificate atom grammar:
  - conjunctions of signed literals over the chosen subset

### Question

`v60` separated the smallest predictive quotient from the smallest
structure-preserving quotient.

This cycle asks whether the structure-preserving slot roles themselves admit a
small exact semantic explanation.

### Strongest claim

On the exact primitive-role dataset induced by `v59`:

- the smallest exact all-positive semantic basis has size:
  - `2`
- the smallest exact positive-cover plus residual-default semantic basis also
  has size:
  - `2`

One natural exact support-profile explanation is:

- feature basis:
  - `has_AB`
  - `has_MIX`
- all-positive role language:
  - `slot_a` by `has_AB`
  - `slot_b` by `not has_AB and has_MIX`
  - `other` by `not has_MIX`
- residual-default role language:
  - `slot_a` by `has_AB`
  - `slot_b` by `not has_AB and has_MIX`
  - default `other`

So the recurring slots are not only structural. They admit an exact semantic
explanation in a two-feature support-profile language.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
