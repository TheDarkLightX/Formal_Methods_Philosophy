---
title: "Formal neural networks"
layout: docs
kicker: Tutorial 33
---

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Working Vocabulary</p>
  <ul>
    <li><a href="{{ '/glossary/#invariant' | relative_url }}"><strong>Invariant</strong></a> means a property that holds at every step. A formal neural network should carry checkable invariants, not just plausible outputs.</li>
    <li><a href="{{ '/glossary/#witness' | relative_url }}"><strong>Witness</strong></a> means a concrete object that makes a formal claim visible: a counterexample, a convergence trace, or a proof certificate.</li>
    <li><a href="{{ '/glossary/#controller' | relative_url }}"><strong>Controller</strong></a> means a compact decision rule. In a Neural Turing Machine, the neural controller decides what to read, write, and output.</li>
    <li><a href="{{ '/glossary/#cegis' | relative_url }}"><strong>CEGIS</strong></a> means counterexample-guided inductive synthesis. The L* automaton-extraction algorithm is a CEGIS-shaped loop applied to trained neural networks.</li>
    <li><a href="{{ '/glossary/#quotient' | relative_url }}"><strong>Quotient</strong></a> means a partition of states that are indistinguishable under the current observation. Extracting a DFA from an RNN is a quotient construction.</li>
  </ul>
</div>

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
    The ladder starts with the logic route and the three main software-level
    routes. The later sections extend the picture with a fourth route through
    probabilistic physical substrates.
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

### The convergence guarantee

When a perceptron learns its weights from data, the learning rule is:

$$
w_{t+1} = w_t + \eta\,(y - \hat{y})\,x
$$

The Perceptron Convergence Theorem (Novikoff, 1962) gives a bounded guarantee:
if the training set is linearly separable with margin $\delta$ and all data
points satisfy $\|x\| \leq R$, then the perceptron makes at most

$$
\frac{R^2}{\delta^2}
$$

mistakes before converging. This is not an asymptotic claim. It is a finite
bound.

### The XOR impossibility

The convergence guarantee is conditional on linear separability. Minsky and
Papert (1969) proved that a single-layer perceptron cannot compute XOR: no
single hyperplane in $\mathbb{R}^2$ separates the positive points $(0,1)$
and $(1,0)$ from the negative points $(0,0)$ and $(1,1)$.

This is not a failure. It is a formal boundary that tells you exactly when to
add structure. A two-layer network with one hidden unit computes XOR easily.

**Interactive lab**

- [McCulloch-Pitts Logic Gate Lab]({{ '/mcculloch_pitts_lab.html' | relative_url }})

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Why the perceptron result is only the first rung</p>
  <p>
    A logical perceptron shows that a neural unit can realize Boolean logic and
    that learning has a convergence bound. It does not yet provide memory,
    addressable state, proof search, or a proof kernel. Those require more
    structure than one universal gate.
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

### How route A would actually become a computer

The missing ingredient is organization.

A single `NAND` gate is not yet memory, branching, or theorem proving. But
large collections of gates can be arranged into the standard pieces of a
machine:

- **combinational circuits** compute the next local result from the current
  inputs
- **latches and flip-flops** preserve bits across steps, giving persistent
  state
- **registers** group several stored bits into structured words
- **control circuits** decide which operation happens next
- **memory addressing logic** chooses where information is read or written

So the full route-A story is:

1. threshold neurons realize universal gates
2. gates realize circuits
3. circuits plus feedback realize state
4. state plus control realize a machine

This is why the logical perceptron matters. It does not complete the story, but
it gives the first formal bridge to all the later pieces.

### The universal approximation theorem

The XOR impossibility applies only to single-layer networks. For multi-layer
networks, a much stronger result holds.

**Theorem (Cybenko, 1989).** For any continuous function
$f : [0,1]^n \to \mathbb{R}$ and any $\varepsilon > 0$, there exists a
feedforward network with one hidden layer and a finite number of sigmoidal
neurons such that

$$
\sup_{x \in [0,1]^n} |f(x) - g(x)| < \varepsilon
$$

In plain language: one hidden layer can approximate any continuous function to
any desired accuracy, given enough neurons.

This is an existence result, not a construction. It says a good network exists
but not how to find it, how many neurons are needed, or whether the trained
network satisfies specific safety properties. That gap between "exists" and
"verified" is why formal verification of neural networks became its own field.

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

