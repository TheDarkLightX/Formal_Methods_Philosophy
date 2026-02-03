---
title: Reformulation and compression (how changing the language changes the leverage)
layout: docs
kicker: Tutorial 5
description: Reformulation is translation that preserves meaning while unlocking better tools. Compression is the common thread, and neuro-symbolic gates turn proposals into evidence.
---

This tutorial is about a quiet superpower: saying the same thing in a different language, without changing what is true, and suddenly having stronger tools.

It is also about the other half of the story. Once a language is expressive enough to talk about real systems, there are hard limits on what can be proven or solved automatically. That is where "propose, then gate with evidence" becomes a practical architecture.

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

There is a row of lights, some on and some off. A button press flips a fixed pattern. The goal is the all-off board.

For a few lights, I can get away with guessing. As the row grows, guessing turns into noise. Each press branches the future, and I cannot see a reliable path.

Then I redraw the situation.

Instead of "a row of lights", I see a bitvector. Instead of "toggle", I see XOR. Instead of "a sequence of button presses", I see addition mod 2.

Now the puzzle is no longer a tree of guesses. It is a linear system over $\mathbb{F}_2$.

The board did not change. The question did not change. Whether a solution exists did not change.
Only the representation changed. The toolchain changed from "try moves" to "Gaussian elimination".

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
    A problem can be expressed in many representations. Translations that preserve meaning let tools travel across representations. The leverage comes from landing in a representation with mature methods.
  </figcaption>
</figure>

To make this precise, we reuse the distinctions from Tutorial 2:

- **Isomorphism:** a 1-to-1 translation that is reversible and preserves the operations and relations in view.
- **Equivalence:** a "same meaning" relation, often defined by equality after applying a semantics function.
- **Sound abstraction:** a deliberate merge of distinctions that preserves a chosen property (often one-way).
- **Encoding/simulation:** one formalism represents another's behavior, but not as a simple 1-to-1 correspondence.

<figure class="fp-figure">
  <p class="fp-figure-title">Many descriptions, one meaning</p>
  {% include diagrams/description-to-meaning.svg %}
  <figcaption class="fp-figure-caption">
    A reformulation is safe only if it preserves meaning. Naming the semantics map is a way to keep that promise honest.
  </figcaption>
</figure>

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

### Four examples of leverage-by-reformulation

This is the move, repeated with different clothing.

1. **Toggle puzzle to linear algebra**  
   Represent board states as vectors in $\{0,1\}^n$ and moves as additions mod 2. Then "is there a sequence of moves that reaches all-off?" becomes "does a linear system $A x = b$ over $\mathbb{F}_2$ have a solution?" The solver is elimination, not branching search.

2. **Circuit equivalence to SAT**  
   Two circuits are equivalent exactly when there is no input that makes their outputs differ. Build a formula for $C_1(x) \ne C_2(x)$ and ask a SAT solver for a satisfying assignment. A model is a concrete counterexample input. UNSAT means no counterexample exists.

3. **Deadlock to cycle detection**  
   Build a wait-for graph with an edge $A \to B$ meaning "A is waiting for B". A deadlock corresponds to a directed cycle. The solver is graph theory.

4. **Program synthesis to logic learning by relational decomposition**  
   Many synthesis systems treat each example as a whole pair: an input structure and an output structure. A different representation is to decompose the structures into relational facts, like <code>in(index,value)</code> and <code>out(index,value)</code>. Then learning becomes: find a logic program that entails the output facts from the input facts. Hocquette and Cropper show that this reformulation can make hard synthesis problems much easier to solve using an off-the-shelf inductive logic programming system.

<figure class="fp-figure">
  <p class="fp-figure-title">Relational decomposition: one example becomes many facts</p>
  {% include diagrams/relational-decomposition.svg %}
  <figcaption class="fp-figure-caption">
    This is not "adding magic". It is a meaning-preserving representation change that makes the search local and compositional.
  </figcaption>
</figure>

These are not metaphors. They are meaning-preserving translations. The only real obligation is the one that matters: show that the translation preserves the question being asked.

## Interlude: two working examples (Tao and Feynman)

Two of the cleanest real-world examples of abstraction and reformulation come from modern mathematics and modern physics.

### Terence Tao: split one hard object into two easier ones

A recurring method in additive combinatorics and analytic number theory is the "structure vs randomness" split:

- take a complicated object (often a function or a set),
- decompose it into a structured part and a pseudorandom part,
- use the right tool on each part,
- then combine the results.

The structured part is chosen so that it can be described compactly and manipulated algebraically.
The pseudorandom part is chosen so that, for the patterns being counted, it behaves like noise (it has small correlation with the relevant test functions).

This is abstraction as compression with a target property in view.
The split forgets detail differently depending on the question, but it keeps exactly what makes the proof go through.

