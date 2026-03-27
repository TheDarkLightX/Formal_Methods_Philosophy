## v51, semantic macro-family frontier

### Structural target

Strengthen the semantic-patch line from `v50` by asking for the smallest exact
semantic macro-family subset, not just the smallest typed edit-signature
vocabulary.

### Bounded domain

- Shared exact core from `v49`:
  - `17` formulas
- Residual patch formulas from `v49`:
  - `5`
- Candidate semantic macro families:
  - `ADD_LITERAL`
  - `DROP_LITERAL`
  - `FLIP_SIGN`

### Question

`v50` showed that typed edit semantics reopen compression on the residual patch
language:

- from `5` nearest-core signatures
- to `4` typed edit signatures

This cycle asks a stronger question:

- what is the smallest semantic macro-family subset that scripts all five patch
  formulas exactly?

### Strongest claim

In the searched semantic macro-family model:

- the five residual patch formulas are exactly scriptable using only:
  - `ADD_LITERAL`
  - `FLIP_SIGN`
- no exact one-family solution exists

The best exact scripts use:

- family count `2`
- total macro-instance count `11`

So the sharper semantic result is not only “typed patches exist”. It is:

- the residual patch language collapses to a two-family semantic macro basis.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
