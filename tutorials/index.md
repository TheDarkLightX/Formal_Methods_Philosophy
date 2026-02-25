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
    class="fp-card fp-card-link fp-card-span-6"
    href="{{ '/tutorials/approximate-state-tracking/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 1: Approximate state tracking</h2>
    <p class="fp-card-text">
      Start inside a card counter’s head, then zoom out into state machines, abstraction,
      counterexamples, CEGIS, and the boundaries between heuristics and proofs.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-6"
    href="{{ '/tutorials/isomorphism/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 2: Isomorphism</h2>
    <p class="fp-card-text">
      A 1-to-1, structure-preserving translation: why some “different abstractions” are
      the same thing in different clothes, and how to move problems into better toolchains.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-6"
    href="{{ '/tutorials/tau-language/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 3: Tau Language</h2>
    <p class="fp-card-text">
      Learn to read and write small executable specifications by listing invariants first,
      then letting a solver produce behaviors that satisfy them.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-6"
    href="{{ '/tutorials/world-models/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 4: World models and continuous learning</h2>
    <p class="fp-card-text">
      Why internal models are more than prediction, why test-time learning is powerful,
      and why invariants and counterexamples become essential when the model can drift.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-6"
    href="{{ '/tutorials/reformulation-and-gates/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 5: Reformulation and compression</h2>
    <p class="fp-card-text">
      How changing representations creates leverage, why abstraction rhymes with compression, and how
      neuro-symbolic gates turn model proposals into checkable evidence.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-6"
    href="{{ '/tutorials/mprd-and-algorithmic-ceo/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 6: MPRD and the Algorithmic CEO</h2>
    <p class="fp-card-text">
      The neuro-symbolic gate from Tutorial 5 turned into production architecture.
      Models propose, rules decide, and counterexamples drive refinement.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-6"
    href="{{ '/tutorials/good-software-engineering-and-clean-code/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 7: What makes a good software engineer, and what clean code means</h2>
    <p class="fp-card-text">
      A user-centered framework for the agentic era: provenance-agnostic quality,
      diamond-rule engineering, and best-practice rails for safe, maintainable systems.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-6"
    href="{{ '/tutorials/predictive-reading-scramble-invariants/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 8: Predictive reading, scrambling, invariants, and proof</h2>
    <p class="fp-card-text">
      Build an interactive scrambler app, verify logic invariants, and separate formal proof
      from empirical proof-by-witness about human predictive reading.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-6"
    href="{{ '/tutorials/prompt-engineering-precision-communication/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 9: Prompt engineering and precision communication</h2>
    <p class="fp-card-text">
      Reduce ambiguity by making structure explicit. Compare bad and good prompts, connect reformulation
      to state explosion, and try a small transpiler demo that turns controlled language into specs.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-6"
    href="{{ '/tutorials/reasoning-connectionism-gofai/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 10: Reasoning, logic, and prediction</h2>
    <p class="fp-card-text">
      What reasoning is, why statistical learning cannot in principle produce logical validity,
      and why even approximate logic from a neural network cannot match a dedicated solver.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-6"
    href="{{ '/tutorials/church-synthesis-problem/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 11: Attacking hard problems with Church's synthesis problem</h2>
    <p class="fp-card-text">
      Define Church synthesis precisely, trace what is decidable, then use a decomposition-plus-invariants
      workflow to run systematic, falsifiable attempts against the complexity wall.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-6"
    href="{{ '/tutorials/llms-not-agi-meaning-and-concepts/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 12: Why current LLMs are not yet AGI</h2>
    <p class="fp-card-text">
      A scoped argument for the conceptual gap: strong language-pattern modeling is not yet
      the same as stable meaning creation, concept invention, or meaning-preserving formalization.
    </p>
  </a>
</div>
