## v50, typed semantic-patch frontier

### Structural target

Test whether the irreducible residual patches from `v49` still compress in a
typed edit language once patch formulas are allowed to attach to any shared-core
formula, not only their nearest one.

### Bounded domain

- Shared exact core from `v49`:
  - `17` formulas
- Frontier-specific residual patches from `v49`:
  - `5` formulas
- Typed edit language over conjunction literals:
  - `ADD_POS_ATOM`
  - `ADD_NEG_ATOM`
  - `DROP_POS_ATOM`
  - `DROP_NEG_ATOM`
  - `ADD_POS_ANDk`
  - `DROP_NEG_ANDk`
  - and the analogous typed variants by sign and feature kind

### Question

`v49` showed that the residual patch formulas are irreducible in the searched
syntax-only template grammar.

This cycle asks a sharper question:

- if each patch may attach to any exact shared-core formula,
- and patches are described by typed literal edits,
- does a smaller shared edit-signature vocabulary appear?

### Strongest claim

In the searched typed edit model:

- nearest-core attachment yields:
  - `5` patch signatures for `5` patches
- allowing non-nearest core attachment yields:
  - `4` typed edit signatures for those same `5` patches

So the residual language is not fully irreducible once the compiler is allowed
to use typed edit semantics over the shared core.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
