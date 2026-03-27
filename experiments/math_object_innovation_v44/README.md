## v44, richer witness-grammar frontier

### Structural target

Test whether the hard witness-language frontier from `v40` to `v43` is already
grammar-saturated, or whether one richer atom family changes the exact
score-abstraction optimum.

### Bounded domain

- Same monotone refill-style controller family as `v29` to `v43`
- Same 3-state training set
- Same 13-state holdout set
- Same `130` residual-consistent viable behaviors
- Same `v38` feature language with `8` features
- Same nontrivial scores:
  - `7, 8, 9, 10, 11, 12`
- Same unconstrained set-partition search over those six scores
- Richer witness-atom grammar:
  - conjunctions of `1` to `4` signed literals over the `8` features

### Question

`v43` closed the partition side tightly:

- all `203` score partitions were checked
- only `10` were exact in the smaller grammar
- the best exact partition was `(7), (8), (9), (10,11), (12)`
- best total witness cost was `23`

This cycle asks whether richer exact witness atoms change that frontier.

### Strongest claim

In the searched richer witness grammar:

- the same best partition from `v42` and `v43` remains optimal:
  - `(7)`, `(8)`, `(9)`, `(10,11)`, `(12)`
- best total positive-cover-plus-residual witness cost drops:
  - from `23`
  - to `22`
- feasible partition count rises:
  - from `10`
  - to `15`

So the partition side was saturated, but the witness grammar was not.

The extra gain comes from the score-`9` region, where the richer grammar admits
one more exact pure witness atom:

- `not err[3] and not err[6] and not err[8] and err[10]`

That lowers the exact score-`9` region cost from `8` to `7`.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
