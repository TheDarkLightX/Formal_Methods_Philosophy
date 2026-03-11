---
title: "What reasoning is: proof, search, and justification"
layout: docs
kicker: Tutorial 13
description: A response to broad cognitive-science notions of reasoning, using a child example, Peano arithmetic, and proof by exhaustive search to separate discovery from justification.
---

This tutorial responds to a broad claim that has become common in AI discussions: if a system searches, recombines what it knows, adapts to context, and lands on good answers, then it reasons.

That claim is not obviously wrong. It is just incomplete.

In cognitive science, that broad notion of reasoning can be useful. It helps compare humans, animals, and machines without assuming they all have the same internal machinery. But mathematics asks a sharper question. It does not ask only whether a system got to the answer. It asks whether the path to the answer is licensed, public, and checkable.

This tutorial makes three scoped claims:

1. A correct answer is not yet a proof.
2. A chain of thought can record search, explanation, or storytelling, but it is not automatically a justification.
3. Brute force counts as proof only when the search is genuinely exhaustive and the checking rule is valid.

The goal is not to deny that models can solve problems. The goal is to separate three things that are constantly blurred together:

- finding an answer,
- explaining an answer,
- proving an answer.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Assumption hygiene (scope first)</p>
  <ul>
    <li><strong>Assumption A (two uses of "reasoning"):</strong> This page distinguishes a broad cognitive-science notion of reasoning from a stricter mathematical notion.</li>
    <li><strong>Assumption B (discovery vs. justification):</strong> How a conclusion was found can differ from why it is correct.</li>
    <li><strong>Assumption C (what a proof is):</strong> A proof is a finite, checkable object whose steps are licensed by rules, or a finite exhaustive search together with a valid checker.</li>
    <li><strong>Assumption D (system boundary):</strong> This page distinguishes a base model, a model with scratchwork, and a model-plus-checker system.</li>
  </ul>
</div>

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Keep these four things separate</p>
  <ul>
    <li><strong>Answer:</strong> the final claim, such as <code>1 + 1 = 2</code>.</li>
    <li><strong>Search trace:</strong> the path that happened to produce the answer.</li>
    <li><strong>Explanation:</strong> a human-readable story about why the answer makes sense.</li>
    <li><strong>Proof or certificate:</strong> a checkable object that establishes correctness.</li>
  </ul>
  <p>
    A system can have one of these without having the others. Most confusion around "LLMs reason" comes from treating them as interchangeable.
  </p>
</div>

<div class="fp-diagram">
  {% include diagrams/reasoning-search-proof.svg %}
</div>

## Part I: the child example (guessing is not yet reasoning)

Start with a simple case.

A child is asked:

$$
1 + 1 = \ ?
$$

Now imagine four different outcomes.

### Case 1: the child says 4

That is just wrong.

### Case 2: the child says 4, then 3, then 2

Now the child has reached the correct answer, but not by reasoning in the strong sense. This is trial and error with feedback. The child found the answer, but the answer is not yet justified.

### Case 3: the child says "one thing plus one thing makes two things"

This is better. There is at least a conceptual explanation. It may be informal, but it is not mere guessing.

### Case 4: the child checks every candidate in a finite list and shows only 2 works

Now we are much closer to proof. If the candidate space is truly finite and the checking rule is valid, then exhaustive search can count as a proof.

That is the first important distinction:

- getting the answer by luck is not reasoning,
- getting the answer by search may be reasoning in a weak sense,
- getting the answer together with a checkable justification is reasoning in the mathematical sense.

This is why "it arrived at the right output" is not enough. The same output can come from guessing, search, insight, imitation, or proof.

## Part II: `1 + 1 = 2` in Peano arithmetic

Peano arithmetic is useful here because it is very explicit. It does not accept "that seems right" as a reason.

We define:

- $1 := S(0)$
- $2 := S(S(0))$

and addition by recursion:

- $x + 0 = x$
- $x + S(y) = S(x + y)$

Now compute:

$$
\begin{aligned}
1 + 1
&= S(0) + S(0) \\
&= S(S(0) + 0) \\
&= S(S(0)) \\
&= 2
\end{aligned}
$$

Each line is licensed:

1. Replace $1$ by $S(0)$.
2. Apply the recursive definition $x + S(y) = S(x + y)$ with $x = S(0)$ and $y = 0$.
3. Apply the base case $x + 0 = x$.
4. Replace $S(S(0))$ by $2$.

That is not just "a chain of thought." It is a derivation.

The point matters because a natural-language scratchpad can look similar while doing something much weaker. A text trace can say "first add the ones, then simplify, then we get 2," but unless each step is tied to an allowed rule, the trace is commentary, not proof.

## Part III: when brute force becomes proof

Brute force is not automatically low-status. Sometimes it is a perfectly valid proof technique.

The key condition is finiteness.

In propositional logic, a truth table is proof by exhaustive search. To show that

$$
P \lor \neg P
$$

is always true, it is enough to check the two possible assignments:

| $P$ | $\neg P$ | $P \lor \neg P$ |
|---|---|---|
| T | F | T |
| F | T | T |

Every case has been covered, and the formula is true in every case. That is a proof.

This also clarifies the child example. If the child really checked all candidates in a finite search space with a valid rule, then yes, that is a proof by exhaustive search.

But Peano arithmetic talks about the natural numbers, which are infinite. That changes the game. One cannot prove a universal statement about all natural numbers by checking a few examples. Something stronger is needed.

That stronger move is often induction.

## Part IV: why induction is not the same as repeated guessing

Suppose the claim is:

$$
\forall n \in \mathbb{N}.\; n + 0 = n
$$

