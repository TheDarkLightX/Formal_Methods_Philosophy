---
title: Labs
layout: base
show_title: false
description: "Interactive labs paired with the tutorial series: bounded witness search, loop geometry, verifier compilation, and state-machine exploration."
---

<section class="fp-hero">
  <div class="fp-hero-grid">
    <div>
      <h1 class="fp-hero-title">Interactive Labs</h1>
      <p class="fp-hero-subtitle">
        Bounded, replayable teaching labs paired with the tutorials. Each one turns
        an abstract claim into something visible: a witness, a quotient, a bad
        state, or a compiled controller.
      </p>
      <div class="fp-badges" aria-label="Lab style">
        <span class="fp-badge">Bounded models</span>
        <span class="fp-badge">Witness search</span>
        <span class="fp-badge">Replayable traces</span>
      </div>
      <div class="fp-hero-actions">
        <a class="fp-btn fp-btn-primary" href="{{ '/tutorials/' | relative_url }}"
          >Browse tutorials</a
        >
        <a class="fp-btn fp-btn-secondary" href="{{ '/glossary/' | relative_url }}"
          >Open glossary</a
        >
      </div>
    </div>
    <div class="fp-hero-visual" aria-hidden="true">
      {% include diagrams/hero-pipeline.svg %}
    </div>
  </div>
</section>

<div class="fp-callout fp-callout-note" style="margin-top: var(--space-xl)">
  <p class="fp-callout-title">Scope note</p>
  <p>
    These labs use small bounded models for teaching clarity, not full proofs of unrestricted systems.
    Each harness is a simplified but replayable slice of a tutorial’s formal object, and a demonstrated
    counterexample shape or search geometry should be read as a concrete witness inside that bounded model,
    not as a claim of general completeness.
  </p>
</div>

<div class="fp-callout fp-callout-try" style="margin-top: var(--space-xl)">
  <p class="fp-callout-title">Suggested first path</p>
  <p>Start with the Concolic Branch Lab, then move to the Grammar Witness Search Lab, and only then open the Grammar-to-Solver Handoff Lab. That sequence goes from path-directed search, to syntax-preserving search, to the hybrid moment where structured search hands off to local solving.</p>
</div>

<section style="margin-top: var(--space-2xl)">
  <h2 class="fp-page-title" style="font-size: 2rem; margin-bottom: var(--space-md)">Witness Search Track</h2>
  <div class="fp-grid">
    <div class="fp-card fp-card-span-4">
      <h3 class="fp-card-title">Concolic Branch Lab</h3>
      <p class="fp-card-text">
        Concrete run, path condition, branch flip, bounded solve, replay. This is
        the hands-on companion to Tutorial 35.
      </p>
      <div class="fp-hero-actions">
        <a class="fp-btn fp-btn-primary" href="{{ '/concolic_branch_lab.html' | relative_url }}">Open lab</a>
        <a class="fp-btn fp-btn-secondary" href="{{ '/tutorials/concolic-testing-and-branch-exploration/' | relative_url }}">Read Tutorial 35</a>
      </div>
    </div>
    <div class="fp-card fp-card-span-4">
      <h3 class="fp-card-title">Grammar Witness Search Lab</h3>
      <p class="fp-card-text">
        Compare raw-byte search with grammar-guided generation on the same bad-state
        predicate. This is the companion lab for Tutorial 36.
      </p>
      <div class="fp-hero-actions">
        <a class="fp-btn fp-btn-primary" href="{{ '/grammar_witness_search_lab.html' | relative_url }}">Open lab</a>
        <a class="fp-btn fp-btn-secondary" href="{{ '/tutorials/grammar-based-fuzzing-and-structured-search/' | relative_url }}">Read Tutorial 36</a>
      </div>
    </div>
    <div class="fp-card fp-card-span-4">
      <h3 class="fp-card-title">Grammar-to-Solver Handoff Lab</h3>
      <p class="fp-card-text">
        Watch structured generation stay valid, then hand off to a bounded solver
        when the remaining obstacle is semantic rather than syntactic.
      </p>
      <div class="fp-hero-actions">
        <a class="fp-btn fp-btn-primary" href="{{ '/grammar_solver_handoff_lab.html' | relative_url }}">Open lab</a>
        <a class="fp-btn fp-btn-secondary" href="{{ '/tutorials/grammar-based-fuzzing-and-structured-search/' | relative_url }}">Read Tutorial 36</a>
      </div>
    </div>
    <div class="fp-card fp-card-span-4">
      <h3 class="fp-card-title">Witness Space Explorer</h3>
      <p class="fp-card-text">
        See proposal distributions, acceptance regions, and found witnesses move
        against each other in a bounded search space.
      </p>
      <div class="fp-hero-actions">
        <a class="fp-btn fp-btn-primary" href="{{ '/witness_space_explorer.html' | relative_url }}">Open lab</a>
        <a class="fp-btn fp-btn-secondary" href="{{ '/tutorials/neuro-symbolic-witness-spaces/' | relative_url }}">Read Tutorial 20</a>
      </div>
    </div>
  </div>
</section>

