# Math Object Innovation Cycle v08

This cycle searches a small family of lookahead-dominance clauses around the mined `v07` rule.

Question:

- is the exact bounded dominance controller unique, or does a small family of nearby Bellman-shaped clauses stay exact on exhaustive `4x4` states?
- among the exact bounded clauses, which ones generalize best to sampled `5x5` and `6x6` roots?

Clause family:

- exact `gain` loss in `{1,2}`
- minimum `child_best_gain` improvement in `{1,2,3}`
- minimum `child_best_cut` improvement in `{0,1,2}`
- `next_uncovered` delta in `{0,1,2}`
- `next_uncovered` comparison mode in `{eq, ge}`

This is a bounded clause-family search, not a theorem for arbitrary `n`.
