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
  <a
    class="fp-card fp-card-link fp-card-span-6"
    href="{{ '/tutorials/what-is-reasoning-proof-search-and-justification/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 13: What reasoning is</h2>
    <p class="fp-card-text">
      Separate guessing, search, explanation, and proof using a child arithmetic example,
      Peano arithmetic, and the difference between discovery and justification.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-6"
    href="{{ '/tutorials/microkernels-micro-models-and-compositional-correctness/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 14: Microkernels and micro-models</h2>
    <p class="fp-card-text">
      Use seL4 as a case study for shrinking the trusted core, proving small local contracts,
      and widening assurance through checked composition rather than monolithic proof blobs.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-6"
    href="{{ '/tutorials/exhaustive-search-and-path-integrals/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 15: Exhaustive search and path integrals</h2>
    <p class="fp-card-text">
      Compare proof by exhaustive search with sum-over-histories, then extend the analogy to
      action, weighted futures, and the boundary between interference and intelligent planning.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-6"
    href="{{ '/tutorials/presburger-arithmetic/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 16: Presburger arithmetic, the decidable island</h2>
    <p class="fp-card-text">
      Build Presburger arithmetic from zero and successor, read its formulas, understand why excluding
      multiplication makes every question decidable, and see how this fragment powers real verification tools.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-6"
    href="{{ '/tutorials/software-shapes-and-zenodex/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 17: Software shapes and ZenoDEX</h2>
    <p class="fp-card-text">
      Start from arcade, ATM, and vending-machine intuition, then compress those shared shapes into
      states and invariants before climbing into ZenoDEX, formal tools, and parameter synthesis.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-6"
    href="{{ '/tutorials/zenodex-shape-transition/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 18: ZenoDEX shape transition</h2>
    <p class="fp-card-text">
      Compare the old ZenoDEX shape with the achieved audited-domain Shape++, then track how exact formulas,
      proof-carrying boundaries, and chaos-engineering probes make disaster states unreachable.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-6"
    href="{{ '/tutorials/resolution-refutation-and-falsification/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 19: Resolution, refutation, and falsification</h2>
    <p class="fp-card-text">
      Put logical refutation and Popperian falsification side by side, then separate proof in a
      closed formal world from corroboration in an open empirical world using explicit formulas.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-6"
    href="{{ '/tutorials/neuro-symbolic-witness-spaces/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 20: Neuro-symbolic reasoning and witness spaces</h2>
    <p class="fp-card-text">
      Treat LLMs as existential engines and symbolic methods as universal verifiers, then map proof search,
      counterexample search, synthesis, experiment design, and coverage limits in one formula family.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-6"
    href="{{ '/tutorials/perceptron-in-tau-language/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 21: A perceptron in Tau Language</h2>
    <p class="fp-card-text">
      Build a perceptron from formulas, execute bounded classifier specs in Tau, inspect real traces,
      and then separate the replayable classifier lane from a host-side learning loop.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-6"
    href="{{ '/tutorials/medical-deciders-mprd-and-tau/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 22: Medical deciders, MPRD, and Tau</h2>
    <p class="fp-card-text">
      Map bounded medical workflows into the MPRD shape, then use educational Tau policies to separate
      model proposals from execution authority through fail-closed guideline gates and human escalation paths.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-6"
    href="{{ '/tutorials/decidable-medical-machines/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 23: Decidable medical machines, from formulas to Tau</h2>
    <p class="fp-card-text">
      Start with a calorie calculator and a kidney follow-up workflow, then view each one as math,
      logic, a decision tree, a finite-state machine, ordinary code, and a downloadable Tau spec.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-6"
    href="{{ '/tutorials/rices-theorem-and-consciousness/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 24: Consciousness, computationalism, and Rice's theorem</h2>
    <p class="fp-card-text">
      Make one controversial argument precise: if consciousness is a nontrivial semantic property of computation,
      then no general Turing-machine detector can decide it from arbitrary encodings of programs.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-6"
    href="{{ '/tutorials/quantifier-factoring-and-neuro-symbolic-loops/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 25: Quantifier factoring and neuro-symbolic loop engineering</h2>
    <p class="fp-card-text">
      Start from "LLM = existential engine, formal tool = universal verifier", then push downward into
      counterexample search, certificate compression, quantified games, quotients, and fixed-point reasoning.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-6"
    href="{{ '/tutorials/galois-loops-and-obligation-carving/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 26: Galois loops and obligation carving</h2>
    <p class="fp-card-text">
      Reframe CEGIS through a Galois and FCA lens, prove the bounded obligation-side policy-improvement loop, show its
      measured power on finite relation universes, and sharpen the next frontier into controller compression.
    </p>
  </a>
  <a
    class="fp-card fp-card-link fp-card-span-6"
    href="{{ '/tutorials/verifier-compiler-loops/' | relative_url }}"
  >
    <h2 class="fp-card-title">Tutorial 27: Verifier-compiler loops</h2>
    <p class="fp-card-text">
      Start from plain CEGIS, then ask when verifier behavior itself can be compressed into a reusable symbolic controller
      for routing, ranking, and fail-closed pre-screening without replacing the exact gate.
    </p>
  </a>
</div>
