---
title: Decidable medical machines, from formulas to Tau
layout: docs
kicker: Tutorial 23
description: Start with two small medical-style programs, a calorie-deficit calculator and a kidney follow-up workflow, then view each one as math, logic, a decision tree, a finite-state machine, ordinary code, and Tau.
---

Prerequisites: [Tutorial 3]({{ '/tutorials/tau-language/' | relative_url }}) for Tau syntax, [Tutorial 6]({{ '/tutorials/mprd-and-algorithmic-ceo/' | relative_url }}) for MPRD, and [Tutorial 22]({{ '/tutorials/medical-deciders-mprd-and-tau/' | relative_url }}) for the broader medical MPRD context.

This tutorial starts with the small machines that appear inside many medical and wellness programs.

Rather than automating medicine at scale, it shows how a bounded workflow appears in several equivalent forms:

- as a math function,
- as a decision tree,
- as a finite-state machine,
- as ordinary code,
- and as a Tau specification.

These representations are complementary, different lenses on the same computational object.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Assumption hygiene</p>
  <ul>
    <li><strong>Assumption A, calorie lane:</strong> the tutorial uses a bounded teaching model of the calorie-deficit formula and treats the published result as an integer floor. The tutorial does not independently establish the physiology claim behind the formula.</li>
    <li><strong>Assumption B, kidney lane:</strong> the tutorial uses the adult creatinine-based eGFR equation listed on NIDDK's adult eGFR page, last reviewed in May 2025, for the calculator step, but the follow-up policy shown here is educational, not clinical guidance.</li>
    <li><strong>Assumption C, Tau boundary:</strong> some formulas are simple enough to encode directly in Tau, while others are better split into <em>host computes, Tau validates</em>.</li>
  </ul>
</div>

## Part I: what makes a small medical program decidable

The simplest software object in this tutorial is a total function:

$$
f : X \to Y
$$

It takes an input from \(X\) and always returns an output in \(Y\).

If the output is a yes or no verdict, the function becomes a decision procedure:

$$
d : X \to \{0,1\}
$$

A predicate \(P\) is decidable exactly when some total Boolean program decides it:

$$
\mathrm{Decidable}(P) \Leftrightarrow \exists d \ \forall x \ (d(x)\downarrow \land (d(x)=1 \Leftrightarrow P(x)))
$$

That is the mathematical view.

The same object can also be drawn as a finite-state machine:

$$
M = (Q,\Sigma,\delta,q_0,F)
$$

with:

- \(Q\), a finite set of states,
- \(\Sigma\), the input alphabet,
- \(\delta\), the transition rule,
- \(q_0\), the start state,
- \(F\), the set of final states.

For the bounded workflows in this tutorial, decidability means:

$$
\forall x \ \exists n \ \mathrm{run}(M,x,n) \in F
$$

Every input reaches a final state, with no loops and no unresolved cases.

By this definition, both calculators and guideline trees qualify as decidable machines.

## Part II: one object, four lenses

For the kinds of examples used here, each system can be read in four ways.

First, as composition:

$$
\mathrm{Decision}(x) = \mathrm{Policy}(\mathrm{Classify}(\mathrm{Compute}(x)))
$$

Second, as a decision tree:

- collect bounded facts,
- test one condition,
- branch,
- reach an action leaf.

Third, as a finite-state machine:

$$
\mathrm{Start} \to \mathrm{Read} \to \mathrm{Compute} \to \mathrm{Classify} \to \mathrm{Act} \to \mathrm{Done}
$$

Fourth, as logic:

$$
\mathrm{Allow}(a,s) \Leftrightarrow P_1(s) \land P_2(s) \land \dots \land P_n(s)
$$

The rest of the tutorial demonstrates each correspondence with concrete examples.

## Part III: example A, the max-calorie-deficit calculator

The first example is the user's own calculator:

- public repo: [TheDarkLightX/MaxCaloricDeficitCalc](https://github.com/TheDarkLightX/MaxCaloricDeficitCalc)

The motivating problem is simple.
A person wants a bounded estimate of the largest calorie deficit that still stays inside a particular published formula.

### The math view

Let:

- \(w\) = body weight in pounds,
- \(b\) = body-fat fraction, so \(20\%\) is \(0.20\),
- \(f\) = fat mass in pounds,
- \(m\) = maximum deficit in kcal/day.

Then the formulas are:

$$
f = w \cdot b
$$

$$
m = 31.4 \cdot f
$$

So the composed function is:

$$
m = 31.4 \cdot w \cdot b
$$

If the program displays an integer result, the bounded calculator can be written as:

$$
m_{\lfloor \rfloor} = \lfloor 31.4 \cdot w \cdot b \rfloor
$$

### The logic view

The arithmetic claim can be written as a relation:

$$
\mathrm{FatMass}(w,b,f) \Leftrightarrow f = w \cdot b
$$

$$
\mathrm{MaxDeficit}(w,b,m) \Leftrightarrow m = \lfloor 31.4 \cdot w \cdot b \rfloor
$$

If a program claims some output \(m\), the checker question is:

$$
\mathrm{CorrectClaim}(w,b,m) \Leftrightarrow m = \lfloor 31.4 \cdot w \cdot b \rfloor
$$

CorrectClaim is a decidable predicate.

### The decision-tree view

Even a calculator has a tiny decision tree:

1. Are the inputs present?
2. Are the inputs in range?
3. If yes, compute the result.
4. If no, reject or escalate.

That becomes:

$$
\mathrm{Accept}(w,b) \Leftrightarrow \mathrm{Present}(w,b) \land \mathrm{InRange}(w,b)
$$

$$
\mathrm{Accept}(w,b) \Rightarrow \mathrm{Output}(m_{\lfloor \rfloor})
$$

$$
\neg \mathrm{Accept}(w,b) \Rightarrow \mathrm{Output}(\mathrm{error})
$$

### The finite-state-machine view

The core formula is a single expression, but the user-facing program is a state machine:

$$
\mathrm{Start} \to \mathrm{ReadWeight} \to \mathrm{ReadBodyFat} \to \mathrm{ComputeFatMass} \to \mathrm{ComputeMaxDeficit} \to \mathrm{Display} \to \mathrm{Done}
$$

This separation of concerns shapes the design.

The mathematical object is:

$$
f(w,b) = \lfloor 31.4 \cdot w \cdot b \rfloor
$$

The interface object is:

$$
M_{\mathrm{ui}} = (Q,\Sigma,\delta,q_0,F)
$$

with several named phases.

<figure class="fp-figure">
  <p class="fp-figure-title">Calorie calculator finite-state machine</p>
  {% include diagrams/medical-calorie-fsm.svg %}
  <figcaption class="fp-figure-caption">
    The chain is linear. Every input either reaches Done or falls into the Error branch. No loops, no unresolved states.
  </figcaption>
</figure>

### The ordinary-code view

In ordinary code, the cleaned core is small:

```cpp
double fat_mass_lb = bodyweight_lb * bodyfat_fraction;
int max_deficit_kcal = static_cast<int>(std::floor(31.4 * fat_mass_lb));
```

The same computation appears in spreadsheet form:

$$
\mathrm{CellC1} = \mathrm{CellA1} \cdot \mathrm{CellB1}
$$

$$
\mathrm{CellD1} = \lfloor 31.4 \cdot \mathrm{CellC1} \rfloor
$$

This example reveals a fundamental principle:
program synthesis in a spreadsheet, C++, Python, or Tau can preserve the same shape.

### The Tau view

The Tau file for this calculator is:

- [medical_max_calorie_deficit_formula_v1.tau]({{ '/examples/tau/medical_max_calorie_deficit_formula_v1.tau' | relative_url }})

The spec is a **checker**, not a calculator.
It takes three inputs, including a claimed result, and outputs whether that claim matches the floor of the formula.
The host or user supplies the claim; Tau validates it.

Because the public teaching lane uses bounded integers, the formula is checked in scaled exact arithmetic.

Body fat is encoded in basis points, so \(20.00\%\) becomes \(2000\).
Then:

$$
31.4 \cdot w \cdot \frac{\mathrm{bf\_bps}}{10000}
=
\frac{314 \cdot w \cdot \mathrm{bf\_bps}}{100000}
$$

To express the floor relation without floating point, the Tau checker uses:

$$
100000 \cdot m \le 314 \cdot w \cdot \mathrm{bf\_bps} < 100000 \cdot (m+1)
$$

That is why this example is especially good for Tau.
The arithmetic is exact, finite, and integer-only, with no floating-point approximation.

The stream mapping is:

| Stream | Meaning |
|---|---|
| `i1` | bodyweight_lb |
| `i2` | bodyfat_bps |
| `i3` | claimed_max_deficit_kcal |
| `o1` | claimed_formula_matches (0 or 1) |
| `o2` | inputs_in_range (0 or 1) |

The core `always` clause:

```tau
always
  (((o2[t]:bv[8] = { #x01 }:bv[8]) <->
     ((i1[t]:bv[32] <= { #x000001F4 }:bv[32]) &&
      (i2[t]:bv[32] <= { #x00002710 }:bv[32]) &&
      (i3[t]:bv[32] <= { #x00004E20 }:bv[32])))) &&
  (((o1[t]:bv[8] = { #x01 }:bv[8]) <->
     ((o2[t]:bv[8] = { #x01 }:bv[8]) &&
      (({ #x000186A0 }:bv[32] * i3[t]:bv[32]) <=
       (({ #x0000013A }:bv[32] * i1[t]:bv[32]) * i2[t]:bv[32])) &&
      ((({ #x0000013A }:bv[32] * i1[t]:bv[32]) * i2[t]:bv[32]) <
       ({ #x000186A0 }:bv[32] * (i3[t]:bv[32] + { #x00000001 }:bv[32])))))) &&
  (((o1[t]:bv[8] = { #x00 }:bv[8]) || (o1[t]:bv[8] = { #x01 }:bv[8])) &&
   ((o2[t]:bv[8] = { #x00 }:bv[8]) || (o2[t]:bv[8] = { #x01 }:bv[8]))).
```

Reading guide:

1. The `o2` biconditional is the range check. The hex constants decode as: `#x1F4` = 500, `#x2710` = 10000, `#x4E20` = 20000.
2. The `o1` biconditional is the floor relation. `#x186A0` = 100000, `#x13A` = 314. It checks \(100000 \cdot \mathrm{claimed} \le 314 \cdot w \cdot \mathrm{bf\_bps} < 100000 \cdot (\mathrm{claimed}+1)\).
3. The final two disjunctions restrict both outputs to 0 or 1.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Checker or calculator?</p>
  <p>
    The spec above is a <strong>checker</strong>: it takes a claimed deficit as input and validates it.
    But the same floor inequality can also serve as a <strong>calculator</strong>.
    If the deficit is moved from an input stream to an output stream, the solver finds the unique value satisfying the constraint:
  </p>
  <pre><code>Input:  weight = 180 lb, bodyfat = 2000 bps (20%)
Solve:  100000 * o1 <= 314 * 180 * 2000 < 100000 * (o1 + 1)
Output: o1 = 1130 kcal/day</code></pre>
  <p>
    That is a direct answer, not a validation.
    The tutorial uses the checker form because it matches the MPRD pattern (host computes, Tau validates) and because the kidney lane <em>cannot</em> work as a direct calculator without leaving Tau's integer arithmetic. Its official equation uses floating-point exponents.
    Teaching both lanes as checkers establishes the uniform pattern.
    But for bounded integer formulas like this one, the same constraint works both ways.
    The direct-calculator version is at <a href="{{ '/examples/tau/medical_max_calorie_deficit_calculator_v1.tau' | relative_url }}">medical_max_calorie_deficit_calculator_v1.tau</a>.
  </p>
</div>

## Part IV: example B, kidney function to bounded follow-up

The second example is closer to ordinary medicine.

A patient gets a serum creatinine result, for example \(1.1\ \mathrm{mg/dL}\).
That result is not yet the same thing as a follow-up decision.
A machine still has to:

1. compute eGFR,
2. classify the result,
3. choose a bounded action class.

### The official calculator step

The 2021 CKD-EPI creatinine equation (NIDDK, race-free variant, reviewed May 2025) is:

$$
\mathrm{eGFR} = 142 \cdot \min(\mathrm{SCr}/\kappa,1)^{\alpha} \cdot \max(\mathrm{SCr}/\kappa,1)^{-1.200} \cdot 0.9938^{\mathrm{Age}} \cdot 1.012 \ [\text{if female}]
$$

with:

- \(\kappa = 0.7\) for females or \(0.9\) for males,
- \(\alpha = -0.241\) for females or \(-0.302\) for males,
- SCr = serum creatinine in mg/dL.

Source:
- [NIDDK adult eGFR equations](https://www.niddk.nih.gov/research-funding/research-programs/kidney-clinical-research-epidemiology/laboratory/glomerular-filtration-rate-equations/adults)

Creatinine alone is not enough: the equation depends on age and sex, so the host must supply all three.

### A concrete worked example

Assumption K1:
adult female, age \(55\), serum creatinine \(1.1\ \mathrm{mg/dL}\), using the NIDDK adult 2021 CKD-EPI creatinine equation.

For females, \(\kappa = 0.7\) and \(\alpha = -0.241\).

$$
\mathrm{SCr}/\kappa = 1.1 / 0.7 \approx 1.5714
$$

Since \(\mathrm{SCr}/\kappa > 1\):

$$
\min(\mathrm{SCr}/\kappa,\,1) = 1, \quad \max(\mathrm{SCr}/\kappa,\,1) \approx 1.5714
$$

$$
1^{-0.241} = 1
$$

$$
1.5714^{-1.200} \approx 0.5893
$$

$$
0.9938^{55} \approx 0.7099
$$

Assembling the equation with the female multiplier \(1.012\):

$$
\mathrm{eGFR} = 142 \times 1 \times 0.5893 \times 0.7099 \times 1.012 \approx 59.34
$$

This step converts serum creatinine into eGFR, the essential computation:

$$
\mathrm{KidneyEstimate}(\mathrm{creatinine},\mathrm{age},\mathrm{sex}) = \mathrm{eGFR}
$$

The National Kidney Foundation's patient-facing guidance also states that an eGFR below \(60\) for three months or more, or an eGFR above \(60\) with kidney damage, can indicate chronic kidney disease. Urine albumin context also matters.

Source:
- [NKF eGFR overview](https://www.kidney.org/kidney-failure-risk-factor-estimated-glomerular-filtration-rate-egfr)

That is why a real deployment needs more than one lab value and one threshold.

### The educational follow-up policy

Because full clinical policy is complex, the teaching example uses a simplified decision tree with three action classes:

- `watch`
- `repeat_lab`
- `human_review`

The host computes the exact eGFR.
Then it reduces the result to a bounded flag:

$$
\mathrm{Below60}(\mathrm{eGFR}) \Leftrightarrow \mathrm{eGFR} < 60
$$

Now the policy can be written:

$$
\mathrm{HumanReviewRequired}(s) \Leftrightarrow \mathrm{RedFlag}(s) \lor \neg \mathrm{Complete}(s) \lor \neg \mathrm{Fresh}(s)
$$

$$
\mathrm{Allow}(s,\mathrm{watch}) \Leftrightarrow \mathrm{OneHot}(s) \land \neg \mathrm{HumanReviewRequired}(s) \land \neg \mathrm{Below60}(s)
$$

$$
\mathrm{Allow}(s,\mathrm{repeat\_lab}) \Leftrightarrow \mathrm{OneHot}(s) \land \neg \mathrm{HumanReviewRequired}(s) \land \mathrm{Below60}(s)
$$

$$
\mathrm{Allow}(s,\mathrm{human\_review}) \Leftrightarrow \mathrm{OneHot}(s) \land \mathrm{HumanReviewRequired}(s)
$$

Though simplified for teaching, the pipeline structure mirrors real workflows:

$$
\mathrm{Decision} = \mathrm{Policy}(\mathrm{Classify}(\mathrm{Compute}(\mathrm{creatinine},\mathrm{age},\mathrm{sex})))
$$

### The finite-state-machine view

The kidney lane is a longer but still finite machine:

$$
\mathrm{Start} \to \mathrm{ReadCreatinine} \to \mathrm{ReadAgeSex} \to \mathrm{ComputeEGFR} \to \mathrm{ClassifyBand} \to \mathrm{ChooseAction} \to \mathrm{Done}
$$

If data are missing or stale, the machine moves to the human-review branch rather than proceeding with incomplete information.

### The decision-tree view

The kidney follow-up gate has the same shape as a small decision tree:

1. Is the result complete and fresh?
2. Is there a red flag?
3. Is eGFR below 60?

The leaves are:

$$
\neg \mathrm{Complete}(s) \lor \neg \mathrm{Fresh}(s) \Rightarrow \mathrm{human\_review}
$$

$$
\mathrm{RedFlag}(s) \Rightarrow \mathrm{human\_review}
$$

$$
\mathrm{Below60}(s) \land \neg \mathrm{RedFlag}(s) \Rightarrow \mathrm{repeat\_lab}
$$

$$
\neg \mathrm{Below60}(s) \land \neg \mathrm{RedFlag}(s) \Rightarrow \mathrm{watch}
$$

Every input combination reaches exactly one leaf.

<figure class="fp-figure">
  <p class="fp-figure-title">Kidney follow-up decision tree</p>
  {% include diagrams/medical-kidney-decision-tree.svg %}
  <figcaption class="fp-figure-caption">
    Three decision levels, three action-class leaves. Missing data or red flags route to human_review before the eGFR branch is reached.
  </figcaption>
</figure>

### The ordinary-code view

The same decision tree in ordinary code:

```cpp
double egfr = ckd_epi_2021(scr, age, sex);
bool below60 = egfr < 60.0;
if (red_flag || !complete || !fresh) return HUMAN_REVIEW;
if (below60) return REPEAT_LAB;
return WATCH;
```

The code, the state machine, and the logic formulas all model the same decision process.

### The Tau view

The public Tau file is:

- [medical_egfr_followup_gate_v1.tau]({{ '/examples/tau/medical_egfr_followup_gate_v1.tau' | relative_url }})

This file does **not** recompute the official floating-point equation.

Instead it follows the safer MPRD split:

$$
\mathrm{HostComputesEGFR} \land \mathrm{TauValidatesActionClass}
$$

This split clarifies the architectural boundary between computation and validation.

- some bounded arithmetic objects fit fully inside Tau,
- some official equations are better handled by host computation plus Tau validation.

The Tau spec implements this split with the following stream mapping:

| Stream | Meaning |
|---|---|
| `i1` | result_complete (0 or 1) |
| `i2` | result_fresh (0 or 1) |
| `i3` | red_flag_present (0 or 1) |
| `i4` | egfr_below_60 (0 or 1) |
| `i5` | propose_watch (0 or 1) |
| `i6` | propose_repeat_lab (0 or 1) |
| `i7` | propose_human_review (0 or 1) |
| `i8` | action_one_hot_ok (0 or 1) |
| `o1` | selected_action_allowed (0 or 1) |
| `o2` | human_review_required (0 or 1) |

The core `always` clause:

```tau
always
  (o2[t]:bv[8] =
    (i3[t]:bv[8] |
     ({ #x01 }:bv[8] - i1[t]:bv[8]) |
     ({ #x01 }:bv[8] - i2[t]:bv[8]))) &&
  (o1[t]:bv[8] =
    ((i8[t]:bv[8] *
      i5[t]:bv[8] *
      ({ #x01 }:bv[8] - i6[t]:bv[8]) *
      ({ #x01 }:bv[8] - i7[t]:bv[8]) *
      i1[t]:bv[8] *
      i2[t]:bv[8] *
      ({ #x01 }:bv[8] - i3[t]:bv[8]) *
      ({ #x01 }:bv[8] - i4[t]:bv[8])) +
     (i8[t]:bv[8] *
      ({ #x01 }:bv[8] - i5[t]:bv[8]) *
      i6[t]:bv[8] *
      ({ #x01 }:bv[8] - i7[t]:bv[8]) *
      i1[t]:bv[8] *
      i2[t]:bv[8] *
      ({ #x01 }:bv[8] - i3[t]:bv[8]) *
      i4[t]:bv[8]) +
     (i8[t]:bv[8] *
      ({ #x01 }:bv[8] - i5[t]:bv[8]) *
      ({ #x01 }:bv[8] - i6[t]:bv[8]) *
      i7[t]:bv[8] *
      o2[t]:bv[8]))).
```

Reading guide:

1. The first conjunct computes `o2` = human_review_required as the bitwise OR of red_flag, NOT complete (`1 - i1`), and NOT fresh (`1 - i2`).
2. The second conjunct computes `o1` as the sum of three mutually exclusive products, one for each action class: watch, repeat_lab, and human_review. Because inputs are restricted to 0 or 1, multiplication is conjunction and addition is disjunction over non-overlapping branches.
3. The watch product includes `(1 - i4)`, so it goes to zero whenever eGFR is below 60. The repeat_lab product includes `i4`, so it only fires when eGFR is below 60. The human_review product fires only when `o2` = 1.

## Part V: why these examples matter

The two examples above already show four recurring shapes. [Tutorial 22]({{ '/tutorials/medical-deciders-mprd-and-tau/' | relative_url }}) develops the full taxonomy; here is the short version with local pointers.

| Shape | Formula | Local example |
|---|---|---|
| Calculator | \(f : X \to Y\) | max calorie deficit |
| Calculator + classifier | \(g(f(x)) \in K\) | creatinine → eGFR → `below_60` band |
| Classifier + gate | \(\mathrm{Allow}(a,s) \Leftrightarrow P_1(s) \land \dots \land P_n(s)\) | watch / repeat_lab / human_review |
| Temporal gate | \(\mathrm{Fresh}(x,t) \Leftrightarrow t - \mathrm{time}(x) \le \Delta\) | stale lab → human_review |

The same shapes appear across many medical workflows: potassium follow-up trees, HbA1c monitoring and retest windows, CBC or anemia follow-up routing, and refill authorization under explicit freshness and identity rules.

They differ medically but share a common software architecture.

## Part VI: why decidability matters in medicine and wellness software

For a bounded workflow, decidability is not theoretical, it is a practical necessity.
It guarantees that every input reaches a final decision without looping indefinitely.

The totality claim is:

$$
\forall x \ \exists y \ (f(x)\downarrow = y)
$$

For a finite-state machine:

$$
\forall x \ \exists n \ \mathrm{run}(M,x,n) \in F
$$

For a gate:

$$
\forall s \ \exists a \ (\mathrm{Allow}(s,a) \lor \mathrm{Escalate}(s))
$$

The practical meanings are:

- every bounded case reaches an explicit conclusion,
- every out-of-scope case routes to a known fallback,
- and the entire decision surface is auditable.

That is why simple medical programs are such good teaching objects.

## Part VII: where Tau fits, and where it should stop

Tau is strongest when the object is:

- bounded,
- typed,
- integer-scaled or Boolean,
- and naturally expressed as invariants or action gates.

That makes the calorie example (Shape 1 in Part V: a pure calculator) a direct Tau object.

The kidney example shows the other lane.
Shape 2+3 from Part V (calculator followed by classifier followed by gate) is too rich for a single Tau spec because the official eGFR equation uses floating-point exponentiation.
The architectural split is:

$$
\mathrm{HostComputes} \to \mathrm{TauChecks} \to \mathrm{ExecutorActs}
$$

This is the same split used in MPRD:

- host code handles the rich arithmetic or parsing,
- Tau validates the bounded decision shape,
- execution only happens through the checked action class.

Tau should **not** be used for:

- open-ended reasoning or unconstrained search,
- floating-point computation that requires exact numeric fidelity,
- unbounded state spaces where totality cannot be guaranteed,
- or tasks where the action menu is not sharply defined.

Those belong on the host side or in a different tool altogether.

The layers above remain grounded in decidable machines, not hidden complexity.
It is just bounded medical machines composed inside a stricter architecture.

## Part VIII: downloadable specs and trace evidence

Spec files:

- [medical_max_calorie_deficit_formula_v1.tau](https://github.com/TheDarkLightX/Formal_Methods_Philosophy/blob/main/examples/tau/medical_max_calorie_deficit_formula_v1.tau) (checker)
- [medical_max_calorie_deficit_calculator_v1.tau](https://github.com/TheDarkLightX/Formal_Methods_Philosophy/blob/main/examples/tau/medical_max_calorie_deficit_calculator_v1.tau) (direct calculator)
- [medical_egfr_followup_gate_v1.tau](https://github.com/TheDarkLightX/Formal_Methods_Philosophy/blob/main/examples/tau/medical_egfr_followup_gate_v1.tau)

Replay artifacts:

- [medical_decidable_tau_traces.json](https://github.com/TheDarkLightX/Formal_Methods_Philosophy/blob/main/assets/data/medical_decidable_tau_traces.json)
- [generate_medical_decidable_tau_artifacts.py](https://github.com/TheDarkLightX/Formal_Methods_Philosophy/blob/main/scripts/generate_medical_decidable_tau_artifacts.py)

Companion lab:

- [medical_decidable_machines_lab.html](https://github.com/TheDarkLightX/Formal_Methods_Philosophy/blob/main/medical_decidable_machines_lab.html)

That means a reader can inspect:

- the formulas,
- the Tau specs,
- the replayable traces,
- and the host-side interactive demo.

### Calorie trace walkthrough

Two cases from the recorded traces show the floor check in action:

| case | weight | bf_bps | claimed | 314 * w * bf | 100000 * claimed | floor check | o1 | o2 |
|---|---|---|---|---|---|---|---|---|
| exact_match | 180 | 2000 | 1130 | 113,040,000 | 113,000,000 | pass | 1 | 1 |
| bad_claim | 180 | 2000 | 1200 | 113,040,000 | 120,000,000 | fail | 0 | 1 |

For the exact match:

$$
100000 \cdot 1130 = 113{,}000{,}000 \le 113{,}040{,}000 = 314 \cdot 180 \cdot 2000
$$

$$
314 \cdot 180 \cdot 2000 = 113{,}040{,}000 < 113{,}100{,}000 = 100000 \cdot 1131
$$

Both inequalities hold, so \(\mathrm{o1} = 1\).

For the bad claim:

$$
100000 \cdot 1200 = 120{,}000{,}000 > 113{,}040{,}000 = 314 \cdot 180 \cdot 2000
$$

The lower bound fails, so \(\mathrm{o1} = 0\). The range check still passes (\(\mathrm{o2} = 1\)) because all three inputs are within bounds.

### Kidney trace walkthrough

Two cases show how the gate blocks a wrong action class and allows the right one:

| flag | bad_watch | repeat_ok |
|---|---|---|
| complete (i1) | 1 | 1 |
| fresh (i2) | 1 | 1 |
| red_flag (i3) | 0 | 0 |
| below_60 (i4) | 1 | 1 |
| propose_watch (i5) | **1** | 0 |
| propose_repeat (i6) | 0 | **1** |
| propose_human (i7) | 0 | 0 |
| one_hot (i8) | 1 | 1 |
| **o1** | **0** | **1** |
| o2 | 0 | 0 |

In the bad_watch case, the model proposes watch even though eGFR is below 60. The watch branch of the Tau spec has the factor \((1 - \mathrm{i4})\):

$$
1 - 1 = 0
$$

That zero kills the entire watch product, so \(\mathrm{o1} = 0\). The gate denies the action.

In the repeat_ok case, the model instead proposes repeat_lab. The repeat branch has the factor \(\mathrm{i4}\):

$$
\mathrm{i4} = 1
$$

All other factors in the repeat product are also 1, so \(\mathrm{o1} = 1\). The gate allows the action.

## Part IX: interactive lab

<figure class="fp-figure">
  <p class="fp-figure-title">Interactive: decidable medical machines lab</p>
  <iframe
    src="{{ '/medical_decidable_machines_lab.html' | relative_url }}"
    title="Interactive decidable medical machines lab"
    style="width: 100%; border: 0; overflow: hidden"
    height="1880"
    loading="lazy"
    data-fp-resize="true"></iframe>
  <figcaption class="fp-figure-caption">
    The lab shows the same object through several surfaces. The calorie lane is a direct arithmetic checker. The kidney lane computes eGFR from the official adult equation, then runs an educational follow-up gate. Recorded Tau traces keep the public evidence replayable.
  </figcaption>
</figure>

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Suggested explorations</p>
  <ul>
    <li>In the calorie tab, enter weight 180 lb and body fat 20.0%. Confirm the floor check accepts a claimed deficit of 1130 kcal. Then change the claim to 1200 and watch the formula match fail.</li>
    <li>Switch to the kidney tab. Enter creatinine 1.1 mg/dL, age 55, sex female, and confirm eGFR appears near 59.34.</li>
    <li>With result_complete and result_fresh toggled on and red_flag off, propose <code>watch</code>. The gate should deny it because eGFR is below 60. Change the proposal to <code>repeat_lab</code> and the gate should accept.</li>
    <li>Toggle the red_flag on. Any non-human-review proposal should be denied. Propose <code>human_review</code> and the gate should accept.</li>
    <li>Toggle result_fresh off. Even without a red flag, the stale-data lane forces <code>human_review</code>.</li>
  </ul>
</div>

## Part X: what to take away

Small medical software need not begin with opaque reasoning algorithms.

It can begin with tiny, decidable machines:

- calculators,
- classifiers,
- gates,
- temporal freshness checks,
- and explicit escalation paths.

Once those machines are visible, the same object can be seen as:

- a formula,
- a decision tree,
- a finite-state machine,
- ordinary code,
- a spreadsheet,
- or a Tau specification.

That is the main lesson.

Every object in this tutorial satisfies the totality property from Part I:

$$
\forall x \ \exists n \ \mathrm{run}(M,x,n) \in F
$$

The calorie calculator is a total function: every bounded input reaches a floor result or an out-of-range error.
The kidney policy is a finite decision tree over a bounded flag surface: every fact pattern designates one admissible class, and a wrong proposal is denied rather than silently executed.
In both cases, every input reaches a definite outcome, with no loops and no unresolved states. That is decidability in practice.

The code may change.
The notation may change.
The shape does not have to change.

The next layer up composes these decidable machines inside the MPRD architecture from [Tutorial 22]({{ '/tutorials/medical-deciders-mprd-and-tau/' | relative_url }}).
