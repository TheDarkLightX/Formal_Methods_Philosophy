## v73, width4 orbit mixed-basis frontier

### Structural target

Find the first exact basis that reconstructs the full width-`4` orbit class
once the transferred support-count laws from `v72` stop being enough.

### Bounded domain

Abstract family:

- unlabeled `4`-subsets of the `4`-cube
- quotiented by cube automorphisms
- exhaustive orbit count:
  - `19`

Searched basis library:

- support-count coordinates:
  - `count_private_roles`
  - `count_size2_roles`
- geometry coordinate:
  - `distance_multiset`

### Strongest claim

On the full width-`4` orbit family:

- support counts alone do not determine the orbit class
- no searched singleton basis is exact
- the first exact bases are:
  - `(count_private_roles, distance_multiset)`
  - `(count_size2_roles, distance_multiset)`

So the first genuine width-`4` orbit obstruction is small:

- support counts control cost and profile
- one geometric multiset is enough to finish orbit reconstruction

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
