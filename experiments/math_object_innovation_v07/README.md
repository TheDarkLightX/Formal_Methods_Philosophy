# Math Object Innovation Cycle v07

This cycle compresses the exact `4x4` motif exception into a more general controller rule.

Controller:

1. start with the flat base rule `("max_gain", "max_child_best_gain")`
2. switch away from the base winner when another obligation:
   - gives up exactly `1` unit of immediate `gain`
   - gains at least `2` units of `child_best_gain`
   - gains at least `1` unit of `child_best_cut`
   - and increases `next_uncovered` by `1`

Why it matters:

- this rule is exact on exhaustive `4x4` roots and reachable states
- it is cleaner than a hard-coded motif dictionary
- it also improves the flat base controller on sampled `5x5` and `6x6` roots

This is still not a general theorem for arbitrary `n`.
