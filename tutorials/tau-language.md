---
title: Tau Language (invariants first, then execution)
layout: docs
kicker: Tutorial 3
description: Learn to read and write small executable stream specifications in Tau, starting from invariants and the common stepwise fragment.
---

This tutorial is about a shift in how to think about writing programs.
Once the idea clicks, Tau starts to feel much less alien.

Tau is not imperative code with odd punctuation.
It is a declarative language for typed input and output streams.

Instead of giving a step-by-step recipe ("do this, then do that"), a Tau spec says how current and earlier stream values may relate over time.
If the spec is satisfiable in Tau's execution sense, Tau can run it step by step: read the current inputs, solve for the current outputs without peeking at future inputs, advance time, repeat.

One careful point matters from the start.
A Tau specification usually denotes a set of possible programs, not just one program.
When that set is non-empty, Tau executes one deterministic representative from it.

That can sound a bit slippery on first contact, so this tutorial starts with a concrete habit: before writing any code, write a list of sentences that are meant to stay true forever.
Those sentences are your invariants.
Everything else, such as syntax, types, and stream declarations, is just scaffolding to make the invariants executable.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Mental pictures to keep</p>
  <ul>
    <li>A timeline of streams: inputs and outputs indexed by time, like frames in a film</li>
    <li>An invariant as a rail: the system can move, but not off the rails</li>
    <li>A solver as a witness generator: it finds concrete current outputs that keep the constraints true</li>
    <li>Three lenses for the same system: state machine, recurrence relation, logic specification</li>
  </ul>
</div>

All examples in this tutorial are runnable from files under `examples/tau/`.
Each file is a self-contained transcript that runs end-to-end without manual typing.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Scope of this tutorial</p>
  <p>
    This page teaches the common beginner fragment: typed input and output streams, initial conditions like <code>o1[0] = ...</code>, and bounded-lookback constraints such as <code>o1[t] = ...</code> or <code>o1[t] = f(o1[t-1], i1[t])</code>.
    Full Tau also has explicit temporal operators such as <code>always</code> (<code>[]</code>) and <code>sometimes</code> (<code>&lt;&gt;</code>), quantifiers, and the special <code>tau</code> type for talking about Tau specs as values.
  </p>
</div>

## Part I: inside your head (invariants before syntax)

Imagine designing a turnstile at a subway entrance.

You do not start by writing code. You start by stating what must always be true:

1. The turnstile is always in one of two states: **Locked** or **Unlocked**.
2. Inserting a coin when locked unlocks it.
3. Pushing through when unlocked locks it again.
4. Pushing through when locked triggers an alarm.
5. No alarm when unlocked.

These are your invariants. They do most of the real design work before a keyboard even enters the story.
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

When the starting point is syntax, it is easy to get trapped in details: "What type is this? How is that declared? Why is the compiler unhappy already?"

When the starting point is invariants, orientation comes first. The invariants are the spec.
Everything else exists to make them checkable.

## Part II: reading Tau (the practical version)

Tau is easiest to read if it is pictured as a row of time-stamped boxes.
That picture may feel almost too simple, but it really does carry a lot of the tutorial.

A **stream** is just a sequence of values indexed by time.
Think of it like frames in a film, numbered 0, 1, 2, 3, ...

- **Input streams** (`i1`, `i2`, ...) receive values from the outside world.
- **Output streams** (`o1`, `o2`, ...) produce values computed by the spec.

At each time step `t`, the spec relates inputs and outputs.
In Tau, `t` is not "the current loop counter." It is a placeholder that means "for every step like this one."

<div class="fp-callout fp-callout-warn">
  <p class="fp-callout-title"><code>t</code> is not a loop variable</p>
  <p>
    In imperative code, a loop counter <code>t</code> advances as the program runs. In Tau, <code>t</code> is a variable that ranges over time steps all at once.
    A line like <code>o1[t] = o1[t-1] + i1[t]</code> is a relationship that must hold at every step, not an instruction executed at one step.
  </p>
  <p>
    Also, a Tau spec with no explicit <code>always</code> or <code>sometimes</code> is implicitly read as <code>always</code>. That is why a bare line like <code>o1[t] = ...</code> is understood as a standing rule.
  </p>
