---
title: "Formal neural networks"
layout: docs
kicker: Tutorial 33
description: "Start from the question 'what is a computer?', then build a careful ladder from logic gates and threshold neurons to hybrid neural systems that search, prove, and emit checkable formal artifacts."
---

## The motivating question

What would it mean for a neural network to be a computer in a strong sense,
not only a pattern recognizer?

That question has at least three layers:

- a philosophical layer, about what counts as computation at all
- a mathematical and logical layer, about state, transition, and symbolic
  rules
- a technical layer, about what kind of machine could actually search for or
  check proofs

This tutorial proposes one umbrella term for that discussion:

- **formal neural network**

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Scope note</p>
  <p>
    <strong>Formal neural network</strong> is a proposed teaching term in this
    tutorial, not a settled standard term. Here it means: a neural architecture
    whose internal states or outputs have explicit formal semantics, and whose
    reasoning can be checked, synthesized, or constrained by exact symbolic
    machinery.
  </p>
</div>

The point is not to claim that present-day neural networks already are full
formal machines.

The point is to ask what must be added, proved, or constrained before such a
claim would make sense.

<figure class="fp-figure">
  <p class="fp-figure-title">From NAND to formal neural networks</p>
  {% include diagrams/formal-neural-network-ladder.svg %}
  <figcaption class="fp-figure-caption">
    There is not only one route. Logic-substrate, executable-neural, and
    carve-solve-check architectures all point toward stronger forms of formal
    neural computation, but they do not make the same promises.
  </figcaption>
</figure>

## Part I: what a computer is

The word "computer" can be made precise at four levels.

### 1. Philosophical level

A computer is a physical or abstract system whose states can be interpreted as
symbols, and whose state transitions preserve a rule-governed meaning under
that interpretation.

This definition matters because it separates:

- raw physics
- from interpreted computation

A rock has physical states. A computer has physical states that are used as
encodings.

### 2. Mathematical level

A computer is a state-transition system.

At minimum it has:

- a set of states
- a transition rule
- an input encoding
- an output interpretation

This is the backbone behind:

- finite-state machines
- circuits
- pushdown automata
- Turing machines
- lambda calculus interpreters
- ordinary software running on hardware

### 3. Logical level

A computer is a machine that carries out rule-governed transformations on
symbolic encodings.

Sometimes those transformations are:

- Boolean
- arithmetic
- logical
- proof-theoretic

The key point is that correctness is not only "the right answer happened to
appear". Correctness means the transitions respect the semantics of the formal
objects being manipulated.

### 4. Technical level

In practice, a computer needs a few things that simple classifiers do not.

- **Stable state**: something persists from one step to the next
- **Composition**: small operations can be chained
- **Conditional control**: one step can depend on earlier results
- **Memory**: the system can store more than the current local input
- **Interpretability of states**: the states can be read as structured data

That is why "a model can output correct-looking text" is not enough.

## Part II: what it means to compute

There is more than one legitimate picture of computation.

### Computation as function evaluation

The simplest picture is:

```text
input -> machine -> output
```

That covers:

- arithmetic circuits
- feed-forward classifiers
- ordinary batch inference

### Computation as state evolution

A stronger picture is:

```text
current state + input -> next state
```

That covers:

- automata
- recurrent systems
- interactive programs
- proof search with backtracking state

### Computation as search

A third picture is important for theorem proving.

The machine is not only executing a fixed straight-line program. It is
searching through a space of possibilities under exact constraints.

This matters because SAT, SMT, theorem proving, and proof assistants often
compute by:

- branching
- pruning
- refuting
- checking certificates

not only by "running one predetermined procedure from line 1 to line 200".

That is one of the tutorial's main philosophical points:

> computing is not only execution, it can also be exact search in a formally
> encoded possibility space.

## Part III: why NAND matters

The perceptron experiment already established a first rung.

A threshold unit can realize a universal Boolean gate such as `NAND`.

One example is:

```text
y = 1  iff  (-x1 - x2 + 1.5) > 0
```

for binary inputs `x1, x2 in {0,1}`.

That matters because `NAND` is universal for Boolean circuits.

So the logic-substrate route begins like this:

1. threshold unit
2. logical gate
3. circuit
4. register and control
5. finite-state or Turing-style machine

This is not yet theorem proving. But it is the first rigorous bridge from
neural-style threshold units to formal symbolic computation.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Why the perceptron result is only the first rung</p>
  <p>
    A logical perceptron shows that a neural unit can realize Boolean logic.
    It does not yet provide memory, addressable state, proof search, or a proof
    kernel. Those require more structure than one universal gate.
  </p>
</div>

## Part IV: route A, logic as the substrate

