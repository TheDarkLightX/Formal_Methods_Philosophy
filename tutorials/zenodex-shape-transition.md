---
title: "ZenoDEX shape transition: from baseline assurance to Shape++"
layout: docs
kicker: Tutorial 18
description: How the ZenoDEX shape was strengthened from a guarded, replayable baseline into a more canonical, exact, proof-carrying target, and why that change prunes disaster states from the reachable state space.
---

Every software system lives inside a space of possible states. Some of those states are safe. Others are disasters: a drained reserve, an ambiguous winner, a stale-oracle execution. The central question of shape engineering is straightforward:

> Can the system still reach any of those disaster states?

That is the question this tutorial explores.

For ZenoDEX, the old shape was already strong by normal software standards. It was guarded, replayable, partially proved, and built around exact integer arithmetic. The new target shape, called `Shape++`, asks for something stricter: ambiguous winners should disappear, accounting should be exact rather than merely monotone, invalid economic states should be hard to represent, and important runtime decisions should carry replayable evidence.

This tutorial explains that transition as mathematics, not as branding. By the end, you will understand exactly which disaster families each new clause removes from the reachable state space, and why that removal is the real security story.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Scope and assumption hygiene</p>
  <ul>
    <li><strong>Source posture:</strong> this tutorial is based on the public ZenoDEX shape notes, optimization notes, reasoning scenarios, disaster-state catalog, security-posture note, and chaos-toolkit docs inspected on March 20, 2026.</li>
    <li><strong>Important scope point:</strong> <code>Shape++</code> is treated here as a <em>target shape</em>, not as a blanket claim that every clause is already fully proved and fully deployed everywhere.</li>
    <li><strong>Model choice:</strong> when this page talks about a "shape," it means a compressed description of states, transitions, invariants, canonicalizers, and evidence gates.</li>
    <li><strong>Security reading:</strong> "ideal" does not mean metaphysically perfect. It means "a strong candidate attractor for the mechanism, given the recurring proof and hardening directions already present in the repo."</li>
  </ul>
</div>

## Part I: what a shape changes mathematically

Let a mechanism be modeled as a transition system

$$
M = (Q, q_0, \to, I)
$$

where:

- $Q$ is the state space,
- $q_0$ is the initial state,
- $\to$ is the transition relation,
- $I$ is the set of invariants and admissibility rules.

The reachable states are

$$
\operatorname{Reach}(M) := \{ q \in Q \mid q_0 \to^* q \}.
$$

Now define a disaster set $D \subseteq Q$. A disaster state might be:

- an economically invalid fill,
- a reserve-draining swap,
- an ambiguous winner,
- a stale-oracle execution,
- a non-canonical settlement packet,
- a deadlock after a phase closes.

The basic assurance question is:

$$
\operatorname{Reach}(M) \cap D = \varnothing \; ?
$$

This is the first reason shape matters. A stronger shape is not just "more rules." It changes the relation between reachable and unreachable worlds.

If a new shape only adds guards, certificates, or stronger canonicalization, then the usual strengthening picture is:

$$
\operatorname{Reach}(M_{\text{new}}) \subseteq \operatorname{Reach}(M_{\text{old}}).
$$

That inclusion is the heart of the security story. The new mechanism can still do the safe things the old mechanism did, but some formerly reachable bad states are cut away.

The diagram below makes the geometry concrete. The full state space is the outer boundary. The old shape already restricts reachability (blue). The stronger shape restricts it further (inner region), and the disaster set (red) no longer overlaps with what the new mechanism can reach.

<figure class="fp-figure">
  <p class="fp-figure-title">State-space pruning: how a stronger shape removes disaster states</p>
  {% include diagrams/shape-state-space-pruning.svg %}
  <figcaption class="fp-figure-caption">
    A stronger shape shrinks the reachable region until it no longer intersects the disaster set.
  </figcaption>
</figure>

## Part II: the old ZenoDEX shape

The best compressed source-backed summary of the older full-stack shape is:

$$
\text{OldShape}(Z)
:=
\text{BoundaryValidity}
\wedge
\text{TemporalAdmissibility}
\wedge
\text{CanonicalWinnerSelection}
\wedge
\text{ReserveMonotonicity}
\wedge
\text{SettlementCompositionality}
\wedge
\text{DeterministicRouting}
\wedge
\text{StablecoinSolvency}.
$$

