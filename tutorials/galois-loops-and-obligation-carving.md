---
title: "Galois loops and obligation carving"
layout: docs
kicker: Tutorial 26
description: "Reframe CEGIS through a Galois and formal-concept-analysis lens, test the loop family on finite relations, and position the result against existing counterexample-driven learning literature."
---

<figure class="fp-figure">
  <p class="fp-figure-title">The Galois connection between candidates and obligations</p>
  {% include diagrams/galois-connection.svg %}
  <figcaption class="fp-figure-caption">
    Two dual maps &Phi; and &Psi; link the candidate space X and the obligation space Y. Larger obligation sets map to smaller candidate sets and vice versa. The defining equivalence C &sube; &Phi;(B) &hArr; B &sube; &Psi;(C) is the deepest mathematical insight behind this tutorial.
  </figcaption>
</figure>

This tutorial is a derivation tutorial.

It does not claim that the underlying mathematics is absent from the literature.

It does something narrower:

- start from the quantified view of neuro-symbolic loops,
- derive a deeper algebra under that view,
- extract an obligation-aware loop family from that algebra,
- test the finite loop laws directly,
- and then position the result against CEGIS, exact learning, and formal concept analysis.

The two views developed below are:

1. **Bidirectional Obligation Carving (BOC)**, the operational view, which makes progress on both the candidate side and the obligation side.
2. **Concept-Lattice CEGIS**, the algebraic view, which stores the same state as a closed intent and extent pair.

Finite stress testing matters here. The current evidence supports this narrower claim:

> with maximal region certification, BOC and Concept-Lattice CEGIS appear to be the same loop written in dual state coordinates.

So this page is not claiming two unrelated breakthroughs.

It is claiming one deeper loop family with two useful presentations.

## Part I: the quantified starting point

The engineering shape is:

$$
\exists x\; \forall y\; Spec(x,y).
$$

Read it as:

- there exists a candidate `x`,
- such that every relevant case `y`,
- satisfies the specification.

Tutorial 25 showed the first factoring move:

$$
\forall y\; Spec(x,y)
\iff
\neg \exists y\; \neg Spec(x,y).
$$

So the task becomes:

$$
\exists x\; \neg \exists y\; \neg Spec(x,y).
$$

This already gives ordinary CEGIS:

- propose `x`,
- search for bad `y`,
- if one is found, refine `x`,
- otherwise accept `x`.

But there is a deeper structure hidden in the two sets:

- the set of still-possible candidates,
- the set of still-unresolved obligations.

## Part II: the Galois connection

Let `X` be the candidate space and `Y` be the obligation space.

Define:

$$
\Phi(B) := \{x \in X \mid \forall b \in B,\; Spec(x,b)\}
$$

and:

$$
\Psi(C) := \{y \in Y \mid \forall x \in C,\; Spec(x,y)\}.
$$

Interpretation:

- `Φ(B)` is the set of candidates that satisfy every obligation in `B`,
- `Ψ(C)` is the set of obligations that every candidate in `C` already satisfies.

Then:

$$
C \subseteq \Phi(B)
\iff
B \subseteq \Psi(C).
$$

This is an antitone Galois connection.

It says:

- a candidate set `C` is consistent with an obligation set `B`,
- exactly when every obligation in `B` is already guaranteed by every candidate in `C`.

That single equivalence is the deepest mathematical insight behind this tutorial.

It means candidate-space reasoning and obligation-space reasoning are dual.

Two closure operators follow immediately:

$$
cl_X(C) := \Phi(\Psi(C))
$$

$$
cl_Y(B) := \Psi(\Phi(B)).
$$

These are the candidate closure and obligation closure.

In plain language:

- `cl_X(C)` adds every candidate that agrees with `C` on all obligations common to `C`,
- `cl_Y(B)` adds every obligation implied by the current basis `B`.

## Part III: why this is deeper than plain CEGIS

Plain CEGIS stores a bag of discovered counterexamples.

This deeper view says:

> the search state should really be a pair of dual sets linked by the Galois connection.

That unlocks a stronger state model for the loop.

<figure class="fp-figure">
  <p class="fp-figure-title">Plain CEGIS vs Bidirectional Obligation Carving</p>
  {% include diagrams/boc-vs-cegis.svg %}
  <figcaption class="fp-figure-caption">
    Plain CEGIS only shrinks the candidate set C. BOC makes progress on both sides: counterexample cuts shrink C, and region certificates shrink the uncovered obligation set U. The combined metric |C| + |U| strictly decreases each step.
  </figcaption>
</figure>

## Part IV: proposed loop 1, Bidirectional Obligation Carving

Maintain:

- a surviving candidate set `C_t`,
- an uncovered obligation set `U_t`,
- and let `D_t := Y \setminus U_t` be the discharged obligations.

The main invariant is:

$$
D_t \subseteq \Psi(C_t).
$$

Read it as:

> every discharged obligation is already satisfied by every surviving candidate.

There is usually also a second invariant:

$$
GoodSet \subseteq C_t
$$

where:

$$
GoodSet := \Phi(Y).
$$

That says no truly correct candidate has been accidentally deleted.

### Counterexample cut

Choose a candidate:

$$
x_t \in C_t.
$$

If the verifier finds an uncovered obligation `y_t` such that:

$$
y_t \in U_t
\land
\neg Spec(x_t,y_t),
$$

update:

$$
C_{t+1} := C_t \cap \Phi(\{y_t\})
$$

$$
U_{t+1} := U_t.
$$

This removes every candidate that also fails `y_t`.

### Region-certificate cut

If the verifier can prove a region `R_t ⊆ U_t` such that:

$$
\forall x \in C_t \; \forall y \in R_t,\; Spec(x,y),
$$

then update:

$$
C_{t+1} := C_t
$$

$$
U_{t+1} := U_t \setminus R_t.
$$

This does not remove candidates. It removes obligations already discharged for all surviving candidates.

### Why this matters

Unlike plain CEGIS, progress can occur in two directions:

- the candidate side shrinks,
- the uncovered-obligation side shrinks.

In finite spaces, if either cut is strict, then:

$$
|C_{t+1}| + |U_{t+1}| < |C_t| + |U_t|.
$$

So the loop has a genuine combined progress metric.

### Why it is different from plain CEGIS

Plain CEGIS only says:

- found another bad `y`,
- remove candidates that fail it.

BOC adds a second kind of move:

- prove a whole region of `y` values already safe for all surviving candidates,
- then remove that region from the universal burden.

That is a different loop shape.

## Part V: the algebraic view, Concept-Lattice CEGIS

The algebraic view starts from the Galois closure directly.

Maintain a **closed** obligation intent:

$$
B_t = cl_Y(B_t) = \Psi(\Phi(B_t)).
$$

Define the surviving candidates exactly as its extent:

$$
C_t := \Phi(B_t).
$$

Now run:

1. choose `x_t ∈ C_t`,
2. ask for a counterexample `y_t` with `¬Spec(x_t,y_t)`,
3. if none exists, `x_t` is good,
4. if one exists, update by closure:

$$
B_{t+1} := cl_Y(B_t \cup \{y_t\})
$$

$$
C_{t+1} := \Phi(B_{t+1}).
$$

### What finite testing changed

The first version of this tutorial treated Concept-Lattice CEGIS as a possibly stronger loop than plain CEGIS.

Finite stress testing pushed that claim downward.

The better-supported claim is:

- plain CEGIS and Concept-Lattice CEGIS seem to have the same candidate trajectory,
- the difference is in how the obligation side is represented and discharged,
- not in a stronger candidate-elimination rule.

The reason is algebraic:

$$
\Phi(cl_Y(B)) = \Phi(B).
$$

So closing the obligation set changes its representation, but not the surviving candidate extent.

That is still useful.

Plain CEGIS stores a bag of counterexamples.

Concept-Lattice CEGIS stores a closed intent/extent pair.

So the benefit is:

- obligation compression,
- explicit discharged-obligation tracking,
- and a clean dual algebra,

not a magically different elimination path.

### The underlying law

Because `B_t` is closed:

$$
B_t = \Psi(C_t)
$$

and:

$$
C_t = \Phi(B_t).
$$

So the loop walks on formal concepts, not raw test sets.

## Part VI: basis compression as a side effect

Suppose there is a finite basis `B` such that:

$$
\forall y \in Y,\;
\forall x \in X,\;
\bigl(
(\forall b \in B,\; Spec(x,b)) \rightarrow Spec(x,y)
\bigr).
$$

Then:

$$
\forall x \in X,\;
\bigl(
(\forall b \in B,\; Spec(x,b))
\leftrightarrow
(\forall y \in Y,\; Spec(x,y))
\bigr).
$$

So the whole universal side has been compressed into a finite basis.

This is one reason the Galoisized loop matters.

It is not only searching for a good `x`.

It is also searching for a small obligation basis that makes universal checking cheap.

## Part VII: finite testing and replayable evidence

The main replayable harness for this tutorial is:

- `scripts/analyze_galois_loops.py`

The pinned replay receipt for the quoted loop-law numbers on this page is:

- [`assets/data/galois_loop_reports.json`]({{ '/assets/data/galois_loop_reports.json' | relative_url }})

It records the exact `3 × 3` exhaustive run, the exact `3 × 4` exhaustive run, and the `6 × 8` random stress run with `1000` trials per density and seed `17`.

It does two kinds of testing:

1. exhaustive checks over every boolean relation on small finite universes,
2. larger random stress tests over denser universes.

The exhaustive checks are stronger than the earlier ad hoc solver probes because they do not sample a few instances. They enumerate the full finite search space.

For `|X| = 3, |Y| = 3`, the harness checked all `2^(3·3) = 512` boolean relations.

For `|X| = 3, |Y| = 4`, it checked all `2^(3·4) = 4096` boolean relations.

In both exhaustive runs, it verified:

1. the Galois equivalence

$$
C \subseteq \Phi(B) \iff B \subseteq \Psi(C),
$$

2. anti-tone laws

$$
B \subseteq B' \rightarrow \Phi(B') \subseteq \Phi(B),
$$

$$
C \subseteq C' \rightarrow \Psi(C') \subseteq \Psi(C),
$$

3. closure extensivity and idempotence,

4. BOC invariant preservation along the implemented counterexample-cut trace with maximal recomputation of `\Psi(C)`,

5. basis-compression equivalence on finite toy domains,

6. candidate-trace equality:

$$
\text{plain CEGIS} = \text{Concept-Lattice CEGIS} = \text{BOC-max},
$$

7. state equality:

$$
B_t = D_t = \Psi(C_t)
$$

whenever BOC uses maximal region certification.

The exact `3 × 3` exhaustive report was:

- average loop steps: `plain = lattice = boc = 1.408`
- average online obligation checks: `plain = 4.225`, `boc = 3.096`

The exact `3 × 4` exhaustive report was:

- average loop steps: `plain = lattice = boc = 1.630`
- average online obligation checks: `plain = 6.519`, `boc = 4.602`

Random stress tests over `1000` relations per density on `|X| = 6, |Y| = 8` also supported the same identity. With smallest-candidate selection and maximal region certification, the average results were:

- density `0.3`: `plain = lattice = boc = 2.050` steps, checks `16.400` vs `13.838`
- density `0.5`: `plain = lattice = boc = 2.578` steps, checks `20.624` vs `15.113`
- density `0.7`: `plain = lattice = boc = 2.864` steps, checks `22.912` vs `13.900`

So the tested gain was not a shorter candidate trajectory. It was a smaller live obligation burden.

These are still finite experiments. They are not literature-level theorems. But they are much stronger than the first draft of this page, and they killed the incorrect claim that the lattice variant had a strictly stronger candidate-elimination path.

## Part VIII: literature position

The closest literature found in the current search breaks into three strands.

### A. Classical counterexample-driven synthesis

On the synthesis side, ordinary CEGIS is already standard. A representative source is:

- Raghothaman, Udupa, and others, *Counterexample Guided Inductive Synthesis Modulo Theories* (2018)

That line of work already has the familiar shape:

- propose a candidate,
- search for a counterexample,
- refine with the result.

So this tutorial is not claiming to invent counterexample-guided synthesis.

### B. Exact learning and query learning

On the learning side, the counterexample pattern is older still. A representative source is:

- Angluin, *Queries and Concept Learning* (1988)

That literature already treats learning as an interaction in which a hypothesis is challenged by queries and counterexamples. So the counterexample loop itself is not new either.

### C. Formal concept analysis and attribute exploration

The closest structural ancestor of the obligation-side closure view appears to be formal concept analysis, especially:

- Ganter, *Attribute exploration* (2016 overview)
- Ganter, *Attribute Exploration with Background Implications and Exceptions* (1996)
- Borchmann et al., *A General Form of Attribute Exploration* (2013)

That literature already has:

- a Galois connection between objects and attributes,
- closure operators,
- implication bases,
- and an interactive process in which an expert supplies counterexamples.

This is much closer to the obligation side of the present tutorial than the mainstream CEGIS papers are.

### What the current search did and did not find

The current bounded search did **not** find a primary source that explicitly states all of the following together:

1. recast CEGIS state as the FCA-style polarity

$$
\Phi(B), \Psi(C),
$$

2. identify maximal obligation discharge with the closed intent

$$
B_t = D_t = \Psi(C_t),
$$

3. and state that plain CEGIS, closed-intent CEGIS, and maximal-carving BOC have the same candidate trajectory while differing in obligation representation and online obligation cost.

That absence is not proof of novelty.

So the safe claim is narrower:

> the Galois machinery is classical, the counterexample loop is classical, attribute exploration is the closest obligation-side ancestor found so far, and the explicit unification of these pieces into one CEGIS-facing state geometry appears at least nonstandard in the sources checked here.

## Part IX: counterexample scheduling is where leverage reappears

The first version of this tutorial put too much weight on state representation alone.

The deeper result from the next discovery cycle was different:

> once the loop state is expressed through `C_t` and `Ψ(C_t)`, the verifier's choice of counterexample becomes a real control problem.

Fix:

- the proposer policy to `x_t = min(C_t)`,
- maximal obligation discharge `D_t = Ψ(C_t)`,
- and let the verifier choose among currently failing uncovered obligations.

Then the verifier is no longer just returning an arbitrary bad witness.

It is choosing a move in a finite game.

### Four verifier schedulers

The bounded cycle compared four verifier policies.

1. `smallest`
   - choose the smallest failing obligation
2. `cut`
   - minimize the next candidate count `|C_{t+1}|`
3. `closure`
   - maximize closure gain

$$
\Delta_\Psi(y \mid C_t)
:=
\left| \Psi(C_t \cap \Phi(\{y\})) \right|
-
\left| \Psi(C_t) \right|
$$

   - then break ties toward smaller `|C_{t+1}|`
4. `live`
   - minimize the next live burden

$$
L(C) := |C| + |Y \setminus \Psi(C)|
$$

   - and choose `y` minimizing `L(C_t \cap \Phi(\{y\}))`

### Exact bounded optimum

Because the bounded domains are finite, there is also an exact dynamic-programming optimum under the fixed proposer used in the implementation:

$$
x_t = \min(C_t).
$$

The report computes two optima on top of that fixed proposer:

- step-optimality, minimizing `(steps, checks)` lexicographically,
- check-optimality, minimizing `(checks, steps)` lexicographically.

For the state recursion itself, the check-cost view is:

$$
Cost(C)
:=
\left|Y \setminus \Psi(C)\right|
+
\min_{y \in Fail(C)}
Cost\!\left(C \cap \Phi(\{y\})\right)
$$

with base case

$$
Fail(C) = \varnothing.
$$

The step-optimal recursion is the same state equation with the lexicographic priority reversed.

That means the heuristics can be compared against true finite step-optimal and check-optimal baselines, not only against each other.

### What survived with the fixed proposer

The strongest result from that cycle was:

- on every `3 × 3` relation, `closure` and `live` both matched the exact step-optimal and check-optimal verifier policies under the fixed proposer
- on every `3 × 4` relation, the same held
- on `4 × 4`, `closure` and `live` remained tied on averages and optimal-hit counts, but neither stayed exact on every relation

The replayable evidence bundle is:

- `experiments/math_object_innovation_v01/`

and the main driver is:

- `experiments/math_object_innovation_v01/run_cycle.py`

The exact exhaustive results were:

- `3 × 3`, `512` relations:
  - `closure = live`: optimal on `512 / 512` for steps and `512 / 512` for checks
  - `smallest`: optimal on `434 / 512` for steps and `412 / 512` for checks
- `3 × 4`, `4096` relations:
  - `closure = live`: optimal on `4096 / 4096` for steps and `4096 / 4096` for checks
  - `smallest`: optimal on `3114 / 4096` for steps and `2865 / 4096` for checks
- `4 × 4`, `65536` relations:
  - `closure = live`: optimal on `64731 / 65536` for steps and `65146 / 65536` for checks
  - `smallest`: optimal on `49482 / 65536` for steps and `42819 / 65536` for checks

In the random holdout runs on `5 × 5` and `6 × 6`, `closure` and `live` continued to beat `smallest` by a wide margin on average.

### Why this matters

This is the first place where the Galoisized view produced a genuine algorithmic advantage.

The representation result alone said:

- same candidate trajectory,
- better obligation bookkeeping.

The scheduler result says:

- the obligation geometry can guide verifier moves,
- and those guided moves are often much closer to bounded optimum than arbitrary counterexample selection.

### Boundary case

The exactness does break.

A smallest `4 × 4` failure example is relation mask `6120`, with table:

$$
\begin{bmatrix}
0 & 0 & 0 & 1 \\
0 & 1 & 1 & 1 \\
1 & 1 & 1 & 0 \\
1 & 0 & 0 & 0
\end{bmatrix}
$$

There, `closure` takes `3` steps while the bounded optimum takes `2`.

That failure matters.

It shows that locally maximizing closure gain is not always globally optimal.

So the new frontier is not “the loop is solved.”

It is:

> closure gain and live-burden scheduling appear to be the current tied frontier among the tested simple local verifier policies, but the remaining gap suggests a richer scheduling law.

### The deeper correction, proposer and verifier are coupled

The next bounded cycle checked that richer law.

Instead of fixing the proposer to:

$$
x_t = \min(C_t),
$$

let the proposer also use the same closure geometry:

$$
x_t
:=
\arg\max_{x \in C_t}
\left|\Psi(\{x\})\right|.
$$

In words:

- choose the surviving candidate that individually satisfies the most obligations,
- then let the verifier choose the failing obligation with maximum closure gain.

That coupled policy produced a much stronger bounded result, under a narrower scope.

In the code and report, the proposer is held fixed to the singleton-closure chooser above, and the dynamic program optimizes only relative to that proposer.

On the full `4 × 4` universe of `65536` boolean relations, the coupled policy matched that fixed-proposer bounded optimum on every relation checked exhaustively:

- optimal steps hits: `65536 / 65536`
- optimal checks hits: `65536 / 65536`

The average cost on that full `4 × 4` universe was:

- `avg steps = 1.3632`
- `avg checks = 5.0490`

This is a stronger statement than “the heuristic looks good,” but it is still conditional on that proposer scope.

The important point is not only that the verifier got stronger.

It is that the proposer and verifier became a single closure-guided control policy.

That is a deeper lesson than the earlier slogan:

> the existential side and the universal side should often be optimized together, not only connected sequentially.

In random `5 × 5` holdout trials, this coupled policy was still extremely strong, though not exact on every sampled relation. So the safe claim is bounded:

> with the singleton-closure proposer held fixed, closure-guided proposer/verifier coupling is the strongest bounded policy found so far in this cycle.

### One more compression, obligation-targeted witness routing

The coupled policy can be compressed one step further.

Define the witness set for an uncovered obligation `y`:

$$
W(C,y) := \{x \in C \mid \neg Spec(x,y)\}.
$$

For every `y \in Y \setminus \Psi(C)`, this set is nonempty.

So the coupled `x,y` control policy can be rewritten as:

1. choose the target obligation `y`,
2. then choose a witness `x \in W(C,y)` that exposes it.

The key object is the route key:

$$
RouteKey(y \mid C)
:=
\min_{x \in W(C,y)}
\bigl(-|\Psi(\{x\})|,\; x\bigr)
$$

and then the target key:

$$
TargetKey(y \mid C)
:=
\bigl(
RouteKey(y \mid C),
\;
-\Delta_\Psi(y \mid C),
\;
|C \cap \Phi(\{y\})|,
\;
y
\bigr).
$$

Now the controller chooses the `y` with minimal `TargetKey(y \mid C)`, and only afterward picks the witness `x` realizing the route key.

This matters because it gives a new role split:

- the formal side chooses the obligation target,
- the existential engine only has to synthesize an exposing witness.

That is a different neuro-symbolic architecture than standard CEGIS.

It is not:

- “LLM proposes the final answer, verifier attacks it.”

It is:

- “formal controller chooses the most leverage-bearing obligation, existential engine routes the system to it.”

The bounded replay for this second compression is:

- `experiments/math_object_innovation_v02/`

In that cycle, the obligation-only controller matched the coupled `x,y` policy on:

- every exhaustive `4 × 4` relation,
- and every sampled `5 × 5` holdout case checked there.

So the strongest current compression ladder is:

1. plain CEGIS,
2. Galoisized state geometry,
3. closure-guided coupled policy,
4. obligation-targeted witness routing.

<figure class="fp-figure">
  <p class="fp-figure-title">Obligation-side policy improvement</p>
  {% include diagrams/policy-improvement-ladder.svg %}
  <figcaption class="fp-figure-caption">
    Initialize with a closure-guided controller, evaluate it exactly on the finite DAG, improve by one-step lookahead, repeat. On exhaustive 4 &times; 4, two rounds of improvement recovered the exact bounded-optimal controller.
  </figcaption>
</figure>

### One more loop, improve the controller itself

The next cycle pushed one step further.

Instead of treating the routed obligation controller as fixed, treat it as the initial policy:

$$
\pi_0.
$$

Then compute its exact bounded value function on the finite state space, and improve it by one-step lookahead:

$$
\pi_{k+1}(C)
:=
\arg\min_{y \in Y \setminus \Psi(C)}
\Bigl(
1 + steps_{\pi_k}(C_y),
\;
|Y \setminus \Psi(C)| + checks_{\pi_k}(C_y),
\;
y
\Bigr)
$$

with

$$
C_y := C \cap \Phi(\{y\}).
$$

This is ordinary policy improvement, but applied to the obligation-side controller extracted from the neuro-symbolic loop.

The bounded result was much stronger than expected.

On exhaustive `4 × 4`:

- `pi_0` was exact on checks for `45392 / 65536` relations
- `pi_1` jumped to `65512 / 65536`
- `pi_2` reached `65536 / 65536`

So two rounds of policy improvement recovered the exact bounded-optimal check policy on the full `4 × 4` universe.

On the sampled holdouts from that cycle:

- `5 × 5`: `pi_2` matched the exact optimum on all `1000` sampled relations at each tested density
- `6 × 6`: `pi_2` matched the exact optimum on all `200` sampled relations at each tested density in the packaged report

The replayable bundle for this third cycle is:

- `experiments/math_object_innovation_v03/`

This is still bounded evidence, not a general theorem.

One scope note matters here.

The exhaustive controller-comparison count is `65536` because it ranges over all boolean `4 × 4` relations.

The later controller-compression frontier uses `65535` nonterminal roots, because the all-true relation has no uncovered obligation at the root and therefore no controller choice to compress.

But it is the strongest loop object found so far:

> initialize with a geometry-guided controller, evaluate it exactly on the formal state space, improve it, repeat.

### Why this loop is actually provable on bounded domains

The key structural fact is simple:

if `y ∈ Y \setminus Ψ(C)`, then some candidate in `C` fails `y`, so

$$
C_y := C \cap \Phi(\{y\})
\subsetneq
C.
$$

So every legal transition strictly shrinks the candidate set.

That means the state graph over candidate sets is a finite directed acyclic graph, not a cyclic control problem.

Now define the per-step cost:

$$
g(C,y)
:=
\bigl(1,\; |Y \setminus \Psi(C)|\bigr).
$$

The first coordinate counts loop steps.

The second counts live uncovered obligations at that state.

Order costs lexicographically.

For any deterministic obligation controller `π`, the value recursion is:

$$
V_\pi(C)
:=
g(C,\pi(C)) + V_\pi(C_{\pi(C)})
$$

with terminal case

$$
Y \setminus \Psi(C) = \varnothing
\Rightarrow
V_\pi(C) = (0,0).
$$

The optimal value satisfies the Bellman equation:

$$
V^\*(C)
:=
\min_{y \in Y \setminus \Psi(C)}
\bigl(
g(C,y) + V^\*(C_y)
\bigr).
$$

Because the transition graph is a finite DAG, this recursion is well-founded.

#### Theorem 1, policy improvement is monotone

Define the improvement operator:

$$
I[\pi](C)
:=
\arg\min_{y \in Y \setminus \Psi(C)}
\bigl(
g(C,y) + V_\pi(C_y)
\bigr).
$$

Then for every state `C`,

$$
V_{I[\pi]}(C) \le_{\mathrm{lex}} V_\pi(C).
$$

Proof sketch:

Use induction on `|C|`.

For terminal states the claim is immediate.

For a nonterminal `C`,

$$
V_{I[\pi]}(C)
=
g(C,I[\pi](C)) + V_{I[\pi]}(C_{I[\pi](C)}).
$$

By the induction hypothesis on the strictly smaller state `C_{I[\pi](C)}`,

$$
V_{I[\pi]}(C_{I[\pi](C)})
\le_{\mathrm{lex}}
V_\pi(C_{I[\pi](C)}).
$$

So:

$$
V_{I[\pi]}(C)
\le_{\mathrm{lex}}
g(C,I[\pi](C)) + V_\pi(C_{I[\pi](C)}).
$$

But `I[π](C)` was chosen to minimize the right-hand side, hence

$$
g(C,I[\pi](C)) + V_\pi(C_{I[\pi](C)})
\le_{\mathrm{lex}}
g(C,\pi(C)) + V_\pi(C_{\pi(C)})
=
V_\pi(C).
$$

Therefore:

$$
V_{I[\pi]}(C) \le_{\mathrm{lex}} V_\pi(C).
$$

#### Theorem 2, fixed points are optimal

If

$$
I[\pi] = \pi,
$$

then

$$
V_\pi = V^\*.
$$

Proof sketch:

At a fixed point, for every state `C`,

$$
V_\pi(C)
=
\min_{y \in Y \setminus \Psi(C)}
\bigl(
g(C,y) + V_\pi(C_y)
\bigr).
$$

So `V_π` satisfies the same Bellman equation as `V*`.

On a finite DAG, that equation has a unique solution by backward induction on `|C|`.

Hence:

$$
V_\pi = V^\*.
$$

