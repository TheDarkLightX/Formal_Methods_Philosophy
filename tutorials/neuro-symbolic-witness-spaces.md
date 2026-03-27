---
title: "Neuro-symbolic reasoning and witness spaces"
layout: docs
kicker: Tutorial 20
description: LLMs search the existential side of hard problems by proposing witnesses, designs, tests, and repairs. Symbolic methods enforce the universal side by checking what survives for all relevant cases.
---

This tutorial is about the cleanest way to think about pairing a language model with symbolic methods:

- the model proposes,
- the symbolic system checks,
- the combined system searches a witness space under semantic constraints.

That is the heart of neuro-symbolic reasoning.

The working slogans are:

> LLMs are priors over candidate structure. Symbolic methods are truth filters over semantics.

and:

> Creativity belongs on the existential side. Trust belongs on the universal side.

This page makes that precise in formulas, pushes it as deep as it will go, and marks where it stops.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Assumption hygiene</p>
  <ul>
    <li><strong>Assumption A (symbolic scope):</strong> "symbolic methods" here includes proof checkers, theorem provers, SAT and SMT solvers, type systems, model checkers, abstract interpreters, and explicit runtime or trace checkers.</li>
    <li><strong>Assumption B (LLM scope):</strong> the model is treated as a generator of candidate objects, proof sketches, test scenarios, abstractions, or repairs. It is not assumed to be sound by itself.</li>
    <li><strong>Assumption C (guarantee scope):</strong> any final guarantee comes from the checker, the solver, the proof assistant, or a proved coverage argument, not from surface fluency.</li>
    <li><strong>Assumption D (Tutorial 19 connection):</strong> the neuro-symbolic pair is a specific instance of the master schema <code>NoBadWitness(X, U, B)</code> from Tutorial 19. The LLM controls how <code>U</code> is populated. The checker defines <code>B</code>.</li>
  </ul>
</div>

## Part I: one picture, one formula

Suppose a model is given a task $x$. It proposes a candidate object $y$: a proof, a program, a test case, a temporal logic formula, an invariant, an abstraction, a patch, a fault scenario.

Let the model's proposal distribution be:

$$
q_N(y \mid x).
$$

Let the symbolic system define the semantic admissibility predicate:

$$
\chi_S(y,x) =
\begin{cases}
1 & \text{if } y \text{ is accepted by the checker for } x, \\
0 & \text{otherwise.}
\end{cases}
$$

Then the combined neuro-symbolic distribution is:

$$
q_{NS}(y \mid x)
\propto
q_N(y \mid x)\cdot \chi_S(y,x).
$$

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Notation guide</p>
  <ul>
    <li>$x$ — the task or problem instance</li>
    <li>$y$ — a candidate object proposed for that task</li>
    <li>$N$ labels the neural proposer (the LLM); $S$ labels the symbolic checker</li>
    <li>$q_N(y \mid x)$ — the model's proposal distribution over candidates $y$ given task $x$</li>
    <li>$\chi_S(y, x)$ — admissibility gate: $1$ if the checker accepts, $0$ if it rejects</li>
    <li>$q_{NS}(y \mid x)$ — the combined neuro-symbolic distribution</li>
    <li>$\mid$ means "conditioned on"; $\propto$ means "proportional to"</li>
  </ul>
  <p>Throughout this tutorial: $w$ names a witness, $c$ a counterexample, $d$ a design, $a$ an adversary move, $u$ a generic candidate, $\theta$ a parameter vector. The symbols $\forall$, $\exists$, $\neg$, $\land$, and $\to$ mean "for all," "there exists," "not," "and," and "implies."</p>
</div>

That equation says three things at once:

- the model provides search pressure (it concentrates probability on regions it considers promising),
- the symbolic method provides semantic filtering (it zeroes out everything outside the admissible region),
- the pair searches the admissible region rather than the full raw proposal space.

This already explains why the pair is stronger than either part alone. The model without the checker can propose fluent nonsense. The checker without the model must enumerate blindly. Together, the search is both focused and honest.

