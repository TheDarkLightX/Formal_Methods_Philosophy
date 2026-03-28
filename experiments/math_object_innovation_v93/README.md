# v93: staged temporal monitor-cell obligation quotient

## Question

`v92` said the biggest unlocks came from changing the search object, not from
widening the current grammar. The strongest next rabbit hole was temporal
obligation geometry.

The bounded first question is:

> on a temporal controller family for the retest tracker safety fragment, do
> symbolic monitor cells replace flat concrete prefixes directly, or only after
> earlier prefix obligations have already carved away bad candidates?

This is a side-branch test of the deeper loop shape, not a claim that Tau is now
the main frontier.

## Method

Bounded domain:

- the safety-action fragment of
  `examples/tau/medical_retest_protocol_tracker_v1.tau`
- current-step semantic predicates:
  - `override`
  - `was_review`
  - `repeat_and_abnormal`
  - `nonzero_result`
- controller family:
  - all ordered decision lists over those four predicates
  - `3` possible actions on each hit
  - `3` possible default actions
  - total candidates:
    - `4! * 3^5 = 5832`
- flat temporal obligations:
  - all two-step traces from the initial `watch` state
  - total:
    - `144`
- symbolic monitor-cell obligations:
  - all `(previous_action, current_input)` cells
  - total:
    - `36`

The report compares two regimes:

1. raw comparison on the whole candidate family
2. staged comparison after flat step-1 carving, meaning only candidates that
   already match the spec on every first-step input are kept

## Main bounded result

The strong positive result is staged, not unconditional.

Raw comparison on all `5832` candidates:

- flat two-step trace behavior classes:
  - `73`
- monitor-cell behavior classes:
  - `168`
- partition match:
  - `false`
- greedy yes-only checks to isolate the exact spec class:
  - flat traces:
    - `4`
  - monitor cells:
    - `6`

So raw monitor cells are too strong if applied from step `0`.

After flat step-1 carving:

- surviving candidates:
  - `108`
- flat residual behavior classes:
  - `12`
- monitor-cell residual behavior classes:
  - `12`
- exact partition match:
  - `true`
- exact spec-class match:
  - `true`
- greedy yes-only checks:
  - flat residual traces:
    - `2`
  - monitor cells:
    - `2`

The residual obligation catalog still shrinks:

- flat concrete prefixes:
  - `144`
- symbolic monitor cells:
  - `36`
- reduction:
  - `108`
- ratio:
  - `4.0`

## Why it matters

This is the first temporal side-branch law in the current program:

- symbolic cells are not always the right obligation object from the start
- they can become the right object after earlier concrete carving has already
  removed controllers that never reach the relevant temporal states

That is a useful general correction for software-engineering loops too.
Symbolic obligation cells may need a staged entry point:

- concrete prefix or test carving first
- symbolic state obligations second

## Status

Survivor, but as a side-branch boundary result.

The surviving object is:

- staged temporal monitor-cell obligation quotient

The main software-engineering frontier should still move back to higher-leverage
loop families, not stay inside Tau-specific temporal detail.

## Next

- translate the staged-carving lesson back into software engineering:
  - concrete failing tests first
  - symbolic obligation fibers after that
- compare obligation-fibered repair, certificate-carrying repair, and minimal
  repair-language discovery on a bounded bug corpus
