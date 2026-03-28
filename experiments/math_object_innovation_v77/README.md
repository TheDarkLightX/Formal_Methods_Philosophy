# v77: minimal witness-language phase diagram

## Structural target

Package the first bounded `minimal witness-language discovery` result on one
fixed exact frontier.

The goal is not another controller search. The goal is to compare several exact
language families side by side on the same repaired verifier frontier and ask:

> what is the smallest exact language once the local witness contract is fixed?

## Bounded domain

- the repaired verifier frontier from `v24`, `v35`, and `v36`
- exact quotient states:
  - `10`
- state coordinates:
  - `H6`
  - `E`
- exact labels:
  - `safe`
  - `fail_13116`
  - `fail_1915`
  - `fail_828`

## Compared language families

1. pure positive atom covers from `v35`
2. mixed atom covers with a residual default from `v35`
3. invented positive covers from `v36`
4. ordered decision-list compiler from `v24`

## Main bounded result

Minimal exact language search does not collapse to one universally best family.

The optimum depends on the witness semantics:

- smallest exact all-positive unordered language:
  - `positive_invented_cover`
  - cost `4`
- smallest exact unordered residual-default language:
  - `mixed_atom_cover`
  - cost `4`
  - default `fail_828`
- smallest exact ordered classifier:
  - `ordered_decision_list`
  - guard count `4`
  - default `fail_828`

The baseline pure positive atom family is strictly worse:

- `positive_atom_cover`
- cost `7`

## Why it mattered

This is the first explicit bounded phase diagram in the repo where the answer to
"what is the best exact language?" depends on the witness contract itself.

That supports a sharper umbrella above verifier compilation:

- not only "find a verifier compiler"
- but "find the smallest exact language in which local witnessing is allowed"

## Claim tier

- tier:
  - `descriptive_oracle`
- oracle dependent:
  - yes

## Strongest claim

On the repaired verifier frontier, minimal exact language search does not return
one universally best family. Instead the optimum depends on the local witness
contract. This is bounded evidence for minimal witness-language discovery as a
meta-loop above verifier compilation.

## Boundary learned

This cycle compares only four already-surviving language families on one fixed
bounded frontier.

The next honest step is stronger:

- search over a larger bounded family of witness languages directly
- or repeat the same phase-diagram comparison on a harder frontier where the
  current exact families do not all tie at cost `4`
