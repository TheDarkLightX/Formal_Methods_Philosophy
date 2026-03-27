## v58, primitive basis template frontier

### Structural target

Compress the six exact raw primitive bases from `v57` into the smallest exact
role-template family.

### Bounded domain

- Keep the exact `v57` raw primitive all-positive basis family
- Primitive features used by that family:
  - `add[3]`
  - `add[6]`
  - `add[8]`
  - `add[10]`
  - `drop[12]`
- Search two-slot role templates:
  - `left`
  - `right`
  - optional `unused`
- A template generates all unordered feature pairs `{l, r}` with:
  - `l in left`
  - `r in right`

### Question

`v57` left the raw primitive line with six exact minimal bases.

This cycle asks whether those six bases are only a flat atlas, or whether they
collapse to a smaller exact template family over primitive roles.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
