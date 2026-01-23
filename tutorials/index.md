---
title: Tutorials
layout: base
show_title: false
---

<section class="fp-hero">
  <div class="fp-hero-grid">
    <div>
      <h1 class="fp-hero-title">Tutorials</h1>
      <p class="fp-hero-subtitle">
        Each tutorial starts with a concrete picture, then tightens into a precise model
        that tools can manipulate.
      </p>
      <div class="fp-badges" aria-label="Learning style">
        <span class="fp-badge">Concrete first</span>
        <span class="fp-badge">Formal accuracy</span>
        <span class="fp-badge">Tool-shaped thinking</span>
      </div>
    </div>
    <div class="fp-hero-visual" aria-hidden="true">
      {% include diagrams/hero-pipeline.svg %}
    </div>
  </div>
</section>

<div class="fp-grid" style="margin-top: var(--space-xl)">
  <a
    class="fp-card fp-card-link fp-card-span-4"
    href="{{ '/tutorials/approximate-state-tracking/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 1: Approximate state tracking</h2>
    <p class="fp-card-text">
      Start inside a card counter’s head, then zoom out into state machines, abstraction,
      counterexamples, CEGIS, and the boundaries between heuristics and proofs.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-4"
    href="{{ '/tutorials/isomorphism/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 2: Isomorphism</h2>
    <p class="fp-card-text">
      A 1-to-1, structure-preserving translation: why some “different abstractions” are
      the same thing in different clothes, and how to move problems into better toolchains.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-4"
    href="{{ '/tutorials/tau-language/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 3: Tau Language</h2>
    <p class="fp-card-text">
      Learn to read and write small executable specifications by listing invariants first,
      then letting a solver produce behaviors that satisfy them.
    </p>
  </a>
</div>