</div>

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Time-compatible means no retroactive cheating</p>
  <p>
    The theory behind Tau uses the idea of a <em>time-compatible</em> (or prefix-preserving) behavior. If two input histories are the same up to step <code>n</code>, the produced output histories must also be the same up to step <code>n</code>. New future inputs are not allowed to reach back and rewrite earlier outputs. That is the clean formal version of "no time travel tricks."
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
    <li><code>bv[8]</code>: an 8-bit bitvector (values 0 to 255). Arithmetic wraps around; 255 + 1 = 0.</li>
    <li><code>sbf</code>: a Boolean-algebra type that we use here like a 0/1 flag for "valid?", "alarm?", and "solved?" signals.</li>
    <li><code>tau</code>: a Tau specification treated as a value. It matters in full Tau, but this page sticks to <code>bv[8]</code> and <code>sbf</code> examples.</li>
  </ul>
</div>

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Why Boolean algebra keeps showing up</p>
  <p>
    Tau is not built around plain yes-or-no booleans alone. Its stream values live in typed Boolean-algebra settings. In one example that means bitvectors and bitwise operations. In another it means symbolic Boolean-function values. That shared algebraic backbone is why the language can reuse the same basic operators across several kinds of objects.
  </p>
</div>

### Writing constraints

In the fragment used on this page, a top-level Tau spec is a formula.
The value side is a **term**, for example <code>o1[t-1] + i1[t]</code>.
The full statement is a **formula**, for example <code>o1[t] = o1[t-1] + i1[t]</code>.

A common beginner pattern is a formula that relates values at the current time step, and sometimes earlier steps too:

```tau
o1[t] = o1[t-1] + i1[t]
```

Plain English: "take the old value, add the new input, and that gives the new value."
That is just a running sum.
This is a good example of a Tau line that looks more forbidding than it really is.

<figure class="fp-figure">
  <p class="fp-figure-title">Time indices as a sliding stencil</p>
  {% include diagrams/tau-time-index.svg %}
  <figcaption class="fp-figure-caption">
    A term like <code>t-1</code> means "one step earlier." A constraint with <code>t</code> is like a stencil that is applied at every time step.
  </figcaption>
</figure>

### How to read <code>t-1</code> and <code>t-2</code> (unroll it)

The safest way to read Tau is to stop being abstract for a moment and plug in actual numbers.
This is worth doing often. Tau gets friendlier very quickly once the symbols are forced to commit to one concrete step.

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

Most runnable examples on this page have **bounded lookback**.
That just means the rule for step <code>t</code> only looks at a fixed finite window, such as <code>t</code> and <code>t-1</code>, or <code>t</code>, <code>t-1</code>, and <code>t-2</code>.
This is the recurrence-shaped fragment that feels most like "state update," even though Tau itself is phrased in streams rather than mutable variables.

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

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Why "state" often shows up as an output stream</p>
  <p>
    Tau allows current outputs to depend on earlier outputs. So memory is already built into the language. In beginner examples like the turnstile, the running count, or the toggle board, the thing called "state" is usually just an output stream whose previous value is read at the next step.
  </p>
</div>

### The mindset shift

This is the biggest mindset shift in the page:

- An **imperative program** computes outputs by executing instructions step by step.
- A **Tau specification** constrains outputs by stating relationships that must hold.

During execution, Tau receives the current inputs and solves for the current outputs in a way that keeps the spec true now and still compatible with continuing later.
One good mental model is "fill in the blanks for this step, but only in ways that keep the run extendable."
It is less like writing instructions for a machine to follow, and more like laying down rails and asking for the next legal move.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Tau satisfiability is stronger than one-shot satisfiability</p>
  <p>
    Roughly, Tau is not asking only "is there one trace that works?" A satisfiable Tau spec must admit indefinite execution for every input stream, with outputs chosen step by step, without dependence on future inputs, and in a way that stays time-compatible as the run grows.
  </p>
