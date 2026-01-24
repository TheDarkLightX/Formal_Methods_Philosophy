---
title: Tau Language (invariants first, then execution)
layout: docs
kicker: Tutorial 3
description: Learn to read and write small executable specifications by listing invariants first, then letting a solver choose behaviors that satisfy them.
---

This tutorial is about a shift in how you think about writing programs.

Instead of giving step-by-step instructions ("do this, then do that"), you state what must always be true.
Then a solver figures out the steps for you.

That sounds abstract. So we will start with a concrete habit: before writing any code, write a list of sentences that are meant to stay true forever.
Those sentences are your invariants.
Everything else, such as syntax, types, and stream declarations, is just scaffolding to make the invariants executable.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Mental pictures to keep</p>
  <ul>
    <li>A timeline of streams: inputs and outputs indexed by time, like frames in a film</li>
    <li>An invariant as a rail: the system can move, but not off the rails</li>
    <li>A solver as a witness generator: it finds concrete values that make your constraints true</li>
    <li>Three lenses for the same system: state machine, recurrence relation, logic specification</li>
  </ul>
</div>

All examples in this tutorial are runnable from files under `examples/tau/`.
Each file is a self-contained transcript that runs end-to-end without manual typing.

## Part I: inside your head (invariants before syntax)

Imagine you are designing a turnstile at a subway entrance.

You do not start by writing code. You start by stating what must always be true:

1. The turnstile is always in one of two states: **Locked** or **Unlocked**.
2. Inserting a coin when locked unlocks it.
3. Pushing through when unlocked locks it again.
4. Pushing through when locked triggers an alarm.
5. No alarm when unlocked.

These are your invariants. They decide most design choices before you touch a keyboard.
They say what the state is, what inputs exist, and what must never be violated.

This is the habit that makes specifications readable: invariants first, then syntax.

<figure class="fp-figure">
  <p class="fp-figure-title">A tiny turnstile state machine</p>
  {% include diagrams/tau-turnstile-fsm.svg %}
  <figcaption class="fp-figure-caption">
    The same system can be viewed as a state machine (states and arrows) or as logical constraints relating current and next values. Both views are correct; they emphasize different things.
  </figcaption>
</figure>

### Why start with invariants?

When you start with syntax, you get lost in details: "What type is this? How do I declare that? Why is the compiler unhappy?"

When you start with invariants, you stay oriented. The invariants are the spec.
Everything else exists to make them checkable.

## Part II: reading Tau (streams, time, and constraints)

Tau specifications talk about **streams**: sequences of values indexed by time.
Think of them like frames in a film, numbered 0, 1, 2, 3, ...

- **Input streams** (`i1`, `i2`, ...) receive values from the outside world.
- **Output streams** (`o1`, `o2`, ...) produce values computed by the spec.

At each time step `t`, the spec relates inputs and outputs.
In Tau, `t` is a logical variable ranging over time steps: a constraint written with `t` is meant to hold for every time step, not as a one-step instruction.

<div class="fp-callout fp-callout-warn">
  <p class="fp-callout-title"><code>t</code> is not a loop variable</p>
  <p>
    In imperative code, a loop counter <code>t</code> advances as the program runs. In Tau, <code>t</code> is a variable that ranges over time steps all at once.
    A line like <code>o1[t] = o1[t-1] + i1[t]</code> is a relationship that must hold at every step, not an instruction executed at one step.
  </p>
</div>

### Declaring streams

```tau
i1 : bv[8] := in console   # input stream, 8-bit values
o1 : bv[8] := out console  # output stream, 8-bit values
```

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Types used in these examples</p>
  <ul>
    <li><code>bv[8]</code>: an 8-bit bitvector (values 0–255). Arithmetic wraps around; 255 + 1 = 0.</li>
    <li><code>sbf</code>: a simple Boolean function. In these tutorials we use it like a 0/1 flag for "valid?", "alarm?", and "solved?" signals.</li>
  </ul>
</div>

### Writing constraints

A constraint relates values at the current time step (and possibly earlier steps):

