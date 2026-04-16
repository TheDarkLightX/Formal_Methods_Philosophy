---
title: "Safe infinite-recursive tables in Tau Language"
layout: docs
kicker: Tutorial 39
description: "A safe table fragment for Tau: pointwise revision, fixed-point semantics, runnable demos, and the boundary between this prototype and full TABA tables."
---

TABA tables are designed as infinite updateable objects: one symbolic rule,
revised a region at a time. Most of that language is still out of reach for
execution. This tutorial walks through the fragment that is safe to run today.

"Safe" is the load-bearing word. The fragment implements pointwise revision
under a Kleene-style recurrence whose update has been proved monotone and
omega-continuous, so the supremum of its finite approximants really is a fixed
point. The fragment deliberately excludes everything that could break that
proof: same-stratum prime, current-state-dependent guards, unrestricted
recursive `common`, full NSO, and full Guarded Successor.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Scope</p>
  <p>The Tau artifact executes on a four-cell finite carrier. The Lean proof artifact establishes the same table-update shape over a complete Boolean algebra. That is why the tutorial calls the semantics infinite-recursive even though the executable Tau replay stays finite-carrier. This is not full unrestricted TABA.</p>
  <p><strong>Project boundary.</strong> This is a community research prototype. It is not an official IDNI or Tau Language table implementation, not an endorsement claim, and not a statement about what IDNI intends to ship. The design may fail standards that the official Tau team would require.</p>
</div>

## Current status

Four objects carry the evidence here. Each one stands on its own, and they do
not combine into a single claim:

- **The Tau demo** runs a feature-gated safe table surface behind
  `TAU_ENABLE_SAFE_TABLES=1`.
- **The semantic proof artifact** establishes the safe recursive update shape
  over a completed Boolean-algebra setting.
- **The finite CBF and priority-table proofs** collapse finite table syntax
  down to ordinary Boolean-function terms and explicit minterm trees with
  $2^n$ leaves.
- **The lowering proof** establishes that the safe priority-table source layer
  and pointwise revision lower into a Tau-helper IR without changing
  denotation.

The current evidence supports this formula:

$$
\operatorname{FiniteDemo}
\wedge
\operatorname{SafeRecEvidence}
\wedge
\operatorname{FiniteCBFEvidence}
\wedge
\operatorname{LoweringEvidence}
\Longrightarrow
\operatorname{RunnableSafeTableFragment}.
$$

<strong>Standard reading.</strong>
If the finite Tau demo runs, the safe-recursive proof artifact holds, the
finite CBF evidence holds, and the lowering evidence holds, then the supported
conclusion is a runnable safe table fragment.

<strong>Plain English.</strong>
Each conjunct is a separate artifact, and each one has been checked. Together
they support a runnable safe table fragment whose safe source layer has a
checked helper-IR lowering. They do not support unrestricted TABA.

## The table update

Think of a table state as a function:

$$
s : I \to \alpha.
$$

<strong>Standard reading.</strong>
The symbol $s$ is a function from table keys in $I$ to Boolean-algebra
values in $\alpha$.

<strong>Plain English.</strong>
A table assigns one Boolean region to each key.

<strong>Trap.</strong>
This is not a spreadsheet cell containing an ordinary number.
The value $s(i)$ is a Boolean-algebra element, so it can be joined, met,
split, complemented, and compared by the Boolean order.

The safe table body denotes an update function:

$$
U_T : (I \to \alpha) \to (I \to \alpha).
$$

<strong>Standard reading.</strong>
$U_T$ maps a current table state to the next table state.

<strong>Plain English.</strong>
One table-update pass computes every next entry from the current entries and
fixed lower-stratum data.

<strong>Trap.</strong>
The update may read the current recursive state only positively.
It may not use same-stratum prime or current-state-dependent guards.
Those forms can break monotonicity.

## The safe operations

The first safe operation is fixed-guard selection:

$$
\mathrm{select}_G(x) := G \wedge x.
$$

<strong>Standard reading.</strong>
$\mathrm{select}_G(x)$ is defined as the meet of the fixed guard $G$ and
the value $x$.

<strong>Plain English.</strong>
Keep the part of $x$ that lies under $G$, and remove the rest.

