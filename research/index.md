---
title: Research Logs
layout: base
show_title: false
description: "Indexed research logs behind the tutorials, with neuro-symbolic methods, scoped claims, and code-shaped evidence."
---

<section class="fp-hero">
  <div class="fp-hero-grid">
    <div>
      <h1 class="fp-hero-title">Research Logs</h1>
      <p class="fp-hero-subtitle">
        Detailed experiment logs behind the tutorials. These pages keep the claims,
        failed boundaries, formal checks, and implementation sketches separate from the
        beginner-facing exposition.
      </p>
      <div class="fp-badges" aria-label="Research posture">
        <span class="fp-badge">Scoped claims</span>
        <span class="fp-badge">Replayable checks</span>
        <span class="fp-badge">No hidden assumptions</span>
      </div>
    </div>
    <div class="fp-hero-visual" aria-hidden="true">
      {% include diagrams/hero-pipeline.svg %}
    </div>
  </div>
</section>

<div class="fp-grid" style="margin-top: var(--space-xl)">
  <a
    class="fp-card fp-card-link fp-card-span-12"
    href="{{ '/research/fragment-sensitive-qelim-and-safe-tables/' | relative_url }}"
  >
    <h2 class="fp-card-title">Short paper: Fragment-sensitive qelim and safe table updates</h2>
    <p class="fp-card-text">
      A two-page PDF and compact academic-style note for readers who want the main results without the tutorial
      or the full research log: core equations, scoped claims, measured qelim result,
      safe pointwise revision, and exact limitations.
    </p>
  </a>
</div>

<div class="fp-grid" style="margin-top: var(--space-xl)">
  <a
    class="fp-card fp-card-link fp-card-span-12"
    href="{{ '/research/cpss-bc-routing-oracle/' | relative_url }}"
  >
    <h2 class="fp-card-title">From false greedy theorem to exact cross-pool routing oracle</h2>
    <p class="fp-card-text">
      A ZenoDEX research arc in adversarial falsification, subset dynamic programming,
      and scoped algorithm claims: the greedy CPSS-BC conjecture failed, an exact
      two-pool routing oracle replaced it, and the remaining <code>2^n</code> frontier
      became visible.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-12"
    href="{{ '/research/energy-based-optimizers-and-telemetry/' | relative_url }}"
  >
    <h2 class="fp-card-title">Energy-based optimizers and telemetry</h2>
    <p class="fp-card-text">
      Evidence behind Tutorial 59: ZenoEnergy verifier-call reduction,
      Tau route-telemetry results, ZenoDEX fast-router timings, and the
      advisory-ranking boundary that keeps verifiers authoritative.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-12"
    href="{{ '/research/tau-energy-based-route-telemetry/' | relative_url }}"
  >
    <h2 class="fp-card-title">Energy-based route telemetry for Tau</h2>
    <p class="fp-card-text">
      The research trail behind Tutorial 58: synthetic EBM feasibility,
      small-real-data negative evidence, expanded telemetry improvement, and
      the guard, abstention, validation, and fallback boundary.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-12"
    href="{{ '/research/taba-tables-and-tau-qelim/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tau qelim and TABA table semantics</h2>
    <p class="fp-card-text">
      The neuro-symbolic research log behind the Tau optimization and TABA table work:
      fragment-sensitive qelim behind Tutorial 40, the measured
      <code>TAU_QELIM_BACKEND=auto</code> candidate, BDD existential abstraction,
      finite table proof artifacts, replayed Tau finite-table kernels, atomless cell
      projection, prefix-clopen carriers, safe infinite-recursive table evidence,
      feature-flagged Tau table helpers, the TauLang-Experiments demo workflow,
      protocol firewall demos, collateral reason routers, incident-memory tables,
      and the remaining frontier.
    </p>
  </a>
</div>

<div class="fp-grid" style="margin-top: var(--space-xl)">
  <div class="fp-card fp-card-span-12">
    <h2 class="fp-card-title">How to read these pages</h2>
    <p class="fp-card-text">
      A research log is not a tutorial and not a proof of unrestricted behavior.
      Each note states what was checked, what was only tested, what failed, and what
      remains outside the current model.
    </p>
  </div>
</div>