<figure class="fp-figure">
  <p class="fp-figure-title">The neuro-symbolic funnel: proposal mass meets admissibility</p>
  {% include diagrams/neuro-symbolic-funnel.svg %}
  <figcaption class="fp-figure-caption">
    The LLM concentrates probability on promising candidates (teal). The checker defines the admissible region (amber boundary). The neuro-symbolic distribution lives in the overlap: proposed with high probability <em>and</em> semantically valid.
  </figcaption>
</figure>

Tutorial 19 derived a master schema for all adversarial reasoning:

$$
\mathrm{NoBadWitness}(X,U,B)
\iff
\neg \exists u\; (U(u,X) \land B(u,X)).
$$

The neuro-symbolic pair is a direct instantiation. The LLM populates $U$ by choosing which witnesses to propose. The checker defines $B$ by deciding which proposals are semantically invalid. The combined system searches for witnesses that survive both: proposed by the model, accepted by the checker.

## Part I.5: existential engines and universal verifiers

The shortest high-leverage reading is this:

$$
\text{LLM} = \exists\text{-engine}
\qquad
\text{formal tool} = \forall\text{-verifier}
$$

Many useful tasks have one of these shapes:

$$
\exists x\; \mathrm{Witness}(x)
$$

$$
\neg \exists c\; \mathrm{Counterexample}(c)
$$

$$
\exists x\; \forall y\; \mathrm{Spec}(x,y)
$$

The first is pure existential search. The second is universal correctness phrased as absence of a counterexample. The third is the mixed design shape that matters most in engineering.

Read

$$
\exists x\; \forall y\; \mathrm{Spec}(x,y)
$$

as:

- there exists a candidate design, proof, program, invariant, policy, or parameter vector `x`,
- such that for every relevant case, attack, input, execution, or environment move `y`,
- the specification still holds.

This is where the division of labor becomes especially valuable:

- the LLM searches for `x`,
- the formal tool checks the `∀y` side,
- if the check fails, it returns a witness `y` that drives the next refinement.

So the practical loop is:

$$
\text{propose } x
\;\to\;
\text{check } \forall y\; \mathrm{Spec}(x,y)
\;\to\;
\text{get counterexample } y
\;\to\;
\text{refine } x
$$

That is the deepest operational meaning of "neuro-symbolic" in this tutorial. The model is strongest on the existential side, where search, reformulation, and creativity matter. The symbolic side is strongest on the universal side, where trust must survive adversarial and edge-case pressure.

## Part I.75: a worked example

Make it concrete. Consider a small satisfiability problem:

$$
\Phi = (A \lor B) \land (\neg A \lor C) \land (\neg B \lor \neg C).
$$

The task is to find a satisfying assignment. Here $\Phi$ is the formula, $A$, $B$, $C$ are Boolean variables, $\lor$ is "or," $\land$ is "and," $\neg$ is "not," $\top$ is true, $\bot$ is false, $\checkmark$ marks a satisfied clause, and $\times$ marks a failed one.

The LLM proposes: $A = \top,\; B = \bot,\; C = \top$.

The checker evaluates each clause:

$$
\begin{aligned}
A \lor B &= \top \lor \bot = \top \quad \checkmark \\
\neg A \lor C &= \bot \lor \top = \top \quad \checkmark \\
\neg B \lor \neg C &= \top \lor \bot = \top \quad \checkmark
\end{aligned}
$$

All clauses satisfied. The checker accepts. The combined system has found a witness.

Now suppose the LLM proposes instead: $A = \top,\; B = \top,\; C = \top$.

$$
\begin{aligned}
A \lor B &= \top \quad \checkmark \\
\neg A \lor C &= \top \quad \checkmark \\
\neg B \lor \neg C &= \bot \lor \bot = \bot \quad \times
\end{aligned}
$$

The third clause fails. The checker rejects. It does not matter how confidently the model proposed this assignment, or how plausible it looked. The clause is false.

