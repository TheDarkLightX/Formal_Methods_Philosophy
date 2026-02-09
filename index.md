---
title: Home
layout: base
show_title: false
---

<section class="fp-hero">
  <div class="fp-hero-grid">
    <div>
      <h1 class="fp-hero-title">Formal Philosophy</h1>
      <p class="fp-hero-subtitle">
        A tutorial series about how to think in formal methods: modeling, abstraction,
        symbolic tools, counterexamples, and what it means to justify a claim about software.
      </p>

      <div class="fp-badges" aria-label="Topics">
        <span class="fp-badge">State machines</span>
        <span class="fp-badge">Abstraction</span>
        <span class="fp-badge">Counterexamples</span>
        <span class="fp-badge">CEGIS</span>
        <span class="fp-badge">Security claims</span>
      </div>

      <div class="fp-search" role="search" aria-label="Search">
        <input
          class="fp-search-input"
          type="search"
          inputmode="search"
          placeholder="Search: counterexample, invariant, state machine, CEGIS..."
          aria-label="Search the site"
          data-fp-search-input
        />
        <div class="fp-search-results" data-fp-search-results></div>
        <div class="fp-search-hint" data-fp-search-hint></div>
      </div>

      <div class="fp-hero-actions">
        <a class="fp-btn fp-btn-primary" href="{{ '/tutorials/' | relative_url }}"
          >Start reading</a
        >
        <a class="fp-btn fp-btn-secondary" href="{{ site.repo_url }}">View on GitHub</a>
      </div>
    </div>

    <div class="fp-hero-visual" aria-hidden="true">
      {% include diagrams/hero-pipeline.svg %}
    </div>
  </div>
</section>

<section style="margin-top: var(--space-2xl)">
  <div class="fp-grid">
    <a
      class="fp-card fp-card-link fp-card-span-6"
      href="{{ '/tutorials/approximate-state-tracking/' | relative_url }}"
    >
      <h2 class="fp-card-title">Tutorial 1: Approximate state tracking</h2>
      <p class="fp-card-text">
        A deck of cards as a mental model for state, abstraction, counterexamples, and
        counterexample-guided synthesis.
      </p>
    </a>
    <a
      class="fp-card fp-card-link fp-card-span-6"
      href="{{ '/tutorials/isomorphism/' | relative_url }}"
    >
      <h2 class="fp-card-title">Tutorial 2: Isomorphism</h2>
      <p class="fp-card-text">
        How 1-to-1, structure-preserving translations let you change languages without
        changing the problem.
      </p>
    </a>
    <a
      class="fp-card fp-card-link fp-card-span-6"
      href="{{ '/tutorials/tau-language/' | relative_url }}"
    >
      <h2 class="fp-card-title">Tutorial 3: Tau Language</h2>
      <p class="fp-card-text">
        Write small executable specifications by listing invariants first, then letting a solver
        produce behaviors that satisfy them.
      </p>
    </a>
    <a
      class="fp-card fp-card-link fp-card-span-6"
      href="{{ '/tutorials/world-models/' | relative_url }}"
    >
      <h2 class="fp-card-title">Tutorial 4: World models and continuous learning</h2>
      <p class="fp-card-text">
        Humans use internal models to simulate and plan. When models learn online, invariants and
        counterexamples become the difference between adaptation and drift.
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
      <h2 class="fp-card-title">Tutorial 6: MPRD and the algorithmic CEO</h2>
      <p class="fp-card-text">
        How MPRD turns model proposals into policy-gated execution, which
        algorithm breakthroughs support the algorithmic CEO, and why this is a
        concrete neuro-symbolic loop.
      </p>
    </a>
    <a
      class="fp-card fp-card-link fp-card-span-6"
      href="{{ '/tutorials/good-software-engineering-and-clean-code/' | relative_url }}"
    >
      <h2 class="fp-card-title">Tutorial 7: Good software engineering and clean code</h2>
      <p class="fp-card-text">
        Why user outcomes are the north star in both traditional and agentic workflows,
        and how best-practice rails turn intent into durable quality.
      </p>
    </a>
    <a
      class="fp-card fp-card-link fp-card-span-6"
      href="{{ '/tutorials/predictive-reading-scramble-invariants/' | relative_url }}"
    >
      <h2 class="fp-card-title">Tutorial 8: Predictive reading and scrambled text</h2>
      <p class="fp-card-text">
        An interactive app and scoped proof framework showing how invariants, ambiguity,
        and context-based prediction fit together in human reading.
      </p>
    </a>
    <a
      class="fp-card fp-card-link fp-card-span-6"
      href="{{ '/tutorials/prompt-engineering-precision-communication/' | relative_url }}"
    >
      <h2 class="fp-card-title">Tutorial 9: Prompt engineering and precision communication</h2>
      <p class="fp-card-text">
        Precision communication for the agentic era. Make constraints explicit, use representation changes
        when the direct route is intractable, and transpile controlled language into a structured spec.
      </p>
    </a>
    <a
      class="fp-card fp-card-link fp-card-span-6"
      href="{{ '/glossary/' | relative_url }}"
    >
      <h2 class="fp-card-title">Glossary</h2>
      <p class="fp-card-text">
        A short, growing vocabulary for the words we use to think clearly: state,
        invariant, reachability, abstraction, soundness, and more.
      </p>
    </a>
  </div>
