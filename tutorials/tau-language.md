---
title: Tau Language (invariants first, then execution)
layout: docs
kicker: Tutorial 3
description: Learn to read and write small executable specifications by listing invariants first, then letting a solver choose behaviors that satisfy them.
---

This tutorial introduces Tau as a way to write executable specifications: not "do this, then that", but "these relationships must hold, at every time-step".

Tau is a good fit for the theme of this project because it makes a familiar formal-methods habit concrete:
start from invariants, then let tools search for behaviors that satisfy them.

All examples in this tutorial are runnable from files under `examples/tau/` and do not require typing into the interpreter.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Mental pictures to keep</p>
  <ul>
    <li>A timeline of variables (streams) indexed by time</li>
    <li>An invariant as a rail: the system is allowed to move, but not off the rails</li>
    <li>A solver as a witness generator: it produces concrete values that make the constraints true</li>
    <li>A state machine as one lens, and a logic specification as another</li>
  </ul>
</div>

## Part I: invariants first (the habit that makes specs readable)

When writing a specification, the fastest way to get lost is to start with syntax.
The fastest way to stay oriented is to start with a list of sentences that are meant to be true.

Here is a small example system: a turnstile with two events.

- Event `coin`: unlock.
- Event `push`: pass through if unlocked, otherwise trigger an alarm.

Before any Tau code, a useful invariants list is:

1. The state is always either `Locked` or `Unlocked`.
2. If the state is `Locked` and the event is `coin`, the next state is `Unlocked`.
3. If the state is `Unlocked` and the event is `push`, the next state is `Locked`.
4. If the state is `Locked` and the event is `push`, an `alarm` flag is raised.
5. If the state is `Unlocked`, `alarm` is not raised.

This list is small, but it already decides most design choices:
it says what the state is, what inputs exist, and what properties must never be violated.

<figure class="fp-figure">
  <p class="fp-figure-title">A tiny turnstile state machine</p>
  {% include diagrams/tau-turnstile-fsm.svg %}
  <figcaption class="fp-figure-caption">
    The same system can be held in view as a state machine (states and arrows) or as a set of logical constraints relating current and next values.
  </figcaption>
</figure>

## Part II: reading Tau (streams, time, and constraints)

Tau specifications talk about **streams** (inputs and outputs) indexed by time.
The index starts at 0, and `t` is used as "the current step" during execution.

Stream declarations look like:

```tau
i1 : bv[8] := in console
o1 : bv[8] := out console
```

Then a local constraint can relate "now" and "one step ago":

```tau
o1[t] = o1[t-1] + i1[t]
```

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">A small practical note: <code>charvar</code></p>
  <p>
    Tau enables <code>charvar</code> by default (see <code>tau --help</code>). In that mode, names are more restrictive.
    These tutorials use longer names like <code>delta_is_valid</code> and <code>bit_not</code>, so every example starts with
    <code>set charvar off</code>.
  </p>
</div>

One crucial shift in mindset:

- An imperative program computes outputs by executing instructions.
- A Tau specification constrains outputs by stating relationships.

During execution, Tau requests values for input streams and then uses a solver to pick output values that satisfy the constraints.

## Part III: the same system in three layers (FSM, recurrence, specification)

The turnstile can be written in at least three closely related forms.

### Layer 1: a state machine (graph)

This is the diagram above: states and labeled transitions.

### Layer 2: a recurrence (a step function)

One can name a transition function:

$$
state_{t+1} = step(state_t, event_t).
$$

This is the functional lens: the whole behavior is determined by an initial state and a repeated application of a step function.

### Layer 3: a Tau specification (constraints over time)

In Tau, a typical pattern is:

- encode the state as an output stream `s[t]`,
- encode the input event as an input stream `e[t]`,
- constrain `s[t]` in terms of `s[t-1]` and `e[t]`,
- add invariants as additional constraints.

The implementation details of this encoding are flexible. The invariants are the point.

### A side note: programs as decision trees (and why state matters)

The turnstile rules above can be read as a case split: given the current state and the current event, pick the next state and outputs.
That is the same structure as a decision tree.

For straight-line code, the decision tree is finite.
For code with loops, the decision tree is conceptually infinite: it keeps branching as time continues.
State machines and stream specifications are ways to describe that infinite unfolding compactly.

## Part IV: cards in Tau (an approximate state tracker)

Tutorial 1 built a precise mental picture for an approximate state tracker (a running count).
There is a runnable Tau version here:

- `examples/tau/card_counting_hilo_state_tracker.tau`

From the repo root:

```bash
./scripts/run_tau_policy.sh examples/tau/card_counting_hilo_state_tracker.tau
```

This example follows a useful convention: parsing is pushed out of Tau.
The input stream provides the already-classified delta (`+1`, `0`, `-1`), and Tau only enforces the update rule and basic validity checks.

## Part V: a toggle puzzle in Tau (and why it wants linear algebra)

