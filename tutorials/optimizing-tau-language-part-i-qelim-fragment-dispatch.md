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
If eliminating \(x\) from \(\exists x.\,\varphi\) returns \(\psi\), then for
every assignment \(\rho\) of the remaining variables, \(\psi\) is true exactly
when there exists a Boolean value \(b\) such that \(\varphi\) is true after
setting \(x\) to \(b\).

<strong>Plain English.</strong>
The eliminated formula must answer the same yes-or-no question about the visible
variables as the original existential formula.

<strong>Trap.</strong>
Quantifier elimination is not witness extraction.
It does not have to return the value of \(x\).
It must remove \(x\) while preserving whether some value of \(x\) makes the
formula true.

For a Boolean variable, the basic compiled-forgetting identity is:

$$
\exists x.\,f
=
f[x:=\bot]\vee f[x:=\top].
$$

<strong>Standard reading.</strong>
The existential abstraction of \(x\) from \(f\) is the join of the cofactor of
\(f\) with \(x\) forced to \(\bot\) and the cofactor of \(f\) with \(x\) forced
to \(\top\).

<strong>Plain English.</strong>
Forget \(x\) by keeping both possible branches and joining them.

<strong>Trap.</strong>
The notation \(f[x:=\bot]\) is substitution, not multiplication and not
function application in the calculus sense.
It means: evaluate the Boolean formula \(f\) after forcing \(x\) to the bottom
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
If \(x\) is not a free variable of \(A\), then existential quantification over
\(x\) can move inward past \(A\), leaving \(A\) outside and quantifying only
\(B\).

<strong>Plain English.</strong>
If one part of a conjunction does not mention the hidden variable, keep that
part outside the search.

<strong>Trap.</strong>
The side condition \(x\notin FV(A)\) is not decorative.
If \(A\) depends on \(x\), moving the quantifier past \(A\) can change the
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
If \(\varphi\) belongs to the supported leading-existential propositional
fragment \(\mathcal{F}_{\exists\mathrm{prop}}\), Tau uses BDD existential
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
"There is no \(y\) satisfying \(P\)" means "every \(y\) fails \(P\)."

<strong>Trap.</strong>
It does not mean:

$$
\exists y.\,\neg P(y).
$$

That would say "some \(y\) fails \(P\)," which is weaker and usually different.

The concrete failing shape was:

```text
qelim !(ex y (y = 0))
```

The inner sentence is true because \(y=0\) has a witness, namely \(0\).
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

when each \(X_i = X\cap FV(F_i)\) and no quantified variable is shared between
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

If \(p_x\) occurs only positively, the safe rewrite is:

$$
\exists x.\,\Phi(p_x,y)
\equiv
\Phi(\top,y).
$$

If \(p_x\) occurs only negatively, the dual rewrite is:

$$
\exists x.\,\Phi(p_x,y)
\equiv
\Phi(\bot,y).
$$

<strong>Standard reading.</strong>
When the zero-test atom \(p_x\) for an existential variable occurs in only one
polarity, choose the truth value that satisfies that polarity and remove the
quantified atom.

<strong>Plain English.</strong>
If the formula only asks for \(x=0\), choose \(x=0\).
If it only asks against \(x=0\), choose a value that makes \(x=0\) false.

<strong>Trap.</strong>
This is not a general rewrite for every expression named \(x\).
It is a polarity rule for the supported zero-test atom \(p_x := (x=0)\) inside
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
To existentially eliminate \(x\) from a CNF formula, keep the clauses \(R\) that
do not mention \(x\), and add every resolvent \((A_i\vee B_j)\) formed from a
positive \(x\)-clause and a negative \(x\)-clause.

<strong>Plain English.</strong>
Pair each positive occurrence of the hidden atom with each negative occurrence,
resolve the pairs, then drop the old clauses mentioning that atom.

<strong>Trap.</strong>
The product \(\bigwedge_{i,j}\) is the danger.
If there are \(m\) positive clauses and \(n\) negative clauses, the raw step can
create \(mn\) resolvents.
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

<strong>Standard reading.</strong>
For every checked command \(i\), sum the default qelim time
\(t_{\mathrm{default}}(i)\), sum the `auto` qelim time
\(t_{\mathrm{auto}}(i)\), then divide the first sum by the second sum.

