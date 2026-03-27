## v36, primitive-invention label frontier

### Structural target

Test the first bounded primitive-invention loop on the repaired verifier
frontier.

### Bounded domain

- Same repaired verifier quotient as `v24` and `v25`
- Same `10` reachable quotient states over `(H6, E)`
- Same `4` exact labels:
  - `safe`
  - `fail_13116`
  - `fail_1915`
  - `fail_828`

### Question

The `v35` result showed:

- all-positive exact label language cost `7`
- best mixed-sign exact language cost `4`

This cycle asks whether the all-positive language can be improved by inventing
new exact label-pure primitives, built as bounded unions of existing pure atoms.

### Primitive model

A candidate invented primitive is allowed if:

- it is a union of `2` or `3` existing pure guards of the same label
- it remains exact on the bounded frontier, meaning it covers only states of
  that label
- it is genuinely new, not a duplicate of an existing pure atom

### Strongest claim

On the repaired verifier frontier:

- one invented primitive lowers the all-positive exact language cost from `7`
  to `5`
- the best one-primitive invention is a new `fail_828` primitive:
  - `E = True OR H6 = 858 OR H6 = 864`
- two invented primitives lower the all-positive exact language cost from `7`
  to `4`, exactly matching the best mixed-sign language from `v35`
- the best two invented primitives are:
  - new `fail_1915` primitive:
    - `H6 = 859 and E = False OR H6 = 865`
  - new `fail_828` primitive:
    - `E = True OR H6 = 858 OR H6 = 864`

So concept invention can eliminate the mixed-sign advantage on this bounded
frontier.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`

