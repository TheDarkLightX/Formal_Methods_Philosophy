---
title: Medical deciders, MPRD, and Tau
layout: docs
kicker: Tutorial 22
description: Use MPRD to think about bounded medical automation. Models propose, policy decides, execution stays narrow, and fail-closed gates turn many bounded doctor-like tasks into checkable workflows.
---

This tutorial takes the MPRD architecture from [Tutorial 6]({{ '/tutorials/mprd-and-algorithmic-ceo/' | relative_url }}) and moves it into a new domain: medicine.

For a simpler entry point built from two bounded examples, see [Tutorial 23]({{ '/tutorials/decidable-medical-machines/' | relative_url }}).

It is **not** that a large language model should be treated like a doctor.
It is that many small medical workflows already have a familiar shape:

- a bounded input surface,
- a finite or at least sharply limited action menu,
- explicit exclusions,
- temporal freshness rules,
- and a safe fallback, usually escalation to a human.

If that is the shape, then **MPRD fits**:

- the model proposes,
- the policy decides,
- the executor acts only on allowed actions,
- and many dangerous states become unreachable because they are rejected before execution.

Source scope:

- the public MPRD repository at [github.com/TheDarkLightX/MPRD](https://github.com/TheDarkLightX/MPRD)
- the public Tau tutorial material in this repository
- three new **educational** Tau examples in `examples/tau/`

<div class="fp-callout fp-callout-warning">
  <p class="fp-callout-title">Scope and safety note</p>
  <p>
    This page is about software architecture and formalization patterns. The Tau examples and the interactive lab are educational, not clinical guidance. Wherever a real deployment would need official equations, regulatory rules, or institution-specific guidelines, this tutorial states that dependency explicitly instead of smuggling in a toy rule as if it were a medical fact.
  </p>
</div>

## Part I: the small machine inside many medical workflows

Take a very simple case.

A patient wants to know what to do next after a result arrives. A chart, a lab panel, or a refill request enters the system. The system does not need to solve all of medicine. It needs to answer one bounded question:

> Is this one proposed next step allowed, given the available evidence and the governing rule set?

This already describes a machine.

In the simplest case, it is just a calculator:

`inputs -> derived value`

In the next case, it is a classifier:

`derived value -> stage`

In the next case, it is a gate:

`stage + exclusions + freshness + identity -> allowed action class`

This is why medicine so often looks like finite-state or decision-tree software:

- collect facts,
- compute derived quantities,
- classify,
- check exclusions,
- choose among a small menu,
- escalate when the bounded rules no longer apply.

## Part II: the MPRD shape in medicine

MPRD states a safety invariant in public documentation:

$$
\forall a_{\mathrm{exec}} \;
\bigl(
\mathrm{Executed}(a_{\mathrm{exec}})
\rightarrow
\mathrm{Allowed}(\mathrm{policy}, \mathrm{state}, a_{\mathrm{exec}})
\bigr)
$$

In plain English:

Every executed action must already have passed policy.

This principle maps directly to bounded medical workflows.

<figure class="fp-figure">
  <p class="fp-figure-title">MPRD pipeline in medicine</p>
  {% include diagrams/medical-mprd-pipeline.svg %}
  <figcaption class="fp-figure-caption">
    Evidence flows through the proposer to the policy gate. Only approved actions reach the executor. Denied or out-of-scope proposals route to escalation.
  </figcaption>
</figure>

Assumption A:
An institution has a versioned guideline or policy artifact \(G\), a trusted fact-extraction layer \(E\), and a bounded action menu \(A\).

Then the medical MPRD pipeline can be written as:

$$
\mathrm{Facts} = E(\mathrm{chart}, \mathrm{labs}, \mathrm{provenance}, G)
$$

$$
\mathrm{Candidates} = \mathrm{Propose}(\mathrm{model}, \mathrm{Facts}, \mathrm{task})
$$

$$
\mathrm{Allowed}(G, \mathrm{Facts}, a)
$$

$$
\mathrm{Sel}(G, \mathrm{Facts}, \mathrm{Candidates}) = a \Rightarrow a \in \mathrm{Candidates} \land \mathrm{Allowed}(G, \mathrm{Facts}, a)
$$

$$
\mathrm{Execute}(b)
\Rightarrow
\mathrm{ValidDecision}(b,r) = \mathrm{true}
$$

The interpretation is exact:

- the model can propose a note, order-set, follow-up class, refill action, or escalation class,
- the policy gate decides whether that proposal is admissible,
- execution happens only through the narrow gate,
- and the audit transcript can bind the executed action back to the governing policy version and the structured facts.

This is much closer to **doctor-like micro-workflows** than to full-scale medical automation.

## Part III: symbol guide

The formulas above use a small vocabulary repeatedly.

| Symbol | Meaning |
|---|---|
| \(G\) | governing policy or guideline artifact |
| \(\mathrm{Facts}\) | structured facts extracted from chart, labs, and provenance |
| \(a\) | one proposed action |
| \(a_{\mathrm{exec}}\) | the action that actually gets executed |
| \(b\) | an execution bundle |
| \(\mathrm{Candidates}\) | bounded action menu proposed by the model |
| \(\mathrm{Allowed}(G,\mathrm{Facts},a)\) | policy says action \(a\) is allowed |
| \(\mathrm{Sel}(G,\mathrm{Facts},\mathrm{Candidates})\) | deterministic selector returns one action |
| \(r\) | registry or execution state tracked by the executor |
| \(\Rightarrow\) | implication, read as "if ... then ..." |
| \(\land\) | conjunction, read as "and" |
| \(a \in \mathrm{Candidates}\) | the selected action actually comes from the candidate set |

The important separation is:

- the model proposes candidates,
- the selector chooses within a bounded menu,
- the policy checks the chosen action,
- the executor acts only after that check.

## Part IV: a taxonomy of recurring medical software shapes

Medicine is large, but many software tasks inside it reuse a small number of shapes.

### 1. Calculators and transducers

A calculator is a total function:

$$
f : X \to Y
$$

Examples:

- estimated risk score,
- derived body-composition quantity,
- derived dose ceiling,
- lab normalization or unit conversion.

These are typically easiest to automate: they require only arithmetic and bounded input validation.

### 2. Classifiers and staging rules

A classifier maps a derived quantity into a finite label set:

$$
g : Y \to K
$$

Examples:

- stage,
- severity bucket,
- low / medium / high risk,
- normal / abnormal / critical.

Here, medical decision trees first take shape.

### 3. Checklist gates

A gate is often just a conjunction of predicates:

$$
\mathrm{Allow}(a,s) \Leftrightarrow P_1(s) \land P_2(s) \land \dots \land P_n(s)
$$

Examples:

- identity bound,
- data complete,
- contraindications absent,
- dose within limit,
- action within institution policy.

This is the most direct MPRD shape.

### 4. Temporal freshness and protocol windows

Many workflows involve temporal constraints:

$$
\mathrm{Fresh}(x, t) \Leftrightarrow t - \mathrm{time}(x) \le \Delta
$$

Examples:

- result still fresh enough,
- cooldown elapsed,
- refill window open,
- follow-up due after a fixed interval.

Temporal freshness naturally suggests a finite-state or temporal-logic formalization.

### 5. Selector and canonicalization rules

If the model proposes several bounded options, a selector can still be deterministic:

$$
\mathrm{Sel}(G, s, C) = a \Rightarrow a \in C \land \mathrm{Allowed}(G, s, a)
$$

If ties matter, a canonical tie-break can be added:

$$
\mathrm{Allowed}(G, s, a_1) \land \mathrm{Allowed}(G, s, a_2) \land \mathrm{Key}(a_1) < \mathrm{Key}(a_2) \Rightarrow \mathrm{Sel}(G,s,\{a_1,a_2\}) = a_1
$$

Deterministic selection is essential for audit trails and replay.

### 6. Human escalation as an explicit action

The safest pattern in medicine is often not "allow or deny" alone.
It is "allow automation or escalate to a human".

That can be formalized:

$$
\mathrm{MissingEvidence}(s) \lor \mathrm{OutOfScope}(s)
\Rightarrow
\mathrm{Allow}(G,s,a_{\mathrm{review}})
$$

and

$$
\mathrm{MissingEvidence}(s) \lor \mathrm{OutOfScope}(s)
\Rightarrow
\neg \mathrm{Allow}(G,s,a_{\mathrm{auto}})
$$

Here \(a_{\mathrm{review}}\) denotes the human-review action, and \(a_{\mathrm{auto}}\) denotes an automatic execution action.

This is the core fail-closed guarantee.

## Part V: which medical scenarios fit this shape best

The better the task is bounded, versioned, and protocolized, the better MPRD fits.

Strong fits:

- calculator-backed wellness or nutrition tools,
- lab-result staging after structured fact extraction,
- refill screening under explicit allowlists and freshness rules,
- documentation completeness checks,
- order-set gating under fixed institutional pathways,
- reminders, retest windows, and escalation workflows.

Weaker fits:

- open-ended diagnosis from unconstrained prose,
- novel treatment design,
- ambiguous multimorbidity management,
- tasks where the action space is not sharply bounded,
- tasks where the evidence model itself is unstable or under-specified.

So the correct slogan is:

> MPRD fits bounded medical workflow fragments, not medicine as a whole.

## Part VI: three educational Tau examples

The new Tau examples in this repository stay inside that bounded zone.

Implementation note:
the public replay lane uses `bv[8]` flags restricted in practice to `0` or `1`, rather than raw `sbf` outputs. This keeps the recorded Tau traces concrete and archive-friendly while preserving the same Boolean decision shape.

### Example A: educational wellness-plan gate

Files:

- [medical_wellness_deficit_gate_v1.tau]({{ '/examples/tau/medical_wellness_deficit_gate_v1.tau' | relative_url }})

This example mirrors the shape of the max-calorie-deficit calculator:

1. the host computes or checks the derived ceiling,
2. the model proposes either `publish_plan` or `escalate_human`,
3. Tau allows publication only when all required evidence flags are true.

Logic shape:

$$
\mathrm{AutoPlanOpen}(s) \Leftrightarrow \mathrm{DataComplete}(s) \land \mathrm{WithinScope}(s) \land \mathrm{IdentityBound}(s) \land \mathrm{RedFlagsClear}(s) \land \mathrm{FormulaBound}(s) \land \mathrm{RequestLeCeiling}(s)
$$

$$
\mathrm{Allow}(s,a_{\mathrm{plan}})
\Leftrightarrow
\mathrm{OneHot}(s) \land \mathrm{AutoPlanOpen}(s)
$$

$$
\mathrm{Allow}(s,a_{\mathrm{escalate}})
\Leftrightarrow
\mathrm{OneHot}(s) \land \neg \mathrm{AutoPlanOpen}(s)
$$

Here \(a_{\mathrm{plan}}\) is the publish-plan action, and \(a_{\mathrm{escalate}}\) is the human-escalation action.

The lesson here is not about nutrition but about architecture:
the model cannot publish merely because it made a proposal.

### Example B: toy lab follow-up gate

Files:

- [medical_lab_followup_gate_toy_v1.tau]({{ '/examples/tau/medical_lab_followup_gate_toy_v1.tau' | relative_url }})

This example uses three action classes:

- `watch`
- `repeat_lab`
- `human_review`

In the public replay lane, the host side compresses several lower-level checks into a smaller bounded flag surface before Tau runs. That is consistent with the MPRD rule from the public repo: **host computes, Tau validates**.

The policy says:

$$
\mathrm{Allow}(s,a_{\mathrm{watch}})
\Leftrightarrow
\mathrm{Complete}(s) \land \mathrm{Fresh}(s) \land \neg \mathrm{RedFlag}(s) \land \neg \mathrm{Abnormal}(s)
$$

$$
\mathrm{Allow}(s,a_{\mathrm{repeat}})
\Leftrightarrow
\mathrm{Complete}(s) \land \mathrm{Fresh}(s) \land \neg \mathrm{RedFlag}(s) \land \mathrm{Abnormal}(s)
$$

$$
\mathrm{HumanReviewRequired}(s) \Leftrightarrow \mathrm{RedFlag}(s) \lor \neg \mathrm{Complete}(s) \lor \neg \mathrm{Fresh}(s)
$$

$$
\mathrm{Allow}(s,a_{\mathrm{review}})
\Leftrightarrow
\mathrm{HumanReviewRequired}(s)
$$

The action names are \(a_{\mathrm{watch}}\) for observe, \(a_{\mathrm{repeat}}\) for repeat the lab, and \(a_{\mathrm{review}}\) for route to human review.

These are simplified examples, but the underlying pattern is genuine.
Many guideline pathways reduce to exactly this pattern once the structured facts are extracted.

### Example C: toy refill gate

Files:

- [medical_refill_gate_toy_v1.tau]({{ '/examples/tau/medical_refill_gate_toy_v1.tau' | relative_url }})

This example shows a common bounded authorization problem:

$$
\mathrm{AutoRefillOpen}(s) \Leftrightarrow \mathrm{IdentityBound}(s) \land \mathrm{AllowlistOk}(s) \land \mathrm{AllergiesClear}(s) \land \mathrm{DoseWithinLimit}(s) \land \mathrm{LabsFresh}(s) \land \mathrm{RefillWindowOk}(s)
$$

$$
\mathrm{Allow}(s,\mathrm{refill}) \Leftrightarrow \mathrm{OneHot}(s) \land \mathrm{AutoRefillOpen}(s)
$$

$$
\mathrm{Allow}(s,a_{\mathrm{hold}})
\Leftrightarrow
\mathrm{OneHot}(s) \land \neg \mathrm{AutoRefillOpen}(s)
$$

Here \(a_{\mathrm{hold}}\) means hold the refill and route it to review. Again, the safe fallback is explicit.

## Part VII: what the Tau traces show

The examples above were run locally through Tau and archived as recorded traces:

- [medical_tau_traces.json]({{ '/assets/data/medical_tau_traces.json' | relative_url }})
- [generate_medical_tau_artifacts.py]({{ '/scripts/generate_medical_tau_artifacts.py' | relative_url }})

The traces show three things clearly.

1. **Good proposals pass.**
   If the structured flags match the policy, the proposed bounded action is allowed.

2. **Bad automation proposals fail closed.**
   If the model proposes `publish_plan` or `refill` while the safety lane is closed, Tau returns deny.

3. **Escalation proposals can still be allowed.**
   The distinction between "deny automation" and "allow human review" is one of the deepest lessons in medical automation. "Deny automation" and "allow human review" are not the same action.

That distinction is part of the shape.

## Part VIII: a medical MPRD lab

<figure class="fp-figure">
  <p class="fp-figure-title">Interactive: medical MPRD lab</p>
  <iframe
    src="{{ '/medical_mprd_lab.html' | relative_url }}"
    title="Interactive medical MPRD lab"
    style="width: 100%; border: 0; overflow: hidden"
    height="1640"
    loading="lazy"
    data-fp-resize="true"></iframe>
  <figcaption class="fp-figure-caption">
    The lab lets the reader toggle structured facts, choose one proposed action, and watch the proposer, policy, and executor layers separate. It also displays recorded Tau cases from the local trace bundle.
  </figcaption>
</figure>

## Part IX: why official guidelines matter

A production deployment requires far more than a simplified boolean gate.

At minimum it would need:

- a versioned official equation or guideline artifact,
- a fact-extraction layer that binds structured inputs to that artifact,
- provenance checks on the data source,
- a bounded action menu,
- a fail-closed policy for missing or contradictory evidence,
- and an execution boundary that cannot bypass policy.

That can be written as:

$$
\mathrm{ClinicalReady}(s,G) \Rightarrow \mathrm{DataBound}(s) \land \mathrm{GuidelineBound}(G) \land \mathrm{VersionResolved}(G) \land \mathrm{Allowed}(G,s,a)
$$

and its fail-closed dual:

$$
\neg \mathrm{ClinicalReady}(s,G)
\Rightarrow
\neg \mathrm{Allow}(G,s,a_{\mathrm{auto}})
$$

If those bindings are missing, the system must not proceed without explicit authorization.

## Part X: stress-testing the assumptions

The most dangerous mistakes in medical automation are often boundary mistakes:

- wrong patient,
- stale lab,
- wrong unit,
- missing evidence,
- contradictory evidence,
- outdated guideline version,
- model proposes an action outside the approved menu.

These are precisely the failure modes MPRD prevents.

The core fail-closed pattern is:

$$
\mathrm{MissingEvidence}(s) \lor \mathrm{BindingFailure}(s) \lor \mathrm{OutOfScope}(s)
\Rightarrow
\neg \mathrm{Allow}(G,s,a_{\mathrm{auto}})
$$

If a human-review action exists, then:

$$
\mathrm{MissingEvidence}(s) \lor \mathrm{BindingFailure}(s) \lor \mathrm{OutOfScope}(s)
\Rightarrow
\mathrm{Allow}(G,s,a_{\mathrm{review}})
$$

That is how disaster states get pruned from the reachable set.

## Part XI: what to take away

The core insight is straightforward.

Many medical tasks already have a recurring software shape:

- compute,
- classify,
- gate,
- escalate if uncertain.

MPRD does not make medicine trivial.
It does make one architectural promise available:

> the model can be clever without being sovereign.

That is bounded medical automation done right.

The model proposes, policy decides, the executor stays narrow, and the safest action is often not silence but escalation under traceable policy.