### 2. Neural Turing Machines (Graves et al., 2014)

The Neural Turing Machine (NTM) couples a neural controller to an external
memory matrix through differentiable attention. The architecture has three
components:

- **Controller**: a neural network that decides what to read, write, and output
- **Memory matrix**: an $N \times M$ array of memory slots (analogous to a tape
  or RAM)
- **Read/write heads**: attention-weighted interfaces with two addressing modes:
  - *content-based*: find slots whose content matches a query (associative
    lookup)
  - *location-based*: shift attention to neighboring slots (sequential access)

The read operation is a weighted sum over memory:

$$
r_t = \sum_i w_t(i)\, M_t(i)
$$

The entire system is differentiable end-to-end, so it trains with gradient
descent. The NTM learned copying, sorting, and associative recall from
input-output examples alone.

### 3. Differentiable Neural Computers (Graves et al., 2016)

The DNC extends the NTM with three mechanisms:

- **Dynamic memory allocation**: a usage vector tracks free slots
- **Temporal link matrix**: records write order for forward/backward traversal
- **Content protection**: prevents recently read content from being overwritten

The DNC successfully answered multi-step reasoning questions, found shortest
paths in random graphs, and solved a moving-blocks puzzle. Published in
*Nature*.

The formal significance: the DNC makes memory, allocation, and temporal
ordering explicit and separable, exactly the distinctions formal methods
care about.

In both the NTM and the DNC, one computational step has a clear internal
structure:

1. the controller reads the current input and previous read vectors
2. it computes parameters for memory access
3. the heads read from or write to external memory
4. the new read vectors are fed back into the controller
5. the controller emits an output and an updated hidden state

That is why these systems matter here. They are not only large function
approximators. They already look like small neural computers with explicit
state transitions.

### 4. Verifying trained networks (Reluplex, Katz et al., 2017)

Once a network is trained, can its behavior be formally verified? Reluplex
answers yes for ReLU networks, by extending the simplex method to handle the
piecewise-linear $\text{ReLU}(z) = \max(0, z)$ constraint as an SMT problem.

It verified safety properties of a prototype airborne collision avoidance
system (ACAS Xu) implemented as a deep neural network, handling networks an
order of magnitude larger than any previously verified.

The broader lesson: formal verification of neural networks is possible but
NP-complete in general. That cost is exactly why neuro-symbolic hybrids
matter.

### 5. Extracting automata from RNNs (Weiss et al., 2018)

A complementary approach asks: what finite-state machine does a trained RNN
implement? Weiss, Goldberg, and Yahav used Angluin's L\* algorithm with the
RNN as oracle:

1. membership queries: "does this input produce class 1?"
2. equivalence queries: counterexamples refine a candidate DFA

This is a CEGIS-shaped loop applied to neural interpretation. The result is
an extracted DFA that matches the RNN's behavior on the tested domain, making
the implicit quotient structure of the RNN's state space explicit.

### 6. Looped Transformers as programmable computers (Giannou et al., 2023)

Giannou and colleagues proved that a 13-layer transformer placed in a loop
can emulate a universal computer. The input sequence acts as a punchcard
containing both instructions and read/write memory.

A constant number of encoder layers can implement lexicographic operations,
nonlinear functions, function calls, program counters, and conditional
branches. The authors demonstrated a single frozen transformer emulating a
calculator, a linear algebra library, and a full backpropagation algorithm.

This is a stronger statement than the universal approximation theorem: specific
computational procedures can be exactly implemented, not merely approximated.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Evidence note</p>
  <p>
    The transformer-as-computer idea is supported by formal theoretical
    results (Giannou et al., ICML 2023; constant-bit-size Turing completeness
    results). Engineering claims about practical program execution inside
    transformers are a live research direction.
  </p>
</div>

### 7. Continuous latent execution with symbolic regrounding (CALM, 2025)

Continuous Autoregressive Language Models (CALM) add a different kind of
evidence to route B.

The central move is not to predict one discrete token at a time. Instead, the
model:

1. compresses a chunk of $K$ tokens into one continuous vector with an
   autoencoder
2. predicts the next continuous vector
3. decodes that vector back into the original token chunk
4. feeds the recovered discrete structure back into the model for the next step

This changes the practical execution picture. The model is no longer limited to
one-token semantic updates. One step can carry the information of a whole
chunk. The paper presents this as increasing the semantic bandwidth of each
generative step.

