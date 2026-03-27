## v48, cross-frontier witness-template frontier

### Structural target

Move beyond one frontier at a time and test whether multiple exact witness
libraries collapse into a smaller meta-language.

### Bounded domain

- Source frontier A:
  - exact global witness-schema library from `v41`
- Source frontier B:
  - exact global witness-schema library from `v46`
- Both are bounded, exact, oracle-dependent witness objects already packaged in
  the repo

### Question

The local and global witness axes are now tight on their main metrics:

- `v45` closed the nearby local grammar line
- `v47` closed the nearby global grammar line

So the sharper question is no longer “one more literal?” It is:

- do multiple exact witness frontiers share a smaller template language above
  their raw formulas?

### Strongest claim

Across the exact schema libraries from `v41` and `v46`:

- raw union of exact formulas:
  - `22`
- exact overlap:
  - `17`
- untyped conjunction-shape templates:
  - `10`
- typed templates, keeping feature kind:
  - `13`

So the next live compression axis is not one more local witness formula. It is a
cross-frontier witness-template language.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
