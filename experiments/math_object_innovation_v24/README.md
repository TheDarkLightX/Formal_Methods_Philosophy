# v24: repaired verifier compiler frontier

## Structural target

Compile the repaired `holdout_6_hits` quotient into the smallest exact verifier logic in a small
guard language.

The bounded question is:

- after `v23`, the pair `(holdout_6_hits, num_eq[4])` is an exact quotient for the full refuter
  partition,
- does that repaired quotient admit a minimal exact decision list,
- and if so, how small is the compiled verifier logic?

## Bounded domain

- the cached `7104` residual-consistent repair-program frontier from `v15`
- quotient state:
  - `H6(x) := holdout_6_hits(x)`
  - `E(x) := p1_4(x) = p2_4(x)`
- the resulting `10` reachable quotient states
- guard grammar:
  - `H6 > c`
  - `H6 = c`
  - `E = b`
  - `H6 = c ∧ E = b`

## Allowed claim

If no decision list of length `< k` exists in this grammar and one of length `k` does, then the
repaired verifier quotient compiles to a minimal exact bounded verifier logic of size `k`.