#### Corollary, finite termination

There are only finitely many deterministic controllers over the finite state graph.

Each non-fixed improvement step strictly improves the value at some state, so the same controller cannot reappear.

Therefore repeated policy improvement terminates after finitely many rounds at an optimal controller.

So the loop is not just a good heuristic under the bounded model.

It is a correct finite policy-improvement procedure on that bounded control problem.

#### Why the depth pattern appeared

Let `depth(C)` be the optimal remaining step count from `C`.

The same induction gives a useful horizon fact:

if `π_k` is already optimal on all states of depth at most `d`, then `π_{k+1}` is optimal on all states of depth at most `d+1`.

That explains the empirical pattern:

- on exhaustive `4 × 4`, `π_1` was already exact on every depth-2 state
- `π_2` then closed the depth-3 states
- and happened also to close the remaining depth-4 cases in that bounded domain

The first two bullets are explained by the proof pattern above.

The last bullet is still an empirical bonus, not yet a theorem.

### Power summary

At this point the bounded evidence is no longer a single lucky example.

It forms a ladder:

- on exhaustive `3 × 3`, closure-gain and live-burden scheduling were exact for steps and online obligation checks under the fixed min-candidate proposer
- on exhaustive `3 × 4`, the same held
- on exhaustive `4 × 4`, closure-guided proposer/verifier coupling matched the fixed-proposer bounded optimum
- on exhaustive `4 × 4`, two rounds of obligation-side policy improvement recovered the exact bounded-optimal controller
- on sampled `5 × 5` and `6 × 6`, the improved controller matched the exact optimum on every replayed holdout in the packaged report

That is enough to say something stronger than “interesting heuristic.”

Under the bounded model, the loop is:

- mathematically well-founded,
- empirically powerful across several finite universes,
- and strong enough that the next frontier is no longer raw performance.

The next frontier is controller compression.

## Part X: failure modes

The loops are only as good as their side conditions.

BOC fails if:

- region certificates are unsound,
- the universal side has no useful carveable regions,
- or the verifier cannot decide enough of the obligation geometry to make `U_t` shrink.

Concept-Lattice CEGIS fails to pay off if:

- closure is too weak,
- closure is too expensive,
- or the problem has little implication structure between obligations.

So these are not universal replacements for CEGIS.

They are candidate useful loops for domains with:

- rich closure structure,
- quotients or symmetries on the obligation side,
- or good certificate languages.

## Part XI: next frontier, compress the improved controller

Once `pi_2` existed, the obvious next question was:

> can the improved controller be compiled down into a small direct local score, or does it really need tabulated dynamic-programming value information?

That question is stronger than “find another good heuristic.”

It asks whether the bounded optimal controller has a short closed-form description.

The fourth cycle attacked that compression question on exhaustive `4 × 4` roots.

The tested formula family was:

- local lexicographic obligation scores,
- built from `10` hand-designed features,
- with both minimizing and maximizing orientations, for `20` signed features total,
- searched up to depth `3`,
- using beam search on a `2048`-root sample,
- then validated on all `65535` nonterminal `4 × 4` roots.

The strongest formulas found were:

- `("max_gain", "max_child_best_gain")`
- `("min_next_uncovered", "max_child_best_gain")`

They matched both the `pi_2` root choice and the exact optimal root choice on:

`65391 / 65535`

nonterminal roots.

That means only:

`144`

root cases remained outside that tested local compression family.

The first replayed failure was relation mask `4830`, where the local score chose obligation `2` and the improved controller chose obligation `0`.

So the strongest current frontier result is negative but useful:

> within the tested family of local lexicographic scores of depth at most `3`, no exact direct compression of the improved controller was found.

This is progress, not disappointment.

It turned the next frontier into a concrete target:

1. explain the remaining `144` exceptional roots,
2. move from root-only compression to full statewise compression,
3. test piecewise controllers, certificate-augmented controllers, or short lookahead formulas,
4. and ask whether `pi_2` is compressible by a small symbolic controller language rather than by a single flat score.

The replayable bundle for this frontier probe is:

- `experiments/math_object_innovation_v04/`

### One more step, motif-carved symbolic compression

The flat-score frontier did not end the story.

A fifth cycle inspected the `144` remaining exceptional roots directly.

The surprise was that the failure set did not fragment into many unrelated cases.

It collapsed to exactly one repeated root motif:

- two obligations with signature `(1, 3, 2, 3)`
- two obligations with signature `(2, 1, 1, 2)`

where the signature means:

`(gain, child_best_gain, child_best_cut, next_uncovered)`

The base flat rule picks the second kind because it has higher immediate `gain`.

The improved controller prefers the first kind because it has much stronger child geometry.

That yielded a tiny symbolic controller:

1. use the base rule `("max_gain", "max_child_best_gain")`
2. except on the repeated motif `[(1,3,2,3), (1,3,2,3), (2,1,1,2), (2,1,1,2)]`
3. on that motif, pick the smaller obligation with signature `(1,3,2,3)`

On exhaustive `4 × 4` nonterminal roots, that two-branch controller was exact:

`65535 / 65535`

So the bounded root-state compression frontier moved again.

The strongest current bounded result is no longer:

> no exact compression found.

It is:

> no exact compression found in the tested flat local-score family, but an exact two-branch symbolic controller was found once the loop was allowed to carve out one repeated failure motif.

The replayable bundle for this cycle is:

- `experiments/math_object_innovation_v05/`

That sharpens the next frontier one more time.

The open problem after that cycle was no longer root-state compression.

It became full statewise symbolic compression:

- can the improved controller over the whole candidate-state DAG be compiled into a small decision list, controller language, or certificate-augmented controller?

### One more compression, generic lookahead dominance

The sixth and seventh cycles pushed one step further.

First, the full bounded statewise gap was checked directly.

Across all reachable nonterminal candidate states in exhaustive `4 × 4`, the flat base controller hit:

`320783 / 320927`

and every miss again collapsed to the same repeated motif.

So the exact root-state exception was already exact on the whole reachable bounded `4 × 4` candidate-state DAG:

`320927 / 320927`

That was still a motif dictionary result.

The cleaner question was whether the motif itself could be compressed into a more general rule.

The answer was yes.

The motif exception distilled into a generic lookahead-dominance controller:

1. start with the flat base rule `("max_gain", "max_child_best_gain")`
2. switch away from the base winner when another obligation:
   - gives up exactly `1` unit of immediate `gain`
   - gains at least `2` units of `child_best_gain`
   - gains at least `1` unit of `child_best_cut`
   - and increases `next_uncovered` by `1`

Under the bounded `4 × 4` model, that generic controller was exact on:

- exhaustive roots: `65535 / 65535`
- exhaustive reachable nonterminal states: `320927 / 320927`

It also improved the flat base controller on larger sampled roots:

- sampled `5 × 5` roots:
  - `0.3` density: `998 -> 999`
  - `0.5` density: `983 -> 996`
  - `0.7` density: `992 -> 999`
- sampled `6 × 6` roots:
  - `0.3` density: `300 -> 300`
  - `0.5` density: `289 -> 298`
  - `0.7` density: `292 -> 296`

So the stronger survivor is no longer just:

> exact motif-carved controller on bounded `4 × 4`

It is:

> exact bounded lookahead-dominance controller on exhaustive `4 × 4`, with measured lift on sampled `5 × 5` and `6 × 6`.

The replayable bundle for this stronger controller is:

- `experiments/math_object_innovation_v07/`

That moves the frontier again.

The next open questions are now:

1. can the lookahead-dominance rule be derived directly from the Bellman proof rather than mined from failures?
2. does a small family of such dominance clauses stay exact or near-exact for larger `n`?
3. can the same controller be lifted from sampled roots to sampled deeper states for `5 × 5` and `6 × 6`?

### One more step, exact clause family search

The next cycle checked whether the mined lookahead-dominance rule was a one-off curiosity or part of a real nearby controller family.

The searched family kept the same Bellman-shaped form:

- exact `gain` loss of `1`
- `next_uncovered` delta of `1`
- small thresholds on `child_best_gain` and `child_best_cut`

Within that bounded family, there were:

`4`

clauses that stayed exact on exhaustive reachable `4 × 4` states.

The best exact clause on larger sampled roots was:

- `gain_loss = 1`
- `child_gain_min = 2`
- `child_cut_min = 0`
- `next_delta = 1`
- `next_mode = eq` (and the `ge` variant tied it on the sampled buckets checked there)

So the strongest exact bounded clause no longer needs the extra `child_best_cut >= +1` requirement.

Its sampled larger-root performance was:

- `5 × 5`: `2998 / 3000`
- `6 × 6`: `895 / 900`

That matters because it shows the controller is not just one brittle mined rule.

It belongs to a small exact bounded clause family, and some members of that family generalize better than others.

The replayable bundle for this search is:

- `experiments/math_object_innovation_v08/`

So the frontier moves again.

The next question is now not “is there any exact symbolic rule at all?”

It is:

> what is the smallest dominance-clause language that stays exact on the bounded universe while maximizing generalization to larger sampled domains?

