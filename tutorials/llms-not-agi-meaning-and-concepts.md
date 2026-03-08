---
title: "Why current LLMs are not yet AGI: concepts, meaning, and formalization"
layout: docs
kicker: Tutorial 12
description: A scoped argument that current LLMs excel at syntactic pattern modeling but do not yet reliably create and stabilize new conceptual objects or preserve meaning during formalization.
---

This tutorial presents a scoped claim about a gap that matters in formal methods and in philosophy of mind: **syntactic fluency** is not the same thing as **conceptual meaning**.

The claim is framed so it can be stress-tested:

- Many current LLMs are high-fidelity models of language usage (statistical syntax).
- That gives them access to **derivative meaning** in practice, meaning carried by human language, human users, and human institutions.
- Some meaning comes from lived experience, but some of the most important meanings in mathematics come from conceptual invention and structural necessity rather than from sensation.
- If AGI requires reliable creation and stabilization of new concepts, then next-token prediction alone is not enough.
- The practical engineering gap appears as semantic drift: translating intent into a formal artifact that changes the intended meaning.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Assumption hygiene (scope and definitions)</p>
  <ul>
    <li><strong>Assumption A (AGI threshold):</strong> AGI requires the ability to move problems across abstraction boundaries (for example, from experience to formal specification) without semantic drift.</li>
    <li><strong>Assumption B (conceptual meaning):</strong> On this page, a concept has meaning when it acquires a stable role inside a web of definitions, transformations, invariants, and problem-solving practices, not merely when a text model can continue sentences about it.</li>
    <li><strong>Assumption C (strong conceptual reasoning):</strong> Conceptual reasoning in the stronger sense includes proposing a new abstraction, stress-testing it through simulation or counterexamples, and stabilizing it through definitions and invariants.</li>
    <li><strong>Assumption D (system boundary):</strong> This tutorial distinguishes a base model (a trained network) from a system (a model plus tools such as memory, simulators, and proof or test checkers).</li>
  </ul>
</div>

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Three ways symbols can get their grip</p>
  <ul>
    <li><strong>Experiential grounding:</strong> meaning tied to lived or embodied interaction with the world.</li>
    <li><strong>Structural grounding:</strong> meaning tied to a stable role inside a conceptual system, as with zero, infinity, or imaginary numbers.</li>
    <li><strong>Derivative meaning:</strong> symbol use that is meaningful to humans because humans already supply the semantics.</li>
    <li><strong>Weak conceptual reasoning:</strong> recombining and extending already-languaged concepts in coherent ways.</li>
    <li><strong>Strong conceptual reasoning:</strong> forming and stabilizing new concepts through grounded experience, simulation, contradiction, and repair.</li>
  </ul>
  <p>
    The strongest criticism on this page is aimed at structural grounding and strong conceptual reasoning. Current LLMs can still be useful in the weaker, derivative senses, and that practical usefulness should not be confused with successful concept creation.
  </p>
</div>

An everyday example makes the contrast easier to see. When one person sends another `😭`, `🥲`, or `💀`, there is usually no need for a formal legend. The symbol works because both people already know something about grief, embarrassment, tenderness, exaggeration, irony, and social tone, then they adjust from context if the meaning is a little off.

Part of what gives that symbol its grip is not just convention. A sad emoji can bring back the memory of an actual feeling, a tone of voice, a social moment, even something close to a bodily echo of the emotion itself. Whatever the exact neural mechanism, human readers can often respond with empathy, emotional recall, and imaginative simulation. That is part of why a short string of symbols can carry nostalgia, tenderness, mock-despair, or consolation so quickly between people. An LLM can often follow that public pattern of use, sometimes very well, but it does so by modeling which symbols tend to appear in which situations. That is useful, but it is still borrowed meaning. Mathematical objects such as zero or $i$ are different again: they do not lean on shared feeling, they earn their meaning by holding a stable role inside a formal system.

## Part I: syntax vs. semantics (the two layers of math)

In formal methods, the **syntactic layer** is symbol manipulation under explicit rules. This is where solvers and compilers operate, and where LLMs can be useful as proposal generators for candidate artifacts.

However, mathematical discovery happens at the **semantic layer**, the construction and stabilization of meaning. Humans introduce new "objects of thought" before they have a notation for them.

For this page, there are really two questions:

- Can a system use symbols in stable and useful ways inside a workflow?
- Can it create a new concept that acquires a stable role inside a reasoning system, rather than merely imitating human talk about one?

Current LLMs often look impressive on the first question. This tutorial argues that they are still weak on the second, and that the engineering failures in formalization are partly downstream of that gap.