No finite list of examples proves that. One can check $0 + 0 = 0$, $1 + 0 = 1$, $2 + 0 = 2$, and still not have a proof of the universal claim.

Induction gives a finite proof object for an infinite domain:

1. Prove the base case.
2. Prove that if the claim holds for $k$, then it holds for $k + 1$.
3. Conclude it holds for all $n$.

This is a good place to see what mathematicians mean by reasoning. The proof does not mirror the psychological path by which someone first thought of the theorem. It compresses justification into a public object that others can check.

That is why mathematics cares so much about proof. It separates the flash of discovery from the obligation of justification.

## Part V: the cognitive-science view of reasoning

Now we can fairly state the broader view.

In cognitive science and comparative cognition, "reasoning" often means something like this:

- using stored information plus current input,
- searching over possibilities,
- recombining representations,
- narrowing uncertainty,
- reaching a conclusion or action.

On that definition, humans reason. Many animals reason. A system can reason even if it uses heuristics, shortcuts, and partial search rather than explicit formal proof at every step.

That is the sense used in Maggie Vale's essay, <em>LLMs Reason and I'm Tired of Pretending They Don't</em> (Vale, 2026). The essay argues that if one uses the same broad comparative-cognition criteria applied to other minds, then LLMs should count as reasoners at least in a functional sense. Search over stored representations, burst-then-snap dynamics, flexible recombination, and context-sensitive problem solving are treated as evidence.

There is a real point here. If the question is:

> Can a system flexibly search, recombine, adapt, and often solve problems?

then many modern models do seem to qualify in some degree.

The problem starts when that descriptive notion is quietly upgraded into a mathematical or epistemic one.

<div class="fp-diagram">
  {% include diagrams/reasoning-two-lenses.svg %}
</div>

The contrast is cleaner in visual form. Maggie's question is mainly behavioral: is the system doing something that looks like flexible problem-solving across contexts? The mathematical question is stricter: what has been produced that another agent can check without trusting the system's story about itself?

## Part VI: the mathematician's objection

The mathematician does not deny that search happens.

The mathematician asks:

- Which rule licenses this step?
- Is the derivation valid?
- Can someone else check it?
- If it is brute force, was the search genuinely exhaustive?
- If it is a proof, where is the proof object?

This is why "reasoning" in mathematics is stricter than "reasoning" in cognitive science.

A mathematician will happily grant that a person often discovers a proof by intuition, analogy, search, lucky guesses, or mental wandering. But none of those things is what makes the theorem accepted. The theorem is accepted when there is a proof.

This is the crucial split:

- **context of discovery:** how the result was found,
- **context of justification:** why the result is correct.

Chain-of-thought usually lives much closer to discovery than to justification.

## Part VII: why chain of thought is not automatically proof

A long answer is not the same as a valid derivation.

Chain-of-thought can be:

- useful scratchwork,
- a search trace,
- a teaching aid,
- a post hoc explanation,
- or plain confabulation.

The surface form does not tell us which one it is.

Return to the child:

- If the child guesses until landing on 2, the answer may be correct but accidental.
- If the child gives a story that sounds plausible, the story may still be wrong.
- If the child produces a derivation from rules, now there is a proof.

The same applies to language models.

A model may emit:

- the right answer,
- a fluent explanation,
- and even a step-by-step narrative.

But unless the steps are tied to a checker, or compiled into a formal certificate, the narrative is still untrusted.

This is why the phrase "the model reasoned" is often too loose. It can mean:

- the model searched effectively,
- the model produced a good-looking rationale,
- or the model produced a checkable proof.

Those are not the same achievement.

## Part VIII: SAT, witnesses, and the modern compromise

Formal methods already have a clean way to separate proposal from proof.

Take SAT. A model proposes a satisfying assignment $\alpha$ for a formula $F$.

That proposal is not yet the proof.

The proof-like object is the certificate:

- for SAT, a satisfying assignment that a verifier can check clause by clause,
- for UNSAT, often a proof trace such as a resolution certificate,
- for theorem proving, a proof term or derivation checked by a proof assistant.

This is the right hybrid picture:

1. Search can be heuristic.
2. Proposal can be messy.
3. Discovery can look like exploration.
4. Acceptance still requires a checker.

That is why "proof by exhaustive search" is a real thing, but "I kept sampling until I felt good about the answer" is not.

## Part IX: what this means for LLMs

The cleanest conclusion is not:

> LLMs never reason.

That is too blunt.

The cleaner conclusion is:

> LLMs may reason in the broad cognitive-science sense of flexible search and problem solving, but that does not by itself amount to reasoning in the mathematical sense of proof, justification, and certificate production.

Or even more sharply:

> Search is not proof.  
> Aha is not a certificate.  
> Chain of thought is not justification.

That is the main counterpoint to the broad blog-style argument.

If the question is about comparative cognition, the answer may be "yes, in some real but weak sense."

If the question is about mathematics, theorem proving, or formal methods, the standard is higher. There, reasoning earns its name only when the result is justified by a derivation, an invariant-preserving argument, or a checkable certificate.

That is the standard a child must eventually meet in arithmetic, a mathematician must meet in proof, and an AI system must meet in high-assurance work.

## References

- Cook, S. A. (1971) <em>The Complexity of Theorem-Proving Procedures</em>.
- Enderton, H. B. (2001) <em>A Mathematical Introduction to Logic</em>.
- Mendelson, E. (2015) <em>Introduction to Mathematical Logic</em>.
- Necula, G. C. (1997) <em>Proof-Carrying Code</em>.
- Vale, M. (2026) <em>LLMs Reason and I'm Tired of Pretending They Don't</em>.
