---
title: "GlassMind-256: A Proof-Carrying Deterministic Thinker"
layout: docs
kicker: Tutorial 71
description: "Build a 256-layer Q table from a pinned knowledge graph, a deontic action gate, and a checked finite-horizon recurrence, then compare literal lookup, shared-feature fitted Q, and language models."
---

A dense Q table can answer a decision question with one array lookup. If the state,
action, reward model, and planning horizon are explicit, the answer can also be
replayed exactly. That makes tabular planning attractive when a system needs a
small, closed decision surface with predictable behavior.

This tutorial builds **GlassMind-256**, a reproducible demonstration with 256
planning layers. Its public table contains 50,331,648 bytes of little-endian
`float32` Q data. A larger local profile contains exactly 536,870,912 bytes, or
512 MiB, of Q data.

The name "deterministic thinker" is an engineering nickname. The checked claim
is narrower: GlassMind performs exact finite-horizon dynamic programming inside
one declared model. It does not establish consciousness, unrestricted
reasoning, moral truth, or general intelligence.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Scope before scale</p>
  <ul>
    <li><strong>Knowledge:</strong> the demonstration uses a hash-pinned 2025 Open English WordNet release. Its lexical links are attributed source records, not formal proofs.</li>
    <li><strong>Generalization:</strong> GlassMind does not learn how to handle states outside its canonical key space. A fitted model or language model can compute an output for a new input, but correctness on new inputs is a task-scoped empirical or conditional statistical claim, not proof of general intelligence.</li>
    <li><strong>Norms:</strong> a finite deontic profile controls which actions are admissible. It is not a universal ethics theory.</li>
    <li><strong>Utility:</strong> a separate outcome model ranks only admissible actions. Alignment is relative to the declared facts, norms, utility, state abstraction, and bounds.</li>
    <li><strong>Time:</strong> layer 255 means 255 remaining decision steps. It does not mean a date, a clock tick, or the 255th neural-network layer.</li>
    <li><strong>Authority:</strong> the table is advisory unless a surrounding system explicitly grants it authority. Safety-critical or value-moving code should keep final acceptance in a deterministic gate.</li>
  </ul>
</div>

<figure class="fp-figure">
  <p class="fp-figure-title">A Q table can store one value surface per remaining horizon</p>
  <img
    src="{{ '/assets/images/glassmind/horizon-layer-stack.webp' | relative_url }}"
    alt="A stack of translucent gridded slabs with an amber path selecting one cell on each successive slab."
    class="fp-illustration"
    width="1440"
    height="960"
    decoding="async">
  <figcaption class="fp-figure-caption">
    Each slab represents a complete state-action table for one remaining horizon. The illustration shows only a few representative slabs so that the structure is visible. GlassMind addresses 256 logical slabs. The amber route is one candidate decision path, not a neural activation trace.
  </figcaption>
</figure>

## 1. What a Q value means

For a policy $\pi$, build the definition in two steps. First define the
discounted return from time zero:

$$
G_0=\sum_{t=0}^{\infty}\gamma^t R_{t+1}.
$$

Here $R_{t+1}$ is the reward received after step $t$, and $\gamma$ is the
discount factor. A smaller $\gamma$ makes distant rewards matter less.

Second, condition that return on the starting state and action:

$$
Q^{\pi}(s,a)
=
\mathbb{E}_{\pi}\!\left[G_0\mid S_0=s, A_0=a\right].
$$

The expectation averages over any randomness in the policy or environment.
In a fully deterministic finite model, it reduces to the return of the single
declared path.

The optimal value is the best value available across policies:

$$
Q^{\ast}(s,a)=\max_{\pi}Q^{\pi}(s,a).
$$

If $\pi^{\ast}$ is a policy that attains this maximum, then

$$
Q^{\ast}(s,a)=Q^{\pi^{\ast}}(s,a).
$$

Finally, a greedy optimal action is any action in

$$
\operatorname*{arg\,max}_{a} Q^{\ast}(s,a).
$$

### A table is also a one-hot weighted model

The word *weight* does not imply a neural network. A literal Q table can be
written as a linear model by assigning one indicator feature to every
state-action cell.

Let $C=S\times A$ be the set of table cells. For every $c\in C$, define

$$
\phi_c(s,a)
=
\begin{cases}
1 & \text{if }c=(s,a),\\
0 & \text{otherwise.}
\end{cases}
$$

Then a table lookup is exactly

$$
Q(s,a)=\sum_{c\in C}w_c\phi_c(s,a),
$$

where $w_c$ is the value stored in cell $c$. Exactly one feature is active, so
the sum retrieves one stored value. Calling table entries *weights* does not
turn the table into a neural network or an approximate model.

A shared-feature fitted model instead uses a smaller basis:

$$
\widehat Q_\theta(s,a)
=
\sum_{i=1}^{d}\theta_i\phi_i(s,a),
\qquad d\ll |S||A|.
$$

One feature can now affect many state-action pairs. This can compress the model
and compute estimates for unseen combinations. The architecture does not prove
that those estimates are correct. Shared features can also create interference
when the feature map merges situations that require different actions.

The separately scoped fitted-Q direction is named **BasisQ-256**.
GlassMind-256 remains the literal table. BasisQ-256 serves only as an
architectural comparison and supplies no evidence for GlassMind's claims.

| Representation | Stored object | Inference | Principal tradeoff |
| --- | --- | --- | --- |
| GlassMind-256 | Dense $Q[h,s,a]$ cells | Array lookup | Exact inside the enumerated model, but storage grows with the state space |
| Sparse layered table | Keyed Q cells and residual cells | Key lookup and addition | Exact for stored keys, but unseen keys require a declared fallback |
| BasisQ-256 | Shared features and coefficients | Dot product, then admissibility filtering | Compact shared prediction across states; held-out accuracy is empirical and feature-dependent |

<figure class="fp-figure">
  <p class="fp-figure-title">Literal address lookup versus shared-feature estimation</p>
  <img
    src="{{ '/assets/images/glassmind/table-versus-shared-features.webp' | relative_url }}"
    alt="On the left, three coordinates identify one glowing cell in a dense grid. On the right, a small set of colored feature columns connects to many output tiles and combines at one highlighted tile."
    class="fp-illustration"
    width="1440"
    height="790"
    loading="lazy"
    decoding="async">
  <figcaption class="fp-figure-caption">
    Left: a literal table stores an independently addressable value at every declared coordinate. Right: a fitted shared-feature model reuses a smaller set of coefficients across many states. Reuse enables compression and predictions for new combinations, but held-out tests must establish whether those predictions are useful. Reuse also couples errors between states.
  </figcaption>
