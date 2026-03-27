## v42, score-abstraction witness frontier

### Structural target

Search for an exact score abstraction above the score-local positive-cover plus
residual-default witness
languages from `v40`.

### Bounded domain

- Same monotone refill-style controller family as `v29` to `v41`
- Same 3-state training set
- Same 13-state holdout set
- Same `130` residual-consistent viable behaviors
- Same `v38` feature language with `8` features
- Same witness-atom grammar as `v40` and `v41`:
  - conjunctions of `1` to `3` signed literals
- Nontrivial scores:
  - `7, 8, 9, 10, 11, 12`

### Search space

- all contiguous partitions of the six nontrivial scores
- for each score region:
  - search the smallest exact positive-cover plus residual-default witness
    language in the same grammar
- optimize:
  - total positive-cover-plus-residual witness cost
  - then region count

### Question

`v40` gave six exact score-local positive-cover plus residual-default witness
languages with total cost
`27`.

This cycle asks whether some neighboring score blocks can be merged into larger
exact witness regions, reducing total cost.

### Strongest claim

In the searched score-abstraction space, the best exact partition is:

- `(7)`
- `(8)`
- `(9)`
- `(10, 11)`
- `(12)`

This lowers total positive-cover-plus-residual witness cost from `27` to `23`.

The merged region `(10,11)` admits an exact positive-cover plus residual-default
witness language of cost `5`, with default label `(1,0,1,1)`.

Among the searched contiguous partitions:

- the score-local partition with `6` regions is feasible
- the merged `5`-region partition above is feasible and better
- no coarser contiguous partition is exact

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
