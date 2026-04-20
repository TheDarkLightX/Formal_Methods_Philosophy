---
title: "Symbolic hypothesis generation with EML and qNS"
layout: docs
kicker: Tutorial 51
description: "Turn model-proposed formula trees into checked symbolic hypotheses using qNS masks, counterexample diagnostics, and proof-backed EML receipts."
---

This tutorial connects the two previous experiments.
Tutorial 49 used a qNS Boolean-algebra carrier to filter candidate atoms.
Tutorial 50 used EML trees as a tiny formula language.
Here the two ideas are combined:

```text
untrusted formula proposal
  -> qNS symbolic masks
  -> counterexample diagnostics
  -> proof-backed survivor manifest
```

The local command is:

```bash
python3 scripts/run_eml_neurosymbolic_loop_demo.py \
  --candidate-json experiments/eml_symbolic_hypothesis_fixtures/llm_candidates_v1.json
```

To create a proposal prompt and validate a returned candidate file, run:

```bash
python3 scripts/generate_eml_llm_proposal_packet.py \
  --llm-output experiments/eml_symbolic_hypothesis_fixtures/llm_candidates_v1.json
```

After one checked run, the feedback packet can condition the next prompt:

```bash
python3 scripts/generate_eml_llm_proposal_packet.py \
  --feedback-json results/local/eml-reproposal-feedback-packet.json \
  --llm-output experiments/eml_symbolic_hypothesis_fixtures/llm_candidates_v2_feedback.json \
  --prompt-out results/local/eml-llm-reproposal-prompt.md \
  --candidate-out results/local/eml-llm-reproposals.json \
  --validation-out results/local/eml-llm-reproposal-validation.json
```

It writes:

```text
results/local/eml-neurosymbolic-loop-demo.json
results/local/eml-tau-sidecar-manifest.json
results/local/eml-reproposal-feedback-packet.json
results/local/eml-llm-proposal-prompt.md
results/local/eml-llm-proposal-validation.json
```

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Scope</p>
  <p>This is a symbolic-hypothesis scaffold, not native analytic Tau semantics. External proposals are treated as untrusted input. A formula is promoted only through explicit masks, bounded checks, and proof receipt metadata.</p>
</div>

## Part 0: the adaptive memory demo

The TauLang-Experiments repo now has a runnable memory demo for this loop.
The public repo is:

