---
title: "Optimizing Tau Language, Part IV"
layout: docs
kicker: Tutorial 52
description: "A careful guide to the sparse impacted-factor optimization in Tau Language, the support-locality math behind it, the measured speedup, and the current route-selector boundary."
---

This tutorial covers one real Tau Language optimization result and the boundary
around it.

The confirmed claim is narrow:

```text
On checked sparse impacted-factor benchmark cases, a patched latest-Tau
indexed factor-solve hook measured an 8.446x median in-process speedup.
```

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Scope</p>
  <p>This is a community research experiment against a patched latest-Tau checkout. It is not an official upstream Tau feature, not a global speed theorem, and not a production route selector.</p>
</div>

## The Shape

Start with a formula that factors as a top-level conjunction:

$$
F = F_1 \wedge F_2 \wedge \cdots \wedge F_n.
$$

Each factor has a support set:

$$
\operatorname{supp}(F_i)
=
\{v : v \text{ occurs in } F_i\}.
$$

Let $D$ be the set of changed variables. In the experiments, $D$ was often
the singleton set $\{d0\}$. The impacted factors are:

$$
I_D
=
\{i : \operatorname{supp}(F_i)\cap D\neq\varnothing\}.
$$

The sparse-impact condition is:

$$
|I_D| \ll n.
$$

In plain language, the formula may be large, but the current update only
touches a few top-level factors.

This is not the same as a small formula. A small formula may have no useful
structure. A large conjunction can be cheap to update if most factors are
unaffected.

## The Indexed Route

The direct route scans or solves every top-level factor.

The indexed route builds an index:

```text
variable -> factor ids that mention the variable
```

Then a changed-variable set selects the impacted factors:

```text
changed variables -> impacted factor ids -> solve only impacted factors
```

The benchmark hook compares two internal paths:

```text
full factor pass     : solve every top-level factor
indexed factor pass  : solve only factors selected by the support index
```

The checked optimization is about this internal factor work. It is strongest
for repeated or incremental workloads, where unimpacted factor results can be
reused instead of recomputed.

## Measured Evidence

The v768 experiment measured the indexed factor-solve hook on a patched
latest-Tau checkout.

| Metric | Value |
|---|---:|
| sparse benchmark cases | `3` |
| median in-process solver speedup | `8.446x` |
| minimum in-process solver speedup | `7.116x` |
| maximum in-process solver speedup | `30.803x` |
| indexed result parity check | passed |
| solver errors | `0` |

The v769 experiment tested the matching cache-reuse shape.

| Metric | Value |
|---|---:|
| median cache reuse ratio | `9.6x` |
| minimum cache reuse ratio | `8.0x` |
| maximum cache reuse ratio | `32.0x` |
| second-run recomputed factors | `3, 5, 3` |
| second-run reused factors | `21, 43, 93` |
| validation mismatches | `0` |

These are meaningful numbers, but they are fragment evidence. They do not say
that arbitrary formulas, one-shot command-line calls, or every Tau qelim input
will speed up.

## Why It Works

A useful first-order work estimate is:

$$
\rho_D
=
\frac{|I_D|}{n}.
$$

If $\rho_D$ is small, the indexed route has a chance to win. In the demo
spec, there are $24$ factors and $3$ impacted factors, so:

$$
\rho_{\{d0\}}
=
\frac{3}{24}
=
\frac{1}{8}.
$$

The support-mass ratio is a second estimate:

$$
\sigma_D
=
\frac{\sum_{i\in I_D}|\operatorname{supp}(F_i)|}
       {\sum_{i=1}^{n}|\operatorname{supp}(F_i)|}.
$$

The term-mass ratio is a third estimate:

$$
\tau_D
=
\frac{\sum_{i\in I_D}\operatorname{size}(F_i)}
       {\sum_{i=1}^{n}\operatorname{size}(F_i)}.
$$

These ratios are only proxies. The real cost depends on the solver work behind
each factor. That is why later experiments measured actual full-first impacted
cost instead of trusting factor count alone.

## The Quantifier-Elimination Connection

The quantifier-elimination tutorial used this law:

$$
\exists x.\,(A\wedge B)
\equiv
A\wedge \exists x.\,B
\qquad
\text{when }x\notin FV(A).
$$

The side condition is the point. If $A$ does not mention $x$, eliminating
$x$ should not enter $A$.

The sparse factor-solve route uses the same support-locality idea:

