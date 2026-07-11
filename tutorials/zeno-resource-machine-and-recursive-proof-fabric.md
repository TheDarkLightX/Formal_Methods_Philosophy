---
title: "ZRM + ZRPF: from proof roots to exact-once resource transitions"
layout: docs
kicker: Tutorial 63
description: A beginner-facing guide to the Zeno Resource Machine, the Zeno Recursive Proof Fabric, their journal boundary, admission and aggregation modes, exact-once semantics, and the evidence still needed for an integrated system.
---

A recursive proof can summarize a large tree of authenticated computations in
one root. A state machine still needs rules for what that root may change.

The **Zeno Recursive Proof Fabric** (ZRPF) and the **Zeno Resource Machine**
(ZRM) address those two questions:

| Layer | Main question |
|---|---|
| ZRPF | Did the expected proof programs authenticate these exact journals and compose them under the governed profile? |
| ZRM | Do these resource changes satisfy existence, freshness, authority, units, conservation, policy, replay, and atomic-commit rules? |

Their common seam is a canonical journal. Before commit, ZRM constructs a
`JournalDraft`. A ZRPF admission profile may authenticate that exact draft.
After successful atomic commit, the runtime returns an `AcceptedJournal`. A
separate ZRPF aggregation profile may compress accepted journals for audit or
anchoring.

This separation gives the pairing its architectural significance. ZRPF can
make verification of many authenticated statements compact. ZRM can make the
state effects of those statements explicit, deterministic, and exact-once.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Evidence and assumption hygiene</p>
  <ul>
    <li><strong>Evidence snapshot:</strong> this tutorial reflects the ZRM and ZRPF materials inspected on July 11, 2026.</li>
    <li><strong>ZRM evidence:</strong> the inspected pre-alpha development snapshot reports a ZRM-L0 implementation slice covering types, canonical resource bytes, vectors, and codec-focused controls. The semantic kernel, authenticated facts, durable commit, proof adapters, and recursive integration remain unimplemented.</li>
    <li><strong>ZRPF evidence:</strong> the bounded public RISC0 profile authenticates a four-leaf, two-level structural tree. Its current claim concerns proof and journal structure, with application semantics outside that aggregate relation.</li>
    <li><strong>Integration status:</strong> the paired interface is a specified architecture. No end-to-end ZRM plus ZRPF implementation or release evidence is claimed.</li>
    <li><strong>Conditional significance:</strong> if the semantic, persistence, proof-binding, data-availability, release, and adversarial gates described below pass, the pair would support compact verification of exact-once, proof-carrying resource transitions.</li>
    <li><strong>Non-claims:</strong> no production-readiness, privacy, consensus, finality, token-value, physical-resource, real-world-truth, or measured-performance claim is made.</li>
  </ul>
</div>

<figure class="fp-figure">
  <p class="fp-figure-title">The typed seam between ZRM and ZRPF</p>
  {% include diagrams/zrm-zrpf-composition.svg %}
  <figcaption class="fp-figure-caption">
    ZRM owns deterministic resource semantics and the commit plan. ZRPF owns
    exact proof and journal authentication. Admission binds a draft before
    commit; postcommit aggregation binds an accepted journal after commit.
  </figcaption>
</figure>

## Part I: what problem remains after a proof verifies?

Suppose a zkVM receipt verifies successfully. That establishes a statement of
the form:

```text
the expected program ran and committed this public output
```

Several state questions remain:

- Did every consumed object exist in the current state?
- Had any consumed object already been used?
- Did the controller have authority for this transition?
- Do all quantities use compatible units?
- Is value conserved, or is a cross-kind transformation explicitly authorized?
- Is the policy version still current?
- Which output resources become canonical?
- Can the same receipt collect a reward twice?
- Does rejection leave state, replay protection, and rewards unchanged?
- Can a crash commit an effect without its matching nullifier?

The verified program can include some of these checks. ZRM makes them part of a
proof-system-neutral semantic contract. The same reference semantics can be
evaluated locally, formally modeled, or authenticated through different proof
backends.

The core law is:

```text
Anyone may propose a resource transition.
Only a transition whose semantics and authority verify may commit.
```

Proof bytes, journal bytes, JSON metadata, and a caller-provided
`verified = true` flag remain untrusted data. Authority appears only after the
governed verifier and the semantic kernel construct sealed typed results.

## Part II: resources make state changes explicit

A ZRM resource is an immutable typed commitment representing something that
can be created, controlled, transformed, consumed, or referenced under
explicit rules.

Examples include:

- a balance, position, escrow, or settlement receipt;
- a proof task, assignment, prover bond, capacity reservation, or reward claim;
- a model checkpoint, evaluation receipt, or dataset-use capability;
- an evidence artifact, challenge, storage lease, or revocation right.

