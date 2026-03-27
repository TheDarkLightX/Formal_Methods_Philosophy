#!/usr/bin/env markdown
# Math Object Innovation Cycle v11

This cycle probes the next frontier after the exact bounded two-clause dominance
language from `v10`.

Structural target:

1. keep the exact bounded `4x4` two-clause controller as the verified core
2. search for one extra tie-break clause that acts only after the `v10` choice
3. require the tie-break clause to preserve every exhaustive reachable
   nonterminal `4x4` state
4. among those safe clauses, ask whether any closes the last sampled larger-root
   residuals

Tie-break clause family:

- same `gain`
- same `child_best_gain`
- same `next_uncovered`
- `cut_gain_min ∈ {1,2}`
- `next_size_drop_min ∈ {1,2}`
- `max_child_cut_drop ∈ {0,1,2}`
- `min_child_sum_drop ∈ {0,1,2,3,4,5}`
- `min_child_best_singleton_gain ∈ {0,1}`
- `origin_guard ∈ {any, core, repair}`
- rank mode in:
  - `cut_next`
  - `cut_next_childsum`
  - `cut_childsum_next`
  - `cut_bestsingleton_next`

Bounded claim target:

- either one more safe tie-break clause exists and improves the verified core,
- or this family is exhausted and the next frontier becomes a richer controller
  language, not another single local clause.
