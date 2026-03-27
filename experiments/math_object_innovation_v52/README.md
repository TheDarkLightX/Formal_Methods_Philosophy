## v52, bundle semantic-macro frontier

### Structural target

Strengthen the semantic macro-family result from `v51` by allowing bundled
semantic macros instead of counting one macro instance per edited literal.

### Bounded domain

- Shared exact core from `v49`:
  - `17` formulas
- Residual patch formulas from `v49`:
  - `5`
- Candidate bundle-macro families:
  - `ADD_BUNDLE`
  - `DROP_BUNDLE`
  - `FLIP_BUNDLE`

### Question

`v51` showed that the residual patch line collapses to an exact two-family
semantic basis:

- `ADD_LITERAL`
- `FLIP_SIGN`

with best total macro-instance count `11`.

This cycle asks whether bundling same-family edits into one semantic macro
instance yields a sharper basis.

### Strongest claim

In the searched bundle-macro model:

- the exact family subset is:
  - `ADD_BUNDLE`
  - `FLIP_BUNDLE`
- no exact one-family solution exists
- best total macro-instance count drops:
  - from `11`
  - to `6`

So the semantic patch line does not only survive. It sharpens into a smaller
exact bundled macro basis.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