Now connect back to Tutorial 2's "puzzle becomes linear algebra" example.

The key observation is that a board of on/off lights is a bitvector, and toggling is XOR.
In Tau, XOR is written `^` in terms.

There is a runnable Tau model of a tiny toggle puzzle here:

- `examples/tau/toggle_puzzle_xor_state.tau`

The spec is just a state update:

$$
board_t = board_{t-1} \oplus move_t.
$$

Once the system is expressed as XOR addition over bits, the same structure is visible as linear algebra over $\mathbb{F}_2$.
That translation is the leverage move from Tutorial 2.

## Part VI: Q-learning as a lookup table (and what Tau can check)

### What a lookup table really is

A lookup table is a representation of a function on a finite domain.

For tabular Q-learning, the domain is `(state, action)` and the values are numbers:

$$
Q : S \times A \to \mathbb{N}.
$$

If `S` and `A` are finite, then a table is just a list of entries with a chosen ordering.
That is a literal isomorphism: "grid of values" and "vector of values" are the same structure up to reindexing.

### The Q-learning update (one step)

In one common form, the update is:

$$
Q(s,a) \leftarrow (1 - \alpha)\,Q(s,a) + \alpha\Bigl(r + \gamma \max_{a^{\prime}} Q(s^{\prime},a^{\prime})\Bigr).
$$

This tutorial uses a simplified, integer-friendly version in a tiny state/action space.
The point is not floating point math. The point is the shape:
one entry in a table is updated using the reward and the best predicted next value.

### A runnable Tau example: tabular update (2x2 table)

There is a runnable Tau spec that maintains a 2x2 Q-table and updates exactly one entry per step:

- `examples/tau/q_learning_tabular_update.tau`

Each step supplies:

- the chosen `(state s, action a)` as two 0/1 bits,
- a reward `r`,
- a provided `q_next` value (a stand-in for the usual `max_{a'} Q(s',a')` term),
- the current table entries `Q00, Q01, Q10, Q11`,
- and a `learn` bit that toggles whether an update happens.

The spec computes `target = r + q_next` and enforces one clean invariant:
if `learn = 1`, exactly one table entry changes (the one selected by `(s,a)`), and it changes to `target`.
All other entries must remain unchanged. If `learn = 0`, the output table equals the input table.

This is the main "Tau + lookup table" move: the host system can choose or learn numbers,
but Tau can enforce that updates are shaped correctly and do not touch anything else.

In practice, that combination is useful because it lets a system be both adaptive and auditable:

- The table is a concrete artifact (a small function on a finite domain) that can be logged, diffed, and replayed.
- The Tau constraints act like guardrails: "only this entry updates", "updates obey this equation", "values stay in range", and so on.
- When something goes wrong, the failure mode is a counterexample trace, not a vague "the model feels off".

## Part VII: tables, weights, latent space (isomorphism or not)

### Lookup tables vs neural network weights

A Q-table is a concrete representation of a function on a small discrete domain.
A neural network is also a representation of a function, but with a different parameterization.

There are two different questions that sound similar:

1. Are two representations both capable of expressing the same input-output behavior?
2. Is there a 1-to-1, structure-preserving map between the representations?

For tables and weights, (1) can be true in many cases, but (2) is generally false.
The map "weights -> behavior" is usually many-to-one:
different weight settings can compute the same function (symmetries, redundancy, overparameterization).
That is an equivalence relation, not an isomorphism.

<figure class="fp-figure">
  <p class="fp-figure-title">Table, weights, meaning</p>
  {% include diagrams/tau-table-weights-meaning.svg %}
  <figcaption class="fp-figure-caption">
    A table has a direct, lossless correspondence with a function on a finite domain. A weight vector often has many distinct parameter settings that denote the same function.
  </figcaption>
</figure>

### Latent space as a learned abstraction

In deep learning, a latent vector is a learned representation of an input.
It is best understood as an abstraction: it forgets many details while preserving the distinctions the model needs to make a prediction.

From the "spaces" point of view, several different spaces show up:

- **state space**: the world states the environment can be in,
- **table space**: the space of all Q-tables (one coordinate per entry),
- **weight space**: the space of all neural network parameters,
- **latent space**: the internal representation space the model learns.

"Learning" and "verification" become different kinds of motion through these spaces.
One searches for counterexamples in a state space. The other searches for parameters that score well on data.

<figure class="fp-figure">
  <p class="fp-figure-title">State spaces and parameter spaces</p>
  {% include diagrams/tau-spaces-traversal.svg %}
  <figcaption class="fp-figure-caption">
    Formal methods and machine learning both involve search. The difference is what space is being traversed and what counts as evidence.
  </figcaption>
</figure>

## Where this tutorial goes next

Next tutorials can build on this in two directions:

- use Tau as a small "logic kernel" inside a larger toolchain (host computes rich checks, Tau enforces rails),
- connect Tau execution with counterexamples and synthesis loops.
