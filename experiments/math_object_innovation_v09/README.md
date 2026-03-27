# Math Object Innovation Cycle v09

This cycle lifts the controller search into a safer synthesis shape:

- keep one exact bounded dominance clause as a verified core
- search for a second repair clause
- reject any repair that changes even one exhaustive `4x4` reachable state
- among the safe repairs, rank by sampled `5x5` and `6x6` root performance

This is a bounded-core-preserving repair loop.

If it works, the loop has a cleaner engineering interpretation:

- verified symbolic core
- untrusted repair proposals
- fail-closed bounded checker
- out-of-domain generalization scorer
