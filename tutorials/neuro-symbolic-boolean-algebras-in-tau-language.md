---
title: "Neuro-symbolic Boolean algebras in Tau Language"
layout: docs
kicker: Tutorial 49
description: "A Tau Language enhancement experiment: qns8, a finite Boolean-algebra carrier for exact symbolic filtering after neural candidate generation."
---

This tutorial describes a small Tau Language experiment for neuro-symbolic
programming: a model proposes candidates, and Tau performs an exact symbolic
filter over a finite audited menu.

The experiment adds a feature-gated Boolean-algebra carrier:

```text
qns8
```

`qns8` is the powerset Boolean algebra over eight audited atoms, represented as
an 8-bit mask. The same design could be widened to more atoms, but this demo
stays at eight.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Scope</p>
  <p>This is a community research experiment, not an official Tau Language feature. It adds one finite carrier (<code>qns8</code>) for exact symbolic filtering over an audited candidate universe. Neural scoring stays in the host program. The demo makes no correctness claim about atom extraction.</p>
</div>

Reference notes for the experiment live in:

- [TheDarkLightX/TauLang-Experiments](https://github.com/TheDarkLightX/TauLang-Experiments)
- [Neuro-symbolic Boolean algebras note](https://github.com/TheDarkLightX/TauLang-Experiments/blob/main/docs/neuro-symbolic-boolean-algebras.md)

This repo includes a local reproduction script:

```text
scripts/run_qns_semantic_ba_demos.sh
```

## Part I: the qNS split

The neuro-symbolic filtering equation is:

$$
q_{\mathrm{NS}}(c \mid x)
=
\frac{
q_{\mathrm{N}}(c \mid x)\,\chi_{\mathrm{S}}(c,x)
}{
\sum_{d\in C_x} q_{\mathrm{N}}(d \mid x)\,\chi_{\mathrm{S}}(d,x)
}.
$$

<strong>Standard reading.</strong>
$q_{\mathrm{NS}}(c \mid x)$ is
$q_{\mathrm{N}}(c \mid x)\chi_{\mathrm{S}}(c,x)$ divided by
$\sum_{d\in C_x} q_{\mathrm{N}}(d \mid x)\chi_{\mathrm{S}}(d,x)$.

<strong>Plain English.</strong>
The model ranks candidates. The symbolic layer deletes candidates that fail the
rules. The host renormalizes the scores of the candidates that remain.

<strong>Trap.</strong>
Tau is not being asked to produce the neural score. Tau checks the exact
Boolean filtering condition. The host program handles numerical scoring and
renormalization.

This is the central design boundary:

$$
\text{neural proposal}
\quad\longrightarrow\quad
\text{finite symbolic filter}
\quad\longrightarrow\quad
\text{renormalized survivors}.
$$

## Part II: the Boolean algebra

For a given input $x$, choose a finite audited candidate set $C_x$.
In the rest of the tutorial, write $U$ for this audited universe, so $U=C_x$.

The carrier is:

$$
B_x = \mathcal{P}(U).
$$

<strong>Standard reading.</strong>
$B_x=\mathcal{P}(U)$.

<strong>Plain English.</strong>
Each Boolean-algebra value is a set of candidates.

The Boolean operations are:

$$
0=\varnothing,\qquad
1=U,\qquad
A\wedge B=A\cap B,\qquad
A\vee B=A\cup B,\qquad
A'=U\setminus A.
$$

<strong>Standard reading.</strong>
$0=\varnothing$, $1=U$, $A\wedge B=A\cap B$, $A\vee B=A\cup B$, and
$A'=U\setminus A$.

<strong>Plain English.</strong>
Meet keeps candidates in both sets. Join keeps candidates in either set. Prime
keeps everything in the audited universe that is not in the set.

<strong>Trap.</strong>
The prime is relative to the finite audited universe $U$. It is not a
probability complement and not a model judgment.

In the Tau experiment, the subsets are stored as masks:

```text
qns8  : 8 audited atoms
```

This is why the implementation is useful. A symbolic candidate filter becomes
ordinary Boolean algebra over a finite audited menu.

## Part III: the candidate filter

The demo uses five regions:

| Symbol | Meaning |
|---|---|
| $U$ | audited universe |
| $N$ | candidates proposed by the neural layer |
| $A$ | candidates allowed by symbolic rules |
| $R$ | candidates requiring human review |
| $H$ | candidates hard-rejected by symbolic rules |

First define the proposed region:

$$
P := U\wedge N.
$$

<strong>Standard reading.</strong>
$P := U\wedge N$.

<strong>Plain English.</strong>
Only candidates inside the audited universe can be treated as proposed.

Then define the eligible region:

$$
E := U\wedge N\wedge A\wedge H'.
$$

<strong>Standard reading.</strong>
$E := U\wedge N\wedge A\wedge H'$.

<strong>Plain English.</strong>
A candidate is eligible exactly when it is audited, proposed, allowed, and not
hard-rejected.

Now split the proposed region into three cases:

$$
\mathrm{Auto} := E\wedge R',
\qquad
\mathrm{Review} := E\wedge R,
\qquad
\mathrm{Reject} := P\wedge(A'\vee H).
$$

<strong>Standard reading.</strong>
$\mathrm{Auto} := E\wedge R'$, $\mathrm{Review} := E\wedge R$, and
$\mathrm{Reject} := P\wedge(A'\vee H)$.

<strong>Plain English.</strong>
Eligible candidates either auto-accept or go to review. Proposed candidates
that are disallowed or hard-rejected go to symbolic rejection.

<strong>Trap.</strong>
This is not a soft preference ranking. These are exact set partitions over the
audited candidate universe.

## Part IV: the checked laws

The first checked law is the no-leak law:

$$
\mathrm{Auto}\wedge H = 0.
$$

<strong>Standard reading.</strong>
$\mathrm{Auto}\wedge H = 0$.

<strong>Plain English.</strong>
Nothing that is hard-rejected can also be auto-accepted.

The second checked law is the partition law:

$$
\mathrm{Auto}\vee\mathrm{Review}\vee\mathrm{Reject}=P.
$$

<strong>Standard reading.</strong>
$\mathrm{Auto}\vee\mathrm{Review}\vee\mathrm{Reject}=P$.

<strong>Plain English.</strong>
Every proposed candidate lands in exactly the supported decision surface:
auto-accept, human review, or symbolic rejection.

The proof packet also checks that these regions do not overlap:

$$
\mathrm{Auto}\wedge\mathrm{Review}=0,\qquad
\mathrm{Auto}\wedge\mathrm{Reject}=0,\qquad
\mathrm{Review}\wedge\mathrm{Reject}=0.
$$

<strong>Standard reading.</strong>
$\mathrm{Auto}\wedge\mathrm{Review}=0$, $\mathrm{Auto}\wedge\mathrm{Reject}=0$,
and $\mathrm{Review}\wedge\mathrm{Reject}=0$.

<strong>Plain English.</strong>
No candidate is classified into two decision regions at the same time.

<strong>Trap.</strong>
The law is about the proposed region $P$, not about all possible actions in the
world. The finite carrier only knows the audited atom set it was given.

## Part V: what Tau runs

The reproduction command is:

```bash
./scripts/run_qns_semantic_ba_demos.sh
```

The script downloads the official Tau Language repository, applies the local
research patches, builds Tau, and runs the qNS demo.

The demo checks:

- native `qns8` meet and join,
- prime-as-XOR-with-top behavior,
- exact symbolic filtering for candidate masks,
- concept-set filtering for controlled audited labels,
- bounded trace-class filtering,
- rejection of `qns8` syntax when `TAU_ENABLE_QNS_BA=1` is absent.

The current result has:

```text
ok: true
mismatch_count: 0
```

That is a runnable evidence claim, not a full semantic claim about arbitrary
natural language.

## Part VI: why this is not `nlang`

Upstream Tau's `nlang` carrier is a natural-language concept carrier. It
composes strings such as:

```text
(A) and (B)
(A) or (B)
not (A)
```

The semantic question for `nlang` is delegated to an external oracle.

The qNS finite carrier is different:

| Carrier | Stored value | Semantic discipline |
|---|---|---|
| `nlang` | natural-language concept string | oracle-backed interpretation |
| `qns8` | finite audited atom mask | exact finite powerset semantics |

So `nlang` is better for exploratory natural-language interfaces.
The qNS carrier is better when the candidate menu has already been audited and
the filtering step must be exact.

## Part VII: what this gives Tau

This experiment gives Tau a concrete role in a neuro-symbolic loop:

```text
Model proposes.
Tau filters.
Host renormalizes.
Proof artifact checks the finite set laws.
```

The proof artifact is small but useful. It proves the no-leak and partition
laws at the finite powerset level:

```text
auto_accept_no_hard_reject:
  Auto ∧ H = 0

partition_eq_proposed:
  Auto ∨ Review ∨ Reject = P
```

The proof packet is checked in the Lean file:

```text
experiments/neuro_symbolic_math_v001/Proofs.lean
```

The implementation artifact shows that Tau can run the exact symbolic carrier
natively, under a feature flag, without claiming
that the neural model itself is formally verified.

That is the point of this carrier: not to replace the neural model, and not to
replace upstream `nlang`, but to give the neuro-symbolic loop one exact
Boolean-algebraic checkpoint.

## Part VIII: practical use cases

The practical gain is that Tau can now check a finite audited candidate menu
natively. That enables workflows that were awkward before this carrier.

| Use case | What the model proposes | What Tau checks |
|---|---|---|
| Agent tool-call gating | candidate tool calls | allow, deny, review, and hard-reject masks |
| DeFi risk triage | collateral or liquidation actions | symbolic risk atoms before execution |
| Governance routing | proposal labels | exact admit, reject, or human-review regions |
| Protocol trace triage | bounded trace classes | safe, forbidden, and unclassified behavior |
| Explanation menus | possible reasons | surviving and rejected reason atoms |
| Proof-task routing | candidate proof obligations | which obligations are allowed into an automated prover |

For example, an agent can propose eight possible actions with soft scores.
Tau can then compute:

$$
\mathrm{Survivors}
=
\mathrm{Proposed}\wedge\mathrm{Allowed}\wedge\mathrm{HardReject}'.
$$

<strong>Standard reading.</strong>
$\mathrm{Survivors}=\mathrm{Proposed}\wedge\mathrm{Allowed}\wedge\mathrm{HardReject}'$.

<strong>Plain English.</strong>
Keep only candidates that were proposed, allowed, and not hard-rejected.

The host can then renormalize the neural scores over $\mathrm{Survivors}$.
This is the concrete new ability:

```text
soft model output becomes an audited finite decision surface.
```

Before this experiment, the host could still perform that filtering in ordinary
application code. The difference is that the symbolic checkpoint now lives in
Tau's Boolean-algebraic world, where it can be composed with other Tau
specifications and audited with the same proof discipline as the table and
qelim demos.

## Part IX: reason-coded routing

The next derived artifact is:

```text
assets/data/qns_reason_manifest.json
```

It is generated from the Tau-checked trace artifact:

```bash
python3 scripts/generate_qns_reason_manifest.py
```

The manifest does not change the Boolean algebra. It compiles the existing mask
outputs into per-atom explanations. For one action atom, a row has this shape:

```json
{
  "name": "tax_extractor",
  "route": "symbolic_reject",
  "reasons": [
    "hard reject mask contains candidate",
    "symbolic allow mask does not contain candidate"
  ]
}
```

The exact partition check is:

$$
\mathrm{Auto}\vee\mathrm{Review}\vee\mathrm{Reject}=P.
$$

<strong>Standard reading.</strong>
The join of the auto-accept region, the human-review region, and the symbolic
reject region is equal to the proposed region $P$.

<strong>Plain English.</strong>
Every proposed candidate gets exactly one supported decision route.

The reason manifest checks this in the bounded demo:

```text
candidate_proposed_partition_failures = 0
candidate_universe_partition_failures = 0
unsafe_leak_failures = 0
```

<strong>Standard reading.</strong>
The generated reason manifest has zero candidate proposed-partition failures,
zero candidate universe-partition failures, and zero unsafe-leak failures.

<strong>Plain English.</strong>
The explanation rows did not drift away from the Tau mask outputs.

<strong>Trap.</strong>
The reasons are not free-form LLM explanations. They are deterministic labels
computed from the same masks Tau already checked.

This is the more practical interface:

```text
mask result
  -> per-atom route
  -> per-atom reason
  -> qNS survivor probability when applicable
```

The current manifest covers:

- $24$ action-candidate entries,
- $24$ controlled-concept entries,
- $24$ bounded trace-class entries.

<strong>Boundary.</strong>
Reason-coded routing still does not prove that the external model chose the
right candidates, extracted the right concepts, or recognized the right trace
classes. It proves that once those finite atom masks are supplied, Tau's exact
Boolean outputs can be rendered as an auditable route-and-reason manifest.

## Part X: a multi-feature Tau demo

The next demo file is:

```text
examples/tau/qns_multifeature_decision_surface_v1.tau
```

The generated trace artifact is:

```text
assets/data/qns_multifeature_demo_traces.json
```

It is produced by:

```bash
python3 scripts/generate_qns_multifeature_demo_artifacts.py
```

This demo adds a toy micro-proposer outside Tau. It maps prompt keywords to a
finite proposed-candidate mask. A real LLM could replace that toy proposer,
provided it emits the same finite mask interface.

The Tau side then checks:

```text
proposed mask
  -> auto/review/reject masks
  -> unsafe-leak check
  -> pointwise revision-style policy memory update
```

The revision expression is:

$$
\operatorname{Rev}(O,G,A)
=
(G\wedge A)\vee(G'\wedge O).
$$

<strong>Standard reading.</strong>
$\operatorname{Rev}(O,G,A)$ is the join of $G\wedge A$ and $G'\wedge O$.

<strong>Plain English.</strong>
Inside the guard, use the replacement value. Outside the guard, preserve the
old value.

The multi-feature artifact checks:

```text
scenario_count = 3
tau_mismatch_count = 0
partition_failure_count = 0
unsafe_leak_failure_count = 0
revision_idempotence_failure_count = 0
```

<strong>Standard reading.</strong>
Across the three bounded scenarios, Tau's qNS outputs match the host reference
outputs, the partition check has no failures, the unsafe leak check has no
failures, and applying the same revision pass twice has no idempotence failure.

<strong>Plain English.</strong>
The demo runs through actual Tau qNS expressions and produces the same result
as the host-side reference model.

There are two execution shapes:

| Shape | Meaning | Status |
|---|---|---|
| Fast staged | Check route masks first, then feed checked masks into revision. | Recommended path. |
| Slow monolithic | Send the fully expanded revision expression to Tau in one expression. | Performance-boundary demo. |

The slow lane is intentionally included. In the current artifact, the fully
expanded revision expression times out under the bounded timeout, while the
staged lane passes.

<strong>Trap.</strong>
The timeout is not a semantic failure. It shows why the qNS pipeline should
compile into staged masks instead of blindly expanding every formula into one
large expression.

This is where qNS can be more useful than raw `nlang` for formal workflows:

```text
nlang: flexible text carrier, oracle interprets meaning
qNS: finite audited atoms, Tau computes exact routes, reasons, and revisions
```

The two designs serve different purposes. `nlang` is broader as an interface.
qNS is stronger as an auditable execution checkpoint.

## Part XI: an audited ontology compiler

The next qNS artifact is:

```text
assets/data/qns_ontology_compiler_traces.json
```

It is generated by:

```bash
python3 scripts/compile_qns_ontology_masks.py
```

The compiler takes bounded policy text and maps audited phrases to qNS atom
masks. It also quarantines two kinds of unsafe input: ambiguous phrases and
unknown terms.

The compiler surface is:

$$
C(t)=
\bigl(
M_{\mathrm{observed}}(t),
M_{\mathrm{ambiguous}}(t),
M_{\mathrm{exact}}(t),
M_{\mathrm{review}}(t),
Q_{\mathrm{unknown}}(t)
\bigr).
$$

<strong>Standard reading.</strong>
$C(t)$ is the ordered tuple whose entries are the observed mask of $t$, the
ambiguous mask of $t$, the exact mask of $t$, the review mask of $t$, and the
unknown-term set of $t$.

<strong>Plain English.</strong>
The compiler turns audited phrases into exact qNS bits, and it keeps ambiguity
or unknown language out of the exact route.

The clean case has no quarantine:

```text
clean_collateral_report:
  observed = registry_verified, liquidity_deep, token_old_enough,
             provenance_clean, governance_separated, oracle_stable
  ambiguous = none
  unknown = none
```

The ambiguous case is not silently accepted:

```text
ambiguous_risk_report:
  ambiguous = review, risk
  review atoms = sanction_risk, human_review_required
  unknown = none
```

The unknown case is quarantined:

```text
unknown_term_report:
  unknown = momentum, quantum, sentiment, vibe
```

The checked summary is:

```text
case_count = 3
ambiguous_case_count = 1
unknown_quarantine_count = 1
total_unknown_terms = 4
exact_mask_nonzero_count = 3
```

<strong>Standard reading.</strong>
The generated artifact contains three cases, exactly one case with a nonzero
ambiguous mask, exactly one case with unknown-term quarantine, four total
unknown terms, and three cases with a nonzero exact mask.

<strong>Plain English.</strong>
The compiler separates the intended clean, ambiguous, and unknown examples.

<strong>Trap.</strong>
This is not the same object as upstream `nlang`. `nlang` is a broad natural
language Boolean algebra. This qNS compiler is narrower: it turns a governed
phrase table into exact finite masks and sends ambiguity to review before Tau
reasoning.

This is why the qNS lane can be stronger than `nlang` for audited workflows:

```text
text phrase
  -> governed ontology match
  -> qNS mask
  -> Tau route/reason/revision expression
```

The gain is not broader language coverage. The gain is that a downstream Tau
spec can receive a finite, checked mask instead of an unconstrained sentence.

## Part XII: ontology masks running through Tau

The ontology compiler is useful only if the compiled masks can enter Tau. The
bridge artifact is:

```text
assets/data/qns_ontology_tau_bridge_traces.json
```

It is generated by:

```bash
python3 scripts/generate_qns_ontology_tau_bridge_artifacts.py \
  --tau-bin external/tau-lang-qns-ba/build-Release/tau
```

The bridge sends the compiled qNS masks into Tau expressions for required-atom
coverage, blocker detection, and pointwise revision-style memory update.

The blocker surface is:

$$
B(t)
=
M_{\mathrm{missing}}(t)
\vee
M_{\mathrm{risk}}(t)
\vee
M_{\mathrm{review}}(t).
$$

<strong>Standard reading.</strong>
$B(t)$ is the join of the missing-required-atom mask of $t$, the risk-hit mask
of $t$, and the review mask of $t$.

<strong>Plain English.</strong>
Anything missing, risky, ambiguous, or unknown becomes a blocker mask before
the decision proceeds.

The memory update reuses the same pointwise revision law:

$$
\operatorname{Rev}(O,B,B)=(B\wedge B)\vee(B'\wedge O).
$$

<strong>Standard reading.</strong>
$\operatorname{Rev}(O,B,B)$ is the join of $B\wedge B$ and $B'\wedge O$.

<strong>Plain English.</strong>
Record the blocker region, and preserve the old memory outside that region.

The checked bridge summary is:

```text
case_count = 3
tau_mismatch_count = 0
clean_blocker_failure_count = 0
nonclean_blocker_failure_count = 0
revision_idempotence_failure_count = 0
```

<strong>Standard reading.</strong>
The generated artifact contains three cases, zero Tau-versus-host mismatches,
zero failures of the clean no-blocker check, zero failures of the non-clean
blocker check, and zero failures of revision idempotence.

<strong>Plain English.</strong>
The clean report stays clear, the ambiguous and unknown reports produce
blockers, and Tau agrees with the host reference on every checked mask.

<strong>Trap.</strong>
The bridge uses staged masks. It does not expand the whole ontology, blocker,
and revision computation into one giant expression. The earlier slow lane shows
why staged qNS compilation matters.

## Part XIII: certificate-carrying proposer output

The strongest qNS interface so far is not a bare text string. It is a small
certificate object:

```text
span, atom, confidence, reason
```

The generated artifact is:

```text
assets/data/qns_certificate_proposer_traces.json
```

It is produced by:

```bash
python3 scripts/generate_qns_certificate_proposer_artifacts.py \
  --tau-bin external/tau-lang-qns-ba/build-Release/tau
```

The acceptance rule is:

$$
\operatorname{Accept}(s,a)
\Longleftrightarrow
a\in A
\wedge
\operatorname{norm}(s)\in P_a.
$$

<strong>Standard reading.</strong>
$\operatorname{Accept}(s,a)$ holds exactly when $a$ is an atom in the audited
atom set $A$ and the normalized span $s$ is a member of the audited phrase set
$P_a$ for atom $a$.

<strong>Plain English.</strong>
A proposed claim is accepted only when it names a known atom and its evidence
span is one of that atom's governed phrases.

The accepted mask is:

$$
M_{\mathrm{accepted}}(C)
=
\bigvee_{\operatorname{Accept}(s,a)}
m(a).
$$

<strong>Standard reading.</strong>
$M_{\mathrm{accepted}}(C)$ is the join of $m(a)$ over all claims in certificate
$C$ whose span and atom satisfy $\operatorname{Accept}(s,a)$.

<strong>Plain English.</strong>
Only accepted certificate claims contribute bits to the qNS mask.

The checked summary is:

```text
certificate_count = 3
total_claim_count = 12
accepted_claim_count = 8
rejected_claim_count = 4
ambiguous_claim_count = 2
unknown_atom_claim_count = 1
unsupported_span_claim_count = 1
tau_mismatch_count = 0
```

<strong>Standard reading.</strong>
The artifact contains three certificate objects, twelve total claims, eight
accepted claims, four rejected claims, two rejected ambiguous claims, one
rejected unknown-atom claim, one rejected unsupported-span claim, and zero
Tau-versus-host mismatches.

<strong>Plain English.</strong>
The external proposer can attach confidence and reasons, but Tau only receives
the finite mask produced by the deterministic certificate validator.

<strong>Trap.</strong>
The confidence field is recorded evidence, not authority. A high-confidence
claim with an unknown atom or unsupported span is still rejected before Tau
reasoning.
