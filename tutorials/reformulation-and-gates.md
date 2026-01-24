---
title: Reformulation and compression (how changing the language changes the leverage)
layout: docs
kicker: Tutorial 5
description: Reformulation is translation that preserves meaning while unlocking better tools. Compression is the common thread, and neuro-symbolic gates turn proposals into evidence.
---

This tutorial is about a quiet superpower: saying the same thing in a different language, without changing what is true, and suddenly having stronger tools.

It is also about the other half of the story: when the language is powerful enough to express real systems, there are hard limits on what can be proven or solved automatically. That is where "propose, then gate with evidence" becomes a practical architecture.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Mental pictures to keep</p>
  <ul>
    <li>A problem as a shape that can be redrawn in many coordinate systems</li>
    <li>A reformulation space: representations as nodes, translations as edges</li>
    <li>Abstraction as compression: forget detail, keep the structure needed for a property</li>
    <li>Symbol manipulation as search with structure, not guessing</li>
    <li>Logic as a counterexample factory for universal claims</li>
    <li>Neuro-symbolic programming as a formal gate: propose, check, refute, refine</li>
  </ul>
</div>

## Part I: inside my head (the problem did not change, but the tool did)

I am staring at a puzzle that feels small, but the search space is enormous.

There is a row of lights, some on and some off. Each button press toggles a fixed pattern of lights. The goal is to turn all lights off.

At first, my mind tries the obvious: brute force, intuition, trial and error. It works for a small row, then collapses as the row grows.

Then I redraw the situation.

Instead of "a row of lights", I see a bitvector. Instead of "toggle", I see XOR. Instead of "a sequence of button presses", I see addition mod 2.

Now the puzzle is no longer a tree of guesses. It is a linear system over $\mathbb{F}_2$.

The board did not change. The meaning did not change. Only the representation changed. But the toolchain changed from "try moves" to "Gaussian elimination".

That is reformulation in one sentence:

> Keep the meaning fixed, change the language, and steal the best tools that language has.

## Part II: reformulation space (representations as a graph)

From far away, reformulation looks like a graph problem.

- Each **node** is a representation of the same underlying situation (a puzzle board, a vector, a formula).
- Each **edge** is a translation (sometimes lossless, sometimes approximate).
- Each node comes with a different library of tools (algebra, graph algorithms, SAT solving, model checking).

<figure class="fp-figure">
  <p class="fp-figure-title">Reformulation space</p>
  {% include diagrams/reformulation-space.svg %}
  <figcaption class="fp-figure-caption">
    A problem can be expressed in many representations. Translations that preserve meaning let tools move with you. The leverage comes from landing in a representation with mature methods.
  </figcaption>
</figure>

To make this precise, we reuse the distinctions from Tutorial 2:

- **Isomorphism:** a 1-to-1, invertible, structure-preserving translation.
- **Equivalence:** a many-to-one "same meaning" relation (often defined via a semantics function).
- **Sound abstraction:** a deliberate forgetting that preserves a chosen property, even if it merges distinct concrete states.
- **Encoding/simulation:** one formalism can represent another's behavior, but not as a simple 1-to-1 correspondence.

Reformulation is not only isomorphism. It is the broader habit of moving along meaning-preserving edges whenever possible, and along sound abstraction edges when the goal is a property rather than exact reconstruction.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Speculative reformulations still belong in the picture</p>
  <p>
    Some proposals, like “it from bit” or “digital physics”, suggest that the most fundamental
    description of reality is informational or computational. These are best viewed as hypotheses about
    a future reformulation edge.
  </p>
  <p>
    The standard is the same: make the translation explicit, and show that it preserves the predictions
    we already trust.
  </p>
</div>

<figure class="fp-figure">
  <p class="fp-figure-title">A speculative edge in reformulation space</p>
  {% include diagrams/speculative-reformulation.svg %}
  <figcaption class="fp-figure-caption">
    Not every “same thing” claim is an isomorphism. Some are research programs. The discipline is to
    label the edge type and demand evidence.
  </figcaption>
</figure>

### Three examples of leverage-by-reformulation

This is the move, repeated with different clothing.

