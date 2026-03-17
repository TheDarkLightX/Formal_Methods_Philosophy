---
title: "Attacking hard problems: Church's synthesis problem"
layout: docs
kicker: Tutorial 11
description: What Church's synthesis problem asks, what the Büchi-Landweber result settled, why complexity remains hard, and an invariant-first workflow for systematic attacks.
---

This tutorial has two goals:

1. Explain Church's synthesis problem and the classical decidability result from the literature.
2. Demonstrate a systematic way to attack hard problems, even when a full solution is not reached.

The method in Part V is the point of this tutorial: decompose the problem, list non-negotiable invariants, then work backward with falsifiable attempts.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Assumption hygiene for this tutorial</p>
  <ul>
    <li><strong>Assumption A (scope):</strong> The main positive decidability claim is scoped to specifications expressible in monadic second-order logic over one successor (S1S), as in the Büchi-Landweber setting.</li>
    <li><strong>Assumption B (artifact):</strong> "Solution" means a finite-state implementation (for example, a transducer or controller) plus a proof obligation that the implementation meets the spec in the chosen model.</li>
    <li><strong>Assumption C (complexity):</strong> Worst-case complexity is a planning signal, not a per-instance runtime prediction.</li>
  </ul>
</div>

## Part I: what Church's synthesis problem asks

Before the theorem statement, hold one tiny game in mind.

At each time step:

1. the **environment** chooses an input bit `req_t`,
2. the **system** responds with an output bit `grant_t`,
3. a specification watches the whole infinite play and decides whether the system met its obligation.

<figure class="fp-figure">
  <p class="fp-figure-title">A tiny realizability game</p>
  {% include diagrams/church-game-board.svg %}
  <figcaption class="fp-figure-caption">
    The environment moves, the system responds, and the specification judges the whole play. Church synthesis asks whether a strategy exists that always wins.
  </figcaption>
</figure>

Two tiny specs already show the shape of the problem:

- **Realizable spec:** "whenever `req_t = 1`, output `grant_t = 1` in the same round." If current input is visible before the system chooses, a simple strategy exists: copy the request bit.
- **Unrealizable spec:** "output `grant_t = req_{t+1}`." This asks the system to know the next environment move before it happens. No causal strategy can do that for all environments.

Those two cases already contain the whole Church question: is there a strategy, under the information pattern of the game, that guarantees the spec against every allowed environment?

Church's question can be phrased as:

Given a formal specification of input-output behavior over time, can an algorithm construct a system that is guaranteed to satisfy that specification for all allowed environments?

A standard formal shape is:

$$
\exists F \;\; \forall X \;\; \varphi(X, F(X))
$$

where:

- $X$ is the environment input stream,
- $F$ is a causal strategy (the system),
- $\varphi$ is the temporal specification.

The outcome is binary:

- **Realizable:** there exists such an $F$.
- **Unrealizable:** no such causal $F$ exists.

This is already a hard shift in mindset. The question is not "does a given program pass tests?". The question is "does a correct program exist, and can it be synthesized algorithmically from logic?".

## Part II: what the literature settled

Historical anchor:

- Alonzo Church posed the synthesis question at the 1957 Cornell Summer Institute (published in the 1960 summaries).
- Büchi and Landweber gave the classical decidability theorem in 1969.

The Büchi-Landweber theorem (informal tutorial statement):

If the specification is expressed in S1S, realizability is decidable. When realizable, a finite-state winning strategy can be constructed. When unrealizable, failure can be certified by an opposing winning strategy.

So the core question is not open in that scope. For the S1S setting, this is a solved decision problem.

In the tiny `req/grant` game, that means the realizable same-round spec is not just intuitively winnable. In the right logical setting, there is a theorem saying a winning strategy can be decided and, when it exists, constructed. The future-looking spec is the opposite shape: there is no causal strategy to extract.

## Part III: if it is solved, why is it still hard in practice?

