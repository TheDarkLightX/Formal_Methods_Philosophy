## v63, support-signature transfer frontier

### Structural target

Test whether the support-profile law from `v62` is a reusable object by checking
whether a second exact frontier also compiles by support signatures.

### Bounded domains

Domain A, cross-frontier schema roles from `v49`:

- roles:
  - `CORE`
  - `V41_PATCH`
  - `V46_PATCH`
- support bits:
  - `has_v41`
  - `has_v46`

Domain B, residual primitive roles from `v62`:

- roles:
  - `ADD_ANCHOR`
  - `MIX_DISCRIM`
  - `OTHER`
- support bits:
  - `has_AB`
  - `has_MIX`

### Question

`v62` showed that the predictive and structure-preserving exact objectives in
the residual-family line are governed by one shared two-feature support-profile
law.

This cycle asks whether that support-signature pattern survives in a second,
earlier exact frontier.

### Strongest claim

Both bounded domains compile exactly by support signatures over two bits.

Domain A:

- `CORE` iff `has_v41 and has_v46`
- `V41_PATCH` iff `not has_v46`
- `V46_PATCH` iff `not has_v41`

Domain B:

- `ADD_ANCHOR` iff `has_AB`
- `MIX_DISCRIM` iff `not has_AB and has_MIX`
- `OTHER` iff `not has_MIX`

So the support-profile law from `v62` is not isolated. It transfers to a second
exact frontier as a generic support-signature role law.

For Domain A, this simplification is scoped to the bounded frontier, because the
`00` support signature does not occur there.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