$$
D\cap\operatorname{supp}(F_i)=\varnothing
\quad\Longrightarrow\quad
F_i\text{ is not impacted by the update over }D.
$$

That does not by itself prove a complete qelim optimizer. It gives a route
shape:

1. Factor the formula.
2. Compute support sets.
3. Find the component touched by the quantified or changed variables.
4. Run the expensive operation only inside that component.
5. Reattach untouched factors.
6. Fall back if the guard cannot certify the fragment.

The guard is part of the mathematics. Without it, a fast route is just a guess.

## The Support Hypergraph

The support hypergraph is the object behind the optimization.

Variables are vertices:

$$
V = \{x_1,\ldots,x_m\}.
$$

Each factor contributes a hyperedge:

$$
E_i=\operatorname{supp}(F_i).
$$

The impacted region for $D$ is:

$$
\operatorname{Impact}(D)
=
\{F_i : E_i\cap D\neq\varnothing\}.
$$

The reusable region is:

$$
\operatorname{Reuse}(D)
=
\{F_i : E_i\cap D=\varnothing\}.
$$

This hypergraph view is better than a single scalar threshold because it keeps
the dependency structure visible.

## Why The Route Selector Is Still Open

An optimizer needs to decide when the indexed route should be used. That is
harder than detecting that some factors are impacted.

The follow-up experiments found several boundaries:

| Experiment | What happened |
|---|---|
| v770 | A simple profit guard looked promising on a small corpus. |
| v772 | A broader threshold search falsified a loose half-impact guard. |
| v782 | Margin widening recovered positives but introduced a holdout false positive. |
| v784 | Source telemetry worked, but sidecar/source feature correspondence was false. |
| v785 | Source-only scalar postfilters failed to produce a promoted guard. |
| v786 | Per-factor distribution thresholds repaired calibration but failed holdout. |
| v787 | Five-repeat labels still left `12` gray-zone rows and `5` threshold crossings. |
| v788 | Support-component-only guards found no safe calibration rule. |

This is real negative knowledge. It says the automatic route selector should
not be promoted yet.

The most important v787 lesson is that timing labels near the boundary are not
stable enough for naive training. A route selector needs a gray-zone policy:

```text
stable positive -> candidate training signal
stable negative -> candidate rejection signal
gray zone       -> quarantine, retest, or force fallback
```

## Try The Demo

The repo includes a local demo that patches a Tau checkout, writes a generated
demo spec, rebuilds Tau, and runs the sparse impacted-factor measurement:

```bash
python3 scripts/run_tau_sparse_impact_demo.py --tau-checkout /path/to/tau-lang-latest
```

Demo artifacts:

- [Demo runner]({{ '/scripts/run_tau_sparse_impact_demo.py' | relative_url }}):
  `scripts/run_tau_sparse_impact_demo.py`
- [Tau source patch]({{ '/patches/tau/indexed-factor-sparse-impact-demo.patch' | relative_url }}):
  `patches/tau/indexed-factor-sparse-impact-demo.patch`
- [Generated Tau spec]({{ '/examples/tau/sparse_impact_factor_speedup_demo.tau' | relative_url }}):
  `examples/tau/sparse_impact_factor_speedup_demo.tau`

The generated spec has $24$ top-level factors. Only $3$ factors mention
`d0`, so the measured route can compare all-factor work with impacted-factor
work.

On one local patched checkout, the demo reported a median speedup above `40x`.
That number is not the tutorial claim, because local timing varies. The
portable claim remains the checked v768 benchmark median, `8.446x`.

For the full evidence trail, see
[Sparse impacted-factor solving in Tau]({{ '/research/tau-sparse-impact-factor-solving/' | relative_url }}).

For the one-command demo page, see
[Tau sparse-impact demo]({{ '/tau-sparse-impact-demo/' | relative_url }}).

## Summary

The confirmed result is:

```text
indexed sparse impacted-factor solving measured an 8.446x median in-process
speedup on a checked sparse Tau fragment
```

The confirmed boundary is:

```text
the automatic route selector is not solved
```

The reusable idea is:

$$
\operatorname{Optimization}
=
\operatorname{support\ locality}
+
\operatorname{fragment\ guard}
+
\operatorname{fallback}
+
\operatorname{evidence}.
$$

That is the real optimization path for Tau: fragment-sensitive,
support-aware, and checked before promotion.
