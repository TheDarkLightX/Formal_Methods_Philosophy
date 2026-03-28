# v95: certificate-carrying repair basis

## Question

`v94` found the first software-engineering-shaped mainline survivor:

- dependency-aware obligation-fibered repair

That still searches over local fibers to identify the patch.

The next question is deeper:

> if the proposer carries a small local witness, can verification become much
> cheaper than dependency-aware search, and what is the smallest exact
> certificate basis on the same bounded patch corpora?

## Method

Bounded domain:

- the two `27`-patch corpora from `v94`
  - `separable_patch_family`
  - `overlap_patch_family`
- three local failure fibers:
  - `guard`
  - `bounds`
  - `transform`

For each patch, define its local observation certificate as the outputs of the
three fiber tests:

- `guard`
- `bounds`
- `transform`

Search all certificate bases over the three observation tokens:

- singletons
- pairs
- triples

The question is whether any smaller basis is exact.

The cost model is:

- certificate-carrying verification cost:
  - basis size
- compare against:
  - `v94` dependency-aware fiber-search average cost
  - `v94` monolithic patch-search average cost

## Main bounded result

The survivor is:

- certificate-carrying repair basis

On both patch corpora:

- no singleton basis is exact
- no pair basis is exact
- the unique minimal exact certificate basis is:
  - `guard`
  - `bounds`
  - `transform`

### Separable family

- minimal exact certificate size:
  - `3`
- certificate verification cost:
  - `3`
- `v94` dependency-aware search cost:
  - `9.0`
- `v94` monolithic search cost:
  - `39.0`

### Overlap family

- minimal exact certificate size:
  - `3`
- certificate verification cost:
  - `3`
- `v94` dependency-aware search cost:
  - `9.0`
- `v94` monolithic search cost:
  - `35.851851851851855`

So the new exact ladder on this bounded software corpus is:

- monolithic search:
  - about `36` to `39`
- dependency-aware fibered search:
  - `9`
- certificate-carrying verification:
  - `3`

## Why it matters

This is a real step beyond `v94`.

`v94` said:

- search over a dependency graph of repair fibers

`v95` says:

- once the proposer can carry a small exact witness, search over fibers can be
  replaced by direct local verification

That is exactly the same deep move that drove the verifier-compiler line:

- stop searching only for the object
- search for the smallest language in which the object becomes locally
  witnessable

On this bounded software corpus, the witness language has a clean exact lower
bound:

- three local observation tokens

## Status

Survivor.

This is still a bounded descriptive-oracle result.
It does not yet give a direct runtime repair compiler.
It does give the first exact software-engineering witness-language result in the
current main line.

## Next

- search the smallest exact repair-language grammar on top of the `v94` fiber
  graph and the `v95` witness basis
- or test whether the same certificate-carrying law survives on a richer
  bounded bug corpus
