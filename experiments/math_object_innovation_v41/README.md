## v41, global witness-schema frontier

### Structural target

Turn the score-local positive-cover plus residual-default witness result from
`v40` into a genuinely
global witness-language object.

### Bounded domain

- Same monotone refill-style controller family as `v29` to `v40`
- Same 3-state training set
- Same 13-state holdout set
- Same `130` residual-consistent viable behaviors
- Same `v38` feature language with `8` features
- Same witness-atom grammar from `v40`:
  - conjunctions of `1` to `3` signed literals over those `8` features

### Question

`v40` showed that every nontrivial score block admits an exact positive-cover
plus residual-default witness language, with total local cost `27`.

This cycle asks a stronger global question:

- among all score-local positive-cover plus residual-default witness languages
  that keep the same optimal
  total cost,
- how small can the shared global witness-schema library become?

### Strongest claim

In the searched grammar, the exact score-local positive-cover plus
residual-default witness frontier from `v40` compresses to a global library of
only `20` distinct witness schemas.

That improves on the raw local total:

- local positive-cover-plus-residual cost `27`
- shared global schema count `20`

So the hard-frontier witness-language line is no longer only a collection of
local covers. It now has a genuine global reusable schema layer.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
