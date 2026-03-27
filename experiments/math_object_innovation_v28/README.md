# v28: earliest-error compiler frontier

## Structural target

Compress the MPRD semantic repair basis into an exact symbolic law.

The bounded question is:

- in the toy MPRD lab-followup transfer case,
- is the first-refuter label exactly the earliest holdout error,
- and does `holdout score + the first four ordered error bits` form a sufficient and minimal basis?

## Bounded domain

- the same residual-consistent unique-behavior frontier from `v26`
- holdout order:
  - `h1 = (0, 0, 1)`
  - `h2 = (0, 1, 0)`
  - `h3 = (0, 1, 1)`
  - `h4 = (1, 1, 0)`
  - `h5 = (1, 1, 1)`
- semantic bits:
  - `e_i(x) := 1` iff the controller makes an error on holdout state `h_i`
- scalar:
  - `S(x) := holdout score`

## Allowed claim

If the first-refuter label equals the earliest true error bit, and `S + (e1,e2,e3,e4)` is exact while
every `S +` three-bit subset fails, then the MPRD transfer case admits an exact earliest-error
compiler law with a minimal ordered-error basis.
