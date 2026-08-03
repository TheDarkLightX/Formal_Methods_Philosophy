---
title: "GlassMind-256: A Proof-Carrying Deterministic Thinker"
layout: docs
kicker: Tutorial 71
description: "Build a 256-layer Q table from a pinned knowledge graph, a deontic action gate, and a checked finite-horizon recurrence, then compare explicit tabular decisions with GPT-5.6 and Kimi K3."
---

A Q table can answer a decision question with one array lookup. If the state,
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
    <li><strong>Norms:</strong> a finite deontic profile controls which actions are admissible. It is not a universal ethics theory.</li>
    <li><strong>Utility:</strong> a separate outcome model ranks only admissible actions. Alignment is relative to the declared facts, norms, utility, state abstraction, and bounds.</li>
    <li><strong>Time:</strong> layer 255 means 255 remaining decision steps. It does not mean a date, a clock tick, or the 255th neural-network layer.</li>
    <li><strong>Authority:</strong> the table is advisory unless a surrounding system explicitly grants it authority. Safety-critical or value-moving code should keep final acceptance in a deterministic gate.</li>
  </ul>
</div>

## 1. What a Q value means

For a policy $\pi$, the action-value function is

$$
Q^{\pi}(s,a)
=
\mathbb{E}_{\pi}\!\left[
\sum_{t=0}^{\infty}\gamma^t R_{t+1}
\;\middle|\;
S_0=s, A_0=a
\right].
$$

It is the expected discounted return after starting in state $s$, taking action
$a$, and then following policy $\pi$. The optimal action-value function is

$$
Q^*(s,a)=\max_{\pi}Q^{\pi}(s,a)=Q^{\pi^*}(s,a).
$$

The greedy optimal action is any action in

$$
\operatorname*{arg\,max}_{a} Q^*(s,a).
$$