- **The Indian Zero:** Moving from "nothing" (a void) to "Zero" (a conceptual object with properties like $x + 0 = x$) was an ontological shift, not a calculation.
- **Cantor's Infinities:** Cantor did not just "find" different sizes of infinity. He created a conceptual framework (cardinality) that allowed them to be compared.
- **Galois' Groups:** Galois reframed polynomial solvability by inventing "groups", a higher-level symmetry object that simplified a low-level algebra problem.
- **Imaginary Numbers:** The symbol $i$ mattered because it stabilized a new formal object, one that repaired algebraic closure and later became indispensable across analysis, geometry, and physics.

None of these objects was "read off" from the senses. They were created because an older conceptual system ran into tension, and the new object resolved that tension in a way that proved stable and fruitful.

**The insight:** A symbolic engine can verify a derivation once the ontology (the types and rules) is fixed. The harder move is creating the new ontology itself, then making it precise enough that the rest of mathematics or engineering can lean on it.

This does not prove that LLMs can never generate useful new abstractions. It isolates the capability this page is tracking: stable introduction and reuse of a new abstraction under stress, with meaning that does not collapse into mere symbol continuation.

## Part II: the conceptual reasoning pipeline

We can model the path from reality to rigor as a three-stage mapping:

$$
\text{Pressure / Experience} \xrightarrow{\phi} \text{Concepts} \xrightarrow{\psi} \text{Symbols} \xrightarrow{\vdash} \text{Derivations}
$$

1. **The Grounding Mapping ($\phi$):** Maps raw pressure into conceptual structures. In empirical science that pressure may come from sensory, simulated, or imagined inputs. In mathematics it may come from structural tension, failed proof attempts, representational awkwardness, or the need to close a theory under useful operations.
2. **The Formalization Mapping ($\psi$):** Encodes those structures into a stable symbolic language (natural language, code, or math).
3. **The Inference Mapping ($\vdash$):** Applies rules to the symbols to produce new symbols (the "calculus").

**A common LLM profile:** Many LLM training setups optimize for producing plausible symbol sequences, then fine-tune for helpfulness. This can make $\psi$ look strong (fluent formalizations) while leaving $\phi$ weak (unstable or weakly grounded conceptual commitments). Under distribution shift or adversarial prompting, the apparent meaning can drift.

That is the practical reason the distinction matters. A system can look strong at the symbol layer while still borrowing its meaning from humans upstream. When that borrowed structure is thin, or when no stable new concept has actually formed, the formalization step is where drift shows up.

## Part III: concept invention (historical proof-of-concept)

Major scientific leaps often occur in the "pre-formal" space through simulation and representational restructuring.

The common pattern in the examples below is not just "someone had a clever idea." It is:

1. an older framing starts to fail,
2. a new object of thought is introduced,
3. that object survives reuse and stress,
4. only then does it become part of stable formal reasoning.

That is much closer to strong conceptual reasoning than to local symbol completion.

The crucial point is that this is not only a story about sensation. In mathematics, the "pressure" can be entirely internal to a theory. The concept is still real in the important sense once it becomes stable, reusable, and generative.

### 1) Representational Leverage (Galois)
Galois stopped looking at the *values* of roots and started looking at the *structure* of their permutations. This was not a better algorithm. It was a better abstraction. LLMs are often excellent at following existing abstractions, but proposing new abstractions is harder to validate without an external loop of tests, counterexamples, or proofs.

What this example shows is representational leverage. It does not show that only humans can ever do it. It does show that the hard part is not just deriving within a framework, but creating the framework that later derivations live inside.

### 2) The Simulation Prime (Einstein)
Einstein used **Gedankenexperimente** (thought experiments) as a low-fidelity world simulation. By "riding a light beam", he used internal world modeling to find a contradiction that algebra had not yet flagged. The math (Lorentz transformations) existed before he gave it the meaning of relativity.

What this example shows is the role of simulation in concept repair. It does not, by itself, settle the question of machine grounding. It does show why strong conceptual reasoning is not just symbol shuffling. A contradiction has to be registered at the level of a model of the world, not just at the level of token continuation.

### 3) Associative Latent Search (Ramanujan)
Ramanujan's autobiographical reports about "visions" are not laboratory measurements. Still, they illustrate a milder point: concept generation can occur before explicit formalization, and the route to a correct formula is not always a clean, linear derivation trace.

What this example shows is that generation and justification can be different phases. It does not license mysticism as an engineering method. The useful point is only that a final proof can be downstream of a much murkier concept-formation phase.

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

