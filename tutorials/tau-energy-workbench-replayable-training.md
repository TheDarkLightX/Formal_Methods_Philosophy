---
title: "TauEnergy Workbench: Replayable Training"
layout: docs
kicker: Tutorial 60
description: "Learn how the TauEnergy workbench turns Tau-checked formulas into measured route labels, trains an advisory energy ranker, and publishes a license-safe replayable demo."
---

This tutorial explains the replayable TauEnergy workbench.

The goal is narrow:

```text
learn a better order for checking Tau optimizer routes
```

Tau, deterministic route certificates, or fallback checks determine route validity, rather than the learned model.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Scope</p>
  <p>This tutorial explains an independent research demo in the TauLang-Experiments repository. It does not represent an official Tau feature, a production optimizer, or a license grant for Tau Language. The public demo publishes metrics only. Readers must obtain Tau from the official source before replaying the experiment.</p>
</div>

## 1. The simple picture

Imagine a solver with several possible routes:

```text
default route
read-once structural route
small truth-table route
Tseitin SAT cross-check route
ordered-BDD route
Tau fallback route
```

Several routes may be semantically safe for a given formula.
One route may be faster on a read-once formula.
Another may be better on an ordered-BDD-shaped formula.
Fallback may be safest when the formula is outside the supported fragment.

TauEnergy learns this kind of preference:

```text
For this checked formula shape, which route should be checked first?
```

The workbench keeps a separate authority rule:

```text
low energy + checker rejects -> reject
low energy + checker accepts -> candidate route may be used
```

The score determines search order without affecting validity.

## 2. The roles

The workbench has four roles.

```text
LLM interface
```

The language model can explain the experiment, propose a candidate route family,
or help turn a question into structured work.

```text
TauEnergy
```

TauEnergy is an energy ranker.
It scores structured route candidates.
Lower energy means "check this earlier."

```text
WES-style schedule
```

WES means the checker order is treated as a search schedule.
If the ranker is good, the schedule reaches the best valid route faster.

```text
Tau and route certificates
```

Tau checks syntax and formula status.
Route-specific deterministic checks compare candidate route results against
Tau status or a certificate.

## 3. The training pipeline

The measured training pipeline is:

```text
generate or load Tau-shaped formula
-> run Tau syntax/status check
-> run candidate route checks
-> keep routes whose result matches Tau
-> label the fastest valid route
-> train TauEnergy to rank that route first
-> evaluate on held-out formulas
```

The label is measured from checked routes rather than manual estimation.

The important fields in a report are:

```text
failed_check_count
invalid_accept_count
fitted_eval_test.top1_oracle_route_rate
hand_eval_test.top1_oracle_route_rate
mean_calls_to_oracle
family_holdout
```

The first two fields are gates.
If either one is nonzero, the report does not support the tutorial claim.

## 4. The replay command

The experiment repository has a license-aware replay wrapper:

```bash
./scripts/run_tau_energy_training_demo.sh --accept-tau-license --quick
```

The larger replay is:

```bash
./scripts/run_tau_energy_training_demo.sh --accept-tau-license --full
```

That wrapper:

1. obtains Tau from the official IDNI repository,
2. applies the local research patches,
3. builds Tau locally,
4. runs the optimizer workbench,
5. trains the measured route ranker,
6. runs stress checks,
7. runs the ordered-BDD curriculum,
8. builds a public metrics-only snapshot.

The generated local reports live under:

```text
results/local/tau-energy/
```

The public website reads a smaller JSON summary:

```text
docs/assets/tau-energy-demo-summary.json
```

That summary is designed for publication and excludes Tau source, Tau binaries, full formulas, local paths, or full receipts.

## 5. The current result

The current public snapshot reports:

```text
genuine optimization route: indexed_impacted_factor_solve
solver-call reduction: 8.0x
measured training top-1: 0.921569
ordered-BDD best top-1: 0.9375
invalid accepts: 0
```

This bounded workbench result indicates that the route ranker learned useful ordering on the checked corpus, without recommending that upstream Tau enable the route by default.

## 6. Why ordered-BDD needed its own curriculum

The stress report exposed a weak family:

```text
ordered-BDD holdout
```

This indicates that a model trained on other families did not reliably rank the
ordered-BDD route first when the entire ordered-BDD family was held out.

The targeted curriculum then asked:

```text
How many measured ordered-BDD examples improve held-out ordered-BDD routing?
```

The result:

```text
zero targeted BDD examples: 0.90625 top-1
32 targeted BDD examples: 0.9375 top-1
invalid accepts: 0
```

This is a useful lesson about training data.
The next examples should target route-family weakness first. Adding generic
formulas can come after the weak family is covered.

## 7. What can Tau developers do with this?

Tau developers can use the workbench as a route-design loop:

```text
propose a route family
-> define its semantic guard
-> build deterministic checks or certificates
-> generate Tau-checked examples
-> measure route profit
-> train advisory ordering
-> stress by seed and formula family
-> promote only after the checker gates pass
```

This is useful for:

- finding fragment-specific optimizations,
- discovering where a hand-coded heuristic is too broad,
- detecting route families that need more examples,
- comparing fallback, hand rules, and learned routing,
- turning failed route predictions into new training curricula.

The workbench is also useful when it recommends against promotion.
Negative route telemetry can block a tempting optimization before it becomes a
default behavior.

## 8. Assumptions and stress tests

### Assumption A, formulas are representative

The synthetic formulas and small real-spec examples may not represent all Tau
workloads.

Stress test:

```text
hold out whole formula families
add more real Tau benchmark commands
track weakest-family top-1
```

### Assumption B, measured labels are stable

A route can look profitable on one machine or Tau version and regress later.

Stress test:

```text
record Tau grammar hashes
rerun after Tau syntax or solver changes
compare reports across seeds and source corpora
```

### Assumption C, ranker features are sufficient

The current ranker is small.
It can miss a route family if the features do not expose the relevant shape.

Stress test:

```text
mine misranked examples
add fragment-specific features
compare against hand rules and fallback
```

## 9. What to remember

TauEnergy is useful because it turns route choice into a checked learning
problem:

```text
measure first
learn route order second
verify always
fallback on failure
```

The model reduces search cost without validating routes.

Related tutorials:

- [Optimizing Tau Language, Part V]({{ '/tutorials/optimizing-tau-language-part-v-energy-based-route-telemetry/' | relative_url }})
- [Energy-Based Models as Fast Optimizers]({{ '/tutorials/energy-based-models-as-fast-optimizers/' | relative_url }})
- [TauEnergy Chat and World-Model Architecture]({{ '/tutorials/tau-energy-chat-and-world-model-architecture/' | relative_url }})
