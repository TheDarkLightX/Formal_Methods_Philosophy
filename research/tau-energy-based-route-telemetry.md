---
title: "Energy-Based Route Telemetry for Tau"
layout: docs
kicker: Research log
description: "Synthetic and real-telemetry experiments testing whether an energy-based model can learn profitable Tau optimization routes while preserving explicit semantic guards."
date: 2026-05-17
---

## Abstract

This log records four experiments on energy-based route selection for Tau
Language optimization.

The question is whether an energy-based model, trained on route telemetry, can
help choose profitable Tau optimization routes.
The answer is conditional.
Synthetic data strongly supports the pattern.
Small real telemetry rejected promotion.
Expanded real telemetry produced a positive but risky signal.

The strongest current claim is:

> Given enough measured route telemetry, an EBM can help rank profitable Tau
> optimization routes, but semantic route guards, abstention, validation, and
> fallback remain mandatory.

This is not a production optimizer claim.
It is an evidence path for a telemetry-driven route selector.

## 1. Model

The route selector sees a workload $x$ and a route option $r$.
It assigns an energy:

$$
E_\theta(x,r)=-(\phi(x)\cdot w_r+b_r).
$$

Lower energy means the route is preferred.
Training uses the conditional distribution:

$$
P(r\mid x)=
\frac{\exp(-E_\theta(x,r))}
{\sum_s\exp(-E_\theta(x,s))}.
$$

For real telemetry, the route decision is binary:

```text
baseline Tau path
observed candidate route
```

The EBM is trained to prefer the option with lower measured elapsed time, after
classification parity has already been checked in the receipt.

## 2. Assumptions

### Assumption A, synthetic generator

The synthetic generator in `experiments/math_object_innovation_v827` is a toy
model of Tau route pressure.
It encodes fragment guards, BDD blowup pressure, Davis-Putnam resolvent
pressure, bitvector affine specialization, and table-revision specialization.

This assumption is useful for method development.
It cannot support a claim about real Tau workloads by itself.

### Assumption B, real telemetry labels

The real-telemetry experiments use existing benchmark receipts.
The labels are derived from measured elapsed time and classification parity.

This assumes the receipts are representative enough to test the route policy.
The expanded corpus is still retrospective and duplicate-heavy, so the
representativeness assumption remains weak.

### Assumption C, route support

The learned model decides profitability, not semantics.
Semantic support must be checked by exact guards or certificates before an EBM
score can matter.

## 3. Experiment ladder

| Cycle | Corpus | Result | Boundary |
|---|---|---|---|
| v827 | synthetic Tau-like route costs | guarded EBM beat hand rule | synthetic oracle only |
| v828 | synthetic stress test | result survived small data and noisy labels | same synthetic oracle |
| v829 | small real route-profit audit | EBM lost to baseline | too little real data |
| v830 | expanded direct real receipts | EBM beat baseline on aggregate elapsed time | still regression-prone |

## 4. v827, synthetic EBM

Cycle v827 trained a conditional discrete-route EBM on generated Tau-like
formula features.
Routes were:

```text
default_qelim
bdd_forget
dp_cnf
bv_affine
table_rr
fallback
```

The synthetic oracle assigned hidden route costs and explicit support masks.

Main result:

| Policy | Accuracy | Invalid route rate | Mean regret |
|---|---:|---:|---:|
| hand rule, iid | `0.830333` | `0.0` | `0.125538` |
| unguarded EBM, iid | `0.926222` | `0.025667` | `1142.106698` |
| guarded EBM, iid | `0.949222` | `0.0` | `0.012427` |
| hand rule, shifted | `0.827800` | `0.0` | `0.134149` |
| guarded EBM, shifted | `0.946200` | `0.0` | `0.015403` |

The unguarded invalid-route rate is the main safety datum.
The model can learn route preference, but the support mask is necessary.

Receipt:

```text
experiments/math_object_innovation_v827/generated/report.json
```

## 5. v828, synthetic stress test

Cycle v828 varied training set size and injected supported-route label noise.

The expanded synthetic result:

```text
configs:                                      11
all guarded invalid-route rates:              0.0
first clean train size beating hand rule:      500
best clean iid mean regret:                    0.011004
best noisy iid mean regret:                    0.010090
hand-rule iid mean regret:                     0.123299
```