The earlier tutorial compressed the same posture into the more human-readable slogan

$$
\text{CurrentTagline}(Z)
:=
\text{Deterministic}
\wedge
\text{Replayable}
\wedge
\text{PartiallyProved}
\wedge
\text{StronglyGuarded}.
$$

That slogan is useful, but the longer formula tells more of the engineering story.

### 1. Boundary validity

The old shape already had strong pointwise boundary guards. A representative example is the reserve invariant guard:

$$
K_{\text{before}} := reserve\_in_{\text{before}} \cdot reserve\_out_{\text{before}}
$$

$$
K_{\text{after}} := reserve\_in_{\text{after}} \cdot reserve\_out_{\text{after}}
$$

$$
\text{ReserveInvariantGuard}
:=
\text{ParamsOK}
\wedge
\text{ReservesOK}
\wedge
\text{SafeOK}
\wedge
\text{DriftOK}
\wedge
(K_{\text{after}} \ge K_{\text{before}}).
$$

This is already fail-closed at the boundary, in the limited sense that malformed or reserve-breaking transitions should be rejected before they become runtime history.

### 2. Temporal admissibility

The old shape also constrained traces over time, not just single-step arithmetic. A representative nonce shadow law is:

$$
\text{Accept}
:=
\exists n.\;
n = lastUsedNonce + 1
\wedge
lastUsedNonce' = n
\wedge
accepted' = \text{TRUE}
$$

with the key invariant

$$
\text{NonceNeverDecreases}
:=
lastUsedNonce \ge prevLastUsedNonce.
$$

This blocks one large class of disaster states:

$$
D_{\text{replay}}
:=
\{ q \mid accepted(q) \wedge requestedNonce(q) \le lastUsedNonce(q) \}.
$$

### 3. Canonical winner selection

The old shape already knew that deterministic procedures are not enough. At the batch level, the stronger theorem shape is:

$$
\forall S \ne \varnothing.\;
\exists! k \in S.\;
\forall x \in S,\; key(k) \le key(x).
$$

This is better than

$$
\text{same inputs} \to \text{same output}
$$

because it rules out semantic ambiguity instead of merely hiding it behind implementation order.

### 4. Reserve monotonicity

The old arithmetic floor was:

$$
K_{\text{after}} \ge K_{\text{before}}.
$$

That is good. It rules out a large class of direct reserve-drain witnesses. But it is still only a monotonicity statement.

### 5. Settlement compositionality

The settlement algebra already had a strong compositional law:

$$
\Delta(s_1 \circ_s s_2) = \Delta(s_1) + \Delta(s_2).
$$

That means reasoning about append and composition is lawful rather than ad hoc:

$$
batchToSettlement(b_1 ++ b_2)
=
batchToSettlement(b_1) \circ_s batchToSettlement(b_2).
$$

### 6. Deterministic routing

The older routing posture already had deterministic tie-breaks, exact-in and exact-out objectives, and full-allocation runtime checks. That is already better than a heuristic quote engine: the same inputs always produce the same output. But "same output every time" is not the same as "the semantically correct output." Deterministic routing can consistently pick the wrong winner if the tie-break rule happens to favor it. Several reasoning notes showed this pressure point:

> Deterministic routing is weaker than globally canonical routing.

### 7. Stablecoin solvency

The zUSD layer already had strong solvency and recovery-mode formulas. For example:

$$
\text{MCR\_OK}(collateral, debt, price, mcr)
:=
debt = 0
\vee
collateral \cdot price \cdot 10000 \ge debt \cdot mcr \cdot 10^8
$$

and the risky-operations gate:

$$
\text{RiskyOpsAllowed}
:=
oracle\_seen
\wedge
price > 0
\wedge
price\_pending > 0
\wedge
price\_pending = price
\wedge
\text{OracleFresh}
\wedge
\neg \text{RecoveryMode}.
$$

This is already a serious assurance surface. The new shape does not start from nothing.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Why list all seven clauses?</p>
  <p>
    Listing the old shape explicitly matters because <code>Shape++</code> does not replace it.
    It <em>extends</em> it. Every old clause remains active; the new shape only adds stronger
    requirements on top. Understanding what was already guarded is essential for seeing what the
    new clauses actually change.
  </p>
