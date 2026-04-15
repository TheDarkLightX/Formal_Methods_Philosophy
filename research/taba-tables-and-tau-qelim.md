---
title: "Tau qelim and TABA table semantics"
layout: docs
kicker: Research log
description: "A neuro-symbolic research log for fragment-sensitive Tau quantifier elimination and the current atomless TABA table-semantics frontier."
---

This log records the neuro-symbolic research loop behind two tutorial threads:

- Tau Language quantifier-elimination optimization,
- TABA table semantics and the Tau table-kernel replay for the executable
  fragment.

It is intentionally more specific than the tutorial version.
The tutorials teach the concepts.
This page shows the method in practice: proposals, autoformalized statements,
proof attempts, failed assumptions, benchmarks, counterexamples, and scoped
promotions.

Related tutorials:

- [Tutorial 40: Optimizing Tau Language, Part I]({{ '/tutorials/optimizing-tau-language-part-i-qelim-fragment-dispatch/' | relative_url }})
- [Tutorial 39: Safe infinite-recursive tables in Tau Language]({{ '/tutorials/safe-infinite-tables-in-tau-language/' | relative_url }})
- [Tutorial 38: TABA, formula by formula]({{ '/tutorials/taba-formulas-and-guarded-successor/' | relative_url }})

Short paper:

- [Fragment-Sensitive Quantifier Elimination and Safe Table Updates in Tau]({{ '/research/fragment-sensitive-qelim-and-safe-tables/' | relative_url }})

Quick navigation:

- [Current recorded status](#current-recorded-status-april-13-2026)
- [Why compile Tau fragments?](#why-compile-tau-fragments)
- [The qelim lesson](#1-the-qelim-lesson)
- [The table-semantics ladder](#4-the-table-semantics-ladder)
- [What finite tables can do](#49-what-finite-tables-can-do)
- [Why the infinite form remains hard](#49-why-the-infinite-form-remains-hard)
- [What remains unsolved](#8-what-remains-unsolved)

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Assumption hygiene</p>
  <p><strong>Scope.</strong> The qelim evidence applies to the supported propositional existential fragment that the experiment compiler accepted. The table evidence applies to the finite and atomless fragments named below. Neither result proves full Tau Language behavior or full TABA tables.</p>
  <p><strong>Stress test.</strong> Unsupported formulas must fall back instead of silently changing meaning. Table carriers must carry semantic equivalence evidence before being treated as executable replacements.</p>
  <p><strong>Project boundary.</strong> The table implementation discussed here is a community research prototype. It is not an official IDNI or Tau Language implementation, not an endorsement claim, and not evidence of what IDNI intends to implement. It may be weaker, narrower, or differently shaped than the standard required for an official Tau feature.</p>
</div>

## How to read this research log

This page has a different job from the tutorials.
The tutorials compress the stable teaching path.
This page keeps the working research record: what was proposed, what was
formalized, what failed, what was checked, and what remains outside the current
model.

The formula readings follow the same convention as the tutorials:

- <strong>Standard reading</strong> states what the displayed formula literally says.
- <strong>Plain English reading</strong> gives the least-loss explanatory version.
- <strong>Boundary</strong> states what the evidence does not prove.

The most important qelim distinction is:

$$
\operatorname{OptimizationEvidence}
\ne
\operatorname{WholeLanguageProof}.
$$

Standard reading:

- Evidence that a guarded optimization works on a checked fragment is not equal
  to a proof about all Tau Language inputs.

Plain English reading:

- A faster route on one legal fragment is a serious result, but it is not a
  license to replace the whole qelim engine.

## Method: the neuro-symbolic loop

The method on this page is:

$$
\operatorname{Idea}
\to
\operatorname{FormalStatement}
\to
\operatorname{Checker}
\to
\operatorname{Counterexample\ or\ Proof}
\to
\operatorname{Revision}
\to
\operatorname{ScopedClaim}.
$$

Standard reading:

- A research idea is turned into a formal statement, checked by a mechanical or
  executable tool, either refuted or supported, revised when necessary, and only
  then promoted as a scoped claim.

Plain English reading:

- The model proposes. The formal tool checks. Counterexamples force revision.
  Only surviving claims are allowed into the tutorial.

This is a small version of a broader formalized-mathematics workflow: human
judgment chooses the statement and boundary, proof tools check the exact claim,
and failures refine the next statement.
The technical dependencies for this page are the TABA draft, the Tau replay
artifacts, the Lean checks, and the cited quantifier-elimination literature.

Boundary:

- This project borrows the method pattern, not the authority of those projects.
  A local Lean proof, Tau replay, or benchmark here proves only the scoped claim
  stated next to it.

## Current recorded status, April 13, 2026

The shortest current summary is:

- the Tau qelim experiment has one measured default candidate,
  `TAU_QELIM_BACKEND=auto`,
- the safe table tutorial has runnable Tau demos behind
  `TAU_ENABLE_SAFE_TABLES=1`,
- the standalone experiment repo now has a public one-command demo suite that
  downloads official Tau, applies the local patch, rebuilds Tau, and runs the
  table and qelim-backed policy checks,
- the finite CBF and priority-table bridge has a checked minterm-tree compiler,
- the safe infinite-recursive table fragment has checked monotone fixed-point
  evidence,
- the latest local Lean artifacts add set/select algebraic laws, stream-level
  Tau semantics, stream laws, and a terminating iterated optimizer API,
- the restricted c111 rewrite normalizer proves a seven-rule Tau-expression
  rewrite system terminating, semantics-preserving, confluent, and
  normal-form unique inside its scoped expression language,
- unrestricted TABA tables remain open because same-stratum prime,
  current-state-dependent guards, unrestricted recurrence, NSO, and Guarded
  Successor still need a fully connected syntax, semantics, and runtime
  lowering bridge.

What the optimizer and stream artifacts give us:

- Composition and runtime: c095, c097, c098, c103, c104, and c109 connect
  semantic-preserving rewrites to a composed dispatcher, a runtime
  satisfiability decider, benchmarked evaluation-count reductions, a combined
  optimizer pipeline, a size-reduction theorem, and a terminating
  `fullSimplify` API.
- Stream layer: c107 and c108 lift the discussion from static table
  expressions to time-indexed transformers and feedback laws in the style of
  TABA section 8.4.
- Higher-order and equivalence surface: c088, c089, and c110 provide a
  higher-order recurrence syntax with examples and a sound but incomplete
  equivalence decider based on simplification and structural equality.
- Restricted rewrite surface: c111 gives a proof-backed normalizer for a small
  expression language with `common`, `pointJoin`, and `pointCompl`. The proof
  supports a scoped compiler prepass, not complete Boolean equivalence for all
  Tau syntax.

Boundary:

- This is a verified fragment pipeline, not a proof of complete equivalence for
  every Tau or TABA expression.
- The equivalence decider is sound where it returns success, but incompleteness
  means failure to prove equality is not evidence of inequality.

The strongest qelim measurement currently recorded is the policy-shaped
semantic corpus:

$$
\frac{
  \sum \operatorname{time}_{\mathrm{default}}
}{
  \sum \operatorname{time}_{\mathrm{auto}}
}
=
\frac{210.853}{40.940207}
\approx
5.15.
$$

Standard reading:

- On the checked policy-shaped corpus, the summed default qelim time was
  $210.853$ ms and the summed `auto` qelim time was about $40.940$ ms, so the
  aggregate qelim-time speedup was about $5.15$.

Plain English reading:

- On this measured corpus, the guarded `auto` route did the same checked work
  in about one fifth of the qelim time.

Boundary:

- `auto` is the promoted experimental candidate.
- `TAU_QELIM_AUTO_GUARD`, `TAU_QELIM_BDD_AC_CANON`, and
  `TAU_REWRITE_DOUBLE_NEG` remain opt-in lanes because their latest measured
  results did not justify making them default.
- The measurement is a same-binary benchmark record on a policy-shaped corpus.
  It is not a proof that `auto` is faster on all Tau inputs.
- The earlier bounded ladder-and-mux matrix recorded about `3.47x`; the
  policy-shaped corpus is the stronger result because its cases mirror the
  safe-table demo domain and the residual validator checks semantic parity.

The later c111-inspired qelim prepass has a more modest guarded form:

$$
\operatorname{KB}_{\mathrm{guard}}(e)
=
\begin{cases}
\operatorname{normalize}_{\mathrm{KB}}(e),
& \operatorname{Absorb}(e)>0,\\
e,
& \operatorname{Absorb}(e)=0.
\end{cases}
$$

Standard reading:

- The guarded KB pass normalizes expression $e$ if the compiled expression
  contains at least one absorption opportunity. Otherwise it returns $e$
  unchanged.

Plain English reading:

- The rewrite pass is selected by a cheap structural sign that the pass has
  something local and useful to remove.

Current check record:

- `TAU_QELIM_BDD_KB_REWRITE=guarded` preserved output parity on the targeted
  qelim probe and on generated matrices.
- On the current 18-case generated matrix with `3` repetitions, guarded KB
  reduced compiled KB nodes by `42.73%` and had internal qelim-time ratio about
  `0.95` against plain BDD.
- On the current 34-case generated matrix with `3` repetitions, guarded KB
  reduced compiled KB nodes by `40.81%` and had internal qelim-time ratio about
  `0.952` against plain BDD.
- Whole-command elapsed time remained effectively neutral in this harness
  because process startup dominates.
- On the policy-shaped semantic corpus, `auto + guarded KB` preserved parity
  but recorded `0` KB rewrite steps and was slightly slower than `auto` alone,
  so the `5.15x` result belongs to the auto BDD/component route rather than to
  KB rewriting.

Boundary:

- This supports `TAU_QELIM_BDD_KB_REWRITE=guarded` as opt-in research evidence.
  It does not justify making the pass default.
- The Lean proof is about the restricted rewrite language. The patched Tau
  prepass is an implementation inspired by that proof, with output parity and
  benchmark records, not a proof of the entire Tau qelim engine.

## Why compile Tau fragments?

For this research log, "compile" means fragment-preserving lowering:

$$
\operatorname{compile}_{\mathcal F}(S)=A
\quad\text{and}\quad
\forall I,O,\;
A(I,O)=\top
\Longleftrightarrow
(I,O)\models S,
\qquad S\in\mathcal F.
$$

Standard reading:

- For a specification $S$ inside fragment $\mathcal F$, the compiler
  produces an artifact $A$. For every input/output pair $I,O$, the artifact
  accepts exactly when $I,O$ satisfies the original specification.

Plain English reading:

- A compiled fragment is useful only when it keeps the same meaning as the
  source spec.

Concrete benefits already seen in this work:

- qelim compilation: the `auto` route lowers supported existential formulas to
  a BDD existential-abstraction path and produced the measured `5.15x`
  aggregate qelim-time speedup on the checked policy-shaped corpus.
- table lowering: the safe table syntax lowers to guarded helper expressions
  and is checked against an explicit raw Boolean-algebra denotation.
- finite table carriers: schema-checked bitset carriers can run finite relation
  operations much faster than direct tuple-set evaluation on the checked
  kernels.

Boundary:

- These are fragment compilers, not a whole-language Tau compiler.
- Each compiler needs its own acceptance guard, fallback behavior, and semantic
  adequacy evidence.

## Public table demo evidence

The demo repo is
[TauLang-Experiments](https://github.com/TheDarkLightX/TauLang-Experiments).

The public reproduction command is:

```bash
./scripts/run_public_demos.sh --accept-tau-license
```

The table-only command is:

```bash
./scripts/run_table_demos.sh --accept-tau-license
```

The workflow is:

```text
official Tau checkout
  + local experiment patch
  + parser regeneration
  + Tau build
  + table checks
```

The local run checked these public facts:

- `safe_table_idempotence`,
- `finite_carrier_update`,
- `finite_carrier_pointwise_revision`,
- `tau_native_table_agrees_with_raw`,
- `protocol_firewall_table_agrees_with_raw`,
- `protocol_firewall_emergency_priority`,
- `protocol_firewall_oracle_slice`,
- `collateral_reason_table_agrees_with_raw`,
- `collateral_reason_registry_priority`,
- `collateral_reason_provenance_slice`,
- `incident_memory_table_agrees_with_raw`,
- `incident_memory_exploit_priority`,
- `incident_memory_clear_slice`,
- `pointwise_revision_entry_agrees_with_helper`,
- `pointwise_revision_whole_table_agrees`,
- `pointwise_revision_outside_guard_preserves_old`,
- `pointwise_revision_inside_guard_uses_replacement`,
- `pointwise_revision_idempotent`,
- `tau_native_table_rejected_without_flag`.

The most important demo equation is:

$$
\operatorname{priority\_quarantine\_update}
=
\operatorname{priority\_quarantine\_raw}.
$$

Standard reading:

- The Tau-native table syntax and the raw guarded-choice expansion denote the
  same Boolean-algebra function.

Plain English reading:

- The table syntax is not merely accepted by the parser. It is checked against
  the formula it is supposed to mean.

Breakthrough:

- Earlier table demos could be read as helper-function demos or JSON-side
  lowering demos. This one is Tau-native: the parser accepts the feature-gated
  table syntax, the syntax lowers to guarded choice, and the feature flag off
  case rejects the same syntax.
- The reproduction workflow also moved from a private dirty checkout to a public
  patch workflow: official Tau is downloaded by the user, patched locally,
  rebuilt, and tested.

Boundary:

- This proves the safe guarded-choice table surface works as a demo.
- It does not prove unrestricted recurrence, same-stratum prime, full NSO,
  Guarded Successor, or official full TABA table semantics.

The more interesting demo equations are all the same kind of check:

$$
\operatorname{TableDemo}_i
=
\operatorname{RawExpansion}_i.
$$

Standard reading:

- For each checked demo $i$, the Tau-native table term denotes the same
  Boolean-algebra value as the explicitly expanded guarded-choice formula.

Plain English reading:

- The demos are not relying on table syntax by trust. Tau is asked whether each
  table can differ from its raw formula, and the expected result is `no
  solution`.

The three new public demos make the table feature easier to understand:

- protocol firewall: overlapping guards with first-row priority,
- collateral reason router: first failed admission reason,
- incident memory: rows that transform an existing symbolic state,
- pointwise revision: guarded table update with locality and idempotence checks.

The pointwise revision law is:

$$
\operatorname{Rev}_{G,A}(T)(i)
:=
\bigl(G(i)\wedge A(i)\bigr)
\vee
\bigl(G(i)'\wedge T(i)\bigr).
$$

Standard reading:

- For each key $i$, the revised table uses $A(i)$ inside $G(i)$ and
  $T(i)$ inside the prime of $G(i)$.

Plain English reading:

- A table update can be stored as a finite symbolic rule and read pointwise at
  any key.

## 1. The qelim lesson

The main qelim lesson was not simply "BDD is faster."
The more accurate lesson was:

> qelim algorithm choice should be fragment-sensitive, because the fastest method depends on where the structure lives: in syntax, or in the compiled carrier.

For the checked Tau fragment, the useful route was direct compiled forgetting before
the default `anti_prenex` path.

The scoped dispatcher is:

$$
\operatorname{qelim}_{\mathrm{Tau}}(\varphi)=
\begin{cases}
\operatorname{abstract}_{\mathrm{BDD}}(\varphi),
& \varphi\in\mathcal{F}_{\mathrm{prop}\exists},\\
\operatorname{qelim}_{\mathrm{antiPrenex}}(\varphi),
& \varphi\notin\mathcal{F}_{\mathrm{prop}\exists}.
\end{cases}
$$

Here $\mathcal{F}_{\mathrm{prop}\exists}$ is the supported propositional
existential fragment accepted by the experiment compiler.

The core Boolean operation is:

$$
\exists x.\,f
=
f[x:=\bot]\lor f[x:=\top].
$$

In the BDD carrier, that is existential abstraction. It removes the quantified
variable while preserving the Boolean function over the remaining variables.

## 2. What the Tau experiment found

The first implementation-shaped Tau result came from the same-binary route that
selected the direct BDD path before `anti_prenex` for supported formulas.

The checked regression surface recorded:

- `60 / 60` supported generated formulas took the `bdd_direct` route,
- `4 / 4` unsupported guard cases fell back to the default route,
- `64 / 64` outputs matched the default route semantically on the checked harness,
- supported median command timing was about `0.2368 ms` for BDD versus `0.8235 ms` for default in that experiment.

This was a real optimization candidate, but it was not a proof of global
superiority. Later timing work showed that order choice and benchmark shape
matter.

The current promoted experimental mode is:

```text
TAU_QELIM_BACKEND=auto
```

The `auto` route means:

- use the guarded BDD route only when the fragment compiler accepts the formula,
- enable the structural preprocessing portfolio by default,
- use quantified-first occurrence-density order by default,
- keep unsupported formulas on Tau's default path.

The current checked auto-density report records:

- exact output parity on the checked policy-shaped corpus,
- semantic residual validation on `9` cases,
- route counts `{ components: 10, dp: 5, monolithic: 30 }`,
- summed default qelim time `210.853 ms`,
- summed `auto` qelim time about `40.940 ms`,
- aggregate qelim-time speedup about `5.15x`.

The surviving engineering rule is that direct BDD qelim is a guarded fast path,
not a universal replacement.

## 3. Why `anti_prenex` was not just wrong

The default path exists for a reason. Syntax-directed transformations can expose
structure that direct compilation may miss. The experiments did not show that
`anti_prenex` is a bad idea in general.

The better conclusion is conditional:

$$
\varphi\in\mathcal{F}_{\mathrm{prop}\exists}
\Longrightarrow
\operatorname{abstract}_{\mathrm{BDD}}(\varphi)
\text{ can avoid fragment-unnecessary syntax work.}
$$

Outside that fragment, the fallback remains part of the safety boundary.

## 4. The table-semantics ladder

The table work has a separate ladder of proof artifacts.
The key distinction is that Ohad Asor's TABA text sketches the table direction,
but it does not provide a completed table semantics or implementation proof.
The local work is therefore not discovering that tables are possible in the
abstract. The local work is filling in checked fragments of the missing semantic
and executable boundary.

Reference source:

```text
external/tau-lang/docs/Theories-and-Applications-of-Boolean-Algebras-0.25.pdf
```

The local PDF metadata records creation and modification on August 10, 2024.
The file may be hosted from a later web path, but the draft itself should be
treated as a 2024 draft source.

The local notes below read the TABA table section as an extensional function
semantics: tables denote functions from finite Boolean keys into a
Boolean-algebra value carrier, with sparse table syntax treated as optimization
or syntactic sugar.

Current checked ladder:

- `v386` proves finite homogeneous schedule semantics.
- `v387` adds explicit lower-key reference syntax.
- `v388` adds typed positive expressions with projection, composition, pullback, and guarded constant negation.
- `v389` proves abstract atomless table-cell splitting.
- `v390` lifts that splitting to DNF-style symbolic table projection.
- `v391` gives a concrete prefix-cylinder splitting carrier.
- `v392` gives bounded executable evidence for finite-union prefix-clopen normalization.
- `v393` proves a Lean semantic carrier for finite clopens over infinite Boolean streams.
- `v394` quotients finite clopens by semantic equivalence and specializes DNF projection completeness to that carrier.
- `v395` proves the translation-validation contract from executable prefix-word lists to quotient cells.
- `v396` proves primitive rewrite certificates for covered-descendant deletion and sibling-cylinder merge.
- `v397` proves multi-step trace soundness for certified normalizer logs, including adjacent swaps.
- `v398` implements a bounded-tested normalizer that emits certificate-shaped traces.
- `v399` adds an external checker for emitted trace logs.
- `v400` lifts row-level trace soundness into typed table expressions with rows, join, and Boolean child projection.
- `v401` proves finite recurrence approximants are preserved under certified row-normalization rewrites of the recursive body.
- `v402` proves finite clopen cells are not closed under all countable recurrence suprema.
- `v403` instantiates the powerset carrier over streams as a reference completion semantics.
- `v404` tests prefix-open cells as a smaller positive-recursion completion carrier.
- `v405` proves prefix-open cells are not closed under complement.
- `v406` adds a symbolic Borel-code Boolean completion over prefix cylinders.
- `v407` gives a concrete two-state deterministic stream automaton for the v402 witness and its complement.
- `v408` proves generic deterministic closure under complement, union, and intersection at the run-predicate level.
- `v409` replaces the running witness's semantic acceptance predicate with finite co-Buchi acceptance data.
- `v410` proves deterministic co-Buchi intersection closure and gives a checked counterexample to the naive union-good product.
- `v411` proves two-state Muller-style product projection, giving union and intersection receipts at the accepted-language level.
- `v412` generalizes the Muller product projection core to arbitrary finite lists of side states.
- `v413` packages listed finite-state Muller stream carriers with checked complement, union, and intersection receipts.
- `v414` adds the first emptiness-facing certificate: a reachable accepted self-loop singleton implies nonempty language.
- `v415` proves that accepted-language equivalence reduces exactly to emptiness of the symmetric-difference language.
- `v416` generalizes the nonempty certificate to any eventual exact recurring-state set accepted by the Muller family.
- `v417` specializes that certificate to a finite recurring-state list.
- `v418` composes the finite-list nonempty certificate with symmetric-difference realization to prove non-equivalence.
- `v419` constructs an executable product-state listed Muller carrier for union and intersection.
- `v420` constructs a first-class listed Muller symmetric-difference carrier.
- `v421` removes the external realization assumption: finite-list evidence on the constructed symmetric-difference carrier proves non-equivalence.
- `v422` proves the constructed symmetric-difference carrier is empty exactly when the original carriers are equivalent.
- `v423` proves eventual periodicity plus one post-cutoff sighting of each listed state generates the infinitely-often evidence needed by the finite-list certificate.
- `v424` proves periodic input bits plus a state-anchor equality produce the run periodicity needed by v423.
- `v425` constructs a tail-periodic input stream from finite cycle data and proves the input-periodicity premise used by v424.
- `v426` replaces abstract post-cutoff sightings with finite cycle-state table membership.
- `v427` derives the state-anchor equality from a final cycle wrap transition.
- `v428` proves bounded cycle transition consistency implies run/table agreement at every bounded index.
- `v429` lowers compact `Fin period` cycle state and bit data into the v428 bounded table theorem.
- `v430` integrates ordinary-edge agreement, wrap-anchor derivation, and finite cycle-state sightings into one finite-cycle nonempty certificate lane.
- `v431` removes the explicit stream bit-match field for `TailCycleStream`, because the stream definition already returns the finite cycle bit at each compact cycle offset.
- `v432` removes the supplied start-match field by proving that finite prelude bits and finite prelude states reach the cycle-start state at the cutoff.
- `v433` removes the supplied eventual-in-recurring predicate by deriving it from post-cutoff run periodicity, cycle-state/run agreement, and finite cycle coverage.
- `v434` implements a bounded deterministic graph-search emitter for explicit finite Muller accepting sets and validates the emitted v433-shaped certificates.
- `v435` proves the explicit finite accepting-set bridge: membership of the recurring list in the finite accepting family supplies the accepted field required by v433.
- `v436` proves the list-backed witness bridge: length-checked ordinary lists lower into the dependent `Fin`-indexed certificate tables.
- `v437` proves raw list witness validator soundness: any raw list lasso witness satisfying the validator lowers through v436 and proves nonempty accepted language.
- `v438` proves local raw-list validator soundness: ordinary-list local checks with natural-number indices lower to the v437 validator and prove nonempty accepted language.
- `v439` proves truly local raw-list validator soundness: even the cycle wrap check is a plain raw-list transition check, with the bridge back to v437 supplied by the v431 tail-cycle theorem.
- `v440` proves executable lasso checker soundness: a finite Boolean checker over raw list witness data implies the v439 validator and therefore proves nonempty accepted language.
- `v441` proves checked emitter adapter soundness: optional emitter output is useful only when the v440 checker accepts it, and accepted output proves nonempty accepted language.
- `v442` proves verified emitter wrapper soundness: wrapping any untrusted optional emitter with the checker yields a safe optional emitter, where every returned witness proves nonempty accepted language.
- `v443` proves finite graph-search emitter wrapper soundness: a Lean executable emitter can be safely used through the v440 checker and v442 wrapper for concrete finite Muller witnesses.
- `v444` proves unordered acceptance checker soundness: accepting sets are compared extensionally by mutual finite membership, so emitter output is not rejected merely because it lists recurring states in a different order.
- `v445` proves unordered verified emitter wrapper soundness: optional emitter output can use the unordered checker through the same safe wrapper pattern.
- `v446` proves graph-search unordered wrapper soundness: the Lean graph-search emitter is composed with the unordered wrapper, so any returned witness proves nonempty accepted language through the order-robust boundary.
- `v447` proves native Lean checker coverage for all v434 emitted certificates: every generated certificate is accepted by the v444 unordered checker and therefore yields nonempty-language evidence.
- `v448` proves executable checker completeness for supplied witnesses: the ordered v440 checker returns `true` exactly when the v439 local witness predicate holds.
- `v449` proves unordered executable checker exactness for supplied witnesses: the unordered checker returns `true` exactly when the local lasso conditions hold and the recurring list equals some accepting list by finite membership.
- `v450` proves the exact returned-output contract for unordered graph-search output: any returned witness satisfies the extensional local predicate and proves nonempty accepted language.
- `v451` proves TABA pointwise revision preservation: revision is old-and-new conjunction when a joint witness exists, fallback to the new spec otherwise, and idempotent when revising a spec by itself.
- `v452` proves the clean pair-indexed atomless existential bridge for terms and DNF: pointwise feasibility is equivalent to existence of a satisfying atomless full assignment in the carrier `BaseCell x Bool`.
- `v453` promotes the fixed bit-indexed version: the same existential bridge is Lean-checked for terms and DNF over `FullCell = Fin 8` and `BaseCell = Fin 4`.
- `v454` abstracts the bit-indexing obligation: any carrier satisfying split-index low/high/parent/side laws gets the same term and DNF existential bridge.
- `v455` promotes Claude c006: the fixed `Fin 8 -> Fin 4 -> Fin 2` two-step iterated bridge is Lean-checked for terms and DNF.
- `v456` audits v451 through the Morph sigma lens and cross-checks the explicit pointwise revision obligations with brute-force enumeration, Z3, cvc5, ESSO, and the v451 Lean receipt.
- `v457` uses Morph tactics as proof-shaping hints and proves the generic two-step composable split-index bridge for terms and DNF under the explicit middle-list agreement law `fine.baseCells = coarse.fullCells`.
- `v458` proves arbitrary finite-depth composition for homogeneous split-index stage lists using `ChainOk`, `ChainExtends`, and `projectThrough`.
- `v459` proves that the concrete `Base x Bool` product carrier satisfies the split-index interface and specializes the one-step and two-step DNF bridge receipts to that carrier.
- `v460` proves a concrete three-step heterogeneous product-carrier bridge: DNF feasibility through three product splits is equivalent to explicit stage-by-stage atomless extension witnesses, with an all-free DNF non-vacuity receipt.
- `v461` proves arbitrary finite dependent heterogeneous split-index chains: projected DNF feasibility through any finite chain is equivalent to a stage-by-stage atomless extension witness.
- `v462` proves compiler adequacy for a DNF table-expression layer with `rows`, `join`, and `project`: compiled DNF feasibility is equivalent to the direct existential expression semantics.
- `v463` proves a finite prefix-word row bridge into the DNF table-expression layer, under an explicit `PrefixWord -> Cell` path embedding and carrier-coverage premise.
- `v464` uses mathlib to prove that `Fin n x Bool` and `Fin (2*n)` have equal finite cardinality and therefore have an equivalence.
- `v465` proves the concrete arithmetic packing laws for `Fin (2*n)`: even/odd low and high children decode by parent and side, low and high do not collide, every packed cell is covered, and encode/decode are inverse.
- `v466` plugs that packed carrier into the split-index DNF projection bridge, proving packed DNF projection feasibility exactly matches existence of a satisfying atomless full assignment.
- `v467` extends the packed bridge to the finite `rows`, `join`, and `project` table-expression compiler: compiled DNF truth matches direct expression semantics for the packed project step.
- `v468` proves extended pointwise revision for partial updates: joint realisability returns old-and-new, new-only realisability returns the new relation, and unrealizable new updates fall back to the old relation.
- `v469` proves the abstract atomless splitter interface: over any mathlib Boolean algebra, having splitters for every non-bottom element is equivalent to atomlessness.
- `v470` proves the BL branching-profile core: different finite bit patterns give disjoint Boolean-algebra conjunctions, and `BL` membership is exactly non-bottom conjunction.
- `v471` bridges Claude's raw Cantor splitter proof and semantic clopen subtype proof: every nonzero semantic `Clopen` value has a semantic splitter, and arbitrary-key tables `K -> Clopen` can split a nonzero value at a chosen key.
- Claude c020 is now audited as the assembled algebraic theorem: a self-contained Lean file proves `Table K := K -> Clopen`, five set/common table laws, and `atomless_table_splitter_exists`.
- Claude c021 proves finite-prefix adequacy for Cantor clopens: `eval c` depends only on the first `depth c` stream positions.
- `c022` proves an abstract least-fixed-point completion bridge: over any complete Boolean algebra with splitters, arbitrary-key tables have pointwise countable suprema, and monotone omega-continuous recurrence has an omega-supremum fixed point.
- `c023` proves the negative carrier boundary: the full powerset of Boolean stream space does not satisfy the splitter property, because singleton stream sets cannot be split.
- `c024` proves the TABA-aligned finite semantic loop core: deterministic recurrence over a finite semantic quotient has a bounded repeated state, adjacent loops are fixed points, and non-adjacent loops can be routed to fallback without falsely reporting a fixed point.
- `c025` lifts that recurrence core to two-component mutual recurrence by treating the components as one product semantic state.
- `c026` lifts the same recurrence core to any finite family of mutually recursive semantic components, once the family has been compiled into one finite dependent-product state.
- `c027` adds the semantic schedule bridge: a finite list of component updates evaluates to a deterministic family-state transformer, absent components are preserved, and the finite loop theorem applies to the scheduled recurrence.
- `c028` adds the dependency-order certificate: when a supplied schedule is tied to a target order and dependency relation, every declared dependency of an update target is proved to occur before that target in the certified order.
- `c029` adds the prefix topological construction certificate: if every emitted node has all declared dependencies already in the emitted prefix, then the final duplicate-free order satisfies the dependency-order property.
- `c030` adds exact dependency extraction for a small formula fragment: a component reference occurs syntactically exactly when it is present in the extracted dependency list.
- `c031` connects formula-derived dependencies to prefix schedules: if the order is prefix-ready for extracted formula dependencies, every syntactic reference in a component body precedes that component in the order.
- `c032` assembles the finite toy kernel: formula-derived dependencies, certified target order, semantic schedule, and bounded scheduled recurrence are tied together in one Lean artifact.
- `c033` proves the first Boolean formula-to-update compiler: each formula body compiles to a target-preserving semantic update, and a requested order compiles to a schedule with exactly that target list.
- `c034` removes the supplied-schedule premise for the Boolean toy carrier: formula bodies compile directly into the schedule, formula references precede their targets, and the compiled recurrence has a bounded repeated state.
- `c035` generalizes the compiled recurrence kernel from Boolean component values to arbitrary Boolean-algebra values, provided the compiled family-state carrier is finite.
- `c036` models Tau's native `ft4` carrier as the four-cell Boolean algebra $\operatorname{Fin}(4)\to\mathbb{B}$, with pointwise zero, one, meet, join, prime, xor, and guarded set laws.
- `v472` promotes the positive Boolean-algebra-valued formula fragment into the main numbered lane: the fragment is monotone and omega-continuous over complete Boolean algebras, so its omega-supremum of finite approximants is a fixed point.
- `v473` adds finite positive guarded row lists over complete Boolean algebras: guarded-row evaluation is monotone and omega-continuous, and simultaneous row updates have an omega-supremum fixed point.
- `v474` adds stratified prime: prime applied to a fixed lower-stratum environment is constant with respect to the current recurrence state, so it preserves omega-continuity.
- `v475` combines finite guarded rows with stratified prime: guards and values may use positive current references plus fixed lower-stratum prime terms, and the resulting simultaneous row updates still have an omega-supremum fixed point.
- `v476` proves priority-row normalization for fixed guards: priority evaluation is equal to guarded-join evaluation of a disjointized normal form.
- `v477` proves the safe priority recurrence fragment: fixed-guard priority rows whose values use positive current references plus lower-stratum prime are omega-continuous and have an omega-supremum fixed point.
- `v479` generalizes fixed priority guards to lower-stratum guard expressions: guards may read fixed lower-stratum data and lower-stratum prime, but still cannot read the current recursive state.
- `v480` connects the lower-stratum priority fragment back to the normal-form
  theorem: after materializing guards and row values, lower-stratum priority
  rows normalize to disjoint guarded joins.
- `v481` adds a restricted table syntax compiler: priority rows plus an explicit default compile into the lower-stratum priority kernel, preserve semantics, and retain omega-continuity.
- `v484` adds a narrow TABA `CBF` syntax-and-denotation bridge: recursive if-then-else expressions over pointwise Boolean functions compile to ordinary Boolean functions by guarded-choice expansion.
- `v485` lifts the narrow `CBF` bridge to arbitrary Boolean algebras: a conditional expression denotes as guard meet then-branch, joined with guard-prime meet else-branch.
- `v486` proves recurrence safety for CBF-bearing positive value terms when conditional guards read only fixed lower-stratum data.
- `v487` integrates the safe CBF fragment into the restricted table compiler: row values and defaults may contain safe conditionals, while compiler semantics and omega-continuity are preserved.
- `v488` proves the obstruction for arbitrary current-state conditional guards: `if ref then false else true` encodes complement and is not monotone.
- `v489` proves a first recovery theorem over the two-point Boolean carrier: current-state conditionals are monotone when the guard and both branches are monotone and the else branch is pointwise below the then branch.
- `v490` abstracts that recovery theorem to arbitrary source and target relations with a transitive target order.
- `v491` proves that branch-ordered monotonicity is still not enough for recurrence, because a monotone guard can fail at an omega-limit.
- `v492` proves the corresponding positive Boolean single-chain theorem: explicit guard and branch supremum preservation restores conditional supremum preservation.
- `v493` lifts v492 from Boolean branch values to ordered branch values with an abstract sequence-supremum operator.
- `v494` proves the algebraic normalization for Boolean-algebra-valued guards: under branch ordering, the guard-prime side of guarded choice can be eliminated.
- `v495` proves the recurrence-shaped pointwise theorem for BA-valued current guards under explicit branch-order and omega-union preservation assumptions.
- `v496` proves the bounded finite splitter-tree expansion that follows c051: recursively splitting by a finite list of splitters and joining all leaves recovers the original element.
- `v497` makes the bounded splitter tree explicit as dyadic leaves: a finite splitter list generates $2^n$ leaves, and joining those leaves recovers the original element.
- `v498` supplies the abstract infinite-table completion layer: if the value carrier has bottom, order, countable suprema, and least-upper-bound laws, then $K\to A$ tables inherit those semantics pointwise, and monotone omega-continuous table updates have a Kleene fixed point.
- `v499` adds the splitter half of that same abstract layer: if the value carrier also splits every non-bottom value, then every non-bottom table has a non-bottom split while retaining the v498 fixed-point semantics. The live-key extraction is classical existence, not executable search.
- `v500` starts the concrete positive prefix-open lane: every binary prefix cylinder is the disjoint nonempty union of its false-child and true-child cylinders.
- `v501` lifts that basis move to arbitrary prefix-open regions in the positive sense: every nonempty prefix-open region contains two nonempty disjoint prefix-open subregions. This is refinement, not a covering partition.
- `v502` proves countable-union closure for prefix-open regions, giving the positive lane an explicit omega-supremum construction by existential union of finite-word generators.
- `v503` sharpens the finite QE boundary: finite masks plus finitely many same-polarity hit constraints eliminate to restricted nonzero checks in any Boolean algebra, so atomlessness is not needed until a formula forces a genuine split between $x$ and $x'$.
- `v504` proves the first narrow mixed-polarity QE rule: one positive hit plus one complement hit eliminates under an abstract non-bottom splitter interface.
- `v505` turns the v504 mixed-polarity proof into an induction-ready extension lemma: one more positive hit can be added while preserving one complement-hit residual.
- `v506` proves the first finite-list mixed-polarity theorem: finite positive-hit lists plus one complement-hit target eliminate under the splitter interface.
- `c059` proves the concrete finite-support Cantor clopen carrier: Boolean operations are extensionally sound, values are determined by finite prefixes, and every nonzero clopen has a nonzero proper split.
- `c060` quotients finite-support Cantor clopens by extensional equality and proves that the quotient carries a Lean `BooleanAlgebra` instance whose operations agree with pointwise stream-predicate evaluation.
- `v507` promotes the c060 quotient carrier into the main numbered workflow: `QClopen` is now a checked mathlib `BooleanAlgebra` receipt owned by the local proof-search lane, with canonical equality, formula integration, recurrence, NSO, Guarded Successor, and Tau lowering still outside scope.
- `v508` proves the first concrete formula/QE integration receipt: the c056 mask-plus-hit and finite-mask-list QE rules instantiate on `QClopen` using the v507 Boolean-algebra instance.
- `v509` adds the concrete non-bottom splitter receipt for `QClopen` and instantiates the first mixed-polarity atomless QE rule with one positive hit and one complement hit.
- `v510` extends the same concrete mixed-polarity lane to one positive hit and a finite list of complement-hit targets by shrinking witnesses under a strengthened mask.
- `v511` combines finite positive-hit lists and finite complement-hit lists in one checked mixed-polarity QE theorem over `QClopen`.
- `v512` adds a finite literal-conjunction driver: `miss`, `hit`, and `cohit` literals normalize to the v511 theorem.
- `v513` proves decidable equality for `QClopen` by finite truth-table comparison at maximum representative support depth.
- `v514` adds a recursive positive formula driver: literals, conjunction, and disjunction compile to finite DNF clauses discharged by the v512/v511 QE path.
- `v515` adds a bounded witness-list layer: finite candidate witnesses can be checked by applying the v514 DNF QE theorem to each listed positive-formula body.
- `v516` internalizes the finite witness-list layer as a bounded positive-formula constructor `existsW`, which compiles by finite disjunction into the same DNF/QE kernel.
- `v517` promotes the direct recursive splitter partition: the partition covers top, has $2^n$ cells, and gives forward domination under explicit non-bottom-witness and cell-constancy assumptions.
- `v518` replaces global cell constancy with a sharper local theorem: unary Boolean terms are stable on cells covered by the witness, yielding domination for cell-aligned witnesses.
- `v519` isolates the constants-only Boolean expression fragment where cell constancy is automatically preserved, and proves identity is not cell-constant on a coarse top-only partition.
- `v520` proves finite cell-union witnesses are cell-aligned under an explicit nonzero-overlap separation assumption, so v518 domination applies to finite unions of whole cells.
- `v521` proves the direct-recursive `splitPartition` is overlap-separating, removing the extra separation assumption from the finite cell-union domination theorem for `splitPartition` cells.
- `v522` builds a Boolean-closed witness-expression fragment from finite cell unions using bottom, top, prime, meet, and join, and proves every well-formed witness expression is cell-aligned.
- `v523` lifts cell alignment to tables: empty, set, standalone select, pointwise join, pointwise meet, pointwise prime, and the current table-expression grammar preserve entrywise alignment.
- `v524` adds a recurrence-body grammar with a current-state variable and proves every finite approximant from the empty table remains table-aligned.

### 4.0 Current concrete carrier proof artifact

The current concrete-carrier result is:

$$
Q_{\mathrm{clop}}
:=
\operatorname{Clopen}_{\mathrm{fin}}(2^{\mathbb{N}})/{\equiv},
\qquad
c\equiv d
\Longleftrightarrow
\forall s\in 2^{\mathbb{N}},\ c(s)=d(s).
$$

Standard reading:

- $Q_{\mathrm{clop}}$ is the quotient of finite-support clopen Boolean-stream predicates by extensional equality. Two representatives are identified exactly when they return the same Boolean value on every infinite Boolean stream.

Plain English reading:

- The carrier ignores the particular finite decision tree used to describe a clopen region. It keeps only the region's meaning as a subset of Boolean stream space.

The checked c060 operation receipts include:

$$
\operatorname{eval}(a\wedge b)
=
\operatorname{eval}(a)\wedge\operatorname{eval}(b),
\qquad
\operatorname{eval}(a')
=
\operatorname{eval}(a)'.
$$

Standard reading:

- Evaluation of the meet of two quotient clopens is pointwise equal to the meet of their evaluations. Evaluation of the prime of a quotient clopen is pointwise equal to the prime of its evaluation.

Plain English reading:

- Meet and prime are not merely syntactic operations on representatives. They preserve the intended region semantics after quotienting.

The Lean receipt is:

$$
\operatorname{BooleanAlgebra}(Q_{\mathrm{clop}}).
$$

Standard reading:

- The quotient carrier $Q_{\mathrm{clop}}$ satisfies Lean's Boolean-algebra typeclass laws.

Plain English reading:

- After quotienting by same-region equality, finite-support Cantor clopens are a genuine Boolean algebra in the proof assistant.

The recurrence scope remains conditional:

$$
\exists N.\ F^{N+1}(\bot)=F^N(\bot)
\Longrightarrow
\mu F=F^N(\bot).
$$

Standard reading:

- If the finite approximant sequence generated by $F$ stabilizes at some finite stage $N$, then the least fixed point is the stabilized value $F^N(\bot)$.

Plain English reading:

- The clopen carrier is enough for recurrence when the recurrence reaches a finite stable clopen. It is not, by itself, a countable-supremum completion for arbitrary omega-limits.

Boundary:

- c060 solves the quotient Boolean-algebra carrier step for finite-support Cantor clopens.
- c060 does not prove decidable canonical normalization or executable equality.
- c060 is not yet plugged into the c045-c058 formula and QE pipeline.
- c060 does not prove full TABA recurrence, NSO, Guarded Successor, or Tau lowering.

The first concrete formula/QE integration receipt is:

$$
\exists x\in Q_{\mathrm{clop}}.\,
x\wedge m=\bot
\wedge
x\wedge h\ne\bot
\Longleftrightarrow
m'\wedge h\ne\bot.
$$

Standard reading:

- There exists a quotient clopen $x$ that misses mask $m$ and hits target $h$ if and only if the part of $h$ outside $m$ is nonempty.

Plain English reading:

- A mask can be avoided while still hitting the target exactly when the target has some live region outside the mask.

The finite-mask-list version is:

$$
\exists x\in Q_{\mathrm{clop}}.\,
\left(\forall m\in M,\ x\wedge m=\bot\right)
\wedge
x\wedge h\ne\bot
\Longleftrightarrow
\left(\bigvee M\right)'\wedge h\ne\bot.
$$

Standard reading:

- There exists a quotient clopen $x$ that misses every mask in the finite list $M$ and hits $h$ if and only if $h$ has a nonempty part outside the join of all masks in $M$.

Boundary:

- v508 is a Boolean-algebra QE integration receipt.
- v508 does not use atomlessness.
- v508 does not prove mixed-polarity splitter QE, recurrence, NSO, Guarded Successor, or Tau lowering.

The first concrete atomless-style QE integration receipt is:

$$
\exists x\in Q_{\mathrm{clop}}.\,
x\wedge m=\bot
\wedge
x\wedge h\ne\bot
\wedge
x'\wedge c\ne\bot
\Longleftrightarrow
\left(m'\wedge h\ne\bot\right)\wedge\left(c\ne\bot\right).
$$

Standard reading:

- There exists a quotient clopen $x$ that misses mask $m$, hits $h$, and whose prime hits $c$, if and only if $h$ has a nonempty part outside $m$ and $c$ itself is nonempty.

Plain English reading:

- If the positive target has live room outside the mask, and the complement target is live at all, the atomless splitter lets $x$ take one live piece while leaving another live piece for $x'$.

The splitter receipt behind that rule is:

$$
a\ne\bot
\Longrightarrow
\exists l,r\in Q_{\mathrm{clop}}.\,
l\ne\bot
\wedge
r\ne\bot
\wedge
l\wedge r=\bot
\wedge
l\vee r=a.
$$

Standard reading:

- Every non-bottom quotient clopen has two non-bottom disjoint quotient-clopen subregions whose join is the original region.

Boundary:

- v509 covers one positive hit and one complement hit.
- v509 does not cover finite complement-hit lists.
- v509 does not prove full formula grammar recursion, recurrence, NSO, Guarded Successor, or Tau lowering.

The finite complement-hit extension is:

$$
\exists x\in Q_{\mathrm{clop}}.\,
x\wedge m=\bot
\wedge
x\wedge h\ne\bot
\wedge
\left(\forall c\in C,\ x'\wedge c\ne\bot\right)
\Longleftrightarrow
\left(m'\wedge h\ne\bot\right)
\wedge
\left(\forall c\in C,\ c\ne\bot\right).
$$

Standard reading:

- There exists a quotient clopen $x$ that misses mask $m$, hits $h$, and whose prime hits every element of the finite list $C$, if and only if $h$ has a nonempty part outside $m$, and every element of $C$ is non-bottom.

Plain English reading:

- A finite list of complement-side targets adds only finite nonzeroness checks, provided there is still a live positive region outside the mask. The atomless splitter supplies enough room to keep shrinking the witness without destroying the positive hit.

The proof-critical shrink law is:

$$
y\wedge(m\vee x')=\bot
\Longrightarrow
y\le x.
$$

Standard reading:

- If $y$ is disjoint from the join of $m$ and $x'$, then $y$ is below $x$.

Plain English reading:

- Strengthening the mask by adding $x'$ forces the next witness to live inside the old witness.

The preservation law is:

$$
y\le x
\wedge
x'\wedge c\ne\bot
\Longrightarrow
y'\wedge c\ne\bot.
$$

Standard reading:

- If $y$ is below $x$, and the prime of $x$ has nonempty meet with $c$, then the prime of $y$ has nonempty meet with $c$.

Plain English reading:

- Shrinking $x$ cannot erase complement-side hits already achieved by $x'$, because $y'$ contains at least everything that $x'$ contained.

Boundary:

- v510 covers one positive hit and finitely many complement hits.
- v510 does not combine finite positive-hit lists with finite complement-hit lists.
- v510 does not prove full formula grammar recursion, recurrence, NSO, Guarded Successor, or Tau lowering.

The finite two-sided mixed-hit theorem is:

$$
\exists x\in Q_{\mathrm{clop}}.\,
x\wedge m=\bot
\wedge
\left(\forall h\in H,\ x\wedge h\ne\bot\right)
\wedge
\left(\forall c\in C,\ x'\wedge c\ne\bot\right)
\Longleftrightarrow
\left(\forall h\in H,\ m'\wedge h\ne\bot\right)
\wedge
\left(\forall c\in C,\ c\ne\bot\right).
$$

Standard reading:

- There exists a quotient clopen $x$ that misses mask $m$, hits every element of the finite list $H$, and whose prime hits every element of the finite list $C$, if and only if every $h\in H$ has a nonempty part outside $m$, and every $c\in C$ is non-bottom.

Plain English reading:

- For finite mixed hit constraints, all positive targets must have live space outside the mask, and all complement targets must be live at all. Under the atomless `QClopen` carrier, those checks are enough.

The growth step used by the proof is:

$$
\left(\forall c\in C,\ x'\wedge c\ne\bot\right)
\wedge
m'\wedge h\ne\bot
\Longrightarrow
\exists y.\,
x\le y
\wedge
y\wedge m=\bot
\wedge
y\wedge h\ne\bot
\wedge
\left(\forall c\in C,\ y'\wedge c\ne\bot\right).
$$

Standard reading:

- If $x$ already leaves every complement target in $C$ visible to $x'$, and $h$ has nonempty overlap with $m'$, then there is an extension $y$ above $x$ that still misses $m$, hits $h$, and leaves every complement target visible to $y'$.

Plain English reading:

- Positive hits can be added one at a time without consuming the finite complement-side reserve.

Boundary:

- v511 is a theorem-level finite mixed-hit QE receipt.
- v511 still does not provide a formula-normalization driver.
- v511 does not prove recurrence, NSO, Guarded Successor, or Tau lowering.

The finite literal-normalization receipt is:

$$
\exists x\in Q_{\mathrm{clop}}.\,
\forall \ell\in L,\ \operatorname{Sem}(x,\ell)
\Longleftrightarrow
\left(
\forall h\in \operatorname{Hits}(L),\
\left(\bigvee \operatorname{Masks}(L)\right)'\wedge h\ne\bot
\right)
\wedge
\left(
\forall c\in \operatorname{Cohits}(L),\
c\ne\bot
\right).
$$

Standard reading:

- There exists a quotient clopen $x$ satisfying every literal in the finite list $L$, if and only if every normalized hit has nonempty overlap with the prime of the joined normalized masks, and every normalized cohit is non-bottom.

Plain English reading:

- A finite conjunction of mask-avoidance, positive-hit, and complement-hit literals can be compiled to the v511 normal form exactly.

Boundary:

- v512 covers finite conjunctions of `miss`, `hit`, and `cohit` literals.
- v512 does not cover nested formula recursion, disjunction, negation normalization, recurrence, NSO, Guarded Successor, or Tau lowering.

The decidable-equality receipt is:

$$
c\equiv d
\Longleftrightarrow
\forall b:\operatorname{Fin}(\max(\operatorname{depth}(c),\operatorname{depth}(d)))\to\mathbb{B},\
c(\operatorname{extend}(b))=d(\operatorname{extend}(b)).
$$

Standard reading:

- Two finite-support clopen representatives are extensionally equal if and only if they agree on every finite bit-pattern up to their shared maximum support depth.

Plain English reading:

- Equality of quotient clopens is a finite truth-table check, because each representative only reads finitely many stream positions.

Boundary:

- v513 proves decidable equality, not canonical normalization.
- The check is finite but exponential in support depth.
- v513 does not prove recurrence, NSO, Guarded Successor, or Tau lowering.

The positive formula DNF receipt is:

$$
\exists x\in Q_{\mathrm{clop}}.\,
\operatorname{Holds}(x,\varphi)
\Longleftrightarrow
\exists C\in\operatorname{DNF}(\varphi).\,
\operatorname{QFree}(C).
$$

Standard reading:

- There exists a quotient clopen $x$ satisfying the positive formula $\varphi$, if and only if there exists a clause $C$ in the DNF compilation of $\varphi$ whose quantifier-free v512 condition holds.

Plain English reading:

- Positive formulas made from literals, conjunction, and disjunction can be reduced to finite literal clauses, and each clause is already handled by the mixed-hit QE theorem.

Boundary:

- v514 covers positive formulas only.
- v514 does not normalize negation or quantifiers.
- v514 does not prove recurrence, NSO, Guarded Successor, or Tau lowering.

The bounded witness-list receipt is:

$$
\exists w\in W.\ \exists x:Q_{\mathrm{clop}}.\,
\operatorname{Holds}(x,\operatorname{Body}(w))
\Longleftrightarrow
\exists w\in W.\ \exists C\in\operatorname{DNF}(\operatorname{Body}(w)).\,
\operatorname{QFree}(C).
$$

Standard reading:

- For a finite witness list $W$ and a body assigning each witness $w$ a positive formula over $Q_{\mathrm{clop}}$, there exists a listed witness $w$ and a quotient clopen $x$ satisfying $\operatorname{Body}(w)$, if and only if there exists a listed witness $w$ and a clause $C$ in the DNF compilation of $\operatorname{Body}(w)$ whose quantifier-free v514 condition holds.

Plain English reading:

- A finite menu of candidate witnesses can be pushed outside the formula. Each candidate is checked by the same DNF-based QClopen test already proved in v514.

Boundary:

- v515 is witness-list-relative.
- v515 does not prove unbounded quantifier elimination.
- v515 does not introduce variable-binding syntax.
- v515 does not prove negation normalization, recurrence, NSO, Guarded Successor, or Tau lowering.

The bounded-existential syntax receipt is:

$$
\exists x:Q_{\mathrm{clop}}.\,
\operatorname{BHolds}(x,\Phi)
\Longleftrightarrow
\exists C\in\operatorname{BDNF}(\Phi).\,
\operatorname{QFree}(C).
$$

Standard reading:

- There exists a quotient clopen $x$ satisfying the bounded positive formula $\Phi$, if and only if there exists a clause $C$ in the bounded-DNF compilation of $\Phi$ whose quantifier-free mixed-QE condition holds.

Plain English reading:

- Positive formulas may now include finite witness-list nodes. Such a node is compiled as a finite disjunction over the listed witnesses, and the resulting clauses are checked by the existing QClopen QE kernel.

Boundary:

- v516's `existsW` constructor ranges only over an explicit finite list.
- v516 does not prove unbounded quantifier elimination.
- v516 does not model general first-order variable binding.
- v516 does not prove negation normalization, recurrence, NSO, Guarded Successor, or Tau lowering.

The direct splitter-partition receipt is:

$$
\bigvee \operatorname{SplitPart}(v_1,\ldots,v_n)
=
\top,
\qquad
\left|\operatorname{SplitPart}(v_1,\ldots,v_n)\right|
=
2^n.
$$

Standard reading:

- The join of all cells generated by recursively splitting on $v_1,\ldots,v_n$ is top, and the generated list has $2^n$ cells.

The conditional forward-domination receipt is:

$$
\operatorname{CellConst}(f,\operatorname{SplitPart}(V))
\wedge
\exists x.\ x\neq\bot\wedge f(x)=\top
\Longrightarrow
\exists c\in\operatorname{SplitPart}(V).\ f(c)\wedge c\neq\bot.
$$

Standard reading:

- If $f$ is constant on every cell of the splitter partition, and if some non-bottom $x$ satisfies $f(x)=\top$, then there exists a partition cell $c$ such that $f(c)\wedge c$ is non-bottom.

Plain English reading:

- A nonzero satisfying witness cannot disappear between the partition cells. If the predicate does not change inside each cell, then one finite cell already carries a nonzero satisfying witness.

Boundary:

- v517 assumes cell-constancy. It does not prove that the target TABA formulas are cell-constant.
- v517 assumes a non-bottom satisfying witness. This matters because the unscoped theorem is false if bottom itself satisfies the predicate.
- v517 does not prove full NSO domination, recurrence, Guarded Successor, or Tau lowering.

The cell-aligned locality receipt is:

$$
x\wedge c=c
\Longrightarrow
\operatorname{Eval}(x,t)\wedge c
=
\operatorname{Eval}(c,t)\wedge c.
$$

Standard reading:

- If witness $x$ covers cell $c$, then evaluating unary Boolean term $t$ at $x$ and evaluating $t$ at $c$ give the same result inside $c$.

The corresponding domination receipt is:

$$
\exists x.\ x\neq\bot
\wedge
\operatorname{CellAligned}(x,\operatorname{SplitPart}(V))
\wedge
\operatorname{Eval}(x,t)=\top
\Longrightarrow
\exists c\in\operatorname{SplitPart}(V).\,
\operatorname{Eval}(c,t)\wedge c\neq\bot.
$$

Standard reading:

- If there exists a non-bottom witness $x$ that is a union of whole splitter cells and $t$ evaluates to top at $x$, then some splitter cell $c$ has non-bottom local satisfaction for $t$.

Plain English reading:

- A finite partition can replace a witness only when the witness is made out of whole partition cells. A witness that merely overlaps a cell partially is not enough.

Boundary:

- v518 does not cover arbitrary witnesses.
- v518 does not prove that all TABA or NSO witnesses are cell-aligned.
- v518 does not decide whether the runtime should enumerate cells or finite unions of cells.
- v518 does not prove recurrence, Guarded Successor, or Tau lowering.

The cell-constant algebra receipt is:

$$
\operatorname{CellConst}(f,P)
\wedge
\operatorname{CellConst}(g,P)
\Longrightarrow
\operatorname{CellConst}(x\mapsto f(x)\wedge g(x),P),
$$

$$
\operatorname{CellConst}(f,P)
\wedge
\operatorname{CellConst}(g,P)
\Longrightarrow
\operatorname{CellConst}(x\mapsto f(x)\vee g(x),P),
$$

$$
\operatorname{CellConst}(f,P)
\Longrightarrow
\operatorname{CellConst}(x\mapsto f(x)',P).
$$

The constants-only expression grammar is:

$$
e ::= k \mid e' \mid e_1\wedge e_2 \mid e_1\vee e_2.
$$

The checked fragment theorem is:

$$
\forall e.\,
\operatorname{CellConst}
\bigl(\operatorname{Eval}(e),\operatorname{SplitPart}(V)\bigr).
$$

Standard reading:

- Cell-constant functions are closed under meet, join, and prime. Therefore every expression built from Boolean constants by those operations is cell-constant on the splitter partition.

Plain English reading:

- If an expression never inspects the quantified witness, then it cannot vary inside a partition cell because of that witness. The strong v517 cell-constancy premise is valid for this constants-only fragment.

The boundary receipt is:

$$
\neg\operatorname{CellConst}(x\mapsto x,[\top])
$$

over the concrete Boolean algebra $\operatorname{Fin}(2)\to\operatorname{Bool}$.

Standard reading:

- It is not the case that the identity function is cell-constant on the one-cell partition whose only cell is top.

Plain English reading:

- A function that returns the witness itself can distinguish two different points inside the same coarse cell. So global cell constancy is too strong for witness-dependent syntax.

Boundary:

- v519 covers the constants-only Boolean expression fragment.
- v519 does not cover expressions that inspect the witness.
- v519 does not prove arbitrary-witness domination, recurrence, Guarded Successor, full TABA tables, or Tau lowering.

The finite cell-union witness receipt is:

$$
\operatorname{OverlapSep}(P)
\wedge
\operatorname{Selected}\subseteq P
\Longrightarrow
\operatorname{CellAligned}
\bigl(\bigvee \operatorname{Selected},P\bigr).
$$

Standard reading:

- If partition $P$ has the property that any two cells with nonzero overlap are equal, and every selected element is a cell of $P$, then the join of the selected cells is cell-aligned with $P$.

The domination receipt is:

$$
\operatorname{OverlapSep}(\operatorname{SplitPart}(V))
\wedge
\operatorname{Selected}\subseteq \operatorname{SplitPart}(V)
\wedge
\bigvee\operatorname{Selected}\neq\bot
\wedge
\operatorname{Eval}\bigl(\bigvee\operatorname{Selected},t\bigr)=\top
$$

$$
\Longrightarrow
\exists c\in\operatorname{SplitPart}(V).\,
\operatorname{Eval}(c,t)\wedge c\neq\bot.
$$

Standard reading:

- If a non-bottom finite union of selected partition cells satisfies unary term $t$, then some single partition cell has non-bottom local satisfaction for $t$, provided the partition is overlap-separating.

Plain English reading:

- A finite union of whole cells is a safe witness shape. It does not cut through a cell, so the local v518 theorem can reduce the finite union to one cell that carries the certificate.

Boundary:

- v520 assumes overlap separation for the partition.
- v520 does not yet prove that `splitPartition` is always overlap-separating.
- v520 does not prove that arbitrary TABA or NSO witnesses compile to finite cell unions.
- v520 does not prove recurrence, Guarded Successor, full TABA tables, or Tau lowering.

The split-partition separation receipt is:

$$
c\in\operatorname{SplitPart}(V)
\wedge
d\in\operatorname{SplitPart}(V)
\wedge
c\wedge d\neq\bot
\Longrightarrow
c=d.
$$

Standard reading:

- If $c$ and $d$ are both cells generated by $\operatorname{SplitPart}(V)$, and their meet is non-bottom, then $c$ and $d$ are the same cell.

Plain English reading:

- The direct-recursive splitter partition really behaves like a partition. Different generated cells do not share a nonzero region.

The cleaned finite cell-union domination theorem is:

$$
\operatorname{Selected}\subseteq \operatorname{SplitPart}(V)
\wedge
\bigvee\operatorname{Selected}\neq\bot
\wedge
\operatorname{Eval}\bigl(\bigvee\operatorname{Selected},t\bigr)=\top
$$

$$
\Longrightarrow
\exists c\in\operatorname{SplitPart}(V).\,
\operatorname{Eval}(c,t)\wedge c\neq\bot.
$$

Standard reading:

- If the selected witness is a non-bottom finite union of cells from $\operatorname{SplitPart}(V)$, and unary term $t$ evaluates to top at that witness, then some generated cell $c$ has non-bottom local satisfaction for $t$.

Plain English reading:

- Once the witness is known to be a finite union of generated cells, the search can reduce that witness to one generated cell that still carries the local certificate.

Boundary:

- v521 proves separation for `splitPartition`.
- v521 still assumes the witness is a finite union of `splitPartition` cells.
- v521 does not prove that arbitrary TABA or NSO witnesses have this finite-union shape.
- v521 does not prove recurrence, Guarded Successor, full TABA tables, or Tau lowering.

The aligned witness-expression grammar is:

$$
w ::=
\bot
\mid \top
\mid \operatorname{cellUnion}(S)
\mid w'
\mid w_1\wedge w_2
\mid w_1\vee w_2.
$$

Standard reading:

- A witness expression is built from bottom, top, a finite union of selected cells, prime, meet, and join.

The well-formedness condition is:

$$
\operatorname{WF}_{\operatorname{SplitPart}(V)}(\operatorname{cellUnion}(S))
\quad\Longleftrightarrow\quad
S\subseteq \operatorname{SplitPart}(V),
$$

with the obvious recursive clauses for prime, meet, and join.

Standard reading:

- A cell-union expression is well formed exactly when every selected cell belongs to the generated split partition. The compound cases are well formed when their subexpressions are well formed.

The closure receipt is:

$$
\operatorname{WF}_{\operatorname{SplitPart}(V)}(w)
\Longrightarrow
\operatorname{CellAligned}
\bigl(\llbracket w\rrbracket,\operatorname{SplitPart}(V)\bigr).
$$

Standard reading:

- If witness expression $w$ is well formed over $\operatorname{SplitPart}(V)$, then its denotation is cell-aligned with $\operatorname{SplitPart}(V)$.

Plain English reading:

- This witness language cannot cut through generated cells. It starts from whole generated cells and uses Boolean operations that preserve the property of being made from whole cells.

The domination receipt is:

$$
\operatorname{WF}_{\operatorname{SplitPart}(V)}(w)
\wedge
\llbracket w\rrbracket\neq\bot
\wedge
\operatorname{Eval}(\llbracket w\rrbracket,t)=\top
$$

$$
\Longrightarrow
\exists c\in\operatorname{SplitPart}(V).\,
\operatorname{Eval}(c,t)\wedge c\neq\bot.
$$

Standard reading:

- If a well-formed aligned witness expression denotes a non-bottom witness and unary term $t$ evaluates to top at that witness, then some generated cell $c$ has non-bottom local satisfaction for $t$.

Plain English reading:

- The search target is now a small witness language, not only a raw list of selected cells. If a satisfying witness can be compiled into this language, one generated cell is enough to expose the certificate.

Boundary:

- v522 proves a safe witness-expression fragment.
- v522 does not prove that arbitrary TABA or NSO witnesses compile into that fragment.
- v522 does not prove recurrence, Guarded Successor, full TABA tables, or Tau lowering.

The table-alignment invariant is:

$$
\operatorname{TableAligned}(P,T)
\quad:\Longleftrightarrow\quad
\forall k.\,\operatorname{CellAligned}(T(k),P).
$$

Standard reading:

- Table $T$ is aligned with partition $P$ exactly when every entry $T(k)$ is cell-aligned with $P$.

The checked pointwise operation laws include:

$$
\operatorname{TableAligned}(P,T)
\wedge
\operatorname{CellAligned}(a,P)
\Longrightarrow
\operatorname{TableAligned}(P,\operatorname{set}(T,k,a)),
$$

$$
\operatorname{TableAligned}(P,T)
\Longrightarrow
\operatorname{TableAligned}(P,\operatorname{select}_{\varphi}(T)),
$$

$$
\operatorname{TableAligned}(P,T)
\wedge
\operatorname{TableAligned}(P,U)
\Longrightarrow
\operatorname{TableAligned}(P,T\vee U),
$$

$$
\operatorname{TableAligned}(P,T)
\wedge
\operatorname{TableAligned}(P,U)
\Longrightarrow
\operatorname{TableAligned}(P,T\wedge U),
$$

$$
\operatorname{TableAligned}(P,T)
\Longrightarrow
\operatorname{TableAligned}(P,T').
$$

Standard reading:

- Setting an aligned value, selecting entries, joining tables pointwise, meeting tables pointwise, and taking pointwise prime all preserve table alignment.

Plain English reading:

- Alignment is stable entry by entry. If a table is built from aligned regions using these pointwise operations, the table does not introduce a region that cuts through the generated partition.

Boundary:

- v523 proves select preservation as a standalone theorem.
- v523's current table-expression grammar does not include select.
- v523 assumes base tables and inserted values are already aligned.
- v523 does not prove recurrence, Guarded Successor, full TABA tables, or Tau lowering.

The finite recurrence grammar is:

$$
r ::=
\operatorname{var}
\mid \operatorname{empty}
\mid \operatorname{base}(T)
\mid \operatorname{set}(r,k,a)
\mid r_1\vee r_2
\mid r_1\wedge r_2
\mid r'.
$$

Standard reading:

- A recurrence body is built from the current-state variable, the empty table, a base table, a set update, pointwise join, pointwise meet, and pointwise prime.

The one-step preservation law is:

$$
\operatorname{WF}_P(r)
\wedge
\operatorname{TableAligned}(P,S)
\Longrightarrow
\operatorname{TableAligned}(P,\llbracket r\rrbracket_S).
$$

Standard reading:

- If recurrence body $r$ is well formed over partition $P$, and the current state $S$ is table-aligned with $P$, then evaluating $r$ in state $S$ produces another table-aligned state.

The finite-approximant law is:

$$
S_0=\operatorname{empty},
\qquad
S_{n+1}=\llbracket r\rrbracket_{S_n},
\qquad
\operatorname{WF}_P(r)
\Longrightarrow
\forall n.\,\operatorname{TableAligned}(P,S_n).
$$

Standard reading:

- Starting from the empty table and repeatedly applying a well-formed recurrence body, every finite approximant $S_n$ is table-aligned.

Plain English reading:

- The scoped recurrence body cannot break the partition discipline at any finite step. The limit is not solved here, but every checked finite stage remains inside the safe table lane.

Boundary:

- v524 proves finite approximant preservation, not least-fixed-point existence or equality.
- v524 does not prove a stabilization bound.
- v524 does not include select inside the recurrence grammar.
- v524 does not prove Guarded Successor, full TABA tables, or Tau lowering.

### 4.1 Narrow CBF proof artifact

The term `CBF` has a local TABA meaning in this research line. It is not the
same thing as every Boolean-function class in the broader literature whose
members satisfy some condition.

The checked v484 grammar is:

$$
\mathrm{CBF}_{X}
::=
\operatorname{leaf}(f)
\mid
\operatorname{cond}(\varphi,t,e),
\qquad
f,\varphi:X\to\mathbb{B}.
$$

Standard reading:

- A conditional Boolean function over a point space $X$ is either a Boolean-function leaf, or a conditional node with a Boolean guard and two conditional Boolean-function branches.

Plain English reading:

- A `CBF` is a recursive if-then-else syntax tree whose leaves and guards are ordinary Boolean functions over the same point space.

The denotation is:

$$
\llbracket \operatorname{cond}(\varphi,t,e)\rrbracket(x)
=
\begin{cases}
\llbracket t\rrbracket(x), & \varphi(x)=\top,\\
\llbracket e\rrbracket(x), & \varphi(x)=\bot.
\end{cases}
$$

Standard reading:

- At point $x$, evaluate the guard $\varphi(x)$. If it is true, return the denotation of the then branch at $x$. If it is false, return the denotation of the else branch at $x$.

The guarded-choice expansion is:

$$
\operatorname{guardedChoice}(\varphi,t,e)(x)
=
(\varphi(x)\wedge t(x))
\vee
(\neg\varphi(x)\wedge e(x)).
$$

Standard reading:

- The value at $x$ is the join of two guarded contributions: the then value guarded by $\varphi(x)$, and the else value guarded by the negation of $\varphi(x)$.

Plain English reading:

- The guard partitions the point $x$ into exactly one active branch. The formula writes the same if-then-else decision as Boolean algebra.

The checked compiler receipt is:

$$
\operatorname{compile}(c)=\llbracket c\rrbracket.
$$

Standard reading:

- For every narrow `CBF` expression $c$, the compiled ordinary Boolean function is extensionally equal to the recursive denotation of $c$.

Boundary:

- v484 does not prove NSO.
- v484 does not prove recurrence safety for conditionals.
- v484 does not integrate `CBF` into the v481 table syntax yet.
- v484 does not lower `CBF` to Tau runtime behavior.

The v485 generalization moves the same equation from pointwise Boolean
functions to arbitrary Boolean algebras:

$$
\llbracket \operatorname{cond}(\varphi,t,e)\rrbracket
=
(\varphi\wedge \llbracket t\rrbracket)
\vee
(\varphi'\wedge \llbracket e\rrbracket).
$$

Standard reading:

- The denotation of a conditional node is the join of the then-branch denotation restricted by the guard and the else-branch denotation restricted by the guard prime.

Plain English reading:

- A conditional Boolean-algebra expression is a guarded merge. The guard selects the part of the carrier where the then branch applies, and the guard prime selects the part where the else branch applies.

The checked Boolean-algebra receipt is:

$$
\operatorname{compile}_{\mathrm{BA}}(c)=\llbracket c\rrbracket_{\mathrm{BA}}.
$$

Standard reading:

- For every narrow Boolean-algebra-valued `CBF` expression $c$, the compiled Boolean-algebra element equals the recursive denotation of $c$.

Boundary:

- v485 is still expression denotation.
- v485 does not prove omega-continuity for CBF-bearing recursive bodies.
- v485 does not integrate `CBF` into the v481 restricted table compiler.

The v486 recurrence-safe fragment is:

$$
\begin{aligned}
g &\in \mathrm{Guard}_{\mathrm{lower}},\\
t,e &\in \mathrm{Value}_{+},\\
\operatorname{cond}(g,t,e)
&\in \mathrm{Value}_{+}^{\mathrm{CBF}}.
\end{aligned}
$$

Standard reading:

- If the guard $g$ is a lower-stratum guard, and both branches $t$ and $e$ are positive value terms, then the conditional expression is admitted as a CBF-bearing positive value term.

The guarded value equation is:

$$
\llbracket \operatorname{cond}(g,t,e)\rrbracket_{\rho,s}
=
\bigl(\llbracket g\rrbracket_{\rho}\wedge
  \llbracket t\rrbracket_{\rho,s}\bigr)
\vee
\bigl(\llbracket g\rrbracket_{\rho}'\wedge
  \llbracket e\rrbracket_{\rho,s}\bigr).
$$

Standard reading:

- In lower environment $\rho$ and current state $s$, the conditional value is the guarded join of the then-branch value and the else-branch value. The guard is evaluated only in the lower environment.

Plain English reading:

- The condition may choose between current-state-dependent branch values, but the condition itself is fixed during the current recurrence step.

The omega-continuity receipt is:

$$
F\left(\bigvee_{n < \omega} X_n\right)
=
\bigvee_{n < \omega} F(X_n),
\qquad
X_n\le X_{n+1}.
$$

Standard reading:

- For every increasing omega-chain of states $X_n$, the update function $F$ produced by CBF-bearing value terms preserves the chain supremum.

The fixed-point receipt is:

$$
F\left(\bigvee_{n < \omega}F^n(\bot)\right)
=
\bigvee_{n < \omega}F^n(\bot).
$$

Standard reading:

- The supremum of the finite approximants is a fixed point of the CBF-bearing update function.

Boundary:

- v486 does not allow conditional guards to read the current recursive state.
- v486 does not allow same-stratum prime.
- v486 does not prove NSO.
- v486 does not lower the fragment into Tau.

The v487 table-compiler extension admits:

$$
\begin{aligned}
\mathrm{Table}
&=
\bigl[(g_i,v_i)\bigr]_{i < m};d,\\
g_i &\in \mathrm{Guard}_{\mathrm{lower}},\\
v_i,d &\in \mathrm{Value}_{+}^{\mathrm{CBF}}.
\end{aligned}
$$

Standard reading:

- A table is a finite list of row guard/value pairs plus an explicit default. Each row guard is lower-stratum only. Each row value and the default may contain safe CBF conditionals.

The compiler law is:

$$
\operatorname{evalPriorityRows}_{\rho,s}
\bigl(\operatorname{compileTable}(T)\bigr)
=
\operatorname{evalTable}_{\rho,s}(T).
$$

Standard reading:

- Evaluating the compiled priority rows in lower environment $\rho$ and state $s$ gives the same Boolean-algebra value as directly evaluating the surface table.

Plain English reading:

- Adding safe CBF conditionals to row values does not change the table compiler's meaning.

The recurrence law is:

$$
\operatorname{OmegaContinuous}
\bigl(\operatorname{updateTables}_{\rho,\mathrm{body}}\bigr).
$$

Standard reading:

- The simultaneous table-update function produced by CBF-bearing restricted tables preserves suprema of increasing omega-chains.

Boundary:

- v487 still excludes current-state-dependent row guards.
- v487 still excludes current-state-dependent conditional guards.
- v487 still excludes same-stratum prime.
- v487 does not prove NSO or Tau lowering.

The v488 obstruction is the two-point witness:

$$
c_{\neg}
:=
\operatorname{cond}(\operatorname{ref},\bot,\top).
$$

Standard reading:

- $c_{\neg}$ is the conditional expression that reads the current state as its guard, returns bottom when the current state is true, and returns top when the current state is false.

It evaluates as:

$$
\llbracket c_{\neg}\rrbracket(\bot)=\top,
\qquad
\llbracket c_{\neg}\rrbracket(\top)=\bot.
$$

Standard reading:

- At bottom, the expression returns top. At top, the expression returns bottom.

The monotonicity failure is:

$$
\bot\le\top
\quad\text{but}\quad
\llbracket c_{\neg}\rrbracket(\bot)
\nleq
\llbracket c_{\neg}\rrbracket(\top).
$$

Standard reading:

- Although bottom is below top, the expression sends bottom to top and top to bottom, so it does not preserve order.

Plain English reading:

- A current-state conditional guard can hide a prime operation. That is why it cannot be admitted into the monotone recurrence fragment without another semantic discipline.

The v489 recovery theorem gives one such discipline on the two-point Boolean
carrier. Let

$$
\operatorname{Cond}(g,t,e)(x)
:=
\begin{cases}
t(x), & g(x)=\top,\\
e(x), & g(x)=\bot.
\end{cases}
$$

The sufficient conditions are:

$$
\operatorname{Mono}(g)
\wedge
\operatorname{Mono}(t)
\wedge
\operatorname{Mono}(e)
\wedge
\forall x,\ e(x)\le t(x).
$$

The checked conclusion is:

$$
\operatorname{Mono}\bigl(\operatorname{Cond}(g,t,e)\bigr).
$$

Standard reading:

- If the guard is monotone, the then branch is monotone, the else branch is monotone, and the else branch is pointwise below the then branch, then the conditional function is monotone.

Plain English reading:

- A current-state guard is safe when switching from else to then only moves upward. The forbidden v488 witness fails exactly because it switches from top down to bottom.

Boundary:

- v489 is only a two-point Boolean monotonicity theorem.
- v489 does not yet prove omega-continuity over complete Boolean algebras.
- v489 does not yet extend the v487 table compiler.

The v490 relation-parametric recovery theorem removes the Boolean-output
accident. Let $S$ be any source relation, let $T$ be any target relation,
and assume the target relation is transitive. Then:

$$
\begin{aligned}
&\operatorname{RelMono}_{S,\mathbb{B}}(g)
\wedge
\operatorname{RelMono}_{S,T}(t)
\wedge
\operatorname{RelMono}_{S,T}(e)
\wedge
\forall x,\ e(x)\le_T t(x)\\
&\qquad\Longrightarrow
\operatorname{RelMono}_{S,T}\bigl(\operatorname{Cond}(g,t,e)\bigr).
\end{aligned}
$$

Standard reading:

- If the Boolean guard is monotone from the source relation into the order $\bot\le\top$, both branches are monotone into the target relation, the target relation is transitive, and the else branch is pointwise below the then branch, then the conditional is monotone into the target relation.

Plain English reading:

- The recovery theorem is an order theorem. The only special Boolean fact is that a monotone Boolean guard may switch from false to true, but may not switch from true to false.

Boundary:

- v490 proves monotonicity only.
- v490 does not prove omega-continuity.
- v490 still uses Boolean guards.

The v491 boundary witness shows why v490 still cannot be promoted directly to
recurrence. Define the ordered carrier:

$$
\mathbb{N}_{\infty}:=\{0,1,2,\ldots\}\cup\{\infty\},
\qquad
0\le1\le2\le\cdots\le\infty.
$$

Let:

$$
\begin{aligned}
X_n &:= n,\\
\bigvee_{n < \omega}X_n &:= \infty,\\
g(n)&:=\bot,\\
g(\infty)&:=\top,\\
t(x)&:=\top,\\
e(x)&:=\bot.
\end{aligned}
$$

The conditional is:

$$
C(x):=\operatorname{Cond}(g,t,e)(x).
$$

The checked facts are:

$$
\operatorname{Mono}(C),
\qquad
\forall n,\ C(X_n)=\bot,
\qquad
C\left(\bigvee_{n < \omega}X_n\right)=\top.
$$

Standard reading:

- The conditional function $C$ is monotone. For every finite stage $X_n$, $C(X_n)$ is bottom. At the omega-supremum of the chain, $C$ is top.

The failed recurrence law is:

$$
C\left(\bigvee_{n < \omega}X_n\right)
\neq
\bigvee_{n < \omega}C(X_n).
$$

Standard reading:

- Applying $C$ after taking the omega-supremum does not equal taking the omega-supremum after applying $C$ at every finite stage.

Plain English reading:

- A monotone guard can still hide a limit jump. It may stay false at every finite approximation and become true only at the omega-limit. That is harmless for order preservation, but fatal for the Kleene-style recurrence proof.

Boundary:

- v491 is a boundary witness, not a positive omega-continuity theorem.
- v491 uses a designated limit carrier, not a full Boolean algebra carrier.
- The next positive theorem must assume guard omega-continuity, or keep current-state guards out of the recursive stratum.

The v492 positive theorem proves the single-chain Boolean repair. Define:

$$
\operatorname{ExistsSup}(X,s,f)
:=
\left(
f(s)=\top
\iff
\exists n,\ f(X_n)=\top
\right).
$$

Standard reading:

- $f$ preserves the Boolean supremum of the chain $X$ at $s$ when $f(s)$ is true exactly when $f$ is true at some finite stage of the chain.

The theorem is:

$$
\begin{aligned}
&
\operatorname{ExistsSup}(X,s,g)
\wedge
\operatorname{ExistsSup}(X,s,t)
\wedge
\operatorname{ExistsSup}(X,s,e)
\wedge
\operatorname{Mono}_{X}(g)
\wedge
\operatorname{Mono}_{X}(t)
\wedge
\forall x,\ e(x)\le t(x)\\
&\qquad\Longrightarrow
\operatorname{ExistsSup}\bigl(X,s,\operatorname{Cond}(g,t,e)\bigr).
\end{aligned}
$$

Standard reading:

- If the guard, then branch, and else branch each preserve the Boolean supremum of the chain; if the guard and then branch are monotone along the finite stages of that chain; and if the else branch is pointwise below the then branch; then the conditional also preserves that Boolean chain supremum.

Plain English reading:

- v491 fails because the guard jumps only at the limit. v492 says that if the guard's limit truth must already appear at some finite stage, then the branch-ordered conditional no longer has that failure mode.

Boundary:

- v492 is Boolean-output and single-chain only.
- v492 is not yet a complete Boolean-algebra omega-continuity theorem.
- v492 is not yet integrated into the restricted table compiler.

The v493 lift replaces Boolean branch values by an ordered branch carrier. Let
$\operatorname{supSeq}$ be a sequence-supremum operator satisfying upper-bound
and least-bound laws, with a transitive and antisymmetric order $\le_T$.

The branch supremum condition is:

$$
\operatorname{SupPres}(X,s,f)
:=
f(s)=\operatorname{supSeq}\bigl(n\mapsto f(X_n)\bigr).
$$

Standard reading:

- $f$ preserves the chosen sequence supremum of $X$ at $s$ when evaluating $f$ at $s$ equals the supremum of the sequence obtained by evaluating $f$ at every finite stage $X_n$.

The theorem is:

$$
\begin{aligned}
&
\operatorname{ExistsSup}(X,s,g)
\wedge
\operatorname{SupPres}(X,s,t)
\wedge
\operatorname{SupPres}(X,s,e)
\wedge
\operatorname{Mono}_{X}(g)
\wedge
\operatorname{Mono}_{X}(t)
\wedge
\forall x,\ e(x)\le_T t(x)\\
&\qquad\Longrightarrow
\operatorname{SupPres}\bigl(X,s,\operatorname{Cond}(g,t,e)\bigr).
\end{aligned}
$$

Standard reading:

- If the Boolean guard preserves the chain supremum in the exists-sup sense; if both ordered branches preserve the sequence supremum; if the guard and then branch are monotone along the finite chain; and if the else branch is pointwise below the then branch; then the conditional preserves the sequence supremum.

Plain English reading:

- The current-state branch-ordered route no longer depends on Boolean branch values. The remaining special restriction is the guard itself: it is still a Boolean guard, not an arbitrary Boolean-algebra-valued guard.

Boundary:

- v493 still has Boolean guards.
- v493 is still a single-chain theorem.
- v493 is not yet a syntax-level table compiler.

The v494 normalization is the first real opening for Boolean-algebra-valued
current guards. Guarded choice usually has a prime on the else side:

$$
\operatorname{GC}(g,t,e)
:=
(g\wedge t)\vee(g'\wedge e).
$$

If the branches are ordered,

$$
e\le t,
$$

then the checked pointwise Boolean-algebra identity is:

$$
(g\wedge t)\vee(g'\wedge e)
=
e\vee(g\wedge t).
$$

Standard reading:

- If the else branch is below the then branch, then the guarded-choice expression equals the join of the else branch with the guard restricted then branch.

Plain English reading:

- The prime is still visible in the usual if-then-else formula, but branch ordering makes it removable. After normalization, the expression is positive in the current guard and positive in the branches.

Boundary:

- v494 is pointwise Boolean algebra.
- v494 is algebraic normalization, not omega-continuity by itself.
- v494 is not yet integrated into table syntax.

The v495 recurrence-shaped theorem uses pointwise omega-union preservation. Let
$X_n$ be a source chain with designated supremum $s$, and let $P$ be the
point space for Boolean-algebra values $P\to\mathbb{B}$. Define:

$$
\operatorname{PresUnion}(X,s,f)
:=
\forall p\in P,\\
f(s)(p)=\top
\iff
\exists n,\ f(X_n)(p)=\top.
$$

Standard reading:

- $f$ preserves pointwise omega-unions along $X$ at $s$ when, at every point $p$, $f$ is true at the supremum exactly when it is true at some finite stage.

The theorem is:

$$
\begin{aligned}
&
\operatorname{PresUnion}(X,s,g)
\wedge
\operatorname{PresUnion}(X,s,t)
\wedge
\operatorname{PresUnion}(X,s,e)
\wedge
\operatorname{Mono}_{X}(g)
\wedge
\operatorname{Mono}_{X}(t)
\wedge
\forall y,\ e(y)\le t(y)\\
&\qquad\Longrightarrow
\operatorname{PresUnion}
\bigl(X,s,\lambda y.\operatorname{GC}(g(y),t(y),e(y))\bigr).
\end{aligned}
$$

Standard reading:

- If the guard, then branch, and else branch each preserve pointwise omega-unions; if the guard and then branch are monotone along the finite chain; and if the else branch is below the then branch at every source state; then guarded choice also preserves pointwise omega-unions.

Plain English reading:

- BA-valued current guards can be recurrence-safe, but only after adding two gates: the branch-order gate $e\le t$, and the omega-union preservation gate for the guard and branches.

Boundary:

- v495 is pointwise Boolean algebra, not arbitrary abstract Boolean algebra.
- v495 is a semantic operator theorem, not syntax-level table integration.
- v495 does not discharge the branch-order proof obligation automatically.

The c051/v496 splitter bridge is separate from the table-guard line. The
one-step splitter identity is:

$$
a=(a\wedge s)\vee(a\wedge s').
$$

The bounded-depth expansion is defined recursively:

$$
\begin{aligned}
\operatorname{SplitExpand}(a,[])
&:=a,\\
\operatorname{SplitExpand}(a,s::S)
&:=
\operatorname{SplitExpand}(a\wedge s,S)
\vee
\operatorname{SplitExpand}(a\wedge s',S).
\end{aligned}
$$

The supplied-key theorem is:

$$
\operatorname{SplitExpand}(a,S)=a.
$$

v497 exposes the leaf list:

$$
\begin{aligned}
\operatorname{Leaves}(a,[])
&:=[a],\\
\operatorname{Leaves}(a,s::S)
&:=
\operatorname{Leaves}(a\wedge s,S)
\mathbin{+\!\!+}
\operatorname{Leaves}(a\wedge s',S).
\end{aligned}
$$

The corresponding checked receipt is:

$$
\operatorname{JoinList}(\operatorname{Leaves}(a,S))=a
\quad\wedge\quad
\left|\operatorname{Leaves}(a,S)\right|=2^{|S|}.
$$

Standard reading:

- Splitting an element $a$ by every splitter in a finite list $S$, then joining all resulting leaves, gives back exactly $a$.
- The explicit leaf-list version says that the finite splitter schedule produces $2^{|S|}$ dyadic leaves, and that the join of exactly those leaves is $a$.

Plain English reading:

- c051 proves one cut preserves the whole region. v496 proves any finite splitter tree preserves the whole region.
- v497 adds the bookkeeping that a depth-$n$ splitter schedule really has $2^n$ terminal pieces.

Boundary:

- v496 is bounded splitter expansion, not a full formula-grammar QE compiler.
- v497 is still finite. It does not supply countable joins or infinite recurrence.
- v496 does not choose splitters.
- v496 does not prove termination or stopping criteria for a QE driver.

### 4.2 Infinite table completion proof artifact

Full infinite tables require a semantic carrier with countable joins. v498
does not choose that carrier. It proves the table lift that any candidate
carrier must pass.

The abstract carrier interface is:

$$
\mathcal{C}=(A,\le,\bot,\bigvee_{n < \omega}).
$$

The table carrier is:

$$
\operatorname{Table}(K,A):=K\to A.
$$

The order and countable supremum are pointwise:

$$
T\le_{\operatorname{Table}}U
\quad:\Longleftrightarrow\quad
\forall k\in K,\ T(k)\le U(k),
$$

$$
\left(\bigvee_{n < \omega}^{\operatorname{Table}}T_n\right)(k)
:=
\bigvee_{n < \omega}T_n(k).
$$

For a monotone and omega-continuous table update $F$, define:

$$
X_0:=\bot,\qquad X_{n+1}:=F(X_n),
\qquad
\mu F:=\bigvee_{n < \omega}X_n.
$$

The checked theorem is:

$$
F(\mu F)=\mu F.
$$

Standard reading:

- If the value carrier has a valid countable-supremum semantics, then the table carrier inherits that semantics one key at a time.
- If a table update $F$ is monotone and preserves countable suprema of increasing chains, then the supremum of its finite approximants is a fixed point.

Plain English reading:

- Infinite tables need a place where an infinite ascending process can actually converge. v498 proves that once the value space has that place, tables inherit it automatically by evaluating each key separately.

Boundary:

- v498 is an abstract semantic receipt, not an executable representation.
- v498 does not choose between Borel codes, automata, prefix-open cells, or another concrete carrier.
- v498 does not prove atomlessness or splitter existence.
- v498 does not compile TABA syntax into $F$.

v499 adds a splitter interface to the same abstract carrier. Suppose the value
carrier can split every non-bottom value $a$ into two non-bottom pieces:

$$
\operatorname{split}_L(a)\vee\operatorname{split}_R(a)=a,
$$

$$
\operatorname{split}_L(a)\wedge\operatorname{split}_R(a)=\bot,
$$

$$
\operatorname{split}_L(a)\ne\bot
\quad\wedge\quad
\operatorname{split}_R(a)\ne\bot.
$$

For a table $T:K\to A$ and a supplied live key $k_0$ with
$T(k_0)\ne\bot$, define:

$$
L(k):=
\begin{cases}
\operatorname{split}_L(T(k_0)), & k=k_0,\\
T(k), & k\ne k_0,
\end{cases}
$$

$$
R(k):=
\begin{cases}
\operatorname{split}_R(T(k_0)), & k=k_0,\\
\bot, & k\ne k_0.
\end{cases}
$$

The checked theorem is:

$$
L\vee R=T
\quad\wedge\quad
L\wedge R=\bot
\quad\wedge\quad
L\ne\bot
\quad\wedge\quad
R\ne\bot.
$$

The strengthened existence theorem is:

$$
T\ne\bot
\quad\Longrightarrow\quad
\exists L,R.\,
L\vee R=T
\wedge
L\wedge R=\bot
\wedge
L\ne\bot
\wedge
R\ne\bot.
$$

Standard reading:

- If one table coordinate is live, and the value at that coordinate can be split, then the whole table can be split by changing only that coordinate.
- The left table keeps all other coordinates unchanged. The right table is bottom at every other coordinate.
- If the table is not bottom, then some coordinate is live, so the table-level split exists.

Plain English reading:

- A table is live when at least one key carries live value. v499 proves that a live coordinate is enough to split the table itself, provided the value carrier already knows how to split live values.

Boundary:

- v499 proves live-key existence classically. It does not provide an executable search procedure for a concrete runtime carrier.
- v499 is abstract. It does not construct Borel, automata, or quotient carriers.
- v499 does not compile TABA syntax.

v500 then applies the discretization trick to the positive prefix-open lane.
For a finite binary word $w$, write $[w]$ for the cylinder of streams
beginning with $w$. The checked basis identity is:

$$
[w]=[w0]\vee[w1].
$$

The children are disjoint:

$$
[w0]\wedge[w1]=\bot.
$$

Both children are nonempty:

$$
[w0]\ne\bot
\quad\wedge\quad
[w1]\ne\bot.
$$

Standard reading:

- Every stream beginning with $w$ begins with either $w0$ or $w1$.
- No stream can begin with both $w0$ and $w1$.
- There is at least one stream beginning with $w0$, and at least one stream beginning with $w1$.

Plain English reading:

- A prefix cylinder is a binary region. v500 proves the local split: every such region has a left child and a right child, the children do not overlap, and together they exactly cover the parent.

Boundary:

- v500 is the basis-cylinder lemma, not the full prefix-open carrier.
- v500 does not prove that arbitrary prefix-open regions can be split.
- v500 does not provide complement or full Boolean expressiveness.

v501 lifts the basis split from one cylinder to any nonempty prefix-open
region. If:

$$
U=\bigcup_{w\in G}[w]
\quad\text{and}\quad
U\ne\bot,
$$

then there exist prefix-open $L$ and $R$ such that:

$$
L\ne\bot
\quad\wedge\quad
R\ne\bot,
$$

$$
L\subseteq U
\quad\wedge\quad
R\subseteq U,
$$

$$
L\wedge R=\bot.
$$

Standard reading:

- If $U$ is a nonempty prefix-open region, then some generator cylinder $[w]$ lies inside it.
- The two child cylinders $[w0]$ and $[w1]$ are nonempty, disjoint, prefix-open, and both are contained in $U$.

Plain English reading:

- Any live prefix-open region contains a smaller binary fork. This proves positive refinement: the region can always be made more precise without collapsing to a single atom.

Boundary:

- v501 does not prove $L\vee R=U$.
- The missing covering equation would require a difference or complement-like operation.
- That distinction matters because prefix-open regions are a positive carrier, not a full Boolean carrier.

v502 proves the omega-supremum side of the positive prefix-open lane. Given a
sequence of generators $G_n$, define:

$$
G_\omega(w)
:=
\exists n.\,G_n(w).
$$

Then:

$$
\bigcup_{n < \omega}\operatorname{Open}(G_n)
=
\operatorname{Open}(G_\omega).
$$

The checked upper-bound law is:

$$
\operatorname{Open}(G_n)
\subseteq
\operatorname{Open}(G_\omega).
$$

The checked least-bound law is:

$$
\left(
\forall n.\,\operatorname{Open}(G_n)\subseteq V
\right)
\Longrightarrow
\operatorname{Open}(G_\omega)\subseteq V.
$$

Standard reading:

- The countable union of prefix-open regions is prefix-open.
- The generator set for the union contains exactly the finite words generated by at least one stage.
- This union is the least upper bound of the stages with respect to inclusion.

Plain English reading:

- Prefix-open regions are closed under countable growth. This gives the positive lane the omega-supremum operation needed by recurrence.

Boundary:

- v502 still does not add complement.
- v502 gives positive omega semantics, not full Boolean table semantics.

v503 corrects the boundary around finite multi-hit QE. Let $M$ be a finite
list of mask regions and $H$ be a finite list of hit regions. The checked
formula is:

$$
\exists x.\left(
\bigwedge_{t\in M} x\wedge t=\bot
\;\wedge\;
\bigwedge_{s\in H} x\wedge s\ne\bot
\right)
\Longleftrightarrow
\forall s\in H.\left(\left(\bigvee M\right)'\wedge s\ne\bot\right).
$$

Standard reading:

- There exists a Boolean-algebra element $x$ such that $x$ is disjoint from every mask $t\in M$, and $x$ has nonzero overlap with every hit region $s\in H$, if and only if every hit region $s\in H$ has nonzero overlap with the prime of the join of all masks.

Plain English reading:

- The same witness can serve every same-polarity hit. Choose $x$ to be everything outside the joined masks. This works exactly when each requested hit region still has a nonzero part outside those masks.

Trap:

- This is not where atomlessness enters. No region needs to be split into two independent live pieces. The witness is just the mask complement.
- Atomlessness begins to matter for mixed-polarity constraints, where the formula demands live overlap for both $x$ and $x'$.

Boundary:

- v503 is same-polarity hit QE only.
- v503 does not compile a full formula grammar.
- v503 does not prove NSO or Tau lowering.

v504 proves the first checked rule where atomless-style splitting is actually
used. With one mask $t$, one positive hit $s$, and one complement hit
$r$, assume the carrier can split every nonzero element into two disjoint
nonzero pieces. Then:

$$
\exists x.\left(
x\wedge t=\bot
\;\wedge\;
x\wedge s\ne\bot
\;\wedge\;
x'\wedge r\ne\bot
\right)
\Longleftrightarrow
\left(t'\wedge s\ne\bot\right)
\;\wedge\;
\left(r\ne\bot\right).
$$

Standard reading:

- There exists a Boolean-algebra element $x$ that avoids $t$, has nonzero overlap with $s$, and whose prime has nonzero overlap with $r$, if and only if $s$ has a nonzero part outside $t$, and $r$ itself is nonzero.

Plain English reading:

- The positive side needs live material outside the mask. The complement-hit side only needs $r$ to be live somewhere. If $r$ is already inside the masked part, then $x'$ hits it automatically. If not, the live region outside the mask may have to be split so that one piece goes into $x$ and another remains for $x'$.

Trap:

- This is not the same proof as v503. v503 uses one witness, the mask complement. v504 sometimes needs a genuine two-piece split of a live residual region.
- The theorem is still not full TABA QE. It covers one positive hit and one complement hit.

Boundary:

- v504 uses an abstract splitter interface, not a concrete infinite carrier.
- v504 does not cover finite many mixed-polarity hit lists.
- v504 does not compile a full formula grammar.
- v504 does not prove NSO or Tau lowering.

v505 extracts the extension step needed for finite positive-hit lists. Suppose
$y$ already avoids the mask and already leaves live room for the complement
hit. If a new positive hit $s$ has nonzero residue outside the mask, then
$y$ can be extended to a larger $x$:

$$
\begin{aligned}
&y\wedge t=\bot
\;\wedge\;
y'\wedge r\ne\bot
\;\wedge\;
t'\wedge s\ne\bot\\
&\Longrightarrow
\exists x.\left(
y\le x
\;\wedge\;
x\wedge t=\bot
\;\wedge\;
x\wedge s\ne\bot
\;\wedge\;
x'\wedge r\ne\bot
\right).
\end{aligned}
$$

Standard reading:

- If $y$ is disjoint from $t$, the prime of $y$ has nonzero overlap with $r$, and $s$ has a nonzero part outside $t$, then there is an $x$ above $y$ that is still disjoint from $t$, has nonzero overlap with $s$, and whose prime still has nonzero overlap with $r$.

Plain English reading:

- A witness can be grown one positive obligation at a time without destroying the remaining complement obligation. If the old complement residue would be consumed by the new positive piece, split it first.

Trap:

- This is an extension lemma, not the full finite-list theorem.
- It preserves one complement-hit target. More complement-hit targets need another layer of bookkeeping.

Boundary:

- v505 uses an abstract splitter interface, not a concrete carrier.
- v505 does not handle finite many complement-hit targets.
- v505 does not compile a full formula grammar.
- v505 does not prove NSO or Tau lowering.

v506 iterates the v505 extension step over a finite list of positive-hit
targets $H$, while preserving one complement-hit target $r$:

$$
\exists x.\left(
x\wedge t=\bot
\;\wedge\;
\bigwedge_{s\in H}x\wedge s\ne\bot
\;\wedge\;
x'\wedge r\ne\bot
\right)
\Longleftrightarrow
\left(
\forall s\in H.\,t'\wedge s\ne\bot
\right)
\;\wedge\;
r\ne\bot.
$$

Standard reading:

- There exists an $x$ that avoids $t$, hits every positive target $s\in H$, and whose prime hits $r$, if and only if every positive target has nonzero residue outside $t$, and $r$ is nonzero.

Plain English reading:

- The witness starts at $\bot$. Each positive obligation is added one at a time. Since the witness only grows, earlier positive hits stay hit. The splitter is used to preserve the one remaining complement obligation.

Trap:

- This is now a finite-list theorem, but only on the positive-hit side.
- It still preserves one complement-hit target. Multiple complement-hit targets need a stronger invariant.

Boundary:

- v506 uses an abstract splitter interface, not a concrete carrier.
- v506 does not handle finite many complement-hit targets.
- v506 does not compile a full formula grammar.
- v506 does not prove NSO or Tau lowering.

### 4.3 Finite Tau table-kernel proof artifact

One executable receipt now sits beside the Lean ladder. It is not a proof of
full TABA tables. It is a Tau replay for the finite mask fragment used in the
tutorial.

The replay has two implementations:

- a self-contained Tau spec,
- a feature-flagged Tau runtime path with native `ft4` finite Boolean-algebra values.

The exact finite carrier is:

$$
\begin{aligned}
\mathrm{Cell}_4 &:= \{0,1,2,3\},\\
\mathrm{Mask}_4 &:= \mathcal{P}(\mathrm{Cell}_4),\\
\operatorname{pack} &:\mathrm{Mask}_4\to\{0,\ldots,15\},\\
\operatorname{unpack} &:\{0,\ldots,15\}\to\mathrm{Mask}_4.
\end{aligned}
$$

The implementation stores a finite subset of `Cell4` as a four-bit integer.
The bit notation is:

$$
A_k := \operatorname{bit}_k(A).
$$

Standard reading:

$$
A_k=1 \Longleftrightarrow k\in\operatorname{unpack}(A),
\qquad
A_k=0 \Longleftrightarrow k\notin\operatorname{unpack}(A).
$$

This is a representation equation. It does not say that an arbitrary TABA table
has four cells. It says that the executable receipt uses a four-cell finite
approximant.

The host-side model clips input integers before interpreting them:

$$
\operatorname{clip}_4(x):=x\mathbin{\&}\mathtt{0x0f}.
$$

Standard reading:

$$
\operatorname{clip}_4(x)_k=x_k
\quad\text{for }k\in\{0,1,2,3\}.
$$

This is why the replay includes a high-bit case. The test is not incidental.
It checks that the executable carrier is exactly the low-four-cell carrier,
not an accidental eight-cell table. Bits with index $k\ge 4$ are outside the
declared carrier and are discarded by the model.

The finite join formula is:

$$
\operatorname{join}_4(A,B)_k := A_k\lor B_k.
$$

Standard reading:

For each cell $k$, the cell $k$ is present in
$\operatorname{join}_4(A,B)$ if and only if $k$ is present in $A$ or
$k$ is present in $B$.

The formula is pointwise. It does not say "append rows" syntactically. It says
that the denotation of the joined table is the union of the denotations of the
two input tables.

The finite common formula is:

$$
\operatorname{common}_4(A,B)_k := A_k\land B_k.
$$

Standard reading:

For each cell $k$, the cell $k$ is present in
$\operatorname{common}_4(A,B)$ if and only if $k$ is present in $A$ and
$k$ is present in $B$.

This is the finite-set intersection operation. It corresponds to the TABA
`common` idea only at this finite Boolean-carrier level. The full table-level
law appears later as `commonTables T1 T2 = fun k => T1 k meet T2 k`.

The finite selection formula is:

$$
\operatorname{select}_4(A,G)_k := A_k\land G_k.
$$

Standard reading:

For each cell $k$, the cell $k$ is present in
$\operatorname{select}_4(A,G)$ if and only if $k$ is present in $A$ and
the guard $G$ contains $k$.

The guard is a region, not a procedural if-statement. In the finite mask carrier
it is represented by another four-bit set.

The finite masked update formula is:

$$
\operatorname{set}_4(A,G,V)_k :=
\begin{cases}
V_k, & G_k=1,\\
A_k, & G_k=0.
\end{cases}
$$

Equivalent Boolean-algebra form:

$$
\operatorname{set}_4(A,G,V):=(A\land G')\lor(V\land G).
$$

Standard reading:

For each cell $k$, if $k$ is inside guard $G$, the result uses $V_k$.
If $k$ is outside $G$, the result uses $A_k$.

The prime `G'` is complement inside the finite four-cell universe. It is not a
propositional negation over formulas and not a derivative. At the mask level:

$$
G' := \mathbf{1}_4\oplus G,
\qquad
\mathbf{1}_4=\mathtt{1111}.
$$

or equivalently:

$$
G'_k=1\Longleftrightarrow G_k=0.
$$

This is the formula that connects the Tau `ft4` carrier to the more general
Boolean-algebra table laws. The case definition is easier to read, but the
Boolean-algebra expression is the executable algebraic form.

The packed four-to-two projection uses the parent map:

$$
\operatorname{parent}(0)=0,\qquad
\operatorname{parent}(1)=0,\qquad
\operatorname{parent}(2)=1,\qquad
\operatorname{parent}(3)=1.
$$

The projection formula is:

$$
\operatorname{project}_{4\to2}(A)_p
:=
\bigvee_{\substack{k\in\mathrm{Cell}_4\\
\operatorname{parent}(k)=p}} A_k.
$$

Specialized to two parent cells:

$$
\operatorname{project}_{4\to2}(A)_0 := A_0\lor A_1,
\qquad
\operatorname{project}_{4\to2}(A)_1 := A_2\lor A_3.
$$

Standard reading:

Parent cell $p$ is present after projection if and only if at least one child
cell of $p$ was present before projection.

Projection is therefore existential elimination over the child-side coordinate.
It is not a choice of one representative child. It is a finite "there exists a
child" operation.

The checked projection law is:

$$
\operatorname{project}_{4\to2}(\operatorname{join}_4(A,B))
=
\operatorname{join}_2
\bigl(
\operatorname{project}_{4\to2}(A),
\operatorname{project}_{4\to2}(B)
\bigr).
$$

Standard reading:

For each parent cell $p$, $p$ is present after projecting the union of
$A$ and $B$ if and only if $p$ is present after unioning the two
projected tables.

Expanded proof shape:

$$
\begin{aligned}
\operatorname{project}_{4\to2}(\operatorname{join}_4(A,B))_p
&=
\bigvee_{\operatorname{parent}(k)=p}
\operatorname{join}_4(A,B)_k\\
&=
\bigvee_{\operatorname{parent}(k)=p}(A_k\lor B_k)\\
&=
\left(\bigvee_{\operatorname{parent}(k)=p}A_k\right)
\lor
\left(\bigvee_{\operatorname{parent}(k)=p}B_k\right)\\
&=
\operatorname{join}_2
\bigl(
\operatorname{project}_{4\to2}(A),
\operatorname{project}_{4\to2}(B)
\bigr)_p.
\end{aligned}
$$

This is the finite existential-distributes-over-disjunction law. It is the
small executable shadow of the later split-index DNF projection bridge.

The Tau runtime `ft4` carrier implements these Boolean operations directly:

$$
\begin{aligned}
0_{\mathrm{ft4}} &:= \mathtt{0000},\\
1_{\mathrm{ft4}} &:= \mathtt{1111},\\
A\land B &:= \text{bitwise AND on the four low bits},\\
A\lor B &:= \text{bitwise OR on the four low bits},\\
A' &:= \text{bitwise complement inside }\mathtt{1111},\\
A\oplus B &:= \text{bitwise XOR on the four low bits}.
\end{aligned}
$$

The feature-flagged example checks these Tau outputs:

$$
\begin{aligned}
o_7  &= i_5\lor i_6,\\
o_8  &= i_5\land i_6,\\
o_9  &= i_5\land i_7,\\
o_{10} &= (i_5\land i_7')\lor(i_8\land i_7),\\
o_{11} &= 1 \Longleftrightarrow i_5\land i_5'=0.
\end{aligned}
$$

Standard reading:

$o_7$ is native `ft4` join. $o_8$ is native `ft4` common. $o_9$ is
native `ft4` guard selection. $o_{10}$ is native `ft4` masked update.
$o_{11}$ checks that a finite region and its prime are disjoint.

The `ft4` splitter used by Tau's solver is deliberately finite:

$$
\operatorname{splitter}(A)
:=
\{k\}
\quad\text{where }k=\min\{j\in\mathrm{Cell}_4:A_j=1\}.
$$

Standard reading:

If $A$ is nonzero, $\operatorname{splitter}(A)$ returns one live singleton
cell of $A$.

This makes finite solving practical, but it is also exactly why `ft4` is not an
atomless carrier. An atomless splitter must split every nonzero element into two
nonzero parts. A finite singleton cell cannot be split inside `ft4`.

The replay claim is:

$$
\forall c\in C_{\mathrm{finite}},
\qquad
\operatorname{TauOut}(c)=\operatorname{ExpectedModel}(c).
$$

Standard reading:

For every checked replay case $c$ in the finite corpus $C_{\mathrm{finite}}$,
the Tau-produced output vector equals the output vector computed by the
independent finite-mask model.

This is not a universal theorem over all inputs. It is executable replay
evidence over the recorded corpus. The corpus is intentionally small and
diagnostic: it checks overlap, guarded update, projection-over-join, high-bit
clipping, native `ft4` operations, and complement disjointness.

The files are:

- `examples/tau/finite_table_kernel_v1.tau`,
- `examples/tau/finite_table_kernel_builtins_v1.tau`,
- `scripts/generate_finite_table_tau_artifacts.py`,
- `assets/data/finite_table_tau_traces.json`,
- `external/tau-lang/src/boolean_algebras/finite_table_ba.h`,
- `external/tau-lang/src/finite_table_builtins.h`.

The current artifact reports four checked cases for each implementation, zero
mismatches.

### 4.4 How the finite formulas came from the TABA table equations

Interpretive assumption:

The TABA table equations are read extensionally.

That means a table is interpreted by the function it denotes, not by the
particular syntax of its row list. The sparse row-list picture is:

$$
T=[(G_i,a_i)]_{i < m}.
$$

where each `G_i` is a guard region and each `a_i` is the value assigned on that
guard. After normalization, the guards are treated as pairwise disjoint.

$$
i\ne j\Longrightarrow G_i\cap G_j=\varnothing.
$$

The extensional reading is:

$$
\llbracket T\rrbracket(x)=
\begin{cases}
a_i, & x\in G_i\text{ for some }i < m,\\
0, & \text{otherwise.}
\end{cases}
$$

Standard reading:

For an input point $x$, the table returns the value attached to the guard
containing $x$. If no row guard contains $x$, the table returns zero.

This is the bridge from Ohad's table notation to the local finite masks. In the
finite executable carrier, the points `x` are the four cells `0,1,2,3`, and a
guard is simply a finite subset of those cells.

Ohad-style `set` becomes:

$$
\operatorname{set}_G(T,a)(x)=
\begin{cases}
a, & x\in G,\\
T(x), & x\notin G.
\end{cases}
$$

The four-cell mask specialization is:

$$
\operatorname{set}_4(A,G,V)_k=
\begin{cases}
V_k, & G_k=1,\\
A_k, & G_k=0.
\end{cases}
$$

Ohad-style `select` becomes:

$$
\operatorname{select}_{\varphi}(T)(x)=
\begin{cases}
T(x), & \varphi(T(x)),\\
0, & \text{otherwise.}
\end{cases}
$$

The four-cell guard specialization is:

$$
\operatorname{select}_4(A,G)_k:=A_k\land G_k.
$$

This is a specialization because the predicate `phi` has been compiled into a
guard region `G`. The finite executable formula does not cover arbitrary value
predicates. It covers the guard-region form.

Ohad-style `common` becomes:

$$
\operatorname{common}(T,U)(x)=
\begin{cases}
T(x), & T(x)=U(x),\\
0, & \text{otherwise.}
\end{cases}
$$

The algebraic finite-mask version used in the tutorial is:

$$
\operatorname{common}_4(A,B)_k:=A_k\land B_k.
$$

This is not the same formula unless table values are read as presence bits and
"common" means shared support. The research page must keep that distinction
explicit. In the finite executable kernel, `common4` means support
intersection. In the BA-valued Lean layer, `commonTables` means pointwise meet:

$$
\operatorname{commonTables}(T_1,T_2)(k):=T_1(k)\wedge T_2(k).
$$

That is the algebraic generalization of finite support intersection.

### 4.5 The neuro-symbolic search loop

The local process was not a single proof attempt. It was a neuro-symbolic
search loop:

$$
\mathrm{TABA\ equation}
\Longrightarrow
\mathrm{extensional\ reading}
\Longrightarrow
\mathrm{finite\ carrier}
\Longrightarrow
\mathrm{Lean\ statement}
\Longrightarrow
\mathrm{Tau\ candidate}
\Longrightarrow
\mathrm{Aristotle\ proof\ search}
\Longrightarrow
\mathrm{independent\ model}
\Longrightarrow
\mathrm{replay\ corpus}
\Longrightarrow
\mathrm{mismatch\ or\ receipt}.
$$

The symbolic side proposed equivalences and carrier choices. The mechanical
side rejected overclaims. A candidate survived only when it had at least one of
these receipts:

```text
Lean theorem
bounded exhaustive check
Tau replay against an independent model
SMT or brute-force cross-check
Aristotle result that was rebuilt locally with no placeholders
```

Aristotle was treated as a proof-search worker inside this loop. The local rule
was: a returned Aristotle proof is not evidence until the theorem statement is
unchanged, the proof builds in the local Lean project, and the file passes the
no-placeholder scan. This matters because the hard part of TABA tables is not
only proving lemmas. It is choosing theorem statements that do not smuggle in a
false semantic assumption.

The important novel moves were:

1. Split the table problem into three carriers:

$$
\mathrm{finite\ executable}
\quad\mid\quad
\mathrm{algebraic\ atomless}
\quad\mid\quad
\mathrm{completed\ reference}.
$$

This avoided treating one representation as if it solved every semantic level.

2. Read projection as existential elimination:

$$
\operatorname{project}(A)_p
:=
\exists k\,\bigl(\operatorname{parent}(k)=p\land A_k\bigr).
$$

This converted a table operation into a quantifier-elimination problem.

3. Abstract the child-parent structure into a split-index interface:

$$
\mathrm{BaseCell}\times\mathbb{B}
\qquad\text{and}\qquad
\operatorname{Fin}(2n).
$$

The product carrier is mathematically clean. The packed `Fin (2*n)` carrier is
closer to implementation. Lean was used to prove that the packed arithmetic
really implements the split-index laws.

4. Separate semantic adequacy from implementation replay:

$$
\mathrm{formula\ theorem}\ne\mathrm{implementation\ replay}.
$$

The Tau replay is evidence that the executable finite kernel matches the finite
model. It is not used as a substitute for the Lean semantic theorems.

5. Add a native Tau base BA only after the finite meaning was stable:

$$
\mathrm{ft4}:\text{four-cell finite Boolean algebra}.
$$

This was not added as a new semantic theory. It was added as an executable
carrier for the already-scoped finite fragment.

### 4.6 Finite compiled BA and Tau `ft4` bridge

c035 moves the finite recurrence compiler from a Boolean-only toy carrier into
an arbitrary Boolean-algebra-valued carrier:

$$
\operatorname{State}_{V,I}:=I\to V.
$$

Standard reading:

A compiled family state assigns one value in the Boolean algebra $V$ to each
component index in $I$.

The expression grammar checked in c035 is:

$$
e ::=
\bot
\mid \top
\mid \operatorname{const}(v)
\mid \operatorname{ref}(i)
\mid e'
\mid e_1\wedge e_2
\mid e_1\vee e_2.
$$

Standard reading:

An expression is built from bottom, top, a constant Boolean-algebra value, a
component reference, prime, meet, and join.

The compiler equation is:

$$
\operatorname{compileUpdate}(B,n)(S)(r)
:=
\begin{cases}
\llbracket B(n)\rrbracket_S, & r=n,\\
S(r), & r\ne n.
\end{cases}
$$

Standard reading:

The compiled update for target $n$ computes the body expression $B(n)$ in
the old state $S$, writes that value at component $n$, and leaves every
other component $r$ unchanged.

The dependency law is:

$$
\operatorname{Occurs}(d,B(n))
\land
\operatorname{PrefixReady}(B,\operatorname{order})
\Longrightarrow
\operatorname{Before}(d,n,\operatorname{order}).
$$

Standard reading:

If component $d$ occurs syntactically inside the body for component $n$, and
the certified order is prefix-ready for those formula dependencies, then $d$
appears before $n$ in the certified order.

The finite recurrence theorem is:

$$
\operatorname{Finite}(I\to V)
\Longrightarrow
\exists i,j,\;
i < j\le |I\to V|
\land
S_i=S_j.
$$

where:

$$
S_0=S,\qquad
S_{n+1}=\operatorname{evalSchedule}
\bigl(\operatorname{compileSchedule}(B,\operatorname{order})\bigr)(S_n).
$$

Standard reading:

If the compiled state space is finite, then iterating the compiled schedule
must eventually repeat a state within the finite cardinality bound.

This is the exact bridge from the Boolean toy recurrence kernel to finite
Boolean-algebra values. It does not prove that the Boolean algebra is atomless,
complete, or able to host arbitrary countable recurrence suprema. It proves the
finite compiled-state loop property once the state carrier is finite.

c036 then pins the semantic carrier behind Tau's feature-flagged `ft4` path:

$$
\operatorname{Ft4}:=\operatorname{Fin}(4)\to\mathbb{B}.
$$

Standard reading:

An `ft4` value is a truth value for each of four cells. A cell maps to
$\mathrm{true}$ exactly when that cell is present in the finite region.

The checked pointwise runtime laws are:

$$
\begin{aligned}
0_{\mathrm{ft4}}(k)&=\mathrm{false},\\
1_{\mathrm{ft4}}(k)&=\mathrm{true},\\
(A\wedge B)(k)&=A(k)\land B(k),\\
(A\vee B)(k)&=A(k)\lor B(k),\\
A'(k)&=\neg A(k),\\
(A\oplus B)(k)&=\operatorname{xor}(A(k),B(k)).
\end{aligned}
$$

Standard reading:

Zero contains no cell. One contains every cell. Meet, join, prime, and xor are
computed independently at each of the four cells.

The guarded-set law is:

$$
\operatorname{set4}(A,G,V)
:=
(A\wedge G')\vee(V\wedge G).
$$

with:

$$
G(k)=\mathrm{true}
\Longrightarrow
\operatorname{set4}(A,G,V)(k)=V(k),
$$

and:

$$
G(k)=\mathrm{false}
\Longrightarrow
\operatorname{set4}(A,G,V)(k)=A(k).
$$

Standard reading:

At a guarded cell, the new value comes from $V$. Outside the guard, the old
value from $A$ is preserved.

The finiteness receipts are:

$$
\operatorname{Finite}(\operatorname{Ft4})
\qquad\text{and}\qquad
\operatorname{Finite}(I)\Longrightarrow
\operatorname{Finite}(I\to\operatorname{Ft4}).
$$

Standard reading:

The four-cell Boolean carrier is finite, and any finite family of four-cell
values is also finite. Therefore `ft4` family states satisfy the finiteness
premise used by c035.

Boundary:

c036 is a semantic carrier proof. It does not prove the C++ parser, printer,
bit-mask clipping code, Tau evaluator, or full table syntax. Those are separate
implementation parity obligations. The Tau replay receipt checks representative
runtime cases; it is not a universal theorem over all C++ executions.

### 4.7 What Lean checked at the algebraic table level

The c013 receipt proves the splitter characterization:

$$
\operatorname{HasSplitters}(\alpha)
\Longleftrightarrow
\operatorname{IsAtomless}(\alpha).
$$

Definitions:

$$
\operatorname{IsSplitter}(a,s)
:=
(a\wedge s\ne\bot)\land(a\wedge s'\ne\bot).
$$

$$
\operatorname{HasSplitters}(\alpha)
:=
\forall a\in\alpha,\;
a\ne\bot\Longrightarrow
\exists s\in\alpha,\;\operatorname{IsSplitter}(a,s).
$$

Standard reading:

A Boolean algebra has splitters exactly when every nonzero element can be cut
by some $s$ into two nonzero parts, the part inside $s$ and the part outside
$s$.

This is the formal version of the atomless idea. It is not an executable search
algorithm for such an `s` in an arbitrary infinite Boolean algebra.

The c017 receipt defines BA-valued tables as:

$$
\operatorname{Table}(\alpha,K):=K\to\alpha.
$$

Standard reading:

A table with key type $K$ and Boolean-algebra value type $\alpha$ is a
function that assigns one Boolean-algebra value to each key.

No finiteness assumption is placed on `K`. The key type can be finite or
infinite. The result is algebraic, not constructive.

The checked set operation is:

$$
\operatorname{setAt}(T,k,v)(k')
:=
\begin{cases}
v, & k'=k,\\
T(k'), & k'\ne k.
\end{cases}
$$

Checked laws:

$$
\operatorname{setAt}(\operatorname{setAt}(T,k,v_1),k,v_2)
=
\operatorname{setAt}(T,k,v_2).
$$

Standard reading:

Overwriting the same key twice leaves only the second overwrite visible.

$$
k_1\ne k_2
\Longrightarrow
\operatorname{setAt}(\operatorname{setAt}(T,k_1,v_1),k_2,v_2)
=
\operatorname{setAt}(\operatorname{setAt}(T,k_2,v_2),k_1,v_1).
$$

Standard reading:

Overwrites at distinct keys commute.

The checked select operation is:

$$
\operatorname{selectWhere}(T,\varphi)(k)
:=
\begin{cases}
T(k), & \varphi(T(k))=\mathrm{true},\\
\bot, & \text{otherwise.}
\end{cases}
$$

Checked law:

$$
\operatorname{selectWhere}
\bigl(\operatorname{selectWhere}(T,\varphi),\psi\bigr)
=
\operatorname{selectWhere}
\bigl(T,\lambda v.\,\varphi(v)\land\psi(v)\bigr).
$$

Standard reading:

Selecting first by $\varphi$ and then by $\psi$ is the same as selecting
once by the conjunction of both predicates.

The checked common operation is:

$$
\operatorname{commonTables}(T_1,T_2)(k):=T_1(k)\wedge T_2(k).
$$

Checked laws:

$$
\operatorname{commonTables}(T,T)=T.
$$

$$
\operatorname{commonTables}(T_1,T_2)
=
\operatorname{commonTables}(T_2,T_1).
$$

$$
\operatorname{commonTables}
\bigl(T_1,\operatorname{commonTables}(T_2,T_3)\bigr)
=
\operatorname{commonTables}
\bigl(\operatorname{commonTables}(T_1,T_2),T_3\bigr).
$$

Standard reading:

Pointwise meet is idempotent, commutative, and associative at the table level
because meet has those laws in the value Boolean algebra.

The checked key-coherence law is:

$$
T_1(k)=v
\Longrightarrow
\operatorname{commonTables}
\bigl(T_1,\operatorname{setAt}(T_2,k,v)\bigr)
=
\operatorname{setAt}
\bigl(\operatorname{commonTables}(T_1,T_2),k,v\bigr).
$$

Standard reading:

If $T_1$ already has value $v$ at key $k$, then setting $T_2$ at $k$
to $v$ before taking common is the same as taking common first and then
setting the result at $k$ to $v$.

The table-level splitter partition formulas are:

$$
\operatorname{setAt}(T,k,T(k)\wedge s)(k)
\vee
\operatorname{setAt}(T,k,T(k)\wedge s')(k)
=
T(k).
$$

and:

$$
\operatorname{setAt}(T,k,T(k)\wedge s)(k)
\wedge
\operatorname{setAt}(T,k,T(k)\wedge s')(k)
=
\bot.
$$

Standard reading:

At key $k$, the two splitter tables cover the old value and are disjoint.

The atomless table capstone is:

$$
\left(
\forall a,\;a\ne\bot\Rightarrow
\exists s,\;(a\wedge s\ne\bot)\land(a\wedge s'\ne\bot)
\right)
\land T(k)\ne\bot
$$

$$
\Longrightarrow
\exists s,\;
\operatorname{setAt}(T,k,T(k)\wedge s)(k)\ne\bot
\land
\operatorname{setAt}(T,k,T(k)\wedge s')(k)\ne\bot.
$$

Standard reading:

If the value Boolean algebra is atomless and table $T$ has a nonzero value at
key $k$, then the table can be split at that key into two nonzero table
values.

This is the precise solved part of "atomless infinite tables." It proves the
algebraic table laws and table-level splitting for arbitrary key type `K` and
Boolean-algebra value type `alpha`.

The v471 receipt closes one concrete carrier bridge that Claude's latest work
left open. Claude c018 proved splitter existence for raw Cantor trees. Claude
c019 proved Boolean identities for the semantic `Clopen` subtype. v471 proves
that the raw-tree splitter can be transported into the semantic subtype:

$$
\forall f:\operatorname{Clopen},\;
\operatorname{Nonzero}(f)
\Longrightarrow
\exists s:\operatorname{Clopen},\;
\operatorname{Nonzero}(f\wedge s)
\land
\operatorname{Nonzero}(f\wedge s').
$$

It then lifts the same result to arbitrary-key tables:

$$
\forall K,\;\forall T:K\to\operatorname{Clopen},\;\forall k:K,\;
\operatorname{Nonzero}(T(k))
$$

$$
\Longrightarrow
\exists s:\operatorname{Clopen},\;
\operatorname{Nonzero}\bigl(\operatorname{setAt}(T,k,T(k)\wedge s)(k)\bigr)
\land
\operatorname{Nonzero}\bigl(\operatorname{setAt}(T,k,T(k)\wedge s')(k)\bigr).
$$

Standard reading:

If a semantic clopen table value is nonzero, it can be split into two nonzero
semantic clopen pieces. If a table indexed by an arbitrary key type has such a
value at key $k$, the value at $k$ can be replaced by either split piece,
and both replacements remain nonzero at $k$.

This is stronger than the earlier raw-tree result because the theorem is stated
at the semantic `Clopen` subtype level. It is still not recurrence, countable
supremum closure, NSO semantics, or Tau lowering.

Claude c020 then assembles this layer into one self-contained file. Its headline
theorem is:

$$
\forall K,\;\forall T:K\to\operatorname{Clopen},\;\forall k:K,\;
T(k)\ne\bot_{\operatorname{Clopen}}
\Longrightarrow
\exists s:\operatorname{Clopen},\;
T(k)\wedge s\ne\bot_{\operatorname{Clopen}}
\land
T(k)\wedge s'\ne\bot_{\operatorname{Clopen}}.
$$

It also checks the concrete table laws for `setAt` and `commonTables`:

$$
\operatorname{setAt}(\operatorname{setAt}(T,k,v_1),k,v_2)
=
\operatorname{setAt}(T,k,v_2),
$$

$$
k_1\ne k_2
\Longrightarrow
\operatorname{setAt}(\operatorname{setAt}(T,k_1,v_1),k_2,v_2)
=
\operatorname{setAt}(\operatorname{setAt}(T,k_2,v_2),k_1,v_1),
$$

and the three pointwise common laws:

$$
\operatorname{commonTables}(T,T)=T,
$$

$$
\operatorname{commonTables}(T_1,T_2)
=
\operatorname{commonTables}(T_2,T_1),
$$

$$
\operatorname{commonTables}(T_1,\operatorname{commonTables}(T_2,T_3))
=
\operatorname{commonTables}(\operatorname{commonTables}(T_1,T_2),T_3).
$$

Standard reading:

At the algebraic table-value layer, tables may have arbitrary key type $K$,
and values live in the semantic `Clopen` carrier. Updating the same key twice
keeps the second update, updates to different keys commute, common is pointwise
meet, and any nonzero table entry can be split into two nonzero clopen parts.

This is the operationally assembled "atomless infinite table" result for the
non-recursive algebraic table layer. It is still not the completed TABA table
language because recurrence, countable suprema, NSO, automata equivalence, and
Tau lowering are outside the c020 theorem surface.

Claude c021 adds the finite-prefix adequacy theorem for the same Cantor clopen
syntax:

$$
\left(
\forall n,\;n < \operatorname{depth}(c)\Longrightarrow s_1(n)=s_2(n)
\right)
\Longrightarrow
\operatorname{eval}(c,s_1)=\operatorname{eval}(c,s_2).
$$

Standard reading:

If two Boolean streams agree on every position below the structural depth of the
Cantor tree $c$, then evaluating $c$ on the first stream gives the same
Boolean result as evaluating $c$ on the second stream.

The depth equation is structural:

$$
\operatorname{depth}(\bot)=0,\qquad
\operatorname{depth}(\top)=0,\qquad
\operatorname{depth}(\operatorname{node}(L,R))
=1+\max(\operatorname{depth}(L),\operatorname{depth}(R)).
$$

Standard reading:

Bottom and top read no input bits. A branch node reads one bit and then needs
enough depth for the deeper child.

This is not a Muller-automaton theorem. It is the finite-prefix theorem needed
before constructing an explicit finite automaton: every Cantor clopen can be
decided after a bounded number of stream bits.

The c022 recurrence bridge then isolates one exact abstract condition for a
least-fixed-point completion lane after c020 and c021:

$$
\operatorname{Table}_K(\alpha):=K\to\alpha.
$$

Standard reading:

A table with keys in $K$ and values in $\alpha$ is a function assigning one
$\alpha$-value to each key.

If $\alpha$ is a complete Boolean algebra, countable table suprema are
pointwise:

$$
\left(\bigvee_{n < \omega}X_n\right)(k)
=
\bigvee_{n < \omega}X_n(k).
$$

Standard reading:

The value at key $k$ of the countable join of tables is the countable join of
the values that the tables assign to $k$.

The omega-continuity condition used by c022 is:

$$
X_n\le X_{n+1}\;\text{for all }n
\Longrightarrow
F\left(\bigvee_{n < \omega}X_n\right)
=
\bigvee_{n < \omega}F(X_n).
$$

Standard reading:

For every increasing omega-chain $X_0,X_1,\ldots$, applying $F$ after taking
the chain supremum gives the same result as applying $F$ at every finite stage
and then taking the supremum.

The finite approximants are:

$$
X_0=\bot,\qquad X_{n+1}=F(X_n),
\qquad
\mu_\omega F:=\bigvee_{n < \omega}X_n.
$$

c022 proves:

$$
\operatorname{Monotone}(F)
\land
\omega\operatorname{-Cont}(F)
\Longrightarrow
F(\mu_\omega F)=\mu_\omega F.
$$

Standard reading:

If $F$ preserves order and commutes with increasing omega-chain suprema, then
the supremum of its finite approximants is a fixed point of $F$.

c022 also proves the rewrite-certificate bridge:

$$
\left(\forall n,\;F^n(\bot)=G^n(\bot)\right)
\Longrightarrow
\mu_\omega F=\mu_\omega G.
$$

Standard reading:

If two recursive bodies produce the same finite approximant at every finite
stage, then their omega-supremum semantics are equal.

This is a semantic shape that can lift v401-style finite-approximant equality
into omega-supremum equality if the completed carrier and omega-continuity
premises are supplied. It is not a claim that TABA 0.25 defines recurrence by
least fixed points. The TABA recurrence section describes finite
equivalence/loop detection and fallback behavior; c022 is a standard
least-fixed-point completion lane. It is still conditional: c022 does not
instantiate a final concrete complete atomless carrier, does not prove NSO
semantics, and does not lower recurrence tables into Tau runtime code.

v472 supplies one concrete positive transformer for the c022 lane. The checked
positive expression grammar is:

$$
e ::=
\bot
\mid \top
\mid \operatorname{const}(v)
\mid \operatorname{ref}(i)
\mid e_1\wedge e_2
\mid e_1\vee e_2.
$$

Standard reading:

A positive expression is built from bottom, top, a constant value, a component
reference, meet, and join.

The missing constructor is intentional:

$$
e' \notin \mathrm{PosExpr}.
$$

Standard reading:

Prime is not part of the same-stratum positive expression language.

The reason is semantic, not cosmetic. Meet and join are monotone. Prime is
anti-monotone:

$$
a\le b\Longrightarrow b'\le a'.
$$

Standard reading:

If $a$ is below $b$, then the prime of $b$ is below the prime of $a$.
The order reverses.

The monotonicity theorem for positive expressions is:

$$
S\le T
\Longrightarrow
\llbracket e\rrbracket_S
\le
\llbracket e\rrbracket_T.
$$

Standard reading:

If every component value in state $S$ is below the corresponding component
value in state $T$, then evaluating a positive expression in $S$ gives a
value below the result of evaluating the same expression in $T$.

The omega-continuity theorem is:

$$
\left(\forall n,\;S_n\le S_{n+1}\right)
\Longrightarrow
\llbracket e\rrbracket_{\bigvee_{n < \omega}S_n}
=
\bigvee_{n < \omega}\llbracket e\rrbracket_{S_n}.
$$

Standard reading:

For every increasing omega-chain of states, evaluating a positive expression
after taking the chain supremum is the same as evaluating it at every finite
stage and then taking the supremum of those values.

The compiled simultaneous update is:

$$
F_B(S)(i):=\llbracket B(i)\rrbracket_S.
$$

Standard reading:

The update transformer $F_B$ assigns to component $i$ the value obtained by
evaluating the body expression $B(i)$ in the old state $S$.

v472 proves:

$$
F_B\left(\bigvee_{n < \omega}S_n\right)
=
\bigvee_{n < \omega}F_B(S_n)
$$

for every increasing chain $S_0\le S_1\le\cdots$. It then instantiates the
omega fixed-point construction:

$$
\mu_\omega F_B:=\bigvee_{n < \omega}F_B^n(\bot),
\qquad
F_B(\mu_\omega F_B)=\mu_\omega F_B.
$$

v473 moves one step from formulas toward table syntax by adding positive
guarded rows. A row has a positive guard and a positive value expression:

$$
r=(g_r,v_r).
$$

Standard reading:

A row $r$ is a pair. The first component $g_r$ is its guard expression, and
the second component $v_r$ is its value expression.

Its semantic value in state $S$ is:

$$
\llbracket r\rrbracket_S
:=
\llbracket g_r\rrbracket_S
\wedge
\llbracket v_r\rrbracket_S.
$$

Standard reading:

The value of a row in state $S$ is the meet of the guard value and the row
value. The row contributes only the part of the value that lies inside the
guard.

For a finite row list $R$, v473 uses guarded-join semantics:

$$
\llbracket R\rrbracket_S
:=
\bigvee_{r\in R}
\left(
\llbracket g_r\rrbracket_S
\wedge
\llbracket v_r\rrbracket_S
\right).
$$

Standard reading:

The value of a finite row list in state $S$ is the join of all guarded row
contributions.

Reading trap:

This is not priority-row semantics and not first-match table semantics. It is
finite guarded-join semantics. If two guards overlap, the overlap contributes
the join of the overlapping row values. Priority behavior would need another
normalization theorem or a different semantic definition.

v473 proves the row-list continuity theorem:

$$
\left(\forall n,\;S_n\le S_{n+1}\right)
\Longrightarrow
\llbracket R\rrbracket_{\bigvee_{n < \omega}S_n}
=
\bigvee_{n < \omega}\llbracket R\rrbracket_{S_n}.
$$

Standard reading:

For every increasing omega-chain of states, evaluating a finite positive row
list after taking the chain supremum is the same as evaluating the row list at
every finite stage and then taking the supremum of those row-list values.

The simultaneous row update is:

$$
F_B(S)(i):=\llbracket B(i)\rrbracket_S.
$$

Standard reading:

The row-update transformer $F_B$ assigns to component $i$ the value obtained
by evaluating the finite row list $B(i)$ in the old state $S$.

v473 proves:

$$
F_B\left(\bigvee_{n < \omega}S_n\right)
=
\bigvee_{n < \omega}F_B(S_n)
$$

for every increasing chain $S_0\le S_1\le\cdots$. It then proves:

$$
F_B\left(\bigvee_{n < \omega}F_B^n(\bot)\right)
=
\bigvee_{n < \omega}F_B^n(\bot).
$$

Standard reading:

The omega-supremum of finite approximants is a fixed point for simultaneous
updates compiled from finite positive guarded-row lists.

Boundary:

This is still not full TABA table semantics. It does not include same-stratum
prime, CBFs, NSO, priority rows, first-match rows, disjoint-row normalization,
automata lowering, or Tau runtime lowering.

v474 separates two meanings that are easy to confuse. Same-stratum prime is not
allowed in the positive recurrence kernel. Prime applied to a fixed lower
stratum is different, because the lower stratum is already completed before the
current recurrence step is evaluated.

Let $E:L\to A$ be a lower-stratum environment. The stratified-prime
constructor is interpreted as:

$$
\llbracket \operatorname{lowerPrime}(\ell)\rrbracket_{E,S}
:=
E(\ell)'.
$$

Standard reading:

The expression $\operatorname{lowerPrime}(\ell)$ evaluates to the prime of
the lower-stratum value $E(\ell)$. It does not take the prime of a current
state component.

Reading trap:

This is not the same as $\operatorname{ref}(i)'$. The expression
$\operatorname{ref}(i)'$ would apply prime to the current recursive state, and
that reverses order. The expression $\operatorname{lowerPrime}(\ell)$ is
constant with respect to the current state.

The independence law is:

$$
\llbracket \operatorname{lowerPrime}(\ell)\rrbracket_{E,S}
=
\llbracket \operatorname{lowerPrime}(\ell)\rrbracket_{E,T}.
$$

Standard reading:

Changing the current state from $S$ to $T$ does not change a lower-prime
term, because its value is determined by $E$, not by the current state.

v474 proves omega-continuity for expressions with positive current references
and lower-stratum prime:

$$
\left(\forall n,\;S_n\le S_{n+1}\right)
\Longrightarrow
\llbracket e\rrbracket_{E,\bigvee_{n < \omega}S_n}
=
\bigvee_{n < \omega}\llbracket e\rrbracket_{E,S_n}.
$$

Standard reading:

For every increasing omega-chain of current states, evaluating a stratified
expression after taking the current-state supremum is the same as evaluating it
at every finite stage and then taking the supremum of those values.

For simultaneous updates,

$$
F_{E,B}(S)(i):=\llbracket B(i)\rrbracket_{E,S},
$$

v474 proves:

$$
F_{E,B}\left(\bigvee_{n < \omega}F_{E,B}^n(\bot)\right)
=
\bigvee_{n < \omega}F_{E,B}^n(\bot).
$$

Standard reading:

When prime only points to completed lower-stratum values, the omega-supremum of
finite approximants is still a fixed point for the current stratum.

Boundary:

This does not make same-stratum prime safe. It proves a stratification rule:
prime is safe in this recurrence proof only when it reads from a fixed
lower-stratum environment.

v475 combines v473 and v474. A stratified row still has a guard and a value:

$$
r=(g_r,v_r).
$$

Now the guard and value may mention both current positive references and
lower-stratum prime terms. The row semantics is:

$$
\llbracket r\rrbracket_{E,S}
:=
\llbracket g_r\rrbracket_{E,S}
\wedge
\llbracket v_r\rrbracket_{E,S}.
$$

Standard reading:

The row contributes the meet of its stratified guard value and its stratified
row value. Lower-prime subterms read from $E$, while current references read
from $S$.

For a finite row list $R$:

$$
\llbracket R\rrbracket_{E,S}
:=
\bigvee_{r\in R}
\left(
\llbracket g_r\rrbracket_{E,S}
\wedge
\llbracket v_r\rrbracket_{E,S}
\right).
$$

Standard reading:

The row-list value is the join of all guarded contributions, with each
contribution evaluated against the fixed lower environment $E$ and the
current state $S$.

v475 proves:

$$
\left(\forall n,\;S_n\le S_{n+1}\right)
\Longrightarrow
\llbracket R\rrbracket_{E,\bigvee_{n < \omega}S_n}
=
\bigvee_{n < \omega}\llbracket R\rrbracket_{E,S_n}.
$$

Standard reading:

For every increasing omega-chain of current states, evaluating the stratified
row list after taking the current-state supremum is the same as evaluating it
at every finite stage and then taking the supremum of those values.

For simultaneous row updates,

$$
F_{E,B}(S)(i):=\llbracket B(i)\rrbracket_{E,S},
$$

v475 proves:

$$
F_{E,B}\left(\bigvee_{n < \omega}F_{E,B}^n(\bot)\right)
=
\bigvee_{n < \omega}F_{E,B}^n(\bot).
$$

Standard reading:

Finite stratified guarded-row updates have an omega-supremum fixed point when
prime is restricted to fixed lower-stratum values.

Reading trap:

This still does not define full TABA table semantics. It is guarded-join row
semantics, not priority-row or first-match semantics, and it does not prove
disjoint-row normalization.

v476 adds the fixed-guard priority normal form. For a row list
$R=[(g_i,v_i)]_{i < m}$, define the effective guard of row $i$ as:

$$
h_i
:=
g_i
\wedge
\bigwedge_{j < i} g_j'.
$$

Standard reading:

The effective guard $h_i$ is the original guard $g_i$, restricted to the
part of the Boolean space not already claimed by any earlier guard.

The normalized guarded-join value is:

$$
\operatorname{JoinNorm}(R)
:=
\bigvee_{i < m}(h_i\wedge v_i).
$$

Standard reading:

The normalized value is the join of all row values, but each row value is
restricted to its effective guard.

v476 proves:

$$
\operatorname{JoinNorm}(R)
=
\operatorname{PriorityEval}(R).
$$

Standard reading:

For fixed Boolean-algebra guards and values, disjointizing the guards preserves
the value of priority evaluation.

Reading trap:

This proof is not a recurrence theorem. It is a pointwise normalization theorem
for fixed guards and fixed values. If guards depend on the current recursive
state, the primes $g_j'$ can become same-stratum negative dependencies.

v477 proves the corresponding safe recurrence fragment. In v477, priority
guards are fixed Boolean-algebra values, while row values may depend positively
on the current state and may use lower-stratum prime. The priority semantics is:

$$
\llbracket []\rrbracket_{E,S}:=\bot,
$$

$$
\llbracket (g,e)::R\rrbracket_{E,S}
:=
\left(g\wedge\llbracket e\rrbracket_{E,S}\right)
\vee
\left(g'\wedge\llbracket R\rrbracket_{E,S}\right).
$$

Standard reading:

An empty priority list evaluates to bottom. A nonempty priority list first takes
the part of the head value inside the fixed guard $g$, then evaluates the tail
only outside $g$.

v477 proves:

$$
\left(\forall n,\;S_n\le S_{n+1}\right)
\Longrightarrow
\llbracket R\rrbracket_{E,\bigvee_{n < \omega}S_n}
=
\bigvee_{n < \omega}\llbracket R\rrbracket_{E,S_n}.
$$

Standard reading:

For every increasing omega-chain of current states, fixed-guard priority
evaluation after taking the current-state supremum is the same as evaluating at
every finite stage and then taking the supremum of those values.

For simultaneous updates,

$$
F_{E,B}(S)(i):=\llbracket B(i)\rrbracket_{E,S},
$$

v477 proves:

$$
F_{E,B}\left(\bigvee_{n < \omega}F_{E,B}^n(\bot)\right)
=
\bigvee_{n < \omega}F_{E,B}^n(\bot).
$$

Standard reading:

Fixed-guard priority row updates have an omega-supremum fixed point when row
values remain positive in the current state and prime only reads from fixed
lower-stratum data.

Reading trap:

The guard $g$ is fixed. This theorem does not allow a priority guard such as
$g(S)$ that changes with the current recursive state.

v479 is the next safe widening. Instead of requiring $g$ to be a raw fixed
Boolean-algebra value, it allows $g$ to be evaluated from a guard-only
lower-stratum expression:

$$
\gamma ::= 0 \mid 1 \mid c \mid \ell \mid \ell' \mid
(\gamma\wedge\gamma) \mid (\gamma\vee\gamma).
$$

The priority rule becomes:

$$
\llbracket []\rrbracket_{E,S}:=\bot,
$$

$$
\llbracket (\gamma,e)::R\rrbracket_{E,S}
:=
\left(\llbracket\gamma\rrbracket_E\wedge
\llbracket e\rrbracket_{E,S}\right)
\vee
\left(\llbracket\gamma\rrbracket_E'
\wedge\llbracket R\rrbracket_{E,S}\right).
$$

Standard reading:

An empty priority list evaluates to bottom. A nonempty priority list evaluates
the guard $\gamma$ from the lower-stratum environment $E$, takes the head
value inside that guard, and evaluates the tail only outside that guard.

Plain English:

The guard is allowed to be a small lower-stratum formula, not just a literal
fixed value. It still cannot inspect the current recursive table state.

v479 proves:

$$
\left(\forall n,\;S_n\le S_{n+1}\right)
\Longrightarrow
\llbracket R\rrbracket_{E,\bigvee_{n < \omega}S_n}
=
\bigvee_{n < \omega}\llbracket R\rrbracket_{E,S_n}.
$$

Standard reading:

For every increasing omega-chain of current states, priority evaluation with
lower-stratum guards after taking the current-state supremum is equal to the
supremum of priority evaluations at each finite stage.

Reading trap:

The expression $\llbracket\gamma\rrbracket_E$ has no $S$ subscript. That is
the entire point. The guard is lower-stratum data during the current recurrence
proof, so its prime is not same-stratum negation.

v480 then proves the pointwise normal-form bridge. Define materialization by:

$$
\operatorname{mat}_{E,S}(\gamma,e)
:=
\left(\llbracket\gamma\rrbracket_E,\;
\llbracket e\rrbracket_{E,S}\right).
$$

For a priority row list $R$, let
$\operatorname{mat}_{E,S}(R)$ be the row list obtained by materializing each
row. Then v480 proves:

$$
\operatorname{EvalJoin}
\left(
\operatorname{disjointize}(\operatorname{mat}_{E,S}(R))
\right)
=
\llbracket R\rrbracket_{E,S}.
$$

Standard reading:

For any fixed lower environment and current state, materialize the lower-guard
priority rows into ordinary Boolean-algebra rows. If those ordinary rows are
disjointized, guarded-join evaluation of the normal form is equal to the
original lower-guard priority evaluation.

Reading trap:

This is pointwise normalization. It is not the omega-continuity theorem. The
recurrence theorem is v479. The normal-form theorem is v480.

v481 packages the fragment as a small table syntax. A restricted table is:

$$
T := (R,d),
$$

where $R$ is a finite list of priority rows and $d$ is an explicit default
value. The compiler appends the default as a final top-guarded row:

$$
\operatorname{compile}(R,d)
:=
\operatorname{compileRows}(R)\mathbin{+\!\!+}
\left[(1,\operatorname{compileVal}(d))\right].
$$

Standard reading:

Compiling a restricted table means compiling each priority row and then adding
one final row whose guard is top and whose value is the default. That final row
fires exactly when no earlier priority row has captured the point.

v481 proves the compiler theorem:

$$
\llbracket \operatorname{compile}(T)\rrbracket_{E,S}^{\operatorname{prio}}
=
\llbracket T\rrbracket_{E,S}^{\operatorname{table}}.
$$

Standard reading:

For every lower environment $E$, current state $S$, and restricted table
$T$, evaluating the compiled priority-row kernel gives the same Boolean
algebra value as evaluating the surface table.

Plain English:

This is the first checked syntax-to-semantics bridge for the safe infinite
fragment. It is still a restricted syntax, but it is no longer just raw semantic
rows.

For simultaneous restricted-table updates,

$$
F_{E,B}(S)(i):=\llbracket B(i)\rrbracket_{E,S}^{\operatorname{table}},
$$

v481 proves:

$$
F_{E,B}\left(\bigvee_{n < \omega}F_{E,B}^{n}(\bot)\right)
=
\bigvee_{n < \omega}F_{E,B}^{n}(\bot).
$$

Standard reading:

If every component body is written in the restricted table syntax, the
omega-supremum of the finite approximants from bottom is a fixed point of the
simultaneous table-update transformer.

Reading trap:

This theorem proves the restricted table syntax only. It does not admit
same-stratum prime, current-state-dependent guards, CBFs, NSO, or Tau runtime
lowering.

Standard reading:

The least omega-supremum candidate generated by repeatedly applying a positive
formula update from bottom is a fixed point of that update transformer.

This is the first checked infinite-recurrence bridge for an actual formula
fragment. It is still not full infinite tables. It does not include prime,
stratified negation, CBFs, table rows, NSO semantics, automata lowering, or Tau
runtime integration.

c023 closes a negative boundary around the simple powerset reference carrier.
Let $\Omega := \mathbb{N}\to\mathbb{B}$. Then:

$$
\neg\operatorname{HasSplitters}(\mathcal{P}(\Omega)).
$$

The local obstruction is:

$$
\forall x\in\Omega,\;
\neg\exists s\subseteq\Omega,\;
\{x\}\cap s\ne\varnothing
\land
\{x\}\cap s'\ne\varnothing.
$$

Standard reading:

For any single stream $x$, no subset $s$ can split the singleton set
$\{x\}$ into two nonempty pieces. Either $x\in s$, in which case
$\{x\}\cap s'$ is empty, or $x\notin s$, in which case
$\{x\}\cap s$ is empty.

This matters because the powerset carrier is closed under arbitrary unions, but
it is atomic. It can serve as a reference semantics for sets of streams, but it
cannot be the final atomless value carrier if the table semantics requires the
TABA splitter property.

c024 formalizes the recurrence-loop core that is closer to the TABA 0.25 draft.
Let $\alpha$ be a finite semantic quotient, let $F:\alpha\to\alpha$ be a
deterministic recurrence step, and define:

$$
x_0=a,\qquad x_{n+1}=F(x_n).
$$

Standard reading:

The recurrence starts at initial semantic state $a$. Each next state is
obtained by applying the deterministic recurrence transformer $F$ to the
previous state.

c024 proves the finite loop guarantee:

$$
\operatorname{Finite}(\alpha)
\Longrightarrow
\exists i,j,\;
i < j\le|\alpha|
\land
x_i=x_j.
$$

Standard reading:

If there are only finitely many semantic states, then among the first
$|\alpha|+1$ samples of the recurrence sequence, two samples must denote the
same semantic state.

The adjacent-loop theorem is:

$$
x_i=x_{i+1}\Longrightarrow F(x_i)=x_i.
$$

Standard reading:

If the recurrence reaches the same semantic state in two adjacent steps, then
that state is a fixed point of the recurrence transformer.

The deterministic periodicity theorem is:

$$
x_i=x_j
\Longrightarrow
\forall t,\;x_{i+t}=x_{j+t}.
$$

Standard reading:

If two samples in a deterministic recurrence are equal, then the two tails that
start from those samples remain equal step by step.

The conservative resolver checked in c024 is:

$$
\operatorname{resolve}(i,j)=
\begin{cases}
\operatorname{fixed}(x_i), & j=i+1,\\
\operatorname{fallback}(d), & j\ne i+1.
\end{cases}
$$

and its soundness theorem is:

$$
\operatorname{resolve}(i,j)=\operatorname{fixed}(x)
\Longrightarrow
F(x)=x.
$$

Standard reading:

The resolver reports a fixed point only when the loop is adjacent. If the loop
has period greater than one, it does not pretend that a fixed point was found;
it returns the explicit fallback value.

This c024 lane does not solve the whole TABA recurrence section. It does not yet
formalize mutual recurrence, dependency-graph acyclicity, formulas versus CBFs,
multi-index recurrence, or Tau lowering. It does give the checked finite
semantic loop core that the fuller recurrence semantics can target.

c025 adds the first mutual-recurrence lift. For two semantic component carriers
$\alpha$ and $\beta$, define the product semantic state:

$$
\operatorname{State}:=\alpha\times\beta.
$$

Standard reading:

A mutually recursive pair of definitions can be represented by one state whose
first projection is the first component and whose second projection is the
second component.

The product-state recurrence is:

$$
S_0=(a,b),\qquad S_{n+1}=F(S_n).
$$

If the product state has an adjacent loop:

$$
S_i=S_{i+1},
$$

then both components are fixed:

$$
\pi_1(F(S_i))=\pi_1(S_i)
\qquad\land\qquad
\pi_2(F(S_i))=\pi_2(S_i).
$$

Standard reading:

If the whole pair of mutually recursive semantic values stops changing, then
the first component has stopped changing and the second component has stopped
changing.

The bounded-loop theorem is:

$$
\operatorname{Finite}(\alpha)\land\operatorname{Finite}(\beta)
\Longrightarrow
\exists i,j,\;
i < j\le|\alpha\times\beta|
\land
S_i=S_j.
$$

Standard reading:

If both component semantic carriers are finite, the product carrier is finite.
Therefore a deterministic mutual recurrence over the product carrier must repeat
a semantic product state within the finite pigeonhole bound.

This does not yet prove TABA's full mutual recurrence syntax. It proves the
semantic move that justifies compiling a mutually recursive block into one
product-state recurrence after the dependency graph and schedule have been
validated.

c026 removes the two-component restriction. Let $I$ be a finite index family,
let $\alpha_i$ be the semantic carrier for component $i$, and define the
compiled family state:

$$
\operatorname{State}:=\prod_{i\in I}\alpha_i.
$$

Standard reading:

The state of a finite mutually recursive block is one tuple-like object. Its
$i$-th projection is the current semantic value of component $i$.

The recurrence is still one deterministic orbit:

$$
S_0=a,\qquad S_{n+1}=F(S_n).
$$

The finite-family loop guarantee is:

$$
\operatorname{Finite}(\operatorname{State})
\Longrightarrow
\exists i,j,\;
i < j\le|\operatorname{State}|
\land
S_i=S_j.
$$

Standard reading:

If the compiled family-state carrier is finite, then a deterministic recurrence
over that carrier must repeat a semantic family state within the finite
pigeonhole bound.

The Lean theorem is deliberately stated at the compiled-state level:
`Fintype State` is the premise. In ordinary finite-table fragments, finite
component carriers over a finite index set supply that premise, but the checked
loop theorem itself only needs the finite compiled carrier.

The component fixed-point law is:

$$
S_i=S_{i+1}
\Longrightarrow
\forall r\in I,\;
F(S_i)(r)=S_i(r).
$$

Standard reading:

If the whole finite family state stops changing between two adjacent recurrence
steps, then every component projection is fixed at that same step.

The component periodic-tail law is:

$$
S_i=S_j
\Longrightarrow
\forall t\in\mathbb{N}\;\forall r\in I,\;
S_{i+t}(r)=S_{j+t}(r).
$$

Standard reading:

If two family states are equal at different recurrence steps, then every
component repeats along the two future tails with the same offset.

This still does not prove the parser, dependency graph, schedule checker,
formula/CBF quotient compiler, multi-index recurrence semantics, or Tau runtime
lowering. It proves the finite semantic kernel those pieces should target.

c027 adds the first schedule layer. A component update is represented by a
target index and an extensional state transformer:

$$
u=(\operatorname{target}(u),\operatorname{next}_u).
$$

The preservation law for one update is:

$$
r\ne\operatorname{target}(u)
\Longrightarrow
\operatorname{next}_u(S)(r)=S(r).
$$

Standard reading:

If update $u$ targets some component other than $r$, then applying that
update does not change the $r$-component of the family state.

A finite schedule is a list of updates:

$$
\Gamma=[u_0,u_1,\ldots,u_{m-1}].
$$

The schedule evaluator is left-to-right composition:

$$
\operatorname{evalSchedule}([],S)=S,
\qquad
\operatorname{evalSchedule}(u::\Gamma,S)
=
\operatorname{evalSchedule}(\Gamma,\operatorname{next}_u(S)).
$$

Standard reading:

An empty schedule leaves the state unchanged. A nonempty schedule applies the
first update, then evaluates the remaining schedule on the updated state.

c027 proves the absent-component law:

$$
r\notin\{\operatorname{target}(u):u\in\Gamma\}
\Longrightarrow
\operatorname{evalSchedule}(\Gamma,S)(r)=S(r).
$$

Standard reading:

If no update in the schedule targets component $r$, then running the whole
schedule leaves component $r$ unchanged.

The scheduled recurrence is:

$$
S_0=a,
\qquad
S_{n+1}=\operatorname{evalSchedule}(\Gamma,S_n).
$$

c027 proves the same finite-loop law for this scheduled recurrence:

$$
\operatorname{Finite}(\operatorname{State})
\Longrightarrow
\exists i,j,\;
i < j\le|\operatorname{State}|
\land
S_i=S_j.
$$

Standard reading:

Once the schedule has been supplied as a finite list of semantic updates, it is
one deterministic transformer over the family state. Therefore the same finite
pigeonhole recurrence theorem applies.

c027 still does not extract the dependency graph from TABA syntax, prove a
topological sort, compile formulas or CBFs into updates, handle multi-index
recurrence, or lower this into Tau runtime code.

c028 adds a checker for the next boundary. Define:

$$
\operatorname{Before}(a,b,\Gamma)
\;:\Longleftrightarrow\;
\exists P,Q,\;
\Gamma=P\mathbin{+\!\!+}[a]\mathbin{+\!\!+}Q
\land
b\in Q.
$$

Standard reading:

$\operatorname{Before}(a,b,\Gamma)$ means that the finite order $\Gamma$ contains an
occurrence of $a$, and later in the remaining suffix contains $b$.

Given a dependency map $\operatorname{deps}$, a target order $\Gamma$ is
valid when:

$$
\operatorname{ValidTopo}(\operatorname{deps},\Gamma)
\;:\Longleftrightarrow\;
\forall n,d,\;
n\in\Gamma
\land
d\in\operatorname{deps}(n)
\Longrightarrow
\operatorname{Before}(d,n,\Gamma).
$$

Standard reading:

For every component $n$ listed in the order, every declared dependency $d$
of $n$ must occur before $n$ in that order.

The schedule certificate ties the semantic schedule to the target order:

$$
\operatorname{targets}(\operatorname{schedule})=\Gamma.
$$

c028 proves:

$$
u\in\operatorname{schedule}
\land
d\in\operatorname{deps}(\operatorname{target}(u))
\Longrightarrow
\operatorname{Before}(d,\operatorname{target}(u),\Gamma).
$$

Standard reading:

For every concrete update in the schedule, every declared dependency of that
update's target appears before the target in the certified order.

c028 is still a checker, not a schedule generator. It does not extract
dependencies from formulas, construct a topological order, compile formulas or
CBFs into update functions, handle multi-index recurrence, or lower schedules
into Tau runtime code.

c029 makes the topological-order certificate construction-shaped. Define:

$$
\operatorname{PrefixReady}(\operatorname{deps},\Gamma)
\;:\Longleftrightarrow\;
\forall P,n,Q,\;
\Gamma=P\mathbin{+\!\!+}[n]\mathbin{+\!\!+}Q
\Longrightarrow
\forall d,\;
d\in\operatorname{deps}(n)
\Longrightarrow
d\in P.
$$

Standard reading:

At every position in the emitted order, all declared dependencies of the current
node are already present in the prefix before that node.

c029 proves:

$$
\operatorname{PrefixReady}(\operatorname{deps},\Gamma)
\Longrightarrow
\operatorname{ValidTopo}(\operatorname{deps},\Gamma).
$$

Standard reading:

If the order was built by only emitting ready nodes, then every dependency of
every listed node occurs before that node in the order.

The construction-shaped certificate also carries:

$$
\operatorname{NoDup}(\Gamma).
$$

Standard reading:

The certified target order does not hide repeated component targets.

c029 still does not extract dependencies from formulas, implement the search
procedure that finds a ready node, prove failure means a cycle exists, compile
formulas or CBFs into update functions, handle multi-index recurrence, or lower
the result into Tau runtime code.

c030 adds the first formula dependency extractor. The formula fragment is:

$$
e ::= c
\mid \operatorname{ref}(i)
\mid \neg e
\mid e_1\land e_2
\mid e_1\lor e_2.
$$

The extractor is:

$$
\begin{aligned}
\operatorname{deps}(c)&:=[],\\
\operatorname{deps}(\operatorname{ref}(i))&:=[i],\\
\operatorname{deps}(\neg e)&:=\operatorname{deps}(e),\\
\operatorname{deps}(e_1\land e_2)&:=\operatorname{deps}(e_1)\mathbin{+\!\!+}\operatorname{deps}(e_2),\\
\operatorname{deps}(e_1\lor e_2)&:=\operatorname{deps}(e_1)\mathbin{+\!\!+}\operatorname{deps}(e_2).
\end{aligned}
$$

Standard reading:

Constants introduce no component dependencies. A reference introduces exactly
that component as a dependency. Negation preserves the dependencies of its
subformula. Conjunction and disjunction combine the dependencies of their two
subformulas.

c030 proves exactness:

$$
\operatorname{Occurs}(i,e)
\Longleftrightarrow
i\in\operatorname{deps}(e).
$$

Standard reading:

Component $i$ occurs syntactically in expression $e$ exactly when $i$ is
listed by the dependency extractor for $e$.

For a finite family of formula bodies:

$$
\operatorname{formulaDeps}(\operatorname{body},n)
:=
\operatorname{deps}(\operatorname{body}(n)).
$$

c030 proves:

$$
\operatorname{Occurs}(d,\operatorname{body}(n))
\Longleftrightarrow
d\in\operatorname{formulaDeps}(\operatorname{body},n).
$$

Standard reading:

A component $d$ occurs in the body of component $n$ exactly when $d$ is
recorded as a dependency of $n$.

c030 is not the full TABA formula language and not the CBF quotient language. It
does not prove semantic dependence minimization, formula-to-update compilation,
multi-index recurrence, or Tau runtime lowering.

c031 composes c030 with the prefix-order theorem. The bridge theorem is:

$$
\operatorname{PrefixReady}(\operatorname{formulaDeps}(\operatorname{body}),\Gamma)
\Longrightarrow
\operatorname{ValidTopo}(\operatorname{formulaDeps}(\operatorname{body}),\Gamma).
$$

Standard reading:

If the target order is prefix-ready for dependencies extracted from formula
bodies, then the order is topologically valid for those formula-derived
dependencies.

c031 also proves:

$$
\operatorname{PrefixReady}(\operatorname{formulaDeps}(\operatorname{body}),\Gamma)
\land
n\in\Gamma
\land
\operatorname{Occurs}(d,\operatorname{body}(n))
\Longrightarrow
\operatorname{Before}(d,n,\Gamma).
$$

Standard reading:

If component $d$ occurs syntactically in the formula body for component $n$,
and the order is prefix-ready for formula-derived dependencies, then $d$
appears before $n$ in the order.

c031 still uses the small formula fragment. It does not cover the full TABA
formula or CBF language, semantic dependence minimization, formula-to-update
compilation, multi-index recurrence, or Tau runtime lowering.

c032 packages the finite toy fragment as one certificate. A certificate contains:

$$
\operatorname{order},\quad
\operatorname{schedule},\quad
\operatorname{targets}(\operatorname{schedule})=\operatorname{order},\quad
\operatorname{NoDup}(\operatorname{order}),\quad
\operatorname{PrefixReady}(\operatorname{formulaDeps}(\operatorname{body}),\operatorname{order}).
$$

Standard reading:

The certificate stores a target order, a semantic schedule, an exact equality
between the schedule targets and the order, a proof that the order has no
duplicate targets, and a proof that every formula-derived dependency is already
available before its target is emitted.

c032 proves:

$$
u\in\operatorname{schedule}
\land
\operatorname{Occurs}(d,\operatorname{body}(\operatorname{target}(u)))
\Longrightarrow
\operatorname{Before}(d,\operatorname{target}(u),\operatorname{order}).
$$

Standard reading:

For every scheduled update, every syntactic reference in that update target's
formula body appears before the update target in the certified order.

c032 also proves the bounded scheduled recurrence theorem:

$$
\operatorname{Finite}(\operatorname{State})
\Longrightarrow
\exists i,j,\;
i < j\le|\operatorname{State}|
\land
S_i=S_j,
\qquad
S_{n+1}:=\operatorname{evalSchedule}(\operatorname{schedule},S_n).
$$

Standard reading:

For this finite certified formula-schedule fragment, once the compiled family
state is finite, repeated schedule execution must revisit a semantic state
within the finite pigeonhole bound.

This is the strongest finite toy-kernel assembly so far. It still does not
solve full TABA tables, because it does not cover the full TABA formula or CBF
language, formula-to-update compilation, semantic-dependence minimization,
multi-index recurrence, atomless infinite recurrence, or Tau runtime lowering.

c033 adds the first formula-to-update compiler for the Boolean toy carrier. A
Boolean state is:

$$
S:I\to\{\bot,\top\}.
$$

For a formula body map $\operatorname{body}:I\to\operatorname{Expr}(I)$, the
compiled update for component $n$ is:

$$
\operatorname{compileUpdate}(\operatorname{body},n)(S)(r)
:=
\begin{cases}
\operatorname{eval}(S,\operatorname{body}(n)),& r=n,\\
S(r),& r\ne n.
\end{cases}
$$

Standard reading:

The compiled update recomputes the target component from its formula body and
leaves every other component unchanged.

c033 proves:

$$
\operatorname{targets}(\operatorname{compileSchedule}(\operatorname{body},\Gamma))
=
\Gamma.
$$

Standard reading:

Compiling a target order into updates preserves exactly that target order.

c034 assembles the compiled Boolean toy kernel. Its key recurrence theorem is:

$$
\operatorname{Finite}(I\to\{\bot,\top\})
\Longrightarrow
\exists i,j,\;
i < j\le|I\to\{\bot,\top\}|
\land
S_i=S_j,
\qquad
S_{n+1}:=
\operatorname{evalSchedule}(\operatorname{compileSchedule}(\operatorname{body},\Gamma),S_n).
$$

Standard reading:

For Boolean component states, formula bodies compile into a concrete schedule.
If the Boolean family-state space is finite, repeated execution of that compiled
schedule must revisit a semantic state within the finite pigeonhole bound.

c034 is the strongest finite Boolean toy kernel. It still does not solve full
TABA tables, because the full TABA formula and CBF languages, table-valued
expressions, semantic-dependence minimization, atomless infinite recurrence, and
Tau runtime lowering remain outside the theorem surface.

### 4.8 What finite tables can do

The finite form is useful because it is executable, inspectable, and small
enough to validate with independent models.

It can express:

```text
finite support union
finite support intersection
finite guard filtering
finite masked update
finite existential projection
finite projection-over-join laws
finite complement and disjointness inside ft4
```

It can be used as:

```text
a replayable Tau kernel
a regression harness for table formulas
a bounded witness carrier for examples
a finite lowering target for small row tables
a debugging model before moving to clopens, automata, or Borel-code carriers
```

The current finite form cannot express:

```text
arbitrary infinite key spaces as finite runtime data
atomless subdivision below singleton finite cells
countable recurrence suprema
stream-clopen quotient equality in general
general table recursion
full TABA NSO interaction
```

The finite form is therefore a correct small kernel, not the final table
semantics.

### 4.9 Why the infinite form remains hard

The infinite form is hard for structural reasons, not because the finite formulas
are unclear.

First, mathematical tables are functions:

$$
T:K\to\alpha.
$$

If `K` is infinite, this is not automatically finite runtime data. It is a
semantic object. To execute it, Tau needs a symbolic carrier, an equivalence
procedure, or a checked translation-validation boundary.

Second, atomlessness destroys finite atomic enumeration:

$$
\forall a,\;
a\ne\bot
\Longrightarrow
\exists s,\;
(a\wedge s\ne\bot)\land(a\wedge s'\ne\bot).
$$

There is no last indivisible cell. A finite mask works by enumerating atoms.
An atomless Boolean algebra works by guaranteeing that every live region can
split again. Those are opposite representation regimes.

Third, recurrence needs countable suprema:

$$
X_0=\bot,\qquad
X_{n+1}=F(X_n),\qquad
\mu F=\bigvee_{n < \omega}X_n.
$$

Finite clopen cells do not contain all such countable joins. The v402 witness is
the countable union:

$$
\bigcup_{n < \omega}[0^n1].
$$

Standard reading:

The set of streams that eventually contain a true bit is the union of all
finite cylinders saying "the first true bit appears here."

No finite clopen decision tree can represent that set, because any finite tree
looks only to a bounded depth, while "eventually true" has no fixed bound.

Fourth, positive completion and Boolean closure pull in different directions:

$$
\mathrm{PrefixOpen}\text{ supports countable positive unions.}
$$

$$
\mathrm{PrefixOpen}\text{ is not closed under complement.}
$$

$$
\mathrm{BoolRef}\text{ is closed under Boolean operations but is not a compact runtime carrier.}
$$

This is why the carrier stack split into:

$$
\mathrm{FinClopen}
\hookrightarrow
\mathrm{PrefixOpen}
\hookrightarrow
\mathrm{BoolRef}.
$$

Fifth, complement is not harmless in recursive definitions. Same-stratum
complement is anti-monotone:

$$
X\le Y\Longrightarrow Y'\le X'.
$$

Least-fixed-point semantics needs monotone, and usually omega-continuous,
operators. A recursive table language with unrestricted complement cannot be
accepted into the positive fixed-point kernel without stratification or another
proof of monotonicity.

Sixth, equality becomes the implementation problem. In the finite `ft4` carrier:

$$
A=B
$$

is four-bit equality. In completed semantic carriers, equality may mean equality
of sets of infinite streams, equality of Borel-code denotations, or equivalence
of automata languages. Those are different engineering problems.

The best current summary is:

- finite executable tables: implemented and replayed,
- algebraic atomless tables: mechanically checked,
- completed infinite recurrence tables: not solved,
- Tau lowering for richer table expressions: not solved.

The missing bridge is a carrier that is at once:

- expressive enough for recurrence and Boolean operations,
- compact enough to execute,
- equipped with decidable or checkable equivalence,
- connected by proof to the reference semantics,
- lowerable into Tau without changing meaning.

That is the reason the frontier did not end with `ft4`.

The root finite-lasso proof receipt is:

```text
experiments/math_object_innovation_v433/generated/MullerFiniteLassoCertificate.lean
```

The main theorem is:

```text
muller_finite_lasso_certificate_receipt
```

It says that finite prelude data, finite cycle data, wrap consistency, periodic
tail input, cycle coverage, recurring-state sightings, and acceptance compose
into a proof of nonempty accepted language.

That finite lasso surface then splits into four checked sub-lanes:

- v434 through v440 move from a bounded Python graph-search emitter to
  list-shaped dependent proof bridges, raw-list validator soundness, local
  validator checks, and a proved finite Boolean checker.
- v441 through v447 add optional-output wrappers for untrusted emitters,
  route a Lean finite graph-search emitter through those wrappers, repair the
  accepting-set order hazard, and check the emitted-certificate corpus natively
  in Lean.
- v448 through v450 prove checker exactness for the ordered and unordered local
  predicates, then lift that exactness to returned graph-search output.
- v451 through v455 move back to table semantics: pointwise revision,
  pair-indexed atomless existential bridges, fixed bit-indexed bridges,
  abstract split-index laws, and the fixed two-step iterated bridge over
  `Fin 8 -> Fin 4 -> Fin 2`.

The emitter is still not proved complete and is not lowered into Tau. The
remaining iterated-elimination problem is generic split-index composition,
not the fixed two-step witness chain.

The next proof artifacts move the projection frontier in stages:

- v456 is a proof-quality audit lane for v451. It exposes representation,
  abstraction, constraints, goals, obligations, solvers, and metadata before
  the prose claim is reused.
- v457 replaces the fixed two-step `Fin 8 -> Fin 4 -> Fin 2` result with an
  abstract two-step composition theorem for compatible split-index interfaces.
- v458 proves arbitrary finite-depth composition for homogeneous split-index
  chains.
- v459 specializes the one-step and two-step DNF bridges to the concrete
  product carrier `Base x Bool`.
- v460 checks a depth-three heterogeneous product-carrier chain and an all-free
  DNF instance, showing that the heterogeneous route is not blocked at depth
  three.
- v461 closes the finite heterogeneous split-index chain by making carrier
  agreement part of the chain type.
- v462 adds a table-expression compiler layer for `rows`, `join`, and
  existential atomless `project`, but not yet the v400 prefix-word clopen
  row-table layer.
- v463 accepts v400-style finite prefix-word rows only under an explicit
  embedding `path : PrefixWord -> Cell`. This narrows the bridge but does not
  prove stream-clopen equivalence.

The packed-representation lane is separate:

- v464 proves `Fin n x Bool ~= Fin (2*n)` as an equivalence-existence theorem.
- v465 gives the concrete arithmetic encoding: `low(i)=2*i`,
  `high(i)=2*i+1`, `parent(c)=c/2`, and `side(c)=c mod 2`.
- v466 plugs that concrete carrier into the split-index DNF bridge.
- v467 extends the bridge to finite `rows`, `join`, and `project`.

The remaining packed-lowering task is no longer one-step DNF projection or
finite expression compilation. It is stream-clopen row equivalence, recurrence,
and Tau runtime integration.

The pointwise and atomless side has a separate boundary:

- v468 closes extended pointwise revision only for the pointwise partial-update
  operator.
- v469 moves the atomless splitter law into mathlib's Boolean-algebra
  interface.
- v470 adds finite BL disjointness and membership characterization.

Recursive table revision, revision-safe partial recomputation, coverage-to-top,
and splitter independence remain separate obligations.

The current carrier stack should be read as:

```text
FinClopen -> PrefixOpen -> BoolRef
```

`FinClopen` is the finite approximant and executable normalizer layer.
`PrefixOpen` is the positive-recursion completion lane. `BoolRef` is the full
Boolean reference semantics, currently represented most faithfully by the
v406-style Borel-code lane, with v403 powersets kept as the simplest reference
model.

The executable Boolean guard target is a separate embedding problem:

```text
AutomataEff -> BoolRef
```

The evidence for that lane should be read in stages, not as one undifferentiated
claim.

First, v407 through v413 build the automata-shaped Boolean surface: concrete
deterministic witnesses, semantic closure scaffolding, co-Buchi finite
acceptance for the running witness, a two-state Muller product projection, the
arbitrary finite-list projection core, and a listed finite-state Muller carrier.

Second, v414 through v421 connect acceptance evidence to language reasoning. A
narrow self-loop nonempty certificate is checked. Semantic equivalence is
reduced to symmetric-difference emptiness. General eventual-set nonemptiness,
finite recurring-list specialization, non-equivalence certificates, product-state
union and intersection, constructed symmetric difference, and exact empty versus
nonempty outcome specifications are all checked at the finite certificate level.

Third, v422 through v447 turn the finite-lasso idea into an executable certificate
lane. The periodic-run bridge derives the infinitely-often evidence from
eventual periodicity. Finite cycle input and state bridges derive the needed
periodic stream facts. Bounded transition consistency proves run/table agreement
for each cycle index. Compact `Fin period` cycle data lowers into that bounded
theorem. The resulting finite-cycle nonempty certificate lane is integrated, and
the graph-search emitter can construct checked finite lasso certificates for
explicit finite Muller accepting sets.

Fourth, v448 through v456 remove representation hazards and connect pointwise
revision. Lean bridges explicit accepting-set membership, list-shaped emitted
lasso data, raw local checks, executable Boolean checks, optional emitter output,
unordered accepting-set checks, and unordered graph-search output into the same
soundness surface. The unordered check fixes a concrete emitter hazard: `[B,A]`
no longer fails only because the accepting family stores `[A,B]`. The pointwise
revision law is also checked: the formula preserves the new spec
unconditionally, preserves the old spec when a joint witness exists, falls back
to the new spec when no joint witness exists, and is idempotent when revising a
spec by itself.

The remaining boundary is still important. Complete finite graph emptiness,
minimization, recurrence compilation, and Tau lowering are not closed by this
automata lane. The same pointwise law also has a v456 sigma audit. The collapsed
Boolean abstraction is `p = phi(x,y)`, `q = psi(x,y)`,
`j = exists t, phi(x,t) and psi(x,t)`, and `r = q and (j -> p)`. The explicit
obligations are checked by brute force, Z3, cvc5, ESSO, and the v451 Lean proof.

## 5. The v393 semantic object

The semantic carrier is a binary decision tree:

$$
\operatorname{Clop}
::=
\bot
\mid
\top
\mid
\operatorname{node}(\operatorname{left},\operatorname{right}).
$$

It is evaluated over infinite Boolean streams. A node branches on the next bit:

$$
\operatorname{Eval}
\bigl(\operatorname{node}(\ell,r),s\bigr)
=
\begin{cases}
\operatorname{Eval}(r,\operatorname{tail}(s)),
& \operatorname{first}(s)=\mathrm{true},\\
\operatorname{Eval}(\ell,\operatorname{tail}(s)),
& \operatorname{first}(s)=\mathrm{false}.
\end{cases}
$$

The proved Boolean operations are:

$$
\begin{aligned}
\operatorname{compl} &: \operatorname{Clop}\to\operatorname{Clop},\\
\operatorname{union} &: \operatorname{Clop}\to\operatorname{Clop}\to\operatorname{Clop},\\
\operatorname{inter} &: \operatorname{Clop}\to\operatorname{Clop}\to\operatorname{Clop}.
\end{aligned}
$$

The key semantic facts are:

$$
\operatorname{Eval}(\operatorname{compl}(t),s)
\Longleftrightarrow
\neg\operatorname{Eval}(t,s).
$$

$$
\operatorname{Eval}(\operatorname{union}(a,b),s)
\Longleftrightarrow
\operatorname{Eval}(a,s)\lor\operatorname{Eval}(b,s).
$$

$$
\operatorname{Eval}(\operatorname{inter}(a,b),s)
\Longleftrightarrow
\operatorname{Eval}(a,s)\land\operatorname{Eval}(b,s).
$$

This is the precise reason v393 matters. It proves the Boolean meaning of the
finite clopen carrier, not merely a bounded Python behavior.

## 6. The quotient correction

The v394 proof exposed an important semantic trap.
Raw clopen decision trees are not canonical.
For example:

$$
\operatorname{node}(\bot,\bot)
$$

is semantically empty, but it is not syntactically the same tree as:

$$
\bot.
$$

The table-cell interface requires empty elements to equal zero.
So raw syntax is the wrong carrier.
The corrected carrier is:

$$
\operatorname{Cell}:=
\operatorname{FinClopen}/\!\equiv_{\mathrm{sem}}.
$$

That quotient is what makes the DNF projection theorem land cleanly.

## 7. The normalizer validation boundary

The executable normalizer from v392 works on finite lists of prefix words.
The quotient carrier from v394 is semantic.
The bridge is coverage preservation:

$$
\operatorname{CoverageEquivalent}(\operatorname{output},\operatorname{input})
\Longrightarrow
\operatorname{CellOfWords}(\operatorname{output})
=
\operatorname{CellOfWords}(\operatorname{input}).
$$

The v395 theorem says that if the output word list covers exactly the same
infinite streams as the input word list, then both lists denote the same quotient
cell.

That does not prove the concrete normalizer algorithm yet.
It gives the exact contract the normalizer or a validator must satisfy.

The v396 proof adds the first certificates for that contract:

```text
drop_covered_descendant_coverage
merge_sibling_cylinders_coverage
rewriteCert_cell_sound
```

The first theorem says a descendant prefix can be removed when its ancestor prefix
is already present. The second says two sibling cylinders can be replaced by
their parent prefix. The third says either certified rewrite preserves the
quotient cell.

The v397 proof then composes those local steps into arbitrary finite traces:

```text
rewriteTrace_cell_sound
```

That theorem is the proof-carrying-normalization boundary. If a normalizer emits
a valid trace, the trace itself proves semantic preservation in the quotient
carrier.

The v398 executable experiment emits those trace-shaped steps and checks them on
a generated bounded corpus through depth 4:

```text
30784 generated inputs
27660 changed inputs
63259 emitted rewrite steps
0 failures
```

This is evidence for the emitter, not a proof of the emitter.

The v399 checker separates the emitter from the validation boundary. It accepts
only logs whose steps match the constructor grammar proved in v397, and it checks
that the trace links from input to output.

The checked v399 run accepted all generated logs through depth 4 and rejected
representative malformed logs:

```text
30784 / 30784 generated logs accepted
63259 emitted rewrite steps
855 malformed trace mutations rejected
0 failures
```

The v400 proof then lifts that row-level validation boundary into a small typed
table-expression layer:

$$
\operatorname{Expr}
::=
\operatorname{rows}
\mid
\operatorname{join}
\mid
\operatorname{project}.
$$

Here a row is still a finite prefix-word description, and its value is still an
infinite clopen quotient cell. The typed table maps keys to those quotient
cells.

The main receipts are:

```text
row_trace_cell_table_sound
eval_rows_trace_sound
eval_project_rows_trace_sound
eval_join_rows_trace_sound
typed_table_trace_soundness_receipt
```

The bounded sanity package also checked 256 deterministic child-table projection
cases over generated prefix-word rows through depth 3:

```text
256 child-table projection cases
1724 row-normalizer steps
0 semantic failures
```

The v401 proof adds the first recurrence-shaped bridge. It extends the v400
expression layer with a recursive variable:

$$
\operatorname{Expr}_{\mathrm{rec}}
::=
\operatorname{var}
\mid
\operatorname{rows}
\mid
\operatorname{join}
\mid
\operatorname{project}.
$$

The receipt theorem is:

```text
recurrence_approximant_trace_soundness_receipt
```

It proves finite approximant equality under certified body rewrites. This is a
strictly smaller claim than full fixed-point equality.

The v402 proof then explains why full fixed-point equality cannot simply reuse
finite clopen cells as the completed carrier. A finite clopen decision tree only
looks at some bounded prefix depth. The set "a true bit appears somewhere" has
no such bound:

$$
1,\quad 01,\quad 001,\quad 0001,\quad \ldots
$$

The Lean theorem is:

```text
finite_clopen_omega_barrier_receipt
```

This proves a barrier, not a replacement semantics.
The next semantic design has to choose one of two routes:

- a completion carrier,
- a finite-stabilization theorem.

The v403 proof records the first route at its most general level:

$$
\operatorname{CompletedCell}:=\operatorname{Stream}\to\operatorname{Prop}.
$$

The countable supremum is pointwise:

$$
\operatorname{countableSup}(\operatorname{chain})(s)
:=
\exists n,\;\operatorname{chain}(n)(s).
$$

The v402 witness is representable there:

$$
\operatorname{countableSup}(\operatorname{bitTrueCell})
=
\operatorname{EventuallyOne}.
$$

This solves semantic closure only at the reference-semantics level.
It does not solve executable compactness.

The v404 proof tests a smaller carrier:

$$
\operatorname{PrefixLanguage}:=\operatorname{Word}\to\operatorname{Prop}.
$$

$$
\operatorname{PrefixOpenEval}(L)(s)
:=
\exists w,\;L(w)\land\operatorname{PrefixEval}(w,s).
$$

This carrier embeds finite word-list cells, supports countable prefix-language
suprema, and represents the v402 witness by the language of finite words ending
in `true`:

$$
\operatorname{PrefixOpenEval}(\operatorname{EndsTrue})
=
\operatorname{EventuallyOne}.
$$

The v405 proof then proves the boundary:

$$
\neg\exists L,\;
\operatorname{PrefixOpenEval}(L)
=
\operatorname{AllFalseOnly}.
$$

So prefix-open cells are a positive-recursion completion lane, not a full Boolean
TABA table carrier.

The v406 proof restores Boolean expressiveness at the symbolic-code level:

$$
\operatorname{BorelCode}
::=
\bot
\mid
\top
\mid
\operatorname{cyl}(w)
\mid
\operatorname{complement}(c)
\mid
\operatorname{finiteUnion}(c_1,\ldots,c_m)
\mid
\operatorname{countableUnion}(f)
\mid
\operatorname{bitPrefix}(b,c).
$$

The checked receipts include:

```text
codeOfWords_receipt
eventuallyOneCode_receipt
allFalseCode_receipt
```

This is a Boolean-completion reference lane, not a compact executable carrier.
The countable-union constructor has type:

$$
\mathbb{N}\to\operatorname{BorelCode}.
$$

That keeps the semantics clean but leaves equivalence, minimization, and Tau
runtime lowering unsolved.

The v407 proof then shows that the key witness pair is not only symbolic. It has
a concrete finite-state recognizer:

$$
\operatorname{state}:=\operatorname{seenTrue}.
$$

$$
\operatorname{step}(\operatorname{seenTrue},b)
:=
\operatorname{seenTrue}\lor b.
$$

The receipts are:

```text
eventuallyOneAutomaton_receipt
allFalseAutomaton_receipt
```

This is the first automata-shaped effective carrier evidence. It is not yet a
full omega-regular theory because acceptance is still written semantically and
there is no equivalence or minimization procedure.

The v408 proof makes the automata move generic. Given deterministic automata
$A$ and $B$, the product state is:

$$
(q_A,q_B).
$$

and the product step runs both machines on the same bit. The Lean receipts prove:

$$
\operatorname{Accepts}(\operatorname{Complement}(A))
=
\neg\operatorname{Accepts}(A).
$$

$$
\operatorname{Accepts}(\operatorname{Union}(A,B))
=
\operatorname{Accepts}(A)\lor\operatorname{Accepts}(B).
$$

$$
\operatorname{Accepts}(\operatorname{Intersect}(A,B))
=
\operatorname{Accepts}(A)\land\operatorname{Accepts}(B).
$$

This is still not the final effective carrier because the acceptance predicate
is arbitrary over infinite runs. The next step is finite acceptance data.

The v409 proof takes that next step for the running witness. Its acceptance
shape is:

$$
\operatorname{Accepts}(A)(s)
:=
\exists N,\;\forall n\ge N,\;
\operatorname{good}(\operatorname{Run}(A,s,n)).
$$

For the two-state witness, `good` is the finite state predicate `seenTrue =
true`. Lean proves:

$$
\operatorname{Accepts}(\operatorname{EventuallySeenTrue})
=
\operatorname{EventuallyOne}.
$$

$$
\operatorname{Accepts}(\operatorname{EventuallyAlwaysFalse})
=
\operatorname{AllFalseOnly}.
$$

This is still a concrete witness, not a general deterministic parity or Muller
theory. But the blocker has moved from "finite acceptance data is missing" to
"generic finite acceptance data, equivalence, minimization, and recurrence
compilation are missing."

The v410 proof sharpens that point. For co-Buchi acceptance, deterministic
intersection works:

$$
\operatorname{Accepts}(\operatorname{Intersect}(A,B))
=
\operatorname{Accepts}(A)\land\operatorname{Accepts}(B).
$$

The tempting union-good product has only one checked direction:

$$
\operatorname{Accepts}(A)\lor\operatorname{Accepts}(B)
\Longrightarrow
\operatorname{Accepts}(\operatorname{NaiveUnion}(A,B)).
$$

The converse is false. Lean checks a two-state toggling witness where the
product is always in at least one good component, but neither component is
eventually always good. This does not prove that deterministic co-Buchi has no
other union construction. It does show that the obvious product construction is
not the general table carrier. The next target should be parity or Muller
acceptance, or a different finite-stabilization route.

The v411 proof tests the Muller route in the smallest nontrivial state space.
It defines:

$$
\operatorname{InfSet}(A,s)(q)
:=
\forall N,\;\exists n\ge N,\;
\operatorname{Run}(A,s,n)=q.
$$

For a two-state product, Lean proves:

$$
\operatorname{ProjectFst}(\operatorname{InfSet}(A\times B,s))
=
\operatorname{InfSet}(A,s).
$$

$$
\operatorname{ProjectSnd}(\operatorname{InfSet}(A\times B,s))
=
\operatorname{InfSet}(B,s).
$$

The hard step is the finite split:

$$
\operatorname{InfOften}(P)
\Longrightarrow
\operatorname{InfOften}(P\land\neg b)
\lor
\operatorname{InfOften}(P\land b).
$$

That is the two-state version of the finite-pigeonhole argument needed for a
general Muller carrier. With those projections, v411 proves:

$$
\operatorname{PairUnionAccepts}(A,B)
=
\operatorname{Accepts}(A)\lor\operatorname{Accepts}(B).
$$

$$
\operatorname{PairIntersectAccepts}(A,B)
=
\operatorname{Accepts}(A)\land\operatorname{Accepts}(B).
$$

This is still not arbitrary finite-state Muller automata, but it is a checked
path through the exact obstruction exposed by v410.

The v412 proof then separates the finite-pigeonhole argument from the automaton
syntax. For arbitrary run functions `runA` and `runB`, if the `runB` states all
belong to a finite list, Lean proves:

$$
\exists r,\;
\operatorname{InfOften}(\operatorname{runA}=q\land\operatorname{runB}=r)
\Longleftrightarrow
\operatorname{InfOften}(\operatorname{runA}=q).
$$

and symmetrically for the second projection. This is the core lemma needed to
lift v411 from two states to listed finite-state Muller automata. It is not yet
the full carrier, but it removes the main finite projection blocker.

The v413 proof packages that projection core into the first listed finite-state
Muller carrier. A carrier contains:

$$
\begin{aligned}
\operatorname{states} &: \operatorname{List}(\operatorname{State}),\\
\operatorname{init} &: \operatorname{State},\\
\operatorname{step} &: \operatorname{State}\to\mathbb{B}\to\operatorname{State},\\
\operatorname{accept} &: (\operatorname{State}\to\operatorname{Prop})\to\operatorname{Prop}.
\end{aligned}
$$

with proofs that the initial state and every transition remain inside the listed
finite state set. Lean proves:

$$
\operatorname{Accepts}(\operatorname{Complement}(A))
=
\neg\operatorname{Accepts}(A).
$$

$$
\operatorname{ProductUnionAccepts}(A,B)
=
\operatorname{Accepts}(A)\lor\operatorname{Accepts}(B).
$$

$$
\operatorname{ProductIntersectAccepts}(A,B)
=
\operatorname{Accepts}(A)\land\operatorname{Accepts}(B).
$$

This is a real carrier milestone. It is still not the final Tau implementation
because product union and intersection are stated through product
infinite-state-set projections, not through a minimized executable product
machine. Emptiness, equivalence, recurrence compilation, and the embedding into
the v403 reference semantics remain open.

The v414 proof adds the first narrow nonempty-language certificate:

$$
\operatorname{reachable}(q)
\land
\operatorname{step}(q,b)=q
\land
\operatorname{accept}(\{q\})
\Longrightarrow
\exists s,\;\operatorname{Accepts}(A,s).
$$

The proof constructs a stream that follows the reaching prefix and then stays on
the one-bit self-loop forever. Its infinite-state set is exactly the singleton
`{q}`.

This is not a complete emptiness algorithm. It is a checked sufficient witness
format. The next step is a general lasso certificate where the loop can visit a
finite set of recurring states, not only one self-loop state.

The v415 proof adds the equivalence reduction:

$$
\neg\exists s,\;\operatorname{SymDiffAccepts}(A,B,s)
\Longleftrightarrow
\operatorname{Accepts}(A)=\operatorname{Accepts}(B).
$$

and the contrapositive witness form:

$$
\operatorname{Accepts}(A)\ne\operatorname{Accepts}(B)
\Longleftrightarrow
\exists s,\;\operatorname{SymDiffAccepts}(A,B,s).
$$

This is still semantic. It does not build the symmetric-difference product
automaton or decide emptiness. It says exactly what such an executable procedure
must certify.

The v416 proof then generalizes the self-loop witness into an eventual-set
certificate. If a run eventually stays inside a set `S`, every state in `S`
appears infinitely often, and `S` is accepted, then:

$$
\exists s,\;\operatorname{Accepts}(A,s).
$$

The key theorem is:

$$
\operatorname{InfSet}(A,s)=S
$$

under those two eventual exactness assumptions. This is still not a finite graph
emptiness checker because the stream and exactness proof are supplied. It is the
semantic target for such a checker.

The v417 proof makes the evidence more finite by replacing the arbitrary
predicate `S` with a finite list `qs`:

$$
\left(
\exists N,\;\forall n\ge N,\;\operatorname{Run}(A,s,n)\in qs
\right)
\land
\left(
\forall q\in qs,\;\operatorname{InfOften}(\operatorname{Run}(A,s,n)=q)
\right)
\land
\operatorname{accept}(qs)
\Longrightarrow
\exists s,\;\operatorname{Accepts}(A,s).
$$

This is still not the graph algorithm. It is the list-shaped certificate that a
future finite path-plus-cycle checker should reduce to.

The v418 proof composes v415 and v417:

$$
\operatorname{Accepts}(C)=\operatorname{SymDiffAccepts}(A,B)
\land
\operatorname{FiniteListNonemptyEvidence}(C)
\Longrightarrow
\operatorname{Accepts}(A)\ne\operatorname{Accepts}(B).
$$

This is a checker contract. A future executable pass must still construct the
symmetric-difference carrier `C` and produce the finite-list nonempty evidence.
But the final implication to non-equivalence is now checked.

The v419 proof constructs the product-state carrier:

$$
\operatorname{ProductCarrier}(A,B,\operatorname{acceptP}).
$$

and proves:

$$
\operatorname{Accepts}(\operatorname{UnionCarrier}(A,B),s)
\Longleftrightarrow
\operatorname{Accepts}(A,s)\lor\operatorname{Accepts}(B,s).
$$

and:

$$
\operatorname{Accepts}(\operatorname{IntersectCarrier}(A,B),s)
\Longleftrightarrow
\operatorname{Accepts}(A,s)\land\operatorname{Accepts}(B,s).
$$

This closes the gap between a semantic product predicate and an executable
listed product carrier. It is not minimization and it is not an emptiness
algorithm.

The v420 proof constructs the symmetric-difference carrier:

$$
\operatorname{SymDiffCarrier}(A,B).
$$

and proves:

$$
\operatorname{Accepts}(\operatorname{SymDiffCarrier}(A,B))
=
\operatorname{SymDiffAccepts}(A,B).
$$

This removes the need to supply a separate carrier that realizes symmetric
difference.

The v421 proof composes v420 with the finite-list certificate:

$$
\operatorname{FiniteListNonemptyCertificate}
\bigl(\operatorname{SymDiffCarrier}(A,B)\bigr)
\Longrightarrow
\operatorname{Accepts}(A)\ne\operatorname{Accepts}(B).
$$

The non-equivalence witness lane is now checked end to end, conditional on a
finite-list nonempty certificate for the constructed symmetric-difference
carrier. The missing piece is discovering or checking that finite certificate by
finite graph search.

The v422 proof states the full semantic decision contract:

$$
\neg\exists s,\;
\operatorname{Accepts}(\operatorname{SymDiffCarrier}(A,B),s)
\Longleftrightarrow
\operatorname{Accepts}(A)=\operatorname{Accepts}(B).
$$

and:

$$
\exists s,\;
\operatorname{Accepts}(\operatorname{SymDiffCarrier}(A,B),s)
\Longleftrightarrow
\operatorname{Accepts}(A)\ne\operatorname{Accepts}(B).
$$

This is not the graph-search algorithm. It is the exact target that such an
algorithm must certify.

The v423 proof moves one step toward lasso checking. It proves:

$$
\begin{aligned}
&\operatorname{EventuallyPeriodicAfterCutoff}(A,s,N,p)\\
&\land\;\forall q\in Q,\;\operatorname{SeenAfterCutoff}(A,s,q,N)\\
&\land\;\exists M,\;\forall n\ge M,\;\operatorname{Run}(A,s,n)\in Q\\
&\land\;\operatorname{accept}(Q)\\
&\Longrightarrow\exists s,\;\operatorname{Accepts}(A,s).
\end{aligned}
$$

The important part is that the "seen after cutoff" facts plus eventual
periodicity generate the infinitely-often evidence required by v417. This still
does not construct the stream from a finite bit cycle, so it is not full finite
graph search.

The v424 proof supplies one source of that periodic run:

$$
\operatorname{Run}(A,s,N+p)=\operatorname{Run}(A,s,N)
\land
\forall m,\;s(N+p+m)=s(N+m)
$$

$$
\Longrightarrow
\forall n\ge N,\;
\operatorname{Run}(A,s,n+p)=\operatorname{Run}(A,s,n).
$$

In words, if the input stream repeats after `N` with period `p`, and the
automaton returns to the same state after one period, then the run repeats after
`N` with that same period. This still does not construct the stream from a
finite bit cycle. It only proves the state-periodicity bridge once the stream
and anchor are supplied.

The v425 proof constructs that repeating input tail:

$$
\operatorname{TailCycleStream}(N,p,\operatorname{cycle}).
$$

where:

$$
\operatorname{cycle}:\operatorname{Fin}(p)\to\mathbb{B}.
$$

and proves:

$$
\operatorname{TailCycleStream}(N,p,\operatorname{cycle})(N+p+m)
=
\operatorname{TailCycleStream}(N,p,\operatorname{cycle})(N+m).
$$

This is the first finite tail-cycle object in the lasso lane. It still leaves
the prelude as a function and still supplies the state anchor and sightings.

The v426 proof replaces those sightings with finite cycle-state table
membership:

$$
\operatorname{cycle\_state}:\operatorname{Fin}(p)\to\operatorname{State}.
$$

If every recurring state appears in `cycle_state`, and the table entries match
the run at the corresponding cycle offsets, then every recurring state has a
post-cutoff sighting. This still does not prove the table entries are generated
by the transition function. That is the next graph-consistency step.

The v427 proof handles the wrap edge:

$$
\operatorname{Run}(A,s,N)=q_0
\land
\operatorname{Run}(A,s,N+p-1)=q_{\mathrm{last}}
\land
\operatorname{step}(q_{\mathrm{last}},s(N+p-1))=q_0
$$

$$
\Longrightarrow
\operatorname{Run}(A,s,N+p)=\operatorname{Run}(A,s,N).
$$

This is the state-anchor equality needed by v424 and v426. It is still only the
last transition of the cycle, not the whole transition-consistency table.

The v428 proof handles the ordinary cycle edges:

$$
\operatorname{Run}(A,s,N)=\operatorname{cycle\_state}(0)
\land
\forall j < L,\;s(N+j)=\operatorname{cycle\_bit}(j)
$$

$$
\land
\forall j+1\le L,\;
\operatorname{cycle\_state}(j+1)
=
\operatorname{step}(\operatorname{cycle\_state}(j),\operatorname{cycle\_bit}(j))
$$

$$
\Longrightarrow
\forall j\le L,\;
\operatorname{Run}(A,s,N+j)=\operatorname{cycle\_state}(j).
$$

This is the finite transition-consistency argument in bounded-index form. The
remaining conversion is from a compact `Fin period` path-plus-cycle witness into
this bounded table.

The v429 proof performs that compact conversion for ordinary edges:

$$
\operatorname{cycle\_state}:\operatorname{Fin}(p)\to\operatorname{State},
\qquad
\operatorname{cycle\_bit}:\operatorname{Fin}(p)\to\mathbb{B}.
$$

with:

$$
\forall j:\operatorname{Fin}(p),\;
\operatorname{cycle\_state}(j+1)
=
\operatorname{step}(\operatorname{cycle\_state}(j),\operatorname{cycle\_bit}(j)).
$$

where the successor premise is restricted to ordinary, non-wrap indices. The
result is:

$$
\forall j:\operatorname{Fin}(p),\;
\operatorname{Run}(A,s,N+j)=\operatorname{cycle\_state}(j).
$$

The final wrap edge remains separate and is handled by v427.

The v430-v431 integrated lane composes the pieces:

$$
\begin{aligned}
&\operatorname{OrdinaryEdgeAgreement}
\land \operatorname{FinalWrapAnchor}
\land \operatorname{CycleStateSightings}\\
&\land \operatorname{TailCycleStreamBitMatches}
\land \operatorname{PreludeReachesCycleStart}\\
&\land \operatorname{PeriodicCoverageImpliesEventualMembership}
\land \operatorname{accept}(\operatorname{recurring})\\
&\Longrightarrow
\exists s,\;\operatorname{Accepts}(A,s).
\end{aligned}
$$

This is now a finite lasso certificate lane with an executable Lean emitter
handoff. It is still not full graph-search completeness.

The bounded search side is:

- v434 implements the search procedure in Python for a bounded finite
  acceptance domain.
- v443 ports a bounded Lean emitter whose returned witnesses are filtered
  through the proved checker and wrapper.
- v447 gives Lean-native coverage for the 30 certificates emitted by the v434
  corpus.

The checker-correctness side is:

- v435 proves that explicit finite accepting-set membership supplies the
  acceptance proof required by the finite-lasso certificate.
- v436 bridges length-checked list witnesses into the dependent certificate
  tables.
- v437 proves validator soundness for raw list witnesses.
- v444 removes a checker-order hazard by accepting recurring lists
  extensionally, when they have the same finite members as one of the accepting
  lists.
- v445 packages that unordered checker as an optional-output wrapper.
- v446 composes the graph-search emitter with that wrapper.
- v448 proves the ordered checker exact for supplied local witnesses.
- v449 proves the unordered checker exact for supplied extensional local
  witnesses.
- v450 composes that exactness theorem with the unordered graph-search wrapper.

For `TailCycleStream`, the bit matches are derived by v431. The cycle-start
match is derived from finite prelude path data by v432. Eventual membership in
the recurring list is derived by v433.

## 8. What remains unsolved

Full TABA tables are not solved yet.
The remaining semantic work is specific:

- specialize deterministic stream automata to finite parity or Muller acceptance data, or prove finite stabilization for the supported recurrence fragment,
- prove complete emptiness or nonemptiness decision procedures for the finite emitter lane, not only sound returned-witness certificates,
- turn c021 finite-prefix adequacy into an explicit clopen-to-DFA or clopen-to-Muller compiler theorem,
- either instantiate c022's least-fixed-point completion theorem with a concrete carrier, such as a regular-open or quotient-completion carrier, or extend c034 from the compiled Boolean toy kernel to the real TABA formula/CBF language, table-valued expressions, and executable ready-node search,
- add composition and pullback to the quotient-valued recursive expression grammar,
- extend the schedule model to heterogeneous typed table entries,
- prove revision-safe partial recomputation,
- connect the supported fragment to real Tau syntax and runtime behavior.

The current blocker has moved again.

What is no longer the blocker:

- finite-union clopen carrier semantics,
- semantic quotient projection,
- executable word-list validation,
- primitive rewrite certificates,
- sound finite normalizer traces,
- external trace-log checking,
- the first typed row/projection bridge,
- finite recurrence approximant preservation,
- powerset reference completion,
- prefix-open positive-recursion semantics,
- prefix-open complement failure,
- concrete deterministic automata witnesses,
- semantic automata closure,
- finite acceptance data for the running witness,
- two-state Muller product projection,
- finite-list Muller projection,
- symmetric-difference equivalence reduction,
- finite recurring-list nonempty certificates,
- product-state Boolean carriers,
- constructed symmetric-difference decision specification,
- periodic-run and input-periodicity bridges,
- finite cycle-state membership,
- wrap-anchor equality,
- bounded transition-consistency agreement,
- compact finite-cycle lowering,
- the integrated finite-cycle nonempty certificate lane.

What remains open:

- complete executable emptiness,
- minimization,
- complete recurrence compilation,
- embedding the executable carrier into the reference semantics,
- or, alternatively, a stabilization criterion strong enough for the intended
  recurrence fragment.

c024 through c028 add the finite recurrence and schedule-certificate side:
finite semantic recurrence, mutual recurrence, finite-family recurrence,
supplied semantic schedules, and supplied dependency-order certificates are
checked. Dependency extraction, checked topological-sort construction,
formula-to-update compilation, and Tau runtime lowering remain open.

## 9. Research status

The honest status is:

```text
Tau qelim:
    significant guarded optimization candidate found for a supported fragment

TABA tables:
    finite executable and algebraic atomless semantic fragments are checked
    typed row/projection preservation is checked for the first quotient-cell layer
    finite recurrence approximants are checked under certified body rewrites
    finite clopen cells are proved insufficient for arbitrary countable suprema
    the full powerset carrier is checked as a reference completion semantics
    prefix-open cells are checked as a positive-recursion completion lane
    prefix-open cells are checked not to be a full Boolean carrier
    symbolic Borel-code completion is checked but not executable enough
    a concrete two-state stream automaton represents the main witness and complement
    deterministic stream automata have checked semantic closure operations
    the running witness has checked two-state co-Buchi acceptance data
    co-Buchi intersection is checked and naive union-good is refuted
    two-state Muller product projection gives checked union/intersection receipts
    finite-list infinitely-often projection core is checked
    listed finite-state Muller carriers have checked Boolean receipts
    self-loop Muller nonempty certificates are checked
    Muller equivalence reduces to symmetric-difference emptiness
    eventual exact recurring-state sets give checked nonempty certificates
    finite recurring-state lists give checked nonempty certificates
    symmetric-difference nonempty certificates prove non-equivalence
    product-state union and intersection carriers are executable and checked
    the symmetric-difference carrier is executable and checked
    constructed symmetric-difference finite-list certificates prove non-equivalence
    the constructed symmetric-difference decision spec is checked
    periodic-run evidence generates finite recurring-list evidence
    input periodicity plus state anchor generates periodic-run evidence
    finite tail-cycle data generates input periodicity
    finite cycle-state table membership generates sighting evidence
    the final cycle wrap transition generates the state-anchor equality
    bounded transition consistency generates run/table agreement
    compact Fin-cycle data lowers into bounded transition consistency
    integrated finite-cycle certificates prove nonempty accepted language
    ordered and unordered supplied-witness checkers are exact for their local predicates
    unordered graph-search output has an exact returned-output contract
    pointwise revision has a sigma audit with SMT and ESSO cross-checks
    two-step split-index projection composition is checked abstractly
    finite-depth homogeneous split-index projection composition is checked
    product-carrier split-index projection is checked for Base x Bool
    three-step product-carrier projection composition is checked
    finite dependent heterogeneous split-index chain composition is checked
    DNF table-expression compiler adequacy is checked for rows, join, and project
    finite prefix-word rows compile into DNF rows under explicit path coverage
    mathlib proves Fin n x Bool and Fin (2*n) have an equivalence
    concrete packed-Fin encode/decode arithmetic is checked
    packed-Fin one-step DNF projection is checked
    packed-Fin rows/join/project expression compilation is checked
    extended pointwise revision for partial updates is checked
    atomless splitters are equivalent to atomlessness in mathlib Boolean algebras
    BL disjointness and membership characterization are checked
    semantic Clopen splitters and arbitrary-key Clopen table splitting are checked
    c020 assembles the algebraic K -> Clopen table theorem with set/common laws
    c021 proves Cantor clopen finite-prefix adequacy by structural depth
    c022 proves an abstract complete-atomless least-fixed-point lane for table suprema and omega fixed points
    c023 proves full stream powerset is atomic and fails the splitter property
    c024 proves the finite semantic loop core for TABA-style recurrence and fallback
    c025 lifts the finite semantic loop core to two-component mutual recurrence by product-state semantics
    c026 lifts the finite semantic loop core to arbitrary finite-family recurrence by dependent-product semantics
    c027 proves finite semantic schedule evaluation and scheduled recurrence loop receipts
    c028 proves dependency-order certificate soundness for supplied finite schedules
    c029 proves prefix topological construction certificates imply valid dependency orders
    c030 proves exact dependency extraction for a small formula fragment
    c031 proves formula-derived dependencies feed prefix topological schedule certificates
    c032 assembles the finite toy formula-schedule recurrence kernel
    c033 proves Boolean formula bodies compile to target-preserving updates
    c034 proves the compiled Boolean toy recurrence kernel
    v497 proves explicit dyadic splitter leaves have count 2^n and join back to the original element
    v498 proves pointwise omega-complete table semantics and Kleene fixed points for abstract completed carriers
    v499 proves non-bottom table splitter inheritance over the abstract omega-split carrier
    v500 proves binary prefix-cylinder splitting for the concrete positive carrier basis
    v501 proves nonempty prefix-open regions contain two disjoint nonempty prefix-open subregions
    v502 proves countable-union closure and generator-union omega suprema for prefix-open regions
    v503 proves finite mask plus finite same-polarity hit QE without atomlessness
    v504 proves one-positive-one-complement mixed QE under a splitter interface
    v505 proves the positive-hit extension step preserving one complement residual
    v506 proves finite positive-hit lists with one complement-hit target
    c035 proves the compiled recurrence kernel for arbitrary finite Boolean-algebra-valued family states
    c036 proves the semantic four-cell Boolean carrier behind Tau ft4
    v472 proves positive BA-valued formula omega-continuity and a fixed-point theorem over complete Boolean algebras
    v473 proves positive guarded-row omega-continuity and a fixed-point theorem over complete Boolean algebras
    v474 proves stratified-prime omega-continuity for lower-stratum prime terms
    v475 proves stratified guarded-row omega-continuity for finite row lists with lower-stratum prime
    v476 proves fixed-guard priority rows normalize to disjoint guarded joins
    v477 proves fixed-guard priority omega-continuity and a fixed-point theorem
    v479 proves lower-stratum priority guards preserve omega-continuity
    v480 proves lower-stratum priority rows normalize pointwise to disjoint guarded joins
    v481 proves a restricted table syntax compiler into the safe lower-guard kernel
    v552 proves safe table-expression syntax with lower guards, positive current references, lower-prime, lower-guarded CBFs, and explicit defaults is monotone and omega-continuous
    v553 proves fixed-guard select and revision are safe, while current guards, arbitrary value-predicate select, and equality-style common have checked nonmonotonicity counterexamples
    v554 adds fixed-guard select and revision as first-class table syntax while preserving monotonicity, omega-continuity, and the fixed-point receipt
    v555 proves safe table expressions lower into an abstract Tau-helper target language with denotation preservation and inherited fixed-point receipt
    v556 proves binary Boolean-polynomial terms compile to four-coefficient minterm form with denotation preservation
    v557 proves finite-arity Boolean-polynomial terms compile to 2^n-leaf minterm trees with denotation preservation
    v558 proves finite Boolean-valued CBF and priority-table syntax collapses to a BF kernel, and proves same-stratum prime is outside the monotone Kleene lane
    v559 proves finite Boolean-valued CBF priority tables compile to explicit 2^n-leaf minterm trees with denotation preservation
    Tau now has a feature-flagged safe-table helper prelude, checked on the finite ft4 carrier and the symbolic tau carrier with TAU_ENABLE_SAFE_TABLES=1
    full official TABA still needs lane assignment for monotone recurrence, certified nonmonotone recurrence, NSO, Guarded Successor, and Tau lowering
```

The next high-value proof target is:

```text
TABA full formula/CBF dependency extraction, executable ready-node topological sorting, arbitrary-arity minterm/Skolem compilation, official NSO and Guarded Successor integration, concrete complete atomless carrier, and explicit clopen-to-automata compiler
```

## 10. Safe table Tau runtime experiment

In `TauLang-Experiments`, the newest Tau-side artifact is deliberately smaller
than full TABA:

```text
examples/tau/safe_table_kernel_builtins_v1.tau
```

It is enabled by:

```bash
TAU_ENABLE_SAFE_TABLES=1
```

The helper prelude adds:

```text
st_select4(x,g)
st_choice4(g,then_value,else_value)
st_revise4(old,g,replacement)
st_update4(old,base,g,replacement)
```

The formulas are the v554 safe forms:

$$
\operatorname{select}_G(x)=G\wedge x.
$$

$$
\operatorname{revise}_{G,a}(x)=(G\wedge a)\vee(G'\wedge x).
$$

$$
U(x)=\operatorname{base}\vee\operatorname{revise}_{G,a}(x).
$$

The replay script, run from the `TauLang-Experiments` repo root, is:

```bash
python3 scripts/generate_safe_table_tau_artifacts.py
```

The generated proof report is:

```text
assets/data/safe_table_tau_traces.json
```

The finite replay checks four cases against an independent host model, with no
mismatches. The symbolic replay checks the `tau` helper equations by asking Tau
to find counterexamples to the defining equalities and the idempotent update
law. Each negated equality returns `no solution`.

The Lean lowering receipt is v555. Its central theorem shape is:

$$
\operatorname{evalTauTable}(\operatorname{compileTable}(T))
=
\operatorname{denoteTable}(T).
$$

Standard reading: evaluating the compiled helper-target table gives the same
Boolean-algebra value as evaluating the source safe table expression.

This is the first checked bridge from source safe-table syntax to a
Tau-helper-shaped target. It is still not a parser or runtime-correctness proof
for Tau itself.

In `TauLang-Experiments`, the source-table compiler demo is:

```text
examples/tau/safe_table_source_examples.json
```

The replay, run from the `TauLang-Experiments` repo root, is:

```bash
python3 scripts/generate_safe_table_compiler_artifacts.py
```

The generated proof report is:

```text
assets/data/safe_table_compiler_tau_traces.json
```

For each source table, the script emits a raw Boolean-algebra expression and a
Tau-helper expression, then asks Tau for a counterexample to their equality.
The checked examples return `no solution`. This is executable evidence for the
same lowering shape that v555 proves abstractly.

In `TauLang-Experiments`, the Tau-native full-style safe table demo source is:

```text
examples/tau/full_style_taba_demo_v1.tau
```

The replay, run from the `TauLang-Experiments` repo root, is:

```bash
python3 scripts/generate_full_style_taba_demo_artifacts.py
```

The generated proof report is:

```text
assets/data/full_style_taba_demo_traces.json
```

This source is closer to the intended table surface than the earlier safe
examples because it is parsed by Tau itself. It has a feature-gated table form,
priority rows by row order, CBF-style conditionals by nested guarded table
choice, safe fixed-guard selection, and safe fixed-guard revision.

The parser-level surface is:

```tau
table {
  when G1 => V1;
  when G2 => V2;
  else => D
}
```

The parser guard is `safe_tables`, enabled by `TAU_ENABLE_SAFE_TABLES=1`.
Without the feature flag, the same source is rejected.
The receipt runs with `--charvar false`, so multi-character names such as
`riskgate` are parsed as single Tau variables.

The lowering check has the same semantic shape:

$$
\operatorname{RawDenote}(T)
=
\operatorname{TauParserDenote}(T).
$$

Standard reading:

For the full-style demo table $T$, the explicit raw Boolean-algebra denotation
is equal to the denotation Tau obtains by parsing and lowering $T$.

Boundary:

This is not full unrestricted TABA. The demo keeps row guards lower-stratum,
keeps select and revision fixed-guard, and does not add unrestricted recurrence.
It is a parser-and-lowering demo lane, not a proof of official NSO, Guarded
Successor, or production lowering for all TABA syntax.

In `TauLang-Experiments`, the app-style demo is:

```text
examples/tau/collateral_quarantine_closure_v1.tau
```

It models a four-asset dependency line:

```text
asset 0 -> asset 1 -> asset 2 -> asset 3
```

The recursive closure law is:

$$
Q_{n+1}=D(Q_n\vee \mathrm{Seed}_{n+1}).
$$

Here $D$ is the one-hop dependency operator. The host closes the recursive
loop by feeding $Q_n$ into the next step. Tau checks the claimed transition
and the claimed stability condition for each step. The replay, run from the
`TauLang-Experiments` repo root, is:

```bash
python3 scripts/generate_quarantine_closure_tau_artifacts.py
```

The generated proof report is:

```text
assets/data/quarantine_closure_tau_traces.json
```

This is a useful demo, not a full proof of TABA tables. It shows that the
recursive-table pattern can drive an application-level closure loop and that
each proposed transition can be checked by Tau. It does not show first-class
official table syntax, a table compiler, or semantic adequacy of such a
compiler.

For public reproduction, the patch and replay path lives in
`TauLang-Experiments`:

```bash
./scripts/run_public_demos.sh --accept-tau-license
```

The focused table-only replay remains:

```bash
./scripts/run_table_demos.sh --accept-tau-license
```

The scope remains experimental. The semantic reason this is more than the old
finite table replay is that v554 proves the same update shape over complete
Boolean algebras, and the new prelude also exposes the shape over Tau's symbolic
`tau` carrier. This is still not a claim of full unrestricted TABA.

The remaining target is smaller and sharper than "solve tables."
The proof artifacts split into separate lanes:

- v402 shows why finite clopens are insufficient for arbitrary countable
  recurrence limits.
- v403 gives the reference semantics.
- v405 prevents overclaiming the prefix-open lane.
- v406 restores Boolean expressiveness, but exposes the implementation problem:
  effective equivalence and minimization.
- c022 through c032 split the semantic recurrence problem into two honest
  lanes: complete atomless least-fixed-point semantics, or TABA-style finite
  quotient loop semantics.

Neither lane is solved by a finite clopen carrier or an atomic powerset
reference model. That is the core lesson. The implementation carrier and the
truth semantics cannot be silently identified.

The automata lane then turns equivalence into a finite certificate problem:

- v407 through v413 move from concrete deterministic witnesses to a listed
  finite-state Muller surface.
- v414 and v415 fix the first nonempty-witness format and the equivalence
  target, namely symmetric-difference emptiness.
- v416 through v422 define finite recurring-list evidence, construct the
  symmetric-difference carrier, and prove the exact equivalence versus
  non-equivalence specification.
- v423 through v433 remove supplied semantic assumptions one by one, replacing
  them with periodic input, finite cycle data, bounded transition consistency,
  wrap-anchor equality, and cycle coverage.
- v434 through v450 build the executable finite-lasso lane: emitter, validator,
  optional-output wrapper, unordered accepting-set repair, native Lean checks
  for the emitted corpus, checker exactness, and returned-output soundness.

The atomless and finite-depth projection lane handles a different obstacle:

- v451 adds the first checked pointwise revision-preservation artifact.
- v452 through v456 build fixed atomless existential bridges, split-index
  interfaces, a two-step bridge, and an ESSO/SMT audit of the collapsed
  pointwise-revision obligations.
- v457 and v458 turn finite-depth projection into a composable theorem. The
  explicit witness object, `ChainExtends stages ba fa`, records the
  stage-by-stage atomless extension path.
- v459 through v461 prove product-carrier and heterogeneous-chain versions, so
  the remaining gap is no longer finite heterogeneous composition.

The table-expression and packed-carrier lane narrows the compiler boundary:

- v462 adds the first DNF-layer table-expression compiler adequacy theorem.
- v463 compiles finite prefix-word rows into DNF rows under an explicit path
  embedding, while leaving stream-clopen quotient semantics as a separate
  theorem.
- v464 through v466 prove the finite packing arithmetic and the one-step packed
  DNF projection bridge through
  `packedSplitIndex n : SplitIndex (Fin n) (Fin (2*n))`.
- v467 closes the finite table-expression fragment for `rows`, `join`, and
  `project` over the packed carrier.

The algebraic atomless table lane states exactly what is solved and what is
not:

- v468 closes extended pointwise revision for partial updates.
- v469 proves that the splitter property is exactly atomlessness over mathlib
  Boolean algebras.
- v470 proves the BL disjointness and membership core.
- c013 and c017 check the algebraic atomless table layer: splitter iff
  atomlessness, pointwise Boolean-algebra-valued table laws, and table-level
  splitter lift for arbitrary key type `K` and Boolean-algebra value type
  `alpha`.
- v471 checks the concrete semantic clopen bridge: Cantor splitter plus
  semantic clopen subtype proof gives splitter existence for nonzero `Clopen`
  values, with an arbitrary-key table lift for `K -> Clopen`.
- c020 assembles that result with `setAt` and `commonTables` laws for the
  algebraic non-recursive table layer.

These are real semantic proof artifacts, but they do not yet supply
constructive infinite-table executability, recurrence, NSO semantics, or full
Tau lowering.

The later QClopen table-alignment lane sharpens the recurrence boundary. v523
lifts cell alignment to table entries. v524 proves that finite recurrence
approximants preserve table alignment. v525 adds `select` back into the checked
grammar as a computable Boolean predicate on each entry. The exact preservation
shape is:

$$
\operatorname{Aligned}(T)
\Longrightarrow
\operatorname{Aligned}(F(T)).
$$

Standard reading:

```text
If the current table is aligned with the splitter partition, then one
well-formed recurrence-body step produces another aligned table.
```

The important trap is that preservation is not stabilization. v526 proves that
unrestricted same-stratum prime can oscillate. The checked witness is the
one-key Boolean recurrence:

$$
F(T)=T'
$$

and the checked non-stabilization statement is:

$$
\neg \exists N.\ \forall n\ge N,\ F^n(\bot)=F^N(\bot).
$$

Standard reading:

```text
There is no finite stage N such that every later approximant is equal to the
approximant at N.
```

So the constructive recurrence lane must be positive or stratified. v527
therefore defines a positive recurrence fragment, excluding same-stratum prime
and arbitrary select predicates, and proves:

$$
T\le U
\Longrightarrow
F(T)\le F(U).
$$

Standard reading:

```text
If one input table is pointwise below another input table, then evaluating the
same positive recurrence body preserves that pointwise order.
```

v528 then proves the finite-height theorem for this positive fragment, and it
collapses to one step:

$$
\forall n\ge 1,\quad F^n(\bot)=F(\bot).
$$

Standard reading:

```text
For every iterate index n at least one, the nth approximant from bottom equals
the first approximant from bottom.
```

The proof does not enumerate the finite state space. It uses the polynomial
shape of positive recurrence bodies. For every table T:

$$
F(T)\le F(\bot)\vee T.
$$

Together with monotonicity, this gives:

$$
F(\bot)\le F(F(\bot))\le F(\bot)\vee F(\bot)=F(\bot).
$$

Standard reading:

```text
The first inequality says monotonicity pushes the first approximant below the
second. The second inequality says a positive body evaluated at any table T
cannot exceed the join of its first approximant and T. At T = F(bottom), the
upper bound collapses back to F(bottom).
```

So the positive recurrence lane is now not merely monotone. It is checked as
one-step stabilizing. This remains a scoped theorem, not full TABA recurrence:
same-stratum prime is excluded by the v526 oscillator, and arbitrary select
predicates are excluded until their monotonicity obligations are made explicit.

v529 adds the safe stratified-prime interpretation. The safe form is not:

$$
F(T)=T'.
$$

That is the v526 oscillator. The safe form is:

$$
F(T)=G(T,C')
$$

where $C$ is fixed lower-stratum data, and the prime is computed before the
recurrence step. The checked compiler law is:

$$
\operatorname{eval}_{\mathrm{strat}}(E,T)
=
\operatorname{eval}_{\mathrm{pos}}(\operatorname{compile}(E),T).
$$

Standard reading:

```text
Evaluating a stratified-prime recurrence body at table T gives the same table
as first compiling it into a positive recurrence body and then evaluating that
positive body at T.
```

Since the compiled body is positive, v528 transfers immediately:

$$
\forall n\ge 1,\quad
F_{\mathrm{strat}}^n(\bot)=F_{\mathrm{strat}}(\bot).
$$

This is the exact semantic difference: prime on lower-stratum constants is
constant preprocessing; prime on the current recursive state is recurrence
negation and can oscillate.

v530 adds the next safe select lane. The predicate is no longer arbitrary. It
must be upward-closed:

$$
\operatorname{Up}(P)
\;:\!\!\Longleftrightarrow\;
\forall x,y.\ x\le y \wedge P(x)=\mathrm{true}
\Longrightarrow P(y)=\mathrm{true}.
$$

Standard reading:

```text
The predicate P is upward-closed exactly when every accepted value remains
accepted after moving upward in the Boolean order.
```

With that premise, select is monotone:

$$
T\le U \wedge \operatorname{Up}(P)
\Longrightarrow
\operatorname{Select}_{P}(T)\le \operatorname{Select}_{P}(U).
$$

Standard reading:

```text
If table T is pointwise below table U, and P is upward-closed, then selecting
entries of T by P gives a table pointwise below selecting entries of U by P.
```

Trap:

```text
This is a monotonicity statement. It is not a stabilization statement.
```

v531 proves that the trap is real. In the two-bit Boolean algebra, let
$a$ and $b$ be disjoint atoms, and let $P(x)$ mean that both bits of
$x$ are true. Then:

$$
F(T)=b\vee \operatorname{Select}_{P}(a\vee T).
$$

Standard reading:

```text
The recurrence body always includes atom b. It also includes the selected part
of a joined with the current recursive table T, but only when the joined value
passes the threshold predicate P.
```

The checked boundary is:

$$
F(\bot)\ne F^{2}(\bot).
$$

Standard reading:

```text
The first approximant from bottom is not equal to the second approximant from
bottom.
```

This means upward-closed select is safe for recurrence monotonicity, but not
safe for copying the v528 one-step stabilization theorem. Any stronger theorem
for select must either use a narrower source fragment or prove a different
finite-height bound.

v532 adds a finite witness-menu theorem suggested by Aristotle and then checked
locally in the project chain. The premise is important:

$$
\operatorname{CellAligned}(C,x)
\;\wedge\;
\bigvee_{c\in C} c = 1.
$$

Standard reading:

```text
The witness x is aligned with the finite cell list C, and the cells in C cover
the whole Boolean space.
```

Under that premise:

$$
x
=
\bigvee \operatorname{HitCells}(C,x).
$$

Standard reading:

```text
The witness x is equal to the join of exactly the cells in C whose meet with x
is non-bottom.
```

This is the finite-menu bridge:

$$
\operatorname{CellAligned}(\operatorname{SplitPartition}(v_1,\ldots,v_n),x)
\Longrightarrow
x=
\bigvee \operatorname{HitCells}(\operatorname{SplitPartition}(v_1,\ldots,v_n),x).
$$

Standard reading:

```text
If x is aligned with the split partition generated by the splitter values, then
x is completely determined by the finite list of generated cells it hits.
```

Trap:

```text
This is not a theorem that every TABA or NSO witness is aligned. It says that
once alignment is proved, the search space collapses to a finite hit-cell menu.
In the current local proof chain, `HitCells` is proof-level noncomputable. An
executable compiler still needs a decidable hit test or a canonical finite
encoding of the menu.
```

v533 then composes the source-fragment theorem with the menu theorem. For a
well-formed aligned witness expression $E$, define:

$$
\operatorname{Menu}_{C}(E)
:=
\operatorname{HitCells}(C,\llbracket E\rrbracket).
$$

Standard reading:

```text
The menu of E over the cell list C is the list of cells in C whose meet with
the value denoted by E is non-bottom.
```

The checked reconstruction theorem is:

$$
\operatorname{WF}_{C}(E)
\Longrightarrow
\llbracket E\rrbracket
=
\bigvee \operatorname{Menu}_{C}(E).
$$

Standard reading:

```text
If E is well formed over C, then the value denoted by E is equal to the join of
the cells in its menu.
```

The domination theorem has the shape:

$$
\llbracket E\rrbracket \ne 0
\;\wedge\;
\operatorname{eval}_{t}(\llbracket E\rrbracket)
  \wedge \llbracket E\rrbracket \ne 0
\Longrightarrow
\exists c\in \operatorname{Menu}_{C}(E).\,
\operatorname{eval}_{t}(c)\wedge c\ne 0.
$$

Standard reading:

```text
If the value denoted by E is non-bottom and the unary term t still has
non-bottom overlap with that value, then some cell in E's finite menu also has
non-bottom overlap with its own t-evaluation.
```

Trap:

```text
This is a compiler theorem for the `AlignedWitnessExpr` fragment. It is not yet
a compiler theorem for arbitrary TABA, NSO, or Guarded Successor syntax. It also
does not make the menu executable. In this proof chain, the menu is defined by
semantic hit testing, so a runtime compiler still needs a canonical finite
encoding or a decidable hit-test implementation.
```

v534 lifts the same idea over a finite list of candidate expressions. Define:

$$
\operatorname{MenuList}_{C}(E_1,\ldots,E_n)
:=
\operatorname{Menu}_{C}(E_1)
\mathbin{++}\cdots\mathbin{++}
\operatorname{Menu}_{C}(E_n).
$$

Standard reading:

```text
The menu list of a finite expression list is the concatenation of the finite
menus of the individual expressions.
```

The bounded search theorem is:

$$
\exists E\in \mathcal{E}.\,
\operatorname{WF}_{C}(E)
\wedge
\llbracket E\rrbracket\ne 0
\wedge
\operatorname{eval}_{t}(\llbracket E\rrbracket)=1
\Longrightarrow
\exists c\in \operatorname{MenuList}_{C}(\mathcal{E}).\,
\operatorname{eval}_{t}(c)\wedge c\ne 0.
$$

Standard reading:

```text
If some expression in the finite candidate list is well formed, denotes a
non-bottom value, and satisfies the unary-term premise, then some cell in the
flattened finite menu of that candidate list satisfies the local domination
premise.
```

Trap:

```text
This is bounded search, not unbounded NSO quantifier elimination. The finite
candidate list is an explicit premise. A full NSO theorem still needs a
source-language argument showing which candidates must be included.
```

v535 separates executable enumeration from semantic overlap testing. Define:

$$
\operatorname{SelectCells}_{p}(c_1,\ldots,c_n)
:=
[\,c_i\mid p(c_i)=\mathrm{true}\,].
$$

Standard reading:

```text
SelectCells_p returns exactly those cells in the finite list for which the
Boolean predicate p returns true.
```

The checked bridge is:

$$
\Bigl(\forall c\in C.\,
p(c)=\mathrm{true}
\Longleftrightarrow
x\wedge c\ne 0\Bigr)
\Longrightarrow
\operatorname{SelectCells}_{p}(C)
=
\operatorname{HitCells}(C,x).
$$

Standard reading:

```text
If p agrees with the semantic hit test on every cell in C, then selecting cells
by p gives exactly the same cell list as HitCells(C,x).
```

Trap:

```text
This proves the selector bridge, not the hit test itself. A Tau implementation
still needs a concrete overlap test for QClopen cells, for example by finite
prefix comparison or BDD-style normalization.
```

v536 closes the representative-level finite-prefix theorem needed by that
selector bridge. For finite-support clopen representatives $a$ and $b$,
define:

$$
\operatorname{PrefixHit}(a,b)
:=
\exists \beta\in 2^{\max(d(a),d(b))}.\,
(a\wedge b)(\operatorname{extend}(\beta))=1.
$$

Standard reading:

```text
PrefixHit(a,b) means that there is a finite bit assignment, long enough to cover
the support depths of a and b, on which their meet evaluates to true.
```

The checked theorem is:

$$
[\bar a]\wedge[\bar b]\ne 0
\Longleftrightarrow
\operatorname{PrefixHit}(a,b).
$$

Standard reading:

```text
The meet of the quotient classes represented by a and b is non-bottom exactly
when there is a finite max-depth prefix witness where the representative meet is
true.
```

Trap:

```text
This is representative-level. It is enough to explain the finite search behind
the hit predicate, but it is not yet a quotient-independent canonical BDD
implementation.
```

v537 proves the matching negative theorem for arbitrary countable recurrence
unions. Define:

$$
\operatorname{EventuallyOne}(s)
:=
\exists n.\,s(n)=1.
$$

Standard reading:

```text
EventuallyOne holds of a stream exactly when at least one position in the stream
is true.
```

The obstruction is:

$$
\neg\exists c\in \operatorname{Clopen}.\,
\forall s.\,
c(s)=1
\Longleftrightarrow
\operatorname{EventuallyOne}(s).
$$

Standard reading:

```text
There is no finite-support clopen whose truth set is exactly the set of streams
with at least one true bit.
```

Why this proof works:

```text
Any finite-support clopen c has some depth N. The all-false stream and the
stream with a single true bit at position N agree on every position below N.
So c must assign them the same value. But EventuallyOne assigns them different
values.
```

Trap:

```text
This does not kill finite tables. It kills the stronger claim that finite-support
clopens alone are a complete semantic carrier for arbitrary countable recurrence
unions. Full infinite tables need a completion, a larger effective carrier, or a
fragment theorem proving finite stabilization before the countable union is
needed.
```

v556 closes one local representation assumption in the Skolem/minterm lane.
Define guarded choice:

$$
C_g(a,b):=(g\wedge a)\vee(g'\wedge b).
$$

Standard reading:

C_g(a,b) is the join of the part of a under guard g and the part of b under
the prime of g.

The four-coefficient binary minterm representation is:

$$
M_{\vec a}(x,y)
:=
C_x\bigl(C_y(a_{11},a_{10}),C_y(a_{01},a_{00})\bigr).
$$

The checked flat-expansion theorem is:

$$
M_{\vec a}(x,y)
=
(a_{11}\wedge x\wedge y)
\vee(a_{10}\wedge x\wedge y')
\vee(a_{01}\wedge x'\wedge y)
\vee(a_{00}\wedge x'\wedge y').
$$

Standard reading:

The nested guarded-choice minterm value is equal to the join of the four
truth-corner coefficients, restricted respectively to xy, xy', x'y, and x'y'.

The binary source grammar is:

$$
t ::= 0 \mid 1 \mid c \mid x \mid y
\mid t_1\wedge t_2
\mid t_1\vee t_2
\mid t'.
$$

The compiler receipt is:

$$
\forall t\in\mathrm{Term}_2,\quad
\exists \vec a,\quad
\forall x,y,\quad
\llbracket t\rrbracket(x,y)=M_{\vec a}(x,y).
$$

Standard reading:

Every binary Boolean-polynomial term built from constants, x, y, meet, join,
and prime has a four-coefficient minterm representation that is denotationally
equal to the original term for all x and y in any Boolean algebra.

The local minterm-realisability bridge is:

$$
\forall t\in\mathrm{Term}_2,\quad
\exists \vec a,\quad
\forall x,y,\quad
\left(\llbracket t\rrbracket(x,y)=0
\Longleftrightarrow
M_{\vec a}(x,y)=0\right).
$$

Standard reading:

For every binary term, its bottom relation is represented by the bottom
relation of the compiled minterm.

Trap:

v556 is not full Skolemization. It is a binary Boolean-polynomial compiler. It
does not include quantifiers, NSO, table syntax, recurrence, Guarded Successor,
Tau runtime lowering, or arbitrary arity. The next proof target is the same
compiler pattern over Fin n, with 2^n coefficients.

v557 closes that next finite-arity compiler step at the tree level. The source
grammar is:

$$
t ::= 0 \mid 1 \mid c \mid \operatorname{var}(i)
\mid t_1\wedge t_2
\mid t_1\vee t_2
\mid t',
\qquad i\in\operatorname{Fin}(n).
$$

The target is a full binary minterm tree:

$$
\operatorname{Minterm}(\alpha,n).
$$

The compiler theorem is:

$$
\forall n,\quad
\forall t\in\mathrm{Term}_n,\quad
\exists m:\operatorname{Minterm}(\alpha,n),\quad
\forall \rho:\operatorname{Fin}(n)\to\alpha,\quad
\llbracket t\rrbracket(\rho)=\llbracket m\rrbracket(\rho).
$$

The size theorem is:

$$
\operatorname{leafCount}(m)=2^n.
$$

Standard reading:

For every finite arity n, every Boolean-polynomial term over n indexed
variables compiles to a minterm tree of depth n. The compiled tree has the same
denotation as the original term under every Boolean-algebra assignment, and its
number of leaves is exactly 2^n.

Trap:

v557 is stronger than v556 because arity is arbitrary finite n. It is still not
full TABA. The representation is a tree, not a flat packed Fin (2^n) vector. It
does not include quantifier binding, NSO syntax, table rows, recurrence,
Guarded Successor, or Tau lowering.

## 11. Feasibility result: CBF collapse and unsafe-prime boundary

v558 packages the returned Aristotle proof for the next semantic choke point.
The proof file is:

```text
experiments/math_object_innovation_v558/Proofs.lean
```

The generated receipt is:

```text
experiments/math_object_innovation_v558/generated/report.json
```

The checker result was:

```text
theorem_count: 11
forbidden: []
returncode: 0
```

The source syntax is finite-arity and Boolean-valued:

$$
\mathrm{BF}_n
::=
0 \mid 1 \mid \operatorname{var}(i)
\mid f\wedge g
\mid f\vee g
\mid f',
\qquad i\in\operatorname{Fin}(n).
$$

$$
\mathrm{CBF}_n
::=
\operatorname{leaf}(f)
\mid
\operatorname{if}\;g\;\operatorname{then}\;c_1\;\operatorname{else}\;c_2.
$$

$$
\mathrm{Table}_n
::=
\bigl[(g_i,c_i)\bigr]_{i < m}
\;+\;
c_{\mathrm{default}}.
$$

Standard reading:

The BF grammar is the ordinary Boolean-function grammar over $n$ indexed
variables. The CBF grammar adds finite guarded conditionals whose guards are BF
terms and whose branches are CBF terms. The table grammar is a finite priority
row list plus a default CBF value.

Trap:

This is not the whole TABA language. It is the finite Boolean-valued table
surface needed to test whether CBF-style conditionals and priority rows add
semantic power beyond the BF kernel.

The guarded-choice expansion is:

$$
C_g(t,e):=(g\wedge t)\vee(g'\wedge e).
$$

Standard reading:

$C_g(t,e)$ is the join of $g\wedge t$ and $g'\wedge e$.

Plain English:

The guard splits the Boolean space into the part where $g$ holds and the part
where $g'$ holds. The then-branch fills the first part, and the else-branch
fills the second part.

The CBF compiler theorem is:

$$
\forall n,\quad
\forall c\in\mathrm{CBF}_n,\quad
\forall \rho:\operatorname{Fin}(n)\to\mathrm{Bool},\quad
\llbracket \operatorname{cbfToBF}(c)\rrbracket_\rho
=
\llbracket c\rrbracket_\rho.
$$

Standard reading:

For every finite arity $n$, every CBF expression $c$, and every Boolean
assignment $\rho$, evaluating the compiled BF term gives the same Boolean
value as evaluating $c$.

The table compiler theorem is:

$$
\forall n,\quad
\forall T\in\mathrm{Table}_n,\quad
\forall \rho:\operatorname{Fin}(n)\to\mathrm{Bool},\quad
\llbracket \operatorname{tableToBF}(T)\rrbracket_\rho
=
\llbracket T\rrbracket_\rho.
$$

Standard reading:

For every finite arity $n$, every priority table $T$, and every Boolean
assignment $\rho$, evaluating the compiled BF term gives the same Boolean
value as evaluating $T$.

This is the new positive result: finite Boolean-valued CBF and priority-table
syntax collapse to a BF kernel by guarded-choice expansion.

The unsafe boundary is:

$$
F(x):=x',
\qquad
\neg\Bigl(\forall a\,b,\;a\le b \Rightarrow F(a)\le F(b)\Bigr).
$$

Standard reading:

For the prime-step function $F(x)=x'$, it is false that $F$ preserves order
for every ordered pair $a\le b$.

Plain English:

Prime is order-reversing. It cannot be admitted into the same monotone
Kleene fixed-point lane as positive recurrence.

The certified fallback theorem is:

$$
\operatorname{resolve}(F,s,c)=\operatorname{fixed}(x)
\Rightarrow
F(x)=x.
$$

Standard reading:

If the resolver returns a fixed result $x$, then applying $F$ to $x$ gives
back $x$.

Plain English:

The finite loop-certificate path is sound for accepted fixed-point reports.
It is not a monotonicity theorem and not a completeness theorem.

The resulting feasibility shape is:

$$
\operatorname{Sem}(e)=
\begin{cases}
\mu F_e, & e\in\mathcal L_{\mathrm{mono}},\\
\operatorname{resolve}(F_e,c), & e\in\mathcal L_{\mathrm{cert}},\\
\bot_{\mathrm{reject}}, & e\notin
\mathcal L_{\mathrm{mono}}\cup\mathcal L_{\mathrm{cert}}.
\end{cases}
$$

Standard reading:

An expression in the monotone lane receives least-fixed-point semantics. An
expression in the certificate lane receives resolver semantics. An expression
outside both lanes is rejected.

Research conclusion:

Full TABA is theoretically feasible as a stratified semantic architecture. It
is not feasible as one unrestricted same-stratum monotone fixed-point universe,
because the prime-step counterexample is already enough to break monotonicity.

## 12. CBF priority tables as explicit minterm trees

v559 composes the v558 CBF/table collapse with the v557 minterm-tree compiler.
The proof file is:

```text
experiments/math_object_innovation_v559/Proofs.lean
```

The generated receipt is:

```text
experiments/math_object_innovation_v559/generated/report.json
```

The checker result was:

```text
theorem_count: 14
forbidden: []
returncode: 0
```

The direct compiler is:

$$
\operatorname{compileTableToMinterm}
:
\mathrm{Table}_n\to\operatorname{Minterm}(n).
$$

The semantic theorem is:

$$
\forall n,\quad
\forall T\in\mathrm{Table}_n,\quad
\forall \rho:\operatorname{Fin}(n)\to\mathrm{Bool},\quad
\operatorname{evalMinterm}
\bigl(\operatorname{compileTableToMinterm}(T),\rho\bigr)
=
\llbracket T\rrbracket_\rho.
$$

The size theorem is:

$$
\operatorname{leafCount}
\bigl(\operatorname{compileTableToMinterm}(T)\bigr)
=2^n.
$$

Standard reading:

For every finite arity $n$, every Boolean-valued CBF priority table $T$,
and every Boolean assignment $\rho$, the explicit minterm tree compiled from
$T$ evaluates to the same Boolean value as $T$. The compiled tree has
exactly $2^n$ leaves.

Plain English:

Finite CBF priority tables now have a checked full-case-tree meaning. This is
useful for demos, bounded proof search, and later Tau lowering, because the row
syntax can be compared against a complete semantic case tree.

Trap:

v559 is still finite and nonrecursive. It does not prove full TABA recurrence,
first-class NSO, Guarded Successor, or production Tau lowering.

The next proof milestones should now be kept narrow:

```text
Milestone A:
  connect finite mixed-hit QE to formula normalization and a QE driver

Milestone B:
  connect v497 dyadic leaves to the c047 formula grammar and splitter-choice policy

Milestone C:
  prove formula-level QE driver soundness for the bounded splitter schedule

Milestone D:
  make v499's live-key extraction executable for a concrete carrier

Milestone E:
  package v500-v502 as a positive omega-carrier interface

Milestone F:
  compile_rows_join_project_to_explicit_finite_muller
  + semantic adequacy for the v400 fragment

Milestone G:
  extend to the v401 finite recurrence-approximant fragment

Milestone H:
  decide which real TABA recurrence bodies fit PositiveRecTableExpr

Milestone I:
  connect real TABA stratification syntax to the v529 source grammar

Milestone J:
  characterize finite-height bounds for upward-closed select recurrence

Milestone K:
  connect v536's representative hit predicate directly to v535's selector bridge

Milestone L:
  make the hit predicate quotient-independent by canonicalization or BDD normalization

Milestone M:
  define the source-language finite witness budget for bounded NSO

Milestone N:
  choose the completed or automata carrier needed beyond the v537 obstruction

Milestone O:
  prove larger source constructors compile into AlignedWitnessExpr, or record
  the exact boundary where they fail

Milestone P:
  flatten v557 minterm trees into packed Fin (2^n) coefficient vectors, then
  connect that compiler to the bounded NSO witness-menu source grammar
```

## 13. Compound mismatch checking for the Tau table demos

After the type-inference cache experiments failed to produce a speedup, the
next successful optimization came from changing the proof obligation shape used
by the public demo harness.

The separate demo checks ask Tau to solve one mismatch query at a time:

$$
\operatorname{Unsat}(\operatorname{Diff}_1),\quad
\operatorname{Unsat}(\operatorname{Diff}_2),\quad
\ldots,\quad
\operatorname{Unsat}(\operatorname{Diff}_n).
$$

The compound check asks one larger question:

$$
\operatorname{Unsat}
\left(
  \bigvee_{i < n}\operatorname{Diff}_i
\right).
$$

The checked logical law is:

$$
\operatorname{Unsat}
\left(
  \bigvee_{i < n}\operatorname{Diff}_i
\right)
\Longleftrightarrow
\forall i < n,\ \operatorname{Unsat}(\operatorname{Diff}_i).
$$

Standard reading:

The disjunction of all mismatch predicates is unsatisfiable if and only if
every listed mismatch predicate is unsatisfiable.

Plain English:

The harness can ask, "does any table-vs-raw mismatch exist?" If the answer is
no, then every listed table equivalence passes.

The proof packet is:

```text
tau_compound_table_check_2026_04_15
```

The current executable receipt from `TauLang-Experiments` is:

```text
checks:              15
individual elapsed:  118544.824 ms
compound elapsed:     53147.339 ms
elapsed reduction:       55.167%
```

The smooth table-demo runner now uses the compound-only mode by default. Its
latest fresh receipt is:

```text
equivalence mode: compound
compound checks:  15
compound elapsed: 54939.340 ms
result:           passed
```

Research conclusion:

This is a real optimization, but it is not a new table semantic feature. It
reduces repeated process startup, parsing, source loading, and command setup in
the public demo harness. It also gives a useful pattern for Tau optimization
work: sometimes the fastest improvement is to reshape the verification question
before changing the solver internals.

## 14. Equality-aware path simplification

The next target comes from Tau's own known-issues list. Tau's README says that
path simplification does not take equalities between variables into account,
which can lead to later blowups.

The safe substitution premise is:

$$
\forall x,\quad \rho(\operatorname{rep}(x))=\rho(x).
$$

Standard reading:

For every variable $x$, the environment $\rho$ gives $x$ the same Boolean value
as the representative chosen for $x$.

The semantic preservation theorem is:

$$
\left(\forall x,\ \rho(\operatorname{rep}(x))=\rho(x)\right)
\Longrightarrow
\llbracket \operatorname{subst}_{\operatorname{rep}}(e)\rrbracket_\rho
=
\llbracket e\rrbracket_\rho.
$$

Standard reading:

If the environment respects the representative map, then evaluating the
representative-substituted expression gives the same Boolean value as evaluating
the original expression.

Plain English:

On a branch where the formula already says two variables are equal, the
normalizer can replace one by the other inside that branch and then simplify the
resulting expression.

Trap:

The branch condition is essential. Representative substitution is not globally
valid. The executable model records counterexamples where the substitution
changes the value outside the equality-assumption path.

The proof packet is:

```text
tau_equality_path_simplification_2026_04_15
```

The executable model is:

```text
scripts/run_equality_path_simplification_demo.py
```

Current receipt:

```text
cases:             3
original nodes:    29
optimized nodes:   10
node reduction: 65.517%
semantic checks: passed
```

The related Tau-facing branch-recombination probe is:

```text
scripts/run_equality_split_tau_probe.py
```

Tau already simplifies simple branch-local equality paths, such as
`x = y:sbf && ((x & y') = 0)`, to `x = y`. The remaining probe is narrower:
after an equality split creates two branches, can the normalizer recombine the
residual branches?

The recombination law is:

$$
(A\wedge B)\vee(\neg A\wedge B)\Longleftrightarrow B.
$$

Standard reading:

The disjunction of the branch where $A$ and $B$ both hold and the branch where
$A$ is false but $B$ holds is equivalent to $B$.

Plain English:

If both sides of a split keep the same residual condition, the split can be
removed.

It checks candidate shorter targets with Tau itself by asking:

$$
\operatorname{Unsat}
\left(
  \neg(\operatorname{Original}\leftrightarrow\operatorname{Target})
\right).
$$

Standard reading:

The negation of the equivalence between the original formula and the target
formula is unsatisfiable.

Plain English:

Tau found no counterexample separating the longer current normal form from the
shorter target form.

Current Tau-facing branch-recombination receipt:

```text
cases:                         4
useful reduction cases:        4
matched target cases:          0
Tau-normalized characters:   152
target-normalized characters: 36
character reduction:      76.316%
equivalence checks:       passed
```

The local proof packet is:

```text
tau_equality_split_recombination_2026_04_15
```

The first feature-gated Tau patch is:

```text
TAU_EQUALITY_SPLIT_RECOMBINE=1
```

Current enabled receipt:

```text
cases:                         4
matched target cases:          3
target-sized cases:            4
Tau-normalized characters:    36
target-normalized characters: 36
MNF-matched target cases:      4
```

Research conclusion:

This is now the strongest next Tau-native normalization target. It is named by
Tau's own README, has a small checked semantic law, and has a bounded
executable model with both positive reductions and negative counterexamples.
The Tau-facing probe sharpens the implementation frontier: Tau can simplify
simple equality paths, but it does not yet recombine all resulting equality
split branches without the feature flag. The feature-gated patch closes all
four checked size-reduction cases. Three match the target text exactly under
`normalize`, and all four match under `mnf`. The remaining work is
presentation-level on the checked cases: canonicalize equivalent term ordering
in the three-alias residual case, then test the full normalizer path on a larger
equality-split corpus.

The wider alias-order smoke test extends the same result:

```text
cases:                         8
matched target cases:          3
target-sized cases:            8
Tau-normalized characters:   108
target-normalized characters: 108
MNF-matched target cases:      8
```

The additional cases permute the equality path and include a transitive alias
chain. They are still bounded smoke tests, not a proof of all equality-path
normalization. They do show that the remaining mismatch is display
canonicalization, not a missed semantic reduction on the checked corpus.

## 15. Effects, derivatives, and finite-carrier equivalence

The latest optimizer proof lane is not qelim-specific. It asks a different
question: once a Tau-shaped expression exists, which parts need to be evaluated,
reevaluated, or compared?

The locally audited packets are:

```text
c117  optimization-lifting coherence
c118  reads/effect analysis
c119  incremental evaluation bound
c120  Tau-Brzozowski derivative
c121  extended bisimulation completeness
c122  complete equivalence check by evaluation wrapping
c123  partial evaluation
c124  table Reader-monad laws
```

All eight packets were rebuilt locally with `lake build` in their pinned
mathlib projects, and the `Proofs.lean` files scanned clean for `sorry`,
`admit`, `axiom`, `unsafe`, and `sorryAx`.

The read-set theorem has this shape:

$$
\rho\!\restriction_{\operatorname{Reads}(e)}
=
\rho'\!\restriction_{\operatorname{Reads}(e)}
\Longrightarrow
\llbracket e\rrbracket_{\rho}
=
\llbracket e\rrbracket_{\rho'}.
$$

Standard reading:

If two environments agree on all keys read by expression $e$, then evaluating
$e$ in those two environments gives the same table.

Plain English:

The compiler can skip reevaluation when the changed input is not in the
expression's read set.

Boundary:

This is proved for the Tau-like kernel with explicit variable reads. It is not
yet a proof about Tau's full C++ IR or runtime cache.

The derivative theorem introduces a symbolic one-key update:

$$
\partial_{k,v} e.
$$

Its soundness theorem is:

$$
\llbracket \partial_{k,v} e\rrbracket
=
\operatorname{update}
\left(
  \llbracket e\rrbracket,
  k,
  \operatorname{evalConst}(e,v)
\right).
$$

Standard reading:

The denotation of the derivative is the old denotation updated at key $k$ by
the value obtained from evaluating the expression shape with constant leaf value
$v$.

Plain English:

The derivative describes the semantic effect of a single-key perturbation
without rebuilding an unrelated expression.

Boundary:

This is not a regex derivative and not a whole Tau delta engine. It is a
checked expression-transform law that can guide such an engine.

The extended bisimulation result is the most important correction to the
rewrite-normalizer account. The original seven-rule relation is sound but not
complete. The counterexample is structural: it lacks rules that evaluate
compound expressions built from constants. Adding constant-evaluation rules
gives:

$$
e \sim_{\mathrm{eval}} \operatorname{const}(\llbracket e\rrbracket).
$$

Therefore:

$$
\llbracket e_1\rrbracket=\llbracket e_2\rrbracket
\Longrightarrow
e_1\sim_{\mathrm{eval}} e_2.
$$

Standard reading:

Every expression is related to the constant expression containing its denotation.
Therefore, if two expressions have equal denotations, the extended relation
relates the two expressions.

Plain English:

The extended relation is complete because it can always collapse the expression
to its meaning.

Boundary:

This is algebraic completeness, not automatic executable equivalence over every
carrier. For finite Boolean-algebra carriers, semantic table equality is
decidable, so the relation gives a real decision procedure for the checked
kernel. For infinite carriers, the semantic equality premise may still be hard
or undecidable.

The partial-evaluation theorem is:

$$
\operatorname{Compatible}(K,\rho)
\Longrightarrow
\llbracket \operatorname{partialEval}(K,e)\rrbracket_{\rho}
=
\llbracket e\rrbracket_{\rho}.
$$

Standard reading:

If runtime environment $\rho$ agrees with the compile-time known-input map $K$,
then partially evaluating $e$ with $K$ preserves the denotation of $e$.

Plain English:

Known inputs can be compiled away, but only under the compatibility condition.

Research conclusion:

The optimizer frontier has split into two complementary lanes. The qelim lane
chooses a backend for eliminating quantifiers. The effect/derivative lane
chooses what should be recomputed after a small input change. The second lane is
especially relevant for stream-like Tau workloads and table demos, because most
ticks may change only a small part of the input environment.

The executable companion now lives in `TauLang-Experiments`:

```text
scripts/run_tau_derivative_equivalence_demo.py
```

Current receipt:

```text
cases:                         80
derivative sound cases:        80
size-preserved cases:          80
away-from-key cases:           80
at-key cases:                  80
equivalence classifications:   80
equivalent cases:              61
non-equivalent cases:          19
result:                        passed
```

Boundary:

The script checks the c120/c121/c122 idea on a finite Tau-like kernel. It does
not prove Tau parser integration, a runtime delta engine, or infinite-carrier
equivalence decidability.

The earlier incremental-execution demo has also moved closer to a runtime
shape. It now builds a child-before-parent node table, records a dependency
index from input key to node IDs, and executes a one-pass dirty-node update.
The current receipt is:

```text
full unique residual nodes:    193
runtime-delta recomputed:       31
runtime-delta saving:       83.938%
runtime dependency checks:   passed
runtime delta checks:        passed
```

Boundary:

This remains a standalone Tau-like kernel. It demonstrates the data structure
shape a Tau runtime patch would need, but it is not yet wired into Tau's C++
runtime.

The native Tau runtime now has a measurement hook:

```text
TAU_RUN_STATS=1
```

The hook records per-step interpreter counters from the real `run` loop. The
first opt-in optimization on this surface is:

```text
TAU_SKIP_UNCHANGED_IO_REBUILD=1
```

It avoids rebuilding input or output stream objects when an accepted update does
not change the IO stream set. The current update-stream pointwise-revision
smoke case gives:

```text
step count:              3
accepted update count:   3
total paths attempted:   6
total paths solved:      6
total outputs:           6
total revisions tried:   1
total added spec parts:  2
input rebuilds skipped:  3
output rebuilds skipped: 1
output parity:           passed
final memory size:       9
```

Standard reading:

On the native Tau run-loop smoke case, three execution steps were performed.
The interpreter accepted three updates, attempted six disjunct paths, solved six
disjunct paths, emitted six output bindings in total, added two specification
parts, revised one existing specification part, and ended with nine memory
bindings.

Plain English reading:

The real interpreter is now instrumented at the step boundary needed for the
next cache experiment, and a small IO-rebuild skip now has baseline-output
parity evidence.

Boundary:

This is an IO-rebuild optimization, not incremental expression evaluation. It
does not skip solver work or prove whole-language cache correctness.

The follow-up stream-class regression adds the missing boundary check:

```text
vector input rebuilds skipped:  3
vector output rebuilds skipped: 1
file input rebuilds skipped:    0
file output rebuilds skipped:   0
vector output parity:           passed
file output parity:             passed
```

Standard reading:

On vector-remapped streams, unchanged rebuild skipping preserves the observed
outputs. On file-remapped streams, the skip flag performs zero skips.

Plain English reading:

The optimization is now guarded by the stream class. It may skip streams whose
rebuild operation preserves state, but it does not skip file streams because
file rebuilds intentionally reopen files.