This definition is associated with [Watkins and Dayan's Q-learning
paper](https://doi.org/10.1007/BF00992698), but a Q table does not have to be
learned by trial and error. If the finite transition and reward model is known,
dynamic programming can compute it directly.

### Layers are remaining-horizon slices

GlassMind stores $Q_h(s,a)$ for every remaining horizon
$h \in \{0,\ldots,255\}$. For a deterministic transition $T$ and reward $r$,

$$
Q_h(s,a)
=
r(s,a)
+
\gamma \max_b Q_{h-1}(T(s,a),b)
$$

for nonterminal actions when $h>0$. Terminal actions have no continuation term.
Layer zero admits only terminal actions.

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

### A checked delayed-reward counterexample

[LogicQ-256 v0.3](https://github.com/TheDarkLightX/LogicQ-256/pull/2)
provides a smaller reference case that separates immediate choice from
multi-step planning. Its authored world gives the initial state two relevant
actions:

- `execute` pays $+4$ immediately, activates a hazard obligation, and forces a
  later mitigation cost of $-12$;
- `mitigate` costs $-1$, activates a three-step waiting obligation, and later
  enables an opportunity worth $+8$.

At $\gamma=15/16$, the path selected from immediate reward has return

$$
4+\frac{15}{16}(-12)=-7.25.
$$

The horizon-eight policy instead selects `mitigate`, with return

$$
-1+\left(\frac{15}{16}\right)^4(8)
=5.1798095703125.
$$

| Policy | First action | Rollout return at $\gamma=15/16$ |
| --- | --- | ---: |
| Immediate-reward action selection | `execute` | $-7.25$ |
| Exact horizon-eight planning | `mitigate` | $5.1798095703125$ |

The common-horizon gain is

$$
5.1798095703125-(-7.25)=12.4298095703125.
$$

This proves that future consequences change the selected first action inside
the declared model. It does not prove that the authored rewards or transitions
describe an external world, and it is not experience-based Q learning. The
values are computed from a known transition graph by exact backward dynamic
programming.

The hardened v0.3 evidence in [draft PR
#2](https://github.com/TheDarkLightX/LogicQ-256/pull/2), including its
[machine-readable build
report](https://github.com/TheDarkLightX/LogicQ-256/blob/agent/million-state-streaming-v2/experiments/results/temporal_v03_build_report.json),
records:

- 19 reachable states and 28 checked, content-addressed transitions;
- 128 admissible horizon-indexed Q cells;
- exact Bellman residual zero and deployed Q16.16 residual zero units;
- zero forbidden selections in both audited rollouts;
- byte-identical duplicate artifact builds; and
- an 8,943-byte artifact with SHA-256
  `0c5827e6f4ffba16be77c60d9f157684dfef52590ee55e8d134aab045ed6b11d`.

Artifact identifiers are version-specific. The hash above identifies the
hardened v0.3 artifact used for these measurements. The scope remains narrow:
the artifact is an exact compiler for one authored finite model.

The two demonstrations also use the word *layer* differently. GlassMind stores
256 horizon slices. LogicQ uses independent axes:

```text
Q[remaining horizon][feature or residual layer][state key][action]
```

Its v0.3 artifact serializes 256 feature-layer slots, but enables only three:
immediate reward, discounted continuation, and quantization calibration. The
remaining slots are reserves. Neither representation has learned 256 levels of
reasoning merely because 256 slots exist.

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

First, $Q^*$ compresses a task model. A Markov decision process may contain a
transition distribution, reward distribution, and many possible trajectories.
The Q function retains the expected return of each state-action pair. Different
world models can therefore induce the same $Q^*$.

Second, a state abstraction $\phi(x)=s$ compresses observations $x$ into table
keys. If two observations that need different actions map to the same state,
the abstraction is lossy in a decision-relevant way.

Third, quantizing Q values compresses the values themselves. This can be lossy
about exact returns while preserving the selected action.

A useful error measure is **decision distortion**:

$$
d(x)
=
V^*(x)-Q^*\!\left(x,\hat\pi(x)\right),
\qquad
\hat\pi(x)=\operatorname*{arg\,max}_a
\widehat Q(\phi(x),a).
$$

This asks how much value is lost because the compressed system selected
$\hat\pi(x)$ instead of an optimal action.

Suppose every stored value has absolute error at most $\varepsilon$. If the
gap between the best and second-best exact action at a state is greater than
$2\varepsilon$, quantization cannot change the greedy action at that state.
For a standard finite discounted setting, a common worst-case greedy-policy
bound is

$$
\lVert V^*-V^{\hat\pi}\rVert_{\infty}
\leq
\frac{2\varepsilon}{1-\gamma}.
$$

The assumptions matter. This bound requires uniform Q error in the modeled
domain. It says nothing about observations that the state encoder maps
incorrectly or cannot represent.

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

For $H$ layers, $S$ states, $A$ actions, and $b_q$ bytes per value,

$$
M_Q=HSA b_q.
$$

GlassMind uses `float32`, so $b_q=4$.

| Profile | Layers $H$ | States $S$ | Actions $A$ | Raw Q bytes |
| --- | ---: | ---: | ---: | ---: |
| Public | 256 | 6,144 | 8 | 50,331,648 bytes, exactly 48 MiB |
| Full local | 256 | 65,536 | 8 | 536,870,912 bytes, exactly 512 MiB |

The public state count factors as

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
7. bind source, policy, utility, and output hashes in every promoted artifact.

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
is best for every problem. The current demo follows that engineering lesson. It
uses a small finite input/output-style detachment profile. Conflicts, unknown
premises, multiple simultaneous obligations, and unsupported
contrary-to-duty constructs are quarantined.

[Priya and Rao](https://arxiv.org/abs/2501.05765) combine deontic and temporal
operators for formal verification of AI ethics. GlassMind does not claim that
temporal logic. Its horizon index counts remaining planning steps, so a real
deadline or "until" obligation would need a separately declared temporal model.

### Compile norms before utility

Let $A_P(s)$ be the actions permitted and not forbidden in state $s$. If the
profile has an active, coherent obligation set $A_O(s)$, the optimizer receives

$$
A_D(s)=
\begin{cases}
A_O(s), & \text{if a coherent obligation is active},\\
A_P(s), & \text{otherwise}.
\end{cases}
$$

The recurrence is then

$$
Q_h(s,a)=
\begin{cases}
-10^6, & a\notin A_D(s),\\
U(s,a), & a\in A_D(s)\text{ and }a\text{ is terminal},\\
U(s,a)+\gamma\max_b Q_{h-1}(T(s,a),b), & \text{otherwise}.
\end{cases}
$$

The finite value $-10^6$ is an unavailable-action sentinel inside this bounded
model. More importantly, an independent Boolean mask controls selection. The
sentinel is not trusted as the sole safety mechanism.

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

The current artifact uses only the first lane plus a small explicit policy
pack. The other sources are candidates for a later ingestion and validation
pipeline. Before a LegalRuleML or legislative rule can constrain real action,
the receipt must bind its issuer, jurisdiction, version, effective interval,
exceptions, amendments, and translation review. Descriptive datasets such as
NormBank belong in a proposal or empirical-evidence lane, not an authority
lane.

### The Luna-generated v0 candidate, and why it failed

A lexical graph helps name concepts, but it is not a substitute for normative
structure. A separate Luna-Max campaign therefore proposed a deontic problem
lattice rather than more WordNet substitutions. Its v0 construction was:

```text
8 typed domains
  x 8 norm graphs
  x 4 premise values
  x 8 temporal states
  x 4 priority states
  x 4 exception states
  x 2 revision states
  = 65,536 synthetic records
```

The premise values are true, false, unknown, and inconsistent. The norm graphs
cover obligations, prohibitions, permissions, same-action conflicts,
exclusive obligations, deadlines, and contrary-to-duty repairs. Other axes
change the clock, conflict order, exception evidence, and revocation state.
This creates typed semantic variation rather than counting paraphrases as new
knowledge.

The generator assigned a candidate result, but did not own acceptance. A
separate oracle, which imported none of the generator code, derived every
coordinate from raw semantic IR, recomputed hashes and references, and
evaluated the bounded result. The historical integrity run reported:

| Corpus check | Result |
| --- | ---: |
| Records checked | 65,536 |
| Unique semantic signatures | 65,536 |
| Independent-oracle errors | 0 |
| Resolved fixtures | 6,944 |
| Unresolved fixtures | 58,592 |
| Exact current-kernel projections | 1,152 |
| Explicitly quarantined projections | 64,384 |
| Negative-knowledge items | 285,056 |
| Compressed size across 16 shards | about 9.3 MiB |

The high unresolved count comes from systematic conflict, uncertainty,
inconsistency, revocation, and unsupported-feature cases. It is not a claim
about real-world prevalence. A clean second generation produced a byte-identical
manifest and all 16 byte-identical shards.

Those results were necessary but not sufficient. A later Luna-Max
falsification pass found only 49 role-normalized behaviors, plus re-sealed
hostile records that the oracle accepted, incorrect contrary-to-duty behavior,
ambiguous deadlines, dormant axes, and counterfactual claims that had never
been executed. The v0 corpus is therefore **NO-GO for semantic promotion**.
Its hashes and deterministic replay remain useful as negative knowledge and as
a regression target. The detailed counterexamples are retained in the
[v0 audit](https://github.com/TheDarkLightX/FormalPhilosophy/blob/main/research/synthetic_deontic_kb_luna_audit_v0.md).

The historical artifacts are the [manifest]({{ '/assets/data/glassmind_synthetic_deontic_65536.manifest.json' | relative_url }}),
[independent verification report]({{ '/assets/data/glassmind_synthetic_deontic_65536.verify.json' | relative_url }}),
[deterministic replay report]({{ '/assets/data/glassmind_synthetic_deontic_65536.replay.json' | relative_url }}),
and 16 compressed JSONL files under
`assets/data/glassmind_synthetic_deontic_65536/`.

Every record says `synthetic_non_authoritative`, `not_law`, `not_ethics`,
`not_world_truth`, and `not_external_authority`. The current kernel does not
implement priority, exception, temporal, or contrary-to-duty semantics. Those
cases are useful future-profile and falsification fixtures, but their current
projection remains `unsupported_quarantine`. The corpus verification also
records SMT, ESSO, Tau, Lean, and HOL as `SKIP`, not implicit success.

### What Luna v1 improved, and why it is still quarantined

**Status: `QUARANTINED_CORPUS`.** Passing some finite checks did not promote
the corpus.

V1 treats the language model as a content proposer, not as the source of
acceptance labels. It replaces the global v0 axes with a causal, topology-local
product:

```text
16 typed domains
  x 16 deontic topology programs
  x 4 evidence values
  x 4 local state variants
  x 4 local resolution variants
  x 4 local defeater variants
  = 65,536 synthetic records
```

This problem bank is upstream of a Q table. It supplies explicit decision
micro-worlds, conflicts, uncertainties, and checked counterfactuals that a
later compiler could use as training, challenge, or regression data. It does
not directly enlarge the GlassMind state space, and its synthetic norms are not
automatically valid policy.

The separate raw-record oracle found:

| Measurement | Exact result |
| --- | ---: |
| Accepted records | 65,536 of 65,536 |
| Normalized dispositions | 322 |
| One-axis pairs classified | 393,216 of 393,216 |
| `EFFECT` classifications | 177,600 |
| `INVARIANT` classifications | 215,616 |
| Declared spanning-effect witnesses | 3,072 of 3,072 |
| Resolved outcomes | 8,480 |
| Unresolved abstentions | 18,576 |
| Unresolved escalations | 38,480 |

The axis counts are informative. Evidence changed 91,136 of its 98,304 pairs,
while resolution changed only 1,536 of 98,304. The remaining resolution pairs
were checked invariants because another condition masked the priority change.
An invariant is useful negative knowledge when both endpoints and their equal
results were actually rebuilt and compared.

Here, an `EFFECT` means that one encoded axis changed the normalized result or
proof trace inside the frozen profile. It is not evidence of real-world
causality. Likewise, 322 normalized dispositions are finite quotient classes,
not 322 discoveries about the world.

The run also exposed mistakes in its own pipeline. The first generator and
oracle disagreed at ordinal `12336`. A peer audit then found that an early
counterfactual path trusted fields on a caller-supplied verified endpoint. Both
defects were repaired and retained as adversarial regressions before any v1
promotion. A second exhaustive peer computation reproduced 322 classes, all
393,216 pair classifications, the outcome counts above, and receipt-set root
`9ccf9ae8d13c9b4fb12cee0503af4010a35ac73c75b3457c4fda528c21a0c2ab`.

Evidence must still be separated by authority:

| Evidence lane | What passed | What remains absent |
| --- | --- | --- |
| Generated content | Exact 65,536-record product, 16 gzip shards, stable roots, and explicit synthetic nonclaims | Real-world truth, legal force, moral authority, or population representativeness |
| Raw-corpus oracle | All records accepted; diversity and outcome gates G08 and G09 passed | A complete schema-derived hostile-mutation and law-witness package |
| Clean rebuild comparison | A second manifest and all 16 shards were byte-identical | A retained two-build receipt with a second complete oracle report |
| Release and tools | The reducer and explicit tool table ran fail-closed | Durable receipt bodies, full call-graph evidence, and exact-profile ESSO, Tau, Lean, Research Kernel, PopperPad, LEAP, Morph, ZAG, Julia, or ZenoFCIS receipts |

The reducer therefore assigned **`QUARANTINED_CORPUS`**. G08, G09, and the
honest-status-table gate G14 passed. G00 through G07 and G10 through G13 remain
`SKIP`, so G15 failed as required. A `SKIP` is missing evidence, not a hidden
success.

The public artifacts are the v1
[manifest]({{ '/assets/data/glassmind_synthetic_deontic_luna_v1_65536.manifest.json' | relative_url }}),
[raw verification report]({{ '/assets/data/glassmind_synthetic_deontic_luna_v1_65536.verify.json' | relative_url }}),
and 16 compressed shards under
`assets/data/glassmind_synthetic_deontic_luna_v1_65536/`. The report file has
SHA-256
`38b6b3fd208e89c6cba7d4c3911f74326325e628b513d3fef217d75b5590460a`.
The detailed evidence and residual gates are in the
[v1 research report](https://github.com/TheDarkLightX/FormalPhilosophy/blob/main/research/synthetic_deontic_knowledge_base_v1.md).

The lesson for synthetic Q-table pipelines is concrete: a strong model can
propose states, abstractions, norms, and edge cases at scale, but generated
volume becomes reusable knowledge only when canonicalization, independent
reconstruction, counterexample search, replay, and a fail-closed reducer bind
the exact claim.

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

The published files are:

- [48 MiB Q table]({{ '/assets/data/glassmind_knowledge_256_50mb.npy' | relative_url }});
- [manifest and provenance]({{ '/assets/data/glassmind_knowledge_256_50mb.manifest.json' | relative_url }});
- [exhaustive verification report]({{ '/assets/data/glassmind_knowledge_256_50mb.verify.json' | relative_url }});
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

For the public artifact, the completed run reported:

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

For the 512 MiB artifact, the completed run reported:

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
fact is true or that the policy is morally correct. The next tutorial's
[Proof-Carrying Decisions v0 specification](https://github.com/TheDarkLightX/FormalPhilosophy/blob/main/research/proof_carrying_decisions_v0.md)
generalizes this boundary to typed evidence, proof DAGs, countermodels,
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

The current 50 MiB artifact uses a neutral evidence-completion utility profile.
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
| Generalization | None outside encoded state abstraction unless another system supplies it | Broad learned generalization | Broad learned generalization |
| Update | Change model inputs and recompute affected values | Train, fine-tune, provide context, or use tools | Train, fine-tune, provide context, or use tools |
| Audit surface | Every cell can be replayed in a bounded domain | Claims need external evaluation or checkers | Open weights help inspection, but behavior still needs evaluation or checkers |

[OpenAI describes GPT-5.6](https://openai.com/index/gpt-5-6/) as a model family
with Sol, Terra, and Luna tiers and makes Luna available through Codex and the
API. OpenAI does not disclose a parameter count or transformer-layer count in
that documentation, so this tutorial does not invent one.

[Moonshot's Kimi K3 repository](https://github.com/MoonshotAI/Kimi-K3)
reports 2.8 trillion total parameters, 104 billion activated parameters, 93
layers, 16 selected experts out of 896, and a 1,048,576-token context. These
figures describe Kimi K3. They are not a conversion into Q-table states.

An LLM is an excellent proposal engine for the Q-table pipeline. It can search
for missing states, adversarial cases, alternative actions, and useful
abstractions. The deterministic compiler and checkers remain responsible for
accepted labels, masks, table bytes, and receipts.

## 12. Could a Q table support general intelligence?

There are two defensible answers, depending on the claim.

In principle, a finite table can encode any finite policy if its state key
contains every decision-relevant history. A table can also be one component of
a computationally universal system when paired with unbounded external memory
and suitable state transitions. This is a real form of computational
capability.

In practice, a standalone finite Q table has no built-in way to invent the
right state representation, interpret unseen language, or generalize to
unlisted states. If $k$ independent Boolean facts matter, a direct state space
can require $2^k$ entries before actions and horizons are counted. Language
models trade explicit enumerability for learned, distributed compression and
generalization.

So both architectures can contribute to general intelligent behavior, but in
different ways:

- a Q table provides explicit, bounded, auditable decisions;
- an LLM provides flexible representation, proposal, and generalization;
- a hybrid uses the LLM to expand the frontier and a deterministic table or
  checker to own a narrow accepted decision surface.

The useful comparison is not "which file is smarter?" It is which subsystem
has authority over which claim.

## 13. What has actually been demonstrated?

The strongest supported claims are:

- 256 horizon-indexed Q layers can be generated and memory-mapped;
- the public and full shapes have exact 48 MiB and 512 MiB raw payloads;
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
- that ESSO checked the entire Python and data pipeline;
- that Tau was executed for this artifact;
- that the system is ready to control safety-critical or value-moving effects.

That boundary is the point of the exercise. Large deterministic artifacts can
be impressive and useful without turning their finite evidence into an
unbounded claim.

### Tutorial gate and paper gate

The current evidence passes a tutorial gate: the artifacts are reproducible,
the claims are bounded, and the delayed-reward example is falsifiable. It does
not pass a research-paper gate. The temporal result is standard finite-horizon
dynamic programming over one authored synthetic world.

A paper would require a significant result beyond that baseline, such as a
preregistered compression or runtime advantage at equal policy fidelity, a new
deontic Bellman construction with machine-checked properties, positive transfer
across independently sourced sequential environments, or a new abstraction
method that defeats strong baselines and is independently replicated.

### From exact planning to multi-step Q learning

An exact solver can serve as a reference oracle for a later experience-based
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
separated before fitting. A credible gate should require lower held-out Bellman
error as informative experience grows, better held-out rollout return than
myopic and small-data controls, zero forbidden selections, deterministic
duplicate builds, source-removal and label-permutation controls, and comparison
with expert graphs, dense tables, and online search.

If additional rows repeat the same authored dynamics and do not improve a
held-out metric, the correct conclusion is increased enumeration, not increased
knowledge.

## 14. The next step: proof-carrying decisions

The next tutorial can strengthen each table recommendation into a
proof-carrying decision package:

```text
decision request
  + canonical observations
  + authority-scoped facts and norms
  + selected logic profile
  + proof or countermodel objects
  + utility and transition model
  + Q-table path
  + negative knowledge and review triggers
  + deterministic verification receipt
```

ESSO is a useful backend for finite decision graphs. Tau can express a governed
logic boundary. Lean can prove mathematical invariants about the compiler.
PopperPad can preserve failed hypotheses and minimal counterexamples. The
Research Kernel can coordinate hypotheses, evidence, and promotion states.

The authority rule remains stable across those tools:

```text
models propose
formal and deterministic tools check declared claims
an explicit gate owns promotion and effects
```

That is how a large synthetic pipeline becomes more than a pile of plausible
bytes. It becomes a bounded, falsifiable, replayable decision system.