</div>

The following diagram shows the transition at a glance: the old shape's seven clauses on the left, the stronger Shape++ target's ten clauses on the right, with the key insight that each new clause either eliminates ambiguity, requires evidence, or makes bad states unrepresentable.

<figure class="fp-figure">
  <p class="fp-figure-title">Old shape versus Shape++: the clause-level transition</p>
  {% include diagrams/shape-old-vs-new.svg %}
  <figcaption class="fp-figure-caption">
    Blue pills are the inherited baseline clauses. Orange pills are the new or strengthened clauses that Shape++ adds.
  </figcaption>
</figure>

## Part III: the target shape, `Shape++`

The new candidate ideal is:

$$
\text{Shape}_{++}(Z)
:=
\text{CBCValidity}
\wedge
\text{UniqueCanonicalWinnerEverywhere}
\wedge
\text{ExactFeeAwareAccounting}
\wedge
\text{ValueAwareSettlementSafety}
\wedge
\text{ProofCarryingOptimizerCertificates}
\wedge
\text{AntiFragmentationByTheorem}
\wedge
\text{NonCommutativityQuarantine}
\wedge
\text{OracleDivergenceSafety}
\wedge
\text{LiquidationSpiralContainment}
\wedge
\text{CrossLayerReplayParity}.
$$

For teaching, it is also useful to compress the target into a shorter slogan:

$$
\text{TargetTagline}(Z)
:=
\text{Canonical}
\wedge
\text{Exact}
\wedge
\text{ValueAware}
\wedge
\text{ProofCarrying}
\wedge
\text{CrossLayerEquivalent}
\wedge
\text{FailClosedEverywhereImportant}.
$$

The names `CrossLayerEquivalent` and `FailClosedEverywhereImportant` are pedagogical compressions. They summarize several narrower clauses rather than naming one already-promoted theorem.

### 1. CBC validity: invalid fills become hard to represent

Think of a vending machine that physically cannot dispense less than one item. The same idea applies here: instead of checking after the fact whether a fill met the user's minimum, the type system itself refuses to construct a "filled" object unless the proof exists. The central formula is:

$$
\text{ValidOutcome}(i)
::=
unfilled
\;\mid\;
filled(output,\; pf : output \ge min\_out(i)).
$$

Then surplus non-negativity is structural:

$$
\forall i,\; o : \text{ValidOutcome}(i).\;
surplus(i,o) \ge 0.
$$

This is a major strengthening. It turns the disaster state

$$
D_{\text{invalid-fill}}
:=
\{ q \mid filled(q) \wedge output(q) < min\_out(q) \}
$$

from "a state that must be filtered out later" into "a state that should never be admitted as a valid outcome object in the first place."

### 2. Unique canonical winners everywhere

The stronger canonical form is:

$$
\forall C \ne \varnothing.\;
\exists! w \in C.\;
\forall c \in C,\; Key(w) \le Key(c).
$$

This blocks the disaster family

$$
D_{\text{ambiguous}}
:=
\left\{
q \mid
\exists a \ne b.\;
feasible(a) \wedge feasible(b)
\wedge score(a)=score(b)
\wedge winner(a)
\wedge winner(b)
\right\}.
$$

This is exactly the difference between "the program happened to pick one route" and "there exists one semantically canonical route."

### 3. Exact fee-aware accounting

Imagine a cash register that says "the total went up" without telling you how much of the increase was the price and how much was the tax. That is what monotonicity alone provides. Exact accounting is the receipt that itemizes every cent. The stronger target is not merely monotonicity:

$$
K_{\text{after}} \ge K_{\text{before}}.
$$

It is exact residue accounting:

$$
K(batch\_fee(s, amounts, fees))
=
K(s) + \sum_i FeeAwareGap(s_i, a_i, f_i).
$$

The advantage is not cosmetic. It blocks silent-leak or unexplained-residue worlds such as

$$
D_{\text{fee-leak}}
:=
\{ q \mid \text{the system claims exact conservation but floor residue is discarded} \}.
$$

This is the difference between "nothing obviously broke" and "every remainder has a place in the model."

### 4. Value-aware settlement safety

One current narrowing of this target is already visible in the replayable settlement packet line. Its acceptance shell is of the form

