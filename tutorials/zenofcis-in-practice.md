---
title: "ZenoFCIS in Practice: From Pure Transitions to Atomic Commit"
layout: docs
kicker: Tutorial 67
description: "A practical guide to ZenoFCIS: its current pre-release status, Rust workspace, feature flags, decision algebra, canonical patches, candidate bundles, atomic shell, replay protection, and a small end-to-end counter example."
---

# ZenoFCIS in Practice: From Pure Transitions to Atomic Commit

[Tutorial 64](../functional-core-imperative-shell-values-as-boundaries/) developed the functional-core/imperative-shell pattern as an architectural idea. Immutable inputs enter a pure transition. The transition returns decision data. A smaller imperative shell interprets authorized effects.

[ZenoFCIS](https://github.com/TheDarkLightX/ZenoFCIS) turns that idea into a Rust library family with explicit protocol values:

```text
admitted state + command + policy + authenticated context
                         |
                         v
              pure total transition
                         |
         +---------------+--------------------+
         |               |                    |
      Accept           Reject        CommittedFailure
         |        unchanged state       intentional
         |          no candidate      committed candidate
         v
canonical patch + closed plans + exact bindings
                         |
                         v
             content-addressed bundle
                         |
                         v
       expected-root atomic shell publication
                         |
                         v
            idempotent outbox delivery
```

The practical gain is inspectability. State changes, external-delivery obligations, receipts, resource use, and version bindings become data that can be encoded, hashed, replayed, compared, and checked.

## 1. What ZenoFCIS is

ZenoFCIS is a high-assurance reference architecture and Rust implementation for systems organized around a functional core and an imperative shell. Its core primitives cover:

- transitively immutable, bounded values;
- a total three-outcome decision algebra;
- deterministic resource budgets;
- ZCVE/1 canonical encoding;
- domain-separated commitments;
- preconditioned state patches;
- closed commit and outbox plans;
- content-addressed candidate bundles and receipts;
- pure reference semantics for atomic commit, replay, and acknowledgement;
- composition and runtime-refinement reports.

Optional packages add schema validation, typed code generation, proof-evidence envelopes, a strict mounted ZenoDEX adapter, authenticated-state planning, bounded synthesis, a SQLite shell, and persistent collection backends. The current package list is visible in the workspace [Cargo manifest](https://github.com/TheDarkLightX/ZenoFCIS/blob/main/Cargo.toml), and the umbrella crate exposes the feature map in [`crates/zeno-fcis/Cargo.toml`](https://github.com/TheDarkLightX/ZenoFCIS/blob/main/crates/zeno-fcis/Cargo.toml).

The semantic packages target `no_std + alloc`, forbid unsafe Rust, and exclude ambient clocks, randomness, networking, filesystems, databases, threads, and executable effect closures. This makes the semantic boundary smaller and easier to replay. It does not prove that every downstream transition is correct.

## 2. Where development stands

This status snapshot is pinned to commit [`fd0628f`](https://github.com/TheDarkLightX/ZenoFCIS/commit/fd0628f217ede472e5344a380d5e381147c5507f), merged on July 26, 2026.

| Surface | Status at the pinned commit | What the status establishes |
| --- | --- | --- |
| Package ladder | Work packages A through H are implemented and merged in [PR #19](https://github.com/TheDarkLightX/ZenoFCIS/pull/19) | The planned reference packages and their integration surfaces exist in the repository |
| Rust API version | Workspace manifests declare `0.1.0`, Rust 1.97, edition 2024 | The source has a pre-1.0 API identity; ordinary APIs may still change between minor versions |
| PR validation | PR head [`8bc821a`](https://github.com/TheDarkLightX/ZenoFCIS/commit/8bc821ae12381c0a4da77ef8cd51e7b8034ba53d) reported successful `ci`, `ecosystem-features`, Miri, fuzz-build, and assurance workflows | Those checks passed for the exact reviewed PR head |
| Distribution | The repository has [no GitHub releases](https://github.com/TheDarkLightX/ZenoFCIS/releases) and [no tags](https://github.com/TheDarkLightX/ZenoFCIS/tags) at this snapshot | A manifest version must not be mistaken for a published, audited release |
| Runtime integration | Strict adapters and reference implementations exist | An external ZenoDEX runtime, production JMT, ESSO, solver, prover, compiler, or LLM runtime is not bundled and approved |
| Production posture | Explicitly pre-release research software | No claim of audit completion, economic correctness, side-channel resistance, value custody, or production authorization is made |

The exact release boundary appears in [Release Assurance](https://github.com/TheDarkLightX/ZenoFCIS/blob/main/docs/RELEASE_ASSURANCE.md) and the repository [security policy](https://github.com/TheDarkLightX/ZenoFCIS/blob/main/SECURITY.md).

“Implemented” therefore means that the repository contains concrete reference code, tests, and fail-closed boundaries. It does not mean that every external dependency and deployment assumption has been discharged.

## 3. Start from a reproducible source revision

There is no release tag to select at this snapshot. Evaluation should pin the exact reviewed commit:

```bash
git clone https://github.com/TheDarkLightX/ZenoFCIS.git
cd ZenoFCIS
git checkout fd0628f217ede472e5344a380d5e381147c5507f
```

The repository pins Rust 1.97.1. A focused first pass is:

```bash
python3 tools/check_assurance.py --self-test
python3 tools/check_assurance.py
cargo +1.97.1 test -p zeno-fcis-core --locked
cargo +1.97.1 test -p zeno-fcis-patch --locked
cargo +1.97.1 test -p zeno-fcis-shell --locked
```

The full local gate is larger:

```bash
cargo +1.97.1 fmt --all -- --check
cargo +1.97.1 clippy --workspace --all-targets --all-features --locked -- -D warnings
cargo +1.97.1 test --workspace --all-features --locked
```

Miri, fuzz builds, dependency policy, source manifests, `no_std` targets, and other release checks are documented in [Release Assurance](https://github.com/TheDarkLightX/ZenoFCIS/blob/main/docs/RELEASE_ASSURANCE.md). A successful local subset establishes only the checks that actually ran.

## 4. Add the umbrella crate to an experiment

Until a reviewed release tag exists, a Git dependency should pin a commit:

```toml
[dependencies.zeno-fcis]
git = "https://github.com/TheDarkLightX/ZenoFCIS.git"
rev = "fd0628f217ede472e5344a380d5e381147c5507f"
features = ["rustcrypto-sha256"]
```

The default umbrella surface includes the semantic values, codec, patches, plans, receipts, reference shell, composition, refinement, and first ZenoDEX profile. Hash providers are optional, so the example enables the vetted RustCrypto SHA-256 provider.

Useful feature choices include:

| Feature | Use |
| --- | --- |
| `rustcrypto-sha256` | Ordinary SHA-256 commitment provider |
| `sha256-parity` | RustCrypto plus libcrux provider parity |
| `schema`, `codegen` | Closed schemas and deterministic typed adapters |
| `evidence` | Canonical proof and checker evidence envelopes |
| `mounted-zenodex` | Strict complete-decision runtime comparison |
| `authenticated-state` | Sparse authenticated-state reference and proofs |
| `synthesis` | Verifier-gated bounded candidate search |
| `sqlite-shell` | Crash-atomic SQLite publication and outbox |
| `persistent-collections` | Vetted `rpds` and `imbl` collection adapters |
| `full` | The complete integration surface |

Enabling `full` is convenient for workspace evaluation. A downstream application should enable only the surfaces it uses, then record that feature set in its evidence.

## 5. The smallest useful end-to-end example

The following program models a bounded counter. Its pure decision accepts `10 + 3` under a maximum of `20`. The accepted value is translated into a preconditioned patch, sealed into one candidate bundle, committed, and replayed with the same replay identity.

The example uses `expect` only for fixed demo literals and construction steps. Boundary-facing application code should return typed errors and preserve rejection data. The demo’s domain names and bindings define a local example protocol. They are not compatible with a production ZenoDEX profile.

```rust
use zeno_fcis::{
    Accepted, CandidateBindings, CandidateBuilder, CanonicalPatch,
    CommitPlan, CommitStatus, Decision, DecisionKind, Domain, Field,
    Hash32, OutboxPlan, PatchOp, PathSegment, Rejected,
    RustCryptoSha256, ShellState, Value, ValuePath, commit,
    commitment, hash_value,
};

fn decide(
    current: u128,
    increment: u128,
    maximum: u128,
) -> Decision<u128, &'static str, &'static str> {
    if increment == 0 {
        return Decision::Reject(Rejected::new("zero_increment"));
    }

    let Some(next) = current.checked_add(increment) else {
        return Decision::Reject(Rejected::new("arithmetic_overflow"));
    };

    if next > maximum {
        return Decision::Reject(Rejected::new("above_limit"));
    }

    Decision::Accept(Accepted::new(next))
}

fn bind(name: &str, bytes: &[u8]) -> Hash32 {
    let domain = Domain::new(name, 1).expect("fixed ASCII domain");
    commitment::<RustCryptoSha256>(domain, bytes)
        .expect("bounded demo commitment")
}

fn main() {
    let current = 10_u128;
    let increment = 3_u128;
    let maximum = 20_u128;

    let next = match decide(current, increment, maximum) {
        Decision::Accept(accepted) => *accepted.candidate(),
        Decision::Reject(rejected) => {
            println!("rejected: {}", rejected.reason());
            return;
        }
        Decision::CommittedFailure(_) => {
            unreachable!("the counter has no committed-failure rule")
        }
    };

    // Stable field identifier 1 means "counter value" in this demo schema.
    let pre_state = Value::normalize_record(vec![
        Field::new(1, Value::U128(current)),
    ])
    .expect("canonical demo state");

    let state_domain =
        Domain::new("demo/counter-state", 1).expect("fixed domain");
    let value_domain =
        Domain::new("zeno-fcis/value", 1).expect("fixed domain");

    let shell =
        ShellState::new::<RustCryptoSha256>(pre_state.clone(), state_domain)
            .expect("valid initial state");

    let patch = CanonicalPatch::try_new(
        1,                    // demo state type identifier
        shell.root(),         // compare-and-swap precondition
        vec![PatchOp::Update {
            path: ValuePath::new(vec![PathSegment::Field(1)]),
            expected_old_hash: hash_value::<RustCryptoSha256>(
                value_domain,
                &Value::U128(current),
            )
            .expect("old value is encodable"),
            value: Value::U128(next),
        }],
    )
    .expect("non-overlapping, preconditioned patch");

    let bindings = CandidateBindings {
        profile_hash: bind("demo/profile", b"counter-v1"),
        command_hash: bind("demo/command", &increment.to_be_bytes()),
        context_hash: bind("demo/context", &maximum.to_be_bytes()),
        precedence_hash: bind(
            "demo/precedence",
            b"arithmetic_overflow:10,above_limit:20,zero_increment:30",
        ),
        algorithm_hash: bind(
            "demo/algorithm",
            b"bounded-counter-transition-v1",
        ),
        budget_hash: bind("demo/budget", b"reads:1,writes:1"),
    };

    let bundle = CandidateBuilder::seal::<RustCryptoSha256>(
        &pre_state,
        state_domain,
        DecisionKind::Accept,
        None,                 // Accept carries no failure reason
        bindings,
        patch,
        CommitPlan::empty(),
        OutboxPlan::empty(),
    )
    .expect("candidate components agree");

    let replay_id = bind("demo/replay", b"request-0001");
    let first = commit::<RustCryptoSha256>(
        &shell,
        state_domain,
        replay_id,
        &bundle,
    )
    .expect("first commit");
    assert_eq!(first.status(), CommitStatus::Committed);

    let second = commit::<RustCryptoSha256>(
        first.state(),
        state_domain,
        replay_id,
        &bundle,
    )
    .expect("exact replay");
    assert_eq!(second.status(), CommitStatus::IdempotentReplay);
    assert_eq!(first.state(), second.state());

    println!("candidate: {}", bundle.candidate_id());
    println!("state: {:?}", second.state().state());
}
```

This example omits external effects. An accepted transition can also produce:

- a `CommitPlan` containing closed authoritative operations;
- an `OutboxPlan` containing delivery destinations and payloads as values.

The plans contain data, not executable closures. The shell interprets operation and channel identifiers through a reviewed registry.

## 6. What each line of the pipeline establishes

### The decision

`Decision` has exactly three cases:

```text
Accept(candidate)
Reject(reason)
CommittedFailure(candidate, reason)
```

`Reject` means unchanged authoritative state and no candidate. A timeout or failed withdrawal may sometimes require an intentional state update, such as recording terminal failure. That case belongs under `CommittedFailure` when the profile explicitly defines it.

The complete library-facing form is the [`Transition`](https://github.com/TheDarkLightX/ZenoFCIS/blob/main/crates/zeno-fcis-core/src/lib.rs) trait:

```rust
fn step(
    state: &State,
    command: &Command,
    context: &Context,
    budget: &mut Budget,
) -> Decision<Candidate, Reject, Failure>;
```

Domain implementations should use typed `StableReason` values with fixed codes and precedence ordinals. Source branch order is too fragile to serve as protocol policy.

### The budget

ZenoFCIS budgets logical work such as reads, writes, candidate evaluations, bytes, witness bytes, and depth. Wall-clock time is excluded because replaying the same input on different machines may take different durations.

The compact example records a declared demo budget binding. A production transition should charge an actual `Budget`, then bind both `BudgetLimits` and `BudgetUsed` through one canonical schema.

### The value and codec

`Value` is a closed algebra of integers, booleans, bytes, ASCII text, tuples, records, sums, vectors, and canonical maps. Records use stable numeric field identifiers. ZCVE/1 gives one accepted byte representation for one admitted value.

Canonical bytes matter because a content hash is meaningful only when equivalent values cannot be serialized in several ways. Schema validation adds domain meaning on top of the generic value shape.

### The patch

`CanonicalPatch` binds:

- the state type;
- the expected pre-state root;
- a canonical set of non-overlapping paths;
- an expected old-value hash for each update or deletion;
- the successor value for each insertion or update.

Patch application is pure and all-or-nothing. A stale root, stale old value, missing path, overlapping path, or type mismatch fails before a successor is produced.

### The candidate bundle

`CandidateBuilder::seal` applies the patch and commits the decision kind, optional committed-failure reason, profile, command, context, reason precedence, algorithm, budget, pre-root, post-root, patch, commit plan, and outbox plan.

The result carries one `CandidateId`. The supported API prevents a receipt from candidate A from being combined with the patch or plan from candidate B.

### The shell

The pure `ShellState` models the semantics expected from a concrete database shell:

1. compare the current root with the candidate’s pre-root;
2. validate the complete bundle again;
3. bind the replay identity to the candidate;
4. publish state, receipt, bundle, replay record, and outbox records together;
5. return the same state for an exact replay;
6. reject a replay identity reused for different content.

The optional SQLite shell is a concrete interpreter with crash-point tests. Its guarantees remain conditional on SQLite, operating-system, storage, and deployment assumptions listed in [SQLite Shell Refinement](https://github.com/TheDarkLightX/ZenoFCIS/blob/main/docs/SQLITE_SHELL_REFINEMENT.md).

## 7. Turning the counter into a real profile

A production-oriented integration requires more work than replacing the counter formula.

1. **Define admitted types.** Give every state field, command variant, reason, effect, and channel a stable identifier. Bound lengths, nesting, integers, and collections.
2. **Separate admission from transition.** Parsing, authentication, signature checking, freshness capture, and policy selection happen before `Transition::step`. Their checked results enter as immutable context.
3. **State the invariants.** Conservation, authorization, uniqueness, arithmetic bounds, reason precedence, and terminal-state rules need explicit tests or proofs.
4. **Charge deterministic work.** Every bounded loop, candidate search, emitted byte sequence, and proof object needs a logical resource policy.
5. **Derive one patch and closed plans.** The shell must not recalculate fees, balances, authorization, or next state.
6. **Bind exact identities.** Profile, schema, codec, command, context, policy, evidence, algorithm, precedence, and budget identities belong in the candidate.
7. **Seal before effects.** Rejection produces no authoritative plan. Accepted and committed-failure candidates are sealed and independently validated before publication.
8. **Commit atomically.** Compare the expected root, publish the complete bundle and outbox, then deliver idempotently.
9. **Retain counterexamples.** Stale roots, wrong old-value hashes, replay collisions, malformed canonical bytes, mismatched runtime outputs, crash points, and acknowledgement mismatches should remain regression fixtures.
10. **Gate promotion.** Tests, proofs, mounted-runtime refinement, evidence envelopes, and security review establish only their declared claims.

This sequence preserves the boundary from the previous tutorial: the model or generator may propose data; a deterministic checker decides whether the data is admissible; the shell exercises authority only over the accepted, exactly bound plan.

## 8. Current integration surfaces

The optional packages are useful once the basic transition-to-bundle path is understood:

- [Mounted ZenoDEX adapter](https://github.com/TheDarkLightX/ZenoFCIS/blob/main/docs/MOUNTED_ZENODEX_ADAPTER.md) compares complete normalized decisions from an external runtime. Matching only an accept bit or state root is insufficient.
- [Authenticated-state adapter](https://github.com/TheDarkLightX/ZenoFCIS/blob/main/docs/AUTHENTICATED_STATE_ADAPTER.md) plans versioned sparse-tree updates and checks membership and absence proofs. The current implementation is a reference backend.
- [Deterministic synthesis](https://github.com/TheDarkLightX/ZenoFCIS/blob/main/docs/DETERMINISTIC_SYNTHESIS.md) searches a bounded canonical candidate domain. Truncated search returns an honest incomplete result.
- [Evidence importers](https://github.com/TheDarkLightX/ZenoFCIS/blob/main/docs/EVIDENCE_IMPORTERS.md) bind tool identity, source, assumptions, retained artifacts, and coverage mode. An envelope does not make a false specification true.
- [Persistent collections](https://github.com/TheDarkLightX/ZenoFCIS/blob/main/docs/PERSISTENT_COLLECTIONS.md) keep logical equality and canonical bytes independent of allocation history and backend structure.

These surfaces extend assurance around the same central object: an immutable, content-addressed candidate whose exact meaning is independently checkable.

## 9. Failure modes to test first

A small integration should begin with adversarial cases:

| Test | Required behavior |
| --- | --- |
| Command exceeds policy maximum | Stable `Reject`, unchanged state, no candidate |
| Addition overflows `u128` | Stable arithmetic rejection |
| Patch uses a stale pre-root | Patch or shell rejects |
| Patch expects the wrong old value | Patch rejects before successor construction |
| Two patch paths overlap | Patch construction rejects |
| Same replay ID and same bundle | Idempotent replay |
| Same replay ID and different bundle | Replay conflict |
| Receipt or plan comes from another candidate | Bundle validation rejects |
| Outbox acknowledgement binds the wrong entry hash | Acknowledgement rejects |
| External runtime omits or changes one normalized field | Refinement report records a mismatch |

These tests stress the assumptions that carry authority. Happy-path output alone provides weak evidence for an FCIS boundary.

## 10. What ZenoFCIS does and does not buy

ZenoFCIS supplies a disciplined language for expressing high-assurance transitions:

- explicit immutable inputs;
- deterministic decisions and budgets;
- canonical values and commitments;
- pure, preconditioned updates;
- closed effect descriptions;
- exact replay and atomic publication semantics;
- fail-closed comparison and evidence boundaries.

Correct use still depends on the domain specification, admission logic, commitment profile, hash provider, database, operating system, external delivery mechanism, deployment policy, and human review. A machine-checked transition can faithfully implement an incomplete economic model. A crash-tested SQLite shell can still be deployed with unsuitable durability settings. A mounted adapter can compare two implementations that share the same mistaken rule.

The practical purpose of ZenoFCIS is to make those assumptions visible and bind evidence to exact artifacts. It provides the structure needed to ask precise questions:

```text
Which state was read?
Which command and policy were authenticated?
Which rule selected this outcome?
Which exact patch and effects were authorized?
Which versions and budgets were bound?
Which candidate was committed?
Which evidence applies to this exact artifact?
Which claims remain open?
```

That is the conceptual FCIS boundary made operational.

## Further reading

- [ZenoFCIS README](https://github.com/TheDarkLightX/ZenoFCIS/blob/main/README.md)
- [Candidate and commit boundary](https://github.com/TheDarkLightX/ZenoFCIS/blob/main/docs/CANDIDATE_COMMIT_BOUNDARY.md)
- [Composition and ZenoDEX refinement](https://github.com/TheDarkLightX/ZenoFCIS/blob/main/docs/COMPOSITION_REFINEMENT_ZENODEX.md)
- [Release assurance](https://github.com/TheDarkLightX/ZenoFCIS/blob/main/docs/RELEASE_ASSURANCE.md)
- [Tutorial 64: Functional Core, Imperative Shell](../functional-core-imperative-shell-values-as-boundaries/)
