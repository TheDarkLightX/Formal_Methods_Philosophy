## v47, global witness-synthesis grammar boundary frontier

### Structural target

Test whether the more-global witness object from `v46` still improves when the
atom grammar grows one step further.

### Bounded domain

- Same monotone refill-style controller family as `v29` to `v46`
- Same 3-state training set
- Same 13-state holdout set
- Same `130` residual-consistent viable behaviors
- Same exact partition from `v44` to `v46`:
  - `(7)`, `(8)`, `(9)`, `(10,11)`, `(12)`
- Compare two global witness-synthesis searches:
  - conjunctions of `1..4` signed literals
  - conjunctions of `1..5` signed literals

### Question

`v46` showed that the exact `v44` partition compresses from raw local witness
cost `22` to a shared global schema library of size `19`.

This cycle asks whether the global object still improves when the atom grammar
grows from `1..4` to `1..5`.

### Strongest claim

In the searched `1..5` grammar:

- the exact partition stays the same
- total region cost stays `22`
- best shared global schema count stays `19`

So the more-global witness line is also tight on its main metric under one more
literal.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