$$
packet\_ok
\leftrightarrow
strong\_certificate\_ok
\wedge
feature\_extension\_ok
\wedge
module\_bundle\_ok
\wedge
full\_price\_rails\_ok
\wedge
value\_lane\_ok.
$$

That matters because token conservation alone does not settle every economic question. A system can conserve token counts and still be value-blind if it ignores price rails, LP liabilities, or declared valuation semantics.

The disaster family here is:

$$
D_{\text{value-blind}}
:=
\{ q \mid \text{settlement accepted without satisfying the declared value interpretation} \}.
$$

### 5. Proof-carrying optimizer certificates

In a traditional system, the optimizer says "route X wins" and you trust it. In a proof-carrying system, the optimizer says "route X wins, and here is the replayable evidence that X is optimal over the declared candidate domain." The evidence is checkable by anyone. The stronger pattern is:

$$
\text{ExecutableWinner}(c) \to \text{ProofOK}(c) \wedge \text{BindingOK}(c).
$$

This changes routing and optimization from "the runtime gave an answer" to "the runtime gave an answer together with a replayable reason that the answer is the right one on the declared candidate domain."

That blocks a family like:

$$
D_{\text{uncertified-winner}}
:=
\{ q \mid winner(q) \wedge \neg certificate(q) \}.
$$

It also supports a cleaner fail-closed rule:

$$
\neg(\text{ProofOK} \wedge \text{BindingOK}) \to reject.
$$

### 6. Anti-fragmentation by theorem

Suppose you need to move 100 units through one pool in one direction. Splitting the order into five 20-unit fragments can never beat executing one 100-unit operation, because the constant-product curve penalizes fragmentation. This clause turns that mathematical fact into a pruning rule: the router does not need to consider fragmented candidates at all, because they are theorem-dominated. The key law is:

$$
\text{SamePoolSameDirection}(F_1,\dots,F_n)
\to
Out(single(\sum_i F_i)) \ge OutSeq(F_1,\dots,F_n).
$$

This is not merely an optimization hint. It is a state-space pruning law. It says an entire family of fragmented candidates can be discarded without losing the canonical winner.

### 7. Non-commutativity quarantine

In everyday arithmetic, 3 + 5 = 5 + 3. But in a liquidity pool, buying then selling is not the same as selling then buying, because each operation changes the price curve for the next. This clause makes that asymmetry explicit rather than assuming it away. The useful law is the negative guardrail:

$$
\text{OppositeDirection}(s_1,s_2) \to \neg AssumeCommutes(s_1,s_2).
$$

or in gap language,

$$
\text{OppositeDirection}(s_1,s_2) \to Gap(s_1,s_2) > 0.
$$

This prevents unsound canonicalization and unsound optimizer pruning.

### 8. Oracle divergence safety

A price oracle is the system's window into external market conditions. If the "pending" price and the "committed" price disagree, the system is looking through two windows at once, and they show different views. Under the old shape, this was a warning. Under Shape++, it is a hard gate: no risky operation proceeds until the views align.

The core gate is:

$$
\text{RiskyOpsAllowed}
:=
oracle\_seen
\wedge
price > 0
\wedge
price\_pending > 0
\wedge
price\_pending = price
\wedge
\text{OracleFresh}
\wedge
\neg \text{RecoveryMode}.
$$

So the disaster family is:

$$
D_{\text{oracle-mismatch}}
:=
\{ q \mid risky(q) \wedge price\_pending(q) \ne price(q) \}.
$$

### 9. Liquidation spiral containment

This clause needs explicit scoping. The target-shape note itself warns that the broad slogan is stronger than current evidence.

A narrower, source-backed working reading is:

$$
\text{LiquidationAllowed}
:=
oracle\_seen
\wedge
price\_pending > 0
\wedge
debt > 0
\wedge
\neg \text{MCR\_OK}(collateral, debt, price\_pending, mcr)
\wedge
debt \le sp\_debt.
$$

This does not prove the entire macro-dynamics of liquidation spirals. What it does do is make the next-step liquidation posture explicit and bounded.

### 10. Cross-layer replay parity

If a flight's air-traffic control record says "landed at gate B7" but the airline's own system says "landed at gate C3," something is badly wrong, even if the plane is safe. The same principle applies here: the runtime, the certificate surface, and the proof-backed reconstruction must agree on the same observable result.

