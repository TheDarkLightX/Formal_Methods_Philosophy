## v68, width3 invariant law frontier

### Structural target

Compress the `v67` six-orbit geometry atlas into the smallest exact graph
invariant law found in the searched invariant library.

### Bounded domain

Width-`3` `4`-role geometry atlas from `v67`:

- `6` cube-orbit classes
- exact orbit costs:
  - `3`
  - `4`
  - `5`
  - `6`

Searched invariant library:

- scalar invariants:
  - `edge_count`
  - `max_degree`
  - `leaf_count`
  - `isolated_count`
  - `connected`
  - `component_sizes`
  - `degree_sequence`

### Question

`v67` showed that the width-`3` `4`-role frontier collapses to a six-orbit
geometry atlas.

This cycle asks whether the orbit cost can be predicted exactly by a much
smaller invariant basis.

### Strongest claim

On the exact `v67` orbit atlas:

- no searched singleton scalar invariant is exact
- the simplest exact invariant pair found is:
  - `(edge_count, max_degree)`

Exact cost law:

- if `(edge_count, max_degree) = (3, 3)`, cost `3`
- if `(edge_count, max_degree) = (3, 2)`, cost `4`
- if `(edge_count, max_degree) = (2, 2)`, cost `5`
- otherwise, cost `6`

So the width-`3` `4`-role frontier now has:

- an exact cost atlas from `v67`
- and an exact two-scalar invariant law above that atlas

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
