#!/usr/bin/env markdown
# Math Object Innovation Cycle v12

This cycle lifts the controller search one level up.

Instead of searching for one more local clause, it synthesizes a short **repair
program** over the tie-break clause language from `v11`.

Repair-program shape:

1. start from the exact bounded two-clause controller from `v10`
2. allow one ordered pair of tie-break clauses
3. require the pair to fix the sampled larger-root residual cases
4. run CEGIS over exhaustive reachable nonterminal `4x4` states:
   - propose the lexicographically simplest pair consistent with the current bank
   - ask the verifier for the first failing `4x4` state
   - add that state to the bank
   - repeat

Bounded target:

- either no safe short repair program exists in this language,
- or one exists and the loop finds it,
- and then the next question becomes whether safety alone is enough, or whether
  the loop also needs an explicit larger-domain ranking objective.