1. **Toggle puzzle to linear algebra**  
   Lights Out style puzzles become $A x = b$ over $\mathbb{F}_2$. The solver is elimination, not search.

2. **Circuit equivalence to SAT**  
   To prove $C_1(x) = C_2(x)$ for all inputs, search for a counterexample input $x$ such that $C_1(x) \ne C_2(x)$. If SAT says UNSAT, there is no counterexample.

3. **Deadlock to cycle detection**  
   A "wait-for graph" converts deadlock into a directed cycle question. The solver is graph theory.

None of these translations are motivational quotes. They are rigorous changes of representation that preserve the truth of the question being asked.

## Interlude: two working examples (Tao and Feynman)

Two of the cleanest real-world examples of abstraction and reformulation come from modern mathematics and modern physics.

### Terence Tao: split one hard object into two easier ones

A recurring method in additive combinatorics and analytic number theory is the "structure vs randomness" split:

- take a complicated object (often a function or a set),
- decompose it into a structured part and a pseudorandom part,
- use the right tool on each part,
- then combine the results.

The structured part is chosen so that it can be described compactly and manipulated algebraically.
The pseudorandom part is chosen so that it is invisible to the patterns being counted (it has small correlation with the relevant test functions).

This is abstraction as compression with a target property in view.
The split forgets detail differently depending on the question, but it keeps exactly what makes the proof go through.

<figure class="fp-figure">
  <p class="fp-figure-title">Tao style decomposition: structure plus randomness</p>
  {% include diagrams/tao-structure-randomness.svg %}
  <figcaption class="fp-figure-caption">
    The point is not the exact split. The point is choosing a representation where each piece can be handled by a mature toolchain.
  </figcaption>
</figure>

If you want an entry point written as a guide to this mindset, see Tao’s book *Structure and Randomness*.

### Richard Feynman: replace a formula jungle with a diagrammatic calculus

In quantum field theory, the objects that appear in calculations can become enormous symbolic expressions.

Feynman’s diagram technique is a reformulation move:

- represent an interaction process as a graph with typed parts,
- translate the graph into a mathematical term by fixed rules,
- sum the contributions.

The diagram is not an illustration added after the fact.
It is a compressed representation of a term in a perturbative expansion, designed so the right combinatorics is visible at a glance.

<figure class="fp-figure">
  <p class="fp-figure-title">Feynman diagrams as a compressed representation</p>
  {% include diagrams/feynman-diagrams-reformulation.svg %}
  <figcaption class="fp-figure-caption">
    The underlying physics is the same. The point is that the diagram makes the structure of the computation explicit, which makes it easier to manipulate correctly.
  </figcaption>
</figure>

## Part III: abstraction as compression (and why compression feels like understanding)

The Abstraction Cheat Sheet has a strong rule of thumb:

> Abstraction means: forget some implementation detail, while preserving the structure needed to reason about a property.

This is not vagueness. It is a controlled blur.

One clean way to write the idea is as a map:

- concrete states: $C$
- abstract states: $A$
- abstraction: $\alpha : C \to A$

Typically, $\alpha$ is many-to-one. That is the point. Many concrete states collapse to one abstract state.

Compression is a closely related lens. A compression scheme has:

- an encoder $enc : X \to Z$
- a decoder $dec : Z \to X$
- and a promise that $dec(enc(x)) = x$ for the data of interest

Abstraction is usually not like that. It does not promise invertibility. It is not lossless.

But abstraction and compression rhyme:

- Both create a smaller object that stands in for a larger one.
- Both succeed only when the smaller object preserves the structure needed for the task.
- Both fail when they merge distinctions that matter.

<figure class="fp-figure">
  <p class="fp-figure-title">Shrink behavior, compress representation, abstract by merging</p>
  {% include diagrams/state-space-shrink-compress.svg %}
  <figcaption class="fp-figure-caption">
    Not all “making it smaller” moves are the same. Some change what the system can do, some keep behavior and change representation, and some merge states to preserve only selected properties.
  </figcaption>
</figure>

### Why compression looks like intelligence (without turning it into a slogan)

When a mind learns a pattern, one useful way to describe what happened is:

- many experiences got mapped into a smaller internal representation,
- that representation kept the regularities that matter,
- and the result can now be used to predict, plan, or explain.