### One more step, two-clause dominance language

The next cycle pushed from single clauses to the first genuinely richer controller language.

Keep the best exact single-clause `4 × 4` core:

- `gain_loss = 1`
- `child_gain_min = 2`
- `child_cut_min = 0`
- `next_delta = 1`
- `next_mode = eq`

Then add one deeper-lookahead repair clause, but under a hard safety rule:

> reject any repair that changes even one exhaustive reachable `4 × 4` state.

The targeted repair family was:

- `gain_loss = 2`
- `child_gain_min = 3`
- `child_cut_min ∈ {0,1,2}`
- `next_delta = 2`
- `next_mode ∈ {eq, ge}`

In that family there were:

`6`

safe repairs.

The best two-clause language was:

- core clause:
  - `gain_loss = 1`
  - `child_gain_min = 2`
  - `child_cut_min = 0`
  - `next_delta = 1`
  - `next_mode = eq`
- repair clause:
  - `gain_loss = 2`
  - `child_gain_min = 3`
  - `child_cut_min = 0`
  - `next_delta = 2`
  - `next_mode = eq`

This strictly improved the best single exact clause on larger sampled roots while preserving the full bounded `4 × 4` core:

- best single exact clause:
  - `5 × 5`: `2998 / 3000`
  - `6 × 6`: `895 / 900`
- best two-clause language:
  - `5 × 5`: `2999 / 3000`
  - `6 × 6`: `898 / 900`

That is the strongest result so far.

It is the first time a richer symbolic controller language, not just a better single clause, produced extra out-of-domain lift without weakening the verified bounded core.

The replayable bundle for this cycle is:

- `experiments/math_object_innovation_v10/`

### One more step, third-clause tie-break frontier

The next cycle asked a narrower question:

> can one more local tie-break clause close the last sampled larger-root misses while preserving the entire exact bounded two-clause core?

The searched family acted only after the `v10` choice and only inside a strict tie regime:

- same `gain`
- same `child_best_gain`
- same `next_uncovered`

Then it varied:

- `cut_gain_min ∈ {1,2}`
- `next_size_drop_min ∈ {1,2}`
- `max_child_cut_drop ∈ {0,1,2}`
- `min_child_sum_drop ∈ {0,1,2,3,4,5}`
- `min_child_best_singleton_gain ∈ {0,1}`
- `origin_guard ∈ {any, core, repair}`
- four local rank modes

This family was not vacuous.

Within it:

- `184` clauses fixed at least one of the remaining sampled larger-root residuals
- many clauses fixed all `3` sampled residuals at the holdout-root level

But the hard safety gate was still:

> preserve every exhaustive reachable nonterminal `4 × 4` state of the exact bounded two-clause core

And under that gate the answer was:

`0`

No single third tie-break clause in the tested family closed all `3` residuals while preserving the exact bounded core.

That is a useful negative result.

It means the next frontier is probably not:

> one more local threshold tweak

It is more likely:

1. a richer controller language,
2. a short repair program over clauses,
3. or a Bellman-derived residual guard that justifies when a local repair should fire.

The replayable bundle for this boundary is:

- `experiments/math_object_innovation_v11/`

### One more step, repair-program CEGIS

The next cycle changed the object being synthesized.

Instead of searching for one more local clause, it searched for a short **repair program** over the tie-break clause language.

The loop was:

1. start from the exact bounded two-clause controller
2. search ordered pairs of residual tie-break clauses
3. require them to fix the sampled larger-root residuals
4. run CEGIS over exhaustive reachable nonterminal `4 × 4` states:
   - propose the lexicographically simplest pair consistent with the current bank
   - ask the verifier for the first failing bounded state
   - add it to the bank
   - repeat

The bounded trace was:

- iteration `1`: `7104` viable pairs, first counterexample at mask `828`
- iteration `2`: `1152` viable pairs, second counterexample at mask `1915`
- iteration `3`: `576` viable pairs, safe pair found

The safe pair was:

- clause `1`:
  - `cut_gain_min = 1`
  - `next_size_drop_min = 1`
  - `max_child_cut_drop = 1`
  - `min_child_best_singleton_gain = 1`
  - `min_child_sum_drop = 0`
  - `origin_guard = any`
  - `rank = cut_bestsingleton_next`
- clause `2`:
  - `cut_gain_min = 1`
  - `next_size_drop_min = 1`
  - `max_child_cut_drop = 1`
  - `min_child_best_singleton_gain = 0`
  - `min_child_sum_drop = 4`
  - `origin_guard = any`
  - `rank = cut_bestsingleton_next`

This is an important structural change.

The existential side is no longer just proposing a controller.

It is proposing a short **patch program** over a controller language.

The verifier is no longer only a rejector.

It is teaching that patch language by growing a bank of failing bounded states.

That is a deeper neuro-symbolic loop.

But the first safe patch was not the final answer.

Its larger sampled-root performance was:

- `5 × 5`: `2945 / 3000`
- `6 × 6`: `876 / 900`

which is worse than the simpler `v10` two-clause language.

So the deeper lesson is:

> safety synthesis and out-of-domain ranking are different objectives

The next frontier is therefore not just:

> can the loop find a safe repair program?

It is:

1. can the loop find a safe repair program,
2. and can it rank safe repair programs by a larger-domain objective without weakening the exact bounded core?

The replayable bundle for this survivor is:

- `experiments/math_object_innovation_v12/`

### One more step, multiple proposers with a shared bank

The next cycle asked the scaling question directly.

Suppose there are not one but many proposers.

Does that automatically help?

In the bounded repair-program search, the proposal space was:

`7104`

residual-consistent ordered repair-program pairs.

Then several ranking rules over that same space were treated as different proposers:

- `lex`
- `singleton`
- `childsum`
- `aggressive`
- `bestsingleton_rank`

All proposers shared:

1. the same exact bounded verifier over reachable nonterminal `4 × 4` states,
2. the same counterexample bank,
3. and the same fail-closed admission rule.

The bounded outcomes were:

- best single proposer:
  - `childsum`
  - safe repair program in `2` exact verifier calls
  - bank size `1`
- every other single proposer:
  - `3` exact verifier calls
  - bank size `2`

The best two-proposer portfolio was:

- `childsum + aggressive`
- safe repair program in:
  - `3` exact verifier calls
  - `2` synchronous rounds
  - bank size `2`

So in this bounded slice, proposer multiplicity did **not** beat the best proposer on exact verifier calls.

That is important.

It means the scaling law is not:

> more proposers, therefore more leverage

It is closer to:

> more proposer diversity, under a shared falsification bank, can help, but only if that diversity improves verifier-efficient ranking

One more useful detail:

the best single proposer and the best portfolio both converged to the same safe repair program, and both had the same larger sampled-root score:

- `5 × 5`: `2945 / 3000`
- `6 × 6`: `876 / 900`

So the shared bank really is useful, but the bounded evidence says:

1. centralized refutation matters,
2. shared memory matters,
3. raw proposer count alone is not the main leverage term.

The replayable bundle for this frontier is:

- `experiments/math_object_innovation_v13/`

### One more step, bank then rank

The next cycle asked whether safety and value can be separated once the bounded counterexample bank is informative enough.

Start from the `v12` bank:

- mask `828`, candidates `(0,1,2,3)`, target `0`
- mask `1915`, candidates `(0,1,2)`, target `2`

Then:

1. keep only repair-program pairs consistent with:
   - the sampled larger-root residuals
   - and those two banked bounded counterexamples
2. rank that viable frontier by larger sampled-root score
3. certify in rank order against the exhaustive reachable nonterminal `4 × 4` verifier

The viable frontier size was:

`576`

And the strongest result was:

> the first ranked viable pair was already safe

That pair was:

- clause `1`:
  - `cut_gain_min = 1`
  - `next_size_drop_min = 1`
  - `max_child_cut_drop = 2`
  - `min_child_sum_drop = 2`
  - `min_child_best_singleton_gain = 1`
  - `origin_guard = core`
  - `rank = cut_next_childsum`
- clause `2`:
  - `cut_gain_min = 1`
  - `next_size_drop_min = 1`
  - `max_child_cut_drop = 1`
  - `min_child_sum_drop = 4`
  - `min_child_best_singleton_gain = 0`
  - `origin_guard = any`
  - `rank = cut_next_childsum`

Its larger sampled-root score was:

- `5 × 5`: `2945 / 3000`
- `6 × 6`: `876 / 900`

That did not beat the best safe repair score already known.

But it revealed something more important:

> once the bank is informative enough, the loop can factor into bank learning, value ranking, and one final exact safety check

That is the cleanest staged neuro-symbolic loop discovered so far in this program.

It also sharpens the next frontier.

The problem is probably no longer:

> how to rank viable repair programs

It is more likely:

1. how to build a better bank,
2. how to specialize proposers by obligation fiber before the bank is complete,
3. and how to port the same staged factorization into MPRD-like systems.

The replayable bundle for this survivor is:

- `experiments/math_object_innovation_v14/`

## Part XII.a: the bank collapses for the winner

The next bounded cycle asked a sharper question:

> is the `v14` bank actually needed to make the winning ranked repair program safe?

The answer in the bounded model was **no**.

The exact `v15` search used:

- the full residual-consistent repair-program frontier, `7104` pairs,
- the exhaustive reachable nonterminal `4 × 4` verifier state space, `320927` states,
- compressed into `4263` unique state patterns.

Then it asked for the smallest bounded teaching bank that would eliminate every higher-ranked unsafe pair while preserving the first safe ranked pair.

The result was:

- `first_safe_rank_without_bank = 1`
- `unsafe_prefix_size = 0`
- `minimal_bank_size = 0`

So the winning pair:

- clause `1`: `cut_gain_min = 1`, `next_size_drop_min = 1`, `max_child_cut_drop = 2`, `min_child_sum_drop = 2`, `min_child_best_singleton_gain = 1`, `origin_guard = core`, `rank = cut_next_childsum`
- clause `2`: `cut_gain_min = 1`, `next_size_drop_min = 1`, `max_child_cut_drop = 1`, `min_child_sum_drop = 4`, `min_child_best_singleton_gain = 0`, `origin_guard = any`, `rank = cut_next_childsum`

was already safe without any additional bounded bank.

That is a real correction to the previous story.

The `v14` factorization remains useful as a way to think about viable-frontier pruning, but for the top winner in this bounded model the loop compresses further:

1. build the residual-consistent frontier,
2. rank it by larger-domain score,
3. certify the top candidate.

The replayable bundle for this correction is:

- `experiments/math_object_innovation_v15/`

## Part XII.b: specialization loses its top-1 leverage

The next cycle asked whether multiple specialized proposers could still help once the `v15` result was known.

In this bounded model, they cannot help on the top-`1` exact-safe objective.

The reason is simple:

- by `v15`, the globally ranked residual-consistent frontier already returns a safe repair program at call `1`
- no proposer can do better than call `1`

So obligation-fiber proposer specialization does **not** have a remaining leverage channel on this objective.

That is still a useful result.

It means specialization, if it matters here at all, must matter somewhere else:

- top-`k` diversity,
- alternative objectives,
- or proposal shaping before the residual-consistent frontier exists.

The replayable bundle for this boundary is:

- `experiments/math_object_innovation_v16/`

## Part XII.c: the loop admits a small winner certificate

The next cycle moved from proposing and ranking controllers to certifying the winner itself.

Take the `7104` residual-consistent repair-program pairs from `v15`, and define an atomic certificate language from winner-features:

- `holdout_total = value`
- `holdout_5_hits = value`
- `holdout_6_hits = value`
- `c1.feature = value`
- `c2.feature = value`

There are `17` such winner-feature atoms in this bounded model.

The search question is:

> what is the smallest conjunction of these atoms that excludes every other residual-consistent pair?

The exact result was:

- no certificate of size `≤ 5`
- minimal certificate size `= 6`
- exactly `3` minimal certificates in the searched atom language

One representative certificate is:

- `holdout_total = 3821`
- `c1.max_child_cut_drop = 2`
- `c1.min_child_sum_drop = 2`
- `c1.origin_guard = core`
- `c1.rank = cut_next_childsum`
- `c2.rank = cut_next_childsum`

This matters because it is the first real certificate-language survivor in the loop family.

The result is still narrow:

- it certifies the winner,
- not the whole safe set.

But it shows that the loop can terminate not only in a safe repair program, but in a compact explanatory witness for why that winner is singled out inside the residual-consistent frontier.

The replayable bundle for this survivor is:

- `experiments/math_object_innovation_v17/`

## Part XII.d: safe regions are simpler than winners

The next cycle asked a sharper certificate question:

> can the loop certify not only the winner, but a whole safe region?

The answer was yes, and the result is surprisingly strong.

Inside the same `7104`-pair residual-consistent frontier used by `v17`, the exact safe subset has size `288`.

Using the same `17`-atom language, the region-certificate search found:

- size-`1` safe-region certificates exist
- each has support `288`
- each has zero unsafe spillover

The three size-`1` region certificates are:

- `holdout_total = 3821`
- `holdout_5_hits = 2945`
- `holdout_6_hits = 876`

So the bounded structure is now very sharp:

- the whole safe top block is certified by one atom
- the single winner inside that block requires six atoms to isolate exactly

This matters because it reveals a two-level certificate geometry:

1. **region level**
   - safety is simple
   - one score atom captures the whole safe top block
2. **winner level**
   - selecting one repair program inside the safe region is harder
   - exact isolation needs a richer conjunction

That is a deeper result than either `v17` or `v15` alone.

It says the loop is learning a stratified object:

- first, a coarse safe region,
- then, a finer winner certificate inside that region.

The replayable bundle for this survivor is:

- `experiments/math_object_innovation_v18/`

## Part XII.e: safety collapses to one score block

The next cycle asked the strongest available bounded question:

> is the safe region merely certified by a score atom, or is it actually identical to one maximal score block?

The answer was yes.

Inside the `7104`-pair residual-consistent frontier:

- the exact safe subset has size `288`
- and:

`Safe(x) <-> holdout_total(x) = 3821`

Equivalently:

- `Safe(x) <-> holdout_5_hits(x) = 2945`
- `Safe(x) <-> holdout_6_hits(x) = 876`

So the top-score block is not only safe.

It is the entire safe set.

The next score block already flips completely:

- `holdout_total = 3796`
- support `288`
- safe count `0`

This is a deeper collapse than the earlier certificate statements.

It says that after residual consistency has already been enforced, the universal safety property has collapsed to scalar maximization inside this bounded model.

That does not mean the scalar score is trusted by itself.

The exact verifier is what established the collapse.

But once the collapse is known, the bounded safe set is described by one scalar equality.

The replayable bundle for this survivor is:

- `experiments/math_object_innovation_v19/`

## Part XII.f: below the safe block is a staircase

The next cycle looked one layer lower.

After `v19`, the strongest open question was:

> what does the unsafe remainder look like once the safe top block has collapsed to one scalar score?

The bounded answer is unexpectedly clean.

There are `10` score blocks in the residual-consistent frontier, and every one of them is pure.

- the top block is safe
- every lower block is unsafe

More than that, every lower block has a single shared **first refuter**.

Examples:

- `holdout_total = 3796`
  - block size `288`
  - every pair is first refuted by:
    - mask `13116`
    - candidates `(0,1,2,3)`
    - target `0`
- `holdout_total = 3775`
  - block size `288`
  - every pair is first refuted by:
    - mask `1915`
    - candidates `(0,1,2)`
    - target `2`
- `holdout_total = 3762`
  - block size `1872`
  - every pair is first refuted by:
    - mask `828`
    - candidates `(0,1,2,3)`
    - target `0`

So the frontier is not merely:

- one safe region,
- one unsafe remainder.

It is a **staircase**:

- one pure score block at a time,
- one dominant refuter at a time.

This is the strongest bounded structural picture in the current program.

The replayable bundle for this survivor is:

- `experiments/math_object_innovation_v20/`

## Part XII.g: the whole refuter partition has a scalar quotient

The next cycle asked the strongest version of the collapse question:

> does one scalar score coordinate carry not only safety, but the full first-refuter label?

For two coordinates, the answer was yes.

Inside the residual-consistent frontier:

- the full first-refuter label is an exact function of `holdout_total`
- and also an exact function of `holdout_5_hits`

But it is **not** an exact function of `holdout_6_hits`.

The single failure bucket is:

- `holdout_6_hits = 859`

and it mixes two different refuter classes:

- `(mask 1915, candidates (0,1,2), target 2)`
- `(mask 828, candidates (0,1,2,3), target 0)`

So the bounded frontier has an even stronger structure than the staircase alone:

- one-dimensional quotient coordinates exist for the whole refuter partition,
- but not every sampled score coordinate is expressive enough to realize that quotient.

That matters because it turns the current bounded story into a coordinate-selection problem.

The question is no longer only:

- what is the safe region,
- what is the winner,
- what is the staircase below it.

It is also:

- which scalar summaries preserve the full verifier-side partition?

The replayable bundle for this survivor is:

- `experiments/math_object_innovation_v21/`

## Part XI.h: the quotient has a small arithmetic logic

The previous section showed that the full first-refuter label is an exact function of `holdout_total`,
and also of `holdout_5_hits`. The next question is whether those scalar quotients are still just
lookups, or whether they admit a small arithmetic presentation.

In the bounded residual-consistent frontier, the answer is yes.

Let:

- `T(x) := holdout_total(x)`
- `H5(x) := holdout_5_hits(x)`

Then the four refuter labels admit exact length-`3` decision lists:

For `T`:

- `if T > 3796 then safe`
- `else if T > 3775 then fail_13116`
- `else if T mod 23 = 3 then fail_1915`
- `else fail_828`

Equivalent bounded formulas:

- `Safe(x) ↔ T(x) > 3796`
- `Fail_13116(x) ↔ 3775 < T(x) ≤ 3796`
- `Fail_1915(x) ↔ T(x) ≤ 3775 ∧ T(x) ≡ 3 (mod 23)`
- `Fail_828(x) ↔ T(x) ≤ 3775 ∧ T(x) ≢ 3 (mod 23)`