That is the neuro-symbolic contract in miniature. The model's job is to make promising guesses. The checker's job is to be incorruptible.

## Part II: why the pair can be sound

Suppose the checker is sound:

$$
\forall x \forall y\;
\big(
\mathrm{Check}_S(y,x) \rightarrow \mathrm{Valid}(y,x)
\big).
$$

Define neuro-symbolic acceptance by:

$$
\mathrm{Accepted}_{NS}(y,x)
\iff
\mathrm{Proposed}_N(y,x)
\land
\mathrm{Check}_S(y,x).
$$

Then:

$$
\forall x \forall y\;
\big(
\mathrm{Accepted}_{NS}(y,x) \rightarrow \mathrm{Valid}(y,x)
\big).
$$

This is the soundness guarantee. It means an unsound generator can still participate in a sound overall pipeline, provided the acceptance gate is sound.

That is the central engineering reason to combine models with symbolic tools. The model does not need to be trustworthy. It only needs to be useful as a search heuristic. The trust comes from the checker.

## Part II.5: what the LLM provably cannot be

The soundness guarantee rests entirely on the checker. That is not an accident. It reflects a hard boundary.

Soundness requires a universal guarantee:

$$
\forall y\; \big(\mathrm{Check}(y,x) \to \mathrm{Valid}(y,x)\big).
$$

That quantifier ranges over every possible input, including inputs never seen during training.

Statistical learning provides a different kind of guarantee:

$$
\Pr_{y \sim \mathcal{D}}\big[\mathrm{Check}(y,x) \to \mathrm{Valid}(y,x)\big] \ge 1 - \delta.
$$

The gap between "for all $y$" and "with high probability over $y \sim \mathcal{D}$" is exactly the gap between proof and corroboration from Tutorial 19. An LLM can approximate a checker with high accuracy. But accuracy is not soundness. A single adversarial or out-of-distribution input can violate the guarantee.

So the sharp result is:

> No LLM, by itself, can serve as a sound checker. Sound checking requires logical verification, not pattern matching. That is why the architecture separates proposal from verification.

This separation is not a temporary limitation that better training will fix. It is a consequence of what statistical learning can and cannot guarantee. The checker must be a symbolic system because soundness is a logical property, not a statistical one.

## Part III: existential witness tasks

Many tasks have the form:

$$
\mathrm{Goal}_{\exists}(x)
\iff
\exists w\; \mathrm{Witness}(w,x).
$$

The neuro-symbolic pattern is:

$$
\exists w\;
\big(
\mathrm{Proposed}_N(w,x)
\land
\mathrm{Check}_S(w,x)
\big).
$$

Four representative instantiations make the pattern concrete.

Proof production:

$$
\mathrm{Proved}(\varphi)
\iff
\exists \pi\;
\big(
\mathrm{ProposedProof}_N(\pi,\varphi)
\land
\mathrm{ProofCheck}(\pi,\varphi)
\big).
$$

Program synthesis:

$$
\mathrm{Synthesized}(p,\mathrm{Spec})
\iff
\mathrm{ProposedProgram}_N(p,\mathrm{Spec})
\land
\mathrm{Verify}(p,\mathrm{Spec}).
$$

Invariant discovery:

$$
\exists I\;
\big(
\mathrm{ProposedInv}_N(I,M)
\land
\mathrm{Init}(M) \rightarrow I
\land
I \land \mathrm{Step}(M) \rightarrow I'
\land
I \rightarrow \mathrm{Safe}
\big).
$$

Abstraction discovery:

$$
\begin{aligned}
\exists \alpha\;\big(\;&\forall s,t\; (\mathrm{Step}_c(s,t) \to \mathrm{Step}_a(\alpha(s),\alpha(t))) \\
&\land\; \forall s\; (\mathrm{Bad}_c(s) \to \mathrm{Bad}_a(\alpha(s)))
\big).
\end{aligned}
$$

The first large possibility frontier follows:

> If a task can be expressed as "there exists a checkable witness," LLMs can search for that witness and symbolic methods can certify it.

## Part IV: universal refutation tasks

The dual frontier has the refutation shape:

$$
\mathrm{Goal}_{\forall}(x)
\iff
\neg \exists c\; \mathrm{Counterexample}(c,x).
$$

Here the model attacks rather than constructs. The neuro-symbolic pattern becomes:

$$
\exists c\;
\big(
\mathrm{Generated}_N(c,x)
\land
\mathrm{ValidCounterexample}_S(c,x)
\big)
\rightarrow
\neg \mathrm{ClaimHolds}(x).
$$

Counterexample mining:

$$
\exists c\;
\big(
\mathrm{Generated}_N(c,\mathrm{Spec})
\land
\mathrm{Counterexample}_S(c,\mathrm{Spec})
\big)
\rightarrow
\neg \mathrm{SpecHolds}.
$$

Model checking with AI-guided trace search:

$$
\exists \tau\;
\big(
\mathrm{GeneratedTrace}_N(\tau,M)
\land
\mathrm{Violates}(\tau,\varphi)
\big)
\rightarrow
\neg (M \models \varphi).
$$

Chaos engineering:

$$
\exists f \exists s\;
\big(
\mathrm{GeneratedFault}_N(f,M)
\land
\mathrm{Reachable}(s,M \oplus f)
\land
\mathrm{Disaster}(s)
\big)
\rightarrow
\neg \mathrm{Robust}(M).
$$

Finding no counterexample is weaker than a full proof unless there is a coverage argument. But one confirmed hit is decisive: a single valid counterexample refutes the claim outright.

That asymmetry — between the difficulty of confirming safety and the ease of refuting it — is why adversarial search is so valuable. The model does not need to be exhaustive. It only needs to find one witness.

## Part V: synthesis and game-shaped tasks

Synthesis pushes one quantifier level deeper than refutation. The task is no longer "find a witness" or "find a counterexample." It is:

$$
\exists d\; \forall a\; \neg \exists u\; \mathrm{Bad}(u,d,a,x).
$$

Read it as: there exists a design such that for every allowed attack, no bad outcome is reachable.

This is the shape behind controller synthesis, protocol design, mechanism design, fail-closed API design, guard design, robust scheduling, and secure configuration selection.

The LLM can help by proposing candidate designs, invariants, decompositions, ranking functions, or proof strategies. The symbolic side checks the quantified claim: does the proposed design survive all allowed attacks?

<figure class="fp-figure">
  <p class="fp-figure-title">Three frontiers: each level adds one alternating quantifier</p>
  {% include diagrams/three-frontiers.svg %}
  <figcaption class="fp-figure-caption">
    Existential search has one quantifier. Refutation adds universal checking. Synthesis nests all three into a game between designer, adversary, and outcome. Each level is harder, and each is still amenable to the neuro-symbolic split.
  </figcaption>
</figure>

The three frontiers now form a clean hierarchy:

$$
\begin{aligned}
\text{Existential:} \quad & \exists w\; \mathrm{Witness}(w,x) \\
\text{Refutation:} \quad & \neg \exists c\; \mathrm{Counterexample}(c,x) \\
\text{Synthesis:} \quad & \exists d\; \forall a\; \neg \exists u\; \mathrm{Bad}(u,d,a,x)
\end{aligned}
$$

Each level adds one alternating quantifier. Each level is harder. Each level is still amenable to the neuro-symbolic split: the model searches, the checker decides.

## Part VI: the counterexample-guided refinement loop

The most important practical neuro-symbolic pattern is not a single propose-check step. It is an iterated loop where the checker's feedback guides the next proposal.

Let $x_0$ be the model's initial candidate:

$$
x_0 \in \mathrm{InitialProposal}_N(x).
$$

If the checker rejects, it returns a counterexample:

$$
c_t = \mathrm{Counterexample}_S(x_t).
$$

The model refines using the counterexample:

$$
x_{t+1} = \mathrm{Refine}_N(x_t, c_t).
$$

The loop terminates when the checker accepts:

$$
\exists T\; \chi_S(x_T, x) = 1.
$$

This is the counterexample-guided refinement loop. It appears under many names: CEGAR in model checking, counterexample-guided inductive synthesis in program synthesis, adversarial training in machine learning. The underlying shape is always the same.

The key convergence question is whether the refinement operator makes progress. Define a measure $\mu(x_t)$ of how far the current proposal is from the admissible region. Convergence is guaranteed if:

$$
\mu(x_{t+1}) < \mu(x_t) \quad \text{whenever } \chi_S(x_t, x) = 0.
$$

That is, each refinement step strictly reduces the distance to admissibility.

Without monotone progress, the loop can oscillate: the model fixes one problem but reintroduces another. This is not a theoretical curiosity. It is the main failure mode of iterative neuro-symbolic systems in practice.

The deeper insight is that the counterexample is not just a rejection signal. It is structured diagnostic information. A good checker does not merely say "no." It says "no, and here is why," in a form that the model can use to propose something better. The richer the diagnostic, the more directed the refinement.

## Part VII: experiment design and witness-space reduction

An intelligent system does not only answer questions. It chooses what to test next.

Let $U_t$ be the current live witness space. After action $a$ and observation $o$:

$$
U_{t+1}(a,o)
=
\{u \in U_t \mid \mathrm{Survives}(u,a,o)\}.
$$

The ideal next action most shrinks uncertainty:

$$
a^*
\in
\arg\max_a \mathbb{E}_o
\big[
|U_t| - |U_{t+1}(a,o)|
\big]
$$

subject to:

$$
\mathrm{Safe}(a).
$$

LLMs are unusually useful here. Proposing good experiments, attacker moves, chaos scenarios, or counterfactuals requires the same pattern-matching skill that makes LLMs effective proposers. The symbolic side then checks feasibility, safety, and consequence.

So the pair is not only a theorem machine. It can be an experiment design machine: the model chooses where to look, the checker determines what the looking reveals.

## Part VIII: coverage, the real bottleneck

The main obstacle is not proposal quality alone. It is coverage.

Define generator coverage over a witness family $W$:

$$
\mathrm{Coverage}_N(W,x)
\iff
\forall w\;
\big(
W(w,x) \rightarrow \Pr_N(w \mid x) > 0
\big).
$$

This says every relevant witness has nonzero probability of being proposed.

If the generator has coverage and the checker is sound, then repeated sampling succeeds in the limit:

$$
\exists w\;
\big(
W(w,x)\land \mathrm{Valid}(w,x)\land \Pr_N(w \mid x)\ge \varepsilon > 0
\big)
$$

implies

$$
\lim_{n\to\infty}
\Pr(\text{found a valid witness by trial } n)
= 1.
$$

That is asymptotic discovery, not formal completeness.

The relationship between soundness and coverage determines what the system can claim:

$$
\begin{aligned}
\text{Sound checker} + \text{full coverage} &\to \text{proof (in the limit)} \\
\text{Sound checker} + \text{partial coverage} &\to \text{honest corroboration} \\
\text{Unsound checker} + \text{full coverage} &\to \text{dangerous (false negatives pass)} \\
\text{Unsound checker} + \text{partial coverage} &\to \text{unreliable}
\end{aligned}
$$

<figure class="fp-figure">
  <p class="fp-figure-title">Soundness &times; coverage: where assurance lives</p>
  {% include diagrams/soundness-coverage-quadrant.svg %}
  <figcaption class="fp-figure-caption">
    Only the top-left quadrant reaches proof-level assurance. The top-right is the honest practical position: the search was sound but might have missed something. The bottom row is where trust breaks down.
  </figcaption>
</figure>

Only the first row reaches proof-level assurance. The second is the honest practical position: the search was sound but might have missed something. Tutorial 19 called this the difference between proof and corroboration. Here it reappears as the difference between full coverage and partial coverage.