A pedagogical compression is:

$$
\text{CrossLayerEquivalent}(obs)
:=
obs_{\text{runtime}}
=
obs_{\text{certificate}}
=
obs_{\text{proof}}.
$$

In fail-closed form, one wants:

$$
obs_{\text{runtime}} \ne obs_{\text{certificate}} \to reject.
$$

This blocks drift worlds:

$$
D_{\text{drift}}
:=
\{ q \mid \text{two trusted layers reconstruct different winners, packets, or rejection reasons} \}.
$$

## Part IV: what changed, clause by clause

The transition from old shape to Shape++ is not a rewrite. It is a sequence of precise strengthenings, each targeting a specific weakness in the original posture. The table below maps every old clause to its stronger counterpart, names the mathematical change, and identifies which disaster family the strengthening removes.

| Older clause | Stronger clause | What changes mathematically | Which bad family is pruned |
|---|---|---|---|
| `DeterministicRouting` | `UniqueCanonicalWinnerEverywhere` | Moves from repeated output to unique semantic representative | ambiguous maximizers |
| `ReserveMonotonicity` | `ExactFeeAwareAccounting` | Moves from inequality to exact residue accounting | silent fee leakage, unexplained remainders |
| runtime validity checks | `CBCValidity` | Moves from post-hoc filtering to validity by construction | filled-below-minimum outcomes |
| local routing checks | `ProofCarryingOptimizerCertificates` | Moves from "runtime chose X" to "runtime chose X with a replayable witness" | uncertified winners |
| token-count safety | `ValueAwareSettlementSafety` | Adds declared value interpretation and price rails | value-blind settlement acceptance |
| heuristic pruning | `AntiFragmentationByTheorem` | Prunes dominated fragmented candidates lawfully | needless split-candidate explosion |
| tacit ordering assumptions | `NonCommutativityQuarantine` | Makes ordering sensitivity explicit | unsound commuting rewrites |
| solvency plus freshness checks | `OracleDivergenceSafety` | Treats mismatched oracle views as inadmissible for risky transitions | stale or in-flight oracle execution |
| bounded liquidation posture | `LiquidationSpiralContainment` | Narrows allowed next steps under stress | uncontrolled liquidation transitions |
| replayable local checks | `CrossLayerReplayParity` | Aligns runtime, packet, and proof surfaces | cross-layer semantic drift |

This table explains why `Shape++` feels "ideal" in the engineering sense. It is not ideal because it sounds elegant. It is ideal because every strengthening follows the same pattern:

1. make invalid states unrepresentable where possible,
2. make ambiguous states non-canonical where representation must stay broad,
3. require replayable evidence at important boundaries,
4. reject on mismatch instead of guessing.

<div class="fp-callout fp-callout-try">
  <p class="fp-callout-title">See it live</p>
  <p>
    The <a href="#part-vi-an-interactive-state-space-lab">interactive lab in Part VI</a> lets you toggle
    these clauses individually and watch the disaster-state count change in real time. Try removing
    one strengthening clause at a time to see which disaster family it was blocking.
  </p>
</div>

## Part V: the state-space view: unreachable disaster states

Abstract clauses become concrete when you write down the exact disaster formulas they eliminate. Each formula below describes a family of bad states. Under the old shape, some of these families still had members inside the reachable region. Under Shape++, each one is either structurally impossible to represent or explicitly rejected before it can become history.

### 1. Partial exact-out accepted as a complete winner

One reasoning note uses the scenario:

$$
\sum_{\ell \in Legs(A)} out(\ell) \le Q
$$

instead of the stronger exact-out requirement

$$
\sum_{\ell \in Legs(A)} out(\ell) = Q.
$$

The disaster set is:

$$
D_{\text{partial-exact-out}}
:=
\left\{
q \mid winner(A,q)
\wedge
\sum_{\ell \in Legs(A)} out(\ell) < Q
\right\}.
$$

Under the stronger shape, full allocation becomes part of admissibility and certificate meaning, not an after-the-fact sanity check.

### 2. Filled below minimum output

The disaster formula is simply:

$$
filled \wedge output < min\_out.
$$

Under `CBCValidity`, this is not merely rejected late. It stops being a valid filled outcome object.

### 3. Reserve drain

The disaster form is:

$$
amount\_out = reserve\_out
$$

or more generally any swap witness that exhausts output reserve or exits the proved CPMM envelope. The older boundary guards already blocked much of this family. The stronger shape keeps that boundary explicit so higher layers cannot silently assume soundness.

### 4. Silent fee leakage

The dangerous world is:

$$
\text{exact conservation claimed}
\wedge
\text{dust discarded}.
$$

If exactness is the claim, then dust has to become first-class state or first-class accounting residue.

### 5. Oracle mismatch execution

The disaster formula is:

$$
risky \wedge (price\_pending \ne price).
$$

This is exactly the kind of state the strengthened oracle clauses try to remove from `Reach(M)`.

### 6. Cross-layer drift

The disaster formula is:

$$
winner_{\text{runtime}} \ne winner_{\text{certificate}}
$$

or more generally

$$
obs_{\text{runtime}} \ne obs_{\text{replay}}.
$$

This is a dangerous class because every local component can look sensible while the composed system stops being replayable.

### 7. Deadlock after phase closure

The sealed-bid disaster catalog adds another important lesson. Not every disaster is theft or insolvency. Some are terminal coordination failures:

$$
D_{\text{deadlock}}
:=
\{ q \mid phase\_closed(q) \wedge \neg Complete(q) \wedge Enabled(q)=\varnothing \}.
$$

Named examples include the empty-auction deadlock and no-reveal deadlock. This is why good assurance work talks about disaster states, not only arithmetic invariant violations.

## Part VI: an interactive state-space lab

<div class="fp-callout fp-callout-try">
  <p class="fp-callout-title">Hands-on exploration</p>
  <p>
    The lab below is the best way to build intuition for how clause sets control reachability.
    Start with the <strong>Baseline old shape</strong> preset and notice which scenarios remain
    reachable (red) or fragile (amber). Then switch to <strong>Shape++ target</strong> and watch
    the disaster count drop. Finally, try the <strong>Minimal shell</strong> preset to see how
    fast bad worlds appear when most guards are removed.
  </p>
</div>

The explorer below treats the old shape and the stronger shape as clause sets. Toggle individual clauses, select a scenario, and inspect which disaster states remain reachable, which are pruned, and which chaos probes fail closed under the active assumptions.

<figure class="fp-figure">
  <p class="fp-figure-title">Interactive: ZenoDEX shape pruning lab</p>
  <iframe
    src="{{ '/zenodex_shape_pruning_lab.html' | relative_url }}"
    title="Interactive ZenoDEX shape pruning lab"
    data-fp-resize="true"
    data-fp-min-height="1180"
    style="width: 100%; min-height: 1180px; border: 0; border-radius: 16px; background: transparent;"
    loading="lazy"></iframe>
  <figcaption class="fp-figure-caption">
    Switch between the baseline and the strengthened shape, then inspect which bad states are still reachable. The reasoning panel shows the exact clause that blocks, or fails to block, the selected scenario.
  </figcaption>
</figure>

## Part VII: how automated reasoning enters the picture

The point of formal reasoning here is not magic, and it is not about replacing human judgment. It is about structured elimination: given a set of facts and a set of shape clauses, derive mechanically whether a disaster state is reachable or blocked.

For a selected scenario, the automation pattern is usually:

1. parse a packet of facts,
2. match those facts against guards, invariants, and certificate requirements,
3. derive either admissibility or rejection,
4. conclude whether the corresponding disaster state is reachable.

For example, with invalid fills:

$$
facts := \{ filled,\; output=93,\; min\_out=100 \}
$$

$$
\text{CBCValidity} := filled(output,pf : output \ge min\_out)
$$

No witness $pf$ exists, so the filled state is ill-formed. The result is not "accepted then scored badly." The result is "rejected before it counts as a valid filled outcome."

That is what "reasoning automation" means in this tutorial. It means pushing more of the acceptance decision into machine-checkable symbolic structure.

## Part VIII: chaos engineering as perturbed state-space search

<figure class="fp-figure">
  <p class="fp-figure-title">Fault-injection branching: reject-or-recover versus disaster</p>
  {% include diagrams/shape-chaos-fault-transition.svg %}
  <figcaption class="fp-figure-caption">
    When a fault is injected, a well-guarded shape redirects the transition into reject or recover. Without those guards, the perturbed path reaches a disaster state.
  </figcaption>
