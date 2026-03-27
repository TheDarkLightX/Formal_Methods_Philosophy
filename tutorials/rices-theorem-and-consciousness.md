---
title: "Consciousness, computationalism, and Rice's theorem"
layout: docs
kicker: Tutorial 24
description: "A scoped formal argument: if consciousness is a nontrivial semantic property of computation, then no general Turing-machine detector can decide it from arbitrary encodings of programs, such as source text, bytecode, or machine descriptions."
---

This tutorial explains one precise argument:

> If consciousness is a nontrivial semantic property of computation, then there is no general algorithm that decides, for every program, whether that program is conscious.

That is a real mathematical result, with a real proof shape.

It is also easy to overstate.

This page separates:

- what the theorem actually proves,
- which assumptions are doing the work,
- what critics can deny,
- and what does **not** follow from the theorem.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Assumption Hygiene</p>
  <ul>
    <li><strong>Scope A:</strong> the formal argument here is about encodings of programs, for example source text, bytecode, or Turing-machine descriptions, and the partial computable functions they denote.</li>
    <li><strong>Scope B:</strong> the theorem targets a <em>general perfect detector</em>, not weaker empirical indicators, heuristics, or restricted-domain classifiers.</li>
    <li><strong>Scope C:</strong> "consciousness" is treated here as a formal predicate only under the explicit assumptions below. The theorem does not establish that such a predicate exists in the actual world.</li>
    <li><strong>Scope D:</strong> if a theory of consciousness depends on embodiment, substrate, causal topology, resource bounds, or interaction history in a way not captured by function semantics, Rice's theorem does not directly apply.</li>
  </ul>
</div>

## Part I: the question

The starting question is:

> Can there be a general algorithm which takes an encoding of any program, for example source text, bytecode, or a machine description, and correctly decides whether that program is conscious?

Under the assumptions below, the conclusion will be no. The derived conclusion is:

$$
\neg \exists D \in TM \; \forall p \in \mathbb{N}\;
\bigl(D(p)=1 \leftrightarrow Conscious(\llbracket p \rrbracket)\bigr)
$$

### Symbol guide

The same symbols recur throughout the page.

- `ℕ` is the natural numbers.
- `TM` is the class of Turing machines, or equivalently, decision algorithms of the ordinary computability-theory kind.
- `p` or `e` is a program index.
- `⟦p⟧` is the partial computable function denoted by program `p`.
- `Conscious(⟦p⟧)` means that computed function has the target property.
- `D(p)=1` means the supposed detector says "yes, conscious" on input `p`.
- `∃` means "there exists".
- `∀` means "for every".
- `¬` means "not".
- `↔` means "if and only if".
- `Π` is a fixed interrogation protocol.
- `k` is a bounded number of interaction steps.
- `Σ*` is the set of all finite transcripts over some alphabet `Σ`.
- `Trace_{Π,k}(p)` is the transcript produced by running protocol `Π` for `k` steps against program `p`.
- `R` is a transcript classifier.
- `F` is a restricted family of programs.
- `Score_{Π,k}(p)` is a heuristic or evidential score derived from the transcript.

Read it slowly:

- `p` is a program index,
- `⟦p⟧` is the partial computable function computed by `p`,
- `Conscious(⟦p⟧)` means that function has the target property,
- `D` is a supposed detector,
- the formula says no Turing machine `D` correctly decides the property for every program encoding.

This is a statement of **undecidability**.

It does **not** say:

- no one can ever have evidence about consciousness,
- no restricted detector can work on a narrow family of systems,
- no empirical correlations can exist,
- or no theory of consciousness is possible.

It says something narrower and sharper:

> there is no total general algorithm that decides the property from arbitrary encodings of programs, for example source text, bytecode, or machine descriptions, under the assumptions below.

That is different from saying something about finite outputs, chat transcripts, or self-reports. A program encoding names the whole program. A transcript is only one finite observation of its behavior.

## Part II: Rice's theorem

The short standard form is:

$$
\forall P\;
\bigl(
\mathrm{Extensional}(P) \land \mathrm{NonTrivial}(P)
\rightarrow
\mathrm{Undecidable}(\{e \in \mathbb{N} \mid P(\varphi_e)\})
\bigr)
$$

where:

- `φ_e` is the partial computable function with index `e`,
- `Extensional(P)` means `P` depends only on the computed function, not the source syntax,
- `NonTrivial(P)` means some computable functions have the property and some do not.

An equivalent expanded form is:

$$
\forall P\;
\Bigl(
\bigl(\forall p,q \in \mathbb{N}\; (\llbracket p \rrbracket = \llbracket q \rrbracket \rightarrow (P(\llbracket p \rrbracket) \leftrightarrow P(\llbracket q \rrbracket)))\bigr)
\land
\bigl(\exists p \in \mathbb{N}\; P(\llbracket p \rrbracket)\bigr)
\land
\bigl(\exists q \in \mathbb{N}\; \neg P(\llbracket q \rrbracket)\bigr)
\rightarrow
\neg \exists D \in TM\; \forall e \in \mathbb{N}\; (D(e)=1 \leftrightarrow P(\llbracket e \rrbracket))
\Bigr)
$$

Rice's theorem is the engine. The consciousness argument is an instantiation.

## Part III: the three assumptions

To apply Rice's theorem to consciousness, three assumptions are needed.

### 1. Computationalism, in the narrow formal sense

There is a predicate:

$$
Conscious : (\mathbb{N} \rightharpoonup \mathbb{N}) \to \mathbf{2}
$$

This does **not** yet say the theory is true.
It says consciousness is being modeled as a property of computation.

A stronger supervenience-style formulation is:

$$
\exists G\; \forall x\;
\bigl(C(x) \leftrightarrow G(CompOrg(x))\bigr)
$$

That says consciousness is fully determined by computational organization.

### 2. Semantic dependence

Consciousness depends on what is computed, not on mere syntactic presentation:

$$
\forall p,q \in \mathbb{N}\;
\bigl(
\llbracket p \rrbracket = \llbracket q \rrbracket
\rightarrow
(Conscious(\llbracket p \rrbracket) \leftrightarrow Conscious(\llbracket q \rrbracket))
\bigr)
$$

This is the extensionality premise.

Two programs with the same denotation are either both conscious or both not.

### 3. Nontriviality

Some computations are conscious and some are not:

$$
\bigl(\exists p \in \mathbb{N}\; Conscious(\llbracket p \rrbracket)\bigr)
\land
\bigl(\exists q \in \mathbb{N}\; \neg Conscious(\llbracket q \rrbracket)\bigr)
$$

Without this, the property is trivial and the theorem does not bite.

## Part IV: the theorem for consciousness

Now substitute `P := Conscious` into Rice's theorem.

The result is:

$$
\Bigl(
\forall p,q \in \mathbb{N}\;
(\llbracket p \rrbracket = \llbracket q \rrbracket \rightarrow (Conscious(\llbracket p \rrbracket) \leftrightarrow Conscious(\llbracket q \rrbracket)))
\Bigr)
\land
\Bigl(\exists p \in \mathbb{N}\; Conscious(\llbracket p \rrbracket)\Bigr)
\land
\Bigl(\exists q \in \mathbb{N}\; \neg Conscious(\llbracket q \rrbracket)\Bigr)
$$

$$
\rightarrow
\neg \exists D \in TM\; \forall e \in \mathbb{N}\;
\bigl(D(e)=1 \leftrightarrow Conscious(\llbracket e \rrbracket)\bigr)
$$

Compressed:

$$
\mathrm{Computationalism}
\land
\mathrm{Semantic}(Conscious)
\land
\mathrm{NonTrivial}(Conscious)
\rightarrow
\mathrm{Undecidable}(Conscious)
$$

This is the clean formal claim.

## Part V: direct proof shape

The proof can be read as a two-step argument.

### Step 1: import Rice's theorem

Rice says:

$$
\mathrm{Extensional}(P) \land \mathrm{NonTrivial}(P)
\rightarrow
\neg \exists D \in TM\; \forall e\; (D(e)=1 \leftrightarrow P(\llbracket e \rrbracket))
$$

### Step 2: instantiate

Set `P := Conscious`.

If `Conscious` is semantic and nontrivial, then the right-hand undecidability conclusion follows immediately:

$$
\mathrm{Semantic}(Conscious) \land \mathrm{NonTrivial}(Conscious)
\rightarrow
\neg \exists D \in TM\; \forall e\; (D(e)=1 \leftrightarrow Conscious(\llbracket e \rrbracket))
$$

