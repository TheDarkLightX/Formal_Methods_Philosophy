---
title: "Why current LLMs are not yet AGI: math, meaning, and thought experiments"
layout: docs
kicker: Tutorial 12
description: A scoped argument that current LLMs excel at syntactic pattern modeling but still struggle with stable meaning, concept invention, and meaning-preserving formalization.
---

This tutorial presents a scoped claim about a gap that matters in formal methods: **syntactic fluency** is not the same thing as **stable meaning**.

The claim is framed so it can be stress-tested:

- Many current LLMs are high-fidelity models of language usage (statistical syntax).
- If AGI requires stable meaning plus reliable concept invention, then next-token prediction alone is not enough.
- The practical gap appears as semantic drift: translating intent into a formal artifact that changes the intended meaning.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Assumption hygiene (scope and definitions)</p>
  <ul>
    <li><strong>Assumption A (AGI threshold):</strong> AGI requires the ability to move problems across abstraction boundaries (for example, from experience to formal specification) without semantic drift.</li>
    <li><strong>Assumption B (symbol grounding):</strong> Symbols (words, tokens) only have stable meaning if they are linked to non-symbolic internal representations (simulations, world models, or embodied feedback).</li>
    <li><strong>Assumption C (concept invention loop):</strong> Concept invention is treated as a loop that proposes a new abstraction, stress-tests it via counterexamples, and stabilizes it via definitions and invariants.</li>
    <li><strong>Assumption D (system boundary):</strong> This tutorial distinguishes a base model (a trained network) from a system (a model plus tools such as memory, simulators, and proof or test checkers).</li>
  </ul>
</div>

## Part I: syntax vs. semantics (the two layers of math)

In formal methods, the **syntactic layer** is symbol manipulation under explicit rules. This is where solvers and compilers operate, and where LLMs can be useful as proposal generators for candidate artifacts.

However, mathematical discovery happens at the **semantic layer**, the construction and stabilization of meaning. Humans introduce new "objects of thought" before they have a notation for them.

- **The Indian Zero:** Moving from "nothing" (a void) to "Zero" (a conceptual object with properties like $x + 0 = x$) was an ontological shift, not a calculation.
- **Cantor's Infinities:** Cantor did not just "find" different sizes of infinity. He created a conceptual framework (cardinality) that allowed them to be compared.
- **Galois' Groups:** Galois reframed polynomial solvability by inventing "groups", a higher-level symmetry object that simplified a low-level algebra problem.

**The insight:** A symbolic engine can verify a derivation once the ontology (the types and rules) is fixed. It rarely proposes the new ontology itself.

## Part II: the conceptual reasoning pipeline

We can model the path from reality to rigor as a three-stage mapping:

$$
\text{Experience} \xrightarrow{\phi} \text{Concepts} \xrightarrow{\psi} \text{Symbols} \xrightarrow{\vdash} \text{Derivations}
$$

1. **The Grounding Mapping ($\phi$):** Maps raw inputs (sensory, simulated, or imagined) into internal conceptual structures.
2. **The Formalization Mapping ($\psi$):** Encodes those structures into a stable symbolic language (natural language, code, or math).
3. **The Inference Mapping ($\vdash$):** Applies rules to the symbols to produce new symbols (the "calculus").

**A common LLM profile:** Many LLM training setups optimize for producing plausible symbol sequences, then fine-tune for helpfulness. This can make $\psi$ look strong (fluent formalizations) while leaving $\phi$ weak (unstable or ungrounded conceptual commitments). Under distribution shift or adversarial prompting, the apparent meaning can drift.

## Part III: concept invention (historical proof-of-concept)

Major scientific leaps often occur in the "pre-formal" space through simulation and representational restructuring.

### 1) Representational Leverage (Galois)
Galois stopped looking at the *values* of roots and started looking at the *structure* of their permutations. This was not a better algorithm. It was a better abstraction. LLMs are often excellent at following existing abstractions, but proposing new abstractions is harder to validate without an external loop of tests, counterexamples, or proofs.

### 2) The Simulation Prime (Einstein)
Einstein used **Gedankenexperimente** (thought experiments) as a low-fidelity world simulation. By "riding a light beam", he used internal world modeling to find a contradiction that algebra had not yet flagged. The math (Lorentz transformations) existed before he gave it the meaning of relativity.

### 3) Associative Latent Search (Ramanujan)
Ramanujan's autobiographical reports about "visions" are not laboratory measurements. Still, they illustrate a milder point: concept generation can occur before explicit formalization, and the route to a correct formula is not always a clean, linear derivation trace.

