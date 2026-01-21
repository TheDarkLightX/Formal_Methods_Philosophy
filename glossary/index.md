---
title: Glossary
layout: base
---

<div class="fp-prose markdown-body">
  <p>
    This glossary is intentionally small. Each definition is phrased to support a mental
    picture, not just a dictionary meaning.
  </p>

  <h2 id="state">State</h2>
  <p>
    A snapshot of “everything the system would need to know” to determine what can happen
    next. In practice, we choose a state representation that preserves the distinctions
    relevant to our question.
  </p>

  <h2 id="state-machine">State machine</h2>
  <p>
    A model of change over time: a set of states, an initial state, and a transition
    relation describing how the system can evolve.
  </p>

  <h2 id="invariant">Invariant</h2>
  <p>
    A property intended to hold for all reachable states. When it fails, a tool can often
    produce a counterexample trace showing how the failure is reached.
  </p>

  <h2 id="counterexample">Counterexample</h2>
  <p>
    A specific witness that refutes a universal claim. In software, it is often a concrete
    input and an execution trace.
  </p>

  <h2 id="abstraction">Abstraction</h2>
  <p>
    A mapping from concrete states to a smaller representation that discards detail while
    preserving the distinctions that matter for a chosen property.
  </p>

  <p>
    More terms will be added as the tutorials grow.
  </p>
</div>

