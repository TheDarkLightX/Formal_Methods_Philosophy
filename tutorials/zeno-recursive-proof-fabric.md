---
title: "ZRPF: how ZenoDEX composes proofs into a governed root"
layout: docs
kicker: Tutorial 62
description: A visual, first-principles, evidence-scoped introduction to the Zeno Recursive Proof Fabric, from authenticated Spot leaves and NodeJournalV3 to recursive structure, information flow, data availability, verifier authority, atomic admission, and proof-market design.
---

Picture an inspection hub at the end of a trading epoch. Sealed packets arrive
from different execution lanes. Each packet names its scope, identifies the
program that produced it, commits to a state transition, and carries a receipt
that a verifier can check. The hub verifies bounded groups of packets and emits
new sealed summaries. The process repeats until one root summarizes the tree.

That picture captures the structural idea behind the **Zeno Recursive Proof
Fabric**, abbreviated **ZRPF**. The exact system is more disciplined than the
metaphor:

| Picture | ZRPF object |
|---|---|
| sealed packet | authenticated proof receipt plus exact public journal |
| inspection card | `NodeJournalV3` |
| sorting group | canonical bounded child partition |
| higher-level packet | structural aggregate receipt |
| final manifest | recursive root journal |
| admission desk | governed ZenoLedger admission policy |

ZRPF has one central design thesis: recursive proof composition becomes
auditable when every level preserves a small governed interface and every
additional guarantee remains an explicit obligation. The proof tree,
data-availability policy, semantic checks, admission rule, privacy model, and
performance model therefore have distinct jobs.

The word *fabric* captures that systems view. ZRPF is a common composition
layer for proof tasks, journals, recursive nodes, proof-system adapters,
data-availability evidence, ledger admission, and eventually proof
procurement. ZenoDEX is the first application described here. Other
applications would need their own governed semantic leaf profiles.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Scope and evidence date</p>
  <ul>
    <li><strong>Evidence snapshot:</strong> this tutorial reflects the ZRPF work inspected on July 10, 2026.</li>
    <li><strong>Current evidence:</strong> a temporary local RISC0 profile contains four authenticated Spot compatibility leaves, two structural level-one receipts, one structural level-two root, and successful verifier-only replay.</li>
    <li><strong>Evidence caveat:</strong> the verifier replay has a recorded source closure. The proving run remains temporary-path evidence, and its executed proving-harness source closure was not attested after a later harness patch.</li>
    <li><strong>Proposed architecture:</strong> semantic aggregation, conflict scheduling, verified data availability, durable atomic admission, proof-market operation, and settlement checkpoints remain separate work items.</li>
    <li><strong>Non-claims:</strong> this page makes no production-readiness, witness-privacy, full ZenoDEX conservation, measured-throughput, or settlement-authority claim.</li>
  </ul>
</div>

<figure class="fp-figure zrpf-media-stage">
  <p class="fp-figure-title">ZRPF at a glance</p>
  <img
    class="fp-diagram"
    src="{{ '/assets/images/zrpf/zrpf-fabric-overview.png' | relative_url }}"
    alt="A five-stage ZRPF flow from ZenoDEX execution to a proof task, leaf proof, recursive root, and governed admission."
    loading="eager"
  >
  <figcaption class="fp-figure-caption">
    The complete path is the proposed architecture. The cyan subtree marks the bounded structural portion with current local evidence.
  </figcaption>
</figure>

<div class="zrpf-status-grid" aria-label="ZRPF claim status legend">
  <section class="zrpf-status-card" data-status="current">
    <p class="zrpf-status-label">Current evidence</p>
    <p>Typed V3 structure, Spot compatibility leaves, exact child-receipt verification, and a four-leaf two-level local proof tree.</p>
  </section>
  <section class="zrpf-status-card" data-status="proposed">
    <p class="zrpf-status-label">Proposed architecture</p>
    <p>Semantic composition, conflict scheduling, DA verification, atomic admission, proof procurement, and external checkpoints.</p>
  </section>
  <section class="zrpf-status-card" data-status="target">
    <p class="zrpf-status-label">Benchmark target</p>
    <p>Capacity and throughput envelopes that still require reproducible latency, cost, memory, network, and adversarial-load measurements.</p>
  </section>
