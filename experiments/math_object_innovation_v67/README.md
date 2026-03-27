## v67, width3 four-role geometry frontier

### Structural target

Explain the `v66` width-`3` `4`-role cost ladder geometrically by classifying
the exact compiler cost by cube-subset orbit.

### Bounded domain

Abstract support-table family:

- labeled `4`-role support tables
- one realized support signature per role
- all four signatures distinct
- support width:
  - exhaustive `3`

Geometry quotient:

- unlabeled `4`-subsets of the `3`-cube
- modulo cube automorphisms

### Question

`v66` showed that width `3` has the exact cost ladder:

- cost `3`: `192`
- cost `4`: `576`
- cost `5`: `576`
- cost `6`: `336`

This cycle asks whether that ladder is just a flat count table, or whether it
collapses to a small exact geometric atlas.

### Strongest claim

The width-`3` `4`-role frontier collapses exactly to `6` cube-orbit classes, and
every orbit has a uniform exact minimal total-literal cost.

Orbit atlas:

- `(0,1,2,4)`, claw orbit:
  - orbit size `8`
  - edge count `3`
  - exact cost `3`
- `(0,1,2,5)`, path orbit:
  - orbit size `24`
  - edge count `3`
  - exact cost `4`
- `(0,1,2,7)`, vee-plus-isolated orbit:
  - orbit size `24`
  - edge count `2`
  - exact cost `5`
- `(0,1,2,3)`, square orbit:
  - orbit size `6`
  - edge count `4`
  - exact cost `6`
- `(0,1,6,7)`, disjoint-edge orbit:
  - orbit size `6`
  - edge count `2`
  - exact cost `6`
- `(0,3,5,6)`, independent orbit:
  - orbit size `2`
  - edge count `0`
  - exact cost `6`

Weighted by orbit size and role labelings, this reproduces the full `v66`
ladder exactly.

So the first `4`-role cost hierarchy is not only a histogram.
It is a small exact geometry atlas.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
