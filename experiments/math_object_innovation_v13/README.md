#!/usr/bin/env markdown
# Math Object Innovation Cycle v13

This cycle asks whether multiple proposers improve the repair-program loop.

Structural target:

1. reuse the repair-program search space from `v12`
2. treat different ranking rules over the same residual-consistent pair set as
   different proposers
3. give all proposers a shared bounded counterexample bank
4. compare:
   - verifier calls to the first safe repair program
   - bank size at discovery
   - proposer rounds for synchronous portfolios

Bounded domain:

- residual-consistent ordered pairs of tie-break clauses above the exact bounded
  two-clause controller
- exhaustive reachable nonterminal `4x4` verifier

Main question:

- does proposer multiplicity alone create leverage,
- or does leverage come from proposer diversity plus shared falsification?
