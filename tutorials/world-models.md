---
title: World models and continuous learning (why constraints matter)
layout: docs
kicker: Tutorial 4
description: A world model is an internal theory of “what is out there and what would happen if…”. If the model learns online, formal constraints become the difference between adaptation and drift.
---

This tutorial is about a practical tension:

- A system that **learns** wants to change itself.
- A system that is **trusted** needs parts of itself to stay invariant.

“World models” sit in the middle. They are the internal objects that let an agent do more than react: simulate, plan, explain, and choose.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Mental pictures to keep</p>
  <ul>
    <li>A world model as an inner simulator: “if I do X, Y will happen”</li>
    <li>An invariant as a law: a statement that should survive all allowed changes</li>
    <li>Learning as search in parameter space; verification as search for counterexamples in state space</li>
    <li>Formal methods as guardrails for self-modifying systems</li>
  </ul>
</div>

## Part I: inside my head (a private simulator)

I walk into a room and reach for a mug.

I do not just predict the next pixel I will see. I implicitly assume a whole bundle of stable structure:

- the mug continues to exist even when I stop looking at it,
- it has a roughly rigid shape,
- it will resist my hand instead of passing through it,
- it will fall if I remove its support,
- if it is full, tilting it will likely spill.

Most of this is not conscious. But it is actionable. It lets me choose movements that work.

The key point is the difference between:

- **prediction**: “what will I see next?”
- **counterfactual simulation**: “what would happen if I did something else?”

The second is what makes a world model feel like a *model* rather than a *reflex*.

<figure class="fp-figure">
  <p class="fp-figure-title">A world model as an inner loop</p>
  {% include diagrams/world-model-loop.svg %}
  <figcaption class="fp-figure-caption">
    Observations update an internal state. The model predicts consequences. A planner chooses actions. The outer world provides new evidence. Constraints can sit “around” the model to keep behavior inside safe bounds.
  </figcaption>
</figure>

## Part II: how a child builds a world model (invariants before words)

A child does not start with equations. But they still learn something that behaves like invariants:

- **object permanence** (things persist),
- **contact and support** (objects do not usually interpenetrate; unsupported things fall),
- **cause and effect** (some actions reliably produce some outcomes),
- **agents and goals** (some moving things act as if they want something).

These are not “theorems” in the mathematical sense. But they function like a first internal physics: stable expectations that compress experience into something reusable.

Later, language makes these expectations shareable. A child can be told:

- “If it is fragile, don’t drop it.”
- “If the light is red, stop.”

That “if/then” structure is already logic-shaped. It is an early bridge from experience to rules.

## Part III: growing up means making the model explicit

Adults do something qualitatively different from purely statistical prediction: they externalize models.

- With **language**, people can store and transmit rules.
- With **math**, people can express structure that is too precise or too large to hold in memory.
- With **logic**, people can chain implications and track assumptions.
- With **tools** (pen and paper, computers, solvers), people can reason beyond working memory.

This is “thinking with external organs”: writing down state, writing down constraints, and letting the external system carry the load.

In that sense, formal reasoning is not an alien activity. It is the sharpened version of what people already do when a mental model needs to be reliable:
make it explicit, then check it.

## Part IV: zooming out (what “world model” means in a technical sense)

In one common formalization, an agent interacts with a system over time:

- a hidden **state** $s_t$,
- an **action** $a_t$ the agent chooses,
- an **observation** $o_t$ the agent receives.

A world model is the agent’s internal representation of the relevant structure:

- how states evolve (dynamics),
- how observations relate to hidden state (perception),
- what outcomes are valuable (reward/utility),
- and which things are impossible or forbidden (constraints).

Some models are learned (parameters fit to data). Some are hand-built (physics, rules). Most realistic systems mix both.

## Part V: continuous learning (the model changes at test time)

If a model only learns during training and is frozen at deployment, it can be audited more like ordinary software.

But a growing frontier is **continual learning**: the model keeps updating while it is being used.

One recent example is “Learning to Discover at Test Time”, which proposes doing reinforcement learning at test time so the model continues to train on experience specific to the *current* problem, with the goal of finding one excellent solution rather than optimizing average generalization. (See [arXiv:2601.16175](https://arxiv.org/abs/2601.16175).)

This kind of test-time adaptation is powerful, but it sharpens the trust problem:
the thing being relied on is also the thing being modified.

## Part VI: why internal world models want formal methods

The more an internal model is used for *action* (not just passive prediction), and the more it is allowed to *change online*, the more it needs rails.

Formal methods contribute three pieces that learning systems usually lack by default:

1. **A meaning function (semantics):** what does an internal representation *mean* in terms of behavior?
2. **A specification:** what must always be true (safety, liveness, noninterference, resource bounds)?
3. **A refuter:** a way to search for concrete counterexamples when the spec is wrong or the model drifts.

This is why code is a useful analogy. As Solar-Lezama notes in the introduction to program synthesis, code requires extreme precision, and the advantage of code is that its semantics let us test and reason about behavior. (See [Lecture 1](https://people.csail.mit.edu/asolar/SynthesisCourse/Lecture1.htm).)

If a world model is “code-like” (a structured representation that drives action), then the same logic applies:
precision, semantics, and checkability stop being nice-to-have and become the difference between *adaptation* and *drift*.

## Part VII: neuro-symbolic structure as an anti-drift move

One way to make a world model more checkable is to force parts of it into an explicit, executable structure.

The Vision-Language Programs (VLP) proposal is one example: use a vision-language model to produce structured descriptions, compile them into programs, and execute those programs under task constraints, so outputs remain consistent and explanations become inspectable. (See [arXiv:2511.18964](https://arxiv.org/abs/2511.18964).)

The lesson to extract is not “programs beat neural nets”.
It is that **structure creates places to attach constraints**.

Once there is an explicit intermediate representation, it becomes possible to say:

- “this rule must never be violated,”
- “this update may change only these entries,”
- “this action is allowed only if these invariants hold,”
- “if the constraint is violated, show the smallest counterexample trace.”

## Part VIII: a design pattern (learned model, formal rails)

For systems that learn online, a practical architecture is:

1. A learned component proposes beliefs, plans, or updates.
2. A small formal “kernel” checks them against invariants (and rejects or repairs).
3. The system logs traces so failures become debuggable counterexamples, not mysteries.

This is the same split as earlier tutorials:
let learning do search in a rich space, and let formal constraints define what counts as “out of bounds”.

## References

- Solar-Lezama, *Introduction to Program Synthesis (Lecture 1)*: https://people.csail.mit.edu/asolar/SynthesisCourse/Lecture1.htm
- Yuksekgonul et al., *Learning to Discover at Test Time* (arXiv:2601.16175): https://arxiv.org/abs/2601.16175
- Wüst et al., *Synthesizing Visual Concepts as Vision-Language Programs* (arXiv:2511.18964): https://arxiv.org/abs/2511.18964
