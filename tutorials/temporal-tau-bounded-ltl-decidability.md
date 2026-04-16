---
title: "Temporal Tau, Part I"
layout: docs
kicker: Tutorial 41
description: "Learn how bounded LTL-style operators fit Tau, why finite-horizon temporal formulas are decidable on finite carriers, and how this creates a new optimizer layer without claiming full unbounded temporal reasoning."
---

This tutorial is about adding time to Tau without losing decidability.

The previous optimization tutorial focused on quantifier elimination. That was
a solver-routing problem: choose the right qelim backend only when a fragment
guard proves that the route is legal.

Temporal Tau is a different layer.
It asks how a Tau expression should be read at time $t$, time $t+1$, and
over a bounded future window. The checked result is not "all temporal logic is
solved." The checked result is narrower and more useful:

> bounded LTL-style Tau expressions are decidable over finite Boolean-algebra
> carriers.

The proof chain is:

1. `c133` adds explicit `next` and `prev` operators.
2. `c135` adds bounded `always` and bounded `eventually`.
3. `c136` adds bounded `until`.
4. `c140` proves bounded satisfiability, validity, and equivalence are
   decidable when the carrier is finite and equality is decidable.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Scope</p>
  <p>This tutorial explains a bounded temporal fragment. It does not claim unbounded LTL synthesis, infinite-time model checking, or full Tau runtime integration.</p>
</div>