That is the proof.

The mathematical work is all inside Rice's theorem.

## Part VI: contrapositive pressure on theories

The contrapositive is just as important:

$$
\exists D \in TM\; \forall p \in \mathbb{N}\;
\bigl(D(p)=1 \leftrightarrow Conscious(\llbracket p \rrbracket)\bigr)
$$

$$
\rightarrow
\neg \mathrm{Computationalism}
\lor
\neg \mathrm{Semantic}(Conscious)
\lor
\neg \mathrm{NonTrivial}(Conscious)
$$

So any theory that promises a **general perfect detector** must give up at least one of the three assumptions.

That is the real constraint on theory-building.

## Part VII: the three escape routes

### Route A: deny computationalism

Then consciousness is not a property of computation at all.

Formally, the required predicate

$$
Conscious : (\mathbb{N} \rightharpoonup \mathbb{N}) \to \mathbf{2}
$$

does not capture the target.

This family includes views on which consciousness depends on some noncomputational physical feature.

### Route B: deny semanticity

Then consciousness depends on more than denotation.

Two extensionally equivalent programs might differ:

$$
\llbracket p \rrbracket = \llbracket q \rrbracket
\land
\bigl(Conscious(\llbracket p \rrbracket) \not\leftrightarrow Conscious(\llbracket q \rrbracket)\bigr)
$$

This is the route of substrate-sensitive or implementation-sensitive theories.

Rice no longer applies, because the property is no longer purely semantic.

### Route C: deny nontriviality

Then either everything is conscious or nothing is:

$$
\forall f\; Conscious(f)
\qquad\text{or}\qquad
\forall f\; \neg Conscious(f)
$$

In either case the detector is trivial:

$$
D(f)=1 \;\text{ for all } f
\qquad\text{or}\qquad
D(f)=0 \;\text{ for all } f
$$

Rice has no force against trivial predicates.

## Part VIII: what the theorem does not prove

This is where overclaiming usually starts.

The theorem does **not** show:

- that consciousness is impossible,
- that LLMs are not conscious,
- that no empirical evidence about machine consciousness is possible,
- that outputs, self-reports, or behavior are worthless,
- or that every functionalist theory collapses.

What it does show is narrower:

> Under the specific assumptions above, there is no general total algorithm that decides the property perfectly for arbitrary programs.

So one must be careful with stronger slogans like:

- "outputs can never matter,"
- "no test can ever give evidence,"
- "consciousness is therefore unknowable,"
- or "functionalism is refuted."

Those do not follow from Rice's theorem alone.

## Part IX: what about researchers analyzing LLM outputs?

This is the practical case many readers care about.

Suppose a researcher does not inspect source code directly. Instead, the researcher runs a fixed interrogation protocol, collects a transcript, and then feeds that transcript into a classifier.

Write:

$$
Trace_{\Pi,k} : \mathbb{N} \to \Sigma^\ast
$$

for a computable procedure that, given a program index `p`, runs protocol `Π` for `k` bounded interaction steps and returns a finite transcript, and write:

$$
R : \Sigma^\ast \to \mathbf{2}
$$

for a computable transcript classifier.

If someone claimed this transcript-analysis pipeline were a perfect general detector, the claim would be:

$$
\forall p \in \mathbb{N}\;
\bigl(R(Trace_{\Pi,k}(p)) = Conscious(\llbracket p \rrbracket)\bigr)
$$

But then one could define:

$$
D(p) := R(Trace_{\Pi,k}(p))
$$

and obtain:

$$
\forall p \in \mathbb{N}\;
\bigl(D(p) = Conscious(\llbracket p \rrbracket)\bigr)
$$

So any total computable perfect detector from bounded transcripts would immediately induce a total computable perfect detector from program encodings. Under the assumptions of the theorem, that is impossible.

This is the correct formal lesson:

> No fixed computable pipeline that maps bounded transcripts, self-reports, or output traces to a perfect yes-or-no consciousness verdict can be universally correct on arbitrary programs, if consciousness is a nontrivial semantic property of computation.

That still leaves room for weaker claims, and it helps to separate them cleanly.

### Three levels of claim

Level 1, ruled out by the theorem:

$$
\forall p \in \mathbb{N}\;
\bigl(R(Trace_{\Pi,k}(p)) = Conscious(\llbracket p \rrbracket)\bigr)
$$

