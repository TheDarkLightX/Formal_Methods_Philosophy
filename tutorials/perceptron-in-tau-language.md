---
title: "A perceptron in Tau Language"
layout: docs
kicker: Tutorial 21
description: Build a perceptron from formulas, map it into Tau specs, inspect real execution traces, and separate what Tau proves from what a host-side learning loop explores.
---

This tutorial turns a real Tau experiment into a teaching artifact.

The object is small on purpose: a two-input perceptron. That size is enough to show what a perceptron is, what weights mean, how a classifier becomes a logical invariant, how a Tau runner executes the spec, and where learning belongs when the public goal is clarity rather than hype.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Assumption hygiene</p>
  <ul>
    <li><strong>Bounded arithmetic:</strong> the executable Tau examples on this page use bounded bitvectors. The unsigned lane uses values in <code>0..127</code>.</li>
    <li><strong>Evidence scope:</strong> the replayable Tau evidence on this page covers three working lanes: external unsigned weights, signed-offset encoding, and internal spec-stored weights.</li>
    <li><strong>Learning scope:</strong> the interactive demo shows a host-side learning loop and displays Tau-friendly encodings of that state. This tutorial does not claim that the full signed learning rule is already a promoted Tau proof object.</li>
    <li><strong>License boundary:</strong> this site ships Tau specs, recorded traces, and a static demo. It does not redistribute the Tau product itself. Reproduction uses a local Tau installation obtained from the official upstream.</li>
  </ul>
</div>

## Part I: what a perceptron is

A perceptron is the smallest useful weighted classifier.

For two inputs, the core equations are:

$$
\mathrm{score} = x_1 w_1 + x_2 w_2 + b
$$

$$
\mathrm{class} =
\begin{cases}
1 & \text{if } \mathrm{score} \ge \theta \\
0 & \text{if } \mathrm{score} < \theta
\end{cases}
$$

The symbols mean:

- $x_1, x_2$ are the input features
- $w_1, w_2$ are the weights
- $b$ is the bias
- $\theta$ is the threshold
- $\mathrm{score}$ is the weighted sum before the decision

The weights say how strongly each input matters. The bias shifts the whole decision up or down. The threshold is the bar the score must clear to produce class 1.

In the plane, the decision boundary is:

$$
x_1 w_1 + x_2 w_2 + b = \theta
$$

Everything on one side is classified as 1, everything on the other side as 0.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Why this is a good Tau example</p>
  <p>
    A perceptron already has the shape Tau likes: a small number of streams, a bounded arithmetic relation, and an explicit Boolean claim to check. It is just complex enough to feel like machine learning, but still small enough that every number can be inspected by hand.
  </p>
</div>

## Part II: the invariant view

Before Tau syntax, write the logical shape.

For the unsigned external-weight version, define:

$$
\mathrm{BoundsOK}
:=
0 \le x_1,x_2,w_1,w_2,b,\theta \le 127
$$

$$
\mathrm{Score}
:=
x_1 w_1 + x_2 w_2 + b
$$

$$
\mathrm{ActualClass}
:=
(\mathrm{Score} \ge \theta)
$$

$$
\mathrm{PerceptronOK}
:=
\mathrm{BoundsOK}
\land
\big(
(\mathrm{ActualClass} \land \mathrm{claimed}=1)
\lor
(\neg \mathrm{ActualClass} \land \mathrm{claimed}=0)
\big)
$$

That is already the whole program, semantically.

Tau then makes that invariant executable over streams.

## Part III: external weights as Tau input streams

The first spec keeps the weights outside the Tau spec. The host supplies them just like any other input stream.

File:

`examples/tau/perceptron_2input_single_output_v1.tau`

Stream meaning:

- `i1 = x1`
- `i2 = x2`
- `i3 = w1`
- `i4 = w2`
- `i5 = bias`
- `i6 = threshold`
- `i7 = class_claimed`
- `o1 = perceptron_ok`

The core Tau clause is:

```tau
always
  (o1[t]:sbf = 1:sbf <->
    ((i1[t]:bv[16] <= { #x007F }:bv[16]) &&
     (i2[t]:bv[16] <= { #x007F }:bv[16]) &&
     (i3[t]:bv[16] <= { #x007F }:bv[16]) &&
     (i4[t]:bv[16] <= { #x007F }:bv[16]) &&
     (i5[t]:bv[16] <= { #x007F }:bv[16]) &&
     (i6[t]:bv[16] <= { #x007F }:bv[16]) &&
     ((((i1[t]:bv[16] * i3[t]:bv[16]) + (i2[t]:bv[16] * i4[t]:bv[16]) + i5[t]:bv[16]) >= i6[t]:bv[16] && i7[t]:sbf = 1:sbf) ||
      (((i1[t]:bv[16] * i3[t]:bv[16]) + (i2[t]:bv[16] * i4[t]:bv[16]) + i5[t]:bv[16]) < i6[t]:bv[16] && i7[t]:sbf = 0:sbf)))).
```

If that looks dense, read it in two passes:

1. the first six conjuncts are only range checks,
2. the last big disjunction is exactly the classifier rule.

The replayed trace for this tutorial uses two steps:

| step | inputs | score | threshold | actual class | claimed class | Tau output |
|---|---|---:|---:|---:|---:|---:|
| 0 | `(x1,x2,w1,w2,b) = (2,3,4,5,1)` | `24` | `20` | `1` | `1` | `o1 = 1` |
| 1 | `(x1,x2,w1,w2,b) = (2,1,1,2,0)` | `4` | `10` | `0` | `0` | `o1 = 1` |

The arithmetic is completely transparent:

$$
2 \cdot 4 + 3 \cdot 5 + 1 = 24 \ge 20
$$

$$
2 \cdot 1 + 1 \cdot 2 + 0 = 4 < 10
$$

The Tau runner captured both the structured outputs and the raw REPL trace. The recorded artifact lives in:

`assets/data/perceptron_tau_traces.json`

## Part IV: signed values without signed arithmetic

Real learning systems often want negative weights. Tau's bounded bitvector surface is easier to drive if those signed values are encoded into unsigned ones.

This tutorial's second spec uses an offset encoding:

$$
\mathrm{encode}(z) = z + 127
$$

$$
\mathrm{decode}(e) = e - 127
$$

So a logical value of `-2` is stored as `125`, a logical value of `0` is stored as `127`, and a logical value of `4` is stored as `131`.

The decoded perceptron rule is still:

$$
x_1 w_1 + x_2 w_2 + b \ge \theta
$$

but the Tau spec uses an equivalent unsigned inequality:

$$
x_{1e}w_{1e} + x_{2e}w_{2e} + b_e + 32258
\ge
127(x_{1e} + x_{2e} + w_{1e} + w_{2e}) + \theta_e
$$

File:

`examples/tau/perceptron_2input_signed_offset_v1.tau`

The replayed steps decode to:

| step | decoded inputs | decoded weights | decoded bias | decoded threshold | score | class | Tau output |
|---|---|---|---:|---:|---:|---:|---:|
| 0 | `(2,3)` | `(4,5)` | `1` | `0` | `24` | `1` | `o1 = 1` |
| 1 | `(-2,-3)` | `(4,5)` | `0` | `0` | `-23` | `0` | `o1 = 1` |

This matters because it creates a bridge:

- the host can think in signed learning variables,
- Tau can still check a bounded unsigned relation,
- the translation between the two is explicit and inspectable.

## Part V: moving the weights inside the spec

The third working lane removes the weights from the input interface entirely.

File:

`examples/tau/perceptron_2input_internal_weights_v1.tau`

Its logical shape is:

$$
\mathrm{Score}_{\mathrm{internal}}
:=
4x_1 + 5x_2 + 1
$$

$$
\mathrm{PerceptronInternalOK}
:=
\mathrm{BoundsOK}(x_1,x_2,\theta)
\land
\big(
(\mathrm{Score}_{\mathrm{internal}} \ge \theta \land \mathrm{claimed}=1)
\lor
(\mathrm{Score}_{\mathrm{internal}} < \theta \land \mathrm{claimed}=0)
\big)
$$

The important modeling change is not mathematical. It is architectural.

In the external-weight lane, the host controls the weights every step.

In the internal-parameter lane, the host controls only:

- `x1`
- `x2`
- `threshold`
- `claimed class`

The spec itself owns the parameters.

This is the smallest precise meaning of "weights stored internally."

There is also a stronger temporal meaning of internal storage in Tau.

