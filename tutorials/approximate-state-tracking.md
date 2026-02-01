---
title: Approximate state tracking (cards)
layout: docs
kicker: Tutorial 1
description: A deck of cards as a concrete mental model for state machines, abstraction, symbolic tools, and counterexamples.
---

This tutorial builds one of the most important muscles in formal methods: the ability to hold two pictures at once.

1. The inside view: a human updates a tiny mental state from a stream of observations.
2. The outside view: a transition system, an abstraction function, and tools that search for refuters.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Key mental images</p>
  <ul>
    <li>A running score as a dial that moves one notch per observation</li>
    <li>A balance: what you saw versus what remains hidden</li>
    <li>An abstraction map α from huge concrete state to small abstract state</li>
    <li>A counterexample as a single witness that breaks an “always” claim</li>
  </ul>
</div>

<figure class="fp-figure">
  <p class="fp-figure-title">Two accurate pictures of the running score</p>
  {% include diagrams/dial-and-scale.svg %}
  <figcaption class="fp-figure-caption">
    The score is both a running dial and a balance. The balance picture is the clean intuition: if the full deck starts “balanced” (total weight 0), then what remains hidden must mirror what you have already seen.
  </figcaption>
</figure>

## Part I: Inside the counter’s head

Imagine you are watching cards come off a shoe in blackjack.

You know there is a real, perfectly definite state of the world:

- exactly which cards remain unseen,
- and (if you care about exact future order) which order they would appear in if you could peek.

But you cannot see that state. You only see a stream of observations: each revealed card.

So you do what humans always do when the world is too detailed to hold in your head:
you maintain a small internal summary that updates as you see new evidence.

Think of it like keeping score in a game. You do not remember every move in perfect detail;
you keep one or two numbers that you can update instantly.

### The counter’s internal state

Most counters do not think “tuple.” They think “I’m keeping a running score, and I have a sense of how much shoe is left.”

- Running score (`running_count`): a whole number you keep in your head and update every time you see a card.
- How much is left (`decks_remaining_estimate`): a rough estimate of how much of the shoe remains (often eyeballed, not measured).

Calling `running_count` a “variable” just means it’s a named value that changes over time. Each new card nudges it up, down, or not at all.

This is one concrete example of an approximate tracker: it keeps some information about the past (what you have seen), but intentionally discards most details (exact identities, exact remaining composition, exact order).

Many systems also compute a derived value, often called a “true count”:

```
true_count ≈ running_count / decks_remaining_estimate
```

The important part for this tutorial is not the gambling move it might drive, but the cognitive pattern:
keep a small state, update it online, and query it as if it were “the state that matters.”

If you like, you can call this a tiny “world model”: not a full picture of the hidden deck, but a compressed belief-summary that preserves just the distinctions you’re using to decide.

### The update rule (as experienced)

From your perspective, each card triggers the same tiny loop:

1. Observe the new card.
2. Classify it (low / high / middle) and apply the `+1 / -1 / 0` rule you have memorized.
3. Update your running score (`running_count`).

That’s it.

You are not enumerating all possible deck configurations.
You are not simulating all possible futures.
You are not proving theorems.

You are executing a very small, very fast state update that fits in working memory.

### Why this works (philosophically)

Even though the world has enormous detail, you act as if a small summary is “the state that matters.”

This is the first key idea we will reuse in formal methods:

> We rarely track the full state. We track the right state: an abstraction that preserves the distinctions relevant to our question.

In blackjack, the “question” is something like “are high cards unusually likely soon?”
In software and math, the question is often “can something bad happen?” or “does this invariant always hold?”

The common theme is the same: choose a state representation that fits your goal.

## Part II: Zooming out. What is an approximate state tracker?

Now we stop speaking in second person and name the moving parts.

### State machines (the outside view)

A state machine is a way to talk about systems that change over time:

- a set of states `S`,
- an initial state `s0`,
- transitions that describe how the system can evolve.

In the deck-of-cards world, there are at least two useful “levels” of state:

1. Concrete state (what is really true): exactly which cards remain (and optionally their order).
2. Abstract state (what you track): a small summary like a running score (`running_count`).

<figure class="fp-figure">
  <p class="fp-figure-title">Concrete transitions versus abstract transitions</p>
  {% include diagrams/state-machine-abstraction.svg %}
  <figcaption class="fp-figure-caption">
    The concrete machine updates the real world state (the remaining deck). The abstract machine updates a small summary. The abstraction function α connects the two levels.
  </figcaption>
