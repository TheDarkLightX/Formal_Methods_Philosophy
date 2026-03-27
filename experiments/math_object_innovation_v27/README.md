# v27: MPRD semantic repair frontier

## Structural target

Refine the `v26` transfer boundary by searching semantically meaningful repair features rather than
raw predicted-action features.

The bounded question is:

- in the same toy MPRD lab-followup controller family,
- does the first exact repair appear in a semantic feature library too,
- and if so, how many semantic repair bits are needed?

## Bounded domain

- the same residual-consistent unique-behavior frontier from `v26`
- primary coordinate:
  - `holdout score`
- semantic repair-feature library over the `5` holdout states:
  - mistake indicators `err[s]`
  - one-hot action indicators:
    - `is_review[s]`
    - `is_repeat[s]`
    - `is_watch[s]`
  - aggregate counts on the holdout set:
    - `error_count`
    - `review_count_holdout`
    - `repeat_count_holdout`
    - `watch_count_holdout`

## Allowed claim

If no exact repair exists with `1`, `2`, or `3` semantic features, but one exists with `4`, that is a
real bounded semantic transfer law for the MPRD case.