The stress result says that the EBM pattern is learnable and data-efficient in
the toy route-cost model.
It still depends on the synthetic oracle.

Receipt:

```text
experiments/math_object_innovation_v828/generated/report.json
```

## 6. v829, small real-telemetry pilot

Cycle v829 used the existing aggregate route-profit audit receipt:

```text
TauLang-Experiments/results/local/route-profit-audit.json
```

The usable corpus had:

```text
decisions:              56
case groups:            18
candidate speedups:     13
candidate regressions:  28
candidate neutrals:     15
```

Result:

| Policy | Mean elapsed | Delta vs baseline | Regressions enabled |
|---|---:|---:|---:|
| always baseline | `1346.258821 ms` | `0.0%` | `0` |
| raw EBM | `1347.626661 ms` | `-0.101603%` | `3` |
| thresholded EBM | `1360.262250 ms` | `-1.040174%` | `7` |

This is negative evidence.
The synthetic result did not transfer with only the small audit receipt.
The threshold overfit the tiny leave-one-case-out folds and made the result
worse.

Receipt:

```text
experiments/math_object_innovation_v829/generated/report.json
```

## 7. v830, expanded real-telemetry harvest

Cycle v830 harvested direct benchmark receipts instead of the aggregate audit.
It excluded route-profit audit files to avoid double-counting their source
observations.

Inputs:

```text
12 real-solver-spec-benchmarks-v1 receipts
3 separator-profit-sweep-v1 receipts
```

Corpus:

```text
decisions:              254
case groups:             18
source receipts:         15
candidate speedups:      79
candidate regressions:  117
candidate neutrals:      58
```

Leave-one-case-out EBM:

| Metric | Value |
|---|---:|
| mean elapsed | `1517.503276 ms` |
| baseline mean elapsed | `1534.561878 ms` |
| aggregate delta vs baseline | `+1.111627%` |
| mean regret | `0.028217` |
| baseline mean regret | `0.030701` |
| captured speedups | `15 / 79` |
| regressions enabled | `6` |

Leave-one-source-out EBM:

| Metric | Value |
|---|---:|
| mean elapsed | `1508.540201 ms` |
| aggregate delta vs baseline | `+1.695707%` |
| captured speedups | `60 / 79` |
| regressions enabled | `84` |
| mean regret | `0.047431` |

The case-held-out result is the useful signal.
The source-held-out result improves aggregate elapsed time but enables too many
regressions.

Receipt:

```text
experiments/math_object_innovation_v830/generated/report.json
```

## 8. Interpretation

The experiment chain supports three claims.

First, EBM route selection is structurally plausible for Tau optimization.
The synthetic model is easy for the EBM to learn, and the learned model beats a
hand-coded heuristic when guarded.

Second, telemetry data is the limiting resource.
The small real audit was not enough.
The expanded direct harvest produced a positive aggregate signal.

Third, profitability prediction must be fail-closed.
The source-held-out screen shows that an EBM can buy aggregate speed while
enabling many regressions.
That is not an acceptable production policy.

## 9. Promotion Gate

A future promotion candidate should satisfy all of the following:

1. Semantic support is checked independently of the EBM.
2. The route policy can abstain.
3. Held-out workload-family evaluation improves aggregate elapsed time.
4. Regression-enabled count is below a stated budget.
5. Fresh benchmark runs reproduce the result.
6. Tau output parity or certificate checks pass on every enabled route.

The current v830 result satisfies part of item 3.
It does not satisfy item 4 strongly enough.

## 10. Next Telemetry

The next useful telemetry corpus should record:

- route family,
- exact fragment guard result,
- validation or certificate result,
- baseline elapsed time,
- candidate elapsed time,
- parse and normalization time,
- solver time,
- route overhead,
- source workload family,
- changed-variable or support-locality features where relevant.

This data would let the EBM learn when the route itself is fast and when route
overhead dominates.

The practical research message is:

```text
telemetry is the training set for optimizer judgment
```

Without telemetry, the EBM is only a synthetic demonstration.
With enough telemetry, it becomes a candidate profit oracle inside a guarded
Tau optimizer.

