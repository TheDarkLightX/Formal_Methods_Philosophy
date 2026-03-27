# v26: MPRD transfer boundary frontier

## Structural target

Test whether the quotient-and-repair verifier-compiler pattern transfers cheaply to a small
MPRD-shaped policy family.

The bounded question is:

- take the toy lab-follow-up policy shape,
- enumerate a finite family of small decision-list controllers,
- condition on a tiny training set,
- then ask whether the first-refuter partition on the residual-consistent frontier collapses to
  `holdout score + a small repair feature set`.

## Bounded domain

- facts:
  - `pathway_open`
  - `red_flag_present`
  - `abnormal_flag`
- gold policy:
  - `review` if pathway is closed or a red flag is present
  - `repeat` if pathway is open, no red flag, and abnormal
  - `watch` otherwise
- controller family:
  - decision lists with `1` to `3` guards
  - guard language over literals and conjunctions of the three fact flags
  - action set `{watch, repeat, review}`
- training set:
  - `(1,0,0)`
  - `(1,0,1)`
  - `(0,0,0)`
- holdout set:
  - the other `5` fact states
- repair-feature library:
  - predicted action on each holdout state
  - total counts of each action across all `8` states

## Allowed claim

If no exact repair exists with up to `k` simple behavior features, but one does exist with `k+1`,
that is a real bounded transfer boundary for the quotient-and-repair loop in this MPRD-shaped domain.