For `H5`:

- `if H5 > 2927 then safe`
- `else if H5 > 2910 then fail_13116`
- `else if H5 mod 17 = 3 then fail_1915`
- `else fail_828`

Equivalent bounded formulas:

- `Safe(x) ↔ H5(x) > 2927`
- `Fail_13116(x) ↔ 2910 < H5(x) ≤ 2927`
- `Fail_1915(x) ↔ H5(x) ≤ 2910 ∧ H5(x) ≡ 3 (mod 17)`
- `Fail_828(x) ↔ H5(x) ≤ 2910 ∧ H5(x) ≢ 3 (mod 17)`

This matters because the quotient is now doing more than compressing the frontier. It is exposing a
small logic of the refuter partition.

There is still a hard boundary:

- `holdout_6_hits` cannot support an exact scalar-only classifier
- because `859` is a mixed bucket:
  - `∃x,y. holdout_6_hits(x) = holdout_6_hits(y) = 859 ∧ Label(x) ≠ Label(y)`

So the current bounded picture is:

- two score coordinates collapse the whole verifier-side partition,
- those two collapses admit short arithmetic presentations,
- and the third score coordinate fails for a precise logical reason, not just because the classifier search was weak.

## Part XI.i: one repair bit fixes the only mixed scalar bucket

The `holdout_6_hits` side looked weaker in Part XI.h, but the failure was very local. There was only
one mixed scalar bucket:

- `holdout_6_hits = 859`

In the searched simple feature library, that bucket is repaired by exactly one feature:

- `E(x) := p1_4(x) = p2_4(x)`

Then:

- `holdout_6_hits(x) = 859 ∧ ¬E(x) -> fail_1915`
- `holdout_6_hits(x) = 859 ∧ E(x) -> fail_828`

So the pair `(holdout_6_hits, E)` is an exact quotient for the full refuter partition in this
bounded model.

This matters because the scalar failure was not a reason to abandon the quotient view. It was a
reason to add one repair bit.

That gives a stronger loop pattern:

- learn a coarse quotient,
- isolate the mixed bucket,
- search the smallest repair coordinate,
- then continue in the repaired verifier space.

## Part XI.j: the repaired quotient compiles to a tiny verifier

After the repair bit is added, the verifier side becomes very small.

Let:

- `H6(x) := holdout_6_hits(x)`
- `E(x) := p1_4(x) = p2_4(x)`

The repaired quotient has only `10` reachable states, and in the searched guard language it compiles
to a minimal exact decision list with `4` guards:

- `if H6 = 859 and E = False then fail_1915`
- `else if H6 = 865 then fail_1915`
- `else if H6 = 869 then fail_13116`
- `else if H6 > 869 then safe`
- `else fail_828`

Equivalent bounded formulas:

- `Safe(x) ↔ H6(x) > 869`
- `Fail_13116(x) ↔ H6(x) = 869`
- `Fail_1915(x) ↔ H6(x) = 865 ∨ (H6(x) = 859 ∧ ¬E(x))`
- `Fail_828(x) ↔ ¬Safe(x) ∧ ¬Fail_13116(x) ∧ ¬Fail_1915(x)`

This is the clearest current version of the verifier-compiler pattern:

- the verifier is not only rejecting proposals,
- it is being compiled into a tiny symbolic controller,
- and that controller can cheaply route or pre-filter later proposals before final exact certification.

## Part XI.k: the compiler is minimal in the bounded guard language

The repaired verifier compiler from Part XI.j is not only compact. In the searched guard language, it
is minimal.

The bounded lower-bound witness is simple:

- `safe` has only one pure branch in this quotient space:
  - `H6 > 869`
- `fail_13116` has only one pure branch:
  - `H6 = 869`
- `fail_1915` has two disconnected pure singleton branches:
  - `H6 = 859 ∧ E = False`
  - `H6 = 865`

So any exact decision list must spend:

- one labeled branch on `safe`
- one labeled branch on `fail_13116`
- two labeled branches on `fail_1915`

That already gives a lower bound of `4` labeled guards before the default `fail_828` case.

Since Part XI.j gave an exact `4`-guard compiler, the bounded result is:

- no exact decision list with `3` guards or fewer exists in this guard language
- the repaired verifier compiler is exact-minimal

This matters because the loop now yields something stronger than a successful heuristic compression.
It yields:

- an exact compiled verifier
- and a matching lower bound

That is close to the right standard for promoting a new loop pattern into its own tutorial.

## Part XI.l: transfer to MPRD is real, but not free

The next test was transfer.

I took a tiny MPRD-shaped policy family, a toy lab-followup workflow with:

- three fact flags,
- three actions,
- a finite decision-list controller family,
- a 3-state training set,
- and the remaining 5 states as holdout.

Then I quotiented controller syntax down to unique behaviors.

The bounded result was:

- `5283` unique controller behaviors in the searched family
- `164` viable behaviors after residual consistency

The important boundary is this:

- on that viable frontier, the first-refuter partition does **not** collapse to:
  - `holdout score + 1` simple behavior feature
  - `holdout score + 2` simple behavior features
  - `holdout score + 3` simple behavior features
- the first exact repair in the searched library appears only at `4` predicted-action features

So the verifier-compiler pattern does transfer, but not cheaply by default.

That is valuable, because it prevents the wrong lesson.

The right lesson is not:

> find one beautiful quotient once, then expect it everywhere.

The right lesson is:

> learn the quotient, test the mixed buckets, search the repair coordinates, and measure transfer cost in each new bounded domain.

That is exactly the kind of boundary a standalone verifier-compiler tutorial should state clearly.

## Part XI.m: the MPRD boundary still has a semantic repair basis

The MPRD transfer boundary from Part XI.l is negative, but it is not shapeless.

In the same toy lab-followup transfer case, the first exact repair does appear in a semantic feature
library. It just does not appear cheaply.

No exact semantic repair exists with:

- `1` feature
- `2` features
- `3` features

The first exact semantic repair appears at `4` mistake-indicator bits:

- `err[(0, 0, 1)]`
- `err[(0, 1, 0)]`
- `err[(0, 1, 1)]`
- `err[(1, 1, 0)]`

So the transfer story becomes:

- cheap quotient-and-repair failed
- but the first exact repair is still semantic and interpretable

That matters because it suggests a better transfer program:

- do not expect one beautiful scalar quotient everywhere
- but do expect that mixed buckets may still admit a small semantic repair basis if the feature family is shaped to the domain

## Part XI.n: the MPRD case still compiles, but by earliest error

The MPRD transfer case does not stop at a negative boundary.

In the same toy lab-followup domain, let the ordered holdout states be:

- `h1 = (0,0,1)`
- `h2 = (0,1,0)`
- `h3 = (0,1,1)`
- `h4 = (1,1,0)`
- `h5 = (1,1,1)`

and let:

- `e_i(x) := 1` iff the controller makes an error on `h_i`
- `S(x) := holdout score`

Then the first-refuter label is exactly the earliest holdout error:

- `Safe(x) ↔ ¬e_1(x) ∧ ¬e_2(x) ∧ ¬e_3(x) ∧ ¬e_4(x) ∧ ¬e_5(x)`
- `FirstRefuter(x) = h_i ↔ ¬e_1(x) ∧ ... ∧ ¬e_{i-1}(x) ∧ e_i(x)`

Also:

- `S(x) = 5 - (e_1(x) + e_2(x) + e_3(x) + e_4(x) + e_5(x))`

So once `S` is known, any `4` of the `5` error bits determine the last one.

That gives the bounded compiler law:

- `holdout score + any 4 of the 5 ordered error bits` is exact
- every searched `holdout score + 3-bit` basis fails

So the transfer case is not:

- scalar quotient, one repair bit, tiny 4-guard compiler

It is:

- ordered error process,
- higher-dimensional repair basis,
- earliest-error compiler.

That is still a verifier-compiler loop. It is just a more expensive one.

## Part XI.o: a second MPRD-shaped domain is even more expensive

To make the transfer story harder, I tested a second bounded MPRD-shaped family, a monotone refill
gate:

- `refill` iff all four evidence flags are true
- `review` otherwise

The searched controller family used:

- positive-conjunction guards only
- decision lists with `1` to `3` guards

The bounded result was:

- `1640` unique controller behaviors
- `130` residual-consistent viable behaviors
- no exact semantic repair with `5` holdout error bits or fewer
- the first exact semantic basis in the searched library appears only at `6` holdout error bits

So the transfer picture is now sharper:

- some domains give a tiny verifier compiler
- some domains give a higher-dimensional earliest-error compiler
- some domains are even more expensive still

That does not weaken the verifier-compiler loop. It clarifies what it is:

- a search pattern for compressing verifier behavior
- whose output size is itself a domain-dependent quantity

That is why the loop should be taught with both:

- positive compiler examples
- and explicit transfer-cost boundaries

## Part XI.p: Horn closure does not remove the refill transfer cost

