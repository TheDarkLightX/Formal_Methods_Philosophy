## v69, width4 support-profile frontier

### Structural target

Compress the width-`4` `4`-role cost histogram into the smallest exact
support-profile object found in the bounded family.

### Bounded domain

Abstract support-table family:

- labeled `4`-role support tables
- one realized support signature per role
- all four signatures distinct
- support width:
  - exhaustive `4`

Per-role support statistic:

- minimal unique-support size for each role, meaning the fewest support bits
  needed to distinguish that role from all other realized roles

### Question

The first width-`4` scan showed:

- no new total compiler cost beyond `6`
- exact cost histogram:
  - `3`
  - `4`
  - `5`
  - `6`

This cycle asks whether that histogram collapses to a small exact law over the
per-role unique-support profile.

### Strongest claim

On the exhaustive width-`4` family:

- only `6` sorted minimal unique-support profiles occur:
  - `(1,1,1,1)`
  - `(1,1,1,2)`
  - `(1,1,1,3)`
  - `(1,1,2,2)`
  - `(1,2,2,2)`
  - `(2,2,2,2)`
- exact counts:
  - `(1,1,1,1)`: `384`
  - `(1,1,1,2)`: `4608`
  - `(1,1,1,3)`: `3840`
  - `(1,1,2,2)`: `18432`
  - `(1,2,2,2)`: `13056`
  - `(2,2,2,2)`: `3360`
- the exact minimal compiler cost is determined by the profile:
  - cost `3` for the first three profiles
  - cost `4` for `(1,1,2,2)`
  - cost `5` for `(1,2,2,2)`
  - cost `6` for `(2,2,2,2)`

Equivalently:

- exact minimal cost = the sum of the three smallest profile entries

So the width-`4` frontier is not just a histogram.
It has an exact support-profile law.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
