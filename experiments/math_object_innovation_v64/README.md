## v64, support-literal compiler frontier

### Structural target

Upgrade the `v63` support-signature transfer result from a descriptive role law
to a small exact compiler family.

### Bounded domains

Domain A, cross-frontier schema roles from `v49`:

- roles:
  - `CORE`
  - `V41_PATCH`
  - `V46_PATCH`
- support bits:
  - `has_v41`
  - `has_v46`

Domain B, residual primitive roles from `v62`:

- roles:
  - `ADD_ANCHOR`
  - `MIX_DISCRIM`
  - `OTHER`
- support bits:
  - `has_AB`
  - `has_MIX`

Domain C, direct patch-delta roles from `v55`:

- roles:
  - `ADD_BUNDLE`
  - `ADD_BUNDLE+DROP_BUNDLE`
  - `FLIP_BUNDLE`
- support bits:
  - `has_add`
  - `has_drop`
  - `has_flip`

### Question

`v63` showed that two exact frontiers admit support-signature role laws.

This cycle asks a sharper question:

- do several exact frontiers admit exact residual-default compilers using only
  single support literals,
- and is that compiler size minimal on each frontier?

### Strongest claim

All three bounded domains admit exact residual-default support compilers with:

- branch count:
  - `2`
- total literal cost:
  - `2`

Preferred exact compilers:

- Domain A:
  - certify `V41_PATCH` by `not has_v46`
  - certify `V46_PATCH` by `not has_v41`
  - default `CORE`
- Domain B:
  - certify `ADD_ANCHOR` by `has_AB`
  - certify `OTHER` by `not has_MIX`
  - default `MIX_DISCRIM`
- Domain C:
  - certify `ADD_BUNDLE+DROP_BUNDLE` by `has_drop`
  - certify `FLIP_BUNDLE` by `has_flip`
  - default `ADD_BUNDLE`

No exact single-branch support compiler exists on any of the three domains.

So the support-signature line now upgrades from:

- a transferred descriptive role law

to:

- a tiny exact support-literal compiler family across three bounded frontiers.

For Domain A, this simplification is scoped to the bounded frontier, because the
`00` support signature does not occur there.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