</figure>

### Concrete state: exact remaining cards

One clean model is:

- `R` is the multiset of remaining cards (for a multi-deck shoe there are duplicates).
- Each observation reveals a card `c`.
- The concrete transition removes that card from `R`.

So a concrete step looks like:

```
(R)  --observe c-->  (R \ {c})
```

Even for a single deck, the concrete state space is enormous:

- If you care about remaining order, there are `52!` possible orders.
- If you only care about which cards remain, there are `2^52` possible subsets.

Both are finite, but far beyond what a human (or naive program) can enumerate.

### Abstract state: a compressed summary

An approximate state tracker is what you get when you replace concrete state with a smaller, information-losing representation.

Formally, you pick:

- an abstract state space `A` (small enough to handle),
- an abstraction function `α : S → A` (how concrete states map to abstract states),
- an abstract update rule `δ̂ : A × Obs → A` (how you update the abstract state from observations).

In the counting example:

- `A = ℤ` (integers) if you only track `running_count`, or `A = ℤ × ℝ_{>0}` if you also track a (possibly rough) `decks_remaining_estimate`,
- `Obs = {cards you can observe}`,
- `δ̂(count, card) = count + weight(card)`.

That’s the mathy way to say: you can track one dial, or you can track two dials.

<figure class="fp-figure">
  <p class="fp-figure-title">Abstraction: many concrete states, one abstract state</p>
  {% include diagrams/abstraction-map.svg %}
  <figcaption class="fp-figure-caption">
    Abstraction is not “hand-waving.” It is a function that deliberately forgets details while preserving the distinctions relevant to a question. Soundness asks whether the abstraction ever misses a real behavior.
  </figcaption>
</figure>

### Finite vs infinite domains

This is where formal methods begins to feel “different” than toy examples:

- The deck is finite (there are finitely many physical configurations).
- Many programs have effectively infinite state spaces (unbounded integers, heaps, recursion, message queues).

Even when a system is technically finite (because memory is finite), its state space can be so large that you must treat it as infinite for reasoning purposes.

The philosophical point:

> Formal methods is largely the art of turning an intractable concrete universe into a tractable abstract one without losing the truths you care about.

### Enumeration vs transitions

Two ways people first imagine “analyzing a system” are:

1. Enumeration: list all states, check all of them.
2. Transitions: describe how states evolve, reason about reachability.

Enumeration breaks immediately in large systems (state explosion).
So tools lean hard on transitions, structure, and symbolic representations.

## Part III: From concrete states to symbolic states

Humans manipulate stories (“I saw three low cards in a row, so…”).
Formal tools manipulate symbols.

### What does “symbolic” mean here?

A symbolic representation encodes many possibilities at once.

Instead of writing down one concrete remaining deck `R`,
you write constraints describing a set of possible decks consistent with what you’ve observed.

For example, after seeing some cards, you might know:

- there are `k` cards left,
- you have removed exactly one Ace so far,
- your running score (`running_count`) is `+3`.

Each of those statements is a constraint. Together they define a space of possible concrete states.

### Tools that “move symbols”

Different tools specialize in different symbolic objects:

- SAT/SMT solvers manipulate logical formulas (“is there an assignment that makes this true?”).
- Model checkers manipulate transition relations (“can I reach a bad state from the start?”).
- Abstract interpreters compute conservative summaries (“what can variables be at this program point?”).

In all cases, the tool’s superpower is the same:

> It can reason about huge (even infinite) spaces by transforming symbolic descriptions instead of enumerating concrete states.

### State space as a shape you can resize in your mind

When people say “state explosion,” they often mix three different problems:

1. The system can do too many different things (too many reachable behaviors).
2. The representation is too large to handle directly (even if the behavior is fixed).
3. The model is too detailed for the question you are asking (you are tracking distinctions you do not need).

The clean mental template is set-shaped.

- `S` is the state space: all states your model allows.
- `Reachable ⊆ S` is what the system can actually reach from the start via transitions.
- `Bad ⊆ S` is the region you want to be impossible.

An invariant is a claim that the reachable region never touches the bad region:

$$
\forall s.\, Reachable(s) \rightarrow \lnot Bad(s)
$$

Equivalently:

$$
Reachable \cap Bad = \emptyset
$$

This is where “size” matters in a precise way.
The truth of the invariant does not depend on whether there are one million states or one trillion.
It depends on whether the intersection is empty.
But the size of the reachable region, and the way it is represented, controls whether you can actually decide emptiness with time and memory you can afford.

