---
title: "Energy-Based Models as Fast Optimizers"
layout: docs
kicker: Tutorial 59
description: "Learn how small energy-based models rank bounded candidate sets, why they can be cheaper than token-generation loops for numeric ranking workloads, and how Tau and ZenoDEX keep verification separate from learned scoring."
---

Energy-based models are useful when the problem has this shape:

```text
finite candidate set
structured features for each candidate
one scalar score per candidate
cheap verifier or certificate check after ranking
fallback if the scorer misses
```

That shape appears in Tau Language optimization and in ZenoDEX routing and
settlement search.

An LLM is useful at the boundary of this system.
It can explain a policy, translate a human request into structured inputs, or
propose candidate families.
The inner loop has a narrower job.
When the task is to rank many already-structured candidates, a small
energy model can do the job with a few arithmetic operations per candidate.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Scope</p>
  <p>This page explains a research pattern. The strongest ZenoEnergy result is synthetic and verifier-labeled. The Tau result is telemetry-driven but not production-promoted. The ZenoDEX fast-router timing probe is local and bounded. The safe claim is that EBMs can be useful advisory optimizers for some structured ranking tasks when exact guards, certificates, and fallback remain in charge.</p>
</div>

## 1. What an EBM does

An energy-based model assigns one number to a candidate:

$$
E_\theta(x,c) \in \mathbb{R}.
$$

Here:

- $x$ is the current problem context,
- $c$ is a candidate action, route, proof step, or settlement certificate,
- lower energy means the candidate should be checked earlier.

For a bounded candidate set $C(x)$, inference is simple:

```text
score every candidate
sort by energy
check candidates in that order
accept only through the verifier
```

The model changes search order.
It does not change the definition of validity.

The useful safety law is:

```text
low energy + verifier rejects -> reject
```

The verifier remains the authority.

## 2. Why this is efficient

An EBM for this kind of ranking can be compact.
The ZenoEnergy v0 settlement-search model uses:

```text
96 input features
96 learned weights
1 bias
97 total parameters
```

Its score is:

$$
E_\theta(x,c)=w\cdot \phi(x,c)+b.
$$

That is a dot product.
For 20 candidates, the model does roughly 20 small dot products and a sort.
There is no token generation, no natural-language parsing step, and no sampling
loop.

An LLM can still be the right tool for:

- explaining the result,
- generating a candidate family,
- translating natural language into a formal request,
- writing a proof sketch for a human to inspect.

For the bounded ranking loop itself, the EBM is a direct machine.

## 3. ZenoEnergy v0

ZenoEnergy v0 studies UPBA v2 partial-fill exact-in settlement search.
The setting is:

```text
settlement context x
finite candidate certificates C(x)
deterministic verifier V_x(c)
deterministic objective J_x(c)
```

The exhaustive winner is:

```text
c*(x) = best verified candidate in C(x)
```

The learned energy model tries to place $c*(x)$ early in the verifier order.
It is trained by pairwise hinge updates:

$$
\max(0, m + E_\theta(x,c_{good}) - E_\theta(x,c_{bad})).
$$

The reported gap-weighted checkpoint uses a 97-parameter linear ranker.
On the 2,000-batch synthetic holdout reported by the ZenoEnergy v0 paper:

| Order | Winner-bearing batches | Mean verifier calls | Top-1 | Top-5 | Top-10 | Invalid accepts |
|---|---:|---:|---:|---:|---:|---:|
| exhaustive | `1,983` | `19.99` | `0.000` | `0.000` | `0.000` | `0` |
| random | `1,983` | `10.21` | `0.048` | `0.258` | `0.527` | `0` |
| hand energy | `1,983` | `1.36` | `0.763` | `0.996` | `1.000` | `0` |
| learned energy | `1,983` | `1.017` | `0.983` | `1.000` | `1.000` | `0` |

The central metric is verifier calls.
The learned model usually puts the winner first.
When it misses, deterministic fallback can still check the remaining candidates.

A small local replay with 200 batches gave the same pattern:

```text
winner-bearing batches: 198
learned mean verifier calls: 1.040
learned top-5 recall: 1.000
learned top-10 recall: 1.000
invalid accepts: 0
energy tests: 24 passed
```

This is the efficiency win:

```text
same verifier
same fallback boundary
much shorter expected path to the winner
```

On this bounded synthetic distribution, the model moves the verifier's likely
winner from position about 20 to position about 1.

## 4. What the model learned

The model audit is interpretable.
Large positive weights raise energy and push a candidate later.
The strongest positive weights are verifier-shaped penalties:

```text
negative reserve flag
CPMM invariant violation flag
limit-price violation count
balance violation count
```

Large negative weights lower energy and pull a candidate earlier.
The strongest negative weights reward objective quality:

```text
executed volume
surplus
volume log feature
signed surplus feature
```

