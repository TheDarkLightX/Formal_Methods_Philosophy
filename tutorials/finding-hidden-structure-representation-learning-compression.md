---
title: "Finding the Hidden Road: Representation Learning as Compression"
layout: docs
kicker: Tutorial 72
description: "How representations expose low-dimensional regularities, why abstraction often compresses, and what three bounded Qgent experiments actually found."
---

Imagine searching a haystack for a needle.

That image is useful, but incomplete. Representation learning usually does not
recover one secret sentence hidden in the data. It searches for a smaller
coordinate system, a collection of recurring patterns, or a family of
invariants that organizes many observations at once.

The haystack is the raw data. The representation is a road through it.

<pre>
raw observations
many coordinates, noise, and accidental detail
             |
             v
find repeatable structure
             |
             v
compact coordinates, clusters, or invariants
             |
             v
reconstruct, predict, or decide
</pre>

This tutorial develops that picture from Buchanan, Pai, Wang, and Ma's
[*Principles and Practice of Deep Representation Learning: or a Mathematical
Theory of Memory*](https://arxiv.org/abs/2606.06624), then tests the ideas on a
compiled Q memory.

<div class="fp-callout fp-callout-warning">
  <p class="fp-callout-title">Assumption: useful structure exists</p>
  <p>
    Compression helps only when observations contain repeatable structure at
    the chosen scale. If task-relevant variation is irreducibly random, a
    shorter representation must discard it or memorize it under another name.
  </p>
</div>

## 1. A giant room with a narrow road

Suppose an image is stored as a vector with $D$ pixel values:

$$
\mathbf{x}\in\mathbb{R}^{D}.
$$

Every possible pixel array is a point in a $D$-dimensional room. Most points
look like noise. Natural images occupy a much more organized region.

A common mathematical model says that useful observations lie near a set
$\mathcal{M}$ with far fewer effective dimensions:

$$
\mathcal{M}\subset\mathbb{R}^{D},
$$

with

$$
d\ll D.
$$

The visible object has $D$ coordinates, while only $d$ coordinates may explain
the variation that matters for a task.

Those compact coordinates are not automatically laws of nature. They may
describe:

- pose, lighting, or viewpoint;
- a linear subspace;
- a sparse combination of reusable parts;
- an invariant under a transformation;
- a recurring decision regime;
- a correlation that has not been shown to be causal.

## 2. The smallest example: data near a line

Consider two-dimensional measurements that approximately satisfy

$$
x_2=2x_1.
$$

One number $t$ almost determines both coordinates:

$$
\mathbf{x}
=
\begin{bmatrix}
t\\
2t
\end{bmatrix}
+
\boldsymbol{\varepsilon}.
$$

The scalar $t$ is a compact coordinate. The vector
$\boldsymbol{\varepsilon}$ contains whatever the line does not explain.

Principal component analysis finds a direction $U$ and projects the observation
onto it:

$$
\widehat{\mathbf{x}}=UU^\top\mathbf{x}.
$$

The projection can be three things at once:

- an abstraction, because off-line differences are ignored;
- a compression, because one coordinate can replace two;
- a denoiser, if the discarded direction really is noise.

The final condition is essential. If a rare safety signal lies in the discarded
direction, projection destroys knowledge.

## 3. Abstraction and compression are related, not identical

An abstraction maps detailed objects into a simpler domain:

$$
\alpha:X\rightarrow A.
$$

It induces an equivalence relation:

$$
x\sim_\alpha y
\quad\Longleftrightarrow\quad
\alpha(x)=\alpha(y).
$$

The abstraction declares that $x$ and $y$ are interchangeable for its intended
purpose.

<pre>
x1 ----\
x2 -----+----> abstract code a
x3 ----/
</pre>

This often compresses because many detailed objects share one code. The ideas
still differ:

- Abstraction states which distinctions are ignored.
- Compression reduces the storage needed for the retained distinctions.
- A task-valid abstraction preserves every distinction needed by that task.

An abstraction may even make one description longer. Naming reusable proof
steps or program components adds symbols locally while shortening an entire
family of later descriptions.

## 4. Lossy compression requires a declared distortion

Representation learning usually permits bounded reconstruction error:

<pre>
observation x
     |
     v
encoder f
     |
     v
representation z
     |
     v
decoder g
     |
     v
reconstruction x-hat
</pre>

The mathematical promise has the form

$$
d\bigl(x,g(f(x))\bigr)\leq\varepsilon.
$$

Three choices determine what this means:

1. The distortion $d$ states which differences matter.
2. The tolerance $\varepsilon$ states how much difference is allowed.
3. The evaluation distribution states where the promise is tested.

Pixel error, semantic error, physical error, Q-value error, and decision error
are different quantities. Good compression under one does not imply safety
under another.

For a feature matrix

$$
Z=[z_1,\ldots,z_N]\in\mathbb{R}^{d\times N},
$$

the book studies a coding-rate expression of the form

$$
R_\varepsilon(Z)
=
\frac{1}{2}
\log\det\left(
I+\frac{d}{N\varepsilon^2}ZZ^\top
\right).
$$

Read it in four stages:

1. $ZZ^\top/N$ describes directions of feature variation.
2. $\varepsilon$ specifies the resolution.
3. The determinant measures occupied volume at that resolution.
4. The logarithm turns multiplicative volume into an additive rate.

The assumptions and derivation are explained in the book's
[lossy-compression chapter](https://ma-lab-berkeley.github.io/deep-representation-learning-book/Ch4.html).

## 5. A useful code must separate families

Compression alone has a trivial solution: map every observation to one code.
That code is short and useless.

A representation should make members of one family compact while keeping
different families distinguishable.

Let $Z_k$ contain the features assigned to family $k$. A within-family rate is

$$
R_\varepsilon^c(Z)
=
\sum_{k=1}^{K}
\frac{N_k}{2N}
\log\det\left(
I+\frac{d}{N_k\varepsilon^2}Z_kZ_k^\top
\right).
$$

Maximal coding-rate reduction uses the difference

$$
\Delta R_\varepsilon(Z)
=
R_\varepsilon(Z)-R_\varepsilon^c(Z).
$$

The first term rewards a globally expressive representation. The second
penalizes spread within each declared family. Feature normalization is needed,
otherwise scale alone can distort the objective.

The construction is developed in the
[coding-rate-reduction chapter](https://ma-lab-berkeley.github.io/deep-representation-learning-book/Ch5.html).

## 6. Does this discover hidden rules?

Sometimes it discovers a useful invariant. Sometimes it discovers a shortcut.

A compact pattern can arise from:

- a genuine mechanism;
- a symmetry;
- a repeated but noncausal correlation;
- the data collection process;
- label leakage;
- a feature that disappears after distribution shift.

Compression provides evidence of regularity under a declared representation
and distortion. It does not, by itself, establish causality.

Causal language needs more. Depending on the claim, that may include
interventions, invariance across environments, temporal assumptions, controlled
experiments, or a formal mechanism.

The honest phrase is therefore:

> Representation learning can expose compact regularities. Calling those
> regularities laws requires additional evidence.

## 7. What a layer means

The word *layer* is overloaded.

| Kind of layer | What changes |
| --- | --- |
| Neural or unrolled layer | A representation is transformed by one learned or optimization-inspired step |
| Q-horizon layer | The number of future decisions remaining changes |
| Lookup-resolution layer | A coarse table is refined by smaller residuals |
| Abstraction layer | Several concrete states share a code |

Unrolled optimization provides a useful bridge. One iteration such as

$$
z_{k+1}
=
\operatorname{prox}_{\lambda R}
\left(
z_k-\eta\nabla D(z_k)
\right)
$$

can become one network layer:

$$
z_{k+1}=F_{\theta_k}(z_k,x).
$$

Depth then means repeated refinement. It does not mean planning farther into
the future unless the recurrence explicitly represents time and transition.
The book develops this connection in its
[chapter on unrolled optimization](https://ma-lab-berkeley.github.io/deep-representation-learning-book/Ch6.html).

## 8. Lookup Q-tables and shared-feature Q models

A literal Q-table stores one value for every represented state-action pair:

$$
Q:S\times A\rightarrow\mathbb{R}.
$$

It can also be written as a weighted model with one one-hot feature per pair.
There is no parameter sharing:

$$
Q(s,a)=w_{s,a}.
$$

A shared-feature model instead uses

$$
\widehat Q(s,a)=w_a^\top\phi(s,a).
$$

Many states reuse the same coefficients. This can compress and interpolate, but
it can also impose the wrong geometry.

The 100-step Qgent lab uses both forms at different stages:

1. Exact dynamic programming labels bounded synthetic worlds.
2. An action-conditional linear model fits 34 shared features.
3. The fitted scores are compiled into a literal deployment table.

This is not model-free Q-learning. The transition and reward model is authored,
and exact dynamic programming supplies the training targets.

More table rows also do not automatically mean more knowledge. New rows count
as new experience only when their values come from additional observations or
checked consequences that improve independent evaluation. Enumerating more
states from the same authored formula may only repeat the formula.

## 9. Choose distortion for the decision

Ordinary score error treats every numerical difference alike. A deployed
decision system often cares first about whether the selected action changes.

For permitted actions $A_D(s)$, define

$$
g_Q(s)
=
\min\operatorname*{arg\,max}_{a\in A_D(s)}Q(s,a).
$$

The minimum implements a fixed deterministic tie order.

A decision-aware distortion can separate two questions:

$$
d_{\mathrm{policy}}(Q,\widehat Q;s)
=
\mathbf{1}\left[g_Q(s)\neq g_{\widehat Q}(s)\right],
$$

and

$$
d_{\mathrm{score}}(Q,\widehat Q;s)
=
\max_{a\in A_D(s)}
\left|Q(s,a)-\widehat Q(s,a)\right|.
$$

The first checks behavior. The second checks numerical fidelity. Reporting both
prevents a tiny action list from being mistaken for a compressed Q memory.

## 10. Remove a deployment symmetry first

For any state-dependent constant $c(s)$,

$$
Q_c(s,a)=Q(s,a)+c(s)
$$

has the same maximizing actions at that state:

$$
\operatorname*{arg\,max}_{a\in A_D(s)}Q_c(s,a)
=
\operatorname*{arg\,max}_{a\in A_D(s)}Q(s,a).
$$

This suggests a quotient representation. Separate the common value

$$
V(s)=\max_{a\in A_D(s)}Q(s,a)
$$

from the relative advantage

$$
A(s,a)=Q(s,a)-V(s).
$$

Every permitted advantage satisfies

$$
A(s,a)\leq 0.
$$

The maximizing actions have advantage zero.

For an even integer step $\Delta$, the lab stores

$$
\overline V(s)
=
\Delta
\left\lfloor
\frac{V(s)+\Delta/2}{\Delta}
\right\rfloor
$$

and

$$
\overline A(s,a)
=
\Delta
\left\lfloor
\frac{A(s,a)}{\Delta}
\right\rfloor.
$$

The reconstructed score is

$$
\widehat Q(s,a)
=
\overline V(s)+\overline A(s,a).
$$

### Policy-preservation lemma

Assume the permitted set is nonempty and the integer codes do not overflow.
Then the maximizing action set of $\widehat Q$ is exactly the maximizing action
set of $Q$.

**Proof.**

If $a$ maximizes $Q$, then $A(s,a)=0$, so

$$
\overline A(s,a)=0.
$$

If $a$ is strictly below the maximum, then $A(s,a)<0$. Therefore

$$
\left\lfloor
\frac{A(s,a)}{\Delta}
\right\rfloor
\leq -1,
$$

and hence

$$
\overline A(s,a)\leq-\Delta.
$$

The common term $\overline V(s)$ cannot change this order. Tied maxima remain
tied, strict nonmaxima remain strict nonmaxima, and the deterministic tie rule
selects the same action. $\square$

The score error is also bounded. Nearest-grid value coding gives

$$
\left|V(s)-\overline V(s)\right|
\leq\frac{\Delta}{2}.
$$

Downward advantage coding gives

$$
0
\leq
A(s,a)-\overline A(s,a)
<
\Delta.
$$

Combining them yields

$$
\left|Q(s,a)-\widehat Q(s,a)\right|
<
\frac{3\Delta}{2}.
$$

This lemma is elementary. The useful design step is choosing the correct
quotient and a one-sided quantizer before applying a general-purpose codec.

## 11. Why ordinary rounding failed

Rounding a small negative advantage to the nearest grid point can produce zero:

$$
-\frac{\Delta}{2}<A(s,a)<0
\quad\Longrightarrow\quad
\operatorname{round}\left(\frac{A(s,a)}{\Delta}\right)=0.
$$

A strict loser then becomes tied with the winner. If its action identifier is
smaller, deterministic tie-breaking changes the decision.

At the selected step $\Delta=256$, nearest rounding caused:

- 275 strict-negative cells to become zero;
- 273 state rows to lose at least one strict gap;
- 101 greedy-action mismatches.

The downward quantizer caused zero mismatches. This is a checked
abstraction-level counterexample: the general idea of quantization survived,
while the nearest-rounding abstraction was rejected.

## 12. Lab result: a denser Q memory

The source table has 27,000 state rows, nine action slots per row, and 972,000
raw bytes.

The strongest lossless control in the lab is not ordinary compression. It
removes deterministically forbidden cells, takes temporal differences,
byte-shuffles the signed integers, and applies zlib level 9.

| Representation | Bytes | Preserves Q scores exactly? | Preserves selected actions? |
| --- | ---: | --- | --- |
| Raw signed-32 table | 972,000 | Yes | Yes |
| Strong lossless Q payload | 114,690 | Yes | Yes |
| Complete decision-quotient artifact | 102,799 | No, maximum error 382 | Yes, 0 of 27,000 changed |
| Policy-only compressed payload | 1,458 | No Q scores retained | Yes |

The complete quotient artifact is:

- 89.4 percent smaller than the raw table;
- 10.4 percent smaller than the optimistic payload-only lossless control;
- within the declared 400-milliunit maximum-error budget;
- byte-identical across duplicate builds;
- bound to the source hash;
- fail-closed under corrupted stream, wrong source, and wrong magic tests.

The policy-only control is far smaller because it answers only *which action*.
It cannot answer how close the alternatives were, reconstruct approximate
Q-values, or support value-sensitive inspection.

The quotient codec improves density. It does not improve the learned policy or
add knowledge.

## 13. Lab result: better validation, worse confirmation

A second experiment tested whether representation geometry could improve the
model itself.

The candidate added nine distances from each state representation to
optimal-action centroids:

$$
\phi_{\mathrm{candidate}}(s,a)
=
\begin{bmatrix}
\phi_{\mathrm{base}}(s,a)\\
\lVert z(s)-\mu_1\rVert^2\\
\vdots\\
\lVert z(s)-\mu_9\rVert^2
\end{bmatrix}.
$$

This expanded the linear model from 34 to 43 features. It was trained on 16
worlds and selected using 12 validation worlds.

| Metric | Validation baseline | Validation candidate | Confirmation baseline | Confirmation candidate |
| --- | ---: | ---: | ---: | ---: |
| Mean optimal-utility ratio | 0.98350 | 0.98669 | 0.98538 | 0.98351 |
| Minimum optimal-utility ratio | 0.95753 | 0.97048 | 0.97245 | 0.91959 |
| Exact-action agreement | 0.87167 | 0.88083 | 0.87150 | 0.86750 |
| Mean gain over myopic | 2,247.67 | 2,269.92 | 2,173.73 | 2,163.25 |

The candidate improved every declared validation metric. On a disjoint
40-world confirmation block, it worsened every one. The minimum ratio fell
especially sharply.

The candidate was rejected.

This negative result carries useful knowledge:

- Visible class separation does not guarantee better sequential decisions.
- Validation improvement can coexist with worse fresh-world robustness.
- A representation must be judged through the complete rollout, not only by
  isolated feature geometry.

The result refutes this fixed centroid feature design. It does not refute
representation learning, coding-rate objectives, centroid methods, or nonlinear
Q models in general.

## 14. Lab result: a curved coordinate map replicated

A straight decision boundary can miss a curved regularity. The next candidate
kept the original 34 features and added a small nonlinear coordinate system.

Start with 29 state-only features in a vector $x$. Standardize them using
training-set statistics:

$$
\widetilde{x}_j
=
\frac{x_j-\mu_j}{\sigma_j}.
$$

PCA then rotates the standardized vector into learned coordinates:

$$
z_i=u_i^\top\widetilde{x}.
$$

The selected model retained ten coordinates. It appended every quadratic
interaction $z_i z_j$ with $i\leq j$:

$$
\psi(s,a)
=
\begin{bmatrix}
\phi_{\mathrm{base}}(s,a)\\
z_1^2\\
z_1z_2\\
\vdots\\
z_{10}^2
\end{bmatrix}.
$$

Ten coordinates produce

$$
\frac{10(10+1)}{2}=55
$$

quadratic terms. The model therefore grew from 34 to 89 features. Candidate
ranks $2,4,6,8,10$ and training budgets of 16 or 32 worlds were compared on
the validation split. Validation selected rank 10 with 32 training worlds.

That larger training budget creates a possible confound. The confirmation
comparison therefore includes two controls:

- the frozen 16-world, 34-feature model;
- a 32-world, 34-feature linear model trained on exactly as many worlds as the
  candidate.

| Confirmation metric, 40 worlds | Frozen linear, 16 worlds | Plain linear, 32 worlds | PCA-quadratic, 32 worlds |
| --- | ---: | ---: | ---: |
| Mean optimal-utility ratio | 0.98291 | 0.98229 | **0.98426** |
| Minimum optimal-utility ratio | 0.96169 | 0.96169 | **0.96209** |
| Exact-action agreement | 0.85250 | 0.84775 | **0.85475** |
| Mean gain over myopic | 2,231.48 | 2,229.23 | **2,244.13** |
| Forbidden selections | 0 | 0 | 0 |

Against the stronger control for each metric, the candidate increased mean
utility ratio by about 0.00135, minimum ratio by about 0.00040, exact-action
agreement by 0.00225, and gain over myopic by 12.65 utility units. These are
small improvements. They occurred on one disjoint block drawn from the same
synthetic generator.

The timing matters. The equal-data linear control was added after the first
confirmation readout, although the candidate was not changed afterward. The
result is bounded exploratory evidence for this representation, rather than a
fully preregistered comparison. All 40 confirmation seeds are now consumed and
cannot be reused to tune a successor.

The next test froze the candidate, both controls, seed blocks, metrics, and
acceptance rule in a committed protocol before evaluation. The primary block
contained 80 untouched worlds from the unchanged generator.

| Preregistered primary metric, 80 worlds | Frozen linear, 16 worlds | Plain linear, 32 worlds | PCA-quadratic, 32 worlds |
| --- | ---: | ---: | ---: |
| Mean optimal-utility ratio | 0.98395 | 0.98259 | **0.98597** |
| Minimum optimal-utility ratio | 0.92191 | 0.92570 | **0.96118** |
| Exact-action agreement, diagnostic | **0.86275** | 0.84838 | 0.86163 |
| Mean gain over myopic | 2,190.50 | 2,182.75 | **2,203.53** |
| Forbidden selections | 0 | 0 | 0 |

The candidate produced greater rollout utility on 52 of 80 worlds against the
frozen control and 57 of 80 against the equal-data control. The corresponding
two-sided exact sign-test values were about 0.0097 and 0.00018. These paired
tests were declared diagnostics, not selection gates.

The candidate had slightly lower exact-action agreement than the frozen
control, 0.86163 rather than 0.86275, while achieving higher rollout utility.
Agreement asks how often two policies choose the same action. Utility asks how
well the entire trajectory scores. They need not move together.

### A narrow population shift

A separate preregistered stress block used all cyclic rotations of the
population profile $(1,1,8,12)$. Training populations were each between 2 and
6, so this moved one declared generator factor outside its training range.

| Population-shift metric, 40 worlds | Frozen linear, 16 worlds | Plain linear, 32 worlds | PCA-quadratic, 32 worlds |
| --- | ---: | ---: | ---: |
| Mean optimal-utility ratio | 0.84472 | 0.83691 | **0.96848** |
| Minimum optimal-utility ratio | 0.75926 | 0.77409 | **0.87316** |
| Exact-action agreement, diagnostic | 0.39475 | 0.36700 | **0.80525** |
| Mean gain over myopic | 3,004.80 | 2,901.05 | **4,678.25** |
| Forbidden selections | 0 | 0 | 0 |

The candidate beat each control on all 40 paired utility comparisons. One
plausible explanation is that quadratic interactions represent how resource
costs scale with population more effectively than the two linear controls.
That explanation remains a hypothesis. The experiment changed only one
factor, using a synthetic profile selected in advance. It does not establish
broad distributional robustness.

The
[frozen protocol is available here]({{ '/experiments/qgent_rate_structured_memory_v001/research/pca_quadratic_replication_protocol_v001.json' | relative_url }})
and the
[complete per-world report is available here]({{ '/experiments/qgent_rate_structured_memory_v001/results/qgent_pca_quadratic_replication_v001.report.json' | relative_url }}).

The
[experimental model can be downloaded here]({{ '/assets/downloads/qgent-pca-quadratic-feature-model-v1.json' | relative_url }}).
It remains a floating-point research artifact. It has not replaced the
quantized Qgent or entered the Tau-gated demo.

## 15. Generalization is a measured claim

Generalization has several meanings.

A model may interpolate between familiar samples, transfer across a bounded
distribution, preserve a known symmetry, or solve an unfamiliar task. These
are different claims.

For a declared distribution and hypothesis class, learning theory can prove
probabilistic bounds under assumptions. A trained large language model can
also demonstrate broad empirical transfer on held-out benchmarks. Neither fact
proves unrestricted general intelligence or reliable transfer to every new
domain.

In this lab, *generalization* first means performance on disjoint synthetic
world seeds from the same bounded generator. The centroid candidate failed
that narrow test. The frozen PCA-quadratic candidate passed an exploratory
confirmation and then a preregistered 80-world replication. It also passed one
preregistered population-shift stress test. That second result changes only one
generator factor, so neither result establishes transfer to a different world
model, a real allocation problem, or an unrestricted domain.

## 16. There is no universal intelligence-per-byte unit

Bytes are objective. Intelligence and morality are not single agreed physical
quantities.

A useful engineering report can state:

$$
\text{bytes per represented state},
$$

$$
\text{policy disagreements per state},
$$

$$
\text{maximum Q-score error},
$$

and

$$
\text{held-out utility regret}.
$$

It can also state the moral rule used to create rewards. None of these becomes
a universal measure of intelligence or morality merely by dividing by bytes.

For this one artifact:

- raw storage uses 36 bytes per state row;
- the strong lossless payload uses about 4.25 bytes per row;
- the complete quotient artifact uses about 3.81 bytes per row;
- the policy-only payload uses about 0.054 bytes per row while discarding Q
  magnitudes.

These are density measurements under a fixed benchmark, not intelligence
scores.

## 17. Deployment equivalence is not Bellman equivalence

The statewise shift

$$
Q_c(s,a)=Q(s,a)+c(s)
$$

preserves a greedy decision at state $s$. It does not generally preserve a
Bellman backup.

A Bellman target contains a successor value:

$$
r(s,a,s')
+
\gamma
\max_{a'}Q(s',a').
$$

After a statewise shift, the successor term gains

$$
\gamma c(s').
$$

That change depends on the successor state. It cannot generally be removed by
one action-independent constant at the current state.

The quotient artifact is therefore suitable for replaying its compiled greedy
policy and inspecting approximate scores. It is not a drop-in replacement for
the source Q-table during retraining, fitted Q iteration, or Bellman
verification.

## 18. A disciplined synthetic pipeline

The broader pipeline is:

<pre>
propose states, abstractions, actions, and edge cases
                         |
                         v
canonicalize and deduplicate state keys
                         |
                         v
simulate or check consequences
                         |
                         v
compute exact or learned Q targets
                         |
                         v
search counterexamples and sparse regions
                         |
                         v
compile a table with provenance and uncertainty
                         |
                         v
compress under explicit policy and score constraints
</pre>

Each boundary has a separate question:

- Did the generator add genuinely different experience?
- Did the checker validate the consequence?
- Did the fitted model improve fresh-world rollout behavior?
- Did compression preserve the declared decision semantics?
- Can a corrupted or stale artifact fail closed?

Conflating these questions makes a large file look more knowledgeable than it
is.

## 19. Reproduce the lab

The public artifact can be
[downloaded here]({{ '/assets/downloads/qgent-decision-quotient-q-v1.qdq' | relative_url }}).

The source, tests, reports, and TheoremSearch retrieval-only receipts are in
the
[experiment directory](https://github.com/TheDarkLightX/Formal_Methods_Philosophy/tree/main/experiments/qgent_rate_structured_memory_v001).

From the repository root:

<pre>
python3 experiments/qgent_rate_structured_memory_v001/rate_structured_memory.py
python3 experiments/qgent_rate_structured_memory_v001/centroid_feature_probe.py
python3 experiments/qgent_rate_structured_memory_v001/pca_quadratic_feature_probe.py
python3 experiments/qgent_rate_structured_memory_v001/pca_quadratic_replication.py
PYTHONPATH=. pytest -q experiments/qgent_rate_structured_memory_v001/test_rate_structured_memory.py
</pre>

The feature probes are slower because they recompute exact dynamic-programming
labels and sequential rollouts. Their confirmation seeds are frozen evidence
and must not be reused as a fresh test for a redesigned model.

## 20. What the experiment changed

The representation-learning perspective produced three different outcomes.

First, the idea of optimal-action centroids looked promising on validation and
failed on confirmation. That idea became negative knowledge.

Second, PCA coordinates with quadratic interactions produced a small rollout
improvement on a disjoint confirmation block. A preregistered replication then
improved the declared utility metrics over both linear controls on 80 more
worlds. A separate one-factor population shift produced a larger improvement.
The equal-data control supports the inference that the feature map, rather
than training volume alone, contributed to the gain. The experiments do not
isolate which quadratic terms matter, and the shifted result does not imply
broad robustness.

Third, choosing the deployment decision as the distortion exposed a symmetry:
statewise Q offsets do not affect greedy action choice. Quotienting out that
symmetry, then using a sign-preserving quantizer, produced a smaller complete
artifact than a strong exact control.

The experiments found two useful roads: a compact quadratic coordinate system
for one bounded predictive task, and an equivalence relation that compresses a
compiled decision memory without changing its selected actions.

## Sources

- Sam Buchanan, Druv Pai, Peng Wang, and Yi Ma,
  [*Principles and Practice of Deep Representation Learning: or a Mathematical Theory of Memory*](https://arxiv.org/abs/2606.06624).
- [Chapter 4: Lossy Compression](https://ma-lab-berkeley.github.io/deep-representation-learning-book/Ch4.html).
- [Chapter 5: Coding Rate Reduction](https://ma-lab-berkeley.github.io/deep-representation-learning-book/Ch5.html).
- [Chapter 6: Unrolled Optimization](https://ma-lab-berkeley.github.io/deep-representation-learning-book/Ch6.html).

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Claim boundary</p>
  <p>
    The mathematical lemma is proved above and exhaustively checked on the
    frozen compiled table. The byte comparison is specific to this artifact
    and implemented controls. The predictive result is a small improvement on
    one consumed confirmation block from the same synthetic generator, with an
    equal-data control added after the first readout. The benchmark does not
    establish a real measure of welfare, morality, or general intelligence.
  </p>
</div>
