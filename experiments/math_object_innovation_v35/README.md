## v35, mixed-sign label language frontier

### Structural target

Test a first bounded dual-language idea on the repaired verifier frontier from
`v24` and `v25`.

### Bounded domain

- Same repaired verifier quotient as `v24`
- Same `10` reachable quotient states over `(H6, E)`
- Same `4` exact labels:
  - `safe`
  - `fail_13116`
  - `fail_1915`
  - `fail_828`

### Question

The verifier-compiler result from `v24` gave a minimal exact 4-guard decision
list.

This cycle asks a different question:

- if each label is explained by existential positive certificates,
- what is the smallest all-positive language?
- and if one label is allowed to be the default residual class,
- what is the smallest mixed-sign language?

This is the first bounded probe of the dual-language idea:

- some labels may be cheaper to explain positively
- another label may be cheaper to explain negatively, as the residual default

### Strongest claim

In the repaired verifier frontier:

- the smallest all-positive exact certificate cover uses `7` pure guards:
  - `safe`: `1`
  - `fail_13116`: `1`
  - `fail_1915`: `2`
  - `fail_828`: `3`
- the smallest mixed-sign exact language uses only `4` guards by proving:
  - `safe` positively with `H6 > 869`
  - `fail_13116` positively with `H6 = 869`
  - `fail_1915` positively with:
    - `H6 = 859 and E = False`
    - `H6 = 865`
  - and leaving `fail_828` as the default residual class

So the best exact explanation is not purely positive.
It is mixed-sign.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`

