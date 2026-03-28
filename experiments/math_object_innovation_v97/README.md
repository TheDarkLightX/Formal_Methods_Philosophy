# v97: shared repair-language template

## Question

`v96` found the first exact repair-language compiler in the software branch:

- the carried witness compiles back into the patch through a tiny decoder graph

The next question is one level higher:

> do the two exact decoder graphs from `v96` compress into one shared
> repair-language template plus a tiny family-specific delta?

If yes, the software branch has not only a decoder, but a shared grammar above
that decoder.

## Method

Bounded domain:

- the two exact decoder graphs from `v96`
  - `separable_patch_family`
  - `overlap_patch_family`
- edge universe:
  - `3` witness observations
  - `3` patch fields
  - total possible decoder edges:
    - `9`

Search object:

- shared base decoder graph
- then family-specific deltas

Two exact models were searched:

1. additive template model
   - each family adds edges to the shared base
2. signed-edit template model
   - each family may add or remove edges from the shared base

The search is exhaustive over all `2^9 = 512` possible base graphs.

## Main bounded result

The survivor is:

- shared repair-language template

Under both template models, the unique exact minimum is the same.

Shared base decoder:

- `guard_obs -> guard`
- `bounds_obs -> bounds`
- `transform_obs -> transform`

Family-specific delta:

- `separable_patch_family`
  - no delta
- `overlap_patch_family`
  - add:
    - `transform_obs -> bounds`

Exact costs:

- additive template:
  - base cost:
    - `3`
  - total delta cost:
    - `1`
  - total:
    - `4`
- signed-edit template:
  - base cost:
    - `3`
  - total edit cost:
    - `1`
  - total:
    - `4`

No smaller shared template exists.

## Why it matters

This compresses the software branch one level further.

The progression is now:

1. monolithic patch search
2. dependency-aware fiber search
3. witness verification
4. witness-to-patch decoder
5. shared repair-language template

The important structural law is:

- one local base decoder is reusable across both software families
- overlap does not require a new grammar
- it only requires one delta edge

So the strongest current software object is no longer just a decoder.
It is:

- a shared repair-language with sparse family patches

## Status

Survivor.

This is still a bounded descriptive-oracle result, but it is a real grammar
compression above `v96`.

## Next

- search the smallest exact patch-program macro language that realizes this
  shared template
- or move to a richer bounded bug corpus and test whether the same
  base-plus-one-delta law survives