<figure class="fp-figure">
  <p class="fp-figure-title">Tao style decomposition: structure plus randomness</p>
  {% include diagrams/tao-structure-randomness.svg %}
  <figcaption class="fp-figure-caption">
    The point is not the exact split. The point is choosing a representation where each piece can be handled by a mature toolchain.
  </figcaption>
</figure>

For an entry point written as a guide to this mindset, see Tao’s book *Structure and Randomness*.

### Richard Feynman: replace a formula jungle with a diagrammatic calculus

In quantum field theory, the objects that appear in calculations can become enormous symbolic expressions.

Feynman’s diagram technique is a reformulation move:

- represent an interaction process as a graph with typed parts,
- translate the graph into a mathematical term by fixed rules,
- sum the contributions.

The diagram is not an illustration added after the fact.
It is a compressed representation of a term in a perturbative expansion, designed so the bookkeeping is visible and repeatable.

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
It is a camera with a focus ring: some details are deliberately out of focus so the relevant shape is sharp.

One clean way to write the idea is as a map:

- concrete states: $C$
- abstract states: $A$
- abstraction: $\alpha : C \to A$

Typically, $\alpha$ is many-to-one. That is the point. Many concrete states collapse to one abstract state.

Compression is a closely related lens. A compression scheme has:

- an encoder $enc : X \to Z$
- a decoder $dec : Z \to X$
- and a promise that $dec(enc(x)) = x$ for the data of interest

If that promise holds on a set $X$, then the encoding is lossless on $X$. The original can be recovered exactly.

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
A child does not memorize every chair. They form a concept that throws away detail but preserves what matters for a goal like sitting.

But it is important not to oversell it:

- Compression is not the only ingredient of intelligence.
- There are many incompatible notions of "best compression".
- Some tasks are hard even with the best representation.

So the safe claim is modest: good abstractions are compressions that preserve the right structure, and finding them is a major source of cognitive and mathematical leverage.

## Part IV: symbol manipulation (why rewriting can beat guessing)

From the outside, symbolic reasoning can look like moving marks around.

From the inside, it is search with rails.

Three examples:

1. **Algebraic simplification**  
   A rewrite like $(x + y)^2 = x^2 + 2xy + y^2$ is not a guess. It is a meaning-preserving transformation that changes what tools can see.

2. **SAT and SMT solving**  
   A SAT solver does not enumerate all $2^n$ assignments. It propagates constraints, learns from conflicts, and prunes vast regions of the search space because the syntax has structure.

3. **Unification and type inference**  
   Type inference solves systems of equations between types by unification. The "symbols moving around" are the constraints being made consistent.

Symbol manipulation becomes powerful when:

- the transformations are guaranteed to preserve meaning, and
- the representation exposes the right local structure for pruning and composition.

This is reformulation again, but inside a language rather than between languages.

At the bottom, this is not mystical. It is what computation is.

A Turing machine is symbol manipulation: it reads a symbol, writes a symbol, moves left or right, and changes an internal state. That is controlled rewriting. Everything above it is a more ergonomic language for the same core act.

## Part V: why logic is powerful, and why it cannot be the whole story

Logic is the mathematics of "must".