The oldest clean route to a formal neural network is the logic-substrate route.

The classic source here is McCulloch and Pitts. Their 1943 paper models neuron
activity with threshold-style assumptions and shows that networks of such units
can realize logical expressions and temporal propositional structure.

That route says:

- start with threshold firing
- interpret firing patterns propositionally
- compose units into logical structure
- build machines from those logical parts

This route has two major strengths.

- **Clarity**: the semantics are explicit from the start
- **Formal leverage**: the machine can be analyzed in the same language as the
  logic it realizes

It also has two limits.

- it does not automatically produce efficient modern learning systems
- by itself it says little about how a large trained neural system should
  discover proofs

So route A is best understood as the cleanest theoretical derivation, not yet
the whole modern engineering story.

## Part V: route B, executable neural architectures

The second route is to build neural systems whose internal dynamics already
look like program execution.

There are two established versions of this idea.

### 1. Recurrent neural networks as general computers

Theoretical work on recurrent networks shows that, in principle, such systems
can simulate very general computation.

That matters because it answers one foundational question cleanly:

- a neural system is not limited in principle to shallow pattern recognition

But this is a computability result, not a promise of practical theorem proving.

It shows possibility, not a turnkey architecture.

### 2. Neural systems with explicit memory

Work such as Neural Turing Machines couples a neural controller to external
memory. The architecture is intentionally described as analogous to a Turing or
von Neumann style machine, but trained end to end.

That route is much closer to a real "neural computer" idea:

- controller
- memory
- read/write operations
- learned algorithms

The system can learn copying, sorting, and associative recall. That is already
much closer to an executable machine than a plain feed-forward network.

### 3. Transformers as computers, a live line of work

There is also a newer transformer-centered line.

Some recent theoretical work proves that transformer-style systems can be
Turing-complete under appropriate assumptions. That places transformers inside
the same broad computability conversation.

There is also a newer engineering claim, represented publicly by the Percepta
essay, that programs can be executed inside transformers with very strong
inference advantages.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Evidence note</p>
  <p>
    The transformer-as-computer idea is worth taking seriously. But as of
    April 1, 2026, the public evidence available to this tutorial is uneven.
    Theoretical transformer-computability papers are real primary sources. The
    Percepta public essay is useful as a directional engineering claim, but it
    is not yet a full public technical paper with the same weight.
  </p>
</div>

So route B is real, but split into:

- a strong theoretical computability story
- a promising modern engineering story

## Part VI: route C, carve, solve, check

The most practical route today is different again.

It does not require the neural network itself to be the whole prover.

Instead it builds a hybrid machine:

1. a neural component proposes structure
2. a symbolic engine solves or refutes exact subproblems
3. a proof checker certifies the whole result

This is the route suggested most clearly by the recent theorem-proving work and
by Marijn Heule's Quanta interview about turning proofs into puzzles.

The neural part can help by:

- carving the problem into subproblems
- proposing lemmas
- proposing encodings
- prioritizing search

The exact part can then:

- prove
- refute
- return counterexamples
- emit certificates

And a proof assistant such as Lean can check the final assembly.

This route is less romantic than "the network itself is the theorem prover",
but it is much more realistic.

It also fits the broader lessons from the loop tutorials:

- first find better structural coordinates
- then let a smaller exact controller or solver finish the job

In that sense, a carve-solve-check formal neural network is already a
geometry-changing loop.

## Part VII: theorem proving and formal semantics

To be worthy of the word **formal**, a neural system should do more than emit
convincing text.

At least one of the following should hold:

- it emits proof objects that a proof assistant can check
- it emits constraints whose satisfiability or unsatisfiability can be checked
- it operates over internal states that already have an explicit formal
  interpretation
- it is itself synthesized or verified against formal specifications

That gives a practical ladder of increasing strength.

### Weak form

- neural system proposes proof steps
- no exact checker

This may be useful, but it is not a formal neural network in the strong sense.

### Medium form

- neural system proposes
- symbolic engine checks

This is already strong enough for a serious theorem-proving workflow.

### Strong form

- the neural architecture itself has explicit formal semantics or formal
  guarantees

This is the most ambitious sense of the term.

## Part VIII: would GPUs help?

Yes, but not uniformly.

### Where GPUs help a lot

- training large neural controllers
- dense inference
- premise selection
- tactic proposal
- search heuristics
- learned encodings

This is why neural-guided theorem proving and transformer-based execution ideas
scale naturally with modern accelerator hardware.

### Where GPUs help less directly

- exact SAT or SMT solving
- proof-kernel checking
- bit-level symbolic search
- branch-heavy irregular control

Those workloads often benefit more from:

- CPUs
- solver infrastructure
- FPGAs
- ASIC-style logic-heavy designs

So the most plausible high-performance formal neural computer is not a single
uniform machine. It is a heterogeneous system:

- GPU for neural proposal and dense learned execution
- symbolic checker for exact trust
- possibly specialized hardware for binary or logic-heavy subroutines

## Part IX: what a formal neural network should mean

A good working definition is now available.

> A formal neural network is a neural architecture whose internal states or
> outputs have explicit formal semantics, and whose reasoning can be checked,
> synthesized, or constrained by exact symbolic machinery.

That definition is broad enough to include:

- logic-substrate networks
- memory-augmented neural computers
- neural-guided proof systems
- verified or synthesized neural submodules

But it is strict enough to exclude:

- ordinary next-token generation by itself
- unverified chain-of-thought by itself
- raw pattern matching with no formal interpretation

## Part X: the three routes side by side

The whole discussion now becomes much clearer.

### Route A: logic as substrate

Best for:

- philosophical clarity
- deriving computers from logic
- explaining how threshold neurons can become gates and machines

Weakness:

- not obviously the fastest route to modern large-scale theorem proving

### Route B: executable neural architecture

Best for:

- neural machines with memory
- GPU-native scaling stories
- studying whether neural dynamics themselves can execute programs

Weakness:

- practical formal guarantees are still much weaker than in hybrid systems

### Route C: carve, solve, check

Best for:

- practical theorem proving
- exact trust
- using neural systems where they help most without giving them final authority

Weakness:

- the neural part is not the whole machine, so it is less pure as a thought
  experiment

That is why the clean conclusion is not that one route replaces the others.

The routes answer different questions.

- route A explains derivation
- route B explores executable neural computation
- route C explains the strongest near-term engineering path

## Part XI: what this tutorial has established

This tutorial makes four main claims.

1. A computer is not just a box with inputs and outputs.
   It is an interpreted state-transition system with stable rule-governed
   semantics.

2. Computing is not only straight-line execution.
   It can also be exact search in a formally encoded possibility space.

3. A logical perceptron is real and important, but it is only the first rung.
   Logic gates are not yet memory, proof search, or formal certification.

4. A serious formal neural network probably comes in more than one form.
   The strongest present routes are:
   - logic as substrate
   - executable neural architecture
   - carve, solve, check hybrid systems

That is enough to justify the research program.

The phrase **formal neural network** is no longer only a slogan.
It names a real design space.

## Sources and further reading

- [*A Logical Calculus of the Ideas Immanent in Nervous Activity* (1943)](https://www.cs.cmu.edu/~epxing/Class/10715/reading/McCulloch.and.Pitts.pdf)
- [*Theoretical Foundations of Recurrent Neural Networks* (1993)](https://scholarship.libraries.rutgers.edu/esploro/outputs/technicalDocumentation/Theoretical-Foundations-of-Recurrent-Neural-Networks/991031550002704646)
- [*Neural Turing Machines* (2014)](https://arxiv.org/abs/1410.5401)
- [*End-to-end Differentiable Proving* (2017)](https://papers.nips.cc/paper/6969-end-to-end-differentiable-proving.pdf)
- [*On the Computational Power of Transformers and its Implications in Sequence Modeling* (2020)](https://arxiv.org/abs/2006.09286)
- [*Constant Bit-size Transformers Are Turing Complete* (2025)](https://arxiv.org/abs/2506.12027)
- [*Olympiad-level formal mathematical reasoning with reinforcement learning* (AlphaProof, Nature 2025)](https://www.nature.com/articles/s41586-025-09833-y)
- [Quanta Magazine interview, *To Have Machines Make Math Proofs, Turn Them Into a Puzzle* (November 10, 2025)](https://www.quantamagazine.org/to-have-machines-make-math-proofs-turn-them-into-a-puzzle-20251110/)
- [Percepta, *Can LLMs Be Computers?* (March 11, 2026)](https://www.percepta.ai/blog/can-llms-be-computers)

## Related tutorials

- [Tutorial 10: Reasoning, logic, and prediction]({{ '/tutorials/reasoning-connectionism-gofai/' | relative_url }})
- [Tutorial 13: What reasoning is]({{ '/tutorials/what-is-reasoning-proof-search-and-justification/' | relative_url }})
- [Tutorial 21: A perceptron in Tau Language]({{ '/tutorials/perceptron-in-tau-language/' | relative_url }})
- [Tutorial 27: Verifier-compiler loops]({{ '/tutorials/verifier-compiler-loops/' | relative_url }})
- [Tutorial 29: Loop-space geometry]({{ '/tutorials/loop-space-geometry/' | relative_url }})
