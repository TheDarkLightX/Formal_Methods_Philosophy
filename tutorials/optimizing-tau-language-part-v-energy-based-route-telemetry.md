---
title: "Optimizing Tau Language, Part V"
layout: docs
kicker: Tutorial 58
description: "Learn how an energy-based route model can help Tau choose profitable optimization paths, why the model needs telemetry, and why semantic guards still decide what is allowed."
---

This tutorial explains a research route selector for Tau Language that is useful
only inside a checked architecture.

The setting is route choice.
Tau receives a formula or command.
Several exact routes may be available:

```text
default qelim
BDD forgetting
Davis-Putnam CNF elimination
bitvector affine solving
safe-table preprocessing
fallback
```

A route can be legal and still unprofitable.
A route can be profitable on one family and slower on another family.
The learned model in this tutorial answers only the profitability question:

```text
If this route is semantically allowed, is it likely to be faster than fallback?
```

The semantic question stays outside the model:

```text
Is this route allowed for this Tau fragment?
```

That question still belongs to explicit guards, certificates, replay, or proof
checks.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Scope</p>
  <p>This tutorial explains a local experiment chain. Synthetic data showed that an energy-based model can learn a Tau-like routing policy. Existing real telemetry showed a small negative result first, then a larger positive-but-risky result after more receipts were harvested. This is evidence for telemetry-driven routing research, not a production Tau optimizer.</p>
</div>

## 1. The route problem

The previous Tau optimization tutorials used exact routes.
For example, Part I used guarded BDD existential abstraction for a supported
leading-existential propositional fragment.
Part IV used sparse impacted-factor solving for large conjunctions where a
small changed-variable set touches only a few factors.

Those optimizations follow a common pattern:

```text
Tau expression
-> semantic support guard
-> candidate route
-> validation or replay
-> fallback on failure
```

The missing piece is route profitability.
Even when a route preserves meaning, it may add overhead.
Validation can dominate the saved solver work.
Table preprocessing can help one family and regress another.
A global "enable every flag" policy can look good in aggregate while causing
many per-case regressions.

So a route selector needs two layers:

```text
semantic guard:    route is allowed
profit model:      route is worth trying
```

The energy-based model belongs only in the second layer.

## 2. What an energy-based model means here

An energy-based model, or EBM, assigns a scalar score to a candidate.
Lower energy means the model prefers that candidate.

For Tau routing, the candidate is a pair:

```text
(workload features, route option)
```

The experiment used a conditional discrete-route EBM:

$$
E_\theta(x,r)=-(\phi(x)\cdot w_r+b_r).
$$

Here:

- $x$ is a feature vector for the Tau-shaped workload,
- $r$ is a route,
- $\phi(x)$ is an expanded feature map,
- $w_r$ and $b_r$ are learned route parameters,
- lower $E_\theta(x,r)$ means the route looks more profitable.

Training uses a contrastive softmax:

$$
P(r\mid x)=
\frac{\exp(-E_\theta(x,r))}
{\sum_s \exp(-E_\theta(x,s))}.
$$

In plain terms, the model learns to put lower energy on the route that the
training oracle says is best.

## 3. Why the support mask is mandatory

The synthetic experiment tested two versions of inference.

Unguarded inference:

```text
choose argmin_r E_theta(x, r)
```

Guarded inference:

```text
choose argmin_r E_theta(x, r)
subject to Support(x, r) = true
```

The support mask is the semantic guard.
It says which routes are even legal for the fragment.

The synthetic experiment found:

| Split | Accuracy | Invalid route rate | Mean regret |
|---|---:|---:|---:|
| unguarded EBM, iid | `0.926222` | `0.025667` | `1142.106698` |
| guarded EBM, iid | `0.949222` | `0.0` | `0.012427` |
| hand rule, iid | `0.830333` | `0.0` | `0.125538` |

The lesson is direct.
The learned energy can rank routes.
It cannot replace the fragment guard.

## 4. Why telemetry is the critical resource

The first synthetic result was positive.
The stress test preserved the positive synthetic pattern: even with smaller
training sets and noisy labels, the guarded EBM usually beat the hand-coded rule
on the synthetic cost model.

But synthetic data is only a model of Tau.
The next experiment used existing real Tau route-profit telemetry.

Each measured row became a two-option decision:

```text
baseline Tau path
observed candidate route
```

The model was trained with leave-one-case-out evaluation.
On the small aggregate audit receipt, the result was negative:

| Policy | Mean elapsed | Delta vs baseline | Regressions enabled |
|---|---:|---:|---:|
| always baseline | `1346.258821 ms` | `0.0%` | `0` |
| raw EBM | `1347.626661 ms` | `-0.101603%` | `3` |
| thresholded EBM | `1360.262250 ms` | `-1.040174%` | `7` |

That negative result matters.
The synthetic result did not transfer automatically.
The model needed more real measurements.

The expanded harvest used direct benchmark receipts instead of the aggregate
audit:

```text
12 real-solver benchmark receipts
3 separator-profit sweep receipts
254 measured decisions
79 candidate speedups
117 candidate regressions
58 candidate neutrals
```

With that larger corpus, the case-held-out EBM showed a useful aggregate signal:

| Policy | Mean elapsed | Delta vs baseline | Mean regret | Regressions enabled |
|---|---:|---:|---:|---:|
| always baseline | `1534.561878 ms` | `0.0%` | `0.030701` | `0` |
| case-held-out EBM | `1517.503276 ms` | `+1.111627%` | `0.028217` | `6` |

The source-held-out EBM improved aggregate elapsed time more, but it enabled too
many regressions:

```text
source-held-out EBM delta:       +1.695707%
source-held-out regressions:     84
```

The value of telemetry data is visible:

1. Synthetic data showed the method can learn the route structure.
2. Small real telemetry rejected promotion.
3. Larger real telemetry produced a positive signal.
4. The regression count still blocks production promotion.

## 5. The optimizer architecture

The safe architecture is:

```text
Tau workload
-> exact semantic route guard
-> EBM profitability score
-> abstention threshold
-> candidate route
-> replay, certificate, or parity check
-> fallback on failure
```

In this architecture, the EBM may say:

```text
try this route
```

It may not say:

```text
this route is semantically valid
```

That distinction keeps the model useful without giving it authority over Tau
semantics.

## 6. A practical recipe

The evidence suggests a practical telemetry loop:

1. Record every route attempt with the route family, fragment guard result,
   validation result, baseline elapsed time, candidate elapsed time, and source
   workload family.
2. Label candidate routes as speedup, neutral, or regression under a stable
   threshold.
3. Train the EBM only on measured decisions whose semantic support was checked.
4. Evaluate with held-out workload families and held-out source receipts.
5. Promote only an abstaining policy that reduces aggregate elapsed time without
   enabling an unacceptable regression rate.
6. Keep fallback as the default.

In this tutorial's experiments, step 5 is not satisfied strongly enough for
production.
The result is a research direction with clear next data requirements.

## 7. What to remember

Energy-based route models are useful because Tau optimization is a structured
choice problem.
They become useful only when telemetry supplies enough examples of which routes
help and which routes regress.

The core equation is:

```text
safe learned optimizer =
semantic guard
+ telemetry-trained profit model
+ abstention
+ validation
+ fallback
```

The research log for this tutorial is:
[Energy-based route telemetry for Tau]({{ '/research/tau-energy-based-route-telemetry/' | relative_url }}).