It is also a reading discipline. Small symbols carry fixed meanings, so a short formula can say exactly what a long paragraph tries to gesture at.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Logic legend (how to read the symbols)</p>
  <div class="fp-prose">
    <table>
      <thead>
        <tr>
          <th>Symbol</th>
          <th>Read as</th>
          <th>Meaning (informal)</th>
        </tr>
      </thead>
      <tbody>
        <tr><td><code>∀</code></td><td>for all</td><td>universal claim</td></tr>
        <tr><td><code>∃</code></td><td>there exists</td><td>existential claim</td></tr>
        <tr><td><code>.</code></td><td>such that</td><td>separator between a binder (<code>∀x</code>, <code>∃x</code>) and its body</td></tr>
        <tr><td><code>∧</code></td><td>and</td><td>both must hold</td></tr>
        <tr><td><code>∨</code></td><td>or</td><td>at least one holds</td></tr>
        <tr><td><code>¬</code></td><td>not</td><td>negation</td></tr>
        <tr><td><code>→</code></td><td>implies</td><td>if left holds, right must hold</td></tr>
        <tr><td><code>↔</code></td><td>if and only if</td><td>both directions of implication</td></tr>
        <tr><td><code>∈</code></td><td>is in</td><td>membership, as in <code>x ∈ S</code></td></tr>
        <tr><td><code>*</code></td><td>times</td><td>usually multiplication (not a standard logical connective; for logical “and”, use <code>∧</code>)</td></tr>
        <tr><td><code>:=</code></td><td>defined as</td><td>a definition, not a claim to prove</td></tr>
        <tr><td><code>⊢</code></td><td>derives</td><td>there is a valid proof from premises to conclusion</td></tr>
        <tr><td><code>∴</code></td><td>therefore</td><td>the conclusion follows</td></tr>
      </tbody>
    </table>
    <p>
      Many authors write <code>∀x. P(x)</code>, <code>∀x, P(x)</code>, or <code>∀x (P(x))</code>. These are the same idea: “for all <code>x</code>, <code>P(x)</code>”.
      Similarly, <code>∃x. P(x)</code> means “there exists an <code>x</code> such that <code>P(x)</code>”.
    </p>
    <p>
      In this tutorial, a symbol like <code>P</code> is usually a <em>predicate</em> (a property or relation), so <code>P(x)</code> is a statement that can be true or false.
      It does not mean “a function of <code>P</code>”.
      A helpful contrast is <code>f(x)</code>, where <code>f</code> is a function symbol and <code>f(x)</code> names a value.
      Predicates can be viewed as boolean-valued functions on the domain, but they are used as formulas (claims), not as values.
    </p>
    <p>
      A common shorthand is <code>∀x ∈ S. P(x)</code>, read “for all <code>x</code> in <code>S</code>, <code>P(x)</code>”. Formally, it expands to
      <code>∀x. (x ∈ S → P(x))</code>. Likewise, <code>∃x ∈ S. P(x)</code> expands to <code>∃x. (x ∈ S ∧ P(x))</code>.
      Parentheses indicate what binds to what, the same way they do in algebra.
    </p>
    <p><strong>Operator precedence and scope (a PEMDAS-like convention)</strong></p>
    <p>
      Logic does not have a single universal precedence standard, but most texts follow a "tightest to loosest" convention close to:
    </p>
    <ol>
      <li>Parentheses: <code>(...)</code></li>
      <li>Negation: <code>¬P</code></li>
      <li>Conjunction: <code>P ∧ Q</code></li>
      <li>Disjunction: <code>P ∨ Q</code></li>
      <li>Implication: <code>P → Q</code></li>
      <li>Biconditional: <code>P ↔ Q</code></li>
    </ol>
    <p>
      Quantifiers (<code>∀x</code>, <code>∃x</code>) are not "infix operators" like <code>∧</code>. They introduce a bound variable, and their scope is the formula they govern.
      This tutorial uses <code>∀x. ...</code> and <code>∃x. ...</code> (dot as a scope marker) to keep that scope explicit.
    </p>
    <p>
      Examples under the convention above:
      <code>¬P ∧ Q</code> parses as <code>(¬P) ∧ Q</code>.
      <code>P ∧ Q → R</code> parses as <code>(P ∧ Q) → R</code>.
      <code>P → Q ∧ R</code> parses as <code>P → (Q ∧ R)</code>.
      For chained operators, conventions vary, but <code>∧</code> and <code>∨</code> are usually treated as associative, and <code>→</code> is often treated as right-associative.
      In ambiguous cases, parentheses are the only universally correct disambiguation.
    </p>
  </div>
</div>

### A paragraph of formulas can out-precise a page of English

Take the turnstile rules from Tutorial 3 and say them in a tiny logic language.

Let:

- $\mathrm{state}_t \in \{0,1\}$ where 0 means Locked and 1 means Unlocked
- $\mathrm{coin}_t \in \{0,1\}$ and $\mathrm{push}_t \in \{0,1\}$
- $\mathrm{alarm}_t \in \{0,1\}$

Now the rules fit in a few lines:

$$
\forall t.\, \mathrm{state}_t \in \{0,1\}
$$

$$
\forall t.\, \mathrm{push}_t = 1 \to \mathrm{state}_{t+1} = 0
$$

$$
\forall t.\, (\mathrm{state}_t = 0 \land \mathrm{coin}_t = 1 \land \mathrm{push}_t = 0) \to \mathrm{state}_{t+1} = 1
$$

$$
\forall t.\, \mathrm{alarm}_t = 1 \leftrightarrow (\mathrm{state}_t = 0 \land \mathrm{push}_t = 1)
$$

This looks dense at first, but notice what it buys:

- no ambiguity about time (it says exactly which step looks at which state),
- no ambiguity about cases (each implication has an explicit condition),
- and a path to automation (a solver can search for a counterexample trace).

English can say the same thing, but it tends to hide these commitments in phrasing. Logic makes the commitments explicit.

### Modus ponens (one step of deduction)

Reasoning is not a vibe. It is rule-governed movement from premises to conclusions.

The most famous rule is **modus ponens**:

$$
\text{from } A \text{ and } (A \to B) \text{ infer } B
$$

In turnstile form, suppose:

$$
\mathrm{state}_7 = 0 \land \mathrm{push}_7 = 1
$$

and we have the rule:

$$
(\mathrm{state}_7 = 0 \land \mathrm{push}_7 = 1) \to \mathrm{alarm}_7 = 1
$$

Then we can conclude:

