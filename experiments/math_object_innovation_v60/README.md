## v60, quotient boundary frontier

### Structural target

Compare the smallest exact slot quotient for direct label compilation against the
smallest exact slot quotient that also preserves the full primitive basis
structure.

### Bounded domain

- Keep the same five residual patch formulas from `v49`
- Keep the same raw primitive edit features from `v57`
- Search all ordered disjoint nonempty slot pairs over the primitive features
- Two objective regimes:
  - `label_only`
    - require exact direct label compilation
  - `basis_faithful`
    - require exact direct label compilation
    - and exact reproduction of the six primitive bases from `v57`

### Question

`v59` found the sharpest current role-slot compiler, but it was constrained to
preserve the full primitive basis family.

This cycle asks whether that structural faithfulness is expensive. In other
words, how much smaller can the exact slot quotient get if it only needs to
compile the labels?

### Strongest claim

On the exact five residual patch formulas:

- the smallest exact `label_only` slot quotient has slot cost:
  - `2`
- the smallest exact `basis_faithful` slot quotient has slot cost:
  - `5`

The `label_only` optimum is not unique. It is the family of singleton-slot
compilers formed by:

- one add-anchor singleton from:
  - `add[3]`
  - `add[6]`
  - `add[10]`
- one mixed discriminator singleton from:
  - `add[8]`
  - `drop[12]`

So there are:

- `6` unordered minimal label-only quotients
- `12` ordered minimal label-only quotients

while the smallest structure-preserving quotient is the exact `v59` slot
compiler:

- `{add[3], add[6], add[10]}`
- `{add[8], drop[12]}`

This is a real boundary. Predictive compression is cheaper than
structure-preserving compression on this bounded residual family.

### Claim tier

- `tier = symbolic_state_compiler`
- `oracle_dependent = true`