That does not by itself create formal semantics or theorem proving. It does
something narrower and still important. It shows that a neural architecture can
use a continuous latent state as the main execution medium, while periodically
regrounding into discrete symbolic structure.

That regrounding step matters. The authors report that feeding predicted latent
vectors directly back into the Transformer did not work as well, because the
model struggled to unpack the compact representation. So CALM is not evidence
for pure latent symbolic execution. It is evidence for a hybrid:

- continuous latent execution
- periodic discrete regrounding

For this tutorial, that is exactly the useful point. A formal neural network
may not need to stay discrete all the way through, but it probably does need a
stable encoding and decoding discipline if its internal computation is to remain
interpretable or checkable.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">What CALM changes, and what it does not</p>
  <p>
    CALM changes the practical design space more than the formal one. It gives
    a stronger GPU-friendly story for latent execution, but it does not by
    itself provide proof objects, explicit formal semantics, or exact theorem
    proving guarantees.
  </p>
</div>

So route B is real and increasingly deep, spanning:

- memory-augmented architectures (NTM, DNC) with explicit state
- formal verification of trained networks (Reluplex)
- automaton extraction from trained networks (L\* + counterexamples)
- computational universality of transformers (Looped Transformers)
- continuous latent execution with symbolic regrounding (CALM)

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

### How route C works in current systems

The easiest way to understand route C is to look at what the current systems
actually delegate to the neural part, and what they keep exact.

**DeepMath (2016)** is an early example. It does not ask the network to prove
the theorem by itself. It asks the network to do one narrow but crucial job:
rank which premises from a large library are likely to matter. That is a neural
carving step. The downstream prover still does the exact proving.

**AlphaGeometry (2024)** makes the split sharper. A neural model proposes
auxiliary constructions that may make the geometry problem easier. A symbolic
engine then performs deductive search over the formalized geometry state. The
success comes from the combination. The neural side expands the useful search
space, and the symbolic side keeps the reasoning exact.

**AlphaProof (2025)** pushes this further in formal mathematics. The learned
system searches for proof steps in a formal environment, but correctness still
comes from exact formal checking rather than from the model's confidence.

The Quanta interview with Marijn Heule points to the same pattern in a more
general form:

1. carve the statement into exact subproblems
2. encode those subproblems into a solver-friendly form
3. let SAT or another exact engine prove or refute them
4. use a proof assistant to check the final assembly

That is why route C matters so much. It is not a fallback for when neural
systems fail. It is the clearest present recipe for combining:

- neural compression and proposal
- exact search
- checkable trust

## Part VII: route D, probabilistic physical substrates

The fourth route changes the hardware substrate itself.

Instead of asking a machine to perform mostly deterministic arithmetic and then
sample at the end, this route asks the hardware to make structured sampling one
of its native operations.

That is the idea behind **p-computers** and newer **thermodynamic sampling**
proposals.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Scope note</p>
  <p>
    This route stretches the phrase <strong>formal neural network</strong> the
    furthest. The point is not that p-computers are standardly classified as
    neural networks. The point is that they are close enough to stochastic
    neural computation to matter as a possible substrate inside a larger
    formal-neural architecture.
  </p>
</div>

### 1. P-computers and p-bits

A **p-bit** is a tunable random bit. It fluctuates stochastically between two
states, and its probability can be biased by an external signal.

Networks of p-bits form a **probabilistic computer**. The 2019 p-computing
paper describes such a machine as closely related to a stochastic neural
network, with the p-bit playing the role of a binary stochastic neuron.

That is exactly why this matters for the tutorial. It is not only "new
hardware." It is a hardware line that is already conceptually adjacent to
stochastic neural computation.

### 2. Thermodynamic sampling hardware

The newer thermodynamic line pushes this further. The Extropic paper on
diffusion-like models proposes an all-transistor probabilistic hardware
architecture whose primitive job is to sample from structured probabilistic
models efficiently.

The key shift is this:

- a CPU or GPU mostly performs deterministic operations, then samples
- a thermodynamic sampling unit aims to sample directly from a programmable
  energy-based model

That changes the natural style of computation. The machine is best understood
as a **sampling-native computer**.

### 3. Why this route matters

This route is important because many AI and search workloads are already more
naturally described as:

- inference
- denoising
- approximate optimization
- structured probabilistic search

So the philosophical lesson is broader than hardware efficiency.