The main barrier is complexity, not logical impossibility.

For full LTL synthesis, realizability is 2EXPTIME-complete. Informally, with formula size $n$, worst-case procedures can scale like:

$$
2^{2^{\Theta(n)}}
$$

That is the state-space wall: automata blow-ups, determinization costs, and large parity games.

The tiny game hides that cost because it barely has any memory. The blow-up starts when the specification needs to remember longer histories, alternate safety with liveness, or encode richer environment assumptions.

Important scope note:

- This is a worst-case class result, not a claim that every practical instance is intractable.
- It still explains why naive "synthesize everything automatically" expectations fail on many real specs.

The tiny `req/grant` game from Part I is nowhere near this hard. That is useful, not embarrassing. It gives a clean baseline: the toy game shows what realizability means, and the complexity result explains what happens when the spec language and game structure scale up.

## Part IV: four major attack vectors in the literature

Keep the tiny `req/grant` game in view here. Each attack vector is a different way of making that same game easier to solve without changing what counts as a winning strategy.

### 1) Restrict the logic (GR(1))

Idea:

- Limit specification shape to a useful fragment (assumptions and guarantees with structured liveness).
- Solve the induced game with symbolic fixed-point algorithms.

Tradeoff:

- Better scalability on many practical classes.
- Lower expressiveness than full LTL.

Gate:

- Check whether the original spec can be encoded in GR(1) without semantic loss.

Tiny-game version:

- If the `req/grant` obligation can be written as structured assumptions and guarantees, this route keeps the same game but moves it into a fragment with better solver behavior.
- The spec "if `req_t = 1`, then `grant_t = 1` in the same round" already has the flavor of a GR(1)-style obligation: an assumption about visible inputs and a structured guarantee about outputs.
- In a toy case like this, the point is not speedup. The point is to see the shape of the restriction: allow the fragment to stay simple enough that the induced game stays manageable.

### 2) Bound the implementation (bounded synthesis)

Idea:

- Fix an implementation size bound $k$.
- Encode existence of a $k$-state implementation into SAT/SMT/QBF constraints.
- If UNSAT, increase $k$ and retry.

Tradeoff:

- Leverages strong solver engineering.
- Requires bound-management strategy and can still grow hard.

Gate:

- Maintain completeness by monotone bound increase and explicit satisfiability certificates.

Tiny-game version:

- Ask first whether a one-state controller can realize the toy spec. If not, ask whether two states are enough.
- For the realizable "copy the request" spec, a tiny finite controller exists. For the unrealizable future-looking spec, every bound fails, and those failures are informative rather than mysterious.

### 3) Compose local syntheses (compositional synthesis)

Idea:

- Split a large system into modules with local assume-guarantee contracts.
- Synthesize locally, then prove that composition preserves global goals.

Tradeoff:

- Reduces monolithic state explosion.
- Risks contract mismatch and emergent deadlock/livelock at composition boundaries.

Gate:

- Require explicit compatibility checks between module assumptions and guarantees.

Tiny-game version:

- Split the toy system into a request-reader and a grant-policy component.
- One local contract can say when a request is considered pending, and another can say when a grant is legal.
- Composition succeeds only if those local rules still realize the original `req/grant` obligation together.
- The exercise is almost comically small, but that is the point. It makes the contract question visible: what does the grant side assume about when the request is available, and what does it guarantee in return?

### 4) Change the mathematical representation

Idea:

- Replace the default discrete transition-system representation with another decidable formal substrate.
- Goal: shift where complexity lands, and expose new solver structure.
- Example hypothesis class: atomless Boolean algebra formulations (including GSSOTC-style proposals), provided the semantics map is explicit and checkable.

Status:

- This is a research program category, not one single settled theorem schema for all alternatives.
- Claims of bypassing classic bottlenecks require explicit translation theorems and benchmark evidence.

Gate:

- For each alternative formalism, prove meaning preservation against the source spec class and publish counterexample behavior when translations fail.