## Part IV: thought experiments in software engineering (state, invariants, and traces)

Thought experiments are not unique to physics. In software engineering, they show up as "what-if" reasoning over traces.

Engineers often compress a system into a state machine (sometimes explicitly as a finite state machine, sometimes implicitly as a transition system), then mentally simulate an execution trace.

When invariants are known, thought experiments become sharper. The invariant plays the same cognitive role as a physics constraint: it focuses the search for contradictions and counterexamples.

### Example: the idempotency "discovery"
Consider a payment system.
1. **Initial Concept:** "Charge the user when the button is clicked."
2. **Thought Experiment:** "What if the network fails *after* the charge but *before* the 'Success' message reaches the user? They click again."
3. **Contradiction:** The user is charged twice (violating the "at most once" invariant).
4. **Conceptual Repair:** Invent a new primitive, the **idempotency key**. This is a stable identity for a "transaction intent" that persists across retries, and it becomes part of the state the system reasons about.

This is a common high-assurance move: refine the model so the invariant becomes enforceable and testable under the intended failure modes. The bad behavior is still representable in an implementation with bugs, but the concept makes the intended prevention mechanism explicit.

## Part V: the AGI capability gap

| Capability | Definition | Typical base-model status |
|---|---|---|
| **Syntactic Fluency** | Modeling the probability of token sequences. | **Exceptional** |
| **Semantic Grounding** | Linking tokens to stable, non-linguistic referents. | **Fragile and task-dependent** |
| **Concept Invention** | Inventing new classes/types to explain data. | **Limited and hard to validate** |
| **Meaning-Preserving Formalization** | Maintaining 1:1 mapping from intent to spec. | **Low Assurance (Drift)** |

## Part VI: formal guardrails (Rice and Searle)

To understand why LLMs struggle with "truth," we must respect two fundamental limits:

### Rice's Theorem (The Technical Limit)
Any non-trivial semantic property of a program is undecidable by a general algorithm.
*   **Implication:** In full generality, semantics cannot be computed from syntax alone. High-assurance work uses restricted domains, extra structure, and explicit proof or counterexample obligations.

### The Chinese Room (The Philosophical Limit)
A clerk in a room following a rulebook to translate Chinese can "pass" as a speaker without knowing a word of Chinese.
*   **Implication:** Behavioral "passing" (the Turing Test) is a measure of **Syntactic Fidelity**, not **Semantic Grounding**.

Together, these are guardrails. They support caution about "meaning from text alone." They do not prove machine understanding is impossible.

## Part VII: the engineering cost of "Semantic Drift"

In high-assurance engineering, the most dangerous failure is **Semantic-to-Formal Drift**:

$$
\text{Human Intent} \neq \text{LLM-Generated Spec} \approx \text{Syntactically Valid Code}
$$

Because an LLM may not maintain stable semantic commitments for invariants (like "safety" or "liveness"), it can produce a specification that passes a linter but violates unstated assumptions. This is why high-assurance workflows use executable specs and formal solvers. Those tools can expose drift that syntax alone cannot see.

## Part VIII: how to stress-test this thesis

Evidence against this tutorial's claim would look like a system that reliably demonstrates:

1. **Novel concept invention:** propose a new structure, then use it consistently across tasks where interpolation fails.
2. **Stable grounding:** maintain referential stability of core concepts across changing contexts and long horizons.
3. **Meaning-preserving formalization:** translate intent into formal artifacts with low semantic drift, verified by executable checks or proofs.
4. **Counterexample discipline:** seek refuters and edge cases as a default part of its own loop.

## Part IX: Conclusion (the path forward)

We do not need to wait for AGI to do high-assurance work. By recognizing the LLM as a **Proposal Engine** (strong at $\vdash$) and the Human as a **Meaning Engine** (strong at $\phi$), we can build "Neuro-Symbolic" workflows:

1.  **Human:** Defines the **Ontology** (the types and invariants).
2.  **LLM:** Proposes the **Formalization** (the candidate implementation).
3.  **Solver:** Verifies the **Logic** (the proof of correctness).

This is the "Formal Philosophy" workflow: using precision to bridge the gap where "Intelligence" currently fails.

## References
- Rice, H. G. (1953) *Classes of recursively enumerable sets and their decision problems*.
- Searle, J. (1980) *Minds, Brains, and Programs*.
- Harnad, S. (1990) *The Symbol Grounding Problem*.
- Wigner, E. (1960) *The Unreasonable Effectiveness of Mathematics in the Natural Sciences*.