> Computing is not only deterministic execution and not only symbolic proof
> search. It can also be controlled sampling from a formally specified
> probability landscape.

### 4. What this route does and does not provide

This route gives:

- a new physical substrate for probabilistic computation
- a possible proposal engine for larger neuro-symbolic systems
- a conditional energy-efficiency argument for some workloads, based on current
  system-level analyses rather than broad deployment evidence

It does not yet give, by itself:

- proof objects
- proof kernels
- theorem-proving guarantees
- exact symbolic trust

So route D is best seen as a possible front end inside a larger formal system:

- probabilistic hardware proposes or samples
- symbolic machinery checks

In that sense, route D can complement route C rather than replace it.

## Part VIII: theorem proving and formal semantics

To be worthy of the word **formal**, a neural system should do more than emit
convincing text.

At least one of the following should hold:

- it emits proof objects that a proof assistant can check
- it emits constraints whose satisfiability or unsatisfiability can be checked
- it operates over internal states that already have an explicit formal
  interpretation
- it is itself synthesized or verified against formal specifications

That gives a practical ladder of increasing strength.

### Proof objects, certificates, and proof kernels

These three ideas are easy to blur together, so it helps to separate them.

- A **proof object** is a structured derivation that a proof assistant can
  replay step by step.
- A **certificate** is any compact artifact that lets an exact checker confirm
  a claim. In SAT, for example, this may be a satisfying assignment or an
  unsatisfiability proof trace.
- A **proof kernel** is the small trusted checker at the center of a proof
  assistant. Its job is not to be clever. Its job is to reject invalid steps.

That is why route C is so attractive. The neural part may be large, heuristic,
and opaque, but the final trust can be concentrated into a much smaller exact
checker.

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

## Part IX: would GPUs help?

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

CALM sharpens this point. If a model can carry more semantic content per
autoregressive step, then part of the sequential bottleneck can be attacked
without abandoning neural execution. That is especially relevant on GPUs,
because chunk-level latent execution stays dense, continuous, and highly
vectorized.

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

Probabilistic substrates complicate the picture further. A p-computer or
thermodynamic sampler is not trying to be a better GPU in the usual sense. It
is trying to make structured sampling cheaper at the hardware level.

So the most plausible high-performance formal neural computer is not a single
uniform machine. It is a heterogeneous system:

- GPU for neural proposal and dense learned execution
- probabilistic hardware for sampling-heavy inference or candidate generation
- symbolic checker for exact trust
- possibly specialized hardware for binary or logic-heavy subroutines

## Part X: what a formal neural network should mean

A good working definition is now available.

> A formal neural network is a neural architecture whose internal states or
> outputs have explicit formal semantics, and whose reasoning can be checked,
> synthesized, or constrained by exact symbolic machinery.

That definition is broad enough to include:

- logic-substrate networks
- memory-augmented neural computers
- probabilistic hardware with programmable structured distributions
- neural-guided proof systems
- verified or synthesized neural submodules

But it is strict enough to exclude:

- ordinary next-token generation by itself
- unverified chain-of-thought by itself
- raw pattern matching with no formal interpretation

## Part XI: the four routes side by side

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
- even strong route-B systems often need explicit regrounding if they compress
  too much state into opaque latents

### Route C: carve, solve, check

Best for:

- practical theorem proving
- exact trust
- using neural systems where they help most without giving them final authority

Weakness:

- the neural part is not the whole machine, so it is less pure as a thought
  experiment

### Route D: probabilistic physical substrate

Best for:

- sampling-heavy workloads
- probabilistic inference
- energy-based search
- hardware-efficient candidate generation

Weakness:

- not by itself a proof system
- current evidence is much stronger for probabilistic workloads than for exact
  symbolic reasoning
- current energy and performance claims are narrower than the GPU literature and
  should be read as model-specific evidence, not a universal replacement story

That is why the clean conclusion is not that one route replaces the others.

The routes answer different questions.

- route A explains derivation
- route B explores executable neural computation
- route C explains the strongest near-term engineering path
- route D explores alternative physical primitives for probabilistic search

## Part XII: what this tutorial has established

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
   - probabilistic physical substrate
   - carve, solve, check hybrid systems

Current work already illustrates those routes in different ways:

- McCulloch-Pitts and perceptrons show the logical bridge
- NTM, DNC, Looped Transformers, and CALM show different execution stories
- p-computers and thermodynamic sampling units show a new hardware route for
  probabilistic computation
