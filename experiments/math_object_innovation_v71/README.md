## v71, width4 profile-pair law frontier

### Structural target

Compress the full six-profile width-`4` law from `v69` into the smallest exact
basis found in the searched profile-derived feature library.

### Bounded domain

Input frontier:

- the exact six-profile width-`4` support-profile frontier from `v69`

Searched scalar features:

- `count_private_roles`
- `count_size2_roles`
- `count_size3_roles`
- `max_support_size`
- `sum_support_sizes`
- `sum_three_smallest`
- `smallest_support_size`

### Strongest claim

On the exact width-`4` support-profile frontier:

- no searched singleton scalar reconstructs the full six-profile law
- the pair
  - `count_private_roles`
  - `max_support_size`
  reconstructs it exactly

So the full `v69` profile law also compresses:

- from six explicit profiles
- to one exact two-scalar basis

This sharpens the picture:

- exact cost needs only one scalar, from `v70`
- exact full profile needs two scalars

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
