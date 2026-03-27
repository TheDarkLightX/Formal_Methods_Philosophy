## v46, global witness-synthesis frontier

### Structural target

Move from local or score-partition witness objects to a more global witness
language on the hard frontier.

### Bounded domain

- Same monotone refill-style controller family as `v29` to `v45`
- Same 3-state training set
- Same 13-state holdout set
- Same `130` residual-consistent viable behaviors
- Same `v38` feature language with `8` features
- Fix the exact best partition from `v44` and `v45`:
  - `(7)`, `(8)`, `(9)`, `(10,11)`, `(12)`
- Same richer witness-atom grammar as `v44`:
  - conjunctions of `1` to `4` signed literals

### Question

`v44` gave the best exact local hard-frontier witness object:

- partition `(7), (8), (9), (10,11), (12)`
- total positive-cover-plus-residual witness cost `22`

This cycle asks whether those five exact regions compress into a materially
smaller shared global witness-schema library.

### Strongest claim

On the exact `v44` partition:

- the raw local witness cost is `22`
- the best shared global witness-schema library has only `19` formulas

So the witness-language line now has a genuinely more global object above the
best score abstraction, not only five exact local regions.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
