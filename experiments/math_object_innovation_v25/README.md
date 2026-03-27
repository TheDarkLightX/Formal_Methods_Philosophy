# v25: verifier compiler lower-bound frontier

## Structural target

Certify that the `v24` repaired verifier compiler is not only exact, but minimal in the bounded guard
language.

The bounded question is:

- after `v24`, the repaired verifier quotient compiles to a `4`-guard exact decision list,
- can the current guard language realize the same partition with `3` guards or fewer,
- and if not, is there a small structural witness explaining why?

## Bounded domain

- the `10` repaired quotient states from `v24`
- label set:
  - `safe`
  - `fail_13116`
  - `fail_1915`
  - `fail_828`
- guard grammar:
  - `H6 > c`
  - `H6 = c`
  - `E = b`
  - `H6 = c ∧ E = b`

## Allowed claim

If exhaustive bounded search finds no exact decision list with `3` guards or fewer, and the pure-atom
geometry shows why at least `4` labeled branches are unavoidable, then the `v24` compiler has an exact
bounded minimality certificate.
