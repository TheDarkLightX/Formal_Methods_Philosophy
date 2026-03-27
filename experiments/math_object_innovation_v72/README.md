## v72, width4 orbit support-count transfer frontier

### Structural target

Test whether the exact support-count laws from `v70` and `v71` survive after
passing from the width-`4` labeled-table frontier to the unlabeled cube-orbit
frontier.

### Bounded domain

Abstract family:

- unlabeled `4`-subsets of the `4`-cube
- quotiented by cube automorphisms
- exhaustive orbit count:
  - `19`

Support-count coordinates:

- `count_private_roles`
- `count_size2_roles`
- `count_size3_roles`
- `max_support_size`

### Strongest claim

On the full width-`4` unlabeled orbit family:

- exact cost is still determined by one scalar:
  - `count_private_roles`
- exact full support profile is still reconstructed by the pair:
  - `count_private_roles`
  - `max_support_size`

So the `v70` and `v71` laws are not artifacts of the labeled presentation.
They survive unchanged on the width-`4` orbit space.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