$$
\therefore \mathrm{alarm}_7 = 1
$$

This is what "deduction" means in its cleanest form: the conclusion is forced by the premises under the rules of the logic.

### Induction (prove it for all time steps)

Many program claims have the shape "for all steps, an invariant holds". Mathematical induction matches that shape.

To prove $\forall t.\, I(t)$ by induction, one proves:

1. **Base case:** $I(0)$.
2. **Step case:** $\forall t.\, (I(t) \to I(t+1))$.

Then $I(t)$ holds for every natural number $t$.

This is the skeleton behind many safety proofs: start with an initial condition, show every transition preserves the invariant, and conclude the invariant holds forever.

Its most practical move is to turn a universal claim into a refutable target:

$$
\forall x.\, P(x)
$$

becomes:

$$
\text{find } x \text{ such that } \lnot P(x)
$$

In pure logic notation, this is the same shape:

$$
\lnot(\forall x.\, P(x)) \leftrightarrow \exists x.\, \lnot P(x)
$$

If the solver finds such an $x$, that $x$ is a counterexample witness. If it proves none exists (in a decidable setting), the universal claim holds.

### What "reasoning" is (and what language models simulate)

In this tutorial, "reasoning" means this:

- there is a language with semantics (the symbols mean something),
- there are rules for valid steps (proof rules, solver rules, algebraic rewrite rules),
- and a conclusion is trusted because it can be checked against those rules.

This gives three related words sharp meanings:

- **Deduction:** deriving a conclusion that is forced by premises. In symbols, $\Gamma \vdash \varphi$ means "from assumptions $\Gamma$, the conclusion $\varphi$ is derivable by valid rules".
- **Induction:** a proof pattern for claims over time or natural numbers. It is still deduction, but it proves $\forall t.\, I(t)$ via a base case and a step case.
- **Abduction:** proposing a plausible hypothesis that would explain the observations. Abduction is useful, but it is not a proof.

The difference matters because a lot of human confusion comes from mixing them.

Language models can produce text that looks like reasoning, including proofs and derivations. Sometimes it is correct.

But the model is not forced to be correct by default. It is trained to produce plausible continuations of text.
It often behaves like a strong abductive engine: it proposes hypotheses and fills in missing steps in a way that looks coherent.

That coherence can be real reasoning, or it can be **pseudo reasoning**: a sequence of steps that reads like deduction but does not actually follow the rules. The gap is not always obvious to a human reader, especially when the surface form is fluent.

This is why neuro-symbolic gates matter: treat the model as a proposer in a large space, and treat a checker as the mechanism that turns "looks right" into "is right, because it passed a refuter".

### Limits: undecidability and intractability

There are two clean, non-negotiable constraints on what logic can do for software:

1. **Undecidability:** for sufficiently expressive languages (general programs), many interesting questions have no algorithm that always terminates with the right yes/no answer.
   The halting problem is the classic example.

2. **Intractability:** even when a problem is decidable (SAT is the classic example), worst-case complexity can be enormous. Modern solvers win by exploiting structure, not by defeating the worst case.
   This is why representation choice matters so much. It is often the difference between "hopeless" and "instant".

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

One way to feel the motivation is physical: there are numbers that cannot be written down in the observable universe. Ultrafinitism treats that gap between "defined in a theory" and "usable in reality" as mathematically significant.

Historically, ultrafinitist ideas show up as a response to foundational debates about infinity, and as a response to the physical reality that reasoning is computation done by finite beings.

One way to keep the history grounded is to name a few signposts. This is not a complete timeline, and labels vary by author:

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
It is the same shape as the lights puzzle: a branching tree that looks manageable until it suddenly is not.

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

Put as a slogan: learn broadly, then gate formally where correctness matters.

When a system is built so that "no" comes with a counterexample trace, iteration becomes cumulative.

Here is the concrete shape of the workflow:

- a model proposes a candidate (a patch, a rule, a table update, a plan),
- the gate checks it against explicit constraints,
- if it fails, the output is not "seems wrong". It is a smallest witness, like an input that breaks a claim or a trace that violates an invariant,
- the next proposal is conditioned on that witness.

The loop turns vague intent into explicit constraints. Each counterexample is information that can be carried forward.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">A concrete example</p>
  <p>
    Imagine an agent proposes an implementation of the turnstile from Tutorial 3. The spec says: if the
    previous state is Locked and the input is Push, then the alarm must be 1. The gate runs a checker.
  </p>
  <p>
    If the implementation is wrong, the gate does not respond with a vibe. It returns a witness trace,
    like a short sequence of inputs (Coin, Push, Push) that leads to a violated invariant. That trace is
    new information the next proposal can directly address.
  </p>
</div>

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
- Hocquette and Cropper, *Relational Decomposition for Program Synthesis* (2024): https://arxiv.org/abs/2408.12212
