#!/usr/bin/env markdown
# Math Object Innovation Cycle v14

This cycle checks whether safety and larger-domain value can be separated once a
bounded counterexample bank has been learned.

Structural target:

1. start from the `v12` banked repair-program frontier
2. keep only repair-program pairs consistent with:
   - the sampled larger-root residual cases
   - the two banked bounded counterexamples from `v12`
3. rank that viable frontier by larger sampled-root score
4. certify the ranked candidates against the exhaustive reachable nonterminal
   `4x4` verifier until the first safe pair appears

Main bounded question:

- after the bank is learned, is the top-ranked larger-domain candidate already
  safe on the bounded exact verifier?

If yes, then the loop can be factored into:

1. bounded bank learning
2. value ranking over the viable frontier
3. one final exact safety check
