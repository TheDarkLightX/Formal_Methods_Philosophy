---
title: "Energy-Based Optimizers and Telemetry"
layout: docs
kicker: Research log
description: "Evidence notes for using energy-based models as advisory optimizers in Tau and ZenoDEX: synthetic EBM training, real telemetry, ZenoEnergy verifier-call reduction, and fast-router timing."
date: 2026-05-17
---

## Abstract

This note records the evidence used for Tutorial 59.
The question is whether energy-based models can act as efficient optimizers for
structured formal-methods workloads.

The current answer is conditional.
For bounded candidate ranking, the evidence is strong enough to justify a
research pattern:

```text
generate candidates
rank by energy
verify deterministically
fall back if ranking misses
```

It is not a production authority claim.
The model may change candidate order.
It must not decide validity.

## 1. Assumptions

### Assumption A, bounded candidate set

The useful EBM setting is finite:

```text
C(x) = finite candidates for context x
```

If candidate generation is incomplete, the EBM can only rank the emitted
candidates.
It cannot recover candidates that were never generated.

### Assumption B, verifier authority

The EBM is advisory.
Validity comes from a semantic guard, replay, Tau parity check, certificate, or
deterministic verifier.

The safety rule is:

```text
LowEnergy(x,c) and VerifierRejects(x,c) -> reject
```

### Assumption C, telemetry labels

Training labels must come from measured or verified outcomes.
For Tau route optimization, the labels are route-profit telemetry.
For ZenoEnergy v0, the labels are synthetic candidate rows checked by the UPBA
v2 verifier.

Synthetic data can test method viability.
It cannot prove production distribution performance by itself.

## 2. External Framing

