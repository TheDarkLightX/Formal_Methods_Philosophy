---
title: "Optimizing Tau Language, Part I"
layout: docs
kicker: Tutorial 40
description: "Learn why Tau qelim optimization is a fragment-dispatch problem, read the exact compiled-forgetting formulas, and see why guarded BDD and CNF-native routes can speed up scoped formulas without replacing Tau semantics."
---

This tutorial is about optimizing Tau Language without changing what Tau means.

That sounds obvious, but it is the whole difficulty.
For a logic language, a faster route is useful only when it preserves the same
formula semantics.
So the optimization question is not:

```text
Which backend is fastest?
```

The real question is:

```text
Which backend is fastest on the fragment where its meaning-preservation
condition is actually true?
```

The answer from this branch is the same lesson that kept appearing in the TABA
table work:

> qelim algorithm choice should be fragment-sensitive, because the fastest
> method depends on where the structure lives: in syntax, or in the compiled
> carrier.

The story is easiest to follow as a ladder.

1. Quantifier elimination removes a hidden variable while preserving truth over
   the visible variables.
2. Tau's default `anti_prenex` route is syntax-directed qelim, not mere cleanup.
3. BDD existential abstraction is a compiled-carrier route for a narrower exact
   fragment.
4. A guard decides whether the compiled route is legal. If the guard fails,
   fallback is part of correctness.
5. Once inside the compiled route, component splitting, pure-atom dropping, and
   CNF-native Davis-Putnam steps become separate optimization choices.
6. The measured default candidate is `TAU_QELIM_BACKEND=auto`, not a claim that
   all Tau qelim is solved.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Scope</p>
  <p>This tutorial explains the checked Tau qelim experiment for a supported leading-existential propositional fragment. The current result is a guarded optimization candidate, not a proof that every Tau formula should use the same backend.</p>
</div>

The detailed research log lives here:

```text
research/taba-tables-and-tau-qelim.md
```

That page is not just a benchmark appendix.
It shows the neuro-symbolic loop in practice: propose a route, formalize the
claim, let Lean, Tau, Aristotle, SMT, or bounded replay try to break it, then
promote only the scoped claim that survives.

There is also a shorter academic-style note:

```text
research/fragment-sensitive-qelim-and-safe-tables.md
```

That note includes a two-page PDF and gives the main equations and results
without the tutorial prose or the full research log.

## Part I: What qelim must preserve

Quantifier elimination starts with a formula that has a hidden variable and
returns an equivalent formula without that hidden variable.

One clean one-variable specification is:

$$
\operatorname{qelim}_x(\exists x.\,\varphi)=\psi
\quad\Longrightarrow\quad
\forall \rho,\;
\psi(\rho)=\top
\Longleftrightarrow
\exists b\in\{\bot,\top\}.\,
\varphi(\rho[x:=b])=\top .
$$

<strong>Standard reading.</strong>
If eliminating $x$ from $\exists x.\,\varphi$ returns $\psi$, then for
every assignment $\rho$ of the remaining variables, $\psi$ is true exactly
when there exists a Boolean value $b$ such that $\varphi$ is true after
setting $x$ to $b$.

<strong>Plain English.</strong>
The eliminated formula must answer the same yes-or-no question about the visible
variables as the original existential formula.

<strong>Trap.</strong>
Quantifier elimination is not witness extraction.
It does not have to return the value of $x$.
It must remove $x$ while preserving whether some value of $x$ makes the
formula true.

For a Boolean variable, the basic compiled-forgetting identity is:

$$
\exists x.\,f
=
f[x:=\bot]\vee f[x:=\top].
$$

<strong>Standard reading.</strong>
The existential abstraction of $x$ from $f$ is the join of the cofactor of
$f$ with $x$ forced to $\bot$ and the cofactor of $f$ with $x$ forced
to $\top$.

<strong>Plain English.</strong>
Forget $x$ by keeping both possible branches and joining them.

<strong>Trap.</strong>
The notation $f[x:=\bot]$ is substitution, not multiplication and not
function application in the calculus sense.
It means: evaluate the Boolean formula $f$ after forcing $x$ to the bottom
Boolean value.

In a BDD, this operation is existential abstraction.
The BDD is the compiled carrier.
It stores the Boolean function in a graph-shaped representation, then removes
the quantified variable by joining the two cofactors.