<figure class="fp-figure">
  <p class="fp-figure-title">Shrink behavior, compress representation, or abstract away detail</p>
  {% include diagrams/state-space-shrink-compress.svg %}
  <figcaption class="fp-figure-caption">
    “Making the state space smaller” can mean three different moves. Only one of them changes what the system can do. The others change how you represent, or how you approximate, the same underlying behavior.
  </figcaption>
</figure>

#### Shrinking, compression, and abstraction are not the same move

**Shrinking behavior** changes the system or the model so that fewer futures are possible.
In set terms, it makes `Reachable` a smaller subset of `S`.
Examples include bounding resources, removing nondeterminism, forcing protocols to be followed, and using types or interfaces that prevent invalid states from being constructed.

**Compression** changes the encoding of the same semantics.
It is lossless with respect to what it represents.
Symbolic model checking is this idea applied to sets and transitions: instead of listing states, you represent a whole set of states with a compact object such as a Boolean formula or a decision diagram.
The set did not change.
Your description of the set got smaller.

**Abstraction** is deliberate forgetting.
You replace the concrete state space `S` with a smaller space `A`, connected by a many-to-one map `α : S → A`.
This is the move a human card counter makes when they compress a detailed history of cards into a single running count.
It is smaller because it throws information away.

These words can be confusing in everyday speech because “compression” sometimes means “lossy compression.”
In this tutorial, “compression” means “lossless re-encoding,” and “abstraction” means “lossy merging guided by a question.”

#### How abstraction can expand the state space you must consider

Abstraction is usually used to make analysis tractable, but it can also create a larger search problem in one important sense.

For safety proofs, tools often use **over-approximating** abstractions: the abstract model includes every behavior the real system can do, and possibly some extra behaviors that are artifacts of forgetting.
This is a trade:

- You gain soundness. If the over-approximate model cannot reach `Bad`, the real one cannot either.
- You may lose precision. The abstract model might reach a bad state that is not actually reachable in the real system, producing a spurious counterexample.

This is why refinement loops exist.
When a counterexample is spurious, you do not just shrug.
You sharpen the abstraction until it preserves the distinctions that matter for the property.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Mental template: three questions before you touch a tool</p>
  <ul>
    <li>What is my state space, and what does “reachable” mean in this model?</li>
    <li>What is my invariant, and what is the corresponding “bad region” it forbids?</li>
    <li>Am I trying to shrink behavior, compress representation, or change the level of abstraction?</li>
  </ul>
</div>

#### Tools that help you think in these shapes

Different tools align with different mental moves:

- To **compress without changing meaning**: symbolic model checking, SAT/SMT solving, BDDs, and symbolic execution.
- To **abstract on purpose and refine when needed**: abstract interpretation, CEGAR-style refinement loops, and predicate abstraction.
- To **shrink reachable behavior by construction**: strong type systems, typestate and protocol state machines, capability-style APIs, and code generation that enforces valid transitions.

And for humans specifically, the most important “tool” is still the picture:
a reachable region, a bad region, and an invariant that claims the two never meet.
Once you can hold that picture, you can reason about shrinking, compression, and abstraction as distinct levers instead of one vague idea.

### A precise bridge: abstraction as a function

Your running score (the number you keep updating) is not magic; it is a function of what happened.

Think of an “idealized counter” whose memory is perfect but still intentionally limited:

1. There is a concrete run: `s0 → s1 → s2 → ...` driven by observations.
2. There is an abstract run: `a0 → a1 → a2 → ...` where `ai = α(si)`.

If your abstract update rule satisfies:

```
α( δ(s, obs) )  =  δ̂( α(s), obs )
```

then your abstract tracker is an exact tracker of the abstract state, even though it discards concrete details.

This distinction matters:

- “Approximate” can mean information-losing (abstraction).
- It can also mean inexact (errors, noise, heuristic estimates).

Formal methods usually focuses on the first kind (abstraction) and then asks for properties like:

- soundness: the abstraction never misses a real behavior (no false negatives),
- precision: the abstraction does not invent too many impossible behaviors (few false positives).

Card counting, as a human practice, often tolerates imprecision because the goal is not proof; it is a decision under uncertainty.

## Part IV: Counterexamples, black swans, and CEGIS

Now we come to the core epistemic loop of formal methods: state a claim, then actively search for a refuter.
In logic and software, the refuter is a counterexample produced by a tool.
In everyday life and science, the refuter is a surprising observation that forces you to revise what you thought was “always true.”

