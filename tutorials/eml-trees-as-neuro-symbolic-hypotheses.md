---
title: "EML trees as neuro-symbolic hypotheses"
layout: docs
kicker: Tutorial 50
description: "Use EML trees as a tiny symbolic hypothesis language inside a neuro-symbolic proposal, filter, and renormalize loop."
---

Tutorial 49 used Tau to filter a finite audited menu.
This tutorial keeps the same propose, filter, and renormalize shape, but
changes the symbolic object. The candidate is a formula tree.

That raises a different question:

```text
What if the symbolic object being proposed is itself a formula?
```

The source idea comes from Andrzej Odrzywolek's 2026 preprint
["All elementary functions from a single binary operator"](https://arxiv.org/abs/2603.21852v2).
The paper shows that the single binary operator

$$
\operatorname{eml}(x,y)=\exp(x)-\ln(y)
$$

together with the constant $1$, can construct a standard elementary-function
basis.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Scope</p>
  <p>This tutorial is a finite teaching experiment. It does not reproduce the paper's gradient-training pipeline. It also does not claim a complete analytic proof stack for EML. The demo uses EML trees as the symbolic hypothesis language inside a propose, filter, and renormalize loop. For the current depth-3 survivors, it adds two stronger checks: a Lean-checked finite certificate layer and a SymPy simplification check with <code>x</code> declared positive.</p>
</div>

The Tau-facing experiment repo is:

- [TheDarkLightX/TauLang-Experiments](https://github.com/TheDarkLightX/TauLang-Experiments)

The local demo is:

```bash
python3 scripts/run_eml_neurosymbolic_loop_demo.py
```

The proposal-filter demo with external candidate input is:

```bash
python3 scripts/run_eml_neurosymbolic_loop_demo.py \
  --candidate-json experiments/eml_symbolic_hypothesis_fixtures/llm_candidates_v1.json
```

The external-proposal prompt and validation packet is:

```bash
python3 scripts/generate_eml_llm_proposal_packet.py \
  --llm-output experiments/eml_symbolic_hypothesis_fixtures/llm_candidates_v1.json
```

The feedback-conditioned second proposal packet is:

```bash
python3 scripts/generate_eml_llm_proposal_packet.py \
  --feedback-json results/local/eml-reproposal-feedback-packet.json \
  --llm-output experiments/eml_symbolic_hypothesis_fixtures/llm_candidates_v2_feedback.json \
  --prompt-out results/local/eml-llm-reproposal-prompt.md \
  --candidate-out results/local/eml-llm-reproposals.json \
  --validation-out results/local/eml-llm-reproposal-validation.json
```

The identity-target extension is enabled explicitly:

```bash
python3 scripts/run_eml_neurosymbolic_loop_demo.py \
  --include-identity-target \
  --candidate-json results/local/eml-identity-proposals.json \
  --out results/local/eml-neurosymbolic-loop-demo-identity.json \
  --sidecar-out results/local/eml-tau-sidecar-manifest-identity.json \
  --feedback-out results/local/eml-reproposal-feedback-packet-identity.json
```

The composition-target extension adds one more target:

```bash
python3 scripts/run_eml_neurosymbolic_loop_demo.py \
  --include-identity-target \
  --include-exp-exp-target \
  --candidate-json results/local/eml-composition-proposals.json \
  --out results/local/eml-neurosymbolic-loop-demo-composition.json \
  --sidecar-out results/local/eml-tau-sidecar-manifest-composition.json \
  --feedback-out results/local/eml-reproposal-feedback-packet-composition.json
```

It writes:

```text
results/local/eml-neurosymbolic-loop-demo.json
results/local/eml-tau-sidecar-manifest.json
results/local/eml-reproposal-feedback-packet.json
```

## Part I: the loop

The hard-filter neuro-symbolic loop is:

$$
q_{\mathrm{NS}}(y\mid x)
=
\frac{q_{\mathrm{N}}(y\mid x)\chi_{\mathrm{S}}(y,x)}
{Z(x)},
\qquad
Z(x)=\sum_{y'}q_{\mathrm{N}}(y'\mid x)\chi_{\mathrm{S}}(y',x).
$$

<strong>Standard reading.</strong>
For candidate $y$ and input $x$, the neuro-symbolic probability of $y$ given
$x$ is the neural probability of $y$ given $x$, multiplied by the symbolic
indicator for $y$ at $x$, divided by the normalizing quantity $Z(x)$. The
normalizing quantity is the sum, over candidates $y'$, of each neural
probability multiplied by its symbolic indicator.

<strong>Plain English.</strong>
The neural side proposes and scores candidates. The symbolic side deletes the
candidates that fail the check. The remaining mass is renormalized.

The soft-scoring version is:

$$
q_{\mathrm{NS}}(y\mid x)
\propto
q_{\mathrm{N}}(y\mid x)\exp(\beta s_{\mathrm{S}}(y,x)).
$$

<strong>Standard reading.</strong>
For candidate $y$ and input $x$, the neuro-symbolic probability is proportional
to the neural probability of $y$ given $x$ multiplied by the exponential of
$\beta$ times the symbolic score of $y$ at $x$.

<strong>Plain English.</strong>
Instead of deleting failures outright, the symbolic layer can raise or lower
candidate weight.

<strong>Trap.</strong>
The hard-filter equation and the soft-scoring equation are different trust
models. A hard filter is appropriate when symbolic rejection must be decisive.
A soft score is appropriate when the symbolic signal is advisory.

In the EML experiment, the candidate is not an action.
The candidate is a tree $T$.

$$
q_{\mathrm{NS}}(T\mid D)
\propto
q_{\mathrm{N}}(T\mid D)\,
\chi_{\mathrm{valid}}(T)\,
\chi_{\mathrm{spec}}(T,D).
$$

<strong>Standard reading.</strong>
For tree $T$ and data $D$, the neuro-symbolic probability of $T$ given $D$ is
proportional to the neural probability of $T$ given $D$, multiplied by the
validity indicator of $T$ and the specification indicator of $T$ on $D$.

<strong>Plain English.</strong>
A proposed formula survives only if it is valid to evaluate and matches the
specification being tested.

An iterative learning version has this shape:

$$
T_t\sim q_{\mathrm{N}}(\cdot\mid D,\theta_t),
\qquad
v_t=\operatorname{Verify}_{\mathrm{S}}(D,T_t),
\qquad
\theta_{t+1}=\operatorname{Update}(\theta_t,v_t).
$$

<strong>Standard reading.</strong>
At step $t$, a tree $T_t$ is sampled from the neural proposal distribution
conditioned on data $D$ and parameters $\theta_t$. The symbolic verifier then
computes $v_t$ from $D$ and $T_t$. The next parameter state
$\theta_{t+1}$ is obtained by applying the update rule to $\theta_t$ and
$v_t$.

<strong>Plain English.</strong>
Generate a formula, check it, feed the check result back, then generate again.

<strong>Trap.</strong>
The first filter is not a proof that a surviving tree is globally identical to
the target function. In this demo, $\chi_{\mathrm{spec}}$ is a finite sampled
numerical check. Two additional checks are then applied to survivors: a
Lean-checked finite certificate layer for the current survivor shapes, and a
SymPy simplification check with $x$ declared positive. The script runs
one finite search pass, not the full parameter-update loop.

## Part II: the EML grammar

The symbolic hypothesis language is:

$$
T ::= x \mid 1 \mid \operatorname{eml}(T,T).
$$

<strong>Standard reading.</strong>
The metavariable $T$ ranges over the smallest tree language generated by three
clauses: the variable $x$ is a tree, the constant $1$ is a tree, and whenever
two objects are trees, an EML node built from those two trees is also a tree.

<strong>Plain English.</strong>
Every candidate formula is a binary tree built from one operation, one
variable, and one constant.

The operation is:

$$
\operatorname{eml}(a,b)=\exp(a)-\ln(b).
$$

<strong>Standard reading.</strong>
The expression $\operatorname{eml}(a,b)$ denotes the exponential of $a$ minus
the natural logarithm of $b$.

<strong>Plain English.</strong>
Each internal node applies the same operation to two child expressions.

<strong>Trap.</strong>
Over the real numbers, $\ln(b)$ requires $b>0$. The paper discusses complex
semantics and branch issues. This tutorial's demo uses a simpler real-domain
guard, so many trees are rejected before scoring.

## Part III: what the demo searches

The demo enumerates all EML trees up to depth $3$ using:

```text
T ::= x | 1 | eml(T,T)
```

For each tree, it checks the sample grid:

$$
G=\{0.5,1,2\}.
$$

The script also evaluates survivors on a holdout grid:

$$
G_{\mathrm{holdout}}=\{0.25,0.75,1.5,3\}.
$$

<strong>Standard reading.</strong>
The holdout grid $G_{\mathrm{holdout}}$ denotes the finite set whose four
elements are $0.25$, $0.75$, $1.5$, and $3$.

<strong>Plain English.</strong>
The demo keeps a small second test set so a survivor has to pass more than the
points used to select it.

It then computes mean squared error:

$$
\operatorname{MSE}(T,f)
=
\frac{1}{|G|}
\sum_{x\in G}
(T(x)-f(x))^2.
$$

<strong>Standard reading.</strong>
The mean-squared error $\operatorname{MSE}(T,f)$ is the average, over sample
points $x$ in $G$, of the squared difference between the value of tree $T$ at
$x$ and the value of the target function $f$ at $x$.

<strong>Plain English.</strong>
The checker measures how closely a candidate tree matches the target on the
chosen sample points.

The symbolic filter is:

$$
\chi_{\mathrm{spec}}(T,D)=1
\quad\Longleftrightarrow\quad
\operatorname{MSE}(T,f)\le \varepsilon.
$$

<strong>Standard reading.</strong>
The specification indicator for $T$ on data $D$ is true exactly when the
mean-squared error of $T$ against $f$ is at most the tolerance
$\varepsilon$.

<strong>Plain English.</strong>
A candidate survives if its sampled error is below the tolerance.

<strong>Trap.</strong>
This is a finite data check. The current script adds SymPy simplification for
survivors, and the proof packet adds a finite Lean certificate layer for the
current survivor shapes. That is still not the same as a complete
machine-checked theorem about all EML trees.

## Part IV: first result

The current run uses depth $3$ and enumerates:

```text
candidate_count: 1446
```

The evidence levels are:

| Level | Meaning |
|---|---|
| training grid | the tree matches $G=\{0.5,1,2\}$ |
| holdout grid | the tree also matches $G_{\mathrm{holdout}}=\{0.25,0.75,1.5,3\}$ |
| Lean certificate | the survivor shape is accepted by the finite `Cert.check` surface whose soundness is proved in Lean |
| Lean normal-form check | the survivor shape maps to a finite normal form, and `checkByNorm_sound` proves accepted normal-form checks are sound |
| symbolic simplification | SymPy simplifies the difference against the target to $0$ with $x$ declared positive |

The Lean layers are checked in `experiments/neuro_symbolic_math_v001/Proofs.lean`.
The SymPy simplification check runs in the Python demo script and is scoped by
declaring $x$ positive.

For the target $\exp(x)$, the run finds one exact survivor:

$$
\operatorname{eml}(x,1).
$$

<strong>Standard reading.</strong>
The expression $\operatorname{eml}(x,1)$ denotes $\exp(x)-\ln(1)$.

<strong>Plain English.</strong>
Since $\ln(1)=0$, this tree denotes $\exp(x)$.

For the target $\ln(x)$, the run finds two survivors:

$$
\operatorname{eml}(1,\operatorname{eml}(\operatorname{eml}(1,x),1))
$$

and

$$
\operatorname{eml}(x,\operatorname{eml}(\operatorname{eml}(x,x),1)).
$$

<strong>Standard reading.</strong>
The first tree denotes
$\exp(1)-\ln(\operatorname{eml}(\operatorname{eml}(1,x),1))$. The second tree
denotes $\exp(x)-\ln(\operatorname{eml}(\operatorname{eml}(x,x),1))$.

<strong>Plain English.</strong>
In the depth-3 demo run, both trees survive the sampled filter for $\ln(x)$.
When the symbolic verifier is available, SymPy simplifies each tree's
difference from $\ln(x)$ to $0$ with $x$ declared positive.

<strong>Trap.</strong>
The first $\ln(x)$ expression is the standard construction cited in the arXiv
abstract. The second is a useful discovery from this finite search. The current
evidence includes a Lean-checked abstract certificate and symbolic
simplification, but it is still not a Lean theorem about the complex
principal-branch semantics discussed in the paper.

The demo receipt also records a finite certificate name for each current
survivor:

```text
certificate_checker:
  Lean-checked finite certificate checker for five current survivor shapes

eml(x,1): certificate = expTree
eml(eml(x,1),1): certificate = expExpTree
eml(1,eml(eml(1,x),1)): certificate = logStandardTree
eml(x,eml(eml(x,x),1)): certificate = logDiscoveredTree
eml(1,eml(eml(1,eml(x,1)),1)): certificate = identityViaLogExpTree
```

The Lean packet also records a finite normal-form layer:

```text
normal forms: x, exp(x), exp(exp(x)), ln(x)
certNorm_sound: accepted normal forms preserve EML meaning
checkByNorm_sound: accepted normal-form checks imply the target identity
```

This is still a finite recognition surface. It is not a recursive EML
normalizer.

With the identity target enabled, the finite survivor family has one more
proof-backed member:

$$
\operatorname{eml}\bigl(1,\operatorname{eml}(\operatorname{eml}(1,\operatorname{eml}(x,1)),1)\bigr).
$$

<strong>Standard reading.</strong>
The displayed expression is
$\operatorname{eml}\bigl(1,\operatorname{eml}(\operatorname{eml}(1,\operatorname{eml}(x,1)),1)\bigr)$.

<strong>Plain English.</strong>
The experiment can now compose discovered building blocks: build $\exp(x)$,
wrap it in the EML form of $\ln$, and recover $x$.

<strong>Boundary.</strong>
This is still a named finite surface. It does not make the strategy normalizer
complete for arbitrary EML trees.

The composition extension uses the context-lift law:

$$
\llbracket \operatorname{eml}(T,1) \rrbracket
=
\exp(\llbracket T \rrbracket).
$$

<strong>Standard reading.</strong>
For any EML tree $T$, the denotation of $\operatorname{eml}(T,1)$ is the
exponential of the denotation of $T$, under the abstract EML laws used by the
Lean packet.

<strong>Plain English.</strong>
Once a tree for $\exp(x)$ has been proved, wrapping that tree as
`eml(_,1)` gives a proved tree for $\exp(\exp(x))$.

The accepted composition tree is:

$$
\operatorname{eml}(\operatorname{eml}(x,1),1).
$$

<strong>Standard reading.</strong>
The displayed expression is an EML node whose left child is
$\operatorname{eml}(x,1)$ and whose right child is $1$. Under the abstract EML
laws, it denotes $\exp(\exp(x))$.

<strong>Boundary.</strong>
This proves one useful context pattern. It is not a theorem that every possible
EML context preserves every known target in a useful normal form.

The next cycle promotes this from one wrapper into a tiny constructor library:

$$
\operatorname{WrapExp}(T)=\operatorname{eml}(T,1),
\qquad
\operatorname{WrapLog}(T)=
\operatorname{eml}\bigl(1,\operatorname{eml}(\operatorname{eml}(1,T),1)\bigr).
$$

The checked semantic laws are:

$$
\llbracket \operatorname{WrapExp}(T) \rrbracket
=
\exp(\llbracket T \rrbracket),
\qquad
\llbracket \operatorname{WrapLog}(T) \rrbracket
=
\ln(\llbracket T \rrbracket).
$$

<strong>Standard reading.</strong>
For every EML tree $T$, the denotation of $\operatorname{WrapExp}(T)$ is
$\exp(\llbracket T \rrbracket)$, and the denotation of
$\operatorname{WrapLog}(T)$ is $\ln(\llbracket T \rrbracket)$, under the
abstract EML laws used by the Lean packet.

<strong>Plain English.</strong>
The search loop now has two reusable safe moves: wrap a proved formula to take
its exponential, or wrap it to take its logarithm.

One accepted composed survivor is:

$$
\operatorname{WrapLog}(\operatorname{WrapExp}(\operatorname{WrapExp}(x))).
$$

Expanded as raw EML syntax, this is:

$$
\operatorname{eml}\bigl(1,
  \operatorname{eml}(
    \operatorname{eml}(1,\operatorname{eml}(\operatorname{eml}(x,1),1)),
    1
  )
\bigr).
$$

<strong>Standard reading.</strong>
The expression denotes $\ln(\exp(\exp(x)))$, which equals $\exp(x)$ under the
abstract law $\ln(\exp(a))=a$.

<strong>Boundary.</strong>
This is a two-constructor proof surface. It is not a full symbolic-regression
engine and not a complete grammar-level EML normalizer.

The practical proposer interface can now be smaller than raw EML. A constructor
plan uses only:

```text
Var
WrapExp(plan)
WrapLog(plan)
```

For example:

```text
WrapLog(WrapExp(WrapExp(Var)))
```

compiles to the raw EML expression above, then passes through the same qNS and
proof-receipt gates as every other candidate.

<strong>Standard reading.</strong>
The displayed constructor plan first applies the exponential wrapper to the
base variable, applies the exponential wrapper a second time to that result,
and then applies the logarithm wrapper to the whole expression.

<strong>Plain English.</strong>
Instead of asking a model to write a long fragile EML string, the prompt can ask
for a short plan over checked constructors.

<strong>Boundary.</strong>
The plan language is safer proposal syntax. It is not trusted by itself. The
compiled formula must still pass the parser, qNS masks, domain checks, sampled
checks, holdout checks, and proof receipts.

The plan compiler now records a small proposal budget:

```text
maximum plan depth = 3
maximum WrapExp count = 2
maximum WrapLog count = 1
```

It also records the obligations introduced by each constructor. `WrapExp`
adds an exponential-argument guard. `WrapLog` adds a positive-log-argument
guard.

<strong>Standard reading.</strong>
A plan is accepted by the budget only if its depth is at most $3$, its number
of exponential-wrapper constructors is at most $2$, and its number of
logarithm-wrapper constructors is at most $1$.

<strong>Plain English.</strong>
The loop can now reject proposals that are too deep, use an unproved
constructor, or omit required constructor arguments before expanding them into
long EML strings.

<strong>Boundary.</strong>
Budget acceptance is still not proof evidence. It is only an early rejection
gate before the normal qNS and proof-receipt checks.

The next audit joins those plan obligations to the sidecar's interval evidence.
For the current accepted plans, the audit checks eight obligations:

```text
exp_argument_guard: source expression appears in exp_arguments_checked
positive_log_argument: source expression appears in log_arguments_checked
```

All eight are discharged on the bounded interval $[0.25,3]$.

<strong>Standard reading.</strong>
An exponential-argument obligation is discharged when the sidecar records an
interval entry for that source expression and that interval stays within the
configured exponential bound. A positive-logarithm obligation is discharged
when the sidecar records an interval entry for that source expression whose
lower endpoint is strictly positive.

<strong>Plain English.</strong>
The plan does not merely say "this formula has a log here." The receipt now
points to the exact interval check that made that log safe in the bounded demo.

<strong>Boundary.</strong>
The obligation audit is still bounded evidence. It links plan obligations to
sidecar checks; it is not a complete proof about all real inputs.

The promotion manifest uses all three gates:

```text
qNS accepted
AND proof metadata accepted
AND constructor obligations discharged
```

In the negative gate test, one audit row is deliberately tampered so one
obligation fails. The promotion manifest then promotes three constructor-plan
candidates and routes one candidate to review.

<strong>Standard reading.</strong>
A constructor-plan candidate is promoted only when three recorded predicates
all hold: the qNS status accepts the formula, the proof metadata accepts the
formula, and the constructor-obligation audit row is marked successful.

<strong>Plain English.</strong>
No single artifact gets to decide promotion alone. The formula has to survive
the symbolic filter, the proof metadata check, and the domain-obligation audit.

<strong>Boundary.</strong>
The promotion manifest is an evidence gate, not the evidence itself.

The loop then emits a constructor-plan feedback packet for the next proposer
round. It contains:

```text
promoted plans,
rejected plans,
active budget,
allowed constructors,
constructor theorem names,
next-round constraints
```

<strong>Standard reading.</strong>
The feedback packet is a finite record whose promoted rows come from the
promotion manifest and whose rejected rows come from the constructor-plan reject
artifact.

<strong>Plain English.</strong>
The next proposer gets the useful examples and the failed examples, but it
still does not get authority over the checker.

<strong>Boundary.</strong>
Feedback is steering information. It is not proof evidence.

The second feedback-conditioned fixture then reruns the same gates:

```text
baseline rejected_plan_count = 3
second_round rejected_plan_count = 0
baseline promoted_count = 4
second_round promoted_count = 5
```

The new promoted constructor sequence is:

$$
\operatorname{WrapLog}(\operatorname{Var})
\rightsquigarrow
\operatorname{eml}(1,\operatorname{eml}(\operatorname{eml}(1,x),1)).
$$

<strong>Standard reading.</strong>
The constructor plan $\operatorname{WrapLog}(\operatorname{Var})$ compiles to
the EML tree
$\operatorname{eml}(1,\operatorname{eml}(\operatorname{eml}(1,x),1))$ and is
promoted for the target $\ln(x)$ with theorem lineage
`NeuroSymbolicMathV001.EML.eval_wrapLogStandard`.

<strong>Plain English.</strong>
After seeing the first feedback packet, the next fixture proposes the direct
logarithm constructor that the earlier batch missed.

<strong>Boundary.</strong>
This is a deterministic feedback-conditioned fixture. It shows a useful loop
improvement on this bounded surface, not learned symbolic regression.

The next handoff layer turns the latest feedback into a JSON-only prompt for an
untrusted constructor-plan proposer, then audits the returned plan file before
compilation.

```text
positive fixture: 5 compliant, 0 noncompliant
negative fixture: 1 compliant, 3 noncompliant
```

The negative fixture is rejected for exactly the hazards the feedback contract
is meant to catch: unsupported constructor, over-budget plan, and missing
constructor argument.

<strong>Standard reading.</strong>
A constructor-plan proposal is feedback-compliant exactly when every proposal
uses an allowed constructor, stays within the active depth and wrapper-count
budgets, and supplies the required arguments for constructor nodes.

<strong>Plain English.</strong>
The prompt can now ask a model for constructor plans, and a separate audit can
reject bad plan shapes before they become raw EML strings.

<strong>Boundary.</strong>
Compliance is not proof evidence. A compliant plan must still pass compilation,
qNS masks, domain checks, sampled checks, holdout checks, proof metadata,
obligation audit, and promotion.

The handoff runner composes those pieces into one quarantine-first round. It
first audits the whole untrusted proposal file, writes a compliant-only plan
file, and then runs only those compliant rows through the evidence gates.

```text
positive handoff: 5 input rows, 0 quarantined, 5 promoted
negative handoff: 4 input rows, 3 quarantined, 1 promoted
```

<strong>Standard reading.</strong>
In the negative handoff run, the input proposal file has four rows. Three rows
are noncompliant and are not compiled. The one compliant row is compiled,
checked by the downstream gates, and promoted.

<strong>Plain English.</strong>
The loop can now handle a mixed-quality proposal file without letting bad rows
poison the good row.

<strong>Boundary.</strong>
The handoff report is orchestration evidence. It is not a new mathematical proof
of EML completeness or a native Tau analytic feature.

The next mathematician tactic is decomposition plus checked equivalence. For
constructor plans, the useful decomposition is the unary constructor spine. On
that spine, one safe equivalence-repair rule is:

$$
\operatorname{WrapLog}(\operatorname{WrapExp}(T)) \leadsto T.
$$

<strong>Standard reading.</strong>
The rewrite rule applies to a constructor plan whose outer constructor is
$\operatorname{WrapLog}$ and whose child has outer constructor
$\operatorname{WrapExp}$ with subplan $T$. In that case, the normalizer
replaces the two-constructor prefix by $T$.

<strong>Plain English.</strong>
A logarithm wrapped around an exponential is redundant, so the plan can be
repaired to the smaller plan underneath.

The equivalence-repair fixture checks four redundant plans:

```text
row_count = 4
changed_count = 4
total depth: 12 -> 4
total WrapExp count: 7 -> 3
total WrapLog count: 5 -> 1
handoff result: 3 promoted, 1 review
```

After adding the direct identity receipt, the same fixture reports:

```text
handoff result after v706: 4 promoted, 0 review
```

<strong>Standard reading.</strong>
The enabled meaning-preserving rewrite rule changes all four fixture rows. The
sum of their plan depths decreases from $12$ to $4$, the sum of their
exponential-wrapper counts decreases from $7$ to $3$, and the sum of their
logarithm-wrapper counts decreases from $5$ to $1$. After the direct variable
receipt is added, all four normalized rows are promoted.

<strong>Plain English.</strong>
The normalizer removes eight constructor layers before the evidence gates run.

<strong>Trap.</strong>
In v705, the row that normalized to `Var` for target $x$ was routed to review
because the sidecar had a receipt for the wrapped identity form but not for the
direct candidate `Var -> x`. v706 closes that proof-interface gap with a direct
`Cert.varTree` receipt and zero-obligation audit handling.

<strong>Boundary.</strong>
This is not a complete EML normalizer. The opposite-looking direction,
$\operatorname{WrapExp}(\operatorname{WrapLog}(T)) \leadsto T$, is not enabled
yet because it needs explicit positivity-domain obligations.

The guarded opposite direction is now tested as a separate rule:

$$
\operatorname{WrapExp}(\operatorname{WrapLog}(T)) \leadsto T
\quad\text{with residual obligation}\quad
\llbracket T \rrbracket > 0.
$$

<strong>Standard reading.</strong>
The rewrite from $\operatorname{WrapExp}(\operatorname{WrapLog}(T))$ to $T$ is
allowed only together with an additional obligation that the denotation of $T$
is strictly positive on the checked interval.

<strong>Plain English.</strong>
The normalizer may remove an exponential around a logarithm only if it carries
forward the condition that the thing inside the logarithm is positive.

The guarded fixture reports:

```text
row_count = 3
changed_count = 3
total depth: 8 -> 2
residual obligations = 2
discharged obligations = 3
failed obligations = 1
handoff result: 2 promoted, 1 review
```

<strong>Standard reading.</strong>
All three fixture rows are changed. The sum of their plan depths decreases from
$8$ to $2$. Two residual positivity obligations are introduced by the guarded
equivalence rule. The full obligation audit discharges three obligations and fails one
obligation.

<strong>Trap.</strong>
The reviewed row is the $\ln(x)$ row. Its normalized value has interval
$[-1.386\ldots,1.098\ldots]$ on $[0.25,3]$, so the residual condition
$\llbracket T \rrbracket>0$ is false on the checked interval. The row is
reviewed because the guard fails, not because the parser or proof sidecar broke.

<strong>Boundary.</strong>
This is bounded interval evidence, not a complete real-analysis theorem.

The next compression step quotients by the normalized representative:

$$
\text{class}(P)=
\bigl(\operatorname{target}(P),\operatorname{normalize}(P)\bigr).
$$

<strong>Standard reading.</strong>
The class of a constructor plan $P$ is the ordered pair whose first component is
the target formula of $P$ and whose second component is the normalized
constructor plan obtained from $P$.

<strong>Plain English.</strong>
After local rewrites are done, syntactically different plans can share one
canonical proof target.

The quotient fixture reports:

```text
row_count = 9
class_count = 3
quotient reduction = 6
changed_count = 6
total depth: 18 -> 6
handoff result: 7 promoted, 2 review
```

<strong>Standard reading.</strong>
The nine constructor-plan rows are partitioned into three normalized classes.
The number of rows minus the number of classes is six. Six rows are changed by
normalization. The sum of plan depths decreases from $18$ to $6$. Seven member
rows are promoted and two member rows are routed to review.

<strong>Trap.</strong>
Class membership does not promote an unsafe member. In the logarithm class, the
canonical `WrapLog(Var)` member promotes, while two guarded-equivalence members are
reviewed because their own residual positivity obligations fail.

The quotient can also be rendered as a local-obligation graph:

$$
\operatorname{Accept}(m)
\Longleftrightarrow
\operatorname{CanonOK}(\operatorname{class}(m))
\wedge
\bigwedge_{o\in\operatorname{Obl}(m)}\operatorname{OK}(o).
$$

<strong>Standard reading.</strong>
A member $m$ is accepted exactly when the canonical proof target for the class
of $m$ is available and every local obligation attached to $m$ is satisfied.

<strong>Plain English.</strong>
Prove the shared case once, but still check every side condition that belongs
to each syntactic variant.

The local-obligation graph reports:

```text
canonical proof targets = 3
member cases = 9
local rewrite obligations = 6
residual obligations = 3
accepted members = 7
blocked members = 2
```

Once the graph exposes the quotient classes, the loop can add a
representative-selection gate:

$$
\operatorname{Rep}(C)
=
\arg\min_{m\in C}
\bigl(
|\operatorname{Obl}(m)|,\operatorname{depth}(m),
\operatorname{constructors}(m)
\bigr).
$$

<strong>Standard reading.</strong>
The representative of a class $C$ is a member $m$ of $C$ minimizing, in order,
the number of obligations of $m$, the depth of $m$, and the constructor count
of $m$.

<strong>Plain English.</strong>
Keep the simplest member with the fewest side conditions, then run the real
evidence gates only on that representative.

The representative-selection fixture reports:

```text
input rows = 9
selected representatives = 3
pruned rows = 6
handoff result = 3 promoted, 0 review
```

<strong>Trap.</strong>
Selection is not proof. It is a way to avoid spending proof-search budget on
known-equivalent variants. The selected representatives still pass through the
same qNS, domain, proof, obligation, and promotion gates.

The claim boundary has to be explicit:

$$
\operatorname{CoverageMode}
\ne
\operatorname{AllMembersCertified}.
$$

<strong>Standard reading.</strong>
Coverage mode and all-members-certified mode are distinct claims.

<strong>Plain English.</strong>
Selecting one representative per quotient class shows that every class has a
checked representative. It does not by itself show that every pruned member
would pass its own side conditions.

The coverage audit reports:

```text
selected representatives = 3
pruned rows = 6
certified pruned rows = 4
hidden blocked rows = 2
all original members certified = false
```

<strong>Trap.</strong>
This is the same discipline as centering a quadratic at its axis of symmetry:
the translation makes one part of the problem vanish, but it does not erase the
conditions needed to move back to the original coordinates.

The loop then turns the quotient audit into next-round feedback:

```text
covered canonical classes = 3
hidden blocked variants = 2
next constraints = 12
```

<strong>Standard reading.</strong>
The feedback packet records three canonical classes already covered by the
current proof-search loop, two hidden blocked variants from coverage-mode
representative selection, and twelve constraints for the next proposal round.

<strong>Plain English.</strong>
The next proposer is told which quotient classes are already solved and which
blocked members failed their side conditions.

The feedback can now be measured against proposal files:

```text
quotient-unaware fixture:
  covered-class repeats = 6
  hidden-blocked repeats = 2
  novel classes = 0

quotient-aware fixture:
  covered-class repeats = 0
  hidden-blocked repeats = 0
  novel classes = 1
  handoff result = 1 promoted, 0 review
```

<strong>Standard reading.</strong>
The first fixture repeats six already covered classes and two hidden blocked
variants, and contributes zero novel normalized classes. The second fixture
repeats no covered classes, repeats no hidden blocked variants, contributes one
novel normalized class, and that proposal is promoted by the downstream
handoff.

<strong>Plain English.</strong>
This is the first measurable sign that quotient-aware feedback can save search
budget.

There is also a general compilation theorem:

```text
Tree.compileExpr: EML tree -> expression AST
compileExpr_sound: compiled expression evaluation equals original tree evaluation
```

This theorem applies to every EML tree. It does not simplify the tree. It
creates the right target language for rewrite certificates because the compiled
expression names `exp`, `log`, and subtraction directly.

The next proof layer is a checked rewrite-certificate system:

```text
RewriteCert.apply?: certificate + expression -> optional rewritten expression
RewriteCert.apply?_sound: every accepted rewrite preserves expression meaning
RewriteChain.apply?: certificate list + expression -> optional final expression
RewriteChain.apply?_sound: every accepted finite chain preserves meaning
```

The root rewrite rules used in this demo are:

- `log(1) -> 0`
- `sub(a,0) -> a`
- `log(exp(a)) -> a`
- `sub(a,sub(a,b)) -> b`

The checker can also apply one such rule under `exp`, under `log`, or on either
side of `sub`.

This turns simplification into an explicit object: a finite list of rewrite
certificates that is either accepted by `RewriteChain.apply?` or rejected. The
soundness theorem for accepted chains is `RewriteChain.apply?_sound`. This is
still not full normalization.

For the discovered $\ln(x)$ survivor, the proof packet now includes a concrete
four-step trace:

```text
logDiscoveredRewriteChain:
1. rewrite nested log(1) to 0
2. rewrite nested sub(a,0) to a
3. rewrite right-side log(exp(a)) to a
4. rewrite root sub(a,sub(a,b)) to b
```

The checked theorem says:

```text
logDiscoveredRewriteChain_sound:
  eval(logDiscoveredTree.compileExpr) = log(x)
```

This is the first end-to-end proof trace for a discovered EML survivor. It is
still one concrete trace, not a general trace generator.

The proof packet also wraps the trace in a fail-closed emitter:

```text
emitRewriteChain?: tree + target -> optional certificate chain
emitRewriteChain?_accepts: every emitted chain applies to the compiled tree
emitRewriteChain?_sound: every emitted chain proves the requested target meaning
```

The current emitter recognizes only the discovered `ln(x)` survivor. Other
cases return `none`. Emitted traces are still checked, and unsupported inputs
fail closed.

The newest layer adds a small fail-closed one-step strategy over compiled
expressions:

```text
RewriteStrategy.emitStepCert?: expression -> optional candidate certificate
RewriteStrategy.emitStep?: expression -> optional (certificate, rewritten expression)
RewriteStrategy.emitStep?_sound: every returned step preserves meaning
```

The one-step strategy is heuristic, but its output is not trusted directly. It
proposes a certificate, immediately runs the checker, and returns only checked
steps.

The bounded iterator repeats that checked step:

```text
RewriteStrategy.emitChainFuel: fuel + expression -> (certificate chain, final expression)
RewriteStrategy.emitChainFuel_accepts: the emitted chain is accepted
RewriteStrategy.emitChainFuel_sound: the final expression preserves meaning
```

This gives bounded automated simplification. It still does not prove that the
fuel is enough to reach a normal form.

For the discovered $\ln(x)$ survivor, the proof packet proves a concrete fuel
bound:

```text
logDiscovered_emitChainFuel_4_reaches:
  emitChainFuel 4 logDiscoveredTree.compileExpr reaches log(x)

logDiscovered_emitChainFuel_4_chain:
  emitChainFuel 4 logDiscoveredTree.compileExpr emits logDiscoveredRewriteChain
```

So the demo now has one complete bounded proof-carrying simplification path.
That is still not a global termination theorem.

The other current survivors now have checked fuel bounds too:

```text
exp_emitChainFuel_2_reaches:
  emitChainFuel 2 expTree.compileExpr reaches exp(x)

expExp_emitChainFuel_size_reaches:
  emitChainFuel expExpTree.compileExpr.size expExpTree.compileExpr reaches exp(exp(x))

logStandard_emitChainFuel_4_reaches:
  emitChainFuel 4 logStandardTree.compileExpr reaches log(x)
```

So every survivor reported by the current depth-3 demo has a checked bounded
rewrite path to its target. This is finite survivor-family coverage, not
arbitrary EML-tree coverage.

The next structural theorem is a size-decrease measure:

```text
RewriteStrategy.emitStep?_size_decreases:
  emitStep? before = some (cert, after) implies after.size < before.size
```

<strong>Standard reading.</strong>
The size-decrease theorem says that whenever one rewrite step succeeds on a
source expression and returns a certificate together with a target expression,
the target expression is strictly smaller than the source expression.

<strong>Plain English.</strong>
Every accepted strategy step makes the expression structurally smaller.

<strong>Boundary.</strong>
This is the termination measure for accepted one-step rewrites. It is not yet a
full normalization theorem, not confluence, and not a proof that the strategy
finds a rewrite whenever one exists.

That measure now supports a bounded stopping theorem:

```text
RewriteStrategy.emitChainFuel_size_stable:
  emitStep? (emitChainFuel before.size before).2 = none
```

<strong>Standard reading.</strong>
The bounded stopping theorem says that after running the rewrite chain from a
source expression with fuel equal to the source expression's starting size, one
more rewrite attempt on the resulting expression reports no accepted next step.

<strong>Plain English.</strong>
The current strategy cannot keep rewriting forever. Starting-size fuel is enough
to reach a point where this strategy has no next step.

<strong>Boundary.</strong>
This is strategy stability. It does not say the final expression is the unique
canonical representative of its semantic equivalence class.

For the current survivor family, the proof packet also names the stable target
forms reached by starting-size fuel:

```text
expTree          -> exp(x)
expExpTree       -> exp(exp(x))
logStandardTree  -> log(x)
logDiscoveredTree -> log(x)
identityViaLogExpTree -> x
```

<strong>Standard reading.</strong>
For each listed tree, running the rewrite chain on its compiled expression with
fuel equal to the compiled expression's size returns the listed target
expression, and that target expression has no further accepted rewrite step.

<strong>Plain English.</strong>
The current examples no longer rely on arbitrary hand-picked fuel. The checked
fuel policy is: use the source expression's own size.

<strong>Boundary.</strong>
This is finite-family normal-form evidence. It is not a canonical-normal-form
theorem for arbitrary EML trees.

The finite normal-form checker and the compiled rewrite strategy are now linked:

```text
certNorm_emitChainFuel_size_reaches:
  tree.certNorm = some norm implies
  (emitChainFuel tree.compileExpr.size tree.compileExpr).2 = norm.compileExpr
```

<strong>Standard reading.</strong>
For any raw EML tree and any normal form, if the finite certificate checker
accepts that normal form for the tree, then running the compiled-expression
strategy with fuel equal to the size of the compiled tree returns the compiled
form of that same normal form.

<strong>Plain English.</strong>
Anything accepted by the current finite normal-form checker now has a checked
path through the compiled rewrite strategy to the same normal form.

<strong>Boundary.</strong>
This quantifies over the accepted surface of `certNorm`, but `certNorm` is still
a finite checker. The next real upgrade is a structurally recursive normalizer
for a wider EML fragment.

The same ingredients now expose a total strategy-normalizer API.
In the Lean file, these live under `RewriteStrategy`:

```text
normalize(expr) := (emitChainFuel expr.size expr).2

normalize_stable:
  emitStep? (normalize expr) = none

normalize_sound:
  eval(expr) = eval(normalize(expr))
```

<strong>Standard reading.</strong>
The normalizer of an expression is defined to be the expression reached by
running the rewrite chain from that expression with fuel equal to its starting
size. The soundness theorem states that the original expression and its
normalized form have the same evaluation. The stability theorem states that the
normalized form has no further accepted rewrite step.

<strong>Plain English.</strong>
The proof stack now gives a checked simplifier API for the current strategy.
It always returns, it stops at a strategy-stable expression, and it preserves
meaning.

<strong>Boundary.</strong>
This is a strategy normalizer, not a canonical semantic normalizer. It does not
prove uniqueness of normal forms.

A small corollary is a sound equality check:

```text
equivByNormalize?(a,b) := decide (normalize(a) = normalize(b))

equivByNormalize?_sound:
  equivByNormalize?(a,b) = true implies eval(a) = eval(b)
```

<strong>Standard reading.</strong>
The normalization-based equivalence checker is sound in this sense: whenever
it returns true on two expressions, those two expressions have the same
evaluation.

<strong>Plain English.</strong>
If the normalizer produces the same output expression, equality is safe to
trust. If the outputs differ, the checker does not prove inequality.

<strong>Boundary.</strong>
This checker is sound but incomplete. Two expressions can be semantically equal
and still normalize to different strategy-stable expressions.

For example, the compiled expression AST includes both a dedicated `zero` node
and the explicit subtraction form `sub(exp(1),exp(1))`. Those two expressions
have the same denotation by definition of `Expr.eval`, but the current
strategy does not rewrite the expanded form back to `zero`, so
`equivByNormalize?` rejects the pair.

A small upgrade is to add a sound pre-pass that canonicalizes
`sub(exp(1),exp(1))` to `zero` before normalization. The proof packet exposes
`equivByNormalizeCanonZero?` as the corresponding sound but incomplete equality
check.

If a witness is useful, the proof packet also exposes a receipt-returning
variant:

```text
equivReceiptCanonZero?(a,b) : Option (chainA, chainB, nf)

equivReceiptCanonZero?_sound:
  equivReceiptCanonZero?(a,b) = some (...) implies eval(a) = eval(b)
```

Operationally, this is `equivByNormalizeCanonZero?` with a witness. When it
returns `some (chainA, chainB, nf)`, `chainA` and `chainB` are the checked
normalization receipts for `a` and `b` (after the canon-zero pre-pass), and
`nf` is the shared normal form they reach.

The proof packet also links the two surfaces:

```text
equivReceiptCanonZero?_some_implies_equivByNormalizeCanonZero?_true:
  equivReceiptCanonZero?(a,b) = some (...) implies equivByNormalizeCanonZero?(a,b) = true

equivByNormalizeCanonZero?_true_implies_equivReceiptCanonZero?_some:
  equivByNormalizeCanonZero?(a,b) = true implies equivReceiptCanonZero?(a,b) = some (...)
```

The strategy normalizer is also idempotent:

```text
normalize_idempotent:
  normalize(normalize(expr)) = normalize(expr)
```

<strong>Standard reading.</strong>
Normalizing an expression that has already been normalized returns the same
normalized expression.

<strong>Plain English.</strong>
Once the current strategy has normalized an expression, running the same
normalizer again does not change it.

<strong>Boundary.</strong>
Idempotence is an API stability law. It is not confluence and does not imply
that different rewrite strategies would reach the same expression.

The receipt also records this symbolic-simplification layer:

```text
symbolic_verifier: sympy simplify over a positive real symbol
eml(x,1): simplified_difference = 0
eml(eml(x,1),1): simplified_difference = 0
eml(1,eml(eml(1,eml(eml(x,1),1)),1)): simplified_difference = 0
eml(1,eml(eml(1,x),1)): simplified_difference = 0
eml(x,eml(eml(x,x),1)): simplified_difference = 0
```

The holdout receipt is:

```text
eml(x,1): holdout_ok = true
eml(eml(x,1),1): holdout_ok = true
eml(1,eml(eml(1,eml(eml(x,1),1)),1)): holdout_ok = true
eml(1,eml(eml(1,x),1)): holdout_ok = true
eml(x,eml(eml(x,x),1)): holdout_ok = true
```

## Part V: zoom in on the discovered log tree

The second $\ln(x)$ survivor is worth slowing down over:

$$
\operatorname{eml}(x,\operatorname{eml}(\operatorname{eml}(x,x),1)).
$$

<strong>Standard reading.</strong>
The displayed expression is an EML node whose left child is $x$ and whose right
child is another EML node. That right child has left child
$\operatorname{eml}(x,x)$ and right child $1$.

<strong>Exact derivation.</strong>
Now expand one layer at a time. First:

$$
\operatorname{eml}(x,x)=\exp(x)-\ln(x).
$$

Then:

$$
\operatorname{eml}(\operatorname{eml}(x,x),1)
=
\exp(\exp(x)-\ln(x))-\ln(1).
$$

Since $\ln(1)=0$, and for $x>0$,

$$
\exp(\exp(x)-\ln(x))
=
\frac{\exp(\exp(x))}{x}.
$$

So the whole expression becomes:

$$
\operatorname{eml}\!\left(x,\frac{\exp(\exp(x))}{x}\right)
=
\exp(x)-\ln\!\left(\frac{\exp(\exp(x))}{x}\right).
$$

For $x>0$:

$$
\ln\!\left(\frac{\exp(\exp(x))}{x}\right)
=
\exp(x)-\ln(x).
$$

Therefore:

$$
\exp(x)-(\exp(x)-\ln(x))=\ln(x).
$$

<strong>Plain English.</strong>
The right subtree builds $\exp(\exp(x))/x$, whose logarithm is
$\exp(x)-\ln(x)$ for $x>0$. The outer subtraction then cancels the $\exp(x)$
term, leaving $\ln(x)$.

<strong>Trap.</strong>
This derivation uses the positive-real law for logarithms. It is not the same
as proving the expression over the complex principal branch without additional
branch conditions.

## Part VI: what this experiment gives

This gives the neuro-symbolic loop a second use case.

The qNS carrier experiment was:

```text
candidate actions -> exact finite symbolic filter
```

The EML experiment is:

```text
candidate formulas -> domain/spec filter -> surviving symbolic explanations
```

Many formal-methods workflows need formula search:

- symbolic regression,
- invariant discovery,
- closed-form cost-model discovery,
- proof-hint generation,
- simplifier rule discovery,
- compact model extraction from numerical traces.

The EML grammar is intentionally small: one operation, one variable, and one
constant. Even in that restricted language, many elementary functions are
expressible.

For Tau Language, this opens a different lane from ordinary Boolean filtering.
The symbolic object can be a formula tree, not only an action or policy choice.
That supports search for compact cost expressions, candidate invariants,
ranking functions, or explanation formulas, then routes only
certificate-carrying survivors into the verified side of the workflow.

The practical Tau-facing version is a sidecar, not native analytic Tau:

```text
Tau spec or trace data
  -> EML candidate formula search
  -> domain/spec filter
  -> checked strategy normalizer
  -> certificate-carrying formula manifest
```

The demo now writes that manifest:

```text
results/local/eml-tau-sidecar-manifest.json
```

Each accepted formula record contains its target, source expression,
normalized expression, real-log domain guard, interval-domain receipt, sample
and holdout errors, theorem names, and a boundary label.

TauLang-Experiments can consume the sidecar and emit positive-real scorecards
for accepted formulas, but that remains sidecar metadata. It is not native Tau
support for $\exp$ or $\ln$.

That sidecar can support concrete user-facing features:

- discover a compact score formula from traces,
- normalize a generated expression before a human reviews it,
- attach theorem names to an accepted simplification,
- reject formulas that fail the real-log domain guard,
- label unsupported formulas as unknown instead of silently trusting them,
- feed accepted formulas back into Tau tooling as metadata, thresholds, or
  explanation text.

<strong>Boundary.</strong>
This does not mean Tau Language itself has unrestricted real analysis,
$\exp$, or $\ln$. The safe feature is a checked formula-discovery and
simplification sidecar whose outputs can inform Tau specs and demos.

The upgraded sidecar uses qNS-style masks to record candidate routing:

```text
proposed, domain_valid, spec_candidate, proof_supported,
accepted, review, rejected
```

<strong>Standard reading.</strong>
Each mask is a finite bitset over the reported candidate list. Bit $i$ is set
in a mask exactly when candidate $i$ has the property named by that mask.

<strong>Plain English.</strong>
The manifest does not only list winners. It also records why candidates were
accepted, rejected, or routed to review.

The next tutorial turns this into the explicit proposal loop:
[Symbolic hypothesis generation with EML and qNS]({{ '/tutorials/symbolic-hypothesis-generation-with-eml-and-qns/' | relative_url }}).

## Part VII: next upgrades

The current demo is deliberately small.
The useful next upgrades are:

- add interval arithmetic, so a survivor is checked on ranges instead of only
  sample points,
- add randomized counterexample search, so false sampled identities are
  rejected faster,
- replace best-effort SymPy simplification with emitted certificates for more
  survivors,
- replace the finite `certNorm` equality-dispatch surface with a structurally
  recursive normalizer for a wider EML fragment,
- test local confluence of the current strategy-normalizer on a deliberately
  small fragment, or record counterexamples where uniqueness fails,
- build a Tau-adjacent demo that reads the sidecar manifest and uses accepted
  formula records as explanation metadata,
- prove termination and confluence only after emitted certificate traces are
  stable,
- add a neural proposer, so the candidate distribution is learned rather than
  assigned by an error-and-size heuristic,
- use the reproposal feedback packet to tell the proposer which rejected
  formulas failed and at which diagnostic points,
- add a qNS-style hard filter for domain, type, and specification constraints.

The important pattern is the same:

```text
propose many symbolic objects,
reject the invalid ones exactly,
renormalize the survivors,
then strengthen the checker until survivors become proof-grade.
```