A resource can be nonfinancial, nonfungible, private under a future profile,
or independent of a blockchain. Claims about physical measurements, legal
rights, or real-world events still require an external trust root. ZRM can
check whether a governed policy used an attestation correctly. It cannot
create truth about the world outside the machine.

### Consumed, referenced, and created

The three roles have different meanings:

| Role | Effect after acceptance |
|---|---|
| consumed | removed from the active set and assigned a nullifier |
| referenced | checked and retained in the active set |
| created | added as a fresh active resource |

For active set `A`, consumed set `C`, and created set `O`, the abstract update
is:

```text
A_next = (A_current - C) union O
```

Every consumed resource also inserts a nullifier. A second attempt to consume
the same resource finds a used nullifier and rejects.

For a conserved resource kind:

```text
consumed + authorized_mint = created + authorized_burn
```

A transition across unlike kinds needs a versioned transformation rule. A host
assertion cannot supply that authority. For example, a governed training rule
might authorize:

```text
ModelCheckpoint(version_n)
+ DatasetUseCapability
+ ComputeCredit
+ TrainingSpecification
    ->
ModelCheckpoint(version_n_plus_1)
+ EvaluationReceipt
+ ResidualComputeCredit
```

The example defines a symbolic resource transformation. It does not establish
that physical compute was consumed or that the resulting model is safe.

### Reject means no committed change

The intended reject law is:

```text
reject(transition, state) -> state_next = state
```

For a durable runtime, the law covers every authority-bearing record in the
same transaction:

```text
reject
  => application_state unchanged
  && active_resources unchanged
  && nullifiers unchanged
  && rewards unchanged
  && finality unchanged
```

Parsing, proof verification, semantic validation, and conflict checks therefore
finish before the commit capability becomes available.

## Part III: ZRPF makes many proof statements compact

ZRPF organizes authenticated leaves into a bounded recursive tree. Each parent
verifies exact child receipts, decodes their authenticated journals, derives a
canonical parent journal, and emits another receipt. A final verifier can check
one root instead of replaying every proof below it.

The companion
[ZRPF tutorial]({{ '/tutorials/zeno-recursive-proof-fabric/' | relative_url }})
shows the complete bounded example:

```text
four authenticated leaves
  -> two level-one structural receipts
  -> one level-two structural root
```

That public profile establishes receipt authentication, exact journal binding,
bounded tree structure, and deterministic structural composition within its
recorded evidence scope. The aggregate currently derives roots over child
commitments. It does not check the application meaning of conservation,
conflict freedom, carry continuity, data availability, or settlement.

This is the point where ZRM becomes relevant. A recursive root can authenticate
many journals. ZRM defines the semantic transition represented by each journal
and the conditions under which it may affect state.

## Part IV: one interface, two stages

The pair requires a strict distinction between data before commit and evidence
after commit.

### Admission mode

Admission mode binds a deterministic `JournalDraft` before durable state
changes:

```text
validated transition
  -> private CommitPlan + exact JournalDraft
  -> ZRPF admission proof binds JournalDraftHash
  -> host verifies expected program, policy, profile, and draft
  -> commit plan checks current state root and version
  -> atomic commit
```

An admission proof authenticates the draft and its governed statement. It does
not prove that the later compare-and-swap commit succeeded. The runtime still
has to check the current state and execute the atomic write.

### Postcommit aggregation mode

After atomic commit, the runtime returns an `AcceptedJournal`. A distinct
profile may aggregate accepted journals:

```text
AcceptedJournal_0
AcceptedJournal_1
...
AcceptedJournal_n
  -> ZRPF postcommit aggregation
  -> recursive epoch root
  -> audit, checkpoint, or external anchor
```

This root records accepted history. It cannot retroactively authorize a state
change that did not pass admission.

### Why the modes cannot substitute for one another

| Artifact | Timing | What it binds | Authority boundary |
|---|---|---|---|
| `JournalDraft` | before commit | deterministic proposed journal payload | data bound into a private commit plan |
| admission receipt | before commit | exact draft plus expected program, policy, profile, and release identity | may satisfy a governed admission obligation |
| `AcceptedJournal` | after commit | payload returned by successful durable commit | evidence of the runtime's accepted transition |
| aggregation receipt | after commit | ordered accepted journals and recursive manifest | compression, audit, or anchoring |

An aggregation leaf presented as an admission leaf must reject. An admission
leaf does not establish that commit occurred. The wrapper stage belongs in the
authenticated statement.

## Part V: semantic identity and proof-tree identity

Recursive trees introduce a subtle identity problem. The same ordered list of
accepted transitions can be grouped into different valid trees:

```text
tree A: ((j0, j1), (j2, j3))
tree B: (((j0, j1), j2), j3)
```

If grouping determined semantic history, a harmless proof-scheduling change
would change the state identity. ZRM therefore specifies two roots with
different meanings.