- [TheDarkLightX/TauLang-Experiments](https://github.com/TheDarkLightX/TauLang-Experiments)

The default path is model-free, so it can be reproduced without a local LLM:

```bash
./scripts/run_eml_qns_llm_memory_demo.sh --skip-setup-patch
```

The local-model path uses an installed Ollama model as the untrusted proposer:

```bash
./scripts/run_eml_qns_llm_memory_demo.sh \
  --skip-setup-patch \
  --live-ollama \
  --model llama3.2:3b
```

In the local smoke test, `llama3.2:3b` produced five EML proposals. All five
parsed. Three were promoted by the Tau `qns8` gate, two were routed to review,
and three memory slots were updated.

The reproducible fixture path currently reports:

```text
candidate_count = 5
parse_ok_count = 3
promoted_count = 3
review_count = 2
memory_updated_count = 3
rejected_count = 2
rejected_preserved_count = 2
qns_table_regression_ok = true
symbolic_tau_table_check_ok = true
```

The JSON receipt can be checked without rerunning Tau:

```bash
python3 scripts/verify_eml_qns_memory_receipt.py
```

The demo runner invokes that verifier automatically. The verifier also mutates
the receipt in memory and confirms that the broken rejected-row update is
rejected.

The table memory is a finite map:

$$
M : I \to B_{\mathrm{qNS}}.
$$

<strong>Standard reading.</strong>
The memory-state symbol $M$ denotes a function from memory slots in $I$ to qNS
Boolean-algebra values in $B_{\mathrm{qNS}}$.

<strong>Plain English.</strong>
Each memory slot stores an evidence mask.

The update uses the same pointwise revision shape as the table tutorial:

$$
M_{t+1}(i)
=
(G(i)\wedge A(i))\vee(G(i)'\wedge M_t(i)).
$$

<strong>Standard reading.</strong>
The update equation says that, for each memory slot $i$, the next memory value
is the join of two pieces: the replacement value $A(i)$ restricted by guard
$G(i)$, and the old memory value $M_t(i)$ restricted by the prime of $G(i)$.

<strong>Plain English.</strong>
Accepted evidence overwrites the selected slot. Rejected or review-routed
evidence leaves the old slot unchanged.

<strong>Boundary.</strong>
This is a checked bounded witness for an MPRD-style loop: propose, check,
filter, and remember. It is not a general theorem that every model proposal is
good, not native analytic Tau semantics, and not full unrestricted TABA tables.
The current memory demo uses Tau qNS evidence functions and then performs the
memory update through a named Tau definition whose body is direct `qns8` table
syntax:

```text
memory_revise_qns8(old, guard, replacement) :=
  table { when guard => replacement; else => old }
```

The result artifact records the exact named call and the equivalent direct
table expression for every candidate. The harness also runs `qns8` table
regressions for top guard, bottom guard, and partial guard cases. The companion
check uses table syntax over symbolic `tau` values to verify the same pointwise
revision shape.

## Part I: the object being searched

The hypothesis language is still the EML grammar:

$$
T ::= x \mid 1 \mid \operatorname{eml}(T,T),
\qquad
\operatorname{eml}(a,b)=\exp(a)-\ln(b).
$$

<strong>Standard reading.</strong>
A tree $T$ is either the variable $x$, the constant $1$, or an EML node whose
left and right children are trees. The value of $\operatorname{eml}(a,b)$ is
the exponential of $a$ minus the natural logarithm of $b$.

<strong>Plain English.</strong>
The search space is a formula forest built from one variable, one constant,
and one operation.

<strong>Trap.</strong>
In the real-valued demo, every logarithm argument must be positive. A proposed
tree can be grammatically valid and still fail the real-domain guard.

## Part II: qNS as candidate routing

For formula trees, the hard-filter loop is:

$$
q_{\mathrm{NS}}(T\mid D)
\propto
q_{\mathrm{N}}(T\mid D)\,
\chi_{\mathrm{parse}}(T)\,
\chi_{\mathrm{domain}}(T,D)\,
\chi_{\mathrm{spec}}(T,D).
$$

<strong>Standard reading.</strong>
The filtered proposal weight for tree $T$ given data $D$ is proportional to
the neural probability of $T$ given $D$, multiplied by three indicator
functions: the parse indicator of $T$, the domain indicator of $T$ on $D$, and
the specification indicator of $T$ on $D$.

<strong>Plain English.</strong>
A model may propose a formula, but the filter deletes it if it is outside the
grammar, invalid on the domain, or inconsistent with the checked examples.

<strong>Trap.</strong>
The formula does not say that the model is trusted. It says that model mass is
conditioned by symbolic gates.

The sidecar records those gates as finite masks:

```text
proposed
domain_valid
spec_candidate
proof_supported
accepted
review
rejected
```

<strong>Standard reading.</strong>
Each mask is a bitset over the reported candidate list. Candidate $i$ belongs
to a mask exactly when bit $i$ is set in that mask.

<strong>Plain English.</strong>
The report keeps the routing decision visible. A candidate can be rejected,
accepted, or sent to human/proof review.

## Part III: the LLM proposer surface

The proposal-packet script writes a prompt with the grammar, target list, real
domain boundary, and required JSON schema. The demo then accepts a JSON proposal
file:

```json
{
  "schema": "eml_candidate_proposals_v1",
  "candidates": [
    {"target": "exp(x)", "origin": "llm_fixture", "expr": "eml(x,1)"},
    {"target": "ln(x)", "origin": "llm_fixture", "expr": "eml(x,eml(eml(x,x),1))"}
  ]
}
```

The parser accepts only:

```text
x
1
eml(T,T)
```

So this proposal is rejected:

```text
eml(x,0)
```

The reason is not that it is mathematically useless. The reason is narrower:
`0` is not a terminal in this demo grammar.

<strong>Boundary.</strong>
This is intentionally strict. The point of the file surface is to show how an
LLM can propose formulas without gaining authority over the checker.

## Part IV: counterexample diagnostics

For a target function $f$ and tree $T$, the sample error is:

$$
\operatorname{MSE}(T,f)
=
\frac{1}{|G|}
\sum_{x\in G}(T(x)-f(x))^2.
$$

<strong>Standard reading.</strong>
The mean-squared error $\operatorname{MSE}(T,f)$ is the average, over sample
points $x$ in $G$, of the squared difference between the value of tree $T$ at
$x$ and the value of target function $f$ at $x$.

<strong>Plain English.</strong>
The checker measures how badly the formula misses the target on the sample
grid.

The demo also records counterexample diagnostics for rejected candidates.
For example, a candidate may fail because evaluation reaches a logarithm of a
non-positive value, or because a holdout point produces a large value error.
In the current bounded run, those diagnostic points are added to the active
sample grid before the final survivor list is emitted.

The same diagnostics are also emitted as a reproposal feedback packet:

```text
results/local/eml-reproposal-feedback-packet.json
```

That packet is meant for the next proposer round. It lists accepted formulas,
rejected formulas, diagnostic points, and the constraints the next proposal
must respect.

<strong>Boundary.</strong>
The feedback packet is not proof evidence. It is steering information. A new
candidate still has to pass parsing, qNS masks, domain checks, sampled checks,
and proof-receipt checks.

In the deterministic second-round fixture, the malformed proposal count drops
from $1$ to $0$. The accepted formula set stays the same: one expression for
$\exp(x)$ and two expressions for $\ln(x)$.

<strong>Standard reading.</strong>
The comparison says that the second fixture has zero parse rejections and the
same accepted source-expression set as the first fixture.

<strong>Plain English.</strong>
The feedback packet improved proposal hygiene in this bounded test, but it did
not discover a new accepted formula.

There is also a flagged identity-target extension:

```bash
python3 scripts/run_eml_neurosymbolic_loop_demo.py \
  --include-identity-target \
  --candidate-json results/local/eml-identity-proposals.json \
  --out results/local/eml-neurosymbolic-loop-demo-identity.json \
  --sidecar-out results/local/eml-tau-sidecar-manifest-identity.json \
  --feedback-out results/local/eml-reproposal-feedback-packet-identity.json
```

The accepted composed identity tree is:

$$
\operatorname{eml}\bigl(1,\operatorname{eml}(\operatorname{eml}(1,\operatorname{eml}(x,1)),1)\bigr).
$$

<strong>Standard reading.</strong>
The displayed tree is an EML node with left child $1$ and right child
$\operatorname{eml}(\operatorname{eml}(1,\operatorname{eml}(x,1)),1)$. Under
the abstract EML laws used by the Lean packet, it denotes $\ln(\exp(x))$, and
therefore denotes $x$.

<strong>Plain English.</strong>
The loop can now certify a composed formula, not just direct formulas for
$\exp(x)$ and $\ln(x)$.

<strong>Boundary.</strong>
This is still abstract-law evidence. It is not a theorem about all complex
branch choices for logarithm, and it is not native Tau analytic semantics.

The composition extension adds the target $\exp(\exp(x))$:

```bash
python3 scripts/run_eml_neurosymbolic_loop_demo.py \
  --include-identity-target \
  --include-exp-exp-target \
  --candidate-json results/local/eml-composition-proposals.json \
  --out results/local/eml-neurosymbolic-loop-demo-composition.json \
  --sidecar-out results/local/eml-tau-sidecar-manifest-composition.json \
  --feedback-out results/local/eml-reproposal-feedback-packet-composition.json
```

Its accepted tree is:

$$
\operatorname{eml}(\operatorname{eml}(x,1),1).
$$

<strong>Standard reading.</strong>
The displayed tree is an EML node with left child $\operatorname{eml}(x,1)$
and right child $1$. Under the abstract EML laws used by the Lean packet, it
denotes $\exp(\exp(x))$.

<strong>Plain English.</strong>
The loop can now promote a formula built by placing a known survivor inside a
larger checked context.

<strong>Boundary.</strong>
This is a context-lifted survivor for one target. It is not arbitrary symbolic
regression, not native Tau analytic semantics, and not a complete EML
normalizer.

The next context-library fixture adds a second proved constructor:

$$
\operatorname{WrapLog}(T)=
\operatorname{eml}\bigl(1,\operatorname{eml}(\operatorname{eml}(1,T),1)\bigr).
$$

Together with $\operatorname{WrapExp}(T)=\operatorname{eml}(T,1)$, it accepts:

$$
\operatorname{WrapLog}(\operatorname{WrapExp}(\operatorname{WrapExp}(x)))
=
\exp(x).
$$

<strong>Standard reading.</strong>
The left side denotes the result of applying the exponential wrapper to $x$,
applying the exponential wrapper again, and then applying the logarithm wrapper.
Under the abstract law $\ln(\exp(a))=a$, the resulting denotation is
$\exp(x)$.

<strong>Plain English.</strong>
This is the first small constructor library for the EML proposal loop. The
model can propose a larger formula, but the promotion still depends on named
checked constructors and receipt metadata.

That suggests a safer proposal surface than raw strings:

```text
Var
WrapExp(plan)
WrapLog(plan)
```

The constructor-plan compiler turns those plans into ordinary EML candidate
JSON. The qNS loop then treats the compiled formula exactly like any other
proposal.

<strong>Standard reading.</strong>
A constructor plan is generated by the grammar above. The variable constructor
denotes the base variable, the exponential-wrapper constructor denotes the
result of applying the checked exponential context constructor to the subplan,
and the logarithm-wrapper constructor denotes the result of applying the
checked logarithm context constructor to the subplan.

<strong>Plain English.</strong>
The model can work in a smaller language where every constructor has a named
semantic law. That reduces proposal fragility without weakening the checker.

<strong>Boundary.</strong>
Constructor plans do not bypass verification. They only produce candidate EML
strings with theorem-lineage metadata.

The plan layer also has a small budget gate:

```text
depth <= 3
WrapExp count <= 2
WrapLog count <= 1
```

The budgeted fixture accepts four plans and rejects three:

```text
accepted: direct exp, exp-exp, log-exp identity, log-exp-exp
rejected: over-depth plan, unsupported WrapSin, missing WrapLog argument
```

<strong>Standard reading.</strong>
The budget gate accepts a constructor plan only if it satisfies all three
numeric bounds above and uses only constructors in the proved constructor set.

<strong>Plain English.</strong>
The model can still propose bad plans, but bad plans are caught before they
become raw EML candidates.

<strong>Boundary.</strong>
The budget gate is proposal hygiene. Passing it does not mean the formula is
correct.

The obligation audit then joins constructor plans to sidecar evidence:

```text
constructor plan obligation
  -> matching interval-domain entry
  -> discharged or failed audit row
```

In the current run, four accepted plans produce eight obligations, and all
eight are discharged by sidecar interval evidence.

<strong>Standard reading.</strong>
The audit succeeds exactly when every recorded constructor obligation has a
matching sidecar interval check and no matched interval violates the local
guard condition.

<strong>Plain English.</strong>
The audit turns a hidden assumption into a visible checklist.

<strong>Boundary.</strong>
The checklist is bounded and local to this demo interval. It is not a global
real-analysis proof.

The final promotion rule is:

```text
promote iff qNS accepted, proof accepted, and obligation audit ok
```

A negative test tampers one audit row. The manifest then routes that candidate
to review instead of promotion.

<strong>Standard reading.</strong>
The promotion rule says that a constructor-plan candidate receives promoted
status exactly when three recorded predicates all hold: the qNS gate accepts
the candidate, the proof metadata accepts the candidate, and the obligation
audit succeeds.

<strong>Plain English.</strong>
The loop now has a fail-closed final gate. If any evidence layer breaks, the
candidate is not promoted.

Finally, the constructor-plan feedback packet summarizes the next proposer
state:

```text
promoted_count = 4
review_count = 0
rejected_plan_count = 3
```

<strong>Standard reading.</strong>
The packet records four promoted constructor plans, no promoted-plan review
rows, and three rejected constructor plans from the budget and syntax layer.

<strong>Plain English.</strong>
The next round starts with a compact map of what worked, what failed, and which
rules must not be broken.

<strong>Boundary.</strong>
The feedback packet is not trusted by itself. Every future plan must rerun all
gates.

The second feedback-conditioned constructor-plan fixture gives the first
measured loop improvement:

```text
baseline rejected_plan_count = 3
second_round rejected_plan_count = 0
baseline promoted_count = 4
second_round promoted_count = 5
```

It adds this promoted plan:

$$
\operatorname{WrapLog}(\operatorname{Var})
\rightsquigarrow
\operatorname{eml}(1,\operatorname{eml}(\operatorname{eml}(1,x),1)).
$$

<strong>Standard reading.</strong>
The constructor plan $\operatorname{WrapLog}(\operatorname{Var})$ compiles to
the EML tree
$\operatorname{eml}(1,\operatorname{eml}(\operatorname{eml}(1,x),1))$ and is
promoted for the target $\ln(x)$ after the parser, qNS masks, proof metadata,
and obligation audit all accept it.

<strong>Plain English.</strong>
The feedback packet helped the next fixture avoid the three known bad plan
shapes and include the missing direct-log plan.

<strong>Boundary.</strong>
This is not evidence that arbitrary model feedback will improve. It is a
checked second-round fixture over the current constructor language.

The loop also has a constructor-plan handoff contract now. The latest feedback
can be rendered as a JSON-only prompt, and the returned plan file can be audited
before compilation:

```text
positive fixture: 5 compliant, 0 noncompliant
negative fixture: 1 compliant, 3 noncompliant
```

<strong>Standard reading.</strong>
The compliance audit accepts a proposal row exactly when the row uses only
allowed constructor operations, satisfies the active budget, and supplies every
required constructor argument.

<strong>Plain English.</strong>
Bad proposal shapes can be filtered before the EML parser and proof sidecar are
even invoked.

<strong>Boundary.</strong>
This audit is only proposal hygiene. It does not prove that a formula is true,
useful, or semantically equal to a target.

The quarantine-first handoff runner then uses that audit before compilation:

```text
positive handoff: 5 input rows, 0 quarantined, 5 promoted
negative handoff: 4 input rows, 3 quarantined, 1 promoted
```

<strong>Standard reading.</strong>
The negative handoff run partitions the four proposal rows into three
noncompliant rows and one compliant row. Only the compliant row is compiled and
sent through qNS, proof metadata, obligation audit, and promotion.

<strong>Plain English.</strong>
A bad proposal file no longer has to be all-or-nothing. The loop can quarantine
the bad rows and still test the row that obeys the contract.

<strong>Boundary.</strong>
Quarantine is not semantic proof. It is the safety wrapper around untrusted
proposal input.

The deeper compression tactic is to decompose a plan into its constructor spine
and remove checked equivalence pairs:

$$
\operatorname{WrapLog}(\operatorname{WrapExp}(T)) \leadsto T.
$$

<strong>Standard reading.</strong>
The rewrite applies only to a constructor-plan node whose outer constructor is
$\operatorname{WrapLog}$ and whose child node has outer constructor
$\operatorname{WrapExp}$. The replacement is the inner subplan $T$.

<strong>Plain English.</strong>
The loop removes a log-after-exp wrapper before asking the rest of the checker
to spend work on it.

The current equivalence-repair fixture reports:

```text
changed rows = 4 / 4
total depth = 12 -> 4
promoted rows after v706 = 4
review rows after v706 = 0
```

<strong>Standard reading.</strong>
The normalizer changes all four fixture rows. After normalization and rerunning
the handoff gates with the direct identity receipt available, all four
normalized rows are promoted.

<strong>Trap.</strong>
The earlier v705 run routed the direct `Var` row to review because the proof
sidecar lacked a direct receipt for `Var` as target $x$. v706 closes that
interface gap. This does not make the equivalence-repair pass complete.

<strong>Boundary.</strong>
This equivalence-repair pass is a bounded repair normalizer, not a complete equality
procedure for EML trees.

The opposite cancellation is guarded:

$$
\operatorname{WrapExp}(\operatorname{WrapLog}(T)) \leadsto T
\quad\text{only under an explicit converse-inverse law surface.}
$$

<strong>Standard reading.</strong>
The constructor-plan normalizer may replace
$\operatorname{WrapExp}(\operatorname{WrapLog}(T))$ by $T$ only if the row
carries the semantic premise

$$
\forall a,\quad \exp(\log(a))=a.
$$

For the real-valued demo interval, it also carries the local domain obligation
that $\llbracket T\rrbracket$ stays positive.

<strong>Plain English.</strong>
This is checked equivalence collapse with a receipt. The loop removes the
redundant shape, but it keeps the law and domain conditions that make the
removal valid.

The guarded fixture reports:

```text
changed rows = 3 / 3
total depth = 8 -> 2
residual obligations = 2
promoted rows = 2
review rows = 1
```

<strong>Trap.</strong>
The review row is intentional. For target $\ln(x)$, the residual value interval
crosses below zero on $I=[0.25,3]$, so the guarded equivalence obligation is not
discharged.

The law-surface split is now explicit. The base EML laws include:

$$
\log(\exp(a))=a.
$$

The stronger bidirectional law surface adds:

$$
\forall a,\quad \exp(\log(a))=a.
$$

<strong>Standard reading.</strong>
The base law states that applying $\log$ after $\exp$ returns $a$. The stronger
law surface additionally states that applying $\exp$ after $\log$ returns $a$
for every $a$ in the active semantic model.

<strong>Plain English.</strong>
Log-after-exp is part of the base proof packet. Exp-after-log is not free. The
demo promotes candidates using that direction only when the stronger law
surface is selected explicitly.

<strong>Boundary.</strong>
The stronger law surface is an abstract law surface. It is not, by itself, a
proof about real numbers, complex branches, or native Tau analytic semantics.

The stronger proof-search compression is quotienting by the normalized
representative:

$$
P \sim Q
\quad\Longleftrightarrow\quad
\operatorname{target}(P)=\operatorname{target}(Q)
\ \wedge\
\operatorname{normalize}(P)=\operatorname{normalize}(Q).
$$

<strong>Standard reading.</strong>
Plans $P$ and $Q$ are equivalent under this quotient exactly when they have the
same target and their normalized constructor plans are equal.

<strong>Plain English.</strong>
The loop can prove or audit one canonical shape and attach the local rewrite
history for every syntactic variant.

The quotient fixture reports:

```text
rows = 9
classes = 3
quotient reduction = 6
total depth = 18 -> 6
promoted members = 7
review members = 2
```

<strong>Trap.</strong>
The quotient is not a shortcut around obligations. A member whose residual
obligation fails stays in review even if another member of the same canonical
class promotes.

The machine-readable version is a local-obligation graph:

$$
m \to \operatorname{class}(m),
\qquad
m \to o
\quad\text{for every}\quad
o\in\operatorname{Obl}(m).
$$

<strong>Standard reading.</strong>
The member node $m$ has a dependency edge to its canonical class and a
dependency edge to each local obligation $o$ in the obligation set of $m$.

<strong>Plain English.</strong>
The graph shows exactly what must be checked before a candidate can be reused
through a quotient class.

The current graph has 21 nodes and 18 dependency edges. It reduces nine member
cases to three canonical proof targets, while keeping six rewrite obligations
and three residual obligations visible.

The same quotient can be used as a representative-selection constraint:

$$
|\operatorname{search\ tasks}|
\quad:\quad
9 \longrightarrow 3.
$$

<strong>Standard reading.</strong>
The number of search tasks is reduced from nine member cases to three selected
representatives.

<strong>Plain English.</strong>
Do not ask the prover or checker to solve the same shape nine times.

The selected representative set passes the downstream handoff with three
promoted rows and zero review rows.

But this is a coverage claim, not an all-member claim:

$$
\operatorname{HiddenBlocked}=2.
$$

<strong>Standard reading.</strong>
The number of pruned members whose full quotient evidence routes them to review
is two.

<strong>Plain English.</strong>
Two discarded variants were not safe. They were discarded because a cleaner
representative covered the class, not because the variants themselves passed.

That audit is now fed back into the proposer prompt. The prompt names the
covered classes:

```text
x       -> Var
exp(x)  -> WrapExp(Var)
ln(x)   -> WrapLog(Var)
```

It also names the blocked variants around $\ln(x)$, so the next proposal round
does not keep spending budget on the same failed equivalent copies.

The loop then audits proposal behavior:

$$
\operatorname{Waste}(P)
=
\operatorname{CoveredRepeats}(P)
+
\operatorname{HiddenBlockedRepeats}(P).
$$

<strong>Standard reading.</strong>
The waste score of a proposal file $P$ is the sum of the number of proposal
rows that repeat already covered classes and the number of proposal rows that
repeat hidden blocked variants.

<strong>Plain English.</strong>
Waste means spending proposal budget on shapes the loop already knows not to
ask for in coverage mode.

In the deterministic comparison, the quotient-unaware fixture has waste
$6+2=8$. The quotient-aware fixture has waste $0+0=0$ and contributes one
novel class that promotes through the full handoff.

The sidecar also records a conservative interval-domain receipt for accepted
formulas over the bounded demo interval:

$$
I=[0.25,3].
$$

<strong>Standard reading.</strong>
The interval symbol $I$ denotes the closed real interval whose lower endpoint
is $0.25$ and whose upper endpoint is $3$.

<strong>Plain English.</strong>
The interval-domain receipt checks whether each real-logarithm argument stays
positive throughout $I$ under the current interval evaluator. This is stronger
than "did the formula work on four points?", and it still remains a bounded
claim.

<strong>Trap.</strong>
These diagnostics are not a completeness proof. They are evidence for why a
bounded candidate was rejected and useful input for the next proposal round.

## Part V: law surfaces and the bounded corpus

The law-surface demo artifact is:

```text
assets/data/eml_law_surface_demo.json
```

The companion visualization is:

[EML Law-Surface Demo Lab]({{ '/eml_law_surface_demo_lab.html' | relative_url }})

The JSON artifact is included directly. The longer research-cycle generator is
intentionally not part of the beginner reproduction path.

The bounded corpus result is:

```text
raw constructor plans               = 96
changed by normalization            = 72
target-consistent normalized rows   = 22
base-law promotions                 = 13
base-law review rows                = 9
BiLaws promotions                   = 20
BiLaws review rows                  = 2
```

The semantic switch is:

$$
\mathcal{L}_{\mathrm{bi}}
=
\mathcal{L}_{\mathrm{base}}
\cup
\{\forall a,\ \exp(\log(a))=a\}.
$$

<strong>Standard reading.</strong>
The bidirectional law surface $\mathcal{L}_{\mathrm{bi}}$ is the union of the
base EML law surface and one additional law: for every admissible value $a$ in
the active semantic model, applying $\log$ to $a$ and then applying $\exp$
returns $a$.

<strong>Plain English.</strong>
The stronger law surface unlocks seven additional promotions in this bounded
corpus, but it does not erase the remaining real-domain failures.

The final two review rows are still blocked because a positive-value interval
obligation fails. In both cases, the relevant interval crosses below zero:

$$
[-1.3862943611198904,\ 1.0986122886681098].
$$

<strong>Standard reading.</strong>
The interval displayed above has a negative lower endpoint. Therefore it does
not satisfy the local obligation that the value interval must be strictly
positive.

<strong>Plain English.</strong>
The stronger law surface helps with symbolic inverse laws. It does not make a
logarithm argument positive when the interval evidence says otherwise.

<strong>Boundary.</strong>
This is a bounded corpus result. It is ready as a demo of proof-hygienic
symbolic hypothesis generation, not as a complete symbolic-regression engine.

## Part VI: what gets promoted

The current promoted formulas are:

$$
\operatorname{eml}(x,1)
$$

for $\exp(x)$,

$$
\operatorname{eml}\bigl(1,
  \operatorname{eml}(
    \operatorname{eml}(1,\operatorname{eml}(\operatorname{eml}(x,1),1)),
    1
  )
\bigr)
$$

also for $\exp(x)$,

$$
\operatorname{eml}(\operatorname{eml}(x,1),1)
$$

for $\exp(\exp(x))$, and

$$
\operatorname{eml}(1,\operatorname{eml}(\operatorname{eml}(1,x),1)),
\qquad
\operatorname{eml}(x,\operatorname{eml}(\operatorname{eml}(x,x),1))
$$

for $\ln(x)$.

The manifest marks them as accepted because they pass the bounded checks and
carry proof-backed normalizer metadata:

```text
normalize_sound
normalize_stable
normalize_idempotent
normalize_certNorm_reaches
normalizeReceiptCanonZero_sound
```

<strong>Standard reading.</strong>
The soundness theorem says that an expression and its normalized expression
have the same evaluation. The stability theorem says that a normalized
expression has no further accepted rewrite step. The idempotence theorem says
that normalizing twice gives the same result as normalizing once. The
certificate-reachability theorem says that when the finite certificate checker
returns a normal form, the normalizer reaches the compiled expression of that
normal form. The canonical-zero receipt theorem says that the receipt-producing
normalizer preserves evaluation.

<strong>Plain English.</strong>
Accepted formulas are not just strings that looked good in a sample. They are
attached to named proof artifacts that explain what has actually been checked.

## Part VII: what this gives Tau tooling

The practical feature is not that Tau suddenly computes arbitrary exponentials
or logarithms. The practical feature is a safe sidecar lane:

```text
Tau trace or spec context
  -> proposed symbolic formula
  -> qNS filter masks
  -> proof-backed accepted record
  -> explanation, threshold, score, or invariant candidate
```

This can support:

- compact score formulas learned from traces,
- explanation formulas attached to solver output,
- candidate ranking functions for search,
- invariant or cost-model proposals that must pass symbolic filters,
- proof-review queues where unsupported formulas are labeled `review`, not
  silently accepted.

<strong>Boundary.</strong>
The current implementation is a sidecar and demo loop. TauLang-Experiments can
validate EML/qNS certificates, send finite evidence masks through Tau, and run a
table-memory update demo. Native Tau does not yet evaluate analytic EML
expressions as mathematical functions.

The Tau-facing public consumer lives in the experiment repo:

- [TheDarkLightX/TauLang-Experiments](https://github.com/TheDarkLightX/TauLang-Experiments)

```bash
cd TauLang-Experiments
./scripts/run_eml_qns_demo.sh --accept-tau-license
./scripts/run_eml_qns_llm_memory_demo.sh --skip-setup-patch
```

The first command checks certificate masks and tamper rejection. The second
command uses Tau `qns8` gates and a named table-backed memory revision:

```text
memory_revise_qns8(old, guard, replacement) :=
  table { when guard => replacement; else => old }
```

<strong>Boundary.</strong>
This does not mean Tau evaluated $\exp$, $\ln$, or EML trees. It means accepted
sidecar evidence was converted into finite qNS masks, passed through Tau, and
used to decide whether table memory should update or remain unchanged.

## Part VIII: bounded symbolic regression

The next artifact moves one step closer to regression:

```text
assets/data/eml_bounded_symbolic_regression.json
```

It is generated by:

```bash
python3 scripts/run_eml_bounded_symbolic_regression.py
```

This script does not start from hand-written candidate proposals. It enumerates
the bounded EML corpus and asks which tree best fits a small train-and-holdout
dataset.

The bounded search surface is:

$$
\mathcal{T}_{\le d}
=
\{T \mid \operatorname{depth}(T)\le d\}.
$$

<strong>Standard reading.</strong>
The bounded tree set $\mathcal{T}_{\le d}$ denotes the set of all EML trees
whose depth is less than or equal to $d$.

<strong>Plain English.</strong>
The search only ranges over EML trees up to the chosen depth bound.

For each target dataset $D$, the selected formula is:

$$
T^\star
=
\min_{\prec}
\{T\in\mathcal{T}_{\le d}
  \mid
  \operatorname{err}_{\mathrm{train}}(T,D)\le\varepsilon
  \wedge
  \operatorname{err}_{\mathrm{holdout}}(T,D)\le\varepsilon
\}.
$$

<strong>Standard reading.</strong>
The selected tree $T^\star$ is the $\prec$-least tree among the trees $T$ in
$\mathcal{T}_{\le d}$ whose training error on $D$ is at most $\varepsilon$ and
whose holdout error on $D$ is at most $\varepsilon$. Here $\prec$ is the
declared bounded-corpus ordering used to break ties.

<strong>Plain English.</strong>
Among the bounded trees that fit both the training points and the holdout
points, choose the smallest one under the declared ordering.

The current run uses $d=3$, $\varepsilon=10^{-9}$, and a corpus of $1446$
trees. It finds minimal bounded fits for:

| Target | Best bounded fit |
|---|---|
| $x$ | `x` |
| $\exp(x)$ | `eml(x,1)` |
| $\ln(x)$ | `eml(1,eml(eml(1,x),1))` |
| $\exp(\exp(x))$ | `eml(eml(x,1),1)` |

The checked summary is:

```text
target_count = 4
all_targets_fit = true
all_best_minimal = true
proof_receipt_accept_count = 4
symbolic_identity_accept_count = 4
```

<strong>Standard reading.</strong>
The artifact has four target datasets, every target has at least one bounded
fit, every selected best fit is minimal within the bounded corpus order, four
selected fits have accepted proof receipts, and four selected fits pass the
symbolic identity check.

<strong>Plain English.</strong>
This is a small but real regression loop: enumerate formulas, fit data, choose
minimal survivors, then attach proof metadata where the known proof surface
supports the survivor.

<strong>Trap.</strong>
This is not full symbolic regression. It is bounded enumerative regression over
$\mathcal{T}_{\le 3}$. It does not prove that no deeper formula fits, it does
not reproduce the EML paper's gradient search, and it does not make Tau a
native analytic solver.

## Part IX: noisy regression certificates

Exact-fit demos are useful, but practical regression often has noisy data. The
next artifact is:

```text
assets/data/eml_noisy_regression_certificates.json
```

It is generated by:

```bash
python3 scripts/run_eml_noisy_regression_certificates.py
```

For noisy data, the selected tree is the lexicographic minimizer:

$$
T^\star
=
\operatorname*{arg\,min}_{T\in\mathcal{T}_{\le d}}
\bigl(
\operatorname{MSE}_{\mathrm{noisy}}(T),
\operatorname{MSE}_{\mathrm{holdout}}(T),
|T|,
\operatorname{depth}(T),
\operatorname{repr}(T)
\bigr).
$$

<strong>Standard reading.</strong>
The selected tree $T^\star$ is an element of $\mathcal{T}_{\le d}$ that
minimizes the displayed ordered tuple: noisy training mean-squared error,
holdout mean-squared error, tree size, tree depth, and tree representation.

<strong>Plain English.</strong>
First fit the noisy training data as well as possible. If there is a tie, prefer
better holdout behavior, then the smaller and simpler expression.

The residual certificate records:

$$
r_i(T)=T(x_i)-y_i.
$$

<strong>Standard reading.</strong>
The residual symbol $r_i(T)$ denotes the signed residual of tree $T$ at sample
index $i$: the value computed by $T$ at input $x_i$ minus the observed value
$y_i$.

<strong>Plain English.</strong>
The report does not only name a winner. It records the signed error at each
checked point.

The current noisy run uses the same depth-3 corpus of $1446$ trees and three
noisy targets:

| Noisy target | Selected formula |
|---|---|
| noisy $\exp(x)$ | `eml(x,1)` |
| noisy $\ln(x)$ | `eml(1,eml(eml(1,x),1))` |
| noisy $\exp(\exp(x))$ | `eml(eml(x,1),1)` |

The checked summary is:

```text
target_count = 3
winner_count = 3
proof_receipt_accept_count = 3
symbolic_identity_accept_count = 3
```

<strong>Standard reading.</strong>
The artifact has three noisy target datasets, three selected winners, three
accepted proof receipts for the selected winners, and three selected winners
whose symbolic identity checks are accepted.

<strong>Plain English.</strong>
The bounded search recovers the compact clean formulas even when the training
values are perturbed by small deterministic noise.

<strong>Trap.</strong>
This is still not statistical learning theory. The certificate proves what won
inside the declared finite corpus and records its residuals. It does not prove
that the winner is the true data-generating law.

## Part X: regression winners as qNS certificates

The next bridge turns regression winners into qNS-style certificate masks:

```text
assets/data/eml_regression_certificate_manifest.json
```

It is generated by:

```bash
python3 scripts/generate_eml_regression_certificate_manifest.py \
  --tau-bin external/tau-lang-qns-ba/build-Release/tau
```

Before running this command directly, build the patched qNS Tau checkout from
Tutorial 49:

```bash
./scripts/run_qns_semantic_ba_demos.sh
```

Each accepted regression winner must carry seven finite evidence bits:

| Bit | Meaning |
|---|---|
| `grammar_bounded` | the formula came from the declared bounded EML corpus |
| `fit_passed` | the source artifact's fit objective passed |
| `holdout_passed` | the source artifact's holdout objective passed |
| `minimality_scoped` | minimality or rank is scoped to the declared bounded corpus |
| `proof_receipt` | the selected formula has accepted proof metadata |
| `symbolic_identity` | the selected formula passed symbolic identity checking |
| `residual_certificate` | the source artifact records error or residual data |

The promotion condition is:

$$
M_{\mathrm{accepted}}\wedge M_{\mathrm{required}}
=
M_{\mathrm{required}}
\quad\wedge\quad
M_{\mathrm{review}}=0.
$$

<strong>Standard reading.</strong>
The meet of the accepted mask and the required mask is equal to the required
mask, and the review mask is zero. Equivalently, every required evidence bit is
present in the accepted mask, and no review blocker bit is present.

<strong>Plain English.</strong>
Every required evidence bit must be present, and no review blocker may remain.

The checked manifest summary is:

```text
certificate_count = 7
promoted_count = 7
review_count = 0
tau_blocker_count = 0
exact_source_count = 4
noisy_source_count = 3
```

<strong>Standard reading.</strong>
The manifest contains seven regression certificates, seven promoted
certificates, zero certificates routed to review, zero Tau blocker masks, four
certificates from the exact bounded source, and three certificates from the
noisy bounded source.

<strong>Plain English.</strong>
All current exact and noisy EML regression winners can be consumed through the
same finite qNS evidence-mask interface.

<strong>Trap.</strong>
The qNS certificate does not strengthen the underlying regression theorem. It
only prevents a winner from being promoted unless the declared evidence fields
are present and Tau agrees that the finite evidence mask is complete.

## Part XI: fail-closed regression certificates

The happy path is not enough. The certificate wrapper also needs negative
tests. The fail-closed artifact is:

```text
assets/data/eml_regression_certificate_failclosed.json
```

It is generated by:

```bash
python3 scripts/verify_eml_regression_certificate_failclosed.py \
  --tau-bin external/tau-lang-qns-ba/build-Release/tau
```

This uses the same patched qNS Tau binary built by
`scripts/run_qns_semantic_ba_demos.sh`.

The verifier accepts a row only when:

$$
H_{\mathrm{row}}=H_{\mathrm{source}}
\quad\wedge\quad
M_{\mathrm{accepted}}\wedge M_{\mathrm{required}}=M_{\mathrm{required}}
\quad\wedge\quad
M_{\mathrm{review}}=0.
$$

<strong>Standard reading.</strong>
The row hash $H_{\mathrm{row}}$ is equal to the current source-artifact hash
$H_{\mathrm{source}}$, the bitwise conjunction of the accepted mask and the
required mask is equal to the required mask, and the review mask is zero.

<strong>Plain English.</strong>
The certificate must point to the current source artifact, include every
required evidence bit, and carry no review blocker.

The negative corpus mutates each valid certificate in four ways:

```text
drop proof_receipt
drop residual_certificate
force review_required
stale source hash
```

The checked summary is:

```text
valid_count = 7
valid_promoted_count = 7
tampered_count = 28
tampered_rejected_count = 28
tau_rejected_count = 21
hash_rejected_count = 7
```

<strong>Standard reading.</strong>
The artifact contains seven valid rows, seven valid promoted rows, twenty-eight
tampered rows, twenty-eight rejected tampered rows, twenty-one tampered rows
rejected by the Tau mask check, and seven tampered rows rejected by the source
hash check.

<strong>Plain English.</strong>
The wrapper now has a negative test surface, not only a success path. Missing
proof bits, missing residual bits, review blockers, and stale source hashes do
not promote.

<strong>Trap.</strong>
This is not a cryptographic attestation system. The hash check is a local
artifact-integrity check, and it does not protect against a compromised verifier.

## Part XII: demo gallery

The tutorial now has one public gallery artifact:

```text
assets/data/eml_qns_demo_gallery.json
```

It separates the slow and fast parts of the experiment.

The slow lane is bounded EML regression. It searches a finite corpus and records
which formula wins under the declared objective.

The fast lane is Tau `qns8` certificate gating. It does not rediscover the
formula. It checks whether the returned certificate has the required evidence
bits and no blocker bits.

The negative lane is the fail-closed test corpus. It checks that tampered
certificates do not promote.

The current gallery summary is:

```text
slow_source_count = 2
fast_promoted_count = 7
negative_rejected_count = 28
```

<strong>Plain English.</strong>
This is the demo shape readers should remember: expensive search can happen
outside Tau, but the artifact that enters Tau is small, finite, auditable, and
rejected when required evidence is missing.

<strong>Trap.</strong>
The gallery does not add neural proposal generation. It shows the symbolic side
of the loop that a neural proposer would have to satisfy.

## Part XIII: next work

The next upgrades are deliberately concrete:

- strengthen the conservative interval checker into a richer range checker,
- add a richer domain type system for real, positive-real, and complex-branch
  assumptions,
- emit certificate traces for more discovered formulas,
- let a real LLM proposer write the JSON proposal file,
- use the reproposal feedback packet to drive a second external proposal round,
- promote only formulas whose proof receipt matches the intended use.

The method is:

```text
models propose;
symbolic gates decide;
proof artifacts promote;
counterexamples steer the next proposal.
```
