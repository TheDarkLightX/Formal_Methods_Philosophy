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

The argument is easiest to follow as a ladder.

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

<figure class="fp-figure">
  <svg viewBox="0 0 880 310" role="img" aria-labelledby="qelim-dispatch-title qelim-dispatch-desc">
    <title id="qelim-dispatch-title">Guarded Tau qelim dispatch</title>
    <desc id="qelim-dispatch-desc">A Tau formula first goes through a fragment guard. Rejected formulas fall back to the default syntax route. Accepted formulas enter structural preprocessing, compiled carrier elimination, and parity checks.</desc>
    <defs>
      <marker id="qelim-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
        <path d="M0,0 L8,3 L0,6 Z" fill="#273044"></path>
      </marker>
      <style>
        .qelim-box { fill: #f7f3ea; stroke: #273044; stroke-width: 2; rx: 18; }
        .qelim-guard { fill: #fff7d6; stroke: #9a6b00; stroke-width: 2; }
        .qelim-fast { fill: #e8f5ee; stroke: #24724a; stroke-width: 2; }
        .qelim-fallback { fill: #fbeaea; stroke: #8a2f2f; stroke-width: 2; }
        .qelim-text { font: 600 18px Georgia, serif; fill: #273044; }
        .qelim-small { font: 14px Georgia, serif; fill: #4d5668; }
        .qelim-edge { stroke: #273044; stroke-width: 2.5; fill: none; marker-end: url(#qelim-arrow); }
        .qelim-good { stroke: #24724a; }
        .qelim-bad { stroke: #8a2f2f; }
      </style>
    </defs>

    <rect x="40" y="120" width="145" height="70" class="qelim-box"></rect>
    <text x="112" y="150" text-anchor="middle" class="qelim-text">Tau formula</text>
    <text x="112" y="174" text-anchor="middle" class="qelim-small">meaning fixed</text>

    <rect x="245" y="105" width="155" height="100" class="qelim-guard"></rect>
    <text x="322" y="145" text-anchor="middle" class="qelim-text">Fragment</text>
    <text x="322" y="170" text-anchor="middle" class="qelim-text">guard</text>

    <rect x="480" y="35" width="170" height="78" class="qelim-fast"></rect>
    <text x="565" y="65" text-anchor="middle" class="qelim-text">Compiled</text>
    <text x="565" y="90" text-anchor="middle" class="qelim-text">carrier route</text>

    <rect x="480" y="198" width="170" height="78" class="qelim-fallback"></rect>
    <text x="565" y="228" text-anchor="middle" class="qelim-text">Default</text>
    <text x="565" y="253" text-anchor="middle" class="qelim-text">syntax route</text>

    <rect x="710" y="35" width="130" height="78" class="qelim-fast"></rect>
    <text x="775" y="65" text-anchor="middle" class="qelim-text">Parity</text>
    <text x="775" y="90" text-anchor="middle" class="qelim-text">checks</text>

    <path d="M185,155 L245,155" class="qelim-edge"></path>
    <path d="M400,140 C430,105 440,74 480,74" class="qelim-edge qelim-good"></path>
    <path d="M400,170 C430,205 440,237 480,237" class="qelim-edge qelim-bad"></path>
    <path d="M650,74 L710,74" class="qelim-edge qelim-good"></path>

    <text x="435" y="105" text-anchor="middle" class="qelim-small">accept</text>
    <text x="435" y="218" text-anchor="middle" class="qelim-small">fallback</text>
    <text x="565" y="132" text-anchor="middle" class="qelim-small">BDD, components, pure atoms, CNF</text>
    <text x="775" y="132" text-anchor="middle" class="qelim-small">same meaning or reject promotion</text>
  </svg>
  <figcaption>
    The optimizer is a guarded portfolio. The compiled route is allowed only
    after the fragment guard accepts; fallback is part of the correctness
    argument.
  </figcaption>
</figure>

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Scope</p>
  <p>This tutorial explains the checked Tau qelim experiment for a supported leading-existential propositional fragment. The current result is a guarded optimization candidate, not a proof that every Tau formula should use the same backend.</p>
</div>

The detailed research log lives here:
[Tau qelim and TABA table semantics]({{ '/research/taba-tables-and-tau-qelim/' | relative_url }}).

That page is not just a benchmark appendix.
It shows the neuro-symbolic loop in practice: propose a route, formalize the
claim, let Lean, Tau, Aristotle, SMT, or bounded replay try to break it, then
promote only the scoped claim that survives.

There is also a shorter academic-style note:
[Fragment-Sensitive Quantifier Elimination and Safe Table Updates in Tau]({{ '/research/fragment-sensitive-qelim-and-safe-tables/' | relative_url }}).

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
\frac{210.853}{40.940207}
\approx 5.15.
$$

This ratio sums the default qelim time over the checked commands, sums the
`auto` qelim time over the same commands, and divides the first total by the
second. On this policy-shaped corpus, the guarded `auto` route used about one
fifth of the qelim time used by the default route.

<strong>Trap.</strong>
This is not a global Tau speed theorem.
It is a same-binary benchmark record over a bounded policy-shaped corpus.

The public reproduction command, run from the
[TauLang-Experiments repo](https://github.com/TheDarkLightX/TauLang-Experiments),
is:

```bash
./scripts/run_qelim_table_demos.sh --accept-tau-license
```

For the full safe-table plus qelim-backed demo suite, use:

```bash
./scripts/run_public_demos.sh --accept-tau-license
```

The current policy-shaped semantic corpus recorded:

- exact output parity on the checked corpus,
- semantic residual validation on `9` policy-shaped cases,
- `45` total `auto` runs across `5` repetitions,
- route counts `{ components: 10, dp: 5, monolithic: 30 }`,
- summed default qelim time `210.853 ms`,
- summed `auto` qelim time about `40.940 ms`,
- aggregate qelim-time speedup about `5.15x`.

The older bounded ladder-and-mux matrix recorded about `3.47x`. The newer
policy-shaped corpus is the stronger tutorial evidence because it mirrors the
safe-table demo domain and validates residual formulas semantically rather
than relying only on printed syntax.

Other flags stayed opt-in because they did not justify default promotion in the
latest check records.
For example, double-negation rewriting preserved meaning on its checked
regression, but `auto + rewrite` was slower than `auto` alone in the latest
wall-clock record.

The next question is whether a rewrite normalizer should run before the
compiled route. The restricted Knuth-Bendix-style normalizer gives a useful
answer, but only in a narrow setting. It is not a whole-language qelim backend.
It is a small convergent rewrite system whose proof says: these seven oriented
rules terminate, preserve denotation, and have unique normal forms inside the
restricted expression language.

The Tau qelim patch uses that idea only as an opt-in prepass:

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
Do not run the rewrite normalizer everywhere. Run it only where the expression
already shows the local pattern the normalizer is meant to remove.

<strong>Trap.</strong>
This is not complete Boolean equivalence checking.
Two expressions can be semantically equal even if this restricted normalizer
does not reduce them to the same form.

The patched-Tau checks preserved output parity on the targeted qelim probes and
reduced the internal compiled KB node count on generated matrices. On the
policy-shaped semantic corpus, however, guarded KB found no useful rewrite
steps and was slightly slower than `auto` alone. That is enough to keep it as
research evidence, not a default optimization.

So the promotion decision is deliberately conservative:

```text
TAU_QELIM_BDD_KB_REWRITE=guarded is useful research evidence.
It is not ready as a default Tau optimization.
```

## Part VII: Other optimizer lanes

Not every Tau optimization is qelim. The qelim work exposed adjacent optimizer
lanes that belong in the same map. The research log keeps the run counts; this
tutorial keeps the laws and boundaries.

The first lane is equality-aware path simplification. It is not qelim. It is a
branch-local normalizer pass that can shrink formulas before later passes see
them.

Write $r(x)$ for the representative chosen for variable $x$.
The safe representative-substitution law is:

$$
\Bigl(\forall x.\ \rho(x)=\rho(r(x))\Bigr)
\Longrightarrow
\operatorname{Eval}(\operatorname{Subst}_{r}(e),\rho)
=
\operatorname{Eval}(e,\rho).
$$

<strong>Standard reading.</strong>
If the environment $\rho$ gives every variable $x$ the same value as its
chosen representative $r(x)$, then evaluating the expression after replacing
each variable by its representative gives the same value as evaluating the
original expression in $\rho$.

<strong>Plain English.</strong>
On a branch where the formula already says two variables are equal, the
normalizer may replace one by the other inside that branch.

<strong>Trap.</strong>
The equality premise is load-bearing.
The replacement is not globally valid.
It is valid only in the path where those equalities are known.

Tau already handles some simple branch-local equality reductions. For example,
it normalizes $x=y\wedge ((x\wedge y^{\prime})=0)$ to $x=y$. The next gap is
recombination: after an equality split creates two residual branches, the
normalizer may still print a longer formula than it needs.

The recombination law is:

$$
(A\wedge B)\vee(\neg A\wedge B)\Longleftrightarrow B.
$$

<strong>Standard reading.</strong>
The disjunction of the branch where $A$ and $B$ both hold and the branch
where $A$ is false but $B$ holds is equivalent to $B$.

<strong>Plain English.</strong>
If both sides of a split keep the same residual condition $B$, the split no
longer matters.

<strong>Trap.</strong>
This recombination law is not equality-specific. Equality matters here because
equality-path simplification can create the repeated residual $B$.

The research log records the current feature-gated Tau probes. The tutorial
takeaway is narrower: equality-aware simplification is a strong Tau-native
normalizer target because its semantic premise is precise, the shorter forms
can be checked by Tau itself, and presentation differences can be separated
from semantic failures.

One later rule that closed the larger equality corpus is an equality-graph
implication rule:

$$
(A\Rightarrow R)\wedge(R\wedge\neg D\Rightarrow A)
\Longrightarrow
A\vee(R\wedge D)\equiv R.
$$

<strong>Standard reading.</strong>
If alias condition $A$ implies residual $R$, and $R$ together with not
$D$ implies $A$, then the disjunction $A\vee(R\wedge D)$ is equivalent to
$R$.

<strong>Plain English.</strong>
If the left branch already guarantees the residual, and the residual covers the
right branch whether the guard-disjunction $D$ holds or fails, the whole split
can be collapsed to the residual.

The conjunction cleanup uses the equality-path law:

$$
a\ne b
\Longrightarrow
\bigvee_{i<k}(t_i\ne t_{i+1})
\quad
\text{when }t_0=a\text{ and }t_k=b.
$$

<strong>Standard reading.</strong>
If $a$ is not equal to $b$, then along any finite path
$a=t_0,t_1,\ldots,t_k=b$, at least one adjacent equality on that path must
fail.

<strong>Plain English.</strong>
If the endpoints differ, some edge in any proposed equality chain between them
must differ.

## Part VIII: Effects, derivatives, and finite equivalence

The next optimizer lane is not another qelim backend. It is an execution model
for deciding which parts of a Tau expression need to run again.

The read-set law is:

$$
\rho|_{\operatorname{Reads}(e)}
=
\rho'|_{\operatorname{Reads}(e)}
\Longrightarrow
\operatorname{Eval}(e,\rho)
=
\operatorname{Eval}(e,\rho').
$$

<strong>Standard reading.</strong>
If the environments $\rho$ and $\rho^{\prime}$ agree after both are restricted to
the keys read by $e$, then evaluating $e$ under $\rho$ gives the same
value as evaluating $e$ under $\rho^{\prime}$.

<strong>Plain English.</strong>
Only recompute the expression when one of its actual inputs changed.

<strong>Trap.</strong>
This is not a whole-language Tau theorem yet. The checked packet proves the law
for the Tau-like expression kernel with explicit variable reads.

Write $\Delta_{k,v}e$ for the derivative-style transform that records the
effect of changing key $k$ to value $v$.

$$
\Delta_{k,v}e.
$$

The checked soundness shape is:

$$
\operatorname{Eval}(\Delta_{k,v}e)
=
\operatorname{Update}
\left(
  \operatorname{Eval}(e),
  k,
  \operatorname{EvalConst}(e,v)
\right).
$$

<strong>Standard reading.</strong>
Evaluating $\Delta_{k,v}e$ equals the evaluation of $e$, updated at key
$k$ by the constant-leaf evaluation of $e$ at $v$.

<strong>Plain English.</strong>
The derivative is a symbolic description of the local effect of one input-key
change.

<strong>Trap.</strong>
This is inspired by Brzozowski derivatives, but it is not a regular-language
derivative. Here the derivative is over Tau-style Boolean-algebra expression
trees.

The equivalence-checking lane has a sharp boundary. For the restricted
`const/common/pointJoin/pointCompl` expression kernel, the extended relation
can reduce every expression to its semantic constant:

$$
e \sim_{\mathrm{eval}} \operatorname{Const}(\operatorname{Eval}(e)).
$$

So semantic equality implies extended bisimulation:

$$
\operatorname{Eval}(e_1)=\operatorname{Eval}(e_2)
\Longrightarrow
e_1\sim_{\mathrm{eval}} e_2.
$$

<strong>Standard reading.</strong>
If two expressions have the same denotation, then the extended bisimulation
relation relates them.

<strong>Plain English.</strong>
After adding constant-evaluation rules, the rewrite relation is complete for
this kernel.

<strong>Trap.</strong>
The completeness theorem is algebraic. Turning it into an executable decision
procedure still requires deciding whether
$\operatorname{Eval}(e_1)=\operatorname{Eval}(e_2)$. That is immediate on a
finite carrier, but it is not automatic over arbitrary infinite carriers.

This gives a cleaner optimizer map:

```text
read sets decide what can be skipped
derivatives describe one-key changes
partial evaluation compiles known inputs away
finite-carrier equivalence checks decide restricted expression equality
```

The executable companions check these ideas on finite Tau-like kernels and on
a small native Tau runtime measurement hook. That is useful engineering
evidence, but it is not a solver-level qelim breakthrough. The detailed counts
belong in the research log.

There is also a newer RR rewrite-stage experiment:

```text
TAU_RR_ACTIVE_RULES=1
```

It is not a qelim backend. It is a dynamic filter for recurrence-definition
rewriting. On each rewrite pass, it scans the current term for visible
reference signatures and tries only the rules whose head signature is present.

The local law is:

$$
\operatorname{Head}(q)\notin\operatorname{Refs}(t)
\Longrightarrow
\operatorname{apply}(q,t)=t.
$$

<strong>Standard reading.</strong>
If rewrite rule $q$'s head reference signature is not present in term $t$,
then applying $q$ to $t$ leaves $t$ unchanged.

<strong>Plain English.</strong>
Do not spend time trying a definition rule whose function symbol does not
appear in the expression currently being rewritten.

<strong>Boundary.</strong>
The rule is not deleted globally. The active set is recomputed on later passes,
because another rewrite may introduce that reference. The current receipt
reduces internal RR rewrite time by `88.821%` on the three-repetition batched
table corpus, but it is still opt-in and not a default Tau optimization. The
missing proof is not merely the local nonmatch law. The full proof must show
that delaying skipped rules across repeated passes preserves the same rewrite
fixed point.

The audit flag `TAU_RR_ACTIVE_RULES_AUDIT=1` checks that final active
repeated-rewrite results match full repeated-rewrite results. On the current
batched receipt, `15 / 15` audit rows were structurally equal. That is stronger
than output parity, but still corpus evidence.

## Part IX: What the optimizer should look like

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
```

This is not meant as pseudocode for the final Tau optimizer.
It is the architecture lesson from the evidence.

The hard part is not inventing one fast path.
The hard part is keeping the semantic bridge explicit at each dispatch point.

## Part X: What to remember

The beginner takeaway is:

- `anti_prenex` is a real syntax-directed qelim idea, not random old machinery.
- BDD existential abstraction is a real compiled-carrier route on a narrower
  fragment.
- Fragment guards are correctness conditions, not optional runtime checks.
- The fastest route depends on where structure lives.
- Component splitting can dominate BDD order.
- CNF-native elimination can avoid a carrier build, but only under explicit
  blowup controls.
- Equality-aware path simplification is path-scoped. The equality facts must
  justify the representative substitution in the branch where it is used.
- Read-set and derivative proofs suggest a second optimizer family: avoid
  rerunning unaffected expression parts after small input changes.
- Extended bisimulation is complete for the checked expression kernel, but an
  executable decision procedure still depends on the carrier's equality
  decision.
- A benchmark speedup is evidence for a scoped engineering choice, not a proof
  of universal superiority.

The research log gives the full experiment record:
[Tau qelim and TABA table semantics]({{ '/research/taba-tables-and-tau-qelim/' | relative_url }}).

That page is intentionally more detailed.
This tutorial keeps the mental model:

```text
meaning first
fragment guard second
backend choice third
benchmark promotion last
```
