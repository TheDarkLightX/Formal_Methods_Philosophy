# v29: monotone refill transfer frontier

## Structural target

Test the verifier-compiler transfer pattern in a second MPRD-shaped domain with a more monotone policy
shape.

The bounded question is:

- take a toy refill gate with four positive evidence flags,
- search a finite family of monotone decision-list controllers,
- condition on a small training set,
- and ask how large the first exact semantic repair basis becomes on the residual-consistent frontier.

## Bounded domain

- fact flags:
  - `id_bound`
  - `dose_ok`
  - `labs_fresh`
  - `window_ok`
- gold policy:
  - `refill` iff all four flags are true
  - `review` otherwise
- controller family:
  - decision lists with `1` to `3` guards
  - positive-conjunction guards only
  - action set `{refill, review}`
- training set:
  - `(1,1,1,1)`
  - `(0,1,1,1)`
  - `(1,1,0,1)`
- holdout set:
  - the other `13` fact states
- semantic repair features:
  - holdout mistake indicators `err[s]`

## Allowed claim

If no exact semantic repair exists with `5` holdout error bits or fewer, but one exists with `6`, that
is a real second-domain transfer boundary for the verifier-compiler loop.