Tiny-game version:

- A new representation is only interesting if it preserves the same split as the toy game: the same-round spec stays realizable, and the future-looking spec stays unrealizable.
- Keep the same `req/grant` behavior but rewrite it in a different substrate, for example as an algebraic or stream-based constraint system.
- If the new representation is honest, it should preserve the same realizability answer. If it changes the answer, that mismatch is already a counterexample to the translation claim.

## Part V: my attack method (decompose, list invariants, work backward)

This section presents the method, not a promise of a complete breakthrough.

Keep the tiny `req/grant` game on the table here. The method should feel usable on that toy case first, before it is trusted on larger synthesis problems.

### Step 1: decompose the problem

Decompose Church-style synthesis into independently testable slices:

1. **Semantic slice:** what exactly counts as satisfaction in the chosen logic.
2. **Game slice:** who controls which variables, and what information each side has.
3. **Automata/encoding slice:** how formulas become checkable artifacts.
4. **Strategy slice:** memory model (finite-state, bounded memory, symbolic memory).
5. **Complexity slice:** where the largest blow-up is expected.
6. **Composition slice:** how local solutions compose.

Each slice should have a local failure witness. If no local witness exists, the slice is underspecified.

In the tiny game, that decomposition is already visible:

- the semantic slice asks whether "same round" or "next round" is the real obligation,
- the game slice asks whether the system sees `req_t` before choosing `grant_t`,
- the strategy slice asks whether memory is needed at all.

### Step 2: create the invariant ledger

A useful attack requires a list of invariants that any valid solution must satisfy.

In the tiny game above, these invariants are already visible:

- `InvCausality` kills the future-looking spec `grant_t = req_{t+1}`.
- `InvTotalStrategy` asks whether the system has a defined move for every request history.
- `InvSafety` would correspond to "never output a forbidden grant on any finite prefix."

| Invariant | Why it is required | Typical falsifier | Gate/check |
|---|---|---|---|
| `InvSemanticsPreserved` | Translation must keep meaning of the original spec | Input trace satisfies original but not translated spec (or reverse) | Equivalence or soundness proof plus counterexample search |
| `InvCausality` | System outputs must not depend on future inputs | Strategy uses information from time `t+1` at time `t` | Causality check on strategy representation |
| `InvTotalStrategy` | Strategy must define an output for every reachable input history | Undefined move in a reachable state | Totality check on transition relation |
| `InvSafety` | Safety clauses must hold on all prefixes | Finite bad prefix witness | Safety model checking |
| `InvLiveness` | Progress obligations must hold on infinite runs | Fair cycle avoiding guarantee forever | Buchi/parity acceptance check |
| `InvFiniteImplementable` | "Synthesized" means implementable artifact, not only existential proof | Constructed witness needs infinite memory | Extract finite-state machine and validate |
| `InvContractCompatibility` | Local components must agree under composition | Local assumptions jointly unsatisfiable | Assume-guarantee discharge |
| `InvTerminationOrRefutation` | Each attempt must end with artifact or counterexample | Open-ended loop without witness | Time-box plus mandatory witness policy |

This ledger is the backbone. New approaches are accepted only if they preserve all required invariants, or if they explicitly relax one invariant and document the consequence.

### Step 3: work backward from invariants to candidate methods

Backward strategy:

1. Pick one hard invariant that currently blocks progress.
2. Choose the representation where that invariant is easiest to check.
3. Run one attempt with a pre-registered failure condition.
4. If falsified, keep the witness and update the next attempt.

This is an evidence loop, not a one-shot derivation.

In the tiny game, that means: if `InvCausality` is the blocker, use the representation that makes illegal future dependence easiest to expose. If `InvFiniteImplementable` is the blocker, use the representation that most directly exposes controller size.

### Step 4: attempt ledger (scientific loop)

Use a fixed experiment table so failed attempts become reusable evidence:

For the tiny game, the table is easy to imagine. GR(1) should handle the same-round obligation cleanly. Bounded synthesis should find a tiny controller quickly. Any alternative representation should be rejected immediately if it makes the future-looking spec look realizable.

| Attempt | Representation | Primary target invariant | Expected gain | Falsifier obtained? | Next move |
|---|---|---|---|---|---|
| A1 | Full LTL -> deterministic automata -> parity game | `InvSemanticsPreserved` | Max expressiveness | Often yes, due to blow-up or timeout | Restrict logic or bound strategy size |
| A2 | GR(1) fragment | `InvTerminationOrRefutation` | Faster fixed-point solving | Yes if spec cannot be encoded cleanly | Refactor spec, or move to A3 |
| A3 | Bounded synthesis with size `k` | `InvFiniteImplementable` | Small explicit controllers | Yes when UNSAT for current `k` | Increase `k`, or revise assumptions |
| A4 | Compositional assume-guarantee | `InvContractCompatibility` | Smaller local games | Yes when contracts conflict | Repair contracts, add interface invariants |
| A5 | Alternative algebraic substrate | `InvSemanticsPreserved` | Potentially different complexity profile | Yes when translation fails equivalence checks | Refine mapping or narrow scope |

## Part VI: what progress looks like without "solving everything"

A serious attack can be successful even without a global win. Progress includes:

1. A sharper decomposition with explicit interfaces.
2. A stable invariant ledger with executable checks.
3. Counterexamples that kill bad directions quickly.
4. Smaller realizable subproblems with certified artifacts.
5. Clear scope boundaries: what is solved, what is open, what assumptions are carrying risk.

This is the practical lesson from hard formal problems: progress is cumulative when claims are falsifiable and every failure leaves a reusable witness.

Even the toy game can contribute to that progress. A one-state winning strategy is a minimal positive artifact. The future-looking spec is a minimal negative witness for causality. Those small cases are not throwaway examples, they are calibration points for the whole attack method.

Put simply, hard problems have shapes. A shape is the practical pattern of the problem: who chooses actions, what must always hold, how long behavior runs, and where complexity explodes. Once that shape is written down, method choice becomes less ideological and more operational.

A compact plain-language shape checklist:

1. Who are the players: system, environment, or both?
2. What must hold: safety, progress, or both?
3. Is time finite or infinite?
4. What artifact counts as success: an implementation, a strategy, or a certificate?
5. Where is the likely bottleneck: state growth, determinization, game solving, or composition?

Method adjustment then follows evidence:

1. If full expressiveness is too costly, restrict logic.
2. If search explodes, bound implementation size and iterate bounds.
3. If global solving stalls, decompose with assume-guarantee interfaces.
4. If failures are mostly timeouts, switch representation to recover informative falsifiers.

This turns method selection into a portfolio process: start with one method, keep witness artifacts, and pivot when progress metrics flatten.

## References (starting points)

- Alonzo Church, *Application of Recursive Arithmetic to the Problem of Circuit Synthesis* (Cornell Summer Institute talks, 1957; published in 1960 summaries).
- J. Richard Büchi and Lawrence H. Landweber, *Solving Sequential Conditions by Finite-State Strategies*, Trans. Amer. Math. Soc. 138 (1969), 295-311. DOI: https://doi.org/10.1090/S0002-9947-1969-0280205-0
- Amir Pnueli and Roni Rosner, *On the Synthesis of a Reactive Module*, POPL 1989. DOI: https://doi.org/10.1145/75277.75293
- Roderick Bloem, Barbara Jobstmann, Nir Piterman, Amir Pnueli, Yaniv Sa'ar, *Synthesis of Reactive(1) Designs*, Journal of Computer and System Sciences 78(3), 2012. DOI: https://doi.org/10.1016/j.jcss.2011.08.007
- Bernd Finkbeiner and Sven Schewe, *Bounded Synthesis*, STTT 15, 2013.