<figure class="fp-figure">
  <svg viewBox="0 0 900 300" role="img" aria-labelledby="temporal-tau-title temporal-tau-desc">
    <title id="temporal-tau-title">Bounded temporal Tau horizon</title>
    <desc id="temporal-tau-desc">A temporal Tau expression is evaluated at a current time and over a finite future horizon. Next shifts one step, alwaysWithin checks every point in the window, eventuallyWithin checks at least one point, and untilWithin checks a guarded path to a goal.</desc>
    <defs>
      <marker id="temporal-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
        <path d="M0,0 L8,3 L0,6 Z" fill="#273044"></path>
      </marker>
      <style>
        .temporal-axis { stroke: #273044; stroke-width: 3; marker-end: url(#temporal-arrow); }
        .temporal-dot { fill: #f7f3ea; stroke: #273044; stroke-width: 2; }
        .temporal-now { fill: #fff7d6; stroke: #9a6b00; stroke-width: 3; }
        .temporal-window { fill: #e8f5ee; stroke: #24724a; stroke-width: 2; opacity: 0.85; }
        .temporal-text { font: 600 18px Georgia, serif; fill: #273044; }
        .temporal-small { font: 14px Georgia, serif; fill: #4d5668; }
        .temporal-rule { fill: #f7f3ea; stroke: #273044; stroke-width: 2; rx: 18; }
      </style>
    </defs>

    <line x1="90" y1="150" x2="805" y2="150" class="temporal-axis"></line>
    <rect x="250" y="108" width="360" height="84" class="temporal-window"></rect>

    <circle cx="150" cy="150" r="22" class="temporal-dot"></circle>
    <circle cx="260" cy="150" r="26" class="temporal-now"></circle>
    <circle cx="370" cy="150" r="22" class="temporal-dot"></circle>
    <circle cx="480" cy="150" r="22" class="temporal-dot"></circle>
    <circle cx="590" cy="150" r="22" class="temporal-dot"></circle>
    <circle cx="700" cy="150" r="22" class="temporal-dot"></circle>

    <text x="150" y="198" text-anchor="middle" class="temporal-small">t-1</text>
    <text x="260" y="198" text-anchor="middle" class="temporal-text">t</text>
    <text x="370" y="198" text-anchor="middle" class="temporal-small">t+1</text>
    <text x="480" y="198" text-anchor="middle" class="temporal-small">t+2</text>
    <text x="590" y="198" text-anchor="middle" class="temporal-small">t+3</text>
    <text x="700" y="198" text-anchor="middle" class="temporal-small">...</text>

    <text x="430" y="90" text-anchor="middle" class="temporal-text">finite horizon</text>
    <text x="430" y="115" text-anchor="middle" class="temporal-small">bounded formulas inspect only this window</text>

    <rect x="78" y="24" width="190" height="58" class="temporal-rule"></rect>
    <text x="173" y="50" text-anchor="middle" class="temporal-text">next e</text>
    <text x="173" y="70" text-anchor="middle" class="temporal-small">read e at t+1</text>

    <rect x="332" y="24" width="230" height="58" class="temporal-rule"></rect>
    <text x="447" y="50" text-anchor="middle" class="temporal-text">alwaysWithin N e</text>
    <text x="447" y="70" text-anchor="middle" class="temporal-small">meet every point in the window</text>

    <rect x="622" y="24" width="230" height="58" class="temporal-rule"></rect>
    <text x="737" y="50" text-anchor="middle" class="temporal-text">untilWithin N p q</text>
    <text x="737" y="70" text-anchor="middle" class="temporal-small">p holds until q appears</text>
  </svg>
  <figcaption>
    Bounded temporal Tau is finite-horizon reasoning. The formulas look forward
    only through a fixed window, which is why the decidability proof can stay
    finite.
  </figcaption>
</figure>

## Part I: The table is now time-indexed

The carrier used in the proof is a table:

$$
\operatorname{Table}(n,\alpha) := (\operatorname{Fin}(n)\to\operatorname{Bool})\to\alpha.
$$

<strong>Standard reading.</strong>
A table of arity $n$ with values in $\alpha$ is a function from Boolean
assignments over $n$ finite input positions to a Boolean-algebra value in
$\alpha$.

<strong>Plain English.</strong>
For each finite input pattern, the table returns a Boolean-algebra value.

<strong>Trap.</strong>
The word "table" does not mean a spreadsheet of numbers. The output value is a
Boolean-algebra element, so it can be met, joined, complemented, and compared
by the Boolean order.

Temporal evaluation adds a time coordinate:

$$
\operatorname{Eval}_T(e,t) : \operatorname{Table}(n,\alpha).
$$

<strong>Standard reading.</strong>
Evaluating temporal expression $e$ at time $t$ returns a table.

<strong>Plain English.</strong>
The same expression can have different table meanings at different time steps.

<strong>Trap.</strong>
The time coordinate is external to the table key. A key chooses a Boolean input
pattern; the time coordinate chooses which tick of the trace is being read.

## Part II: The one-step temporal operators

The first temporal operator is `next`:

$$
\operatorname{Eval}_T(\operatorname{next}(e),t)
=
\operatorname{Eval}_T(e,t+1).
$$

<strong>Standard reading.</strong>
Evaluating `next e` at time $t$ is the same as evaluating $e$ at time
$t+1$.

<strong>Plain English.</strong>
`next` shifts the expression one tick into the future.

The `prev` operator has a boundary condition:

$$
\operatorname{Eval}_T(\operatorname{prev}(e),0)=\bot,
\qquad
\operatorname{Eval}_T(\operatorname{prev}(e),t+1)=\operatorname{Eval}_T(e,t).
$$

<strong>Standard reading.</strong>
At time $0$, `prev e` evaluates to bottom. At successor time $t+1$, `prev e`
evaluates to what $e$ evaluated to at time $t$.

<strong>Plain English.</strong>
`prev` reads one tick backward, but there is no earlier tick before time $0$,
so the proof chooses bottom there.

<strong>Trap.</strong>
The bottom value at time $0$ is a design choice in the checked model. Another
runtime could choose an explicit error or option type, but then the proof
surface would be different.

## Part III: Bounded always and bounded eventually

Unbounded temporal logic talks about all future time. That is powerful, but it
is not the proof surface here.

The bounded always operator is:

$$
\operatorname{Eval}_T(\Box_{<N}e,t)
=
\bigwedge_{i<N}\operatorname{Eval}_T(e,t+i).
$$

<strong>Standard reading.</strong>
Evaluating bounded always for $N$ steps is the meet of the evaluations of
$e$ at times $t,t+1,\ldots,t+N-1$.

<strong>Plain English.</strong>
The property must hold at every tick in the finite window.

The bounded eventually operator is:

$$
\operatorname{Eval}_T(\Diamond_{<N}e,t)
=
\bigvee_{i<N}\operatorname{Eval}_T(e,t+i).
$$

<strong>Standard reading.</strong>
Evaluating bounded eventually for $N$ steps is the join of the evaluations of
$e$ at times $t,t+1,\ldots,t+N-1$.

<strong>Plain English.</strong>
The property must hold at least somewhere in the finite window.

<strong>Trap.</strong>
These are bounded operators. $\Box_{<N}$ is not the unbounded LTL operator
$\Box$, and $\Diamond_{<N}$ is not the unbounded LTL operator $\Diamond$.
The finite bound is what keeps the evaluator structurally recursive.

The bounded De Morgan law has the expected form:

$$
\neg\Box_{<N}e
=
\Diamond_{<N}\neg e.
$$

<strong>Standard reading.</strong>
The complement of "always $e$ within $N$ steps" equals "eventually not
$e$ within $N$ steps."

<strong>Plain English.</strong>
A finite window fails an always-check exactly when the window contains a
counterexample.

## Part IV: Bounded until

The bounded `until` operator is the most important temporal connective for
protocol specifications.

The recursive law is:

$$
p\,U_{<0}\,q := \bot,
\qquad
p\,U_{<N+1}\,q := q\vee(p\wedge\operatorname{next}(p\,U_{<N}\,q)).
$$

<strong>Standard reading.</strong>
At horizon $0$, bounded until is bottom. At horizon $N+1$, $p$ until
$q$ holds if $q$ holds now, or if $p$ holds now and the bounded-until
condition holds over the remaining $N$ future steps.

<strong>Plain English.</strong>
Either the goal has already arrived, or the guard must hold now while the same
question is passed to the next tick with one fewer step left.

<strong>Trap.</strong>
The guard $p$ does not have to hold after $q$ appears. The word "until"
means "keep $p$ true up to the first successful $q$-point," not "keep $p$
true forever."

This is the bounded version of the standard LTL idea:

$$
p\,U_{<N}\,q
\quad\text{means}\quad
\exists j<N.\ \operatorname{Eval}_T(q,t+j)\ne\bot
\ \wedge\
\forall i<j.\ \operatorname{Eval}_T(p,t+i)\ne\bot.
$$

<strong>Standard reading.</strong>
There is a future offset $j$ inside the $N$-step window where $q$ holds,
and at every earlier offset $i<j$, $p$ holds.

<strong>Plain English.</strong>
Reach $q$ before the window closes, while maintaining $p$ on the way there.

<strong>Trap.</strong>
This existential reading is a helpful semantic explanation. The Lean proof
uses the recursive definition because it gives a structurally terminating
evaluator.

## Part V: The decidability theorem

The decisive theorem in `c140` is not a new temporal law. It is a finite
decision boundary.

The assumptions are:

$$
\operatorname{Finite}(\alpha)
\quad\wedge\quad
\operatorname{DecidableEq}(\alpha)
\quad\wedge\quad
\operatorname{BooleanAlgebra}(\alpha).
$$

<strong>Standard reading.</strong>
The value carrier $\alpha$ is finite, equality on $\alpha$ is decidable,
and $\alpha$ is a Boolean algebra.

<strong>Plain English.</strong>
There are finitely many possible output values, equality can be checked, and
the values support the Boolean operations Tau needs.

Under those assumptions, pointwise equality of evaluations is decidable:

$$
\operatorname{Decidable}
\left(
  \operatorname{Eval}_T(e_1,t)=\operatorname{Eval}_T(e_2,t)
\right).
$$

<strong>Standard reading.</strong>
For two temporal Tau expressions $e_1,e_2$ at a fixed time $t$, there is a
decision procedure for whether their evaluated tables are equal.

<strong>Plain English.</strong>
At a fixed tick, the checker can decide whether two bounded temporal
expressions mean the same table.

Bounded satisfiability is decidable:

$$
\operatorname{Decidable}
\left(
  \exists t\le T.\ \exists k.\ \operatorname{Eval}_T(e,t)(k)\ne\bot
\right).
$$

<strong>Standard reading.</strong>
There is a decision procedure for whether some time $t$ up to horizon $T$
and some Boolean input assignment $k$ make $e$'s evaluation non-bottom.

<strong>Plain English.</strong>
Within the bounded horizon, the checker can decide whether the property is ever
possible.

Bounded validity is decidable:

$$
\operatorname{Decidable}
\left(
  \forall t\le T.\ \forall k.\ \operatorname{Eval}_T(e,t)(k)=\top
\right).
$$

<strong>Standard reading.</strong>
There is a decision procedure for whether every time $t$ up to horizon $T$
and every Boolean input assignment $k$ make $e$'s evaluation top.

<strong>Plain English.</strong>
Within the bounded horizon, the checker can decide whether the property always
holds.

Bounded equivalence is decidable:

$$
\operatorname{Decidable}
\left(
  \forall t\le T.\ \operatorname{Eval}_T(e_1,t)=\operatorname{Eval}_T(e_2,t)
\right).
$$

<strong>Standard reading.</strong>
There is a decision procedure for whether $e_1$ and $e_2$ evaluate to the
same table at every time up to horizon $T$.

<strong>Plain English.</strong>
Within the bounded horizon, the checker can decide whether two temporal
expressions are equivalent.

<strong>Trap.</strong>
The theorem is finite twice: the time horizon is finite, and the carrier is
finite. Removing either condition changes the problem.

## Part VI: What this gives Tau

The qelim tutorial showed one optimizer shape:

```text
recognize fragment
dispatch to exact backend
fall back outside the fragment
```

Temporal Tau gives a second optimizer shape:

```text
make time explicit
bound the horizon
evaluate structurally
decide satisfiability, validity, or equivalence over the finite surface
```

This opens several practical compiler passes:

- `next` can be pushed through Boolean operations.
- `alwaysWithin` and `eventuallyWithin` can be unfolded into finite meet and
  join chains.
- `untilWithin` can be unfolded into a finite recursive expression.
- bounded equivalence can justify temporal simplification.
- bounded satisfiability can support temporal counterexample search.

The important boundary is that these are bounded passes. They help Tau reason
about a finite trace window. They do not replace unbounded temporal synthesis,
omega-automata, or full infinite-trace LTL.

## Part VII: What to remember

Temporal Tau is not another qelim backend. It is an execution and optimization
layer for time-indexed expressions.

The core ladder is:

1. Add a time coordinate to evaluation.
2. Read `next` as a one-step future shift.
3. Read bounded `always` as a finite meet.
4. Read bounded `eventually` as a finite join.
5. Read bounded `until` as a recursive guarded search for a goal.
6. Use finiteness of the carrier and the horizon to obtain decidability.

The result is strong because it is modest. It gives a mechanically checked
finite-horizon temporal fragment, and that is exactly the kind of fragment that
can become a safe Tau optimizer layer.