<strong>Trap.</strong>
This is not arbitrary selection by any predicate.
The predicate is specifically a fixed Boolean-algebra guard.
The checked boundary proof gives a counterexample for arbitrary value-predicate
selection.

The second safe operation is fixed-guard revision:

$$
\mathrm{revise}_{G,a}(x) := (G \wedge a) \vee (G' \wedge x).
$$

<strong>Standard reading.</strong>
Inside $G$, use replacement value $a$.
Inside $G'$, use the old value $x$.
Then join the two regions.

<strong>Plain English.</strong>
Overwrite the guarded region and leave everything outside the guard unchanged.

<strong>Trap.</strong>
The prime in $G'$ is the Boolean-algebra prime of the lower-stratum guard.
It is allowed here because $G$ is fixed relative to the current recurrence.
This is not permission to use $x'$ on the same recursive stratum.

The table-level implementation law is pointwise revision:

$$
\operatorname{Rev}_{G,A}(T)(i)
:=
\bigl(G(i)\wedge A(i)\bigr)
\vee
\bigl(G(i)'\wedge T(i)\bigr).
$$

<strong>Standard reading.</strong>
For every table key $i$, $\operatorname{Rev}_{G,A}(T)(i)$ is obtained by
using replacement entry $A(i)$ inside guard entry $G(i)$, and using old
entry $T(i)$ inside $G(i)'$.

<strong>Plain English.</strong>
Revise each table entry locally: replace the guarded part and preserve the rest.

<strong>Trap.</strong>
This is pointwise over keys.
It does not mean the runtime stores infinitely many concrete cells.
It means the runtime stores a finite symbolic rule whose denotation can be read
at any key.

## Visualize the update

Before the recurrence formulas get abstract, the visualizer below shows one
pointwise revision step at a time, over four sampled regions. Every row is a
sampled region; the symbolic table is the rule behind the rows.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">How to read the visualizer</p>
  <p>Click a region to select it, then step revision to apply Rev row by row. Inside the guard $G$, the entry is replaced by $A$; outside $G$, the old $T$ is preserved. Split refines the selected nonzero region into two halves. This is a teaching model for Ohad's splitter idea, not a proof of atomlessness. The proof obligation behind the split button is $0 < b < a$: every nonzero region $a$ has a proper nonzero subregion $b$.</p>
  <p><strong>Keyboard:</strong> Space steps, S splits, P plays, R resets.</p>
</div>

<div data-taba-table-visualizer></div>
<script src="{{ '/assets/js/taba-table-visualizer.js' | relative_url }}" defer></script>

The visualizer is meant to connect four ideas at once:

- A table entry is a Boolean region, not a scalar cell.
- Fixed-guard revision updates only the part selected by $G(i)$.
- Atomlessness says every live nonzero region can be split again, so there is
  no final smallest live cell.
- In the NSO picture, formulas themselves denote Boolean-algebra values, so a
  sentence can act as a guard or splitter in the semantic model.

<strong>Trap.</strong>
This is a teaching model. It does not implement full NSO, unrestricted
recurrence, or full TABA tables. It shows only the safe pointwise update shape
and the mental picture behind atomless splitting.

## The recurrence meaning

The recurrence starts from bottom and advances one update at a time:

$$
s_0 := \bot,
\qquad
s_{n+1} := U_T(s_n).
$$

<strong>Standard reading.</strong>
The zeroth approximant $s_0$ is the bottom table state, and the next
approximant $s_{n+1}$ is obtained by applying the update function $U_T$ to the
current approximant $s_n$.

<strong>Plain English.</strong>
Start with the empty table meaning. Each step applies one safe table-update
pass to the previous approximant.

For this sequence to converge to something that deserves to be called a fixed
point, two properties of $\operatorname{Rev}_{G,A}$ need to hold. The first
says the approximants stay ordered:

$$
T \le U
\Longrightarrow
\operatorname{Rev}_{G,A}(T)
\le
\operatorname{Rev}_{G,A}(U).
$$

<strong>Standard reading.</strong>
If table $T$ is pointwise below table $U$, then revising $T$ with fixed guard
$G$ and fixed replacement $A$ is pointwise below revising $U$ with the same
$G$ and $A$.

<strong>Plain English.</strong>
Pointwise revision is monotone. If $T$ is pointwise below $U$, revising $T$
lands pointwise below revising $U$.

The second says the limit passes through the update:

$$
\operatorname{Rev}_{G,A}\!\left(\bigvee_{n < \omega} T_n\right)
=
\bigvee_{n < \omega}
\operatorname{Rev}_{G,A}(T_n).
$$

<strong>Standard reading.</strong>
For an increasing omega-chain of tables $T_n$, revision of the countable join
equals the countable join of the revised tables.

<strong>Plain English.</strong>
Pointwise revision commutes with the infinite join. Revising first and then
taking the supremum gives the same table as taking the supremum first and then
revising.

Together, monotonicity and omega-continuity let the approximants close up.
The infinite-recursive meaning is the supremum:

$$
\mu U_T := \bigvee_{n < \omega} s_n.
$$

<strong>Standard reading.</strong>
The value $\mu U_T$ is defined as the countable join of all approximants
$s_n$ for natural numbers $n < \omega$.

<strong>Plain English.</strong>
The limit collects everything that appears at any finite stage: the countable
join of all approximants.

<strong>Trap.</strong>
This is where finite clopens alone are not enough in the general case.
A finite executable carrier, meaning a concrete runtime representation with
finitely many visible cells, can run examples and stabilized fragments.
The full semantic statement needs a completed Boolean-algebra reference layer,
meaning a mathematical universe where the countable join is defined.

The checked fixed-point proof artifact is:

$$
U_T(\mu U_T) = \mu U_T.
$$

<strong>Standard reading.</strong>
Applying the update to the recursively defined value $\mu U_T$ returns
$\mu U_T$ again.

<strong>Plain English.</strong>
The limit is stable under one more update.

## What Tau runs

The public reproduction path now lives in the
[TauLang-Experiments repo](https://github.com/TheDarkLightX/TauLang-Experiments).

The smooth public demo command is:

```bash
./scripts/run_public_demos.sh --accept-tau-license
```

That command runs the safe table demo and the qelim-backed policy-shape demo.
To run only the safe table syntax and solver-equivalence demo, use:

```bash
./scripts/run_table_demos.sh --accept-tau-license
```

That repo does not redistribute Tau Language. The scripts download Tau from the
official IDNI repository, check out the tested commit, apply the experiment
patch locally, regenerate Tau's parser, build Tau, and run the demos.
The default runner uses the compound equivalence check for the table-vs-raw
obligations. The older one-check-at-a-time audit path is still available with
`TABLE_DEMO_EQUIV_MODE=individual`. There is also an audit-friendly batched
path with `TABLE_DEMO_EQUIV_MODE=batched`, which keeps one solver result per
obligation while running the checks in one Tau process.

The latest smooth run used `TABLE_DEMO_EQUIV_MODE=compound`, checked the fifteen
table-vs-raw mismatch obligations as one compound query, and passed. The
compound-equivalence step took `54939.340 ms` on that local check. This timing
is descriptive, not a cross-machine performance claim.

The latest batched audit run checked the same fifteen obligations, returned
fifteen `no solution` results, reduced Tau process count from `15` to `1`, and
reduced elapsed time by about `50.990%` against the separate-process audit path.
It also exercised the opt-in command-file path behind `TAU_CLI_FILE_MODE=1`.
This is a demo-harness optimization, not a solver speedup claim.

The public demo checks:

- safe symbolic table update idempotence,
- finite four-cell carrier update behavior,
- finite-carrier pointwise revision behavior,
- Tau-native table syntax equals the raw guarded-choice expansion,
- a protocol-firewall priority table equals its raw expansion,
- priority slices prove that earlier rows win when guards overlap,
- a collateral-admission reason table returns the first failed reason,
- an incident-memory table applies state-transforming rows correctly,
- pointwise revision preserves old values outside the guard,
- pointwise revision uses replacement values inside the guard,
- pointwise revision is idempotent for the same guard and replacement,
- table syntax is rejected when `TAU_ENABLE_SAFE_TABLES` is absent.

The visible breakthroughs are:

- parser-level table syntax, not just JSON-side lowering,
- a raw-formula equivalence check, not just a successful parse,
- compound mismatch checking, where one unsatisfiable disjunction proves all
  table-vs-raw checks at once,
- priority-table behavior with overlapping guards,
- explanation-carrying table rows, not just admit-or-deny formulas,
- state-transforming rows that read the old symbolic state positively,
- pointwise revision as an explicit table-update law,
- feature-flag rejection when the syntax is not enabled,
- official-Tau download plus local patching, rather than redistribution of a
  modified Tau fork.

The standalone demo gallery is documented in
[`docs/demo-gallery.md`](https://github.com/TheDarkLightX/TauLang-Experiments/blob/main/docs/demo-gallery.md).

The compound check uses this proof obligation:

$$
\operatorname{Unsat}\!\left(\bigvee_i \operatorname{Diff}_i\right)
\Longrightarrow
\forall i,\ \operatorname{Unsat}(\operatorname{Diff}_i).
$$

<strong>Standard reading.</strong>
If the disjunction of all mismatch predicates has no satisfying assignment,
then every individual mismatch predicate has no satisfying assignment.

<strong>Plain English.</strong>
Instead of asking Tau to restart and check each table-vs-raw mismatch
separately, the demo asks one larger question: does any mismatch exist? If the
answer is no, all checked table equivalences pass.

<strong>Boundary.</strong>
This is an optimization of the demo proof obligation. It does not add a new
table operator, and it does not prove unrestricted TABA tables.

The Tau experiment uses the feature flag:

```bash
TAU_ENABLE_SAFE_TABLES=1
```

In `TauLang-Experiments`, the example file is:

```text
examples/tau/safe_table_kernel_builtins_v1.tau
```

The runtime prelude exposes these finite-carrier helpers:

```text
st_select4(x,g)
st_choice4(g,then_value,else_value)
st_revise4(old,g,replacement)
st_update4(old,base,g,replacement)
```

It also exposes symbolic `tau` helpers:

```text
st_select_tau(x,g)
st_choice_tau(g,then_value,else_value)
st_revise_tau(x,g,a)
st_update_tau(x,b,g,a)
```

The symbolic helpers are closer to the infinite-recursive semantic target than
the four-cell demo helpers. They operate over Tau's symbolic Boolean-algebra
type, not merely over the finite `ft4` carrier.

The executable update is:

$$
U(x) := \mathrm{base} \vee \mathrm{revise}_{G,a}(x).
$$

<strong>Standard reading.</strong>
The next value is the join of a fixed base value and the fixed-guard revision
of the current value.

<strong>Plain English.</strong>
Keep the required base cells, then apply the guarded overwrite.

The Tau example checks that one more update does not change the result for this
particular update shape:

$$
U(U(x)) = U(x).
$$

<strong>Standard reading.</strong>
Applying $U$ twice gives the same value as applying $U$ once.

<strong>Plain English.</strong>
This concrete update stabilizes after one Tau step.

<strong>Trap.</strong>
This one-step stabilization is a property of this example update shape.
It is not a theorem that every safe table recurrence stabilizes after one step.

Replay the finite-carrier trace from the `TauLang-Experiments` repo root:

```bash
python3 scripts/generate_safe_table_tau_artifacts.py
```

The generated proof report is:

```text
assets/data/safe_table_tau_traces.json
```

Replay the symbolic `tau` solver checks from the `TauLang-Experiments` repo
root:

```bash
python3 scripts/generate_safe_symbolic_tau_artifacts.py
```

The generated symbolic proof report is:

```text
assets/data/safe_symbolic_tau_traces.json
```

## Demo: source table compiler

The next demo starts from a small source table AST in `TauLang-Experiments`:

```text
examples/tau/safe_table_source_examples.json
```

The compiler emits two expressions:

- the raw Boolean-algebra denotation of the source table,
- the Tau-helper expression using `st_choice_tau`, `st_select_tau`, and
  `st_revise_tau`.

It then asks Tau whether the two expressions can differ.
The expected answer is `no solution`.

Replay it from the `TauLang-Experiments` repo root:

```bash
python3 scripts/generate_safe_table_compiler_artifacts.py
```

The generated proof report is:

```text
assets/data/safe_table_compiler_tau_traces.json
```

This is still useful as a compiler-smoke test, but it is no longer the main Tau
native demo. It starts from JSON, so it checks the semantic lowering shape
outside Tau's parser.

The corresponding Lean theorem is:

$$
\operatorname{evalTauTable}
\bigl(\operatorname{compileTableProgram}(P)\bigr)
=
\operatorname{evalTableProgram}(P).
$$

<strong>Standard reading.</strong>
For a safe key-indexed table program $P$, evaluating the compiled Tau-helper
program gives the same Boolean-algebra value as evaluating the source table
program.

<strong>Plain English.</strong>
The JSON compiler demo is backed by a checked denotational theorem: the helper
IR has the same meaning as the safe source table.

<strong>Trap.</strong>
This proves the semantic compiler contract for the helper IR. It is still not
a proof of Tau's C++ parser, Tau's full runtime, unrestricted recurrence, full
NSO, or Guarded Successor.

## Demo: Tau-native table syntax

The next demo uses Tau's own parser. In `TauLang-Experiments`, the
feature-gated source file is:

```text
examples/tau/full_style_taba_demo_v1.tau
```

It includes:

- a parser-level table form,
- priority rows through row order,
- CBF-style conditional values through nested guarded table choice,
- safe fixed-guard select,
- safe fixed-guard revision.

The syntax is:

```tau
table {
  when G1 => V1;
  when G2 => V2;
  else => D
}
```

The parser production is guarded by `TAU_ENABLE_SAFE_TABLES=1`.
Without that feature flag, the table syntax is rejected.
The replay also runs Tau with `--charvar false`, so a name like `riskgate` is
one variable rather than a product of character variables.

Replay it from the `TauLang-Experiments` repo root:

```bash
python3 scripts/generate_full_style_taba_demo_artifacts.py
```

The generated proof report is:

```text
assets/data/full_style_taba_demo_traces.json
```

The same check is the centerpiece of the standalone experiment repo.
Its public-facing equation is:

$$
\operatorname{priority\_quarantine\_update}
=
\operatorname{priority\_quarantine\_raw}.
$$

<strong>Standard reading.</strong>
The Tau-native `table { when ... else ... }` definition is parsed, lowered to
nested guarded choice, and checked against an explicit raw Boolean-algebra
denotation. Tau is asked whether the two denotations can differ. The expected
answer is `no solution`.

<strong>Plain English.</strong>
Tau itself now accepts the safe table syntax when the feature flag is on, and
the checked symbolic query confirms the parsed table means the same thing as
the expanded formula. The syntax is not just accepted; it is checked.

<strong>Trap.</strong>
This is a syntax-and-lowering breakthrough for safe guarded choice. The table
form is safe guarded choice only: it does not add unrestricted recurrence,
same-stratum prime, NSO, or Guarded Successor to Tau, and it is not a claim
that the official full TABA table language has been implemented.

## New proof bridge: finite minterms

The latest proof does not finish full TABA tables, but it removes one local
assumption from the Skolem/minterm side of the search.

First define guarded choice:

$$
C_g(a,b) := (g \wedge a) \vee (g' \wedge b).
$$

<strong>Standard reading.</strong>
$C_g(a,b)$ is the join of the part of $a$ under guard $g$ and the part of
$b$ under the prime of $g$.

<strong>Plain English.</strong>
Use $a$ inside $g$, and use $b$ outside $g$.

<strong>Trap.</strong>
This is a Boolean-algebra merge. It is not a procedural if-statement in a
program, and $g'$ is the Boolean prime of the guard.

For two variables $x$ and $y$, a four-coefficient minterm form is:

$$
M_{\vec a}(x,y)
:=
C_x\bigl(C_y(a_{11},a_{10}),\,C_y(a_{01},a_{00})\bigr).
$$

The same expression expands to:

$$
M_{\vec a}(x,y)
=
(a_{11}\wedge x\wedge y)
\vee(a_{10}\wedge x\wedge y')
\vee(a_{01}\wedge x'\wedge y)
\vee(a_{00}\wedge x'\wedge y').
$$

<strong>Standard reading.</strong>
The value of $M_{\vec a}(x,y)$ is the join of four guarded coefficients, one
for each truth corner of $x$ and $y$.

<strong>Plain English.</strong>
The formula splits the Boolean space into the four cases
$(x,y)=(1,1),(1,0),(0,1),(0,0)$, assigns one coefficient to each case, and
joins the four guarded pieces.

The checked compiler theorem is:

$$
\forall t\in\mathrm{Term}_2,\quad
\exists \vec a,\quad
\forall x,y,\quad
\llbracket t\rrbracket(x,y)=M_{\vec a}(x,y).
$$

<strong>Standard reading.</strong>
Every binary Boolean-polynomial term $t$ built from constants, $x$, $y$,
meet, join, and prime has a four-coefficient minterm representation with the
same denotation for every $x$ and $y$.

<strong>Plain English.</strong>
For this binary term fragment, the proof assistant can compile the expression
into a complete four-case table without changing its meaning.

The next checked step generalizes the compiler from two variables to any finite
number of variables. Instead of four coefficients, the target is a full
minterm tree:

$$
\forall n,\quad
\forall t\in\mathrm{Term}_n,\quad
\exists m,\quad
\forall \rho,\quad
\llbracket t\rrbracket(\rho)=\llbracket m\rrbracket(\rho).
$$

It also proves:

$$
\operatorname{leaves}(m)=2^n.
$$

<strong>Standard reading.</strong>
For every finite arity $n$, every Boolean-polynomial term over variables
indexed by $\mathrm{Fin}(n)$ compiles to a minterm tree with the same
denotation under every assignment $\rho$, and that tree has $2^n$ leaves.

<strong>Plain English.</strong>
The proof is no longer limited to four cases. With $n$ Boolean variables, it
builds the $2^n$-case table and proves that the table means the same thing as
the original expression.

<strong>Trap.</strong>
This is still Boolean-polynomial syntax. It does not prove full quantifier
elimination, full NSO, full recurrence, full TABA table syntax, or Tau runtime
lowering.

## New proof bridge: CBF and table collapse

The next proof checks a larger syntax layer.
It adds CBF-style conditionals and priority table rows, then proves that this
finite Boolean-valued syntax can be collapsed back into an ordinary
Boolean-function term.

The key constructor is still guarded choice:

$$
C_g(t,e) := (g \wedge t)\vee(g'\wedge e).
$$

<strong>Standard reading.</strong>
$C_g(t,e)$ is the join of $t$ met with guard $g$ and $e$ met with the
prime of $g$.

<strong>Plain English.</strong>
Inside the guard, keep the then-branch. Outside the guard, keep the
else-branch. Then join the two disjoint pieces.

<strong>Trap.</strong>
This is not an operational if-statement.
It is a Boolean-algebra identity.
The word "then" is only a reading aid for the guarded split.

For a CBF expression $c$, the compiler theorem is:

$$
\forall c\in\mathrm{CBF}_n,\quad
\forall \rho,\quad
\llbracket \operatorname{cbfToBF}(c)\rrbracket_\rho
=
\llbracket c\rrbracket_\rho.
$$

<strong>Standard reading.</strong>
For every finite-arity CBF expression $c$ and every assignment $\rho$, the
ordinary Boolean-function term produced by $\operatorname{cbfToBF}$ has the
same denotation as $c$.

<strong>Plain English.</strong>
The conditional syntax does not add a new meaning layer in this fragment.
It can be expanded into ordinary Boolean meet, join, and prime without changing
what it denotes.

For a priority table $T$, the table compiler theorem is:

$$
\forall T\in\mathrm{Table}_n,\quad
\forall \rho,\quad
\llbracket \operatorname{tableToBF}(T)\rrbracket_\rho
=
\llbracket T\rrbracket_\rho.
$$

<strong>Standard reading.</strong>
For every finite-arity priority table $T$ and every assignment $\rho$, the
Boolean-function term produced by $\operatorname{tableToBF}$ has the same
denotation as the table.

<strong>Plain English.</strong>
A finite priority table with CBF-style values can be compiled into one ordinary
Boolean formula, and the proof says the compiled formula means exactly the same
thing as the table.

<strong>Trap.</strong>
This is a finite Boolean-valued table result.
It does not yet prove first-class NSO, Guarded Successor, unrestricted
recurrence, or production Tau lowering.

The next bridge compiles the table all the way to an explicit minterm tree.
Define:

$$
m_T := \operatorname{compileTableToMinterm}(T).
$$

The semantic theorem is:

$$
\forall T\in\mathrm{Table}_n,\quad
\forall \rho,\quad
\operatorname{evalMinterm}(m_T,\rho)
=
\llbracket T\rrbracket_\rho.
$$

The size theorem is:

$$
\operatorname{leafCount}(m_T)=2^n.
$$

<strong>Standard reading.</strong>
For every finite-arity priority table $T$, the compiled minterm tree $m_T$
has the same denotation as $T$ under every assignment $\rho$, and the tree
has exactly $2^n$ leaves.

<strong>Plain English.</strong>
The finite table can be expanded into the complete case tree over its $n$
Boolean inputs. No case is missing, and no case changes meaning.

<strong>Trap.</strong>
This is an explicit finite case tree.
It is not yet recurrence, NSO, Guarded Successor, or full infinite TABA.

The same proof also marks the unsafe boundary:

$$
F(x):=x',
\qquad
\neg\bigl(\forall a\,b,\;a\le b \Rightarrow F(a)\le F(b)\bigr).
$$

<strong>Standard reading.</strong>
For the prime-step function $F(x)=x'$, it is not true that every ordered pair
$a\le b$ is sent to an ordered pair $F(a)\le F(b)$.

<strong>Plain English.</strong>
Prime reverses order.
That is why same-stratum prime cannot be placed inside the monotone
least-fixed-point lane.

<strong>Trap.</strong>
This is not merely an implementation limitation.
It is a semantic limitation of the monotone proof method.

The certified fallback rule is:

$$
\operatorname{resolve}(F,s,c)=\operatorname{fixed}(x)
\Rightarrow
F(x)=x.
$$

<strong>Standard reading.</strong>
If the resolver returns the result $\operatorname{fixed}(x)$, then $x$ is a
fixed point of $F$.

<strong>Plain English.</strong>
When the checker accepts a loop certificate as a fixed point, the reported
state really is stable under one more application of the update rule.

<strong>Trap.</strong>
This proves soundness of accepted fixed-point certificates.
It does not prove that every recurrence has a certificate, and it does not make
nonmonotone recurrence monotone.

## Demo: quarantine closure

The app-style demo is a collateral quarantine closure rule.
It is intentionally small: four toy assets, with dependency flow:

```text
asset 0 -> asset 1 -> asset 2 -> asset 3
```

The one-hop dependency operator is written $D$.
For a quarantine set $Q_n$ and a newly discovered seed set
$\mathrm{Seed}_{n+1}$, the recursive update is:

$$
Q_{n+1} := D(Q_n \vee \mathrm{Seed}_{n+1}).
$$

<strong>Standard reading.</strong>
The next quarantine set is obtained by joining the previous quarantine set with
the newly seeded risk set, then applying the dependency-propagation operator
$D$.

<strong>Plain English.</strong>
Keep everything already quarantined, add new direct risk, then quarantine every
asset reached by one dependency edge.

<strong>Trap.</strong>
This is not a static lookup table.
The meaning is recursive because the output $Q_{n+1}$ becomes the next input
$Q_n$.

The fixed-point reading is:

$$
Q_\infty := \mu Q.\,D(Q \vee \mathrm{Seed}).
$$

<strong>Standard reading.</strong>
$Q_\infty$ is the least fixed point of the function
$Q \mapsto D(Q \vee \mathrm{Seed})$.

<strong>Plain English.</strong>
It is the smallest quarantine set closed under the dependency rule.

The Tau demo uses a host loop.
The host computes a candidate next state, feeds it to Tau, and Tau checks the
claim. This is the same architecture as many production policy engines: the
host proposes, the policy checker accepts or rejects.

Replay it from the `TauLang-Experiments` repo root:

```bash
python3 scripts/generate_quarantine_closure_tau_artifacts.py
```

The generated proof report is:

```text
assets/data/quarantine_closure_tau_traces.json
```

The demo includes a bad host claim.
The expected result is that Tau rejects that step.

## Does this prove tables work?

It proves a scoped fragment, not full TABA tables.

The evidence supports this claim:

$$
\text{safe helpers} + \text{Tau transition checks} + \text{Lean semantic evidence}
\Rightarrow
\text{a runnable safe recursive table fragment}.
$$

<strong>Standard reading.</strong>
Given the safe helper definitions, the Tau transition checks, and the Lean
semantic proof artifact, the supported conclusion is that a safe recursive table
fragment is runnable.

<strong>Plain English.</strong>
The demo has enough evidence to teach and test the safe fragment.
It is not enough evidence to claim full official TABA tables are implemented.

## What has been proved

The local Lean proof artifacts establish the semantic shape behind the feature:

- v552 proves safe table expressions denote monotone omega-continuous simultaneous updates.
- v553 proves fixed-guard selection and fixed-guard revision are safe, and gives counterexamples for unsafe variants.
- v554 puts safe selection and safe revision into the table grammar itself.
- v555 proves that the safe table grammar lowers into an abstract Tau-helper
  target language without changing its denotation; the later Aristotle-audited
  lowering packet rebuilds the same source-to-helper-IR contract for safe
  priority tables and pointwise revision.
- v556 proves that binary Boolean-polynomial terms compile to four-coefficient
  minterm form without changing their denotation.
- v557 generalizes the minterm compiler to arbitrary finite arity, using a
  minterm tree with $2^n$ leaves.
- v558 proves that finite Boolean-valued CBF and priority-table syntax collapses
  to an ordinary Boolean-function kernel, and proves that same-stratum prime is
  outside the monotone Kleene lane.
- v559 proves that finite Boolean-valued CBF priority tables compile to
  explicit minterm trees with $2^n$ leaves and denotation preservation.
- `tau_compound_table_check_2026_04_15` proves the finite-list law behind the
  compound demo check: unsatisfiability of the compound mismatch predicate is
  equivalent to unsatisfiability of every listed mismatch predicate.

The research log keeps the detailed evidence ladder:

<p>
  <a class="fp-inline-link" href="{{ '/research/taba-tables-and-tau-qelim/' | relative_url }}">
    Read the detailed research log
  </a>
</p>

## What has not been proved

The current feature does not include:

- unrestricted same-stratum prime,
- current-state-dependent row guards,
- arbitrary value-predicate selection,
- unrestricted recursive common,
- full NSO syntax,
- full Guarded Successor syntax,
- full official TABA table semantics,
- a flat packed `Fin (2^n)` Skolem/minterm coefficient vector,
- production parser and runtime lowering correctness for the whole Tau feature.

## Route to full TABA

The target is clearer now. Full TABA cannot live in a single unrestricted
least-fixed-point universe. It needs a split semantic architecture, one lane
for each kind of recurrence:

$$
\operatorname{Sem}(e)=
\begin{cases}
\mu F_e, & e\in\mathcal L_{\mathrm{mono}},\\
\operatorname{resolve}(F_e,c), & e\in\mathcal L_{\mathrm{cert}},\\
\bot_{\mathrm{reject}}, & e\notin
\mathcal L_{\mathrm{mono}}\cup\mathcal L_{\mathrm{cert}}.
\end{cases}
$$

<strong>Standard reading.</strong>
An expression $e$ receives least-fixed-point semantics when it belongs to the
monotone fragment $\mathcal L_{\mathrm{mono}}$. It receives certified resolver
semantics when it belongs to the certificate fragment
$\mathcal L_{\mathrm{cert}}$. Otherwise it is rejected.

<strong>Plain English.</strong>
Safe recursive expressions use the monotone fixed-point rule.
Nonmonotone expressions need a checked certificate path.
Expressions that fit neither path do not get silently accepted.

<strong>Trap.</strong>
This is the feasibility shape, not a finished implementation of full TABA.
The proof stack still has to connect the official language to each lane.

To claim full TABA tables, these pieces still need to line up:

- official table, CBF, NSO, recurrence, and Guarded Successor syntax,
- a compiler from that syntax into a checked semantic kernel,
- a monotone lane for safe recurrence, plus a certificate lane for nonmonotone
  recurrence,
- an executable representation of the carrier or a verified lowering into Tau's
  runtime primitives,
- demos that exercise the official syntax path rather than only hand-written
  helper expressions.

The current work has checked meaningful pieces of that ladder. It has not
closed the ladder.

This boundary is not a weakness of the tutorial. It is the point. The safe
fragment earns its usefulness by making both sides of the line explicit: why
the included forms work, and why each excluded form would break the proof.