For accepted journals sorted by a governed canonical key:

```text
semantic_epoch_root = H(
  epoch,
  policy_root,
  journal_count,
  ordered_journal_hashes
)
```

The semantic root depends on ordered accepted history. It remains stable across
valid proof-tree regroupings.

The separate `proof_tree_root` commits:

- recursive topology;
- child positions;
- child journal and statement hashes;
- verifier policies and proof profiles;
- program or key digests;
- release identities and receipt identities.

This split supports two audits:

1. **Semantic audit:** Which accepted transitions define the epoch?
2. **Proof audit:** Which programs, receipts, profiles, and tree structure authenticated them?

The required law is:

```text
same ordered accepted journals
  -> same semantic_epoch_root
```

The `proof_tree_root` may change when a valid scheduler chooses another tree.

## Part VI: worked example, an exact-once proof reward

ZRM's first specified reference adapter is a **Proof Resource Machine**. The
following example is a design scenario, not current implementation evidence.

### Step 1: publish and fund a task

```text
ProofBudget + TaskSpecification
  -> ProofTask + RewardEscrow
```

The task fixes the statement, accepted verifier policy, deadline in logical
time, reward rule, and any redundancy requirement.

### Step 2: assign bounded capacity

```text
ProofTask + ProverCapacity + ProverBond
  -> ProofAssignment + ReservedCapacity + LockedBond
```

The assignment prevents one unit of capacity from being promised twice under
the same policy.

### Step 3: authenticate completion

The prover returns proof bytes. A governed ZRPF or direct proof adapter checks
the expected program, statement, journal, profile, and release identity. A
successful check constructs a sealed `VerifiedProofFact`.

```text
ProofAssignment + VerifiedProofFact
  -> VerifiedProofReceiptResource
   + RewardClaimResource
   + ReleasedCapacity
   + ReleasedBond
```

### Step 4: settle exactly once

```text
RewardClaim + RewardEscrow
  -> ProverPayment + ResidualEscrow
```

Now consider a replay of the original valid proof. Cryptographic verification
may accept the same proof again because its mathematical statement remains
valid. ZRM sees that the assignment or reward resource has already been
consumed. Its nullifier is present, so the replay rejects without a second
payment.

This example isolates the contribution of each layer:

- ZRPF or another governed adapter authenticates the proof statement;
- ZRM authenticates the resource lifecycle and exact-once effects;
- the runtime commits payment, nullifiers, capacity, and journal atomically;
- postcommit ZRPF aggregation can compress the accepted proof-work history.

## Part VII: an attacker-to-gate map

The pairing becomes meaningful only when each failure has a named owner and a
no-op reject path.

| Attacker move or failure | Primary gate | Required result |
|---|---|---|
| submit proof-looking bytes from the wrong program | governed ZRPF or proof adapter | reject before constructing an authenticated fact |
| pair a valid receipt with altered journal bytes | exact receipt-to-journal binding | reject exact-byte mismatch |
| use a postcommit receipt for admission | wrapper-stage binding | reject profile mismatch |
| replay a consumed resource or reward claim | ZRM nullifier and active-resource checks | reject with no payment or state mutation |
| build under an old policy | ZRM policy-root and validity-window checks | reject as stale |
| create duplicate output identifiers | ZRM uniqueness checks | reject before commit |
| mint, burn, or transform without authority | accounting and transformation rules | reject uncovered effects |
| mix quantities with incompatible units | typed unit checks | reject the accounting row |
| race two commits against one pre-state | atomic compare-and-swap | at most one commit succeeds |
| crash after effects but before replay protection | durable atomic write set | effects and replay state commit together or neither commits |
| omit or reorder a recursive child | ordered manifest and proof-tree root | reject the root |
| claim availability from a data commitment | governed DA policy | require separate availability evidence or make no availability claim |
| claim physical truth from a digital attestation | application trust-root policy | scope the claim to the authenticated attestation |

The final two rows remain separate because proof composition cannot create data
availability or external truth.

## Part VIII: where the implementation stands

ZRM defines a conformance ladder:

| Level | Required capability | July 11 snapshot |
|---|---|---|
| ZRM-L0 | typed schemas, canonical encoders, vectors, constructor rejects | pre-alpha implementation slice reported in the inspected development snapshot |
| ZRM-L1 | deterministic semantic kernel, exact-once accounting, reject-is-no-op | unimplemented |
| ZRM-L2 | sealed verified facts and proof or signature adapters | unimplemented |
| ZRM-L3 | durable atomic commit, concurrency, crash recovery | unimplemented |
| ZRM-L4 | authenticated journal leaves, semantic epoch root, recursive proof, DA policy, root replay protection | specified target |
| ZRM-L5 | formal obligations, independent review, reproducible release, public replay | future target |

