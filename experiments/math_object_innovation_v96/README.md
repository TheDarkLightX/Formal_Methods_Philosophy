# v96: certificate-to-patch decoder graph

## Question

`v95` showed that patch-plus-witness beats dependency-aware fiber search:

- verification cost `3`
- versus dependency-aware search cost `9`

The next question is deeper:

> can the carried witness compile back into the patch itself through a tiny
> exact decoder graph?

If yes, the main software line has moved again:

- from search over patches
- to search over repair fibers
- to verification of patch-plus-witness
- to synthesis of patch from witness

## Method

Bounded domain:

- the two `27`-patch corpora from `v94` and `v95`
  - `separable_patch_family`
  - `overlap_patch_family`
- carried witness observations from `v95`:
  - `guard_obs`
  - `bounds_obs`
  - `transform_obs`

Search object:

- exact symbolic decoders from witness observations back to patch fields:
  - `guard`
  - `bounds`
  - `transform`

For each patch field, choose a nonempty subset of witness observations as
decoder inputs.

Search all such decoder structures exactly and minimize:

- total decoder arity

This is a bounded symbolic-state compiler search.

## Main bounded result

The survivor is:

- certificate-to-patch decoder graph

### Separable family

Minimal exact decoder cost:

- `3`

Unique minimal exact decoder:

- `guard <- guard_obs`
- `bounds <- bounds_obs`
- `transform <- transform_obs`

So on the separable family, one local witness token per field is enough.

### Overlap family

Minimal exact decoder cost:

- `4`

Unique minimal exact decoder:

- `guard <- guard_obs`
- `bounds <- bounds_obs, transform_obs`
- `transform <- transform_obs`

So the overlap family needs only one extra dependency edge:

- `transform_obs -> bounds`

Not two.

That is stronger than the earlier expectation.

### Exact cost ladder

On this bounded software corpus, the current exact ladder is now:

- monolithic patch search:
  - about `35.85` to `39.0`
- dependency-aware fiber search:
  - `9`
- witness verification:
  - `3`
- witness-to-patch decoder:
  - `3` on separable
  - `4` on overlap

## Why it matters

This is the first exact repair-language compiler in the software branch.

The object is no longer only:

- a witness basis

It is:

- a minimal symbolic decoder graph from witness state to patch fields

That is a stronger loop family than `v95`, because it closes the loop:

- propose witness
- verify witness cheaply
- decode patch exactly from witness

The important structural lesson is:

- overlap did not destroy local decoding
- it only inserted one extra dependency edge

## Status

Survivor.

Claim tier:

- `symbolic_state_compiler`

The result is still bounded and oracle-dependent in discovery.
But it is the strongest current software-shaped object in the repo.

## Next

- search the smallest exact repair-language grammar above this decoder graph
- or move to a richer bounded bug corpus and test whether the same decoder law
  survives