Logical Intelligence's article
[Energy-Based Models for Reasoning, LLMs for the Interface](https://logicalintelligence.com/blog/energy-based-models-for-reasoning)
frames energy-based reasoning as scoring intermediate states against constraints
and objectives.

The transfer used here is narrower:

```text
intermediate reasoning state -> candidate route or settlement certificate
energy -> advisory priority
constraint -> semantic guard or verifier obligation
objective -> speed, verifier-call reduction, or settlement objective
```

This keeps the model useful without giving it authority over formal validity.

## 3. Tau Route-Telemetry Evidence

The Tau route-telemetry chain has four experiments:

| Cycle | Corpus | Result | Boundary |
|---|---|---|---|
| v827 | synthetic Tau-like route costs | guarded EBM beat hand rule | synthetic oracle only |
| v828 | synthetic stress test | result survived small data and noisy labels | same synthetic oracle |
| v829 | small real route-profit audit | EBM lost to baseline | too little real data |
| v830 | expanded direct real receipts | EBM beat baseline on aggregate elapsed time | still regression-prone |

The synthetic result was strong:

| Policy | Accuracy | Invalid route rate | Mean regret |
|---|---:|---:|---:|
| hand rule, iid | `0.830333` | `0.0` | `0.125538` |
| unguarded EBM, iid | `0.926222` | `0.025667` | `1142.106698` |
| guarded EBM, iid | `0.949222` | `0.0` | `0.012427` |

The unguarded invalid-route rate is the key safety result.
The energy score needs a support mask.

The expanded real telemetry run had:

| Policy | Mean elapsed | Delta vs baseline | Mean regret | Regressions enabled |
|---|---:|---:|---:|---:|
| always baseline | `1534.561878 ms` | `0.0%` | `0.030701` | `0` |
| case-held-out EBM | `1517.503276 ms` | `+1.111627%` | `0.028217` | `6` |

Interpretation:

```text
telemetry improved the model
regression risk still blocks promotion
semantic support remains outside the EBM
```

## 4. ZenoEnergy v0 Evidence

ZenoEnergy v0 studies UPBA v2 partial-fill exact-in settlement candidate search.
It trains a small CPU-only energy ranker:

```text
features: 96
weights: 96
bias: 1
parameters: 97
model: linear pairwise-hinge energy scorer
```

The model ranks candidates before deterministic verifier checking.
It does not authorize settlement.

The main reported holdout result:

| Order | Winner-bearing batches | Mean verifier calls | Top-1 | Top-5 | Top-10 | Invalid accepts |
|---|---:|---:|---:|---:|---:|---:|
| exhaustive | `1,983` | `19.99` | `0.000` | `0.000` | `0.000` | `0` |
| random | `1,983` | `10.21` | `0.048` | `0.258` | `0.527` | `0` |
| hand energy | `1,983` | `1.36` | `0.763` | `0.996` | `1.000` | `0` |
| gap-weighted learned | `1,983` | `1.017` | `0.983` | `1.000` | `1.000` | `0` |

The reported cross-seed stress preserved the same pattern:

| Order | Configs | Top-1 mean | Top-1 min | Top-5 mean | Top-10 min | Mean calls | p99 max | Invalid accepts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| hand energy | `9` | `0.782` | `0.752` | `0.996` | `1.000` | `1.326` | `5` | `0` |
| learned linear | `9` | `0.982` | `0.964` | `0.999` | `1.000` | `1.026` | `2` | `0` |

The current preferred gap-weighted model audit reports:

```text
parameters: 97
feature_dim: 96
nonzero_weight_count: 38
reserved_nonzero_count: 0
forbidden_feature_names: none
```

The largest positive weights are verifier-shaped penalties.
The largest negative weights reward executed volume and surplus.

## 5. Local Replays

A small local replay of the ZenoEnergy benchmark used 200 synthetic batches with
20 requested candidates per batch.
It produced 198 winner-bearing batches.

| Order | Mean verifier calls | Top-1 | Top-5 | Top-10 | Invalid accepts | Permutation violations |
|---|---:|---:|---:|---:|---:|---:|
| exhaustive | `19.995` | `0.000` | `0.000` | `0.000` | `0` | `0` |
| random | `10.621` | `0.040` | `0.237` | `0.480` | `0` | `0` |
| hand energy | `1.359` | `0.778` | `0.990` | `1.000` | `0` | `0` |
| learned energy | `1.040` | `0.960` | `1.000` | `1.000` | `0` | `0` |
| hard-barrier hybrid | `1.040` | `0.960` | `1.000` | `1.000` | `0` | `0` |

Focused ZenoEnergy tests passed:

```text
24 passed
```

This replay is a sanity check, not a replacement for the larger reported
receipt.

## 6. ZenoDEX Fast-Router Evidence

The ZenoDEX fast quote router is not presented here as the trained ZenoEnergy
model.
It is evidence for the same optimizer architecture:

```text
cheap scalar score
bounded top-k frontier
exact integer replay
receipt verification
fallback
```

A local timing probe compared exhaustive routing to fast routing on synthetic
CPMM markets:

| Case | Two-hop pairs | Exact-in exhaustive | Fast exact-in | Speedup | Exact-out exhaustive | Fast exact-out | Speedup |
|---|---:|---:|---:|---:|---:|---:|---:|
| small | `640` | `113.703 ms` | `12.410 ms` | `9.16x` | `102.402 ms` | `90.893 ms` | `1.13x` |
| medium | `2,500` | `141.357 ms` | `14.630 ms` | `9.66x` | `142.738 ms` | `92.290 ms` | `1.55x` |
| large | `9,000` | `251.964 ms` | `20.675 ms` | `12.19x` | `293.650 ms` | `99.290 ms` | `2.96x` |

The fast route matched the exhaustive route's final amount in those measured
cases.
The focused fast-router tests passed:

```text
8 passed
```

Scope:

```text
tested synthetic markets only
heuristic top-k routing only
receipt verification still required
```

## 7. LLM Comparison Boundary

This note does not claim a direct benchmark against a specific LLM API.
LLM latency, price, and model behavior vary by provider, context length, and
deployment.

The supported comparison is structural:

| Task | Small EBM | LLM |
|---|---|---|
| Rank fixed numeric candidates | direct scalar scoring | requires serialization, generation, parsing, and verification |
| Preserve deterministic validity | no, verifier required | no, verifier required |
| Explain a result | limited | strong |
| Translate natural language into a formal request | limited | strong |
| Inner-loop top-k verifier scheduling | strong fit | usually inefficient |

The useful system design is:

```text
LLM for interface and proposal
EBM for cheap structured ranking
formal verifier for acceptance
```

## 8. Promotion Gate

A production candidate would need:

1. Exact candidate-domain definition or a certified generation boundary.
2. Proof or test evidence that ranking preserves candidate-set membership.
3. Deterministic fallback or a checked-stop certificate.
4. Zero invalid accepts under adversarial low-energy tests.
5. Held-out telemetry or replayed real workload evidence.
6. Regression budget stated before promotion.
7. Public replay receipts that rebuild without private data.

Current status:

```text
Tau EBM: telemetry-positive, regression-prone, not promoted
ZenoEnergy v0: strong synthetic verifier-call reduction, research-only
ZenoDEX fast router: useful bounded timing signal, advisory heuristic
```

## 9. Tutorial Link

Beginner-facing explanation:
[Energy-Based Models as Fast Optimizers]({{ '/tutorials/energy-based-models-as-fast-optimizers/' | relative_url }}).