</section>

<section style="margin-top: var(--space-2xl)">
  <div class="fp-grid">
    <div class="fp-card fp-card-span-4">
      <h2 class="fp-card-title">Make claims explicit</h2>
      <p class="fp-card-text">
        Formal methods starts by forcing ambiguity into the open. If you cannot state the
        claim, you cannot check the claim.
      </p>
    </div>
    <div class="fp-card fp-card-span-4">
      <h2 class="fp-card-title">Search for refuters</h2>
      <p class="fp-card-text">
        Tools are not there to praise you. They are there to find the smallest, sharpest
        counterexample that breaks what you thought was “always true.”
      </p>
    </div>
    <div class="fp-card fp-card-span-4">
      <h2 class="fp-card-title">Refine into predictability</h2>
      <p class="fp-card-text">
        Proving bad states unreachable is a way of narrowing the program’s possible
        futures. That narrowing is what predictability means, formally.
      </p>
    </div>
  </div>
</section>

<section style="margin-top: var(--space-2xl)">
  <h2 style="font-family: 'Crimson Pro', ui-serif, Georgia, serif; font-size: 32px">
    FAQ
  </h2>
  <div style="display: grid; gap: var(--space-md); margin-top: var(--space-md)">
    <details class="fp-faq">
      <summary>Does this site render LaTeX math?</summary>
      <div class="fp-prose" style="margin-top: var(--space-sm); color: var(--color-muted)">
        Yes. We use MathJax. Example: \( \forall s.\, Reachable(s) \rightarrow \lnot Bad(s) \).
      </div>
    </details>
    <details class="fp-faq">
      <summary>Can I zoom in on the diagrams?</summary>
      <div class="fp-prose" style="margin-top: var(--space-sm); color: var(--color-muted)">
        Yes. Click or tap a diagram to open a larger viewer. Press Escape to close.
      </div>
    </details>
    <details class="fp-faq">
      <summary>Is this a math textbook?</summary>
      <div class="fp-prose" style="margin-top: var(--space-sm); color: var(--color-muted)">
        No. It is a set of mental models, careful definitions, and tool-shaped ways of
        thinking. The goal is to make formal accuracy feel intuitive.
      </div>
    </details>
    <details class="fp-faq">
      <summary>Do I need to know logic already?</summary>
      <div class="fp-prose" style="margin-top: var(--space-sm); color: var(--color-muted)">
        Not to start. We introduce the minimum logic you need, right when you need it,
        and we always connect it back to a concrete picture.
      </div>
    </details>
    <details class="fp-faq">
      <summary>What is the one sentence definition of a counterexample?</summary>
      <div class="fp-prose" style="margin-top: var(--space-sm); color: var(--color-muted)">
        A counterexample is a specific witness (often a trace) that refutes a universal
        claim.
      </div>
    </details>
  </div>
</section>