If a parameter is carried by an output stream, then Tau can describe memory with recurrences such as:

$$
w_1[t] = w_1[t-1] + \Delta w_1[t]
$$

$$
w_2[t] = w_2[t-1] + \Delta w_2[t]
$$

$$
b[t] = b[t-1] + \Delta b[t]
$$

That is the precise sense in which weights can live in Tau-visible memory rather than arriving fresh from the host at every step.

For this public tutorial, the promoted replayed evidence stays with the three faster classifier lanes above. During preparation, recurrent memory variants were explored, but the stronger learning-shaped versions did not stay inside a tutorial-friendly runner budget. So the memory idea is real, but the public trace bundle on this page is scoped to the smaller verified fragment.

The replayed trace again uses two steps:

| step | inputs | internal parameters | score | threshold | actual class | Tau output |
|---|---|---|---:|---:|---:|---:|
| 0 | `(x1,x2) = (2,3)` | `(w1,w2,b) = (4,5,1)` | `24` | `20` | `1` | `o1 = 1` |
| 1 | `(x1,x2) = (2,1)` | `(w1,w2,b) = (4,5,1)` | `14` | `15` | `0` | `o1 = 1` |

## Part VI: what the Tau runner actually does

The public tutorial does not ship the Tau product.
It ships:

- the Tau specs,
- recorded execution traces,
- a regeneration script,
- a host-side interactive demo.

The regeneration path is:

1. use a local Tau checkout from official upstream,
2. import the Tau runner from a local Autonomous Tau DEX checkout,
3. write the concrete stream values to temporary files,
4. invoke Tau locally,
5. collect `stdout`, `stderr`, the generated REPL script, and the output files.

The script is:

`scripts/generate_perceptron_tau_artifacts.py`

It writes:

`assets/data/perceptron_tau_traces.json`

There is now a second local path for readers who want to run the current workbench state through a real local Tau install without rebuilding the trace bundle.

The bridge script is:

`scripts/tau_local_bridge.py`

Its shape is deliberately narrow:

1. the page sends only the current perceptron mode and the bounded stream values for that mode,
2. the localhost bridge validates those inputs,
3. the bridge invokes the reader's own local Tau install against one of the three whitelisted perceptron specs,
4. the bridge returns structured JSON with the resulting Tau output and a short trace excerpt.

The browser never scans the disk for Tau and it never executes local binaries by itself. The reader opts in by running the bridge locally.

The setup is:

1. install Tau from the official upstream repository, `https://github.com/IDNI/tau-lang`
2. from the repo root, run `python3 scripts/tau_local_bridge.py`
3. open the lab and click `Check local bridge`
4. click `Run current step with local Tau`

## Part VI.a: where to download the exact files

Everything needed for independent verification is in the public repository.

Repository:

- [Formal Methods Philosophy](https://github.com/TheDarkLightX/Formal_Methods_Philosophy)

Promoted perceptron specs:

- [perceptron_2input_single_output_v1.tau](https://github.com/TheDarkLightX/Formal_Methods_Philosophy/blob/main/examples/tau/perceptron_2input_single_output_v1.tau)
- [perceptron_2input_signed_offset_v1.tau](https://github.com/TheDarkLightX/Formal_Methods_Philosophy/blob/main/examples/tau/perceptron_2input_signed_offset_v1.tau)
- [perceptron_2input_internal_weights_v1.tau](https://github.com/TheDarkLightX/Formal_Methods_Philosophy/blob/main/examples/tau/perceptron_2input_internal_weights_v1.tau)

Supporting public artifacts:

- [perceptron_tau_traces.json](https://github.com/TheDarkLightX/Formal_Methods_Philosophy/blob/main/assets/data/perceptron_tau_traces.json)
- [generate_perceptron_tau_artifacts.py](https://github.com/TheDarkLightX/Formal_Methods_Philosophy/blob/main/scripts/generate_perceptron_tau_artifacts.py)
- [tau_local_bridge.py](https://github.com/TheDarkLightX/Formal_Methods_Philosophy/blob/main/scripts/tau_local_bridge.py)
- [tau_perceptron_lab.html](https://github.com/TheDarkLightX/Formal_Methods_Philosophy/blob/main/tau_perceptron_lab.html)

The shortest local path is:

1. clone the repository,
2. install Tau from official upstream,
3. run the bridge with `python3 scripts/tau_local_bridge.py`,
4. open the lab and compare the local Tau result with the recorded public trace bundle.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">License-safe teaching pattern</p>
  <p>
    The site shows formulas, specs, traces, and a static browser demo. Reproduction uses the reader's own local Tau installation, optionally through a localhost helper that the reader starts deliberately. That keeps the educational value while avoiding public redistribution of the Tau product itself.
  </p>
</div>

## Part VII: how the demo shows learning

The interactive lab below goes one step beyond the replayed Tau traces.

It shows a host-side learning loop for a two-input perceptron:

$$
w' = w + \eta (y - \hat{y}) x
$$

$$
b' = b + \eta (y - \hat{y})
$$

where:

- $y$ is the target label,
- $\hat{y}$ is the current prediction,
- $\eta$ is the learning rate.

Written per coordinate, the same update is:

$$
w_{1,t+1} = w_{1,t} + \eta (y_t - \hat{y}_t) x_{1,t}
$$

$$
w_{2,t+1} = w_{2,t} + \eta (y_t - \hat{y}_t) x_{2,t}
$$

$$
b_{t+1} = b_t + \eta (y_t - \hat{y}_t)
$$

This is where "the perceptron can learn" becomes visible.

The right mathematical boundary is linear separability.

A binary dataset $D$ is linearly separable when there exist weights and bias such that every positive point lands strictly on one side of the boundary and every negative point lands strictly on the other:

$$
\exists w_1,w_2,b.\;
\forall (x_1,x_2,y)\in D.\;
\big(
y = 1 \rightarrow w_1x_1 + w_2x_2 + b > 0
\big)
\land
\big(
y = 0 \rightarrow w_1x_1 + w_2x_2 + b < 0
\big)
$$

That is why the demo includes both converging and non-converging presets:

- OR, AND, and NAND are linearly separable,
- XOR is not.

In the XOR case, the useful lesson is not "the learner failed mysteriously." It is "one line cannot separate those four corners."

The demo does three things at once:

- it shows the decision boundary moving in the plane,
- it updates the signed weights and bias step by step,
- it displays the offset-encoded Tau-facing representation of that same signed state.
- it keeps a visible mistake count and epoch history, so convergence is not only felt visually, it is counted explicitly.

That last point is the bridge back to Tau.

The learning loop is host-side.
The representation bridge is explicit.
The classifier relation is the same one Tau checked in the replayed evidence.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Why the full learning rule is not in the promoted Tau lane here</p>
  <p>
    A bounded recurrent Tau learning lane was explored during preparation for this tutorial. Under the current public runner budget, those stronger temporal variants became much more search-heavy than the three promoted classifier lanes. That is a useful lesson, not a failure: some relations are clean enough to promote immediately as executable invariant checks, while others are better taught first as host loops with explicit, checkable state encodings and replayable trace boundaries.
  </p>
</div>

## Part VIII: the interactive perceptron lab

<figure class="fp-figure">
  <p class="fp-figure-title">Interactive: Tau perceptron lab</p>
  <iframe
    src="{{ '/tau_perceptron_lab.html' | relative_url }}"
    title="Interactive Tau perceptron lab"
    style="width: 100%; border: 0; overflow: hidden"
    height="1480"
    loading="lazy"
    data-fp-resize="true"></iframe>
  <figcaption class="fp-figure-caption">
    The lab combines three replayed Tau trace lanes with a host-side learning visualization. It also exposes an optional localhost bridge for readers who want the current workbench state checked by a real local Tau install. The line that moves during learning is the geometric face of the same weighted-sum classifier encoded in the Tau specs above.
  </figcaption>
</figure>

## Part IX: what to take away

The experiment compresses into five lessons.

1. A perceptron is already a logic object: a weighted sum plus a thresholded claim.
2. Tau is a natural fit for bounded classifier relations and explicit acceptance predicates.
3. External weights, signed encodings, and internal parameters are different interface choices over the same underlying classifier.
4. Tau can represent internal memory through time-indexed streams, but the promoted public evidence on this page stays with the faster classifier fragment.
5. Learning can be shown honestly as a host-side state update with explicit convergence and failure stories, while Tau stays in the role it handles best here: executable invariant checker over a sharply stated bounded relation.