<strong>Trap.</strong>
In this experiment, the BDD route works after the accepted Tau fragment has
been compiled into propositional atoms.
That does not mean every Tau variable in the full language is just a two-valued
Boolean switch.
The guard decides when this propositional view is legal.

## Part II: Why Tau already has a syntax route

Tau's `anti_prenex` pass can look like a formatting step.
That reading is too weak.

The useful syntax identity is:

$$
\exists x.\,(A\wedge B)
\equiv
A\wedge \exists x.\,B
\qquad
\text{when }x\notin FV(A).
$$

<strong>Standard reading.</strong>
If $x$ is not a free variable of $A$, then existential quantification over
$x$ can move inward past $A$, leaving $A$ outside and quantifying only
$B$.

<strong>Plain English.</strong>
If one part of a conjunction does not mention the hidden variable, keep that
part outside the search.

<strong>Trap.</strong>
The side condition $x\notin FV(A)$ is not decorative.
If $A$ depends on $x$, moving the quantifier past $A$ can change the
meaning.

This is why `anti_prenex` is not merely "old code."
It tries to move quantifiers inward so Tau can solve smaller local problems.
That is a real algorithmic idea.

The qelim experiment did not prove that `anti_prenex` is bad.
It proved a narrower claim:
on one checked fragment, a compiled BDD route can be better if it runs before
the default syntax-directed path.

## Part III: The guarded compiled route

The experimental dispatcher has this shape:

$$
\operatorname{qelim}_{\mathrm{Tau}}(\varphi)=
\begin{cases}
\operatorname{abstract}_{\mathrm{BDD}}(\varphi),
& \varphi\in\mathcal{F}_{\exists\mathrm{prop}},\\
\operatorname{qelim}_{\mathrm{default}}(\varphi),
& \varphi\notin\mathcal{F}_{\exists\mathrm{prop}}.
\end{cases}
$$

<strong>Standard reading.</strong>
If $\varphi$ belongs to the supported leading-existential propositional
fragment $\mathcal{F}_{\exists\mathrm{prop}}$, Tau uses BDD existential
abstraction. Otherwise Tau uses the default qelim route.

<strong>Plain English.</strong>
Use the fast compiled route only where its compiler knows how to preserve
meaning. Fall back everywhere else.

<strong>Trap.</strong>
The fragment guard is not a performance tweak.
It is the correctness boundary.
If the guard accepts too much, the optimizer can become wrong.

The supported fragment in this experiment is intentionally narrow:

- a leading existential prefix,
- followed by a quantifier-free Boolean body,
- built from supported zero-test atoms.

The accepted shape is like:

```text
qelim ex x ex y ((x = 0) && (y = 0) && (a = 0))
```

The rejected shape is like:

```text
qelim ex x (!(ex y (y = 0)))
```

The second formula must fall back because the inner existential is nested under
negation.

## Part IV: The guard audit

The review loop found the most important correctness trap in the whole branch:

$$
\neg\exists y.\,P(y)
\equiv
\forall y.\,\neg P(y).
$$

<strong>Standard reading.</strong>
The negation of an existential statement is equivalent to a universal statement
of the negated body.

<strong>Plain English.</strong>
"There is no $y$ satisfying $P$" means "every $y$ fails $P$."

<strong>Trap.</strong>
It does not mean:

$$
\exists y.\,\neg P(y).
$$

That would say "some $y$ fails $P$," which is weaker and usually different.

The concrete failing shape was:

```text
qelim !(ex y (y = 0))
```

The inner sentence is true because $y=0$ has a witness, namely $0$.
Its negation is false.
Tau's default route returned `F`.
The old unguarded BDD experiment returned `T`.

That was not a timing issue.
It was a semantic-guard bug.

The corrected route accepts only leading existential prefixes.
Nested or non-prefix quantifiers fall back to Tau's default route.

<div class="fp-callout fp-callout-warn">
  <p class="fp-callout-title">Optimization rule</p>
  <p>A fast backend is not an optimizer until the bridge into that backend is guarded. The guard is part of the algorithm.</p>
</div>

## Part V: Structure inside the compiled route

Once the formula is inside the guarded fragment, BDD abstraction is not the only
decision.
The optimizer can still exploit structure before building one large carrier.

### Component splitting

The component law is:

$$
\exists X.\,\bigwedge_{i=1}^{k}F_i
\equiv
\bigwedge_{i=1}^{k}\exists X_i.\,F_i,
$$