- DeepMath, AlphaGeometry, and AlphaProof show the strongest present hybrid
  path

That is enough to justify the research program.

The phrase **formal neural network** is no longer only a slogan.
It names a real design space.

## Sources and further reading

**Foundational results:**

- [McCulloch and Pitts, *A Logical Calculus of the Ideas Immanent in Nervous Activity* (1943)](https://www.cs.cmu.edu/~epxing/Class/10715/reading/McCulloch.and.Pitts.pdf)
- [Novikoff, *On Convergence Proofs for Perceptrons* (1962)](https://cs.uwaterloo.ca/~y328yu/classics/novikoff.pdf)
- Minsky and Papert, *Perceptrons: An Introduction to Computational Geometry* (MIT Press, 1969)
- [Cybenko, *Approximation by Superpositions of a Sigmoidal Function* (1989)](https://link.springer.com/article/10.1007/BF02551274)

**Memory-augmented architectures:**

- [Graves, Wayne, and Danihelka, *Neural Turing Machines* (2014)](https://arxiv.org/abs/1410.5401)
- [Graves et al., *Hybrid Computing Using a Neural Network with Dynamic External Memory* (Nature, 2016)](https://www.nature.com/articles/nature20101)

**Verification and extraction:**

- [Katz et al., *Reluplex: An Efficient SMT Solver for Verifying Deep Neural Networks* (CAV, 2017)](https://arxiv.org/abs/1702.01135)
- [Weiss, Goldberg, and Yahav, *Extracting Automata from RNNs Using Queries and Counterexamples* (ICML, 2018)](https://arxiv.org/abs/1711.09576)

**Computational power:**

- [Giannou et al., *Looped Transformers as Programmable Computers* (ICML, 2023)](https://arxiv.org/abs/2301.13196)
- [*On the Computational Power of Transformers and its Implications in Sequence Modeling* (2020)](https://arxiv.org/abs/2006.09286)
- [*Constant Bit-size Transformers Are Turing Complete* (2025)](https://arxiv.org/abs/2506.12027)
- [Shao et al., *Continuous Autoregressive Language Models* (2025)](https://arxiv.org/abs/2510.27688)

**Probabilistic substrates:**

- [Sutton et al., *Autonomous Probabilistic Coprocessing with Petaflips per Second* (2019)](https://arxiv.org/abs/1907.09664)
- [Jelinčič et al., *An efficient probabilistic hardware architecture for diffusion-like models* (2025)](https://arxiv.org/abs/2510.23972)

**Theorem proving and engineering:**

- [Irving et al., *DeepMath: Deep Sequence Models for Premise Selection* (NeurIPS, 2016)](https://arxiv.org/abs/1606.04442)
- [*End-to-end Differentiable Proving* (2017)](https://papers.nips.cc/paper/6969-end-to-end-differentiable-proving.pdf)
- [Trinh et al., *Solving olympiad geometry without human demonstrations* (AlphaGeometry, Nature, 2024)](https://www.nature.com/articles/s41586-023-06747-5)
- [*Olympiad-level formal mathematical reasoning with reinforcement learning* (AlphaProof, Nature 2025)](https://www.nature.com/articles/s41586-025-09833-y)
- [Quanta Magazine interview, *To Have Machines Make Math Proofs, Turn Them Into a Puzzle* (November 10, 2025)](https://www.quantamagazine.org/to-have-machines-make-math-proofs-turn-them-into-a-puzzle-20251110/)
- [Percepta, *Can LLMs Be Computers?* (March 11, 2026)](https://www.percepta.ai/blog/can-llms-be-computers)

## Related tutorials

- [Tutorial 10: Reasoning, logic, and prediction]({{ '/tutorials/reasoning-connectionism-gofai/' | relative_url }})
- [Tutorial 13: What reasoning is]({{ '/tutorials/what-is-reasoning-proof-search-and-justification/' | relative_url }})
- [Tutorial 21: A perceptron in Tau Language]({{ '/tutorials/perceptron-in-tau-language/' | relative_url }})
- [Tutorial 27: Verifier-compiler loops]({{ '/tutorials/verifier-compiler-loops/' | relative_url }})
- [Tutorial 29: Loop-space geometry]({{ '/tutorials/loop-space-geometry/' | relative_url }})
