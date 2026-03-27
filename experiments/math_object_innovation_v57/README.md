## v57, raw edit-basis frontier

### Structural target

Remove the aggregated direct delta coordinates from `v56` and search for the
smallest exact feature basis over raw observed edit primitives.

### Bounded domain

- Keep the same five residual patch formulas from `v49`
- For each `core -> patch` edit, derive raw observed primitive features:
  - `add[i]` when literal `err[i]` or `not err[i]` is added
  - `drop[i]` when a literal on `err[i]` is removed
  - `flip[i]` when the sign of `err[i]` changes
- Use only primitive edit features that appear at least once in the bounded
  domain
- Search all nonempty primitive-feature subsets, smallest-first
- Target labels:
  - `FLIP_BUNDLE`
  - `ADD_BUNDLE`
  - `ADD_BUNDLE + DROP_BUNDLE`
- Certificate atom grammar:
  - conjunctions of signed literals over the chosen primitive basis

### Question

`v56` showed that the direct symbolic compiler survives on a minimal two-feature
basis over aggregated delta coordinates.

This cycle asks whether the same exact compiler survives when the search is
forced down to raw primitive edit features instead.

### Strongest claim

On the exact five residual patch formulas:

- the smallest exact all-positive raw-primitive basis has size:
  - `2`
- the smallest exact positive-cover plus residual-default raw-primitive basis
  also has size:
  - `2`
- no singleton primitive basis is exact
- the exact all-positive minimal bases are exactly:
  - `add[3]`, `add[8]`
  - `add[3]`, `drop[12]`
  - `add[6]`, `add[8]`
  - `add[6]`, `drop[12]`
  - `add[8]`, `add[10]`
  - `add[10]`, `drop[12]`

So the direct residual-family compiler survives even after removing the
aggregated semantic coordinates.

The surviving primitive bases factor cleanly:

- one add-anchor from:
  - `add[3]`
  - `add[6]`
  - `add[10]`
- one mixed-patch discriminator from:
  - `add[8]`
  - `drop[12]`

### Claim tier

- `tier = symbolic_state_compiler`
- `oracle_dependent = true`