when each $X_i = X\cap FV(F_i)$ and no quantified variable is shared between
different components.

<strong>Standard reading.</strong>
If the top-level conjuncts do not share quantified variables, then existential
elimination over the whole conjunction can be performed component by component.

<strong>Plain English.</strong>
Do not build one large BDD when the quantified subproblems are independent.

<strong>Trap.</strong>
The components may still share free variables.
The split is blocked by shared quantified variables, because those are the
variables being eliminated.

The checked experiment added a component mode and found a structural case where
this mattered.
On a `disjoint_or` family with ten independent quantified pieces, the monolithic
BDD root had `2046` nodes, while the component route used `20` total root nodes
across components.

That is why this is not just a micro-optimization.
It changes the size of the compiled carrier.

### Pure quantified atoms

Let:

$$
p_x := (x=0).
$$

If $p_x$ occurs only positively, the safe rewrite is:

$$
\exists x.\,\Phi(p_x,y)
\equiv
\Phi(\top,y).
$$

If $p_x$ occurs only negatively, the dual rewrite is:

$$
\exists x.\,\Phi(p_x,y)
\equiv
\Phi(\bot,y).
$$

<strong>Standard reading.</strong>
When the zero-test atom $p_x$ for an existential variable occurs in only one
polarity, choose the truth value that satisfies that polarity and remove the
quantified atom.

<strong>Plain English.</strong>
If the formula only asks for $x=0$, choose $x=0$.
If it only asks against $x=0$, choose a value that makes $x=0$ false.

<strong>Trap.</strong>
This is not a general rewrite for every expression named $x$.
It is a polarity rule for the supported zero-test atom $p_x := (x=0)$ inside
the guarded propositional fragment.

The checked lane skipped BDD construction on the pure-route cases and matched
Tau default on the regression corpus.
The timing win was modest, but the structural effect is clean:
some quantified atoms can disappear before the carrier is built.

### Davis-Putnam clause distribution

For CNF-shaped formulas, one exact elimination step is:

$$
\exists x\,
\left(
  R
  \wedge
  \bigwedge_i (x\vee A_i)
  \wedge
  \bigwedge_j (\neg x\vee B_j)
\right)
\equiv
R\wedge
\bigwedge_{i,j}(A_i\vee B_j).
$$

<strong>Standard reading.</strong>
To existentially eliminate $x$ from a CNF formula, keep the clauses $R$ that
do not mention $x$, and add every resolvent $(A_i\vee B_j)$ formed from a
positive $x$-clause and a negative $x$-clause.

<strong>Plain English.</strong>
Pair each positive occurrence of the hidden atom with each negative occurrence,
resolve the pairs, then drop the old clauses mentioning that atom.

<strong>Trap.</strong>
The product $\bigwedge_{i,j}$ is the danger.
If there are $m$ positive clauses and $n$ negative clauses, the raw step can
create $mn$ resolvents.
So this route needs an explicit cap or a minimization step before promotion.

The experiment added thresholded Davis-Putnam distribution under an explicit
cap.
Later, a subsumption-aware version counted the minimized residual instead of the
raw resolvent set.
That changed some formulas from "refuse the DP route" to "accept the DP route"
without changing the semantic target.

The teaching lesson is simple:
CNF-native routes are not worse versions of BDD routes.
They are different output languages with different blowup families.

## Part VI: The measured current candidate

The current measured experimental candidate is:

```text
TAU_QELIM_BACKEND=auto
```

This does not mean "always use BDD."
It means:

- accept only the supported leading-existential propositional fragment,
- run exact structural preprocessing before BDD construction,
- use a measured BDD order inside the compiled route,
- fall back when the fragment compiler rejects the formula.

The current aggregate measurement is:

$$
\operatorname{speedup}_{\mathrm{agg}}
:=
\frac{
  \sum_i t_{\mathrm{default}}(i)
}{
  \sum_i t_{\mathrm{auto}}(i)
}
=
\frac{83.878}{24.158}
\approx 3.47.
$$

<strong>Standard reading.</strong>
For every checked command $i$, sum the default qelim time
$t_{\mathrm{default}}(i)$, sum the `auto` qelim time
$t_{\mathrm{auto}}(i)$, then divide the first sum by the second sum.

<strong>Plain English.</strong>
On this measured corpus, the guarded `auto` route used about one third of the
qelim time used by the default route.

<strong>Trap.</strong>
This is not a global Tau speed theorem.
It is a same-binary benchmark receipt over a bounded generated corpus.

