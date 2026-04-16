---
title: "Fragment-Sensitive Quantifier Elimination and Safe Table Updates in Tau"
layout: docs
kicker: Short paper
description: "A concise mathematical note on the Tau qelim optimization and safe table-update fragment, with scoped claims, core equations, and measured evidence."
author: Dana Edwards
date: 2026-04-13
---

## Abstract

Author: Dana Edwards. Date: April 13, 2026.

PDF version:
[Fragment-Sensitive Quantifier Elimination and Safe Table Updates in Tau]({{ '/assets/papers/fragment-sensitive-qelim-safe-tables.pdf' | relative_url }}).

We report two scoped results from a neuro-symbolic study of Tau Language and
TABA-inspired table semantics.
First, quantifier elimination in Tau benefits from fragment-sensitive dispatch:
on a checked leading-existential propositional fragment, a guarded BDD route
with structural preprocessing produced a measured aggregate qelim-time speedup
of about $5.15$ over Tau's default route on the policy-shaped corpus.
Second, a safe table-update fragment can be given a precise pointwise revision
semantics and executed in a feature-gated Tau experiment.
Neither result proves full Tau Language optimization, full TABA tables, full
NSO, or unrestricted recurrence.
The contribution is a scoped method: propose a semantic route, formalize the
claim, mechanically check or refute it, benchmark the executable artifact, and
promote only the surviving fragment.

## 1. Method

The research loop was:

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

The symbolic side proposed candidate equivalences, carriers, and compiler
routes.
The mechanical side used Lean, Tau replay, bounded exhaustive checks, SMT
cross-checks, and theorem-proving agents to reject false statements or confirm
scoped ones.
This follows the general pattern visible in contemporary formalized
mathematics projects: human judgment selects the statement and tool boundary,
while proof assistants and automation check the exact claim.

## 2. Fragment-sensitive qelim

For a Boolean variable, exact compiled forgetting is:

$$
\exists x.\,f
=
f[x:=\bot]\vee f[x:=\top].
$$

This identity is valid for the propositional Boolean function represented by
$f$.
It does not imply that arbitrary Tau formulas can be projected by collecting all
existentials globally.
The experimental dispatcher therefore has the guarded form:

$$
Q(\varphi)=
\begin{cases}
\operatorname{abstract}_{\mathrm{BDD}}(\varphi),
& \varphi\in\mathcal{F}_{\exists\mathrm{prop}},\\
Q_0(\varphi),
& \varphi\notin\mathcal{F}_{\exists\mathrm{prop}},
\end{cases}
$$

where $Q_0$ is Tau's default qelim route and
$\mathcal{F}_{\exists\mathrm{prop}}$ is the supported leading-existential
propositional fragment.
The guard is part of correctness.
The counterexample shape

$$
\neg\exists y.\,P(y)\equiv \forall y.\,\neg P(y)
\not\equiv
\exists y.\,\neg P(y)
$$

shows why nested or non-prefix existential formulas must fall back.

Inside the accepted fragment, additional exact rewrites are available.
For independent quantified components:

$$
\exists X.\,\bigwedge_{i=1}^{k}F_i
\equiv
\bigwedge_{i=1}^{k}\exists X_i.\,F_i,
$$

provided no quantified variable is shared between distinct components.
For a pure zero-test atom $p_x:=(x=0)$:

$$
\exists x.\,\Phi(p_x,y)\equiv \Phi(\top,y)
\quad
\text{if }p_x\text{ occurs only positively},
$$

and

$$
\exists x.\,\Phi(p_x,y)\equiv \Phi(\bot,y)
\quad
\text{if }p_x\text{ occurs only negatively}.
$$

For CNF-shaped formulas, Davis-Putnam elimination gives:

$$
\exists x
\left(
  R
  \wedge
  \bigwedge_i(x\vee A_i)
  \wedge
  \bigwedge_j(\neg x\vee B_j)
\right)
\equiv
R\wedge
\bigwedge_{i,j}(A_i\vee B_j).
$$

This route is exact but can create a product of resolvents, so the executable
lane uses explicit caps and subsumption-aware minimization before accepting the
step.

The current measured candidate is:

