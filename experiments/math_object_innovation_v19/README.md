# v19: score-safety collapse frontier

## Structural target

Test whether exact bounded safety collapses to maximizing a single sampled score after residual
consistency has already been enforced.

The bounded question is:

- inside the `7104` residual-consistent repair-program frontier,
- does exact safety coincide with one maximal score block?

## Scalar candidates

The scalar score coordinates already present in the frontier are:

- `holdout_total`
- `holdout_5_hits`
- `holdout_6_hits`

## Allowed claim

If safety coincides exactly with one maximal scalar block, then in this bounded model universal
safety has collapsed to scalar maximization inside the residual-consistent frontier.