<strong>Plain English.</strong>
On this measured policy-shaped corpus, the guarded `auto` route used about one
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

The later restricted Knuth-Bendix-style normalizer gives a different kind of
optimization evidence.
It is not a whole-language qelim backend.
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
The guarded KB pass normalizes expression \(e\) only when a cheap scan finds at
least one absorption opportunity. If the scan finds no absorption opportunity,
the pass returns \(e\) unchanged.

<strong>Plain English.</strong>
Do not run the rewrite normalizer everywhere. Run it only where the expression
already shows the local pattern the normalizer is meant to remove.

<strong>Trap.</strong>
This is not complete Boolean equivalence checking.
Two expressions can be semantically equal even if this restricted normalizer
does not reduce them to the same form.

Current patched-Tau check records:

- the qelim probe preserved output parity on all `5` targeted formulas,
- the 18-case generated matrix with `3` repetitions preserved output parity
  across all modes,
- on that 18-case matrix, guarded KB reduced compiled KB nodes by `42.73%` and
  had internal qelim-time ratio about `0.95` against plain BDD,
- on a 34-case generated matrix with `3` repetitions, guarded KB reduced
  compiled KB nodes by `40.81%` and had internal qelim-time ratio about `0.952`
  against plain BDD,
- on the policy-shaped semantic corpus, `auto + guarded KB` preserved parity
  but recorded `0` KB rewrite steps and was slightly slower than `auto` alone,
- elapsed whole-command time stayed effectively neutral because this harness is
  dominated by Tau process startup.

So the promotion decision is deliberately conservative:

```text
TAU_QELIM_BDD_KB_REWRITE=guarded is useful research evidence.
It is not ready as a default Tau optimization.
```

## Part VII: A separate path-simplification target

Tau's public known-issues list also points to a different optimization surface:
path simplification should use equalities between variables.
This is not qelim itself.
It is a normalizer pass that can shrink branch-local formulas before later
passes see them.

The safe law is:

$$
\left(\forall x,\ \rho(\operatorname{rep}(x))=\rho(x)\right)
\Longrightarrow
\llbracket \operatorname{subst}_{\operatorname{rep}}(e)\rrbracket_\rho
=
\llbracket e\rrbracket_\rho.
$$

<strong>Standard reading.</strong>
If the environment \(\rho\) gives every variable \(x\) the same value as its
chosen representative \(\operatorname{rep}(x)\), then evaluating the expression
after representative substitution gives the same value as evaluating the
original expression.

<strong>Plain English.</strong>
On a branch where the formula already says two variables are equal, the
normalizer may replace one by the other inside that branch.

<strong>Trap.</strong>
The equality premise is load-bearing.
The replacement is not globally valid.
It is valid only in the path where those equalities are known.