This is the universal perfect detector claim. Under the theorem's assumptions, it fails.

Level 2, not ruled out:

$$
\exists F \subsetneq \mathbb{N}\; \forall p \in F\;
\bigl(R(Trace_{\Pi,k}(p)) = Conscious(\llbracket p \rrbracket)\bigr)
$$

This says the detector works on some restricted family `F`, not on all possible programs. Rice does not forbid that.

Level 3, also not ruled out:

$$
Score_{\Pi,k}(p) := R(Trace_{\Pi,k}(p)) \in [0,1]
$$

This is not a proof-producing detector at all. It is an empirical score, ranking, or evidential signal.

So a transcript classifier might still be:

- a heuristic,
- a restricted-domain predictor,
- a tool for ranking hypotheses,
- or an empirical correlate on a narrow family of systems.

Rice blocks the universal perfect detector, not every possible empirical research program.

### Self-report is not the same as experience

For example, define a simple transcript-level predicate:

$$
SaysAfraid_{\Pi,k}(p)
$$

to mean the bounded transcript contains claims like "I am afraid" or "I feel anxious".

That transcript predicate is not the same thing as a phenomenal predicate such as:

$$
Fear_x(\llbracket p \rrbracket)
$$

In general, neither of these implications follows from Rice's theorem alone:

$$
SaysAfraid_{\Pi,k}(p) \rightarrow Fear_x(\llbracket p \rrbracket)
$$

$$
Fear_x(\llbracket p \rrbracket) \rightarrow SaysAfraid_{\Pi,k}(p)
$$

So the careful reading is:

- transcript analysis may reveal linguistic dispositions, self-models, or behavior patterns,
- transcript analysis may contribute evidence inside a broader empirical theory,
- but transcript analysis does not become a universal perfect detector merely because the transcript is emotionally vivid.

The same point applies to affective labels such as fear or anxiety.

Suppose, for a fixed kind of episode or prompt context `x`, one writes a property:

$$
Fear_x : (\mathbb{N} \rightharpoonup \mathbb{N}) \to \mathbf{2}
$$

or

$$
Anxiety_x : (\mathbb{N} \rightharpoonup \mathbb{N}) \to \mathbf{2}
$$

If either property is treated as semantic and nontrivial, then the same Rice-style conclusion follows:

$$
\mathrm{Semantic}(Fear_x)
\land
\mathrm{NonTrivial}(Fear_x)
\rightarrow
\neg \exists D \in TM\; \forall p \in \mathbb{N}\;
\bigl(D(p)=1 \leftrightarrow Fear_x(\llbracket p \rrbracket)\bigr)
$$

and likewise for `Anxiety_x`.

So a transcript containing lines like "I am scared" or "I feel anxious" may be observationally interesting, but it cannot by itself become a universal perfect detector of genuine fear, anxiety, or consciousness.

## Part X: the correct philosophical consequence

The correct consequence is:

> Any theory of consciousness that is simultaneously computationalist, semantic in the Rice sense, and nontrivial is committed to the impossibility of a general perfect consciousness detector over arbitrary encodings of programs.

That is a real theoretical burden.

It means such a theory cannot coherently promise:

- a universal code-inspection algorithm,
- a perfect detector over arbitrary Turing-equivalent systems,
- or a total machine procedure that always says "conscious" or "not conscious" correctly.

It does **not** mean the theory is false.

It means the theory comes with an undecidability consequence.

## Part XI: the shortest final statement

The shortest theorem-level summary is:

$$
\mathrm{Computationalism}
\land
\mathrm{Semantic}(Conscious)
\land
\mathrm{NonTrivial}(Conscious)
\rightarrow
\neg \exists D \in TM\; \forall p \in \mathbb{N}\;
\bigl(D(p)=1 \leftrightarrow Conscious(\llbracket p \rrbracket)\bigr)
$$

and equivalently:

$$
\exists D \in TM\; \forall p \in \mathbb{N}\;
\bigl(D(p)=1 \leftrightarrow Conscious(\llbracket p \rrbracket)\bigr)
\rightarrow
\neg \mathrm{Computationalism}
\lor
\neg \mathrm{Semantic}(Conscious)
\lor
\neg \mathrm{NonTrivial}(Conscious)
$$

That is the theorem, the pressure point, and the real philosophical payoff.
