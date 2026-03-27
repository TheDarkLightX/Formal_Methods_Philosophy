## v70, width4 support-count law frontier

### Structural target

Compress the exact width-`4` support-profile law from `v69` into the smallest
exact scalar law found in the searched profile-derived feature library.

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

where `count_private_roles` means the number of roles whose minimal
unique-support size is `1`.

### Strongest claim

On the exact width-`4` support-profile frontier:

- the minimal compiler cost is already determined by one scalar:
  - `count_private_roles`
- exact law:
  - `4 -> 3`
  - `3 -> 3`
  - `2 -> 4`
  - `1 -> 5`
  - `0 -> 6`

So the `v69` six-profile law collapses again.

It is not only:

- a support-profile law

It is also:

- a one-scalar private-role-count law for exact cost

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
