# v15: minimal-bank synthesis frontier

## Structural target

Find the smallest bounded counterexample bank that makes the staged `bank -> rank -> certify`
loop work.

More precisely:

- start from the residual-consistent repair-program pairs from `v12`
- rank them by the fixed larger-domain holdout score used in `v14`
- let the target pair be the first pair in that ranking that is actually safe on the
  exhaustive reachable nonterminal `4x4` verifier
- synthesize the smallest bank of bounded verifier states that preserves that target pair
  and eliminates every higher-ranked unsafe pair

This is a teaching-set problem, not another controller-tuning problem.

## Bounded domain

- exhaustive reachable nonterminal `4x4` verifier states, compressed into unique state patterns
- sampled `5x5` roots with seed `99`
- sampled `6x6` roots with seed `123`
- repair-program language inherited from `v12` and `v14`

## Claim discipline

The strongest allowed claim is bounded and descriptive:

- either the staged loop needs both known bank states
- or a smaller exact teaching bank exists in this bounded model

No direct runtime claim is allowed.