The checked matrix recorded:

- exact output parity on the checked corpus,
- `10` wins, `1` loss, and `0` ties against Tau's default qelim path,
- summed default qelim time `83.878 ms`,
- summed `auto` qelim time about `24.158 ms`,
- aggregate qelim-time speedup about `3.47x`.

Other flags stayed opt-in because they did not justify default promotion in the
latest receipts.
For example, double-negation rewriting preserved meaning on its checked
regression, but `auto + rewrite` was slower than `auto` alone in the latest
wall-clock receipt.

## Part VII: A separate rewrite-normalizer lane

There is now a second kind of optimization evidence.
It is not qelim.
It is a checked rewrite-normalizer lane for a restricted Tau Boolean-expression
language with `common`, `pointJoin`, and `pointCompl`.

The rewrite soundness theorem has this shape:

$$
e\to e'
\Longrightarrow
\operatorname{Den}(e)=\operatorname{Den}(e').
$$

<strong>Standard reading.</strong>
If one rewrite step sends expression $e$ to expression $e'$, then both
expressions have the same denotation.

Here $\operatorname{Den}(e)$ means the Boolean-algebra value denoted by
expression $e$.

<strong>Plain English.</strong>
Every accepted simplification step keeps the same meaning.

The termination theorem uses a measure $M$ with the complement case weighted
more heavily:

$$
M(\operatorname{pointCompl}(a)) := 3M(a)+1.
$$

The checked decrease law is:

$$
e\to e'
\Longrightarrow
M(e')<M(e).
$$

<strong>Standard reading.</strong>
Every rewrite step strictly decreases the measure $M$.

<strong>Plain English.</strong>
The simplifier cannot run forever, because every step moves down a
well-founded numeric measure.

The confluence theorem has the usual diamond shape:

$$
e\to^{*} a
\wedge
e\to^{*} b
\Longrightarrow
\exists c.\,
a\to^{*} c
\wedge
b\to^{*} c.
$$

<strong>Standard reading.</strong>
If one expression rewrites to $a$ and also rewrites to $b$ through zero or more
steps, then $a$ and $b$ have a common reduct $c$.

<strong>Plain English.</strong>
Different rewrite orders can still be joined again.
That gives unique normal forms for this restricted rewrite system.

<strong>Trap.</strong>
The restriction is essential.
The checked system intentionally drops commutativity, associativity, and
distributivity as rewrite rules, because oriented versions can cycle or grow
terms.
So this is not a complete Boolean-algebra equivalence procedure.
It is a terminating and confluent simplifier for a useful Tau-expression
fragment.

The executable companion is in the public experiment repo:

[TauLang-Experiments restricted rewrite normalizer](https://github.com/TheDarkLightX/TauLang-Experiments/blob/main/docs/rewrite-normalizer.md)

The direct demo command is:

```bash
python3 scripts/tau_kb_normalizer.py normalize \
  'pointCompl(common(a, pointJoin(a, b)))' \
  --json
```

The expected normal form is:

```text
pointCompl(a)
```

The benchmark command is:

```bash
./scripts/run_benchmarks.sh
```

The latest local deterministic corpus receipt checked `255` expressions,
performed `5161` rewrite steps, found `0` Boolean-parity failures, and reduced
total expression size from `11984` nodes to `870` nodes.

<strong>Boundary.</strong>
That is a benchmark of the standalone restricted normalizer, not a Tau runtime
speedup.
It becomes a Tau performance claim only after the normalizer is wired into a Tau
execution path and measured there.

There is now a first opt-in Tau-side probe:

```bash
TAU_QELIM_BDD_KB_REWRITE=1
```

In the current patch, this flag runs a c111-inspired simplification pass inside
the experimental BDD qelim backend.
The probe suite checks five targeted qelim formulas and compares the backend
with and without the flag.
The current receipt has `5` matching outputs and `0` mismatches.
On the targeted absorption cases, the compiled expression shrank from `6` nodes
to `2`, and from `5` nodes to `1`.

<strong>Boundary.</strong>
The timing evidence is mixed on this tiny corpus.
This is a correctness-and-simplification result, not yet a promoted speedup.

There is also a guarded version:

```bash
TAU_QELIM_BDD_KB_REWRITE=guarded
```

The guarded selector has this shape:

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

<strong>Standard reading.</strong>
The guarded KB pass normalizes expression $e$ only when a cheap scan finds at
least one absorption opportunity. If the scan finds no absorption opportunity,
the pass returns $e$ unchanged.

<strong>Plain English.</strong>
Run the normalizer only where the expression already shows the local pattern
the normalizer is designed to remove.

<strong>Trap.</strong>
This is not complete Boolean-equivalence checking.
It is a selector for one restricted simplifier.

The generated matrix makes the promotion boundary sharper.
It compares six modes:

```text
bdd
bdd+kb
bdd+kb_guarded
bdd+ac
bdd+ac+kb
bdd+ac+kb_guarded
```

The current receipts preserved output parity across all modes.
On the 18-case generated matrix with `3` repetitions, guarded KB reduced
compiled KB nodes by `42.73%` and had an internal qelim-time ratio of about `0.95`
against plain BDD.
On the 34-case generated matrix with `3` repetitions, guarded KB reduced
compiled KB nodes by `40.81%` and had an internal qelim-time ratio of about `0.952`
against plain BDD.

<strong>Boundary.</strong>
These are internal qelim measurements in a generated harness.
Whole-command elapsed time stayed effectively neutral because this harness is
dominated by Tau process startup.

The production-shaped follow-up asks a different question:

```text
does guarded KB improve TAU_QELIM_BACKEND=auto?
```

That answer is currently no.
The auto-route matrix checks exact output parity against the unmodified `auto`
route and records exact default parity separately, because default and `auto`
can print equivalent residual formulas in different syntactic forms.

Current auto-route receipts:

- 18-case matrix, `3` repetitions: `auto` qelim total `18.334684 ms`;
  `auto+kb_guarded` qelim total `19.228504 ms`; ratio
  `auto+kb_guarded / auto` about `1.049`.
- 34-case matrix, `3` repetitions: `auto` qelim total `45.620071 ms`;
  `auto+kb_guarded` qelim total `45.8326 ms`; ratio
  `auto+kb_guarded / auto` about `1.005`.

With only `3` repetitions, the `1.005` ratio is within measurement noise, and
the `1.049` ratio is suggestive rather than conclusive.
The safe conclusion is narrower: this matrix is consistent with no improvement
from adding guarded KB to `auto`.

<strong>Trap.</strong>
Compiled-node reduction is not the same thing as portfolio-level speedup.
Here, guarded KB reduced intermediate nodes in the BDD sublane above, but did
not improve the composed `auto` route.

So the current engineering decision is:

```text
keep TAU_QELIM_BDD_KB_REWRITE and guarded mode opt-in
do not promote it to default yet
```

The next optimization problem is still a selector problem.
The current absorption-only guard has useful signal on generated
absorption-heavy formulas, but it is not strong enough to justify default
promotion.

## Part VIII: What the optimizer should look like

The honest optimizer shape is a portfolio, not one heroic backend.

```text
if the formula is outside the guarded fragment:
    use Tau default
else:
    drop pure quantified atoms
    apply blocked CNF dropping when the body is CNF-shaped
    apply capped Davis-Putnam distribution when the minimized residual is small
    split independent quantified-variable components
    build the BDD carrier only for the residual
    existentially abstract the remaining quantified variables
    parity-check against the reference route on bounded regressions
    run terminating rewrite normalization only on its checked rule fragment
```

This is not meant as pseudocode for the final Tau optimizer.
It is the architecture lesson from the evidence.

The hard part is not inventing one fast path.
The hard part is keeping the semantic bridge explicit at each dispatch point.

## Part IX: What to remember

The beginner takeaway is:

- `anti_prenex` is a real syntax-directed qelim idea, not random old machinery.
- BDD existential abstraction is a real compiled-carrier route on a narrower
  fragment.
- Fragment guards are correctness conditions, not optional runtime checks.
- The fastest route depends on where structure lives.
- Component splitting can dominate BDD order.
- CNF-native elimination can avoid a carrier build, but only under explicit
  blowup controls.
- Rewrite normalization is a separate lane: useful after its rule set is proved
  terminating, confluent, and semantics-preserving.
- A benchmark speedup is evidence for a scoped engineering choice, not a proof
  of universal superiority.

The research log gives the full experiment record:

```text
research/taba-tables-and-tau-qelim.md
```

That page is intentionally more detailed.
This tutorial keeps the mental model:

```text
meaning first
fragment guard second
backend choice third
benchmark promotion last
```
