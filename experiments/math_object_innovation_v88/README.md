# v88: lab-followup partition-aware residual-budget transfer frontier

## Question

`v87` closed the literal-width story on the hard refill frontier.

The next honest step is transfer:

> if the same partition-aware residual-budget search is moved to the earlier toy
> lab-followup MPRD frontier, does it produce a similar descending ladder, or a
> different exact residual structure?

## Method

Bounded domain:

- reuse the residual-consistent unique-behavior frontier from `v26`
- holdout states:
  - `(0,0,1)`
  - `(0,1,0)`
  - `(0,1,1)`
  - `(1,1,0)`
  - `(1,1,1)`
- mixed score blocks:
  - `1, 2, 3, 4`
- verifier labels:
  - first-refuter labels on those holdout states

Language:

- signed conjunction atoms over the five holdout error bits
- widths `1` through `4`
- same grammar for:
  - strict all-positive certificate regions
  - residual-default witness regions

Objective:

- search all set partitions of score blocks `1,2,3,4`
- for each exact residual budget:
  - minimize shared schema count
  - then exact total formula cost

## Main bounded result

The transfer survives, but not as a monotone descending ladder.

Exact schema-first ladder:

- budget `0`:
  - shared schemas `5`
  - total cost `5`
  - partition:
    - `(1,2,3,4)`
  - residual regions:
    - none
- budget `1`:
  - shared schemas `4`
  - total cost `4`
  - partition:
    - `(1,2,3,4)`
  - residual regions:
    - `(1,2,3,4)`
- budget `2`:
  - shared schemas `4`
  - total cost `5`
  - partition:
    - `(1)`
    - `(2,3,4)`
  - residual regions:
    - both regions
- budget `3`:
  - shared schemas `4`
  - total cost `7`
  - partition:
    - `(1)`
    - `(2)`
    - `(3,4)`
  - residual regions:
    - all three regions
- budget `4`:
  - shared schemas `6`
  - total cost `10`
  - partition:
    - `(1)`
    - `(2)`
    - `(3)`
    - `(4)`
  - residual regions:
    - all four regions

## Why it matters

This is a real transfer result, not a replay of the refill frontier.

The same loop shape survives:

- search score partitions
- assign regions to strict certificates or residual-default witnesses
- optimize shared schemas first

But the exact geometry changes:

- on the lab-followup frontier, a single merged residual region already beats
  the best all-positive presentation
- forcing more residual regions does not improve shared schema count
- after budget `1`, exact total cost worsens

So residual structure transfers, but as a single merged exception layer rather
than as the steadily improving ladder seen on the refill frontier.

## Status

Survivor. This is an exact transfer-side residual-budget law on the bounded
lab-followup frontier.

## Next

- compare this transfer object directly against a richer certificate language on
  the same frontier
- or search for the smallest semantic invariant that explains why one merged
  residual region is optimal here
