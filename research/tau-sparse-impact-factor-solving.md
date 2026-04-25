---
title: "Sparse Impacted-Factor Solving in Tau"
layout: docs
kicker: Research log
description: "Evidence, falsifications, patch instructions, and reproducible demo for the sparse impacted-factor optimization experiment in Tau Language."
date: 2026-04-24
---

## Abstract

This note records the evidence behind Tutorial 52. The supported result is a
fragment-sensitive optimization for sparse top-level conjunctions in a patched
latest-Tau checkout. On the checked v768 sparse benchmark corpus, the indexed
factor-solve hook measured an `8.446x` median in-process speedup. The matching
v769 factor-cache experiment measured a `9.6x` median cache reuse ratio.

The result is not a global Tau speed theorem. It does not promote a default
route selector. It says that when a formula is a large conjunction and a small
changed-variable set touches only a few factors, support indexing can avoid
unrelated factor work.

## Model

Let

$$
F=\bigwedge_{i=1}^{n}F_i.
$$

For each factor, define:

$$
E_i=\operatorname{supp}(F_i).
$$

For changed variables $D$, the impacted factor index set is:

$$
I_D=\{i:E_i\cap D\neq\varnothing\}.
$$

The reusable factor index set is:

$$
R_D=\{i:E_i\cap D=\varnothing\}.
$$

The sparse-impact fragment is the case where:

$$
|I_D|\ll n.
$$

The patched hook builds a variable-to-factor index and compares:

```text
full factor path     : solve all top-level factors
indexed factor path  : solve factors in I_D
```

The hook also checks that scan-selected and index-selected impacted factors
agree on the measured cases.

## Confirmed Results

### v768 indexed factor solve

| Metric | Value |
|---|---:|
| sparse benchmark cases | `3` |
| median in-process solver speedup | `8.446x` |
| minimum in-process solver speedup | `7.116x` |
| maximum in-process solver speedup | `30.803x` |
| index selection parity | passed |
| solver errors | `0` |

Claim tier: `symbolic_state_compiler`.

Non-claim: this is not a default latest-Tau optimizer and not arbitrary Tau
formula acceleration.

### v769 factor-cache shape

| Metric | Value |
|---|---:|
| median cache reuse ratio | `9.6x` |
| minimum cache reuse ratio | `8.0x` |
| maximum cache reuse ratio | `32.0x` |
| second-run recomputed factors | `3, 5, 3` |
| second-run reused factors | `21, 43, 93` |
| validation mismatches | `0` |

This shows why the optimization matters for incremental workloads: unchanged
factors can be reused rather than recomputed.

## Route-Selector Falsifications

The route selector is not solved. The experiments after v769 deliberately
tried to break simple guard ideas.

| Cycle | Result |
|---|---|
| v772 | Loose half-impact guards were falsified on broader threshold search. |
| v782 | Margin widening recovered positives but introduced a holdout false positive. |
| v784 | Source telemetry worked, but sidecar/source feature correspondence was false. |
| v785 | Source-only scalar postfilters failed to produce a promoted guard. |
| v786 | Distribution thresholds fixed calibration but failed holdout. |
| v787 | Five-repeat labels still produced `12` gray-zone rows and `5` threshold crossings. |
| v788 | Support-component-only rules found no calibration-safe rejector or acceptor. |

The v788 support graph result is especially instructive:

```text
all-support component counts: [1]
residual-support component counts: [6, 7]
residual-support edge densities: [0]
```

Interpretation:

- All impacted factors connect through the changed variable bridge `d0`.
- After removing changed variables, residual supports are disconnected in this
  generated corpus.
- Component count alone does not explain the remaining stable false positive
  or stable false negative.

## Reproduction

The repository includes a patch artifact, a demo runner, and the generated
Tau spec:

- [Tau source patch]({{ '/patches/tau/indexed-factor-sparse-impact-demo.patch' | relative_url }}):
  `patches/tau/indexed-factor-sparse-impact-demo.patch`
- [Demo runner]({{ '/scripts/run_tau_sparse_impact_demo.py' | relative_url }}):
  `scripts/run_tau_sparse_impact_demo.py`
- [Generated Tau spec]({{ '/examples/tau/sparse_impact_factor_speedup_demo.tau' | relative_url }}):
  `examples/tau/sparse_impact_factor_speedup_demo.tau`

Run the demo against a Tau checkout:

```bash
python3 scripts/run_tau_sparse_impact_demo.py --tau-checkout /path/to/tau-lang-latest
```

The script:

1. applies the patch if needed,
2. builds `build-Release/tau`,
3. writes the generated demo solve command,
4. runs Tau with `TAU_INDEXED_FACTOR_SOLVE_STATS=1`,
5. writes `results/tau_sparse_impact_demo_report.json`.

The demo formula has:

```text
24 top-level factors
3 factors impacted by d0
21 factors reusable by the sparse-impact model
```

On one local patched checkout, two smoke runs reported:

```text
min speedup:    38.077x
median speedup: 41.1025x
max speedup:    44.128x
```

These smoke numbers are not the research claim. They are a convenient local
way to check that the patch and telemetry are functioning. The research claim
remains the checked v768 benchmark median, `8.446x`.

## Patch Boundary

The patch is intended for the latest-Tau source shape used in the experiments.
If `git apply --check` fails, the checkout may already be patched or may have
drifted from the expected source. In that case, inspect the patch manually
before applying it.

The patch is feature-gated. The demo route is active only when the relevant
environment variables are set:

```bash
TAU_INDEXED_FACTOR_SOLVE_STATS=1
TAU_INDEXED_FACTOR_PROFIT_STATS=1
TAU_INDEXED_IMPACT_DELTA=d0
TAU_INDEXED_FACTOR_SOLVE_ORDER=full_first
```

Without those flags, ordinary Tau execution should not emit the indexed-factor
diagnostic lines.

## Next Frontier

The next useful research step is not another scalar threshold. The current
evidence points to a richer route object:

```text
support components
+ changed-occurrence distribution
+ operator mix per component
+ stabilized labels
+ forced fallback for gray-zone cases
```

That route should be promoted only if it improves holdout behavior without
introducing false positives.