This example is useful because it sits right on the border between philosophy and engineering. The idempotency key is not just a prettier name. It is a new object in the ontology of the system. Once it exists, the invariant becomes thinkable, specifiable, and checkable in a way it was not before.

## Part V: the AGI capability gap

| Capability | Definition | Typical base-model status |
|---|---|---|
| **Syntactic Fluency** | Modeling the probability of token sequences. | **Exceptional** |
| **Derivative Semantic Use** | Using human meaning-bearing symbols coherently inside tasks and workflows. | **Often strong, but unstable over long horizons** |
| **Structural Concept Formation** | Inventing and stabilizing new formal objects through contradiction, repair, and reuse. | **Weak and hard to validate** |
| **Experiential Meaning** | Meaning tied to lived or embodied interaction with the world. | **No evidence in current base models** |
| **Strong Conceptual Reasoning** | Inventing and stabilizing new classes/types through structural pressure, simulation, contradiction, and repair. | **Weak and hard to validate** |
| **Meaning-Preserving Formalization** | Maintaining 1:1 mapping from intent to spec. | **Low Assurance (Drift)** |

## Part VI: two cautionary lenses (Rice and Searle)

To understand why text fluency should not be mistaken for semantic assurance, it helps to keep one technical lens and one philosophical lens in view:

### Rice's Theorem (The Technical Limit)
Any non-trivial semantic property of a program is undecidable by a general algorithm.
*   **Implication:** In full generality, semantics cannot be computed from syntax alone. High-assurance work uses restricted domains, extra structure, and explicit proof or counterexample obligations.

### The Chinese Room (The Philosophical Limit)
A clerk in a room following a rulebook to translate Chinese can "pass" as a speaker without knowing a word of Chinese.
*   **Implication:** Behavioral "passing" shows at most derivative competence with symbols. It does not by itself establish that the symbols are anchored by an internally stable conceptual scheme, still less by lived understanding.

Together, these are guardrails. Rice says syntax alone does not give semantic guarantees in the general case. The Chinese Room says syntax alone does not obviously give understanding in any rich sense merely from symbol manipulation. Neither argument proves that machine understanding is impossible in every future architecture, but both support caution about treating fluent text as settled evidence of concept possession.

## Part VII: the engineering cost of "Semantic Drift"

In high-assurance engineering, the most dangerous failure is **Semantic-to-Formal Drift**:

$$
\text{Human Intent} \neq \text{LLM-Generated Spec} \approx \text{Syntactically Valid Code}
$$

Because an LLM may not maintain stable semantic commitments for invariants (like "safety" or "liveness"), it can produce a specification that passes a linter but violates unstated assumptions. This is why high-assurance workflows use executable specs and formal solvers. Those tools can expose drift that syntax alone cannot see.

This is the engineering version of the philosophical point. Even if one brackets consciousness entirely, a workflow that relies on borrowed symbol use without stable ontology control is exposed to drift at exactly the moment where natural language becomes code, policy, or proof obligation.

## Part VIII: how to stress-test this thesis

Evidence against this tutorial's claim would look like a system that reliably demonstrates:

1. **Novel concept invention:** propose a new structure, then use it consistently across tasks where interpolation fails.
2. **Stable grounding:** maintain referential stability of core concepts across changing contexts and long horizons.
3. **Meaning-preserving formalization:** translate intent into formal artifacts with low semantic drift, verified by executable checks or proofs.
4. **Counterexample discipline:** seek refuters and edge cases as a default part of its own loop.

The first two items matter most for the stronger thesis. They are not just about fluent behavior. They are about whether the system can stabilize a concept rather than merely talk around one.

## Part IX: Conclusion (the practical path)

We do not need to wait for AGI to do high-assurance work. A workable present-day pattern is to treat humans, explicit specs, and external checks as the places where concepts are stabilized, while the LLM serves as a powerful proposal engine over inherited symbols.

1.  **Human or prior spec:** Defines the **Ontology** (the types, invariants, and intended meaning).
2.  **LLM:** Proposes the **Formalization** (the candidate implementation, explanation, or spec text).
3.  **Solver or checker:** Verifies the **Logic** (the proof obligation, executable constraints, or counterexample search).

This is the "Formal Philosophy" workflow: use models to propose, use explicit conceptual structure to stabilize the task, and use checkers to catch drift before it becomes authority.

## References
- Rice, H. G. (1953) *Classes of recursively enumerable sets and their decision problems*.
- Searle, J. (1980) *Minds, Brains, and Programs*.
- Harnad, S. (1990) *The Symbol Grounding Problem*.
- Wigner, E. (1960) *The Unreasonable Effectiveness of Mathematics in the Natural Sciences*.