This is why "having a model" and "being able to compress" feel close.

But it is important not to oversell it:

- Compression is not the only ingredient of intelligence.
- There are many incompatible notions of "best compression".
- Some tasks are hard even with the best representation.

So the safe claim is modest: good abstractions are compressions that preserve the right structure, and finding them is a major source of cognitive and mathematical leverage.

## Part IV: symbol manipulation (why rewriting can beat guessing)

From the outside, symbolic reasoning can look like moving marks around.

From the inside, it is search with rails.

Two examples:

1. **Algebraic simplification**  
   A rewrite like $(x + y)^2 = x^2 + 2xy + y^2$ is not a guess. It is a meaning-preserving transformation that changes what tools can see.

2. **SAT and SMT solving**  
   A SAT solver does not enumerate all $2^n$ assignments. It propagates constraints, learns from conflicts, and prunes vast regions of the search space because the syntax has structure.

Symbol manipulation becomes powerful when:

- the transformations are guaranteed to preserve meaning, and
- the representation exposes the right local structure for pruning and composition.

This is reformulation again, but inside a language rather than between languages.

## Part V: why logic is powerful, and why it cannot be the whole story

Logic is the mathematics of "must".

Its most practical move is to turn a universal claim into a refutable target:

$$
\forall x.\, P(x)
$$

becomes:

$$
\text{find } x \text{ such that } \lnot P(x)
$$

If the solver finds such an $x$, that $x$ is a counterexample witness. If it proves none exists (in a decidable setting), the universal claim holds.

### Limits: undecidability and intractability

There are two clean, non-negotiable constraints on what logic can do for software:

1. **Undecidability:** for sufficiently expressive languages (general programs), many interesting questions have no algorithm that always terminates with the right yes/no answer.

2. **Intractability:** even when a problem is decidable (SAT is the classic example), worst-case complexity can be enormous. Modern solvers win by exploiting structure, not by defeating the worst case.

A deeper limit lives even in pure mathematics: in any sufficiently strong formal system, there are true statements that cannot be proven within that system (incompleteness). In software terms, this is a reminder that "formal" does not mean "omniscient". It means "explicit about assumptions and rules".

That is why formal methods is full of tradeoffs:

- restrict the language (finite-state models, bounded verification) to regain decidability,
- accept approximations (sound abstractions) to regain scalability,
- or accept incompleteness (find bugs reliably, but do not always prove absence of bugs).

## Part VI: ultrafinitism (when “existence” means “feasible”)

Most working mathematics treats natural numbers as an unbounded infinity: for any $n$, there exists $n+1$.

Ultrafinitism is a family of views that pushes back on that comfort by treating feasibility as foundational.
Strict finitism is one especially sharp version: it rejects not only actual infinity but also potential infinity in arithmetic.

The core intuition is feasibility:

- It is one thing to say "a number exists" in a formal system.
- It is another to say it can be constructed, represented, or used in any meaningful way.

Historically, ultrafinitist ideas show up as a response to foundational debates about infinity, and as a response to the physical reality that reasoning is computation done by finite beings.

One way to keep the history grounded is to name a few signposts (not a complete timeline):

- **1958:** Hao Wang surveys foundational work and explicitly centers concepts like proof and feasible number, proposing "anthropologism" as one feasibility-oriented domain.
- **1959 to 1961:** Alexander Esenin-Volpin presents an "ultra-intuitionistic" program for foundations (often discussed as an ultrafinitist influence).
- **1982:** Crispin Wright argues for strict finitism as a philosophical position in the philosophy of mathematics.
- **Today:** strict finitism continues as a live topic. One formulation posits a largest natural number, with variants that treat the successor of that number as undefined or as looping back to itself.

This matters for formal methods because it puts a spotlight on a practical truth:

- Proofs, models, and counterexamples are not only about truth. They are also about resources: time, memory, and proof length.

Even if one rejects ultrafinitism as a foundation, the engineering lesson remains: feasibility is part of reliability.

## Part VII: the Lighthill report (a warning about demos without guarantees)

In July 1972, Sir James Lighthill completed a survey report on AI for the UK Science Research Council (often discussed by its 1973 publication).

