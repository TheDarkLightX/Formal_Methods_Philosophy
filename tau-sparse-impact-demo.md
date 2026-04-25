---
title: "Tau Sparse-Impact Demo"
layout: base
show_title: false
description: "Patch a Tau checkout and run the sparse impacted-factor speed demo."
---

<section class="fp-hero">
  <div class="fp-hero-grid">
    <div>
      <h1 class="fp-hero-title">Tau Sparse-Impact Demo</h1>
      <p class="fp-hero-subtitle">
        Patch a Tau checkout, build it, and run a generated sparse
        impacted-factor spec that reports the measured indexed-factor speedup.
      </p>
      <div class="fp-badges" aria-label="Demo scope">
        <span class="fp-badge">Feature-gated patch</span>
        <span class="fp-badge">Local timing</span>
        <span class="fp-badge">Fallback boundary</span>
      </div>
    </div>
    <div class="fp-card">
      <p class="fp-card-kicker">What this demo checks</p>
      <h2 class="fp-card-title">24 factors, 3 impacted</h2>
      <p class="fp-card-text">
        The generated Tau formula is a top-level conjunction. Only three
        factors mention <code>d0</code>, so the patched diagnostic route can
        compare all-factor solving with impacted-factor solving.
      </p>
    </div>
  </div>
</section>

<div class="fp-callout fp-callout-note" style="margin-top: var(--space-xl)">
  <p class="fp-callout-title">Scope</p>
  <p>This is a local research demo. A large speedup here does not imply that every Tau formula speeds up. The confirmed benchmark claim remains the checked sparse-impact result described in Tutorial 52.</p>
</div>

<section style="margin-top: var(--space-xl)">
  <h2 class="fp-section-heading">One command</h2>
  <p>
    From the repository root, point the script at a Tau checkout:
  </p>

  <pre><code class="language-bash">python3 scripts/run_tau_sparse_impact_demo.py --tau-checkout /path/to/tau-lang-latest</code></pre>

  <p>
    The script applies the patch if needed, rebuilds Tau, writes the generated
    demo spec, runs the patched Tau binary, and writes a JSON report.
  </p>
</section>

<section style="margin-top: var(--space-xl)">
  <h2 class="fp-section-heading">Files</h2>
  <div class="fp-grid" style="margin-top: var(--space-md)">
    <div class="fp-card fp-card-span-4">
      <p class="fp-card-kicker">Patch</p>
      <h3 class="fp-card-title">Tau source patch</h3>
      <p class="fp-card-text"><code>patches/tau/indexed-factor-sparse-impact-demo.patch</code></p>
    </div>
    <div class="fp-card fp-card-span-4">
      <p class="fp-card-kicker">Runner</p>
      <h3 class="fp-card-title">Demo script</h3>
      <p class="fp-card-text"><code>scripts/run_tau_sparse_impact_demo.py</code></p>
    </div>
    <div class="fp-card fp-card-span-4">
      <p class="fp-card-kicker">Spec</p>
      <h3 class="fp-card-title">Generated Tau command</h3>
      <p class="fp-card-text"><code>examples/tau/sparse_impact_factor_speedup_demo.tau</code></p>
    </div>
  </div>
</section>

<section style="margin-top: var(--space-xl)">
  <h2 class="fp-section-heading">Expected output shape</h2>
  <p>
    Exact timings depend on the machine and checkout, but a successful run
    prints a JSON summary like this:
  </p>

  <pre><code class="language-json">{
  "status": "passed",
  "median_speedup": 41.1025,
  "scope": "sparse top-level conjunction with 24 factors and 3 factors impacted by d0"
}</code></pre>

  <p>
    The important fields in the full report are:
  </p>

  <pre><code>factors = 24
impacted_indexed = 3
saved_factors = 21
scan_equals_indexed = 1
full_errors = 0
indexed_errors = 0</code></pre>
</section>

<section style="margin-top: var(--space-xl)">
  <h2 class="fp-section-heading">Interpretation</h2>
  <p>
    The demo is a smoke test for the sparse-impact route. It checks that the
    support index selects the same impacted factors as a scan, and that the
    patched diagnostic path solves far fewer factors on this generated case.
  </p>
  <p>
    It is not a production optimizer. It does not solve the automatic
    route-selector problem. For the full evidence and falsifications, read
    <a href="{{ '/research/tau-sparse-impact-factor-solving/' | relative_url }}">the research log</a>.
  </p>
</section>