</div>

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Companion semantic layer</p>
  <p>
    This page focuses proof composition. The companion
    <a href="{{ '/tutorials/zeno-resource-machine-and-recursive-proof-fabric/' | relative_url }}">ZRM + ZRPF tutorial</a>
    explains how typed resources, nullifiers, policy, conservation, journal
    stages, and atomic commit can give a recursive root a scoped state-transition
    meaning. The integrated architecture remains a future evidence target.
  </p>
</div>

## Part I: the problem ZRPF addresses

ZRPF addresses a systems-composition problem. A DEX may execute thousands of
operations during one epoch, while its final verifier needs a bounded,
well-defined public interface. An unbounded input containing every transaction,
asset row, receipt, and cross-lane message would reproduce the scaling problem
at the final verification step.

### Four artifacts come first

This tutorial follows the first-principles method developed in
[Jung-Hua Liu's protocol-design article](https://medium.com/@gwrx2005/principled-design-and-analysis-of-zero-knowledge-protocols-for-intent-centric-private-state-99632c60a898):
write down the information-flow topology, external interfaces, security
properties, and performance characteristics as co-equal design artifacts.
Applied to ZRPF, the four artifacts are:

| Design artifact | ZRPF question | Current status |
|---|---|---|
| information-flow topology | Which facts reach the prover, guest, host, ledger, DA system, and observer? | Public receipt and journal flow are partly specified. End-to-end privacy is open. |
| external interfaces | Which exact tasks, receipts, journals, image IDs, manifests, and reject reasons cross trust boundaries? | `NodeJournalV3` and the sealed RISC0 receipt boundary are implemented in the bounded profile. |
| security properties | Which adversary moves must fail, and which state must remain unchanged after rejection? | Several receipt-binding attacks are exercised. Semantic conservation and atomic admission remain open. |
| performance characteristics | Which limits and measurements constrain proving, verification, DA, memory, and admission? | Structural bounds exist. End-to-end measurements do not. |

This order makes backend selection a consequence of the relation, trust
boundaries, and operating point. It also prevents a succinct root from
silently inheriting guarantees that were never part of its proved statement.

ZRPF instead aims for a fixed public surface with variable internal scale. A
leaf proof authenticates one bounded unit of work. Aggregate proofs verify
bounded sets of child receipts and emit the same journal type. A root journal
contains commitments and counts rather than an unbounded transcript.

The intended topology is:

```text
application execution
  -> canonical task and statement
  -> conflict-aware partitioning
  -> leaf proofs
  -> bounded recursive aggregates
  -> epoch root
  -> atomic ZenoLedger admission
  -> optional Tau or external settlement checkpoint
```

### Who sees what, and who may decide

The current evidence supports only part of the information-flow topology. The
following table separates observed interfaces from deployment assumptions:

| Actor or boundary | Information received | Authority after successful checks |
|---|---|---|
| leaf prover | bounded task and the witness supplied by its deployment | may propose a receipt; gains no ledger authority |
| aggregate guest | exact child receipts and their public journals | may authenticate one structural parent journal |
| sealed host verifier | receipt, exact journal bytes, governed image ID, and profile | may expose a verified child descriptor |
| ZenoLedger admission policy | proposed root, governed bindings, DA evidence, and current ledger state | atomic state admission is proposed and unimplemented in this profile |
| network observer | public journals plus possible timing, size, routing, and retry metadata | no current privacy bound is established |

The current structural claim is conditional on the soundness of the pinned
RISC0 receipt system, collision resistance of the selected hashes, correct
governance of image and profile identifiers, and the recorded source closure.
The temporary proving-run source-closure caveat remains in force.

Three costs remain real:

1. application execution still has to run;
2. leaf and aggregate proofs still have to be produced;
3. the underlying data still has to be published or made retrievable under a
   separate availability policy.

Recursion compresses the final verification interface. It does not make the
represented computation free.

## Part II: one authenticated leaf

A recursive tree inherits its authority from its leaves. The current
compatibility path begins with an existing ZenoDEX Spot V1 proof receipt. A
RISC0 adapter guest accepts only the compile-time governed Spot program,
profile, and lane. Its authority-bearing order is:

```text
bounded adapter input
  -> verify the exact Spot receipt under the pinned Spot image
  -> decode the exact authenticated Spot journal
  -> derive the compatibility commitments
  -> commit one canonical NodeJournalV3 leaf
```

The ordering closes an important attack surface. Decoding a caller-supplied
journal first would allow unverified metadata to influence the proof path.
Receipt verification comes first, and the exact authenticated journal becomes
the source for every derived field.

### What the leaf says

A V3 leaf fixes these structural values by construction:

```text
node_kind              = leaf
node_level             = 0
immediate_child_count  = 0
leaf_count             = 1
subtree_node_count     = 1
```

The Spot V1 journal does not disclose how many user transactions produced its
transition. The compatibility adapter therefore records:

```text
operation_count = 1
count_unit_id    = source_transition_receipt
```

The value means one authenticated source transition receipt. Reading it as one
transaction would strengthen the claim beyond the available evidence.

### Why the common journal matters

`NodeJournalV3` groups the public statement into five conceptual regions:

1. **Scope:** application, domain, epoch interval, policy, feature suite, and
   toolchain or dependency locks.
2. **Counts and partition:** node level, child count, leaf count, operation
   count, count-unit identity, subtree size, and a dense half-open partition.
3. **Proof identity:** task, statement, program, proof profile, manifest, and a
   verifier ID derived from the program and profile.
4. **Application commitments:** state, inputs, transactions, effects,
   receipts, write sets, asset deltas, cross-lane messages, schedules, data
   availability, carry state, and provenance.
5. **Child roots:** ordered commitments to child tasks, claims, journals,
   programs, profiles, verifiers, statements, manifests, effects, provenance,
   and DA roots.

Every mandatory commitment is nonzero. A profile uses a domain-separated
empty-set hash when a set is empty. Zero cannot quietly mean “unused.” Facts
that the Spot V1 adapter cannot establish, such as a verified DA certificate or
carry continuity, receive distinct nonzero unsupported sentinels. An admission
profile that requires those facts must reject the compatibility leaf.

<figure class="fp-figure zrpf-media-stage">
  <p class="fp-figure-title">The common node interface</p>
  <img
    class="fp-diagram"
    src="{{ '/assets/images/zrpf/zrpf-common-journal.png' | relative_url }}"
    alt="A NodeJournalV3 card shared by a leaf and an aggregate, divided into scope, counts and partition, identity, commitments, and child roots."
    loading="lazy"
  >
  <figcaption class="fp-figure-caption">
    Leaves and aggregates share one journal shape. The interface carries structural commitments; profile-specific semantic evidence must still justify their application meaning.
  </figcaption>
</figure>

## Part III: how the recursive tree composes

Recursive composition is safe only when a parent authenticates every child and
derives one canonical public statement. The current proof-bearing example
contains seven receipts:

```text
Spot receipt 0 -> adapter leaf 0 --\
                                  -> structural L1 left --\
Spot receipt 1 -> adapter leaf 1 --/                         \
                                                             -> structural L2 root
Spot receipt 2 -> adapter leaf 2 --\                         /
                                  -> structural L1 right --/
Spot receipt 3 -> adapter leaf 3 --/
```

Each structural guest verifies every exact child receipt inside the zkVM before
decoding the child journal. The level-one guest accepts adapter receipts. The
level-two guest accepts level-one structural receipts. The host independently
reconstructs the expected parent journals and checks exact equality.

<figure class="fp-video-figure zrpf-media-stage">
  <p class="fp-figure-title">Visual tour of the proof fabric</p>
  <video
    class="fp-video"
    controls
    playsinline
    preload="metadata"
    poster="{{ '/assets/images/zrpf/zrpf-evidenced-tree.png' | relative_url }}"
  >
    <source src="{{ '/assets/videos/zrpf/zrpf-proof-fabric.mp4' | relative_url }}?v=20260710-hd" type="video/mp4">
    <track
      kind="captions"
      srclang="en"
      label="English"
      src="{{ '/assets/videos/zrpf/zrpf-proof-fabric.vtt' | relative_url }}"
      default
    >
    The browser cannot play the embedded ZRPF animation.
  </video>
  <figcaption class="fp-figure-caption">
    The Blender animation follows the evidence labels used throughout this page: current structural evidence in cyan, DA obligations in violet, accepted gates in green, rejects in red, and proposed or benchmark-dependent claims in amber.
  </figcaption>
</figure>

<figure class="fp-figure zrpf-media-stage">
  <p class="fp-figure-title">The locally evidenced tree</p>
  <img
    class="fp-diagram"
    src="{{ '/assets/images/zrpf/zrpf-evidenced-tree.png' | relative_url }}"
    alt="Four Spot adapter leaves grouped into two level-one structural receipts and one level-two structural root."
    loading="lazy"
  >
  <figcaption class="fp-figure-caption">
    The observed tree has four leaves, seven total nodes, and depth two. Its count unit is source-transition receipt. The root has structural computational-integrity evidence within the recorded local profile.
  </figcaption>
</figure>

### Canonical child composition

For child journals `c_1, ..., c_n`, the structural constructor requires:

```text
1 <= n <= 8
same scope hash
same child level
same operation-count unit
unique immediate task, claim, and journal identities
canonical dense partitions with no internal gap or overlap
checked leaf, operation, subtree, byte, and level bounds
```

Canonical ordering uses each child partition and task identity. Permuting the
same valid child set yields the same parent. Swapping persisted level-one
receipts into the wrong expected positions changes the expected journal and is
rejected.

Counts are derived with checked arithmetic:

```text
leaf_count(parent)      = sum(leaf_count(child_i))
operation_count(parent) = sum(operation_count(child_i))
subtree_nodes(parent)   = 1 + sum(subtree_nodes(child_i))
```

The operation-count equation is meaningful only after every child proves the
same `count_unit_id`. Transaction counts cannot be added to transition-receipt
counts.

### Bounds, tests, and observed proof evidence

| Surface | Current V3 compiled bound | Current receipt evidence | Broader architecture ceiling |
|---|---:|---:|---:|
| immediate children | 8 | 2 per observed aggregate | 16 |
| maximum node level | 2 | 2 | 4 |
| leaves per root | 64 | 4 | 65,536 |
| total nodes | 73 | 7 | profile-dependent |
| operations per leaf | 128 | 1 source transition receipt | 1,024 protocol maximum in the architecture draft |
| node journal bytes | 4,096 | 1,547 in the recorded tree | profile-specific |

Pure constructor tests include a saturated 64-leaf structural tree. The
cryptographic receipt evidence currently covers the four-leaf tree shown
above. Neither fact supplies a throughput number.

### The semantic boundary

The structural aggregate derives field-specific roots over authenticated child
commitments. It currently does not verify the ZenoDEX meaning of those roots.
The following obligations remain outside the current aggregate relation:

- asset-delta-row conservation;
- complete accepted and rejected receipt semantics;
- descendant-wide receipt, task, message, and write-set uniqueness;
- cross-lane message cancellation;
- conflict-schedule validity;
- carry-queue continuity;
- data-availability certificate policy;
- complete value-flow coverage.

A future semantic aggregate profile must verify disclosures or certificates
for those facts before it commits the parent journal.

## Part IV: scheduling work without inventing parallelism

Proof parallelism is constrained by state dependence. Recursive trees create
parallel proof opportunities only when the underlying state transitions can be
separated safely. A proposed scheduler derives read and write sets, builds a
conflict graph, and commits the resulting schedule.

Two tasks can run independently when their effects do not conflict. A simple
sufficient condition is:

```text
W_i ∩ (R_j ∪ W_j) = ∅
and
W_j ∩ (R_i ∪ W_i) = ∅
```

Here (R_i) and (W_i) are the read and write sets for task (i). Unknown or
unbounded write sets belong in a conservative serial lane.

A popular liquidity pool illustrates the hard case. Two swaps cannot both
pretend to start from the same reserve state. The architecture proposes one of
four treatments:

- deterministic batch clearing;
- state-delta netting;
- canonical ordered execution;
- a specialized conflict-aware leaf proof.

The current four-leaf structural profile proves dense partition structure. It
does not prove a complete conflict-free ZenoDEX schedule.

## Part V: a proof root is not a data-availability certificate

Computational integrity and data availability answer different questions. A
catalog can prove that a book with a particular digest belongs to a collection.
The catalog does not place a readable copy of the book in a reader's hands. A
proof root and data availability have the same separation.

A recursive proof can establish that computation used data committed by a
root. Availability needs an independently checked policy, such as full
replication, erasure-coded sampling, a committee receipt, public-testnet replay,
or a chain-native blob commitment.

<figure class="fp-figure zrpf-media-stage">
  <p class="fp-figure-title">Two rails into admission</p>
  <img
    class="fp-diagram"
    src="{{ '/assets/images/zrpf/zrpf-proof-vs-data-availability.png' | relative_url }}"
    alt="A cyan proof rail and violet data-availability rail entering a proposed ledger-admission gate as separate obligations."
    loading="lazy"
  >
  <figcaption class="fp-figure-caption">
    Current V3 journals contain DA commitment fields. The Spot adapter marks unsupported DA-certificate semantics explicitly, and the current structural tree does not verify retrieval policy.
  </figcaption>
</figure>

The proposed admission condition has the shape:

```text
admit(root)
  ⇒ proof_ok(root)
  ∧ da_policy_ok(root)
  ∧ governed_bindings_ok(root)
```

The conjunction prevents a valid computation proof from silently supplying a
missing availability guarantee.

### Whole-system privacy remains a separate specification

A proof can limit what its public statement reveals while the surrounding
system still leaks information through witness custody, task routing, bid
traffic, journal sizes, timing, retries, DA retrieval, or admission logs. A
future ZRPF privacy claim therefore needs an explicit network adversary and a
fact-by-party leakage table covering the complete path.

The current profile establishes neither witness privacy nor system privacy.
Its public journals intentionally reveal scope, counts, partitions, program
identity, and commitment structure. The proof-market and DA designs may create
additional metadata channels. Those channels require bounded leakage claims
and adversarial tests before a privacy label can carry authority.

## Part VI: verifiers decide

Authority advances through a sequence of successful checks. ZRPF uses this
layered rule:

```text
prover proposes bytes
guest verifies witnesses and exact child receipts
host verifies receipts, exact journals, and program identity
ledger verifies governed policy and state bindings
only then may state or rewards commit
```

<figure class="fp-figure zrpf-media-stage">
  <p class="fp-figure-title">Where authority moves</p>
  <img
    class="fp-diagram"
    src="{{ '/assets/images/zrpf/zrpf-verifier-authority.png' | relative_url }}"
    alt="Prover bytes passing through guest, host, and proposed ledger-policy verification, with invalid inputs diverted to a no-op reject lane."
    loading="lazy"
  >
  <figcaption class="fp-figure-caption">
    Guest and sealed-host receipt verification exist in the current bounded profile. Durable ledger policy and atomic admission remain proposed.
  </figcaption>
</figure>

### The sealed receipt boundary

The host-side `VerifiedNodeReceiptV3` object keeps its fields private and
enforces this sequence:

```text
verify Succinct receipt under the expected image
  -> strict-decode the exact canonical NodeJournalV3 bytes
  -> require journal.actual_program_id = verified image ID
  -> derive the claim binding locally
  -> expose a child descriptor
```

This construction prevents a caller-selected claim hash or self-reported
program label from becoming proof authority.

### Falsification controls already exercised

| Attacker move | Expected result | Current local result |
|---|---|---|
| omit a required child assumption | aggregate proof cannot verify the child | rejected |
| substitute one source-journal byte | original receipt no longer authenticates the exact bytes | rejected |
| swap the two persisted level-one receipts | reconstructed root journal differs | rejected |
| present a receipt under the wrong image | program and receipt binding fails | rejected |
| use a cryptographically valid false self-label | outer program-image equality fails | rejected |

The intended reject law is stronger than returning an error message:

```text
reject
  ⇒ state'    = state
  ∧ replay'   = replay
  ∧ rewards'  = rewards
  ∧ finality' = finality
```

The current proof profile exercises receipt and journal rejects. The complete
state-level no-op law still needs the proposed durable admission layer and its
crash-consistency tests.

## Part VII: atomic admission and the finality ladder

A valid root becomes authoritative state only through admission. Once a
semantic root eventually satisfies its proof, policy, schedule, and DA
obligations, ZenoLedger admission must update several records as one atomic
transaction:

- application state root;
- authenticated root and journal identity;
- exact-once root, child, receipt, and message replay sets;
- carry-queue state;
- DA certificate root;
- proof-market payouts and slashes;
- finality status.

<figure class="fp-figure zrpf-media-stage">
  <p class="fp-figure-title">The proposed atomic bundle</p>
  <img
    class="fp-diagram"
    src="{{ '/assets/images/zrpf/zrpf-atomic-admission.png' | relative_url }}"
    alt="State root, replay sets, carry queue, data-availability root, and proof-market payouts entering one atomic commit, followed by four finality states."
    loading="lazy"
  >
  <figcaption class="fp-figure-caption">
    A crash must not commit value effects without replay protection, or consume replay state without the corresponding value effects. This admission path is proposed and has no current production authority.
  </figcaption>
</figure>

The architecture separates four finality meanings:

| State | Meaning |
|---|---|
| `EXECUTED` | ZenoLedger ordered and applied the operation. |
| `PROVEN` | The operation is included in an authenticated recursive root. |
| `CHECKPOINTED` | The configured settlement anchor accepted the root. |
| `FINALIZED` | The anchor's finality policy is satisfied. |

Tau is proposed as a slower checkpoint, policy, and hard-finality layer. The
design does not require every trade to execute directly through Tau.

## Part VIII: proof-system adapters and the proof market

Proof-system neutrality is a governed-interface property. The common journal
and task statement allow different backends to describe the same kind of node,
provided that each adapter authenticates its program and emits the standard
journal. RISC0 3.0.5 is the current reference backend because the repository
already contains a hardened recursive receipt boundary.

Backend choice should follow the shape and rate of change of the proved
relation. The following table is a design heuristic, not an implemented ZRPF
backend matrix:

| Relation regime | Candidate substrate | Potential fit | Main obligation |
|---|---|---|---|
| fixed, compact, heavily optimized relation | bespoke arithmetic circuit | low constant factors after substantial circuit engineering | prove that every witness value and public input is fully constrained |
| long repeated step computation | folding or incremental verification | amortized step processing with final compression | account for fold seams, relaxed relations, and final compression assumptions |
| evolving, general program | zkVM | ordinary program semantics and faster iteration | trust and test the VM, guest program, continuation logic, and image binding |
| heterogeneous proof fabric | governed adapters over several substrates | assign each relation to a suitable backend | specify and test every adapter seam and shared serialization contract |

The current ZRPF evidence occupies the zkVM row. The other rows describe
possible future profiles. Each new profile would need its own governed program
identity, canonical codec, cross-implementation vectors, negative controls,
and release evidence.

The proposed proof market treats proving as procurement. Its default policy is
a commit-reveal reverse auction with explicit assignment:

```text
publish bounded task
  -> receive bonded bid commitments
  -> reveal price, latency, capacity, and proof-system version
  -> assign primary and standby provers under diversity limits
  -> verify submitted receipt and exact journal
  -> pay only accepted assigned work
```

Critical roots may require proofs from independently governed implementations.
Objective violations, such as equivocation or an unauthorized manifest, can be
slashed under an explicit policy. Proof-looking bytes alone earn no reward.

This market remains architectural work. The current temporary structural tree
was produced by a local proving harness rather than a deployed permissionless
procurement system.

## Part IX: reading performance formulas honestly

Capacity formulas describe conditional envelopes. A meaningful performance
claim also fixes hardware, software versions, concurrency, proof mode, network
conditions, DA policy, workload distribution, and the statistic being
reported.

Let:

```text
k       = recursive fanout
D       = tree depth
B       = operations per semantic leaf
E       = epoch duration in seconds
P       = concurrent leaf-proving capacity
T_leaf  = leaf proof latency
T_agg   = aggregate latency per level
S_op    = available bytes per operation
BW_DA   = sustainable DA bandwidth
```

An architecture envelope is:

```text
architecture_TPS = (B × k^D) / E
```

Actual throughput is bounded by the slowest required subsystem:

```text
actual_TPS = min(
  execution_TPS,
  prover_TPS,
  architecture_TPS,
  DA_TPS,
  admission_TPS
)
```

| Quantity | Status | Honest reading |
|---|---|---|
| four leaves, two levels | current local evidence | four authenticated source-transition receipts in one structural tree |
| fanout 8, level 2, 64 leaves | current compiled bound | bounded construction capacity, with pure saturated-tree tests |
| 819 TPS | initial architecture target | `8^2` leaves, 128 semantic operations per leaf, ten-second epoch, assuming every other bottleneck keeps pace |
| about 104,858 TPS | ambitious scale envelope | `16^3` leaves, 256 operations per leaf, ten-second epoch, requiring a future profile and extensive benchmarks |

The compatibility leaves currently count source transition receipts, so their
operation count cannot be substituted for `B` in a transaction-throughput
claim. No ZenoDEX TPS, latency, proving cost, RAM, VRAM, or DA bandwidth result
is established by the current proof tree.

Total prover work remains approximately linear in represented computation:

```text
total_work ≈
  leaf_count × leaf_work
  + ((leaf_count - 1) / (k - 1)) × aggregate_work
```

Recursion mainly stabilizes the final proof interface and final verification
cost. It does not erase the work performed below the root.

## Part X: a compact audit checklist

Eight questions locate the authority boundary of a future ZRPF claim:

1. **What is the information-flow topology?** List each party, each visible
   fact, each hidden fact, and every residual metadata channel.
2. **Which external interface crosses each trust boundary?** Pin exact codecs,
   domain separators, identifiers, size bounds, and failure semantics.
3. **Which adversary and security property are in scope?** State the attack
   game, setup assumptions, and the condition under which acceptance is safe.
4. **Which typed statement is proved?** Scope, count units, profiles, and
   commitment semantics must be explicit.
5. **Which program and manifest are governed?** A self-reported image or
   manifest has no authority.
6. **Which exact receipt authenticates which exact journal?** Duplicate host
   metadata cannot strengthen the authenticated statement.
7. **Which obligations remain separate?** Semantic conservation, conflict
   freedom, DA, privacy, admission, and finality need their own evidence.
8. **Which performance claim was measured, and what changes on rejection?**
   Record the cost model and require a no-op across application, replay,
   reward, carry, and finality state.

<figure class="fp-figure zrpf-media-stage">
  <p class="fp-figure-title">The final claim map</p>
  <img
    class="fp-diagram"
    src="{{ '/assets/images/zrpf/zrpf-claim-status.png' | relative_url }}"
    alt="Three panels separating current ZRPF evidence, proposed architecture, and benchmark targets."
    loading="lazy"
  >
  <figcaption class="fp-figure-caption">
    The structural proof path is real within its recorded local scope. Semantic composition is partial. Performance remains to be measured.
  </figcaption>
</figure>

## Part XI: organize evidence as nested loops

Cryptographic ground truth is expensive. A full proof run may take minutes or
hours, while an external review may take weeks. The loop-engineering method in
Liu's article places cheap falsifiable checks before expensive verdicts. For
ZRPF, the useful hierarchy is:

| Loop | Typical check | Status in the inspected profile |
|---|---|---|
| specification and vector | canonical hash vectors, codec vectors, field meaning, and bound derivation | present for the V1 adapter and V3 hash construction |
| pure constructor | valid saturated trees plus wrong-level, duplicate, gap, overflow, and noncanonical inputs | present for bounded structural composition |
| sealed receipt | prove or replay, then bind exact receipt, exact journal, governed image, and locally derived claim | present for the four-leaf profile |
| persisted verifier replay | reconstruct both level-one journals and the root from seven saved receipts | present, with the recorded source-closure caveat |
| semantic and admission | conservation, conflict schedule, DA policy, carry continuity, exact-once commit, and reject-is-no-op | future work |
| benchmark and adversarial load | latency distributions, proving cost, memory, bandwidth, crash recovery, and denial-of-service bounds | future work |
| release and independent review | governed manifest, cross-host replay, independent implementation, and external audit | future work |

Each rung supports a bounded claim and gates the next rung. Passing a fast
checker supplies evidence for its stated surface. Promotion still depends on
the broader semantic, operational, and governance checks appropriate to the
claim.

## Reproducing the visual assets

The animation and stills are generated from a procedural Blender scene. From
the FormalPhilosophy repository root:

```bash
scripts/render_zrpf_blender_tutorial.sh --render-stills --render-video
```

The source generator is `scripts/blender/render_zrpf_tutorial.py`. It creates:

- `assets/blender/zrpf-proof-fabric.blend`;
- seven PNG teaching frames under `assets/images/zrpf/`;
- the 48-second, 1920×1080 MP4 under `assets/videos/zrpf/`;
- a render manifest containing Blender version, file sizes, and SHA-256
  digests.

The compact machine-readable claim ledger is available at
[`zrpf_tutorial_claims_20260710.json`]({{ '/assets/data/zrpf_tutorial_claims_20260710.json' | relative_url }}).

## Source posture

The main July 10 source artifacts used for this tutorial are:

- *Zeno Recursive Proof Fabric Architecture Specification*, version 0.1 draft;
- *ZRPF V3 Correct-by-Construction Protocol Specification*;
- *ZRPF V1 Leaf Adapter Compatibility Specification*;
- the public
  [*ZRPF RISC0 Structural Proof Profile*](https://github.com/TheDarkLightX/ZenoDEX/blob/agent/zrpf-v3-structural-cbc/zk/zrpf_risc0/README.md);
- the V1 Spot adapter and V3 structural-tree temporary local evidence
  manifests;
- the recorded verifier replay and negative-control transcripts.

Several of those artifacts were still temporary or unpromoted when inspected.
Their names identify the evidence basis without implying a release-backed or
public-replay status.

Promotion from this bounded profile to production would be a new specification
and review exercise. It would need governed release identities, public and
cross-host replay, semantic aggregation, DA policy, atomic admission,
adversarial load measurements, privacy analysis, and independent review.

## References and influences

1. Jung-Hua Liu,
   [“Principled Design and Analysis of Zero-Knowledge Protocols for Intent-Centric Private State Machines: From Shielded State Synchronization to Verifiable Resource Machines”](https://medium.com/@gwrx2005/principled-design-and-analysis-of-zero-knowledge-protocols-for-intent-centric-private-state-99632c60a898),
   Medium, July 1, 2026. Its first-principles ordering, regime-sensitive proof-system analysis, whole-system privacy framing, and nested evidence loops influenced the organization of this tutorial.
2. ZenoDEX,
   [“ZRPF RISC0 Structural Proof Profile”](https://github.com/TheDarkLightX/ZenoDEX/blob/agent/zrpf-v3-structural-cbc/zk/zrpf_risc0/README.md),
   `agent/zrpf-v3-structural-cbc` branch, accessed July 10, 2026. This is the public technical anchor for the implemented four-leaf RISC0 profile and its explicit authority boundary.