Tau already handles some simple branch-local equality reductions. For example,
it normalizes \(x=y\wedge ((x\wedge y')=0)\) to \(x=y\). The next gap is
recombination: after an equality split creates two residual branches, the
normalizer may still print a longer formula than it needs.

The recombination law is:

$$
(A\wedge B)\vee(\neg A\wedge B)\Longleftrightarrow B.
$$

<strong>Standard reading.</strong>
The disjunction of the branch where \(A\) and \(B\) both hold and the branch
where \(A\) is false but \(B\) holds is equivalent to \(B\).

<strong>Plain English.</strong>
If both sides of a split keep the same residual condition \(B\), the split no
longer matters.

<strong>Trap.</strong>
This recombination law is not equality-specific. Equality matters here because
equality-path simplification can create the repeated residual \(B\).

The Tau-facing branch-recombination probe asks Tau to prove:

$$
\operatorname{Unsat}
\left(
  \neg(\operatorname{Original}\leftrightarrow\operatorname{Target})
\right).
$$

<strong>Standard reading.</strong>
There is no satisfying assignment that separates the original formula from the
candidate shorter target.

<strong>Plain English.</strong>
Tau itself confirms that the shorter target says the same thing.

Current probe check record:

- `4` checked cases,
- `4` useful reduction cases,
- baseline matched target cases: `0`,
- combined current normalized size `152` characters,
- combined target normalized size `36` characters,
- candidate character reduction `76.316%`,
- all equivalence checks passed.

The proof packet `tau_equality_split_recombination_2026_04_15` checks the
Boolean and propositional forms of the recombination law.

The first feature-gated Tau patch is:

```text
TAU_EQUALITY_SPLIT_RECOMBINE=1
```

With the flag enabled, the current patch makes Tau emit the target normal form
for `3` of the `4` checked cases and reduces the combined normalized-character
count from `152` to `36`, the same combined size as the target forms.
The fourth case matches under Tau's `mnf` command, so the remaining mismatch is
presentation-level ordering in `normalize`, not a semantic failure.

This is the strongest current Tau-native normalizer target because the semantic
premise is precise and Tau already proves the target formulas equivalent.
The current implementation is still scoped and feature-gated. The remaining
technical issue is canonical presentation: the three-alias case reaches the
target size but prints an equivalent Boolean term ordering instead of the exact
target string. The next step is to move beyond the smoke corpus and test the
real normalizer path on a larger equality-split corpus.

The wider alias-order smoke test is also useful:

```text
cases:                         8
matched target cases:          3
target-sized cases:            8
Tau-normalized characters:   108
target-normalized characters: 108
MNF-matched target cases:      8
```

The additional cases permute the equality path. They show that the pass is not
limited to one hand-written alias order. They also show the current boundary:
the feature-gated pass has closed the size-reduction obligation on this corpus,
while final presentation canonicalization remains separate work.

The generated path-sensitive corpus is harder:

```text
baseline target-sized cases:   2 / 48
enabled target-sized cases:   48 / 48
baseline normalize chars:    2088
enabled normalize chars:     378
target normalize chars:      378
MNF-matched target cases:     48 / 48
```

<strong>Standard reading.</strong>
On the generated corpus, the feature flag improves the number of formulas whose
normalized output is no longer larger than the target from \(2\) out of \(48\)
to \(48\) out of \(48\). The enabled normalized-character count is \(378\),
which is exactly the target count. Exact `normalize` text still matches \(24\)
out of \(48\) cases, and all \(48\) cases match the target under Tau's `mnf`
command.

<strong>Plain English.</strong>
The feature-gated recombination pass now closes this generated corpus on size.
What remains is canonical printing of equivalent Boolean terms.

<strong>Trap.</strong>
The \(24\) textual mismatches are not semantic mismatches. They are presentation
differences under `normalize`, such as equivalent Boolean terms printed in
different orders. This is still not a default Tau optimization: the pass remains
feature-gated until larger generated corpora and presentation canonicalization
are checked.

The next stress corpus uses four-variable equality chains:

```text
enabled target-sized cases:  105 / 105
enabled normalize chars:     847
target normalize chars:      847
MNF-matched target cases:    105 / 105
exact normalize matches:      84 / 105
```

<strong>Standard reading.</strong>
On the stress corpus, every one of the \(105\) formulas produced by the
feature-gated normalizer has normalized size no larger than the corresponding
target formula. The total normalized-character count is \(847\), exactly the
target total. All \(105\) cases match under `mnf`, while \(84\) cases match the
target text exactly under `normalize`.

<strong>Plain English.</strong>
The pass now handles equality chains where the alias branch changes the shape
of the residual, including cases where the alias branch makes the residual
trivially true.

<strong>Trap.</strong>
This still does not prove a default Tau optimization. It proves a stronger
feature-gated experiment over a larger generated corpus. The remaining gap is
canonical presentation and broader workload testing.

The five-variable wide corpus extends the same check:

```text
enabled target-sized cases:  200 / 200
enabled normalize chars:    1980
target normalize chars:     1980
MNF-matched target cases:    200 / 200
exact normalize matches:     130 / 200
```

<strong>Standard reading.</strong>
On the wide corpus, all \(200\) feature-gated normal forms are target-sized.
The total enabled normalized-character count is \(1980\), exactly the target
total. All \(200\) cases match under `mnf`, and \(130\) cases match exactly
under `normalize`.

<strong>Plain English.</strong>
The current recombination rules survive the next generated-corpus expansion.
The next unsolved problem is not branch recombination on these corpora, it is
canonical presentation of equivalent Boolean terms.

<strong>Trap.</strong>
The wide corpus is still generated evidence. It is not a proof over every Tau
formula and it is not a reason to enable the pass by default without a profit
guard and broader workload testing.

The timing screen for the same corpus is:

```text
baseline normalize time:     19958.521 ms
enabled normalize time:      19432.444 ms
baseline MNF time:           16847.849 ms
enabled MNF time:            16813.717 ms
```

<strong>Standard reading.</strong>
In this harness, the total elapsed time for the \(200\) baseline `normalize`
commands is \(19958.521\) milliseconds, and the total elapsed time for the
\(200\) feature-gated `normalize` commands is \(19432.444\) milliseconds. The
same screen reports \(16847.849\) milliseconds for baseline `mnf` commands and
\(16813.717\) milliseconds for feature-gated `mnf` commands.

<strong>Plain English.</strong>
The pass removes the normalized-size blowup without showing a timing regression
in this screening run.

<strong>Trap.</strong>
This is whole-command timing. Each row calls Tau as a separate process, so the
numbers include startup and file I/O. They are useful for catching an obvious
regression, not for proving an in-process speedup.

The same wide corpus also checks whether the first `normalize` output is stable
under a second `normalize` call:

```text
baseline first-pass idempotent cases: 7 / 200
enabled first-pass idempotent cases:  140 / 200
enabled non-idempotent cases:         60 / 200
enabled second-pass growth cases:     30 / 200
guarded-presentation target-sized:    200 / 200
guarded-presentation exact matches:   160 / 200
guarded-presentation characters:      1980
guarded-MNF non-growing cases:        200 / 200
guarded-MNF shrinking cases:          40 / 200
guarded-MNF characters:               1480
```

<strong>Standard reading.</strong>
Without the recombination flag, only \(7\) of the \(200\) baseline first-pass
normal forms are unchanged by a second `normalize` call. With the recombination
flag enabled, \(140\) of the \(200\) first-pass normal forms are unchanged.
There are still \(60\) enabled cases that change on the second pass, and \(30\)
of those become longer. If the probe accepts the second-pass output only when
it is no longer than the first-pass output, then all \(200\) cases remain
target-sized, \(160\) cases match the target text exactly, and the total
guarded-presentation size remains \(1980\) characters.

<strong>Plain English.</strong>
The recombination patch improves stability, but it does not make `normalize`
fully idempotent on this corpus. A guarded second pass improves exact
presentation without giving up the size win.

<strong>Trap.</strong>
This is a different boundary from semantic correctness. All \(200\) enabled
cases still match under `mnf`. The open issue is fixed-point presentation: the
first `normalize` output should ideally already be the form that another
`normalize` call would return. The guarded second-pass rule is probe evidence,
not yet a Tau C++ optimizer patch. A direct AST-level second-normalize hook was
tested and did not improve the corpus. The remaining target is a
presentation-aware canonicalization pass, not simply running the same tree
through `normalize` again.

The stronger candidate is guarded `mnf`: use the `mnf` presentation only when
it does not increase printed size. On this corpus it is non-growing for all
\(200\) cases, shrinks \(40\) cases, and reduces total printed size from
\(1980\) to \(1480\) characters. This is still a candidate presentation mode,
not a claim that `mnf` should replace `normalize` globally.

The new rule that closed the larger corpus is an equality-graph implication
rule:

$$
(A\Rightarrow R)\wedge(R\wedge\neg D\Rightarrow A)
\Longrightarrow
A\vee(R\wedge D)\equiv R.
$$

<strong>Standard reading.</strong>
If alias condition \(A\) implies residual \(R\), and \(R\) together with not
\(D\) implies \(A\), then the disjunction \(A\vee(R\wedge D)\) is equivalent to
\(R\).

<strong>Plain English.</strong>
If the left branch already guarantees the residual, and the residual covers the
right branch whether the guard-disjunction \(D\) holds or fails, the whole split
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
If \(a\) is not equal to \(b\), then along any finite path
\(a=t_0,t_1,\ldots,t_k=b\), at least one adjacent equality on that path must
fail.

<strong>Plain English.</strong>
If the endpoints differ, some edge in any proposed equality chain between them
must differ.

## Part VIII: Effects, derivatives, and finite equivalence

The next optimizer lane is not another qelim backend. It is an execution model
for deciding which parts of a Tau expression need to run again.

The read-set law is:

$$
\rho\!\restriction_{\operatorname{Reads}(e)}
=
\rho'\!\restriction_{\operatorname{Reads}(e)}
\Longrightarrow
\llbracket e\rrbracket_{\rho}
=
\llbracket e\rrbracket_{\rho'}.
$$

<strong>Standard reading.</strong>
If two environments agree on every key read by expression \(e\), then evaluating
\(e\) in the first environment gives the same value as evaluating \(e\) in the
second environment.

<strong>Plain English.</strong>
Only recompute the expression when one of its actual inputs changed.

<strong>Trap.</strong>
This is not a whole-language Tau theorem yet. The checked packet proves the law
for the Tau-like expression kernel with explicit variable reads.

The derivative lane writes a single-key perturbation as an expression transform:

$$
\partial_{k,v} e.
$$

The checked soundness shape is:

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

<strong>Standard reading.</strong>
Evaluating the derivative of \(e\) at key \(k\) with replacement value \(v\)
equals the original denotation of \(e\), updated at \(k\) by the constant-leaf
evaluation of \(e\) at \(v\).

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
e \sim_{\mathrm{eval}} \operatorname{const}(\llbracket e\rrbracket).
$$

So semantic equality implies extended bisimulation:

$$
\llbracket e_1\rrbracket=\llbracket e_2\rrbracket
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
\(\llbracket e_1\rrbracket=\llbracket e_2\rrbracket\). That is immediate on a
finite carrier, but it is not automatic over arbitrary infinite carriers.

This gives a cleaner optimizer map:

```text
read sets decide what can be skipped
derivatives describe one-key changes
partial evaluation compiles known inputs away
finite-carrier equivalence checks decide restricted expression equality
```

The executable companion in `TauLang-Experiments` is:

```text
scripts/run_tau_derivative_equivalence_demo.py
```

Current check record:

```text
cases:                         80
derivative sound cases:        80
size-preserved cases:          80
equivalence classifications:   80
equivalent cases:              61
non-equivalent cases:          19
result:                        passed
```

<strong>Boundary.</strong>
This check record is for a finite Tau-like kernel. It is useful because it shows the
optimizer architecture can be executed and tested, not because it proves the
full Tau runtime already implements derivatives.

The incremental runtime-cache prototype now checks the concrete data-structure
shape too:

```text
full unique residual nodes:    193
runtime-delta recomputed:       31
runtime-delta saving:       83.938%
runtime delta checks:        passed
```

<strong>Plain English.</strong>
The demo no longer only says that an unread key can be skipped. It builds the
node table, marks dirty node IDs from a dependency index, recomputes those IDs,
and checks the cached result against full reevaluation.

There is also a native Tau runtime measurement hook:

```text
TAU_RUN_STATS=1
```

The first opt-in runtime optimization on that surface is:

```text
TAU_SKIP_UNCHANGED_IO_REBUILD=1
```

Current native-run check record:

```text
step count:              3
accepted update count:   3
total paths attempted:   6
total paths solved:      6
total revisions tried:   1
total added spec parts:  2
input rebuilds skipped:  3
output rebuilds skipped: 1
output parity:           passed
final memory size:       9
```

<strong>Standard reading.</strong>
On the update-stream pointwise-revision smoke case, the native Tau interpreter
executed three steps, accepted three updates, attempted six disjunct paths,
solved six disjunct paths, added two new specification parts, revised one
existing specification part, and ended with nine stored memory bindings.

<strong>Plain English.</strong>
Tau's real `run` loop is now measurable at the point where a future
incremental runtime cache would attach, and one small IO-rebuild optimization
now has baseline-output parity evidence.

<strong>Boundary.</strong>
This skip flag does not cache expression values or change the solver. It only
avoids recreating IO stream objects when the IO stream set is unchanged and the
active stream class declares that unchanged rebuild skipping is safe.

The follow-up regression checks the boundary directly:

```text
vector input rebuilds skipped:  3
vector output rebuilds skipped: 1
file input rebuilds skipped:    0
file output rebuilds skipped:   0
vector output parity:           passed
file output parity:             passed
```

<strong>Standard reading.</strong>
Vector-remapped streams may skip unchanged rebuilds while preserving observed
outputs. File-remapped streams perform zero skips under the same flag.

<strong>Plain English.</strong>
The optimization has a stream safety gate. Tau may skip rebuilds for streams
whose rebuild is only a state-preserving wrapper operation, but it does not skip
file streams, because rebuilding a file stream reopens the file.

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