```tau
o1[t] = o1[t-1] + i1[t]
```

This says: "the output at time `t` equals the previous output plus the current input."
It is a running sum.

<figure class="fp-figure">
  <p class="fp-figure-title">Time indices as a sliding stencil</p>
  {% include diagrams/tau-time-index.svg %}
  <figcaption class="fp-figure-caption">
    A term like <code>t-1</code> means "one step earlier." A constraint with <code>t</code> is like a stencil that is applied at every time step.
  </figcaption>
</figure>

### How to read <code>t-1</code> and <code>t-2</code> (unroll it)

The most reliable mental move is to temporarily replace <code>t</code> with concrete numbers.

If a spec contains:

```tau
o1[t] = o1[t-1] + i1[t]
```

then the first few instances look like:

```tau
o1[1] = o1[0] + i1[1]
o1[2] = o1[1] + i1[2]
o1[3] = o1[2] + i1[3]
```

That is all <code>t-1</code> means: "the previous frame."
Similarly, <code>t-2</code> means "two frames back." If a constraint uses <code>t-2</code>, unrolling it will show dependencies that skip one step.

If the state-machine picture is easier to hold in mind, read the indices like this:

- <code>o1[t-1]</code>: the state before the transition
- <code>i1[t]</code>: the event/input at this step (the arrow label)
- <code>o1[t]</code>: the state after the transition

Tau writes the transition rule as an equation over these time-indexed values.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">A small but important detail: <code>t-1</code></p>
  <p>
    When a constraint mentions <code>t-1</code>, it only makes sense starting at <code>t = 1</code>.
    That is why examples also include initial conditions like <code>o1[0] = ...</code> to define the base case.
  </p>
</div>

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Fixed indices vs offsets</p>
  <ul>
    <li><code>o1[0]</code> means "the value at time 0" (a fixed index).</li>
    <li><code>o1[t]</code> means "the value at time <code>t</code>" (a universally-scoped time variable).</li>
    <li><code>o1[t-1]</code> means "one step earlier than <code>t</code>" (a relative offset).</li>
  </ul>
  <p>
    Writing <code>t-0</code> is unnecessary, because it is the same as <code>t</code>. In specs, the meaningful contrast is usually between <code>[0]</code> (an anchor) and <code>[t-1]</code> (a delay).
  </p>
</div>

### The mindset shift

This is where Tau differs from ordinary programming:

- An **imperative program** computes outputs by executing instructions step by step.
- A **Tau specification** constrains outputs by stating relationships that must hold.

During execution, Tau asks for input values, then uses a solver to find output values that satisfy all the constraints.
The specification describes the rails; the solver finds a path that stays on them.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Two operator families (a common source of mistakes)</p>
  <ul>
    <li><code>&amp; | ' ^</code> are <em>term</em> operators (bit-level operations on values)</li>
    <li><code>&amp;&amp; || ! &lt;-&gt;</code> are <em>formula</em> operators (logical connectives combining constraints)</li>
  </ul>
  <p>
    A comparison like <code>x = y</code> is a formula, so it should be combined with <code>&amp;&amp;</code>, not <code>&amp;</code>.
  </p>
  <p>
    In these examples, bit-flips are written with XOR against a mask (for example, <code>x ^ { 1 }:bv[8]</code>), because it makes the intended bit-level change explicit.
  </p>
</div>

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">A practical note: <code>charvar</code></p>
  <p>
    Tau restricts variable names by default. To use longer names like <code>delta_is_valid</code>, every example starts with <code>set charvar off</code>.
  </p>
</div>

## Part III: the same system in three lenses

The turnstile can be described in three equivalent ways.
Each lens emphasizes something different.

### Lens 1: state machine (the picture)

Draw circles for states (Locked, Unlocked) and arrows for transitions (coin, push).
This is the visual view: good for intuition, but hard to execute directly.

### Lens 2: recurrence relation (the function)

Define a step function that takes the current state and event, and returns the next state:

$$
\text{state}_{t+1} = \text{step}(\text{state}_t, \text{event}_t)
$$

This is the functional view. The whole behavior unfolds from an initial state and repeated application of `step`.

### Lens 3: Tau specification (the constraints)

Encode the state as an output stream, encode the event as an input stream, and write constraints:

- `o1[0] = 0` (start locked)
- `o1[t] = 1` if coin and not push (unlock)
- `o1[t] = 0` if push (lock)
- `o2[t] = 1` if push while locked (alarm)

This is the declarative view. You state what must hold; the solver handles the rest.

### Why three lenses?

Different tools want different representations:

- Humans often prefer state machines (visual, local).
- Recursive code uses recurrence relations.
- Constraint solvers use logic specifications.

The key insight from Tutorial 2 (Isomorphism) applies here: these are not three different systems.
They are three equivalent descriptions of the same system.
Picking the right lens for your task is a practical skill.

### Programs as infinite decision trees

The turnstile rules form a case split: given the current state and event, pick the next state.
That is a decision tree.

For code without loops, the tree is finite.
For code with loops, the tree is conceptually infinite. It keeps branching forever.

State machines and stream specifications are compact ways to describe infinite unfoldings.

## Part IV: cards in Tau (an approximate state tracker)

Tutorial 1 built a precise mental picture of a card counter's running score.
Now let's see that same system in Tau.

The runnable example is:

```
examples/tau/card_counting_hilo_state_tracker.tau
```

From the repo root:

```bash
./scripts/run_tau_policy.sh examples/tau/card_counting_hilo_state_tracker.tau
```

### What the spec does

The input stream provides a pre-classified delta: `+1`, `0`, or `-1` (encoded as 8-bit values: 1, 0, or 255).
The output stream maintains a biased running count.

The core constraint is simple:

$$
\text{count}_t = \text{count}_{t-1} + \text{delta}_t
$$

That is it. The spec just enforces the update rule.

### A useful convention: push parsing out of Tau

Notice that Tau does not classify cards. It receives the already-classified delta.
This is a design pattern: keep complex parsing in the host system, let Tau enforce simple invariants.

Why? Tau is good at constraints, not string manipulation. The split keeps both sides clean.

## Part V: a toggle puzzle in Tau (and why XOR is linear algebra)

Now connect back to Tutorial 2's "puzzle becomes linear algebra" example.

Consider a row of lights that are either on or off.
Pressing a button toggles some subset of lights.
The puzzle: turn all lights off.

The insight is that toggling is XOR. A board of lights is a bitvector. Applying a move is:

$$
\text{board}_t = \text{board}_{t-1} \oplus \text{move}_t
$$

where $\oplus$ is bitwise XOR.

The runnable example is:

```
examples/tau/toggle_puzzle_xor_state.tau
```

### Why this matters

XOR over bits is the same as addition in $\mathbb{F}_2$ (the field with two elements).
So "toggle puzzle" and "linear algebra over a finite field" are the same structure.

This is the leverage move from Tutorial 2: recognize an isomorphism, then use tools designed for the target domain.

## Part VI: Q-learning as a lookup table (and what Tau can check)

### What a lookup table really is

A lookup table is a function on a finite domain, stored as a list of values.

For tabular Q-learning, the table maps (state, action) pairs to scores:

$$
Q : S \times A \to \mathbb{R}
$$

If $S$ and $A$ are small and finite, you can literally store every entry.
That is a Q-table: a grid of numbers, one per (state, action) pair.

### The Q-learning update

The classic update rule is:

$$
Q(s,a) \leftarrow (1-\alpha) Q(s,a) + \alpha \left(r + \gamma \max_{a'} Q(s',a')\right)
$$

In words: blend the old value with a target computed from the reward and the best predicted future value.

For this tutorial, we use a simplified integer version: `target = r + q_next`, and if `learn = 1`, the selected entry becomes `target`.

### A runnable Tau example: 2x2 table update

The runnable spec is:

```
examples/tau/q_learning_tabular_update.tau
```

Each step provides:

- `(s, a)`: which entry to update (two 0/1 bits)
- `r`: the reward
- `q_next`: a stand-in for $\max_{a'} Q(s', a')$
- `learn`: whether to update (0 = no, 1 = yes)
- `Q00, Q01, Q10, Q11`: the current table entries

The spec computes `target = r + q_next` and enforces:

- If `learn = 1`: exactly one entry changes to `target`; the others stay the same.
- If `learn = 0`: all entries stay the same.

### What Tau gives you

This is the "Tau + lookup table" pattern:

- The host system chooses which entry to update and what the reward is.
- Tau enforces that the update has the right shape.

The combination is powerful because it separates concerns:

- The table is a concrete artifact you can log, diff, and replay.
- The constraints are guardrails: "only this entry updates," "the update uses this formula."
- When something breaks, you get a counterexample trace, not a mystery.

### A note on closing the loop

This spec models a single update step. It takes the current table as input and produces the updated table as output.

To run multi-step learning, the host system must "close the loop": take the output table and feed it back as the next step's input.
Tau specifies the shape of each step; the host orchestrates the sequence.

## Part VII: tables vs weights vs latent space

### Lookup tables versus neural network weights

A Q-table represents a function on a small discrete domain. Each entry is one input-output pair.

A neural network also represents a function, but parameterized differently: by weights.

Two questions that sound similar but are not:

1. **Expressiveness**: Can both representations compute the same input-output behavior?
2. **Isomorphism**: Is there a 1-to-1, structure-preserving map between them?

For tables and neural networks, (1) can be true. A small network can compute the same function as a table.
But (2) is generally false. The map "weights → behavior" is many-to-one: different weight settings can compute the same function.

That is an equivalence relation (same behavior), not an isomorphism (same structure).

<figure class="fp-figure">
  <p class="fp-figure-title">Table, weights, meaning</p>
  {% include diagrams/tau-table-weights-meaning.svg %}
  <figcaption class="fp-figure-caption">
    A table has a direct, lossless correspondence with a function on a finite domain. A weight vector often has many distinct settings that compute the same function.
  </figcaption>
</figure>

### Latent space as a learned abstraction

In deep learning, a latent vector is the model's internal representation of an input.
It is an abstraction: it forgets details while preserving distinctions the model needs.

From the "spaces" perspective:

- **State space**: all configurations the environment can be in.
- **Table space**: all possible Q-tables (one coordinate per entry).
- **Weight space**: all possible neural network parameters.
- **Latent space**: the internal representation space the model learns.

"Learning" and "verification" are different kinds of search through these spaces:

- Learning searches parameter space for weights that score well on data.
- Verification searches state space for counterexamples that break an invariant.

<figure class="fp-figure">
  <p class="fp-figure-title">State spaces and parameter spaces</p>
  {% include diagrams/tau-spaces-traversal.svg %}
  <figcaption class="fp-figure-caption">
    Formal methods and machine learning both involve search. The difference is which space you traverse and what counts as evidence.
  </figcaption>
</figure>

## Running the examples

All examples live in `examples/tau/`. To run them:

1. Build Tau (once):
   ```bash
   ./scripts/update_tau_lang.sh
   ```

2. Run an example:
   ```bash
   ./scripts/run_tau_policy.sh examples/tau/turnstile_fsm_alarm.tau
   ```

Each `.tau` file is a self-contained REPL transcript: it declares streams, runs the spec, feeds demo inputs, and quits.
You can read the file to see both the spec and the expected behavior.

## Where this tutorial goes next

This tutorial introduced Tau as a way to write executable specifications.
The key habit: invariants first, syntax second.

Next directions:

- Use Tau as a small "logic kernel" inside a larger system: the host computes complex checks, Tau enforces guardrails.
- Connect Tau execution with counterexamples and synthesis loops (CEGIS).
- Build more complex state machines with multiple interacting streams.

If you want to see how constraints connect to learning systems, read [Tutorial 4: World Models]({{ '/tutorials/world-models/' | relative_url }}).