<section style="margin-top: var(--space-2xl)">
  <h2 class="fp-page-title" style="font-size: 2rem; margin-bottom: var(--space-md)">Loop Geometry Track</h2>
  <p class="fp-card-text" style="margin-bottom: var(--space-lg)">If the witness-search track is finished, this is the best next stop. Start with the Hybrid Loop Comparison Lab, then move to Galois Loop Lab if the goal is to see how the search space itself can be reshaped.</p>
  <div class="fp-grid">
    <div class="fp-card fp-card-span-4">
      <h3 class="fp-card-title">Hybrid Loop Comparison Lab</h3>
      <p class="fp-card-text">
        Compare direct control with two hybrid loops on the same bounded task and
        inspect what the hybrid stages are actually buying.
      </p>
      <div class="fp-hero-actions">
        <a class="fp-btn fp-btn-primary" href="{{ '/hybrid_loop_comparison_lab.html' | relative_url }}">Open lab</a>
        <a class="fp-btn fp-btn-secondary" href="{{ '/tutorials/hybrid-geometry-changing-loops/' | relative_url }}">Read Tutorial 31</a>
      </div>
    </div>
    <div class="fp-card fp-card-span-4">
      <h3 class="fp-card-title">Galois Loop Lab</h3>
      <p class="fp-card-text">
        Watch obligation carving happen over a finite relation universe and see how
        the quotient changes the repair problem.
      </p>
      <div class="fp-hero-actions">
        <a class="fp-btn fp-btn-primary" href="{{ '/galois_loop_lab.html' | relative_url }}">Open lab</a>
        <a class="fp-btn fp-btn-secondary" href="{{ '/tutorials/galois-loops-and-obligation-carving/' | relative_url }}">Read Tutorial 26</a>
      </div>
    </div>
    <div class="fp-card fp-card-span-4">
      <h3 class="fp-card-title">Verifier-Compiler Lab</h3>
      <p class="fp-card-text">
        See verifier labels collapse into a smaller symbolic controller, and inspect
        when that compression is pure and when it is mixed.
      </p>
      <div class="fp-hero-actions">
        <a class="fp-btn fp-btn-primary" href="{{ '/verifier_compiler_lab.html' | relative_url }}">Open lab</a>
        <a class="fp-btn fp-btn-secondary" href="{{ '/tutorials/verifier-compiler-loops/' | relative_url }}">Read Tutorial 27</a>
      </div>
    </div>
    <div class="fp-card fp-card-span-4">
      <h3 class="fp-card-title">Temporal Label Basis Lab</h3>
      <p class="fp-card-text">
        Compare coarse and richer temporal label bases, then see why the stronger
        basis becomes exact only after the right first carve.
      </p>
      <div class="fp-hero-actions">
        <a class="fp-btn fp-btn-primary" href="{{ '/temporal_label_basis_lab.html' | relative_url }}">Open lab</a>
        <a class="fp-btn fp-btn-secondary" href="{{ '/tutorials/temporal-label-functions-and-staged-bases/' | relative_url }}">Read Tutorial 32</a>
      </div>
    </div>
  </div>
</section>

<section style="margin-top: var(--space-2xl)">
  <h2 class="fp-page-title" style="font-size: 2rem; margin-bottom: var(--space-md)">State and Shape Track</h2>
  <p class="fp-card-text" style="margin-bottom: var(--space-lg)">For a gentler change of pace, start here with the Vending Machine Explorer. It is the most concrete entry point for states, transitions, and invariants before the later shape tutorials become more abstract.</p>
  <div class="fp-grid">
    <div class="fp-card fp-card-span-4">
      <h3 class="fp-card-title">Vending Machine Explorer</h3>
      <p class="fp-card-text">
        A small live state machine for learning states, transitions, and invariants
        before the tutorials become more abstract.
      </p>
      <div class="fp-hero-actions">
        <a class="fp-btn fp-btn-primary" href="{{ '/vending_machine_explorer.html' | relative_url }}">Open lab</a>
        <a class="fp-btn fp-btn-secondary" href="{{ '/tutorials/software-shapes-and-zenodex/' | relative_url }}">Read Tutorial 17</a>
      </div>
    </div>
    <div class="fp-card fp-card-span-4">
      <h3 class="fp-card-title">Shape Evolution Explorer</h3>
      <p class="fp-card-text">
        Move through shape choices and see how adding clauses changes the reachable
        system behaviors.
      </p>
      <div class="fp-hero-actions">
        <a class="fp-btn fp-btn-primary" href="{{ '/shape_evolution_explorer.html' | relative_url }}">Open lab</a>
        <a class="fp-btn fp-btn-secondary" href="{{ '/tutorials/software-shapes-and-zenodex/' | relative_url }}">Read Tutorial 17</a>
      </div>
    </div>
    <div class="fp-card fp-card-span-4">
      <h3 class="fp-card-title">ZenoDEX Shape Pruning Lab</h3>
      <p class="fp-card-text">
        Treat clauses as structural blockers on disaster states and inspect what each
        strengthening step actually removes.
      </p>
      <div class="fp-hero-actions">
        <a class="fp-btn fp-btn-primary" href="{{ '/zenodex_shape_pruning_lab.html' | relative_url }}">Open lab</a>
        <a class="fp-btn fp-btn-secondary" href="{{ '/tutorials/zenodex-shape-transition/' | relative_url }}">Read Tutorial 18</a>
      </div>
    </div>
  </div>
</section>