</div>

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Scope check: what Tau does and does not do</p>
  <ul>
    <li><strong>Tau does:</strong> enforce relationships between typed streams, and solve current outputs from the current history</li>
    <li><strong>Tau does not:</strong> parse messy inputs, own the environment loop, or replace the host system that feeds outputs back into future inputs</li>
    <li><strong>Practical split:</strong> host code handles orchestration, Tau handles the logic kernel</li>
  </ul>
</div>

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
Nothing about the system changes. Only the notation changes.

### Lens 1: state machine (the picture)

Draw circles for states (Locked, Unlocked) and arrows for transitions (coin, push).
This is the visual view: good for intuition, but hard to execute directly.

### Lens 2: recurrence relation (the function)

Define a step function that takes the current state and event, and returns the next state:

$$
\mathrm{state}_{t+1} = \mathrm{step}(\mathrm{state}_t, \mathrm{event}_t)
$$

This is the functional view. The whole behavior unfolds from an initial state and repeated application of `step`.

### Lens 3: Tau specification (the constraints)

Encode the state as an output stream, encode the event as an input stream, and write constraints:

- `o1[0] = 0` (start locked)
- `o1[t] = 1` if coin and not push (unlock)
- `o1[t] = 0` if push (lock)
- `o2[t] = 1` if push while locked (alarm)

This is the declarative view. For this tiny example, the constraints pin down one behavior. In general Tau can leave several behaviors admissible, then execution picks one deterministic representative.
Same turnstile, different accent.

### One turnstile step through all three lenses

Take one concrete moment:

- at time `t-1`, the turnstile is **Locked**
- at time `t`, a **coin** arrives
- at time `t`, there is **no push**
- at time `t`, the next state should be **Unlocked**

Here is the same event in three forms:

- **State machine:** `Locked --coin--> Unlocked`
- **Recurrence instance:** `state_t = step(Locked, coin) = Unlocked`
- **Tau instance:** if `o1[t-1] = 0 && coin[t] = 1 && push[t] = 0`, then `o1[t] = 1`

<figure class="fp-figure">
  <p class="fp-figure-title">One event, three equivalent lenses</p>
  {% include diagrams/tau-three-lenses.svg %}
  <figcaption class="fp-figure-caption">
    The picture, the recurrence, and the Tau clause are doing the same job. They differ in notation, not in meaning.
  </figcaption>
</figure>

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

That is it. No hidden cleverness. The spec just enforces the update rule.

### A useful convention: push parsing out of Tau

Notice that Tau does not classify cards. It receives the already-classified delta.
This is a design pattern: keep complex parsing in the host system, let Tau enforce simple invariants.

Why? Tau is good at constraints, not string manipulation. The split keeps both sides clean, and it keeps the spec focused on the part that is actually worth checking.

## Part V: a toggle puzzle in Tau (and why XOR is linear algebra)

Now connect back to Tutorial 2's "puzzle becomes linear algebra" example.

Consider a row of lights that are either on or off.
Pressing a button toggles some subset of lights.
The puzzle is simple to state and strangely satisfying to solve: turn all lights off.

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

This is the leverage move from Tutorial 2: recognize an isomorphism, then use tools designed for the target domain. A puzzle that looked fiddly by hand becomes crisp once it is seen in the right language.

## Part VI: Q-learning as a lookup table (and what Tau can check)

### What a lookup table really is

A lookup table is a function on a finite domain, stored as a list of values.
There is nothing mystical about it. It is just a very explicit function representation.

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

For this tutorial, we use a much smaller executable toy. The table entries are `bv[8]` values, and the update is simplified to `target = r + q_next`. If `learn = 1`, the selected entry becomes `target`.

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
- When something breaks, there is a counterexample trace to inspect instead of a vague sense that "training went oddly."

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

That is an equivalence relation (same behavior), not an isomorphism (same structure). Same outcome, different internal bookkeeping.

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