That is the intended behavior.
Hard invalidity indicators stay expensive.
High-volume, high-surplus candidates that pass hard screens move earlier.

## 5. The ZenoDEX paper boundary

The ZenoDEX full-system paper frames the public execution core around bounded
candidate families and total keys:

$$
\Winner(C) := \argmin_{c \in C} \Key(c).
$$

The appendix gives the operational skeleton:

```text
emit a bounded candidate family
compute the explicit key for each candidate
select the winner
build the route certificate or packet
expose the result as canonical only when the guarded packet verifies
```

This is a natural place for an energy model.
It can change the order in which candidates are inspected.
Canonical acceptance still comes from the key, certificate, verifier, or
fallback path.

The Lean-side contract behind ZenoEnergy says the same thing in proof language:

```text
if ranked_order is a permutation of exact_candidates,
then full fallback preserves the same audited weak-optimality surface.
```

Ranking is advisory.
Permutation plus fallback is the safety boundary.

## 6. ZenoDEX fast routing as an energy pattern

The ZenoDEX fast quote router uses the same architectural idea even where the
local code calls the score an approximation instead of a learned energy.

For exact-in routing:

```text
energy(candidate route) = - approximate output amount
```

For exact-out routing:

```text
energy(candidate route) = approximate input amount
```

The router scores many two-hop candidate pairs cheaply, keeps a small top-k
frontier, then replays those candidates with deterministic integer swap math.
Receipt verification remains the safety gate.

A local timing probe over synthetic CPMM markets measured:

| Case | Two-hop pairs | Exact-in exhaustive | Fast exact-in | Speedup | Exact-out exhaustive | Fast exact-out | Speedup |
|---|---:|---:|---:|---:|---:|---:|---:|
| small | `640` | `113.703 ms` | `12.410 ms` | `9.16x` | `102.402 ms` | `90.893 ms` | `1.13x` |
| medium | `2,500` | `141.357 ms` | `14.630 ms` | `9.66x` | `142.738 ms` | `92.290 ms` | `1.55x` |
| large | `9,000` | `251.964 ms` | `20.675 ms` | `12.19x` | `293.650 ms` | `99.290 ms` | `2.96x` |

In this probe, the fast route matched the exhaustive route's final amount in
all listed cases.
The focused fast-router test file also passed:

```text
8 passed
```

The scoped claim is narrow.
This timing probe supports the value of cheap scoring plus exact replay on the
tested synthetic markets.
It does not prove global optimality for every live route universe.

## 7. How this helps Tau Language

Tau optimization has the same candidate-ranking shape.
For one Tau workload, several semantically legal routes may exist:

```text
default qelim
BDD forgetting
Davis-Putnam CNF elimination
bitvector affine solving
safe-table preprocessing
fallback
```

The semantic guard decides which routes are allowed.
The EBM ranks only the allowed routes by expected profitability.

The route selector should look like:

```text
Tau workload
-> exact route support guard
-> telemetry-trained energy score
-> abstention threshold
-> candidate route
-> replay, certificate, or parity check
-> fallback on failure
```

The previous Tau EBM tutorial measured this on synthetic and real telemetry.
The expanded real telemetry run had:

```text
decisions: 254
case-held-out EBM aggregate elapsed delta: +1.111627%
regressions enabled: 6
```

That is useful evidence, but not enough for production promotion.
The value of telemetry is that it supplies the labels the EBM needs:

```text
route was allowed
route preserved output
route was faster or slower than fallback
route overhead dominated or did not dominate
```

Without telemetry, the model is a toy demonstration.
With enough checked telemetry, it becomes a candidate optimizer inside a
guarded Tau route selector.

## 8. Where LLMs still fit

The clean division is:

```text
LLM: propose, explain, translate, summarize, help design candidate families
EBM: score structured candidates cheaply
Verifier: decide validity
Tau or ZenoDEX guard: enforce the semantic boundary
```

For bounded numeric or symbolic candidate ordering, asking an LLM to rank every
candidate is usually an inefficient inner loop.
The data is already structured.
The scoring target is scalar.
The verifier is deterministic.

The EBM should handle that ranking job.
The LLM can remain the interface and research assistant around it.

## 9. What to remember

An energy model is valuable when it is placed between generation and
verification:

```text
candidate generation
-> EBM ranking
-> deterministic verifier
-> certificate or fallback
```

The model can cut verifier work sharply on the right task.
It cannot replace the verifier.

The research companion for this page is:
[Energy-based optimizers and telemetry]({{ '/research/energy-based-optimizers-and-telemetry/' | relative_url }}).

Related Tau tutorial:
[Optimizing Tau Language, Part V]({{ '/tutorials/optimizing-tau-language-part-v-energy-based-route-telemetry/' | relative_url }}).
