## v65, three-signature support law frontier

### Structural target

Test whether the `v64` support-literal compiler family is only a three-domain
 coincidence, or whether it reflects a generic law of small support tables.

### Bounded domain

Abstract support-table family:

- labeled `3`-role support tables
- one realized support signature per role
- all three signatures distinct
- support widths:
  - exhaustive: `2` through `7`

Concrete instantiations:

- Domain A from `v64`
- Domain B from `v64`
- Domain C from `v64`

### Question

`v64` showed that three exact bounded frontiers admit exact residual-default
 support compilers with two single-literal branches.

This cycle asks a sharper question:

- is that a generic law of every bounded `3`-role support table with distinct
  signatures,
- and can the law be witnessed by a small geometric object rather than only by
  running compiler search case by case?

### Strongest claim

Every labeled `3`-role support table with distinct realized signatures in widths
 `2` through `7` admits:

- an exact residual-default compiler with:
  - `2` branches
  - `2` single literals total
- a `private-literal star` witness:
  - choose one role as default
  - each non-default role has a private support literal that is true on that
    role and false on the default and the other non-default role

Exact bounded counts:

- width `2`:
  - `24 / 24`
- width `3`:
  - `336 / 336`
- width `4`:
  - `3360 / 3360`
- width `5`:
  - `29760 / 29760`
- width `6`:
  - `249984 / 249984`
- width `7`:
  - `2048256 / 2048256`

The three live domains from `v64` are exact instances of the same law.

So the support-literal line is now stronger than a transferred family pattern.
It is a bounded support-table law candidate for the full `3`-role case.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
