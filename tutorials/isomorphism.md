---
title: Isomorphism (same structure, different names)
layout: docs
kicker: Tutorial 2
description: A 1-to-1, structure-preserving translation that lets the same problem be expressed in the language where the tools are strongest.
---

This tutorial is about a very specific promise: translate there and back, and end where things started.

When two descriptions are connected by a 1-to-1 translation that is reversible and preserves the operations/relations in view, mathematicians say the structures are **isomorphic**.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Mental pictures to keep</p>
  <ul>
    <li>Two perfect ledgers for the same hidden situation</li>
    <li>A translation that runs forward and backward</li>
    <li>The same melody in a different key (renaming without changing structure)</li>
    <li>Abstraction as forgetting detail while preserving what matters</li>
    <li>Equivalence classes: many descriptions, one meaning</li>
    <li>Curry-Howard: proofs and programs as two views of one structure</li>
  </ul>
</div>

## Part I: inside my head (two perfect ledgers)

I'm watching cards come off a shoe.

If my goal is **perfect** tracking (not card counting), then what I want to know is a real, definite object:
the *exact multiset of remaining cards*.

But I still have a choice about *representation*. I have to pick what kind of notebook page I keep.

### Ledger A: a multiset (a "bag") of remaining cards

Let `Card` be the 52 distinct card labels in a standard deck (rank + suit).

If I ignore order and I'm modeling a single deck, then the exact remaining deck really is a subset $R \subseteq Card$: each card-label is either still in the shoe or it isn't.

That space already has $2^{52} = 4{,}503{,}599{,}627{,}370{,}496$ (about 4.5 quadrillion) possible remaining-subset states.

For a multi-deck shoe, the remaining cards form a **multiset** `R` over `Card`: a "bag" where order does not matter but multiplicity does.

### Ledger B: a 52-entry count table

Instead of writing a bag, I can keep a tally sheet with 52 rows, one per card-label.

That table is a function:

$$
m_R : Card \to \mathbb{N}
$$

where $m_R(c)$ is "how many copies of card-label $c$ remain".

If I choose a fixed ordering of the 52 card labels $c_1,\dots,c_{52}$, then the same information is a vector:

$$
v_R = (m_R(c_1), \dots, m_R(c_{52})) \in \mathbb{N}^{52}.
$$

### The 1-to-1 map (and why it is structure-preserving)

There are two translations:

- `encode(R) = v_R` (count how many of each card-label remains)
- `decode(v)` = "the multiset with $v_i$ copies of $c_i$"

These translations are inverses: `decode(encode(R)) = R` and `encode(decode(v)) = v`.

That is already the core idea of **isomorphism**: different surface forms, exactly the same underlying structure.

It is not just a bijection of "data"; it also respects the operations I do mentally:

- Removing a card from the multiset corresponds to subtracting 1 from exactly one coordinate of the vector.
- Combining bags corresponds to pointwise addition of vectors.

So "bag of cards" and "52-entry count table" are not two different states of the world.
They are the **same** state written in two different languages.

<figure class="fp-figure">
  <p class="fp-figure-title">Isomorphism as a reversible translation</p>
  {% include diagrams/isomorphism-encode-decode.svg %}
  <figcaption class="fp-figure-caption">
    The left and right ledgers look different, but they carry the same information. "encode" and "decode" go both ways, and updates on one side correspond to updates on the other.
  </figcaption>
</figure>

### What card counting is not (not an isomorphism)

In the first tutorial, the running count was an **abstraction**: many different concrete decks map to the same integer.

That map is useful, but it is not invertible.
If all I know is a running count of `+2`, there are many possible remaining compositions consistent with it, and I cannot reconstruct the exact deck.

So: isomorphism is lossless re-encoding (1-to-1 and invertible). Abstraction is deliberate forgetting (typically many-to-1, not invertible).

## Part II: zooming out (a precise definition)

Informally: two structures are isomorphic if they have the same "shape".

Formally, fix a *signature* (the operations and relations in view). A structure $A$ consists of:

- an underlying set $|A|$,
- interpretations of the signature's function symbols (operations) on $|A|$,
- interpretations of the signature's relation symbols on $|A|$,
- and (optionally) constants.

An **isomorphism** $f : |A| \to |B|$ between structures $A$ and $B$ (with the same signature) is a bijection such that:

- for every operation $op$, $f(op_A(a_1,\dots,a_n)) = op_B(f(a_1),\dots,f(a_n))$,
- for every relation $R$, $R_A(a_1,\dots,a_n)$ holds iff $R_B(f(a_1),\dots,f(a_n))$ holds,
- and constants map to constants.

If such an $f$ exists, write $A \cong B$.

This one definition powers many "same thing, different notation" moves:

- In **sets**, an isomorphism is just a bijection.
- In **groups**, an isomorphism is a bijection that preserves the group operation.
- In **graphs**, an isomorphism is a bijection on vertices that preserves adjacency.

A useful picture: draw the structure as "things + wiring" (elements plus the relations/operations between them). An isomorphism is a renaming of the things that leaves the wiring unchanged.

The point is not that the symbols are fancy. The point is the promise:
any statement expressible *in the chosen language* has the same truth value after renaming elements via the isomorphism.

## Part III: different abstractions, and when they are secretly the same thing

A useful software-side reference for the ideas in this section is the
[Software Abstraction Cheat Sheet](https://thedarklightx.github.io/Beyond-Code-Abstraction-Cheatsheet/).
Its rule of thumb is strong enough to treat as a definition:

> Abstraction means: forget some implementation detail, while preserving the structure needed to reason about a property.

That sentence is doing a lot of work. It is saying: abstraction is not vagueness.
It is a controlled camera angle. Some details are allowed to blur (mutation, allocation, evaluation order, scheduling, pointer layout) so the remaining shape is crisp enough to reason about a target property (correctness, safety, liveness, equivalence, complexity).

One way to make this precise is to name a function:

- Concrete states live in a big space $C$.
- Abstract states live in a smaller space $A$.
- An abstraction is a map $\alpha : C \to A$.

In general, $\alpha$ is many-to-one. Different concrete states collapse to the same abstract state.
That is not a bug. It is the point: the abstraction forgets what does not matter for the property in view.

<figure class="fp-figure">
  <p class="fp-figure-title">Abstraction as a deliberate many-to-one map</p>
  {% include diagrams/abstraction-map.svg %}
  <figcaption class="fp-figure-caption">
    Abstraction is a controlled loss of information. Many concrete states map to one abstract state, chosen to preserve the distinctions needed to reason about a property.
  </figcaption>
</figure>

In practice, several different moves get called "abstraction". Keeping them separate prevents confusion.

<figure class="fp-figure">
  <p class="fp-figure-title">Different “same”-claims</p>
  {% include diagrams/sameness-moves.svg %}
  <figcaption class="fp-figure-caption">
    "Same thing" can mean a lossless re-encoding (isomorphism), the same denotation after applying a meaning function (equivalence), or a deliberate approximation that preserves only certain properties (sound abstraction).
  </figcaption>
</figure>

### A quick taxonomy (so the words do not slip)

When a text says "this is the same thing in a different abstraction", the question is which kind of sameness is meant.

- **Isomorphism (lossless re-encoding):** there is a reversible translation `encode`/`decode`, and operations correspond across the translation.
- **Equivalence (same meaning):** there is a meaning function `⟦·⟧` and two descriptions are treated as the same when they denote the same object (often many-to-one).
- **Sound abstraction (property-preserving approximation):** there is a map from concrete to abstract that forgets details but preserves a property of interest (usually one-way).
- **Encoding/simulation (expressive power):** one formalism can simulate another; behavior may be preserved, but not as a simple 1-to-1 map.

The cheat sheet collects many lenses on one page. The point is not memorization; it is the repeatable move:
hold the same underlying behavior in view as functions, machines, relations, traces, or proofs, depending on the question.

For example, its "quick reference" places these side by side:

- foundational models (lambda calculus, Turing machines, finite-state machines),
- semantic views (operational vs denotational),
- logics (Hoare logic, separation logic, temporal logic),
- verification lenses (abstract interpretation, model checking, SAT/SMT),
- and data lenses (ADTs, relational algebra).

These lenses are related, but not always by literal isomorphisms. The relationships vary:

- Sometimes there is an **isomorphism** (a lossless change of representation).
- Sometimes there is an **equivalence of meaning** (different descriptions denote the same object).
- Sometimes there is a **sound abstraction** (a property is preserved while detail is deliberately merged, which can introduce false positives).
- Sometimes there is an **encoding** (one formalism can simulate another).

### Example: one state machine, three isomorphic encodings

A finite-state machine can be written in at least three ways that are "the same" up to a choice of naming/ordering:

- as a directed graph (states as nodes, transitions as edges),
- as a transition function $\delta : S \times \Sigma \to S$,
- as an adjacency matrix (after choosing an ordering of the states).

Each representation is just a different way of storing the same structure.
The translations between them are lossless once the naming/ordering convention is fixed.

### Example: two concrete stacks, one abstract stack

This is a classic "same thing in a different abstraction" situation in software.

Define an abstract meaning for a stack as a finite list of elements (top at the head). A concrete implementation might store that list:

- as an array plus a length index, or
- as a linked list of heap nodes.

Those concrete states are not isomorphic as raw memory graphs. They do not even live in the same state space.
But there is a simple meaning function that forgets representation details and keeps the abstract stack content:

`meaning : ConcreteState -> List(Element)`.

Two concrete states are then *equivalent* if they map to the same abstract list.
That equivalence relation is what makes sentences like "these implementations are the same" precise:
it means they realize the same abstract behavior at the interface.

### A reliable mental move: separate "description" from "meaning"

To say "it's the same thing in a different abstraction" without hand-waving, it helps to name two layers:

- **Descriptions**: syntax, diagrams, code, proof scripts, automata, formulas.
- **Meanings**: the mathematical object those descriptions denote (a function, a relation, a language, a transition system, a set of traces, and so on).

Many frameworks make this explicit with a semantics function, often written as:

`⟦·⟧ : Descriptions → Meanings`.

This is why "same thing" so often shows up as *many-to-one*: many descriptions can denote one meaning.

<figure class="fp-figure">
  <p class="fp-figure-title">Many descriptions, one meaning</p>
  {% include diagrams/description-to-meaning.svg %}
  <figcaption class="fp-figure-caption">
    In practice, "equivalent" often means "has the same denotation." An equivalence relation can be defined by equality after applying a semantics map.
  </figcaption>
</figure>

So when someone says "these two abstractions are the same", it helps to ask what kind of sameness is meant.
Is the claim about isomorphism (1-to-1 renaming), equivalence in meaning (same denotation), or a sound approximation for a particular property?

### Example: operational vs denotational (two views of one meaning)

This is why the cheat sheet places **operational** and **denotational** semantics next to each other.

For a simple *pure* expression language, one can often prove a theorem of the form:

- $e$ evaluates to value $v$ by the step-by-step rules iff the denotation of $e$ is $v$.

When that bridge exists, either lens can be used:

- operational semantics when the goal is a concrete execution story (steps, traces),
- denotational semantics when the goal is algebraic reasoning (equalities, composition).

### A clean pattern: equivalence first, then isomorphism

Often, "same thing" only appears after quotienting away irrelevant representation choices.

Example pattern:

1. Start with a set of *descriptions* (like regular expressions, or automata).
2. Define an equivalence relation $\sim$ meaning "denotes the same behavior".
3. Work with the quotient set of equivalence classes (meanings), where one meaning may have many descriptions.
4. If canonical representatives are chosen, it may be possible to recover an isomorphism between "meanings" and "canonical descriptions".

For regular languages, this shows up as:

- many different regular expressions can denote the same language,
- many different DFAs can recognize the same language,
- but each regular language has a minimal DFA that is unique *up to isomorphism* (rename the states).

So there is not a simple 1-to-1 correspondence "regex ↔ DFA".
Instead, there is "language ↔ minimal DFA (up to renaming)".

## Part IV: Curry-Howard (why proofs and programs rhyme)

Curry-Howard gives a tight, structure-preserving translation between certain logics and certain programming languages.

In its simplest form:

- **propositions** correspond to **types**,
- **proofs** correspond to **programs (terms)**,
- **proof normalization** corresponds to **program evaluation**.

For intuitionistic propositional logic and the simply typed lambda calculus, common connectives line up like this:

| Logic | Types (programming) | Meaning as a construction |
|---|---|---|
| $A \land B$ | product `A × B` | a pair: "I have an `A` and a `B`" |
| $A \lor B$ | sum `Either A B` | a tagged choice: "left with `A` or right with `B`" |
| $A \to B$ | function `A → B` | a function that turns evidence for `A` into evidence for `B` |
| `True` | `Unit` | trivial evidence |
| `False` | `Void` | impossible evidence |

One consequence is a very practical transfer trick:
if a program inhabits a certain type, then (in the corresponding logic) it is a proof of the corresponding proposition, and vice versa.

Example: the logical theorem $A \land B \to B \land A$ corresponds to the program that swaps a pair:

```
swap : (A × B) → (B × A)
swap (a, b) = (b, a)
```

## Interlude: thinking *behind* the code (two programmers)

Curry-Howard makes a concrete claim about what code can be: types behave like propositions, programs behave like proofs, and evaluation behaves like simplification.

Zoom back to daily software work and two default metaphors show up:
**code as a machine to operate**, and **code as a description to reason about**.
Here are two extremes.

### Developer A (inside my head): I treat code as a machine

When I'm building something, my attention is glued to the concrete surface:

- syntax, compiler errors, build systems, dependency versions,
- performance cliffs, memory layout, caching, concurrency primitives,
- APIs, frameworks, idioms, and the "current best way" to do things in *this* language.

I might never say "lambda calculus" out loud. I might not know that "state machine" is a general mathematical structure rather than "a diagram some people draw."

And yet I can still write good software, the way someone can play chess intuitively or play piano by ear:

- I recognize patterns,
- I can *feel* what a refactor will do,
- and I can often fix bugs by stepping through execution and patching the concrete mechanism.

If I'm object-oriented, my "state" lives in objects and their fields. My evidence is mainly empirical: tests, benchmarks, logs, traces, production behavior. My abstraction toolkit is mostly the one my language and ecosystem hands me.

This is also where "craft knowledge" lives: the little domain-specific moves that make codebases healthy in practice (naming, boundaries, observability, performance habits, the quirks of a compiler or runtime).

This style can be extremely productive, especially when the hard part is shipping a real system: integration, performance, observability, ergonomics, and working within constraints.

### Developer B (inside my head): I treat code as a description of behavior

When I'm building something, my attention starts one layer up:

- "What is the state space?"
- "What are the transitions?"
- "What property do we actually want to be true for all reachable states?"
- "What is the smallest abstraction that preserves that property?"

I might be bad at the local quirks that get past *this* compiler on *this* day. I might not know the latest idioms of a particular language. But I'm comfortable manipulating the behavior of the system in the abstract:

- I can write the model down as a transition system.
- I can phrase requirements as invariants, refinement claims, or input/output contracts.
- I can change representations on purpose: types, equations, state machines, relations, automata, whatever makes the reasoning easier.

Because those descriptions are (ideally) language-independent, I can then implement the same behavior in many programming languages.
Or I can hand the description to an agent and treat code generation as a compilation step: "Here is the spec; produce an implementation, and show the obligations/tests used."

This style helps when the hard part is not typing code, but knowing what is true about *all executions*, especially in adversarial, concurrent, or safety-critical settings.

### The contrast (and why isomorphism matters)

The "code-as-machine" developer is fluent in a concrete language of construction.
The "behavior-first" developer is fluent in translations between languages of description.

Isomorphisms and equivalences are what make those translations safe. They justify sentences like:

- "This refactor didn't change behavior; it just changed representation."
- "This code and this state machine are the same structure, written in two different notations."
- "This proof obligation and this type signature are two views of one constraint."

In practice, the strongest people and teams become bilingual: they can think in the abstract *and* land the idea in real code without losing the thread.

### Not vibe coding

Using an agent after having a precise, checkable description is not the same thing as vibe coding.

- **Vibe coding** leans on plausible-looking code and iterative prompting while the intent is still under-specified. The output may compile and even appear to work, but the meaning is drifting and mostly implicit.
- **Structure-first development** uses the agent as a mechanism after the meaning is pinned down: a model, a contract, an invariant, a type, tests derived from a spec, or a proof obligation. The agent is closer to "a compiler plus a fast assistant," not "a substitute for specification."

The difference is whether it is possible to say, clearly and mechanically, what would count as being wrong.

## Part V: Equivalence relations (when 1-to-1 is too strict)

An **equivalence relation** $\sim$ on a set $X$ is a relation that is:

- reflexive: $x \sim x$,
- symmetric: $x \sim y \Rightarrow y \sim x$,
- transitive: $x \sim y \land y \sim z \Rightarrow x \sim z$.

Equivalence relations are how we formalize "different presentation, same meaning".
They carve a set of descriptions into **equivalence classes** (blocks of mutually equivalent things).

This shows up everywhere:

- In lambda calculus, terms that differ only by renaming bound variables are equivalent (α-equivalence).
- In algebra, two expressions may be equivalent because they evaluate to the same value.
- In automata theory, two machines may be equivalent because they accept the same language.

Isomorphism is stricter: it says elements can be matched 1-to-1 in a way that preserves all structure in view.
Equivalence relations still help even when "1-to-1" is the wrong granularity.

## Part VI: Translation as a problem-solving move

The practical reason to care about all of this is simple:

> If a hard problem can be translated into an isomorphic (or meaning-preserving) form where the tools are better, the problem has not changed. Leverage has.

Here are three examples of how this works.

### Example: a puzzle becomes linear algebra

Consider a grid puzzle where each move "toggles" a fixed pattern of bits (like *Lights Out*).

If a board has $n$ lights, then:

- a board state is a vector in $\{0,1\}^n$,
- a move is "add a fixed vector mod 2",
- and sequences of moves are just sums mod 2.

So the puzzle's state space has size $2^n$. For a 5x5 board ($n=25$):

- $2^{25} = 33{,}554{,}432$ (about 33 million) possible states.

Brute force is already uncomfortable at that scale. But the algebraic view gives a different tool:
the whole puzzle becomes a linear system $A x = b$ over $\mathbb{F}_2$, solvable by Gaussian elimination.

### Example: circuit equivalence becomes SAT

Consider two combinational circuits $C_1$ and $C_2$ that take the same input bits $x$ and produce one output bit each.
The question "are they equivalent?" means:

- for all inputs $x$, $C_1(x) = C_2(x)$.

That universal claim can be turned into an existential search problem:

- find an input $x$ such that $C_1(x) \ne C_2(x)$.

Encode the circuits and the inequality into a SAT instance. Then:

- if the SAT solver finds a model, the model is a concrete counterexample input,
- if the SAT solver reports UNSAT, there is no such input, so the circuits are equivalent.

This is not magic. It is a change of language to one with industrial-strength tools.

### Example: deadlock becomes a cycle problem

In lock-based concurrency, deadlock is a pattern of circular waiting.
Thread A waits for something held by thread B, thread B waits for something held by thread C, and eventually some thread waits for something held by A.

That situation can be captured as a directed "wait-for" graph.
Vertices represent threads. An edge $A \to B$ means A is waiting for B.

In that model, a deadlock corresponds to a directed cycle.
Once the problem is phrased as "is there a cycle?", graph algorithms apply immediately.

That is the translation move again: the original situation is unchanged, but the tool choice gets better.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">A useful closing quote</p>
  <p>
    "The purpose of abstraction is not to be vague, but to create a new semantic level in which one can be absolutely precise."
    - Edsger W. Dijkstra
  </p>
</div>
