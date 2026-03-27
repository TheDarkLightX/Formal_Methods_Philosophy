## v53, semantic fiber decomposition frontier

### Structural target

Move from one global semantic macro basis to a true explanation-fiber search on
the residual patch language.

### Bounded domain

- Residual patch formulas from `v49`:
  - `5`
- Candidate bundled macro families:
  - `ADD_BUNDLE`
  - `DROP_BUNDLE`
  - `FLIP_BUNDLE`
- Search all `52` set partitions of the five residual patches
- For each fiber:
  - search the smallest exact family subset, allowing each patch to attach to
    any shared-core formula

### Question

`v52` gave the strongest global bundled semantic basis:

- exact family subset:
  - `ADD_BUNDLE`
  - `FLIP_BUNDLE`
- best total macro-instance count:
  - `6`

This cycle asks whether the residual patch language admits a cleaner
explanation-fiber decomposition than one global basis.

### Strongest claim

The five residual patches admit an exact explanation-fiber decomposition with:

- mixed patches:
  - `1`
- mixed fibers:
  - `1`
- total fibers:
  - `3`

The best exact decomposition is:

- one pure `FLIP_BUNDLE` fiber covering `3` patches
- one pure `ADD_BUNDLE` fiber covering `1` patch
- one mixed `ADD_BUNDLE + DROP_BUNDLE` singleton fiber covering the remaining
  patch

So the residual semantic language is almost fiber-pure. Only one patch remains
mixed under the searched bundled macro language.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