</figure>

The fitted direction arose because almost every natural-language episode can
have a distinct raw key. A literal table cannot transfer to an unseen key
unless a declared canonicalizer or backoff map relates it to a stored state.
Shared features can produce a prediction for a new key, but useful transfer
must be demonstrated on untouched data. That is a different architecture and
must not be silently presented as a giant lookup table.

This definition is associated with [Watkins and Dayan's Q-learning
paper](https://doi.org/10.1007/BF00992698), but a Q table does not have to be
learned by trial and error. If the finite transition and reward model is known,
dynamic programming can compute it directly.

### Layers are remaining-horizon slices

GlassMind stores $Q_h(s,a)$ for every remaining horizon
$h \in \{0,\ldots,255\}$. For a deterministic transition $T$ and reward $r$,
one Bellman backup can be read as three small operations.

First, apply the selected action:

$$
s'=T(s,a).
$$

Second, find the best continuation value on the preceding horizon:

$$
C_{h-1}(s')=\max_b Q_{h-1}(s',b).
$$

Third, add the immediate reward to the discounted continuation:

$$
Q_h(s,a)=r(s,a)+\gamma C_{h-1}(s').
$$

These three lines are equivalent to the usual one-line recurrence. They apply
to nonterminal actions when $h>0$. Terminal actions have no continuation term,
and layer zero admits only terminal actions. Section 5 further restricts the
maximum to deontically admissible actions.

### Worked example: planning can reverse the immediate choice

Assume a small deterministic model with two possible first actions:

- `execute` gives $+4$ now, then forces a repair cost of $-12$ one step later;
- `mitigate` costs $-1$ now, waits safely for three steps, then produces $+8$
  at time $t=4$.

This is a declared teaching model, not an empirical claim about an external
system.

<figure class="fp-figure">
  <p class="fp-figure-title">The larger immediate reward is not the better path</p>
  {% include diagrams/glassmind-delayed-reward-fork.svg %}
  <figcaption class="fp-figure-caption">
    The upper path wins if only the first reward is inspected. The lower path wins when the complete discounted return is evaluated. The exponent four is part of the model: the positive outcome arrives four decision steps after the initial action.
  </figcaption>
</figure>

Set the discount factor first:

$$
\gamma=\frac{15}{16}=0.9375.
$$

For `execute`, discount the later loss by one step:

$$
\gamma(-12)=-11.25.
$$

Then add the immediate reward:

$$
4+(-11.25)=-7.25.
$$

For `mitigate`, calculate the four-step discount:

$$
\gamma^4=0.7724761962890625.
$$

Apply it to the delayed reward:

$$
8\gamma^4=6.1798095703125.
$$

Finally, include the immediate cost:

$$
-1+6.1798095703125=5.1798095703125.
$$

The planned advantage over the immediate-reward choice is therefore

$$
5.1798095703125-(-7.25)=12.4298095703125.
$$

Inside this toy model, the multi-step planner selects `mitigate`. If the delay,
rewards, or transition graph changes, the calculation must be rebuilt.

These 256 layers are not analogous to 256 transformer blocks. Each table layer
is an explicit value function for one planning horizon. A transformer layer is
a learned computation that transforms a distributed representation.

### Expert rules, planning, and learning are different

A complete expert system can map every valid state directly to a required
action. In a small, stable, fully understood domain, that decision graph may be
simpler than a Q table and easier to prove.

The components answer different questions:

| Component | Question |
| --- | --- |
| Deontic or expert rules | Which actions are required, permitted, or forbidden? |
| Transition model | What state follows an action? |
| Reward or utility model | How is the immediate consequence scored? |
| Planner | Which admissible path has the best cumulative score? |
| Q function | What is the cumulative value of taking action $a$ in state $s$, then continuing well? |

A Q representation becomes useful when delayed outcomes create many
overlapping paths, online tree search is too expensive, or values must be
estimated from experience. Logic can still own hard obligations and
prohibitions. Q values rank only the actions that logic admits.

Prediction is not necessary when the transition and reward functions are known
and deterministic. Exact dynamic programming can calculate every bounded
value. Statistical prediction becomes necessary when outcomes are unknown,
noisy, partially observed, or too large to enumerate. Logic can derive
consequences from premises, but it cannot create empirical facts about the
world. Such premises need measurements, a simulator, reviewed evidence, or
explicitly labeled assumptions.

<div class="fp-callout fp-callout-warning">
  <p class="fp-callout-title">Compiled planning is not learned Q</p>
  <p>
    GlassMind computes exact values from a declared transition and reward
    model. It does not learn a multi-step Q function from sampled experience.
    Evidence that more experience improves decisions would require frozen
    holdout families, small-data and shuffled-label controls, and a
    reproducible scaling curve.
  </p>
</div>

### More records are not automatically more knowledge

A trajectory record can be experience:

```text
(state, action, observed reward, next state, terminal, provenance)
```

It can add knowledge when it covers a new state-action region, reveals a rare
consequence, distinguishes competing transition models, or reduces uncertainty.
Repeating one deterministic transition mostly tests reproducibility. Duplicating
rows increases storage without adding a distinction. Enumerating millions of
states from one authored equation expands coverage of that equation, not
external knowledge.

Claims about learning should therefore report held-out decision improvement,
transition-family coverage, uncertainty, sensitivity to source removal, and a
small-data control. Dataset size is supporting telemetry, not the conclusion.

## 2. Is a Q table a compression algorithm?

Often, yes, but the precise answer has three parts.

First, $Q^{\ast}$ compresses a task model. A Markov decision process may
contain a transition distribution, reward distribution, and many possible
trajectories.
The Q function retains the expected return of each state-action pair. Different
world models can therefore induce the same $Q^{\ast}$.

Second, a state abstraction $\phi(x)=s$ compresses observations $x$ into table
keys. If two observations that need different actions map to the same state,
the abstraction is lossy in a decision-relevant way.

Third, quantizing Q values compresses the values themselves. This can be lossy
about exact returns while preserving the selected action.

A useful error measure is **decision distortion**. Calculate it in two steps.
First, record the action chosen by the compressed system:

$$
\hat\pi(x)=\operatorname*{arg\,max}_a
\widehat Q(\phi(x),a).
$$

Second, evaluate that chosen action with the exact reference values:

$$
d(x)=V^{\ast}(x)-Q^{\ast}\!\left(x,\hat\pi(x)\right).
$$

Thus $d(x)$ asks how much value is lost because the compressed system selected
$\hat\pi(x)$ instead of an optimal action. The approximate model chooses the
action, but the reference model measures the loss.

Suppose every stored value has absolute error at most $\varepsilon$. If the
gap between the best and second-best exact action at a state is greater than
$2\varepsilon$, quantization cannot change the greedy action at that state.

For a standard finite discounted setting, first define the discount-dependent
amplification factor

$$
B(\gamma)=\frac{2}{1-\gamma}.
$$

A common worst-case greedy-policy bound can then be written as

$$
\lVert V^{\ast}-V^{\hat\pi}\rVert_{\infty}
\leq B(\gamma)\varepsilon.
$$

The assumptions matter. This bound requires uniform Q error in the modeled
domain. The infinity norm means the largest absolute value error over all
modeled states. The bound says nothing about observations that the state
encoder maps incorrectly or cannot represent.

The ICLR 2025 paper [*Physics of Language Models: Part 3.3, Knowledge Capacity
Scaling Laws*](https://proceedings.iclr.cc/paper_files/paper/2025/hash/26d3c9a66836ded8f34a944f2bfe868e-Abstract-Conference.html)
reports roughly two learned bits per parameter in controlled factual-tuple
experiments. That is a valuable result about one measured kind of knowledge
storage. It is not a universal conversion rate between model parameters,
intelligence, Q entries, or useful decisions.

## 3. How many Q layers are possible?

There is no mathematical maximum such as 16, 256, or 1,000 layers. A finite
implementation is limited by storage, build time, and whether a longer horizon
changes the policy.

For $H$ layers, $S$ states, and $A$ actions, first count the table cells:

$$
N_Q=HSA.
$$

If each value occupies $b_q$ bytes, convert that count into storage:

$$
M_Q=N_Qb_q.
$$

GlassMind uses `float32`, so $b_q=4$. For the public profile, the cell count is

$$
N_Q=256\times6{,}144\times8=12{,}582{,}912.
$$

Multiplying by four bytes per cell gives

$$
M_Q=12{,}582{,}912\times4=50{,}331{,}648\text{ bytes}=48\text{ MiB}.
$$

| Profile | Layers $H$ | States $S$ | Actions $A$ | Raw Q bytes |
| --- | ---: | ---: | ---: | ---: |
| Public | 256 | 6,144 | 8 | 50,331,648 bytes, exactly 48 MiB |
| Full local | 256 | 65,536 | 8 | 536,870,912 bytes, exactly 512 MiB |

The public state count combines 6 decisions, 256 graph slots, and 4 evidence
masks:

$$
6\text{ decisions}\times256\text{ graph slots}\times4\text{ evidence masks}
=6{,}144.
$$

The full profile uses

$$
16\times1{,}024\times4=65{,}536
$$

states. Storage grows linearly with the number of layers, but usually grows
combinatorially when additional facts must be represented in the state.

### Logical layers versus physical slabs

The formulas above describe a dense baseline. They do not imply that every
logical horizon must occupy a different physical array. If two complete
horizon slabs are byte-identical, a lossless quotient can store the slab once.

First map each logical horizon to a physical slab identifier:

$$
m:\{0,\ldots,255\}\rightarrow\{0,\ldots,P-1\}.
$$

Then answer a logical query through that mapping:

$$
Q_{\mathrm{logical}}[h,s,a]
=Q_{\mathrm{physical}}[m(h),s,a].
$$

The horizon remains part of the query. Only its physical storage is shared.
Every returned value is still an explicit table cell. There is no fitted dot
product and no approximation.

An audit of the generated tables found that the Bellman recurrence reaches an
exact byte-level fixed point much earlier than horizon 255:

| Profile | Logical horizons | Byte-distinct slabs | Fixed-point representative | Quotient raw data | Raw bytes avoided | Exhaustive quotient replay |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Public | 256 | 14 | 13 | 2,752,512 bytes (2.625 MiB) | 47,579,136 (94.53125%) | 12,582,912 values, 0 mismatches |
| Full local | 256 | 16 | 15 | 33,554,432 bytes (32 MiB) | 503,316,480 (93.75%) | 134,217,728 values, 0 mismatches |

The ordinary Bellman verifier establishes the recurrence. The separate
quotient verifier checks every logical `(h, s, a)` query against the original
dense table. Together they support an exact fixed-point interpretation inside
this finite model.

This improves **representation efficiency**, not knowledge. In these exact
artifacts, 242 or 240 tail horizons repeat the same bytes. Those addressable
horizons must not be counted as independent layers of learned information. The
quotient is standard exact deduplication, not a claimed novel data structure.

A second exact audit counted byte-distinct eight-action value rows at the final
horizon:

| Profile | Registered states | Distinct final-horizon Q rows | Fraction |
| --- | ---: | ---: | ---: |
| Public | 6,144 | 558 | 9.082% |
| Full local | 65,536 | 659 | 1.006% |

Equal final Q rows do not prove that two states have identical provenance,
transitions, or earlier-horizon behavior. This is not a fact count. It does
show why raw state count is also an inadequate knowledge metric: the larger
registry has much more address space than final-horizon decision diversity.

At a fixed byte budget, the recovered space can instead hold more canonical
states. For example, suppose a larger model still needs only 16 physical slabs,
eight actions, and four bytes per value. One state then occupies

$$
16\times8\times4=512\text{ bytes}.
$$

A 512 MiB payload can therefore address

$$
\frac{512\times2^{20}\text{ bytes}}{512\text{ bytes per state}}
=1{,}048{,}576\text{ states}.
$$

This is a conditional capacity calculation, not an achieved learning result.
Adding meaningful transitions can increase the graph diameter and the number
of distinct slabs. A scaled build must measure both quantities again.

Reclaimed bytes should be spent only when at least one decision-relevant
measure improves: reachable transition families, distinct
normative conflicts, independently sourced outcomes, held-out rollout return,
calibration, source-removal sensitivity, or exact counterexample coverage.
Merely adding Cartesian-product keys is not an improvement.

For storage benchmarking, a precise metric is *verified logical queries
preserved per stored byte*. The quotient preserves about 4.57 logical values
per NPY byte in the public profile and 4.00 in the full profile. This is not
"intelligence per byte" or "morality per byte." Those labels would collapse
task quality, normative premises, coverage, and representation overhead into
one misleading number.

## 4. From source data to checked decision bytes

{% include diagrams/glassmind-knowledge-compiler.svg %}

The pipeline is:

```text
LLM proposes states, abstractions, actions, edge cases, and trajectories
        |
canonicalizer removes duplicates and assigns stable state keys
        |
pinned source, simulator, formal checker, preference, or measurement assigns evidence
        |
Tau or ESSO policy derives obligations, prohibitions, and permissions
        |
deontic compiler creates an admissible-action mask
        |
dynamic programming computes 256 Q layers
        |
counterexample search targets sparse, contradictory, and low-gap regions
        |
verified table + provenance + uncertainty counts + reason receipt
```

An LLM is useful at the proposal boundaries. It can suggest vocabulary, state
factorizations, actions, edge cases, and challenge trajectories. It should not
silently label its own proposals as facts or rewards. In this demonstration,
the language-model contribution is quarantined in a seed proposal pack. A
deterministic parser accepts only bounded source records from a pinned release.

High-quality synthetic data means more than fluent examples. A useful pipeline
should:

1. mark each record as proposed, source-attributed, simulated, measured, or
   formally checked;
2. canonicalize before splitting or counting so duplicates do not inflate
   coverage;
3. obtain rewards from a simulator, checker, measurement, or separately
   declared preference process;
4. retain rejected and contradictory examples as negative knowledge;
5. search low-coverage and low-action-gap regions instead of generating only
   easy cases;
6. keep the generator outside the final acceptance boundary; and
7. bind source, policy, utility, and output hashes in every accepted artifact.

More generated rows do not repair a weak labeler. If the simulator or normative
profile is wrong, dynamic programming will faithfully amplify the wrong model.

### Why use a downloaded knowledge base?

[Open English WordNet](https://github.com/globalwordnet/english-wordnet) is a
free lexical graph released under CC-BY 4.0. The demo pins the 2025 GWA-LMF XML
release by SHA-256:

```text
9ca6d1dcb75f822fdd66617f7d9da48142ace38dd544d6ad5e2feca1674ad3fe
```

The source contains synsets for concepts such as data structure, algorithm,
deontic logic, obligation, permission, welfare, and utilitarianism. The bounded
adapter starts from declared synset IDs, follows an allowlist of lexical
relations, sorts all records canonically, and emits 256-node and 1,024-node
snapshots.

This is more reproducible than relying on a live endpoint during the build. It
does not make the source infallible. A WordNet hypernym link is a lexical
assertion from that release, not a theorem. Browsing a link backward is a search
operation, not an assertion that the inverse predicate is true.

## 5. Deontic logic is the normative boundary

Deontic logic studies normative notions such as:

- $O(a)$: action $a$ is obligatory;
- $F(a)$: action $a$ is forbidden;
- $P(a)$: action $a$ is permitted.

An obligation can require a decision, but the terms are not identical. An
obligation states what is required in a context. A **required decision** is a
procedural object that requires an explicit resolution. Depending on the
policy, an action, abstention, or escalation can discharge that procedural
requirement. Silence is not a recorded resolution.

This distinction matters in contrary-to-duty cases. If a primary obligation is
violated, a repair obligation can become active. Treating the repair as though
it erased the original violation produces misleading receipts.

[Benzmüller, Parent, and van der
Torre](https://xavierparent.github.io/pdf/C69.pdf) describe a deontic reasoning
infrastructure that supports multiple logics instead of assuming one formalism
is best for every problem. GlassMind follows that engineering lesson. It
uses a small finite input/output-style detachment profile. Conflicts, unknown
premises, multiple simultaneous obligations, and unsupported
contrary-to-duty constructs are quarantined.

[Priya and Rao](https://arxiv.org/abs/2501.05765) combine deontic and temporal
operators for formal verification of AI ethics. GlassMind does not claim that
temporal logic. Its horizon index counts remaining planning steps, so a real
deadline or "until" obligation would need a separately declared temporal model.

### Compile norms before utility

<figure class="fp-figure">
  <p class="fp-figure-title">The logic gate acts before numerical ranking</p>
  {% include diagrams/glassmind-deontic-gate.svg %}
  <figcaption class="fp-figure-caption">
    A coherent active obligation narrows the optimizer to the obligation set. Otherwise, the optimizer receives the permitted and not-forbidden set. An action outside the resulting set never enters the Q-value comparison.
  </figcaption>
</figure>

Let $A_P(s)$ be the actions permitted and not forbidden in state $s$. If the
profile has an active, coherent obligation set $A_O(s)$, the optimizer receives

$$
A_D(s)=
\begin{cases}
A_O(s), & \text{if a coherent obligation is active},\\
A_P(s), & \text{otherwise}.
\end{cases}
$$

Selection first enforces the Boolean condition

$$
\operatorname{selectable}(s,a)\iff a\in A_D(s).
$$

For a selectable action, apply the transition and compute the best admissible
continuation:

$$
s'=T(s,a),
$$

$$
C_{h-1}(s')=\max_{b\in A_D(s')}Q_{h-1}(s',b).
$$

The admissible recurrence is then

$$
Q_h(s,a)=
\begin{cases}
U(s,a), & a\text{ is terminal},\\
U(s,a)+\gamma C_{h-1}(s'), & \text{otherwise}.
\end{cases}
$$

The serialized table writes the unavailable-action sentinel separately:

$$
Q^{\mathrm{stored}}_h(s,a)=-10^6
\quad\text{when }a\notin A_D(s).
$$

The independent Boolean mask still controls selection. The sentinel is not
trusted as the sole safety mechanism. If a required continuation has no
admissible action, the compiler must fail closed or quarantine the state rather
than take a maximum over an empty set.

The demo's ESSO model checks finite adapter invariants with explicit domains
and observables. Z3 and CVC5 agreed on all seven declared queries in two
determinism trials. This supports only the finite adapter invariants. It does
not verify the complete Python implementation, WordNet truth, a universal
deontic calculus, or production readiness. A Tau backend is specified in the
proof-carrying decision protocol but was not run for this artifact.

### Which deontic knowledge bases are needed?

No single database supplies facts, valid norms, authority, and deontic
semantics for every domain. A serious system needs separate, versioned lanes:

| Lane | Useful open source | What it supplies | What it does not supply |
| --- | --- | --- | --- |
| Lexical concepts | [Open English WordNet](https://github.com/globalwordnet/english-wordnet) | Synsets and attributed lexical relations | Normative authority or proof |
| Logic definitions and worked theories | [LogiKEy](https://github.com/cbenzmueller/LogiKEy) | Isabelle/HOL embeddings of deontic logics and ethical or legal theory experiments | A universal policy or current jurisdictional facts |
| Norm interchange | [OASIS LegalRuleML](https://www.oasis-open.org/committees/legalruleml/) | A standard, schemas, and examples for representing legal rules, provenance, violations, and reparations | Automatic correctness of an encoding or legal advice |
| Authoritative source text | [EUR-Lex data services](https://eur-lex.europa.eu/content/help/data-reuse/webservice.html?locale=en) | Versioned EU legal documents and bulk-access routes | A ready-made O/F/P translation; amendments, scope, and applicability still need checking |
| Descriptive social norms | [NormBank](https://aclanthology.org/2023.acl-long.429/) | A large empirical collection of situational social norms | Legal authority, moral truth, or formal deontic proofs |

GlassMind uses only the first lane plus a small explicit policy pack. The other
sources require separate ingestion and validation. Before a LegalRuleML or
legislative rule can constrain real action, the receipt must bind its issuer,
jurisdiction, version, effective interval, exceptions, amendments, and
translation review. Descriptive datasets such as NormBank belong in a proposal
or empirical-evidence lane, not an authority lane.

### Synthetic deontic data needs semantic validation

A lexical graph can name concepts, but it cannot supply normative authority.
Synthetic problem banks can add structured challenge cases by varying:

- obligation, prohibition, and permission topologies;
- true, false, unknown, and inconsistent evidence;
- priorities, exceptions, deadlines, and revocations;
- resolved, abstaining, and escalating outcomes; and
- contrary-to-duty repairs after a primary obligation is violated.

A Cartesian product over these axes is a test surface, not evidence about the
world. Large row counts can still collapse to a small number of distinct
behaviors, and a deterministic generator can reproduce the same semantic error
perfectly.

Acceptance labels should therefore come from an independently implemented
oracle rather than from the content generator. The oracle should reconstruct
each result from semantic inputs, execute both endpoints of every claimed
counterfactual, reject caller-supplied verification fields, and preserve
minimal disagreements as regression cases.

Unsupported semantics must remain explicit. If the checker does not implement
priority, exception, temporal, or contrary-to-duty rules, those records belong
in an `unsupported_quarantine` class. A missing proof-tool run is missing
evidence, not an implicit success.

Byte-identical regeneration establishes deterministic construction. It does
not establish legal force, moral authority, real-world truth, population
representativeness, or semantic correctness. Those claims require separate
sources and checks.

## 6. What is inside the state and action spaces?

A state is

```text
(required decision, graph-node slot, two-bit evidence mask)
```

The evidence mask has four values:

- `00`: neither graph discovery channel has been traversed;
- `01`: a forward source relation was traversed;
- `10`: a reverse browsing step was traversed;
- `11`: both channels were traversed.

These bits record model-local discovery events. They do not prove that an edge
is true. In a production system, evidence bits should point to typed,
independently checked propositions rather than generic traversal events.

Every state has eight action slots:

```text
navigate_0 ... navigate_5, resolve, abstain_or_escalate
```

Navigation candidates are sorted and capped at six. Dropped candidates are
counted in the manifest. Padded graph slots admit only
`abstain_or_escalate`. On a real node, navigation and abstention remain
available until a target node has the required evidence. At a complete target,
the finite profile makes `resolve` obligatory and exclusive.

That last rule is why a deontic adapter is not optional. If it is absent,
malformed, incomplete, or tries to permit premature resolution, compilation
fails closed.

## 7. Reproduce the public artifact

Download and pin the free source:

```bash
mkdir -p artifacts/local/sources
curl -L \
  https://en-word.net/static/english-wordnet-2025.xml.gz \
  -o artifacts/local/sources/english-wordnet-2025.xml.gz
sha256sum artifacts/local/sources/english-wordnet-2025.xml.gz
```

The digest must match the pinned value above. Then build the bounded snapshot:

```bash
python3 -m examples.layered_q_tables.wordnet_snapshot \
  --source artifacts/local/sources/english-wordnet-2025.xml.gz \
  --seed-pack examples/layered_q_tables/wordnet_seed_proposals.json \
  --output assets/data/glassmind_wordnet_256.json \
  --retrieved-at 2026-08-02T00:20:57Z \
  --max-nodes 256 \
  --min-nodes 256 \
  --max-depth 6 \
  --max-relations-per-node 12
```

Compile the Q table:

```bash
python3 -m examples.layered_q_tables.knowledge_q_table build \
  --profile public \
  --snapshot assets/data/glassmind_wordnet_256.json \
  --decisions examples/layered_q_tables/planner_required_decisions_public.json \
  --evidence-deontic \
  --deontic-logic-semantics bounded-finite-detachment-v1 \
  --deontic-logic-semantics-sha256 1a95da0066a4bdb8a8fb6cfde4629eab95ac35d3b814bfcaf21e10328ed355df \
  --deontic-profile neutral-evidence-completion-v1 \
  --deontic-profile-sha256 4046ef1d6377f9eed77d86b76f7f813268d51bef6af8b2fd5a93c355b8c51efa \
  --esso-evidence-hash model_sha256=78e5d57a463365d21741045a64a556176427963eb81aae0c0a8d48e0ee56b270 \
  --esso-evidence-hash ir_sha256=0fed6db3d9a4a1927cda867e0683c5a257c9feb9471452f7eb5621820900b965 \
  --output assets/data/glassmind_knowledge_256_50mb.npy \
  --manifest assets/data/glassmind_knowledge_256_50mb.manifest.json
```

Replay every layer, state, and action:

```bash
python3 -m examples.layered_q_tables.knowledge_q_table verify \
  --profile public \
  --snapshot assets/data/glassmind_wordnet_256.json \
  --decisions examples/layered_q_tables/planner_required_decisions_public.json \
  --evidence-deontic \
  --deontic-logic-semantics bounded-finite-detachment-v1 \
  --deontic-logic-semantics-sha256 1a95da0066a4bdb8a8fb6cfde4629eab95ac35d3b814bfcaf21e10328ed355df \
  --deontic-profile neutral-evidence-completion-v1 \
  --deontic-profile-sha256 4046ef1d6377f9eed77d86b76f7f813268d51bef6af8b2fd5a93c355b8c51efa \
  --esso-evidence-hash model_sha256=78e5d57a463365d21741045a64a556176427963eb81aae0c0a8d48e0ee56b270 \
  --esso-evidence-hash ir_sha256=0fed6db3d9a4a1927cda867e0683c5a257c9feb9471452f7eb5621820900b965 \
  --table assets/data/glassmind_knowledge_256_50mb.npy \
  --manifest assets/data/glassmind_knowledge_256_50mb.manifest.json \
  --report assets/data/glassmind_knowledge_256_50mb.verify.json
```

Build and exhaustively replay the lossless horizon quotient:

```bash
python3 -m examples.layered_q_tables.horizon_quotient_table build \
  --source assets/data/glassmind_knowledge_256_50mb.npy \
  --quotient assets/data/glassmind_knowledge_256_horizon_quotient.npy \
  --manifest assets/data/glassmind_knowledge_256_horizon_quotient.manifest.json

python3 -m examples.layered_q_tables.horizon_quotient_table verify \
  --source assets/data/glassmind_knowledge_256_50mb.npy \
  --quotient assets/data/glassmind_knowledge_256_horizon_quotient.npy \
  --manifest assets/data/glassmind_knowledge_256_horizon_quotient.manifest.json \
  --report assets/data/glassmind_knowledge_256_horizon_quotient.verify.json
```

The published files are:

- [48 MiB Q table]({{ '/assets/data/glassmind_knowledge_256_50mb.npy' | relative_url }});
- [manifest and provenance]({{ '/assets/data/glassmind_knowledge_256_50mb.manifest.json' | relative_url }});
- [exhaustive verification report]({{ '/assets/data/glassmind_knowledge_256_50mb.verify.json' | relative_url }});
- [lossless horizon quotient with a 2.625 MiB raw Q payload]({{ '/assets/data/glassmind_knowledge_256_horizon_quotient.npy' | relative_url }});
- [quotient manifest]({{ '/assets/data/glassmind_knowledge_256_horizon_quotient.manifest.json' | relative_url }});
- [quotient exhaustive replay]({{ '/assets/data/glassmind_knowledge_256_horizon_quotient.verify.json' | relative_url }});
- [256-node WordNet snapshot]({{ '/assets/data/glassmind_wordnet_256.json' | relative_url }});
- [example reason receipt]({{ '/assets/data/glassmind_knowledge_256_trace.json' | relative_url }}).

The NPY file stays below GitHub's enforced 100 MiB single-object limit, though
[GitHub warns above 50 MiB and blocks files above 100 MiB](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).
The large artifact therefore remains a reproducible local output rather than a
published Git object.

### The 512 MiB profile

The full profile uses the same code and a 1,024-node snapshot:

```bash
python3 -m examples.layered_q_tables.wordnet_snapshot \
  --source artifacts/local/sources/english-wordnet-2025.xml.gz \
  --seed-pack examples/layered_q_tables/wordnet_seed_proposals.json \
  --output assets/data/glassmind_wordnet_1024.json \
  --retrieved-at 2026-08-02T00:20:57Z \
  --max-nodes 1024 \
  --min-nodes 1024 \
  --max-depth 8 \
  --max-relations-per-node 12

python3 -m examples.layered_q_tables.knowledge_q_table build \
  --profile full \
  --snapshot assets/data/glassmind_wordnet_1024.json \
  --decisions examples/layered_q_tables/planner_required_decisions_full.json \
  --evidence-deontic \
  --deontic-logic-semantics bounded-finite-detachment-v1 \
  --deontic-logic-semantics-sha256 1a95da0066a4bdb8a8fb6cfde4629eab95ac35d3b814bfcaf21e10328ed355df \
  --deontic-profile neutral-evidence-completion-v1 \
  --deontic-profile-sha256 4046ef1d6377f9eed77d86b76f7f813268d51bef6af8b2fd5a93c355b8c51efa \
  --esso-evidence-hash model_sha256=78e5d57a463365d21741045a64a556176427963eb81aae0c0a8d48e0ee56b270 \
  --esso-evidence-hash ir_sha256=0fed6db3d9a4a1927cda867e0683c5a257c9feb9471452f7eb5621820900b965 \
  --output artifacts/local/glassmind_knowledge_256_512mib.npy \
  --manifest assets/data/glassmind_knowledge_256_512mib.report.json

python3 -m examples.layered_q_tables.knowledge_q_table verify \
  --profile full \
  --snapshot assets/data/glassmind_wordnet_1024.json \
  --decisions examples/layered_q_tables/planner_required_decisions_full.json \
  --evidence-deontic \
  --deontic-logic-semantics bounded-finite-detachment-v1 \
  --deontic-logic-semantics-sha256 1a95da0066a4bdb8a8fb6cfde4629eab95ac35d3b814bfcaf21e10328ed355df \
  --deontic-profile neutral-evidence-completion-v1 \
  --deontic-profile-sha256 4046ef1d6377f9eed77d86b76f7f813268d51bef6af8b2fd5a93c355b8c51efa \
  --esso-evidence-hash model_sha256=78e5d57a463365d21741045a64a556176427963eb81aae0c0a8d48e0ee56b270 \
  --esso-evidence-hash ir_sha256=0fed6db3d9a4a1927cda867e0683c5a257c9feb9471452f7eb5621820900b965 \
  --table artifacts/local/glassmind_knowledge_256_512mib.npy \
  --manifest assets/data/glassmind_knowledge_256_512mib.report.json \
  --report assets/data/glassmind_knowledge_256_512mib.verify.json
```

The local lossless quotient is generated and checked separately:

```bash
python3 -m examples.layered_q_tables.horizon_quotient_table build \
  --source artifacts/local/glassmind_knowledge_256_512mib.npy \
  --quotient artifacts/local/glassmind_knowledge_256_512mib.hq.npy \
  --manifest assets/data/glassmind_knowledge_256_512mib.hq.manifest.json

python3 -m examples.layered_q_tables.horizon_quotient_table verify \
  --source artifacts/local/glassmind_knowledge_256_512mib.npy \
  --quotient artifacts/local/glassmind_knowledge_256_512mib.hq.npy \
  --manifest assets/data/glassmind_knowledge_256_512mib.hq.manifest.json \
  --report assets/data/glassmind_knowledge_256_512mib.hq.verify.json
```

Memory mapping means the compiler does not allocate the entire 512 MiB table
in RAM. Disk capacity still matters. The local artifact is reproducible from
the public source snapshot, decisions, code, and manifest.

## 8. What the verifier checks

The replay pass deterministically recomputes:

1. the canonical knowledge and decision hashes;
2. every deontic action mask and reason ID;
3. every transition, immediate utility, and Bellman value;
4. all table values in bounded chunks;
5. every greedy choice for forbidden-action and termination violations;
6. the NPY shape, order, data type, byte length, and SHA-256 digest.

The public verification report records:

```text
passed: true
shape: [256, 6144, 8]
checked Q values: 12,582,912
checked greedy policy states: 1,572,864
maximum absolute Bellman error: 0.0
mismatches and non-finite values: 0
forbidden, nonterminating, bound, and resolution violations: 0
maximum observed terminal steps: 13
table SHA-256: 39b26a62f096011efe0b8ec444cff917b736f5713fcf7221665a7c9d10790c2e
```

The 512 MiB verification report records:

```text
passed: true
shape: [256, 65536, 8]
checked Q values: 134,217,728
checked greedy policy states: 16,777,216
maximum absolute Bellman error: 0.0
mismatches and non-finite values: 0
forbidden, nonterminating, bound, and resolution violations: 0
maximum observed terminal steps: 15
table SHA-256: 6d36964fe36f6882f54139304fabfcced3df19e7b690e0a0062809c7129935e8
```

The public [verification report]({{ '/assets/data/glassmind_knowledge_256_50mb.verify.json' | relative_url }})
and the full-profile [verification report]({{ '/assets/data/glassmind_knowledge_256_512mib.verify.json' | relative_url }})
contain the canonical machine-readable results. The full Q array itself remains
local because it exceeds GitHub's single-object limit.

The horizon-quotient checks are deliberately separate from the Bellman checks.
They reported:

```text
public physical shape: [14, 6144, 8]
public quotient SHA-256: bb32caac7f4b3b6f2dbca22bf172566d9c6ef57a4e1f4072060cee3caa484384
public logical values replayed: 12,582,912
public distinct final-horizon Q rows: 558

full physical shape: [16, 65536, 8]
full quotient SHA-256: 909d5c85890c2877b1630b7e1ae402d2fbca7174ec017100f7152cd774d1b023
full logical values replayed: 134,217,728
full distinct final-horizon Q rows: 659

quotient mismatches: 0
lossy: false
```

Two independent public quotient builds were byte-identical, including their
canonical manifests. This is same-machine deterministic-build evidence, not a
cross-platform reproducibility claim.

Exhaustive means exhaustive over the declared finite table. It does not mean
that the state abstraction covers the real world. The replay pass deliberately
shares the planner's model compiler and Bellman chunk implementation. It is a
strong corruption and deterministic-consistency check, but not an independently
implemented Bellman oracle. A separate implementation, mutation tests, or a
formal recurrence proof would strengthen this boundary.

## 9. Why reason receipts matter

A table cell gives a number, not an explanation. GlassMind's query path emits a
bounded receipt containing:

- the starting decision, node, evidence mask, and horizon;
- each selected action and Q value;
- each traversed source edge and its direction;
- deontic rule and quarantine reason IDs;
- the terminal resolution or abstention;
- all source, policy, utility, recurrence, table, and configuration hashes;
- a finite-trace gate result.

The receipt explains the checked computation. It does not prove that the source
fact is true or that the policy is morally correct. The
[Proof-Carrying Decisions specification](https://github.com/TheDarkLightX/FormalPhilosophy/blob/main/research/proof_carrying_decisions_v0.md)
extends this boundary with typed evidence, proof DAGs, countermodels,
revocation, multiple logic profiles, ESSO, and Tau.

## 10. Can data become policy-aligned Q bytes?

Yes, conditionally. The valid pipeline is not simply "data in, aligned bytes
out." It needs separately declared normative and outcome models:

```text
observations -> checked facts
facts + authority-scoped norms -> O/F/P action mask
measured outcomes + stakeholder weights -> utility
mask + utility + transitions -> Q layers
Q layers + all input hashes -> replay receipt
```

Suppose a bounded profile declares stakeholders $i=1,\ldots,n$, predicted
consequences $c_i(s,a)$, and weights $w_i$. A simple utilitarian score is

$$
U_{\text{sum}}(s,a)=\sum_{i=1}^{n} w_i c_i(s,a).
$$

A deontic policy can require selection only among actions that meet hard
obligations and prohibitions. Dynamic programming can then maximize the
declared sum over that admissible set.

This construction aligns the bytes with **that finite formalization**. It does
not prove utilitarianism, the stakeholder list, weights, forecasts, or state
abstraction correct. An omitted stakeholder, a bad outcome model, or a harmful
proxy can produce a perfectly verified but badly specified table. Review
triggers, counterexamples, sensitivity analysis, and policy versioning are
therefore part of the alignment boundary.

The 50 MiB artifact uses a neutral evidence-completion utility profile.
It demonstrates normative masking and replay, not a claim of utilitarian moral
authority. A small companion counterfactual shows how a bounded stakeholder-sum
profile changes a policy and its Q bytes while preserving the same source and
transition model:

- [policy comparison receipt]({{ '/assets/data/glassmind_policy_comparison.json' | relative_url }}).

## 11. Q tables compared with GPT-5.6 and Kimi K3

Equal byte counts do not imply equal capability. The systems store and compute
different objects.

| Property | Layered Q table | GPT-5.6 | Kimi K3 |
| --- | --- | --- | --- |
| Representation | Explicit scalar for each declared `(h,s,a)` | Learned distributed parameters; architecture and parameter count are not publicly disclosed | Open-weight MoE with 2.8T total parameters, 104B activated per token, and 93 layers |
| Input surface | Closed, canonical state keys | Open-ended token, tool, and supported multimodal workflows | Text, image, long-context, and agentic workflows |
| Computation | Array lookup after offline DP | Learned inference plus optional tools | Learned MoE inference plus optional tools |
| Exact repeatability | Yes for fixed bytes, key, and tie rule | Not generally guaranteed across sampling, service revisions, or tool state | Not generally guaranteed across sampling, runtime, or tool state |
| Generalization | No learned transfer outside its keys; an authored canonicalizer may map several observations to one key | Can compute outputs for new prompts; correctness and transfer require task-specific evaluation | Can compute outputs for new prompts; correctness and transfer require task-specific evaluation |
| Update | Change model inputs and recompute affected values | Train, fine-tune, provide context, or use tools | Train, fine-tune, provide context, or use tools |
| Audit surface | Every cell can be replayed in a bounded domain | Claims need external evaluation or checkers | Open weights help inspection, but behavior still needs evaluation or checkers |

[OpenAI describes GPT-5.6](https://openai.com/index/gpt-5-6/) as a model family
with Sol, Terra, and Luna tiers and makes Luna available through Codex and the
API. OpenAI does not disclose a parameter count or transformer-layer count in
that documentation, so no parameter or transformer-layer count is assumed
here.

[Moonshot's Kimi K3 repository](https://github.com/MoonshotAI/Kimi-K3)
reports 2.8 trillion total parameters, 104 billion activated parameters, 93
layers, 16 selected experts out of 896, and a 1,048,576-token context. These
figures describe Kimi K3. They are not a conversion into Q-table states.

### What is actually proven about learned generalization?

Generalization is not a model-wide yes-or-no property. It is relative to a
target distribution, a task, a loss function, and a training procedure. If
$f$ is a trained model, $\mathcal D$ is a declared target distribution, and
$\ell$ is a loss, its population risk is

$$
R_{\mathcal D}(f)
=
\mathbb E_{(x,y)\sim\mathcal D}
\left[\ell(f(x),y)\right].
$$

An untouched test set $T$ estimates this quantity with

$$
\widehat R_T(f)
=
\frac{1}{|T|}
\sum_{(x,y)\in T}
\ell(f(x),y).
$$

A generalization theorem can bound the gap between population and measured
risk with stated probability, but only under its assumptions. Typical
assumptions restrict how examples are sampled, the loss, the model or learning
algorithm, and the relationship between training and target distributions.

There are genuine mathematical results for restricted transformer settings.
For example, [Li et al.](https://arxiv.org/abs/2301.07067) derive
in-context-learning bounds under explicit stability, bounded-loss, and task
sampling assumptions. [Lotfi et
al.](https://arxiv.org/abs/2312.17173) derive non-vacuous compression-based
bounds for particular pretrained language-model settings using a compressed
parameterization. These are real theorems. They do not prove that every answer
from GPT-5.6, Kimi K3, or another deployed language model is correct, that the
model will succeed after arbitrary distribution shift, or that it has general
intelligence.

<div class="fp-callout fp-callout-warning">
  <p class="fp-callout-title">A new input is not automatically a generalization result</p>
  <p>A fitted model normally produces some output for an unseen input. That demonstrates a defined computation, not correct extrapolation. Evidence of generalization requires a predeclared untouched evaluation, contamination controls, an appropriate baseline, and uncertainty or confidence reporting.</p>
</div>

The claims form a ladder. Success on one rung does not establish the next.

| Claim level | Required evidence | What GlassMind establishes |
| --- | --- | --- |
| Authored key reuse | Several raw observations are deliberately canonicalized to one encoded state | GlassMind supports this, but the invariance comes from its authored canonicalizer rather than learning |
| Same-distribution predictive transfer | Performance on untouched samples drawn by the same declared process as training | Not measured; GlassMind is compiled rather than fitted |
| Held-out-family or compositional transfer | Entire concept families, relation types, or combinations are excluded before model and threshold selection | Not established |
| Distribution-shift robustness | Evaluation sources or mechanisms differ materially from training, with the shift declared in advance | Not established |
| General intelligence | Broad, adaptive competence across unfamiliar domains, goals, representations, and environments | Not established by a Q table, a fitted-Q result, or a language-model benchmark |

For GlassMind, exhaustive replay proves that the table implements its declared
finite recurrence. It does not prove learned generalization because the values
were compiled from an authored model. BasisQ could support a bounded
predictive-transfer claim only with a fresh source-held-out and
family-held-out evaluation. Such a result still would not imply general
intelligence.

A language model can serve as a proposal engine for the Q-table pipeline. It
can search for missing states, adversarial cases, alternative actions, and
useful abstractions. The deterministic compiler and checkers remain responsible
for accepted labels, masks, table bytes, and receipts.

## 12. Could a Q table support general intelligence?

There are two different questions: representational capacity and demonstrated
intelligence.

In principle, a finite table can encode any finite policy if its state key
contains every decision-relevant history. A table can also be one component of
a computationally universal system when paired with unbounded external memory
and suitable state transitions. This is a real form of computational
capability. Computational universality is not general intelligence. It means
that a system can represent arbitrary computations under suitable conditions,
not that it can learn the representation, understand a new domain, select good
goals, or adapt reliably.

In practice, a standalone finite Q table has no built-in way to invent the
right state representation, interpret unseen language, or generalize to
unlisted states. If $k$ independent Boolean facts matter, a direct state space
can require $2^k$ entries before actions and horizons are counted. Language
models trade explicit enumerability for learned, distributed compression that
can support useful transfer on evaluated tasks. The correctness and reach of
that transfer remain empirical and distribution-dependent.

Both architectures could be components of a broader agent, but neither claim
above demonstrates general intelligence:

- a Q table provides explicit, bounded, auditable decisions;
- an LLM provides flexible representation, proposal, and empirically evaluated
  transfer to new inputs;
- a hybrid uses the LLM to expand the frontier and a deterministic table or
  checker to own a narrow accepted decision surface.

The useful comparison is not "which file is smarter?" It is which subsystem
has authority over which claim.

## 13. Verified properties and limits

The strongest supported claims are:

- 256 horizon-indexed Q layers can be generated and memory-mapped;
- the public and full shapes have exact 48 MiB and 512 MiB raw payloads;
- the same 256 logical horizons can be represented losslessly by 14 public or
  16 full-profile physical slabs for these exact artifacts;
- a pinned external knowledge source can be converted into canonical bounded
  state keys;
- deontic constraints can be compiled before utility ranking;
- conflicts, unknowns, missing adapters, premature resolution, and padding can
  fail closed;
- every Q value and greedy finite-trace choice can be replayed in the bounded
  model;
- reason receipts can bind source, policy, utility, recurrence, and table
  hashes.

The demonstration does not establish:

- that WordNet relations are formal proofs;
- that two traversal bits are sufficient evidence for real decisions;
- that the selected normative profile is the correct ethics;
- that a 512 MiB table has capabilities comparable to a 512 MiB language
  model;
- that a finite table generalizes outside its canonical keys;
- that horizon deduplication adds facts, decisions, or moral competence;
- that the measured 14- or 16-slab fixed point survives a larger state and
  transition registry;
- that ESSO checked the entire Python and data pipeline;
- that Tau was executed for this artifact;
- that the system is ready to control safety-critical or value-moving effects.

These limits keep finite verification evidence separate from claims of
unbounded capability.

### From exact planning to experience-based multi-step Q learning

An exact solver can serve as a reference oracle for an experience-based
learner. One deterministic fitted-Q iteration is:

```text
freeze Q_k
    |
    v
for each checked transition, calculate
y = r + gamma * max Q_k(next_state, admissible_action)
    |
    v
fit Q_(k+1) into selected layers
    |
    v
search for Bellman and deontic counterexamples
```

The transition stream should retain provenance, support counts, and
uncertainty. Training transitions and held-out transition families must be
separated before fitting. Validation should require lower held-out Bellman error
as informative experience grows, better held-out rollout return than myopic and
small-data controls, zero forbidden selections, deterministic duplicate builds,
source-removal and label-permutation controls, and comparison with expert
graphs, dense tables, and online search.

If additional rows repeat the same authored dynamics and do not improve a
held-out metric, the correct conclusion is increased enumeration, not increased
knowledge.
