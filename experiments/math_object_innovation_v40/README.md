## v40, score-local witness frontier with residual defaults

### Structural target

Move from shortcut tuning to witness-language discovery on the hard refill
frontier.

### Bounded domain

- Same monotone refill-style controller family as `v29` to `v39`
- Same 3-state training set
- Same 13-state holdout set
- Same `130` residual-consistent viable behaviors
- Feature language taken from the exact `v38` ladder:
  - `err[6] AND err[10] AND err[12]`
  - `err[3]`
  - `err[9] AND err[10] AND err[12]`
  - `err[6]`
  - `err[8]`
  - `err[9]`
  - `err[10]`
  - `err[12]`
- Witness atom grammar:
  - conjunctions of `1` to `3` signed literals over those `8` features

### Question

The local shortcut line is now tight:

- `v37` found one helpful shortcut
- `v38` found a stronger two-shortcut ladder
- `v39` showed the anchored third shortcut does not improve the main cost or
  depth metrics

This cycle asks a different question:

- in the `v38` feature language,
- do the nontrivial score blocks admit exact score-local witness languages,
- and does positive-cover plus residual-default treatment help where all-positive witnesses fail?

### Strongest claim

In the searched witness-atom grammar, every nontrivial score block on the hard
`v38` feature space admits an exact positive-cover plus residual-default witness
language.

The total positive-cover-plus-residual cost across the six nontrivial score
blocks is `27`.

All-positive witness languages already fail on the hardest score blocks:

- score `9`
- score `10`

So the frontier really has moved up a level:

- local shortcut search is near saturation,
- but score-local witness-language discovery still yields exact structure.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
