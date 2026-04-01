# v278: anomaly-route Fibonacci-periodic decomposition law

## Assumption

Work on the anomaly-side route through the bridge-fan-tail feeder family:

- source family:
  - `BFT(r, t)`
- target:
  - the star on the same `n = r + t + 6`
- checked strip:
  - `2 <= r <= 7`
  - `1 <= t <= 10`
  - `n <= 23`

Write:

- `B(r, t) = TD(BFT(r, t))`
- `S(r, t) = TD(star_{r + t + 6}) = 2^(r + t + 5) - 1`
- `Delta(r, t) = S(r, t) - B(r, t)`

Let `F_t` be the Fibonacci sequence with `F_0 = 0`, `F_1 = 1`.

## Claim

The whole anomaly-side amount law may already separate into two symbolic
channels:

- an exponential star target
- a Fibonacci-periodic feeder term

## Result

On the checked strip, the feeder amount is given exactly by

`B(r, t) = A_r * F_t + B_r * F_{t + 1} + C_r * cos(pi t / 2) + A_r * sin(pi t / 2)`

with

- `A_r = (14 / 5) * (3 * 2^r - 1)`
- `B_r = (7 / 5) * (8 * 2^r - 1)`
- `C_r = (14 / 5) * (2^r - 2)`

So the whole route deficit is exactly

`Delta(r, t) = 2^(r + t + 5) - 1 - B(r, t)`

The forcing term from `v277`

`5 * 2^(r + t + 1) + 2`

is exactly the amount by which the exponential target sequence `S(r, t)`
fails the homogeneous feeder recurrence.

## Why this matters

This is cleaner than a checked recurrence table.

The anomaly-side route now looks like one symbolic decomposition:

- a universal exponential target term
- minus a feeder term with Fibonacci growth and a small period-4 residue

That is the first route law on this line that exposes the mechanism, not only
the compiler surface.

## Artifacts

- `generated/report.json`