One of the report’s themes was that many AI approaches ran into combinatorial explosion when scaled, and that demonstrations in small or toy settings did not necessarily carry to the general case.

In June 1973, a BBC TV debate about the report took place at the Royal Institution. The report and the surrounding debate are often cited as part of the story of reduced UK funding for AI research in that era.

The reason it belongs in this tutorial is not nostalgia. It is a pattern:

- A system can look good in a demo.
- A claim about "always" needs a different kind of support.

Formal methods is what it looks like to take the second kind of claim seriously: state the property, then search for refuters, not applause.

## Part VIII: neuro-symbolic programming (propose, then gate with evidence)

Here is a definition that is practical enough to build systems around:

> Neuro-symbolic programming is a workflow where models propose ideas, hypotheses, candidates, or code, but final outputs are formally gated by evidence-based checks.

The model is a generator. The symbolic layer is a judge.

<figure class="fp-figure">
  <p class="fp-figure-title">Neuro-symbolic gate (propose, check, refute)</p>
  {% include diagrams/neuro-symbolic-gate.svg %}
  <figcaption class="fp-figure-caption">
    A model can explore a large space of candidates. A formal checker decides which candidates are allowed, and returns counterexamples when a candidate is wrong.
  </figcaption>
</figure>

This is a close cousin of CEGIS:

<figure class="fp-figure">
  <p class="fp-figure-title">Counterexample-guided synthesis as a template</p>
  {% include diagrams/cegis-loop.svg %}
  <figcaption class="fp-figure-caption">
    Proposals become stronger only by surviving refuters. This loop is the opposite of “seems plausible”.
  </figcaption>
</figure>

### Why it is powerful

This architecture combines two strengths:

- **Models** are good at proposing candidates in huge, fuzzy spaces (programs, proofs, rewrites, plans).
- **Formal methods** are good at saying "no" precisely, with a witness.

When a system is built so that "no" comes with a counterexample trace, iteration becomes cumulative.

The loop turns a vague prompt into an ever tighter constraint set. Over time, the spec and the candidate converge.

### What it does not solve

Formal gates do not remove the need for good specs.

If the specification is wrong, incomplete, or expressed in the wrong abstraction, the gate can approve the wrong thing. A gate is only as good as the property it checks.

So the deepest skill here is the same one that started the tutorial:

- reformulate until the meaning is clear, and
- choose the abstraction that matches the property being claimed.

## References (entry points, not prerequisites)

- Abstraction Cheat Sheet: https://thedarklightx.github.io/Beyond-Code-Abstraction-Cheatsheet/
- Solar-Lezama, *Introduction to Program Synthesis (Lecture 1)*: https://people.csail.mit.edu/asolar/SynthesisCourse/Lecture1.htm
- Tao, *Structure and Randomness: An Introduction to Probabilistic Combinatorics* (2008): https://bookstore.ams.org/gsm-76
- Feynman, *Space-Time Approach to Quantum Electrodynamics* (1949): https://journals.aps.org/pr/abstract/10.1103/PhysRev.76.769
- Wang, *Eighty years of foundational studies* (1958): https://philpapers.org/rec/WANEYO
- Wright, *Strict Finitism* (1982): https://philpapers.org/rec/WRISF
- de Oliveira, *Is strict finitism arbitrary?* (2024): https://academic.oup.com/pq/advance-article/doi/10.1093/pq/pqae093/7730546
- Seisenberger and Sterkenburg, *A strict finitistic logic* (2023): https://link.springer.com/article/10.1007/s11229-022-03962-4
- Lighthill, *Artificial Intelligence: A General Survey* (1973): http://www.chilton-computing.org.uk/inf/literature/reports/lighthill_report/p001.htm
- McCarthy, *Review of “Artificial Intelligence: A General Survey”* (1973): http://www-formal.stanford.edu/jmc/reviews/lighthill/lighthill.html
- University of Edinburgh AIAI, *Lighthill Report and debate* (1972 to 1973): https://aiai.ed.ac.uk/project/lighthill/
- Agar, *What is the AI Winter?* (2020): https://www.cambridge.org/core/journals/bjhs-themes/article/what-is-the-ai-winter/F0D1E0F6D434D4A73D79DDDF5646ED46