<div class="fp-callout fp-callout-try">
  <p class="fp-callout-title">Hands-on exploration</p>
  <p>
    The interactive explorer below lets you see these ideas in action. Adjust the LLM's
    temperature to spread or concentrate its proposal mass. Toggle a coverage gap to see
    what happens when valid witnesses live in the model's blind spot. Switch between task
    types (proof search, counterexample mining, synthesis) and watch how the witness space
    and checker boundary change.
  </p>
</div>

<figure class="fp-figure">
  <p class="fp-figure-title">Interactive: witness space explorer</p>
  <iframe
    src="{{ '/witness_space_explorer.html' | relative_url }}"
    title="Interactive witness space explorer"
    data-fp-resize="true"
    data-fp-min-height="920"
    style="width: 100%; min-height: 920px; border: 0; border-radius: 16px; background: transparent;"
    loading="lazy"></iframe>
  <figcaption class="fp-figure-caption">
    Sample from the LLM's proposal distribution, watch the checker accept or reject, and
    see how coverage gaps prevent discovery of valid witnesses. The statistics panel tracks
    proposals, acceptances, and coverage.
  </figcaption>
</figure>

## Part IX: what LLMs are especially good at

The cleanest characterization of the LLM's role is:

$$
\text{LLM} = \text{amortized prior over useful symbolic candidates}.
$$

The symbolic system provides:

$$
\text{checker} = \text{semantic truth condition}.
$$

That pair explains why the combination beats brute-force symbolic search in practice. The LLM has absorbed patterns from an enormous training corpus: likely proof shapes, likely invariants, likely failure modes, likely useful reformulations. It concentrates search pressure where witnesses are most likely to live, even though it cannot verify what it finds.

There is a clean complexity-theoretic reading. An NP problem is one where a candidate witness can be verified in polynomial time. The LLM acts as a non-deterministic guesser: it proposes witnesses without exhaustive enumeration. The checker acts as the polynomial-time verifier. So the neuro-symbolic pair is essentially:

$$
\begin{aligned}
\text{LLM} &= \text{NP oracle (guess the certificate)}, \\
\text{checker} &= \text{P verifier (verify it)}.
\end{aligned}
$$

This is why the pattern fits NP-like search tasks naturally. If verification is cheap and the search space is huge but structured, the LLM's pattern-matching prior is exactly the kind of heuristic that concentrates search on promising candidates.

That is the practical reason the pair is stronger than brute-force symbolic search, even when the final truth still comes from the symbolic side.

## Part X: adversarial robustness of the pipeline

Suppose the LLM is corrupted: adversarial prompt injection, poisoned training data, or simply a bad day. What breaks?

The answer is clean. Corruption can degrade *coverage* but cannot break *soundness*:

$$
\mathrm{Sound}(\mathrm{Check}_S)
\land
\mathrm{Corrupted}(q_N)
\to
\mathrm{Sound}(\mathrm{Pipeline}_{NS}).
$$

A corrupted model might stop proposing valid witnesses (coverage drops to zero). It might flood the checker with garbage (efficiency drops). But it cannot force the checker to accept an invalid witness. The checker is the trust anchor.

Compare this with an end-to-end neural system where the same model both proposes and evaluates. If that model is corrupted, the evaluation is corrupted too. There is no independent verification layer.

The architecture's separation between proposal and verification is not just a design pattern. It is a security boundary. The model is untrusted. The checker is trusted. The pipeline inherits the checker's soundness regardless of what the model does.

This is the same principle that makes proof assistants useful: the kernel is small and trusted, and the proof-search heuristics outside the kernel can be arbitrarily complex without compromising the kernel's soundness.

## Part XI: composition of neuro-symbolic pairs

Real systems compose multiple proposer-checker stages. If two stages are available:

$$
\begin{aligned}
\text{Stage 1: } &(q_{N_1}, \chi_{S_1}) \\
\text{Stage 2: } &(q_{N_2}, \chi_{S_2})
\end{aligned}
$$

