## v54, fiber-certificate frontier

### Structural target

Compare the new explanation-fiber object from `v53` against direct
certificate-language discovery on the same bounded residual domain.

### Bounded domain

- Keep the exact `v53` fiber decomposition fixed
- Residual patches:
  - `5`
- Fiber labels:
  - `FLIP_BUNDLE`
  - `ADD_BUNDLE`
  - `ADD_BUNDLE + DROP_BUNDLE`
- Patch-summary features derived from used family sets:
  - `has_add`
  - `has_drop`
  - `has_flip`
- Certificate atom grammar:
  - conjunctions of `1` to `3` signed literals over those three summary features

### Question

`v53` showed that the residual semantic language is almost fiber-pure:

- only one mixed patch remains
- only one mixed fiber remains

This cycle asks whether a direct certificate language over patch-summary
features can compress those exact fiber labels further.

### Strongest claim

On the exact `v53` fiber labels:

- the smallest exact all-positive certificate language has cost:
  - `3`
- a positive-certificate plus residual-default language has cost:
  - `2`

The best residual-default language is:

- certify `ADD_BUNDLE + DROP_BUNDLE` by:
  - `has_drop`
- certify `FLIP_BUNDLE` by:
  - `has_flip`
- treat `ADD_BUNDLE` as the residual default class

So the direct certificate line slightly compresses the explanation-fiber object
once the exact fibers are known.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
