## v49, cross-frontier core-plus-patch frontier

### Structural target

Refine the `v48` template vision into a sharper compiler shape:

- shared exact core
- frontier-specific patch sets
- and a check for whether the patches still collapse syntactically

### Bounded domain

- Source frontier A:
  - exact global witness-schema library from `v41`
- Source frontier B:
  - exact global witness-schema library from `v46`
- Use the same conjunction-shape template grammar as `v48`

### Question

`v48` showed that two exact frontiers share a much smaller template language
than their raw formula union.

This cycle asks a sharper question:

- does that cross-frontier object decompose into a large stable exact core plus a
  small patch language,
- and do the frontier-specific patches collapse any further?

### Strongest claim

The exact `v41` and `v46` witness-schema frontiers decompose into:

- shared exact core:
  - `17`
- `v41`-only patch schemas:
  - `3`
- `v46`-only patch schemas:
  - `2`

The residual patch union has size `5`, and those `5` patch formulas are already
template-irreducible in the searched conjunction-shape grammar.

So the sharper vision is now:

- the stable part of the meta-language is real,
- but the remaining novelty is not one more shared syntax trick,
- it is a small irreducible patch language.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
