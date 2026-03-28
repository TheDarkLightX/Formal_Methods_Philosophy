# v80: hard certificate-language boundary

## Structural target

Compare the current hard witness-language winner against a stricter family:
exact all-positive certificates.

The concrete question is:

> on the exact hard merged-region partition from `v44`, is an all-positive
> certificate language already enough?

## Bounded domain

- the hard merged-region witness frontier from `v44`
- same exact partition:
  - `(7)`
  - `(8)`
  - `(9)`
  - `(10,11)`
  - `(12)`
- same conjunction grammar:
  - `1` to `4` signed literals over the `v38` feature surface

## Main bounded result

The searched all-positive certificate family is not exact everywhere.

It succeeds on:

- `(7)`
- `(8)`
- `(9)`
- `(12)`

but already fails on:

- `(10,11)`

Partial exact cost over the feasible regions:

- total certificate cost:
  - `23`
- shared schema count:
  - `21`

## Why it mattered

`v79` showed that exact decomposition is available on the hard frontier but does
not beat the current label-level witness language.

`v80` sharpens the certificate side:

- all-positive certification is not only more expensive in general
- in this searched grammar it is not even exact on the full hard partition
- and even on the four feasible regions it is still worse than the current
  label-level witness language

So residual-default witness languages are not merely a compression trick here.
They are necessary in the current bounded language family.

## Claim tier

- tier:
  - `descriptive_oracle`
- oracle dependent:
  - yes

## Strongest claim

On the hard merged-region witness frontier, residual-default witnessing is
necessary in the searched conjunction grammar because the all-positive
certificate family already fails on region `(10,11)`.

## Boundary learned

This rules out one natural stricter family on the same bounded corpus.

The next honest step is:

- compare against richer certificate languages on the same hard frontier
- or search certificate languages that allow a small amount of local negative or
  residual structure