<figure class="fp-figure">
  <p class="fp-figure-title">A counterexample is a refuter, not an essay</p>
  {% include diagrams/counterexample-refutation.svg %}
  <figcaption class="fp-figure-caption">
    Universal claims fail by a single witness. A model checker’s counterexample trace is the software version of a black swan.
  </figcaption>
</figure>

### What is a counterexample?

A counterexample is not an argument in words; it is a specific witness that breaks a universal claim.

If your claim is:

> “No matter what order the remaining cards are in, my tracker will never be misleading in situation X.”

then a counterexample is:

- a particular remaining deck composition and order,
- a particular sequence of dealt cards,
- that leads to situation `X`,
- where your claimed property fails.

In the deck metaphor, a counterexample is literally a concrete ordering of cards that proves: “your statement about all possible orders is false.”

### Black swans: a counterexample in one image

The black swan is the cleanest mental picture of a counterexample:

- Claim: “All swans are white.”
- Observation: “Here is a black swan.”
- Result: the universal claim is refuted.

In logic, “All swans are white” is a universal statement:

```
∀x. Swan(x) → White(x)
```

And “here is a black swan” means: there exists a specific thing `b` such that it is a swan and not white:

```
Swan(b) ∧ ¬White(b)
```

Now you can see the refutation as a direct contradiction.
From the universal claim and the fact `Swan(b)`, you can derive `White(b)`.
But you also have `¬White(b)`. So the universal claim cannot be true.

### Proofs and refutations (a quick map)

Logic has multiple ways to establish a statement, and a few very crisp ways to refute certain forms.
Formal methods borrows these shapes.

- Direct proof: to prove `∀x. P(x)`, pick an arbitrary `x` and show `P(x)`. To prove `P → Q`, assume `P` and derive `Q`.
- Proof by contrapositive: in classical logic, to prove `P → Q`, it is enough to prove `¬Q → ¬P` (they are equivalent).
- Proof by contradiction (reductio): in classical logic, to prove `P`, assume `¬P` and derive a contradiction (`⊥`).
- Proof by induction: to prove `∀n ∈ ℕ. P(n)`, prove a base case and an inductive step.
- Refutation by counterexample: to refute `∀x. P(x)`, exhibit a specific witness `b` such that `¬P(b)`. People sometimes say “proof by counterexample,” but it is really a proof that the universal statement is false.

Note: some formal methods tools use constructive logic. In constructive logic, `P → Q` implies `¬Q → ¬P`, but the reverse direction does not generally hold. Similarly, “proof by contradiction” gives you `¬¬P`, which is weaker than `P` unless you assume additional principles. This page uses the classical reading unless stated otherwise.

### Witness vs contradiction (two equivalent views)

There are two ways to hold the same idea in your head:

- Witness view (counterexample-first): “To refute an ‘all’ statement, I only need one concrete exception.”
- Contradiction view (proof-style): “Assume the ‘all’ statement; combine it with the exception; a contradiction appears; therefore the ‘all’ statement must be rejected.”

Formal tools tend to think in the witness view: they search for a `b` (or a trace) that makes the property fail, because that witness can be inspected and replayed.
Proofs often present the contradiction view because it makes the logical structure explicit.

### What gets updated (Popper’s point)

In Popper’s picture, the world did not change when you found the black swan. Your map of the world changed.

People use different words for that map:

- World model: the internal picture you use to predict and decide.
- Theory: the same picture written down as explicit, testable general claims. (Here “theory” does not mean “mere guess.”)

In this tutorial, I treat “world model” and “theory” as the same content viewed from two angles: one psychological (in your head), one logical (on paper).

In practice (in the real world), there is an extra nuance: refutations rely on background assumptions.
Maybe the lighting was weird. Maybe `b` isn’t actually a swan. Maybe “white” was defined differently.
So empirically, the conflict is really between claim + background assumptions + observation.
But the core lesson still matches what counterexample-driven tools do: treat a serious refuter as a reason to revise the claim into a new, testable one.

This is Popper’s core idea about knowledge: bold universal claims are never confirmed in the way a theorem is confirmed.
Instead, they earn their status by surviving hard attempts at refutation.

Formal methods makes that idea executable. Instead of hoping to stumble on a black swan, we build tools that systematically search for one.

### Learning and knowledge from counterexamples

A counterexample can update you in two different senses:

- Learning (belief update): you change what you expect about the world or system. This is the Popper loop in human terms: conjecture, refuter, revision.
- Knowledge generation (reusable artifact): you gain a concrete witness you can keep and reuse. In software this often becomes a regression test, a minimal “steps to reproduce” trace, or a refinement constraint for the next candidate.

The epistemic strength depends on the setting:

- In pure logic and mathematics: a counterexample witness is deductive. Once you have `b` with `¬P(b)`, the universal claim `∀x. P(x)` is false, full stop.
- In empirical science: a would-be counterexample is evidence. It pressures your current world model, but you may also revise the assumptions that connect observation to the claim.
- In software verification: a solver’s counterexample is deductive about the formal model you gave it. The “learning step” is mapping it back to reality: is it a real bug, or did you model/specify the system incorrectly?

### From philosophy to software: invariants and traces

In programs we usually do not mean “for all imaginable states.” We mean “for all reachable states.”

Think of an invariant as a guardrail: a statement you want to be true at every step of every execution you consider possible.
Formally, that is closer to:

```
∀s. Reachable(s) → P(s)
```

A counterexample is then a particular reachable state `s*` where the property fails:

```
Reachable(s*) ∧ ¬P(s*)
```

Model checkers do not just hand you `s*`; they typically produce a trace (a sequence of transitions) showing how `s*` is reached.

This is why counterexamples are so valuable in software: the trace is like an automatically generated bug report with a reproducible scenario.

One subtle but important point: the counterexample is always relative to a model.
Sometimes it exposes a real bug in the system. Sometimes it exposes a gap between the model and the system.
Sometimes it even exposes a gap created by an overly coarse abstraction (a “spurious” counterexample), which still teaches you something: you need a sharper model for the question you are asking.

Also note that not every tool gives the same kind of guarantee. Some tools can prove that no counterexample exists (a genuine proof of the invariant, under the model). Other tools only search up to some bound, in which case “no counterexample found” is evidence, not a proof.

### What a counterexample gives you (two payloads)

1. Refutation: “This universal claim is not true as stated.”
2. Guidance: “Here is exactly how it fails.” In software, the trace tells you which steps lead to the bad state. In modeling, it tells you which assumption, abstraction, or candidate needs revision.

### Counterexample-guided synthesis (CEGIS)

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">A practical definition of “learning”</p>
  <p>
    A computer program is said to learn from experience <code>E</code> with respect to some class of tasks <code>T</code> and performance measure <code>P</code>,
    if its performance at tasks in <code>T</code>, as measured by <code>P</code>, improves with experience <code>E</code>. (Tom Mitchell, 1997)
  </p>
</div>

Mitchell’s definition is useful because it makes learning feel less mystical. It is an improvement claim with three handles: tasks <code>T</code>, measurement <code>P</code>, and experience <code>E</code>.

CEGIS can be read in the same shape. The task is “satisfy this spec.” The performance measure is “does the checker accept the candidate?” The experience is the stream of counterexamples.

CEGIS is also the Popper loop turned into an algorithm:

1. Propose a candidate (an invariant, a program, a controller, an abstraction, a proof sketch).
2. Verify it against the specification.
3. If verification fails, obtain a counterexample trace.
4. Refine the candidate to rule out that counterexample (without breaking what already worked).
5. Repeat.

Another way to say step 4: each counterexample becomes a new constraint. The next candidate is required to handle that specific failing case, so the search space tightens over time.

<figure class="fp-figure">
  <p class="fp-figure-title">CEGIS as a refuter loop</p>
  {% include diagrams/cegis-loop.svg %}
  <figcaption class="fp-figure-caption">
    Propose, verify, refute, refine. This is Popper’s philosophy turned into an executable workflow.
  </figcaption>
</figure>

In the deck metaphor:

- You propose a rule (“this running-score threshold always indicates advantage”).
- A tool (or reality) finds a deck order where you are wrong.
- You revise the rule (maybe track one more feature, or tighten the claim).

Over time, the process can converge toward a candidate that withstands many refutation attempts.
Sometimes the loop instead teaches you that your original goal was impossible under your constraints, which is also valuable knowledge.

#### CEGIS as a design and debugging loop

In practice, the counterexample does not only mean “the candidate is wrong.” It means: at least one thing in the triangle is wrong.

- The candidate could be wrong (a bug in the proposed invariant or program).
- The specification could be wrong (the property is not what was intended).
- The model could be wrong (important real-world assumptions are missing, or the abstraction is too coarse).