</figure>

The chaos toolkit in the ZenoDEX repo is helpful because it makes the shell-boundary story explicit. Its experiments are hypothesis-driven, falsifiable, and aimed at imperative boundaries such as:

- subprocess execution,
- verifier timeouts,
- truncated TCP replies,
- malformed or oversized HTTP bodies.

The chaos-engineering version of the transition system is:

$$
\to_{\text{fault}}
:=
\to_{\text{nominal}}
\;\vee\;
\to_{\text{perturbation}}.
$$

The relevant question is no longer only

$$
\operatorname{Reach}(M) \cap D = \varnothing.
$$

It becomes:

$$
\operatorname{Reach}(M_{\text{fault}}) \cap D = \varnothing
$$

or, when full elimination is too strong,

$$
\text{Fault} \to (\text{Reject} \vee \text{Recover})
$$

instead of

$$
\text{Fault} \to \text{ProceedWithGuess}.
$$

The chaos toolkit's refutation criteria make this concrete. A resilience claim is falsified if a boundary:

- accepts partial or malformed data,
- hangs,
- raises the wrong class of error,
- triggers a retry storm,
- leaks resources.

That is the same shape story, just under adversarial perturbation. A good fail-closed boundary redirects fault transitions into reject or recover states, not into silent corruption.

## Part IX: why a few formulas can summarize a huge codebase

One of the deepest engineering advantages of shape thinking is compression. A city map is not a city, but it preserves enough structure to answer navigation questions. Shapes work the same way: a small set of formulas preserves enough of the codebase's behavior to answer safety questions, without requiring anyone to read every line of implementation.

A large concrete codebase can often be abstracted by a map

$$
\alpha : Q_{\text{concrete}} \to Q_{\text{shape}}
$$

such that the concrete transition relation refines the abstract one:

$$
c \to c' \;\Rightarrow\; \alpha(c) \to_{\text{shape}} \alpha(c').
$$

If that abstraction is sound for the property in question, then proving an abstract invariant can rule out whole families of concrete bad states.

For example, if

$$
\forall c \in \operatorname{Reach}(M_{\text{concrete}}).\;
\alpha(c) \notin D_{\text{shape}}
$$

and the abstraction preserves the relevant danger predicate, then the concrete implementation inherits the safety result for that predicate.

This is why a tutorial can talk about a DEX in a few pages of formulas without becoming dishonest. The formulas are not replacing the code. They are compressing the part of the code that matters for a particular proof obligation.

The old shape compressed a large system into guardedness, replayability, exact arithmetic, and compositionality.

The new shape compresses the next strengthening step:

- canonical winners,
- exact residue accounting,
- validity by construction,
- proof-carrying acceptance,
- cross-layer parity,
- explicit rejection of ambiguity.

That is shape-preserving compression, not hand-wavy simplification.

## Takeaway

The transition from the older ZenoDEX shape to `Shape++` is not a change in aesthetic preference. It is a change in what the system allows to become history.

The old shape already said:

> Guard the boundaries. Keep traces replayable. Preserve reserves. Compose lawfully. Stay solvent.

The new shape says something stricter:

> Make invalid economic states hard to represent. Make winners canonical. Explain every residue. Carry proofs at important boundaries. Reject drift or ambiguity instead of proceeding.

That difference is the difference between "nothing obviously broke" and "here is the evidence that nothing could break."

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">The four moves of shape strengthening</p>
  <p>Every clause in Shape++ follows one or more of the same four moves:</p>
  <ol>
    <li><strong>Make invalid states unrepresentable</strong> where possible (CBC validity, exact accounting).</li>
    <li><strong>Make ambiguous states non-canonical</strong> where representation must stay broad (unique winners, anti-fragmentation).</li>
    <li><strong>Require replayable evidence</strong> at important boundaries (proof-carrying certificates, cross-layer parity).</li>
    <li><strong>Reject on mismatch</strong> instead of guessing (oracle divergence, non-commutativity quarantine).</li>
  </ol>
</div>

Shape++ is "ideal" in the engineering sense because it pushes disaster states out of the reachable region, and it does so with formulas that can be inspected, replayed, falsified, and, in the strongest cases, proved. The interactive lab above lets you see exactly how each clause contributes to that pruning.