the composed checker is:

$$
\chi_{S_1 \land S_2}(y,x) = \chi_{S_1}(y,x) \cdot \chi_{S_2}(y,x).
$$

Soundness composes:

$$
\mathrm{Sound}(\chi_{S_1}) \land \mathrm{Sound}(\chi_{S_2})
\to
\mathrm{Sound}(\chi_{S_1} \land \chi_{S_2}).
$$

The composed checker is strictly tighter than either alone: anything that passes both is valid under both criteria. The space of checkers forms a lattice under conjunction and disjunction.

This connects to Tutorial 14's microkernel principle. Small, independently verified checkers compose into a verified pipeline. Each checker can be simple, auditable, and proved correct. The composition inherits soundness from the parts.

Practically, this means a neuro-symbolic system can layer a type checker, a property-based test suite, a model checker, and a runtime monitor into a single acceptance gate. Each layer catches a different class of defects. The conjunction of all layers is the strongest available filter.

## Part XII: the Curry-Howard connection

At the type-theoretic level, the existential witness pattern

$$
\exists w\; \mathrm{Witness}(w,x)
$$

is a dependent sum type:

$$
\Sigma_{w : W}\; \mathrm{Valid}(w,x).
$$

The witness $w$ is a proof term. The checker verifies the typing judgment. "Propose a proof sketch and check it," "propose a program and verify it," and "propose an invariant and validate it" are the same type-theoretic operation: construct a term, then verify its type.

This is the deepest reason why the neuro-symbolic split is not an engineering hack. It is the computational content of existential quantification itself. Finding a witness is constructing a proof term. Checking a witness is type checking. The LLM searches the space of proof terms. The checker verifies the typing derivation.

That observation connects to Tutorial 13 (what reasoning is): reasoning, in the constructive sense, is producing witnesses together with evidence that they are correct. The neuro-symbolic pair mechanizes exactly that.

## Part XIII: what becomes possible in practice

The practical map is broad. Six applications illustrate the range. Each one follows the same pattern — propose, check, accept or refine — but the domain gives it different texture.

Natural language to formal logic:

$$
\exists \varphi\;
\big(
\mathrm{Parsed}_N(\text{English},\varphi)
\land
\mathrm{TypeCheck}(\varphi)
\land
\mathrm{MeaningCheck}(\varphi)
\big).
$$

The model translates informal requirements into formal specifications. The checker verifies well-formedness and semantic plausibility. This is where the model's linguistic strength is most directly useful: it bridges the gap between natural language and formal syntax.

Spec repair:

$$
\exists \varphi'\;
\big(
\mathrm{ProposedRepair}_N(\varphi',\varphi,c)
\land
\mathrm{Blocks}(\varphi',c)
\land
\mathrm{PreservesReqs}(\varphi')
\big).
$$

When a counterexample reveals a design flaw rather than a coding bug, the spec itself needs repair. The model proposes a tightened spec that blocks the counterexample while preserving the original requirements. This is the Part VI loop applied at the specification level.

Patch generation:

$$
\exists p'\;
\big(
\mathrm{ProposedPatch}_N(p',p,c)
\land
\mathrm{Blocks}(p',c)
\land
\mathrm{Preserves}(p',\mathrm{Req})
\big).
$$

The coding-level analogue of spec repair. The model proposes a code change; the checker verifies that the change eliminates the bug without breaking existing requirements.

Parameter synthesis:

$$
\exists \theta\; \forall \sigma\; \neg \exists s\;
\big(
\mathrm{Scenario}(\sigma)
\land
\mathrm{Reachable}(s,M(\theta),\sigma)
\land
\mathrm{Bad}(s)
\big).
$$

This has synthesis shape: find parameter values such that no allowed scenario reaches a bad state. The model proposes candidate parameter regions; the symbolic side checks universally within each region.

Abductive diagnosis:

$$
\exists h\;
\big(
\mathrm{ProposedHypothesis}_N(h,e)
\land
\mathrm{Explains}(h,e)
\land
\mathrm{Consistent}(h)
\big).
$$

Given observed evidence, find a hypothesis that explains it and is internally consistent. This is the diagnostic direction: reasoning backward from symptoms to causes, with the checker ensuring the proposed explanation is logically coherent.

Counterexample-guided refinement (the Part VI loop in its simplest notation):

$$
x_{t+1}
=
\mathrm{Refine}_N(x_t,c_t),
\qquad
c_t = \mathrm{Counterexample}_S(x_t).
$$

## Part XIV: what remains impossible or limited

There are hard limits.

Undecidability still applies:

$$
\mathrm{Undecidable}(L)
\rightarrow
\neg \exists D\; \forall x\;
\big(
\mathrm{Halts}(D,x)
\land
\mathrm{Correct}(D,x)
\big).
$$

No pairing of models and checkers can make every semantic property decidable. Rice's theorem ensures that for any Turing-complete language, most non-trivial semantic properties are undecidable. The LLM can make heuristic search much better within a given time budget, but it cannot move the decidability boundary.

Open-world tasks remain open-world:

$$
\neg \exists c\;
\big(
\mathrm{GeneratedAndChecked}_{NS}(c,x)
\land
\mathrm{Bad}(c,x)
\big)
$$

does not imply

$$
\neg \exists c\; \mathrm{Bad}(c,x)
$$

unless there is a coverage argument.

This is the same gap Tutorial 19 identified between corroboration and proof. There it appeared as $E \subsetneq E^*$: the evidence set is always a proper subset of the space of possible tests. Here it appears as the LLM's proposal distribution having blind spots: regions of the witness space where $q_N(y \mid x) = 0$.

The most dangerous mistake is to confuse "the model found no counterexample" with "no counterexample exists." The first is a statement about the model's coverage. The second is a statement about the world. One is bounded by the search. The other is bounded by reality.

The model can make search much better.

It cannot erase logic's boundary conditions.

## Part XV: the deepest synthesis

The cleanest combined formula is:

$$
\mathrm{Assured}_{NS}(x)
\iff
\mathrm{Sound}(\mathrm{Check}_S)
\land
\mathrm{Coverage}(U)
\land
\neg \exists u\;
\big(
\mathrm{GeneratedAndChecked}_{NS}(u,x)
\land
\mathrm{Bad}(u,x)
\big).
$$

In practice, when coverage is not proved, the honest claim is weaker:

$$
\mathrm{HighConfidence}_{NS}(x)
\iff
\mathrm{Sound}(\mathrm{Check}_S)
\land
\neg \exists u\;
\big(
\mathrm{GeneratedAndChecked}_{NS}(u,x)
\land
\mathrm{Bad}(u,x)
\big).
$$

The difference between Assured and HighConfidence is exactly the presence or absence of a coverage argument.

So the bottom line is:

- LLMs expand and guide search,
- symbolic methods compress that search into semantically valid survivors,
- the pair is strongest where tasks reduce to witnesses, counterexamples, or quantified designs with explicit checkers,
- the architecture's trust comes from the checker, not the model,
- and the honest epistemological position distinguishes coverage from non-coverage.

## Takeaway

The deepest working slogan is:

$$
\begin{aligned}
\text{LLM} &= \text{proposal prior}, \\
\text{symbolic method} &= \text{semantic judge}.
\end{aligned}
$$

From that, three neuro-symbolic frontiers follow, one quantifier level deeper than the last:

$$
\exists w\; \mathrm{Witness}(w,x)
$$

$$
\neg \exists c\; \mathrm{Counterexample}(c,x)
$$

$$
\exists d\; \forall a\; \neg \exists u\; \mathrm{Bad}(u,d,a,x)
$$

If a problem can be put into one of those forms, the pairing can be extremely powerful.

The final guarantee comes from the checker.

The final leverage comes from the model.

And the honest boundary between them is the line between soundness and coverage.
