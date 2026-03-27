## v66, four-role support cost frontier

### Structural target

Push past the `v65` three-role support law and identify the first exact
compiler-cost ladder for `4`-role support tables.

### Bounded domain

Abstract support-table family:

- labeled `4`-role support tables
- one realized support signature per role
- all four signatures distinct
- support widths:
  - exhaustive: `2` and `3`

Compiler grammar:

- residual-default support compilers
- one branch per non-default role
- each branch is a conjunction of signed support literals

### Question

`v65` showed that every bounded `3`-role support table up to width `7` admits a
`2`-branch `2`-literal residual-default compiler.

This cycle asks what replaces that law in the first `4`-role case:

- where does the single-literal support law first fail,
- and what exact total-literal-cost ladder replaces it?

### Strongest claim

The `3`-role support law fails immediately for `4` roles.

At width `2`:

- all `24 / 24` labeled tables are the support-square family
- none admit a `3`-branch single-literal compiler
- all admit an exact compiler with total literal cost:
  - `6`

At width `3`:

- total labeled tables:
  - `1680`
- exact single-literal star cases:
  - `192`
- exact minimal total-literal-cost distribution:
  - cost `3`: `192`
  - cost `4`: `576`
  - cost `5`: `576`
  - cost `6`: `336`

So the first `4`-role frontier is not just an obstruction.
It has an exact bounded cost ladder.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