$$
\operatorname{speedup}_{\mathrm{agg}}
:=
\frac{\sum_i t_{\mathrm{default}}(i)}
     {\sum_i t_{\mathrm{auto}}(i)}
=
\frac{210.853}{40.940207}
\approx 5.15.
$$

This is a bounded same-binary benchmark result for `TAU_QELIM_BACKEND=auto`.
It is not a global speed theorem. The measured corpus is policy-shaped and
semantic residual parity was checked for the printed residual formulas.

## 3. Safe table update

The safe table fragment treats a table as a function:

$$
T:I\to\alpha,
$$

where $I$ is the key space and $\alpha$ is a Boolean-algebra value carrier.
The pointwise revision operator is:

$$
\operatorname{Rev}_{G,A}(T)(i)
:=
\bigl(G(i)\wedge A(i)\bigr)
\vee
\bigl(G(i)'\wedge T(i)\bigr).
$$

For each key $i$, the revised table uses $A(i)$ inside guard $G(i)$ and
the old value $T(i)$ inside the prime $G(i)^{\prime}$.
This is safe in the checked recurrence fragment because $G$ and $A$ are
fixed relative to the current recursive state.
It is not permission to use same-stratum prime on the current table.

The checked semantic laws are:

$$
T\le U
\Longrightarrow
\operatorname{Rev}_{G,A}(T)
\le
\operatorname{Rev}_{G,A}(U),
$$

and, for increasing omega-chains,

$$
\operatorname{Rev}_{G,A}\!\left(\bigvee_{n < \omega}T_n\right)
=
\bigvee_{n < \omega}\operatorname{Rev}_{G,A}(T_n).
$$

Thus pointwise revision is monotone in the old table and commutes with the
omega-supremum used by the safe recurrence semantics.
The Tau experiment implements a finite executable surface and symbolic helpers
behind a feature flag, and checks the table syntax against raw guarded-choice
expansions.

## 4. Boundary

The results are intentionally fragment-scoped.
They do not prove:

- global replacement of Tau's default qelim route,
- correctness or speedup on all Tau inputs,
- unrestricted TABA tables,
- same-stratum prime in recursive table bodies,
- current-state-dependent guards without extra monotonicity conditions,
- full NSO or Guarded Successor lowering,
- production integration into upstream Tau.

The mathematical lesson is narrower and reusable:

$$
\operatorname{Optimization}
=
\operatorname{SemanticGuard}
+ \operatorname{ExactRoute}
+ \operatorname{Fallback}
+ \operatorname{Evidence}.
$$

The engineering lesson is that table and qelim optimization should be planned
as fragment dispatch.
The fastest route depends on where the exploitable structure lives: syntax,
CNF clauses, a compiled carrier, or a table representation.

## References

- Ohad Asor, [Theories and Applications of Boolean Algebras](https://tau.net/wp-content/uploads/2026/03/Theories-and-Applications-of-Boolean-Algebras-0.25.pdf), draft v0.25, 2024.
- R. E. Bryant, "Graph-Based Algorithms for Boolean Function Manipulation," IEEE Transactions on Computers, 35(8), 1986.
- M. Davis and H. Putnam, "A Computing Procedure for Quantification Theory," Journal of the ACM, 7(3), 1960.
- Christoph Zengler, Andreas Kuebler, and Wolfgang Kuechlin, "New Approaches to Boolean Quantifier Elimination," 2011.
- Eugene Goldberg and Panagiotis Manolios, "Quantifier Elimination by Dependency Sequents," Formal Methods in System Design, 45, 2014.
- Hidenao Iwane and Hirokazu Anai, "Formula Simplification for Real Quantifier Elimination Using Geometric Invariance," ISSAC, 2017.
- Esther Claudine Bitye Mvondo, Yves Cherruault, and Jean-Claude Mazza, "Global Optimization with Alpha-Dense Curves: Resolution of Boolean Equations," Kybernetes, 41, 2012.
- K. G. Papakonstantinou and G. Papakonstantinou, "A Nonlinear Integer Programming Approach for the Minimization of Boolean Expressions," Journal of Circuits, Systems, and Computers, 27(10), 2018.
- Full local research log: [Tau qelim and TABA table semantics]({{ '/research/taba-tables-and-tau-qelim/' | relative_url }}).