The monotone refill case admits another useful logic question.

Let the exact semantic basis from Part XI.o be:

- `B = {3,6,8,9,10,12}`

Let:

- `e_i(x) := 1` iff controller `x` makes a holdout error on holdout state `i`
- `Cl_B(x)` be the closure of the active basis bits under all exact single- and pair-Horn implications among the `13` holdout error bits
- `Ref(x)` be the first-refuter label
- `S(x)` be the holdout score

Then define:

- `Exact(B) := ∀x,x' ((S(x)=S(x') ∧ Cl_B(x)=Cl_B(x')) -> Ref(x)=Ref(x'))`

In the bounded refill frontier:

- `Exact(B)` holds
- `Cl_B` reaches `11` of the `13` error bits
- the only non-derivable bits are `5` and `11`
- no Horn-closed basis of size `5` or less is exact

So Horn closure helps explain the frontier, but it does not shrink it below six retained bits.

That is a useful correction.

The refill transfer cost is not just “too many features were searched.”
It persists even after exact Horn implication closure.

## Part XI.q: the refill Horn basis is irredundant

The next question is whether the six retained bits are all really needed.

Define:

- `Irredundant(B) := Exact(B) ∧ ∀b∈B. ¬Exact(B \\ {b})`

In the bounded refill frontier, this stronger law holds.

Each retained basis bit is essential. Dropping any one of them creates a mixed first-refuter bucket:

- drop `3` -> hold score `7`, labels `(0,0,1,0)` and `(0,1,0,0)`
- drop `6` -> hold score `8`, labels `(0,0,1,0)` and `(1,0,0,0)`
- drop `8` -> hold score `7`, labels `(0,0,0,0)` and `(1,0,0,0)`
- drop `9` -> hold score `10`, labels `(1,0,1,0)` and `(1,0,1,1)`
- drop `10` -> hold score `11`, labels `(1,0,1,1)` and `(1,1,0,0)`
- drop `12` -> hold score `8`, labels `(0,0,0,0)` and `(1,0,0,0)`

Now compare this with the two non-derivable bits from Part XI.p:

- `5`, corresponding to holdout state `(0,1,0,1)`
- `11`, corresponding to holdout state `(1,1,0,0)`

Those two bits are logically independent from the Horn-closed basis, but they are not required for exact first-refuter classification.

They can split already-pure buckets, but they do not improve label exactness.

So the refill frontier has a cleaner logic shape than it first appeared to have:

- six bits are essential
- two more bits are independent but classifier-unnecessary

That distinction matters for the verifier-compiler story.

It shows that transfer cost is not just about “how many bits are visible.”
It is about which bits are actually needed to preserve exact verifier labels.

## Part XI.r: the refill basis still admits an ordered compiler

The refill transfer story has one more positive result.

The six essential bits from Part XI.q do not just form an irredundant set.
They also admit an ordered active-prefix compiler law.

Fix an order `σ` on the basis `B = {3,6,8,9,10,12}`.
Let:

- `Prefix_k^σ(x)` be the first `k` active basis bits of controller `x` in order `σ`

Now ask when the truncated key

- `(S(x), Prefix_k^σ(x))`

already determines `Ref(x)`.

The bounded refill result is:

- no order is exact for `k = 3`
- some orders are exact for `k = 4`
- every order is exact for `k = 5`

So the hard refill frontier still compiles, but differently from the earlier domains.

The lab-followup case gave an earliest-error compiler.
The refill case gives an ordered essential-basis compiler.

This is a stronger transfer-side lesson:

- small verifier compilers can survive even after cheap quotient repair fails
- but the compiler object may move from:
  - scalar quotient plus one repair bit
  - to earliest semantic error
  - to truncated ordered essential basis

The current bounded formulas are:

- `¬∃σ Exact_3(σ)`
- `(∃σ) Exact_4(σ)`
- `(∀σ) Exact_5(σ)`

where:

- `Exact_k(σ) := ∀x,x' ((S(x)=S(x') ∧ Prefix_k^σ(x)=Prefix_k^σ(x')) -> Ref(x)=Ref(x'))`

## Part XI.s: the `k = 4` split also has an exact law

Part XI.r leaves one natural question open.

Why are some `k = 4` orders exact, while others are not?

In the bounded refill frontier, this split also admits a clean symbolic criterion.

Let:

- `B = {3,6,8,9,10,12}`
- `F4(σ)` be the first four positions of order `σ`

Then:

- `Exact_4(σ)` iff
  - `3 ∈ F4(σ)` and `F4(σ)` contains at least one of `{6,8}`, or
  - `3 ∉ F4(σ)`, both `6` and `8` lie in `F4(σ)`, and `3` appears before the unique omitted bit from `{9,10,12}`

This criterion matches all `720` orders exactly.

So the refill branch now has three nested compiler facts:

- `¬∃σ Exact_3(σ)`
- `(∃σ) Exact_4(σ)`
- `(∀σ) Exact_5(σ)`

and the middle one is no longer just empirical.
It has an exact order law.

## Part XII: the deepest takeaway

The deepest lesson is not just:

> LLM = existential engine. Formal tool = universal verifier.

It is:

> candidate search and universal obligation management form a dual algebra.

Once that duality is visible, stronger loops become possible.

The main survivors from this page are:

1. **Galoisized CEGIS / obligation carving**
   - cut candidates with counterexamples,
   - discharge obligations with region certificates,
   - and represent the state either operationally as `(C_t, U_t)` or algebraically as a closed intent/extent pair.

2. **Closure-gain counterexample scheduling**
   - use the obligation closure geometry to choose the verifier move,
   - compare it against bounded optimum on finite domains,
   - and treat the remaining non-optimal cases as the real next frontier.

3. **Closure-guided proposer/verifier coupling**
   - choose candidates by singleton closure strength,
   - choose counterexamples by closure gain,
   - and treat the whole loop as a coupled control policy rather than one heuristic proposer plus one checker.

4. **Obligation-targeted witness routing**
   - choose the obligation target first,
   - then synthesize a witness that exposes it,
   - and use the existential engine as a router into obligation space.

5. **Obligation-side policy iteration**
   - initialize with a geometry-guided obligation controller,
   - compute its exact bounded value function,
   - improve the controller,
   - repeat.

6. **Controller compression as the next real frontier**
   - once the improved bounded controller exists,
   - the next question is whether it can be compiled into a short symbolic score or controller language,
   - the flat-score probe showed that a simple local score comes very close but does not yet close the gap,
   - and the next bounded cycle showed that a tiny motif-carved decision list can close the root-state gap exactly.

7. **Exception-carved controller distillation**
   - start from a strong local controller,
   - collect the structured failure motifs against the improved policy,
   - and distill a small symbolic controller by adding explicit exception branches only where the bounded evidence forces them.

8. **Lookahead-dominance controller distillation**
   - compress a mined exception motif into a generic comparative rule,
   - make the controller exact on the bounded `4 × 4` universe without memorizing one special case,
   - and then test whether the same comparative rule buys lift on larger sampled domains.

9. **Exact clause-family search**
   - once one exact bounded rule exists, search its nearby symbolic neighborhood,
   - keep only clauses that remain exact on the bounded universe,
   - and rank them by generalization on larger sampled domains.

10. **Core-preserving repair languages**
   - freeze an exact bounded symbolic core,
   - search for extra clauses only under the hard constraint that they never alter the verified bounded universe,
   - and let those extra clauses compete only on larger sampled domains.

These are promising because they do not just rename a search loop.

They change:

- the state space the loop operates on, from a flat bag of tests to a dual candidate-obligation geometry,
- the control policy on the verifier side, from arbitrary counterexample return to geometry-aware scheduling,
- the proposer side too, once the same geometry is used to pick candidate witnesses,
- and finally the role split itself, once the existential side is treated as a witness router rather than only a final-answer proposer.
- and beyond that, the thing being optimized, once the loop starts improving the controller itself rather than only the current witness.

That is where new leverage usually comes from.

## References

Primary sources checked during the literature pass:

- Raghothaman et al., [*Counterexample Guided Inductive Synthesis Modulo Theories*](https://link.springer.com/chapter/10.1007/978-3-319-96145-3_15), 2018.
- Angluin, [*Queries and Concept Learning*](https://link.springer.com/article/10.1023/A:1022821128753), 1988.
- Ganter, [*Attribute exploration*](https://link.springer.com/referenceworkentry/10.1007/978-3-662-49291-8_4), 2016 overview.
- Ganter, [*Attribute Exploration with Background Implications and Exceptions*](https://link.springer.com/chapter/10.1007/978-3-642-80098-6_39), 1996.
- Borchmann et al., [*A General Form of Attribute Exploration*](https://doi.org/10.25368/2022.192), 2013.
- Distel, [*Model Exploration by Confidence with Completely Specified Counterexamples*](https://doi.org/10.25368/2022.201), 2013.
- Wang et al., [*Provenance-guided synthesis of Datalog programs*](https://doi.org/10.1145/3371130), 2019.

The testing harness used for the finite results on this page is:

- `scripts/analyze_galois_loops.py`
