# Math Object Innovation Cycle v10

This cycle lifts the exact bounded clause family into a small two-clause language.

Language shape:

1. keep the best exact single-clause `4x4` core
2. add one deeper-lookahead repair clause
3. reject any repair that changes any exhaustive reachable `4x4` state
4. among the safe repairs, rank by sampled `5x5` and `6x6` root performance

Targeted repair family:

- `gain_loss = 2`
- `child_gain_min = 3`
- `child_cut_min ∈ {0,1,2}`
- `next_delta = 2`
- `next_mode ∈ {eq, ge}`

This is a bounded, fail-closed repair search, not a theorem for arbitrary `n`.