The current ZRPF four-leaf structural profile supplies bounded evidence for a
different part of the eventual stack. It does not advance ZRM to L4. An L4
claim requires every lower ZRM level plus the integrated recursive and DA
obligations.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Promotion rule</p>
  <p>
    A design document can specify a higher level without supplying its evidence.
    Public maturity follows the lowest missing obligation in the dependency
    chain. The current pair remains an architecture with separately evidenced
    early slices.
  </p>
</div>

## Part IX: why the pairing could matter

The conditional value of the architecture comes from a division of labor:

- **semantic portability:** ZRM defines resource rules independently of one proof system;
- **proof scalability:** ZRPF can compress many authenticated journals into a bounded root interface;
- **exact-once effects:** nullifiers and atomic commit connect proof acceptance to durable state;
- **backend agility:** governed adapters can change proof substrates while preserving the semantic statement;
- **audit separation:** semantic history and proof topology receive distinct roots;
- **market compatibility:** proof tasks, capacity, bonds, receipts, and rewards can themselves become governed resources.

If those interfaces are implemented and independently checked, the result would
be a proof-carrying resource layer in which large batches receive compact
cryptographic authentication and every accepted effect remains subject to
deterministic resource semantics.

The performance claim remains open. Recursion can stabilize final proof size
and verification cost for a chosen profile. Total proving work, semantic
validation, data publication, storage, networking, and atomic persistence
remain real costs. Throughput requires reproducible measurements under a fixed
hardware, software, proof, workload, and DA profile.

## Part X: a safe implementation order

The dependency order prevents a proof from authenticating an underspecified
state machine:

```text
1. typed resource and transition statements
2. canonical bounded codecs and independent vectors
3. deterministic proof-independent reference semantics
4. stable accepted journals and reject receipts
5. authenticated verifier facts with exact bindings
6. private commit plans and durable atomic commit
7. admission leaf over exact JournalDraftHash
8. postcommit leaf over exact AcceptedJournal bytes
9. semantic epoch root plus separate proof-tree root
10. DA, replay, release, privacy, and adversarial gates
```

Each step should add positive vectors, negative controls, property tests,
mutations, and the bounded formal evidence appropriate to its claim. A timeout,
missing tool, unknown solver result, or unverified proof artifact remains a gap.

## Part XI: compact audit checklist

Before accepting a future integrated root, an auditor should be able to answer:

1. Which exact resource transition and policy root does each leaf bind?
2. Is the wrapper stage admission or postcommit aggregation?
3. Which governed program, proof profile, and release identity were expected?
4. Do exact receipt bytes authenticate exact canonical journal bytes?
5. Are consumed resources active and their nullifiers fresh?
6. Are outputs unique, quantities unit-compatible, and transformations authorized?
7. Does the commit plan still match the current state root, version, and validation context?
8. Do effects, nullifiers, rewards, and accepted journal commit atomically?
9. Does proof-tree regrouping preserve the semantic epoch root?
10. Which DA, privacy, consensus, finality, and external-truth obligations remain separate?
11. Which tests would fail after omission, substitution, duplication, reordering, replay, or crash?
12. Which public claim is justified by the current evidence, and which claim remains unavailable?

The machine-readable claim ledger for this tutorial is
[`zrm_zrpf_tutorial_claims_20260711.json`]({{ '/assets/data/zrm_zrpf_tutorial_claims_20260711.json' | relative_url }}).

## Sources and further reading

1. FormalPhilosophy,
   [“ZRPF: how ZenoDEX composes proofs into a governed root”]({{ '/tutorials/zeno-recursive-proof-fabric/' | relative_url }}),
   evidence snapshot July 10, 2026.
2. ZenoDEX,
   [“ZRPF RISC0 Structural Proof Profile”](https://github.com/TheDarkLightX/ZenoDEX/blob/agent/zrpf-v3-structural-cbc/zk/zrpf_risc0/README.md),
   bounded public structural profile, accessed July 11, 2026.
3. Zeno Resource Machine,
   [public repository](https://github.com/TheDarkLightX/Zeno-Resource-Machine),
   incubation project. The implementation evidence summarized here comes from
   an inspected pre-alpha development snapshot rather than a tagged public
   release.
4. Anoma,
   [“Resource Machine” specification, version 1.0.0](https://specs.anoma.net/v1.0.0/arch/system/state/resource_machine/index.html),
   background on immutable resources, nullifiers, and resource-machine state.
5. Jung-Hua Liu,
   [“Principled Design and Analysis of Zero-Knowledge Protocols for Intent-Centric Private State Machines”](https://medium.com/@gwrx2005/principled-design-and-analysis-of-zero-knowledge-protocols-for-intent-centric-private-state-99632c60a898),
   July 1, 2026. Its separation of information flow, interfaces, security
   properties, and performance characteristics informs the claim discipline
   used here.