CEGIS becomes a design and debugging discipline when each counterexample is triaged through that triangle and then turned into a specific refinement.

#### Invariant search (what must never break)

For safety-critical systems, the first candidates are often invariants: statements that should hold for every reachable state.

An invariant proof obligation has a simple shape:

- Base case: the initial state satisfies the invariant.
- Step case: if the invariant holds now, one valid step of the system preserves it.

Written schematically:

$$
\mathrm{Init}(s) \to I(s)
$$

$$
\forall s, s'.\, (I(s) \land \mathrm{Step}(s,s')) \to I(s')
$$

Invariant search is what happens when the first guess at $I$ is not strong enough, and counterexamples are used to strengthen it until the step case stops leaking.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Example: solvency as an invariant in a perpetual exchange</p>
  <p>
    In a perpetual exchange, a central safety claim is solvency: under an explicit set of market and oracle assumptions, the system should never end up owing more than it can pay.
    A simple way to write that goal is: for every reachable state <code>s</code>, total liabilities do not exceed total assets.
  </p>
  <p>
    $$\forall s.\, \mathrm{Reachable}(s) \to \bigl(\mathrm{Liabilities}(s) \le \mathrm{Assets}(s)\bigr)$$
  </p>
  <p>
    The exact accounting identity depends on the design (margining, insurance funds, auto-deleveraging rules, liquidation priorities).
    The point of the example is the workflow: define state, state the invariant, then search for refuters (a price path and action sequence) that violate the invariant.
    Each refuter becomes a design constraint. The next version of the system must handle that case.
  </p>
  <p>
    This is the style of thinking that can prevent whole classes of failures.
    When a system instead relies on implicit assumptions (“liquidity will always be there,” “the oracle cannot be manipulated,” “liquidations always reduce risk”),
    reality will eventually supply a black swan trace.
  </p>
  <p>
    A concrete recent example discussed in the industry is Hyperliquid’s March 2025 JELLYJELLY perps episode: a low-liquidity market created large exposure for Hyperliquid’s liquidity vault,
    validators delisted the market and force-settled positions to prevent a large loss, and the project later reimbursed many users.
    It is a vivid reminder that “solvency” is not a vague hope. It is an invariant (or a set of invariants) that must be engineered, checked, and gated.
  </p>
  <p>
    Further reading: https://docs.hyperliquid.xyz/hyperliquid-docs/trading/delisting
    and https://www.coindesk.com/markets/2025/03/26/hyperliquid-delists-jelly-after-suspicious-market-activity-prompts-security-review/
  </p>
</div>

## Part V: Safety, security, and two developer mindsets

This section shifts from “what is a counterexample?” to “what do we do with it, and why does any of this make software safer?”

I will start with two first person perspectives. They are stylized. Real teams mix these mindsets, and good engineering usually needs some of both.

I am using a well known blockchain culture contrast as a concrete anchor: in a 2021 discussion summarized by Decrypt, Vitalik Buterin defended moving faster with “heuristic arguments” and called deep academic rigor overrated, while Charles Hoskinson defended a more proof and peer review oriented “evidence-based software” posture because money and privacy are at stake. See: https://decrypt.co/72824/vitalik-buterin-takes-swipe-at-cardano-charles-hoskinson-strikes-back

### Perspective A: the heuristic builder (first person)

I am trying to ship something real into a messy world where the biggest failures are often “outside the model.”
Users do not just run my code. They run it in adversarial environments with incentives, weird hardware, weird networks, weird usage, and creative attackers.

So I do not start by asking “can I prove this?” I start by asking “what could go wrong, including the things we forgot to formalize?”

My default tools are:

- mental models, informal math, and engineering judgment
- fast feedback loops: tests, fuzzing, simulation, telemetry, and staged rollouts
- redundancy and defense in depth: multiple checks that fail closed
- social and operational strategies: audits, bug bounties, incident response, and the ability to patch

When I say “heuristic,” I do not mean “random.” I mean “a practical argument that is strong enough to act on, even though it is not a theorem.”
I try to build confidence by stacking multiple imperfect lines of evidence.

How I reach safety and security:

- I aim for systems that degrade gracefully.
- I assume I missed something, so I reduce blast radius.
- I treat production as a teacher: the world will supply counterexamples eventually, so I want to learn quickly and recover quickly.

My limits:

- I cannot honestly say “this can never happen.” At best I can say “we have not seen it happen, and here is why I think it is unlikely.”
- My confidence can silently depend on an assumption I did not notice I was making.
- If the system has too many corners, my intuition can stop tracking the true risk surface.

### Perspective B: the formal methods builder (first person)

I am trying to build software that is predictable in the strongest available sense.
When users’ money, safety, or privacy is at stake, I want fewer “surprises.”

So I start by asking “what is the claim, exactly?” and I make the claim explicit enough that a tool can check it.
I treat ambiguity as a bug in the specification.

My default tools are:

- explicit state machines and invariants
- proof obligations and machine-checked proofs (or model checking) where feasible
- designs that make invalid states unrepresentable (types, protocol state machines, restricted interfaces)
- counterexample analysis as a disciplined loop, not just debugging

How I reach safety and security:

- I try to carve out a core of behavior that I can state and prove.
- I try to prove that certain bad states are unreachable, so entire classes of failure are removed from the system’s behavior.
- When a tool gives me a counterexample, I do not treat it as “the tool being annoying.” I treat it as the fastest possible teacher.

My limits:

- I can only prove what I can state. If I did not model an attack surface, I did not prove anything about it.
- Proofs can create false comfort if the spec is wrong, incomplete, or disconnected from real deployment.
- Some properties are too expensive to verify, or are undecidable in the general case, so I must still use approximations and judgment.

### Zooming out: counterexample analysis, and what it gives you

“Counterexample analysis” is what you do after a tool hands you a witness that your claim is false.
It is the step where a counterexample becomes understanding instead of noise.

In formal terms, you had a universal claim like “for all reachable states, `P` holds”:

```
∀s. Reachable(s) → P(s)
```

and the tool gave you a witness:

```
Reachable(s*) ∧ ¬P(s*)
```

Counterexample analysis usually includes:

1. Validate the witness. Is it a real execution of the real system, or only of an abstract model?
2. Minimize it. Can we shrink the trace to the smallest, simplest failing case?
3. Classify the failure. Is it a real bug, a missing precondition, a wrong spec, or a spurious counterexample caused by an over-approximation?
4. Generalize the lesson. What new invariant, precondition, or abstraction refinement would rule out not just this witness, but the whole family of similar failures?
5. Turn it into an artifact. Add a regression test, a new proof obligation, a refined model, or a synthesis constraint.

What it gives you:

- Refutation: a clean reason to stop believing a universal claim as stated.
- Guidance: a concrete trace you can replay, inspect, and use to drive refinement.
- Knowledge you can carry forward: the witness often becomes a permanent test or a permanent refinement constraint.

### Mutation testing vs counterexample mining (from an experienced engineer)

After twenty years of shipping software, I separate two questions that beginners blend together: “did I test my code?” and “did I test my tests?”

Mutation testing is the second question. It deliberately introduces small, plausible defects into the implementation (mutants), then reruns the test suite. A surviving mutant is a counterexample to a comforting claim like “my tests would notice if this logic were wrong.” What you learn is mostly about your test suite and your test oracles. The suite has blind spots, or it asserts the wrong things, or it is too coupled to the current implementation to notice meaningful behavior changes.

Counterexample mining is the other direction. You write down a property you actually care about and a model of the system, then a solver or model checker searches for a witness trace that violates the property. A found trace is a counterexample to the universal claim “for all reachable behaviors, the bad thing never happens.” What you learn is mostly about the system and the claim. Either there is a real bug, or your specification is wrong, or your abstraction is too coarse and needs refinement.

In short: mutation testing attacks the adequacy of your observations; counterexample mining attacks the truth of your statement. Both are refuter factories, but they refute different kinds of confidence. When you use both, you get a nice loop: counterexamples tell you what to add, mutation testing tells you whether what you added can actually see.

<figure class="fp-figure">
  <p class="fp-figure-title">Two different “refuter factories”</p>
  {% include diagrams/mutation-vs-counterexample.svg %}
  <figcaption class="fp-figure-caption">
    Mutation testing searches for tests that fail to notice a bug. Counterexample mining searches for a trace that breaks a stated property.
  </figcaption>
</figure>

### Correct by construction: the idea and the theory behind it

“Correct by construction” is not a slogan that means “no bugs.” It is a specific development strategy:
you build the program together with a chain of reasoning that establishes the property as you go.

There are a few theoretical foundations that support this:

1. Refinement (stepwise development): start with a high level specification, then refine it into an implementation through small steps, where each step is proven to preserve the specification’s meaning. At the end, the code is correct because it is the result of meaning-preserving refinement steps.

2. Type theory and “making invalid states unrepresentable”: use types and interfaces so that certain bad configurations cannot even be expressed. If “this state cannot be constructed,” then “this state cannot be reached” follows, because the program never has a way to create it.

3. Constructive proofs and program extraction (Curry Howard): in constructive settings, a proof of “there exists a program with property `P`” can be treated as a recipe for building such a program. Proof assistants can sometimes extract executable code from proofs, or enforce that each program step corresponds to a proof step.

4. Proof-carrying code and certified compilation: the artifact you ship can include, or be linked to, a machine-checkable proof that it satisfies some policy, and the compilation pipeline can be verified so that proofs are not invalidated by the toolchain.

The central mental frame is this:
verification checks a finished artifact; correct by construction tries to prevent whole classes of artifacts from ever being built.

### Why proving “bad states are unreachable” makes software more predictable

When you model a program as a transition system, its behavior is the set of all execution traces it could produce.
Predictability, in the formal sense, means that this set is constrained.

A safety property can be framed as unreachability:

```
∀s. Reachable(s) → ¬Bad(s)
```

or equivalently:

```
¬∃s. Reachable(s) ∧ Bad(s)
```

If you can prove that, you have done something stronger than testing.
You have removed an entire region of behavior from the program’s possible futures.

Examples of “bad states” that teams often try to make unreachable:

- out of bounds array access
- use after free
- violating a protocol’s step ordering (for example, using a key before authentication)
- violating an invariant (for example, total balances do not match, or a token can be minted without authorization)

This increases predictability because it converts “this will probably not happen” into “this cannot happen, given the model and assumptions.”
It also makes downstream reasoning easier: other parts of the system can rely on the invariant as a stable fact.

There is an important boundary: proving unreachability is most naturally about safety properties. Liveness and performance are different shapes of claim, and they often need different tools and assumptions.

### Security is not just predictability and reliability

Reliable software is software that behaves consistently.
Predictable software is software whose behavior stays within known boundaries.

Secure software is software that continues to protect what must be protected even in the presence of an adversary.

<figure class="fp-figure">
  <p class="fp-figure-title">Security adds an adversary model</p>
  {% include diagrams/security-vs-reliability.svg %}
  <figcaption class="fp-figure-caption">
    Reliability is not the same as security. Security is about properties that remain true even when someone is actively trying to break them, under explicit assumptions about the attacker.
  </figcaption>
</figure>

Security usually includes, at minimum:

- confidentiality: secrets do not leak
- integrity: attackers cannot change what they should not be able to change
- availability: attackers cannot easily prevent the system from providing service
- authenticity and authorization: actions happen only when the right principals authorize them

This is why “predictable” is not enough.
A program can be perfectly predictable and still be predictably wrong, for example by reliably returning private data to anyone who asks.

Formal methods can contribute to security by proving precise security claims under an explicit threat model.
But the threat model matters. Side channels, supply chain compromises, and human operational failures can sit outside the proof boundary.

### What formal methods uniquely add (and what they do not)

Heuristics, testing, and audits can build strong practical confidence, but they fundamentally sample behavior.
They show you many traces and many attacks, but never all.

Formal methods, when successful, let you replace sampling with a universal statement:

- “For all inputs, for all interleavings, for all reachable states (under assumptions A), property P holds.”
- “There does not exist any execution trace that violates P.”

That is the kind of sentence a logician can say that a purely heuristic approach cannot justify.
It is not a mood or a level of confidence. It is a theorem about a model.

This does not mean formal methods makes you omniscient.
It means formal methods gives you a different kind of guarantee, with a different kind of failure mode.

- If your proof is correct but your model is missing reality, you get a true theorem about the wrong thing.
- If your model is faithful but the property is the wrong goal, you can prove the wrong goal very well.

The practical art is choosing the smallest set of claims that matter, making them formal, and then using counterexamples and refinement to close the gap between “what we meant” and “what we said.”

## Where this tutorial goes next

Next pages will make these pictures manipulable:

- write the deck model as a small transition system,
- express properties as logical statements,
- use tools to search for counterexamples,
- learn when two different descriptions are actually the same structure (isomorphism) versus a lossy abstraction,
- and use counterexamples to refine models and synthesize better ones.

If you want the next conceptual tool immediately, read
[Tutorial 2: Isomorphism]({{ '/tutorials/isomorphism/' | relative_url }}).
