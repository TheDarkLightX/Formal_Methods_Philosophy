---
title: "From Acceptance Tests to a Certified Design Choice"
layout: docs
kicker: Tutorial 69
description: "A reproducible tutorial on turning design requirements into a finite grammar, searching it canonically with ZenoFCIS, preserving rejected candidates, and coordinating ATDD, Research Kernel, ESSO, Lean, and runtime evidence."
---

# From Acceptance Tests to a Certified Design Choice

Imagine a safe with seven dials. Each dial controls one engineering decision:
the data representation, validation strategy, Python closure checks, Rust
construction surface, canonical identity rule, runtime scope, and delivery
evidence. The dials admit 648 settings.

A reviewer has also supplied a card of non-negotiable behaviors. A setting is
acceptable only when every behavior on the card holds. Trying settings by hand
would produce a persuasive story and a weak audit trail. The experiment in this
tutorial turns the dials in one canonical order, checks every setting with one
deterministic verifier, retains each rejection, and stops at the first accepted
design.

The observed result was:

```text
candidate space:          648
candidates evaluated:     576
rejected points retained: 575
selected profile:         (2, 1, 2, 2, 1, 1, 1)
```

The selected profile means:

```text
immutable named records
standalone pure validation at every point of use
Python transitive-alias analysis plus full-import runtime probes
exact Rust derive/implementation closure plus fallible encoding
exact equality between stored fields and canonical fields
carrier-only, unmounted scope
exact-head packet and delivery evidence
```

This is a worked example of **bounded design synthesis**. It establishes a
design-selection result under a fixed grammar and checker. It does not establish
that the grammar contains every good design, that the checker expresses every
real requirement, or that the selected design is mounted as production
authority.

## 1. The engineering problem

The immediate problem came from a security-sensitive carrier layer. The layer
held untrusted values that would eventually cross Python and Rust boundaries.
Reviewers repeatedly found ways that a locally reasonable construction could
escape its intended contract:

- a sibling Python module could replace a carrier method after class creation;
- a transitive alias could hide the class being mutated;
- a Rust `Default` derive could manufacture an unchecked value;
- an encoder could serialize a value without revalidating it;
- a hidden stored field could be omitted from canonical bytes;
- a carrier-only checkpoint could accidentally acquire a runtime consumer;
- a merge build could pass while the exact pull-request head or delivery packet
  remained unchecked.

Each review suggested another repair. The useful next move was to turn those
repairs into a finite design language.

```text
review findings
    ↓
behavioral obligations
    ↓
closed design holes
    ↓
canonical candidate assignments
    ↓
deterministic checker
    ↓
selected design + rejected frontier + replay certificate
```

The search did not invent the obligations. Human review, counterexamples, and
the architecture contract supplied them. Search answered a narrower question:

> Which candidate is first in the declared canonical order that satisfies all
> declared obligations?

Requirements own meaning. Search explores the declared space. The checker
decides acceptance.

## 2. The instruments and their authority

Five instruments participate in the broader loop. They have different jobs.

| Instrument | Job | What it may establish |
| --- | --- | --- |
| ATDD | Bind readable scenarios to fixed executable commands | The declared acceptance workflow ran and retained its expected bindings |
| ZenoFCIS synthesis | Enumerate a bounded candidate grammar canonically and call an external checker | The selected assignment is the first accepted assignment under the fixed problem |
| Research Kernel | Preserve questions, claims, dependencies, risks, evidence, refutations, promotions, and open frontier work | A scoped claim passed the local evidence-promotion gate |
| ESSO | Propose or evolve candidate designs when direct enumeration is too large | Candidate quality or search priority under its stated objective |
| Lean and Aristotle | State and check mathematical laws; Aristotle may propose proof terms and Lean checks them | The exact theorem compiled by the Lean kernel under its assumptions |

Runtime authority requires another layer:

```text
selected design
  + implementation refinement
  + exact source binding
  + authenticated current state
  + atomic publication
  + recovery and no-bypass evidence
```

No search certificate, ATDD run, Research Kernel status, ESSO score, or isolated
Lean theorem supplies those runtime facts on its own.

## 3. Turn the design into seven finite holes

The search grammar used seven stable hole identifiers. Each hole had a closed,
nonempty domain.

| Hole | `0` | `1` | `2` | Acceptance rule |
| --- | --- | --- | --- | --- |
| Representation | Mutable mapping | Positional tuple | Immutable named record | `representation = 2` |
| Validation | Constructor only | Standalone point-of-use validator | Constructor plus point-of-use validator | `validation ≥ 1` |
| Python closure | Values module only | Direct whole-closure scan | Transitive aliases plus runtime probe | `python_closure = 2` |
| Rust closure | Private fields only | Exact derive and impl surface | Exact surface plus fallible encoding | `rust_closure = 2` |
| Canonical identity | Sampled fixtures | Exact stored/projection field closure | — | `canonical_identity = 1` |
| Checkpoint scope | Authority-bearing or mounted | Carrier-only and unmounted | — | `checkpoint_scope = 1` |
| Delivery evidence | Merge-head evidence | Exact-head packet plus delivery verification | — | `exact_head_evidence = 1` |

Choice `1` for validation requires a standalone pure validator at every
authority-relevant use. A constructor may delegate to the same helper. The
constructor is never trusted as the only validation boundary. Choice `2` adds
constructor invocation as an explicit requirement, while leaving the same
point-of-use authority check in place.

Let an assignment be

```text
a = (r, v, p, u, c, s, e).
```

The checker accepts exactly when

```text
Accept(a)
  ⇔ r = 2
   ∧ v ≥ 1
   ∧ p = 2
   ∧ u = 2
   ∧ c = 1
   ∧ s = 1
   ∧ e = 1.
```

This formula is the compact semantic center of the experiment.

## 4. Count the candidate space

The first four holes have three values. The final three have two:

```text
|Designs|
  = 3 × 3 × 3 × 3 × 2 × 2 × 2
  = 648.
```

ZenoFCIS orders candidate values by canonical encoded bytes. For these small
`U128` domains, that yields the declared ascending order. The selected
assignment was

```text
(2, 1, 2, 2, 1, 1, 1).
```

Its zero-based mixed-radix index is:

```text
((((((2 × 3 + 1) × 3 + 2) × 3 + 2) × 2 + 1) × 2 + 1) × 2 + 1)
  = 575.
```

The search therefore encountered it on evaluation:

```text
575 + 1 = 576.
```

Every earlier candidate failed at least one obligation. This explains both
reported counts:

```text
evaluated = 576
rejected before selection = 575.
```

The remaining 72 candidates were not evaluated because the contract asked for
the first canonical solution. “Rejected frontier” here means the retained
rejected prefix of this bounded search. It is not a claim about a Pareto
frontier.

## 5. Encode the acceptance checker

The checker reads all seven choices and refuses to guess when an assignment is
missing or has the wrong type. Its decisive part is small:

```rust
let obligations = [
    (representation == 2, 1_u128),
    (validation >= 1, 2),
    (python_closure == 2, 3),
    (rust_closure == 2, 4),
    (canonical_identity == 1, 5),
    (checkpoint_scope == 1, 6),
    (exact_head_evidence == 1, 7),
];

if let Some((_, failed_obligation)) =
    obligations.iter().find(|(holds, _)| !holds)
{
    return CheckResult::Rejected {
        counterexample: Value::U128(*failed_obligation),
    };
}

CheckResult::Accepted {
    compiled: Value::tuple(vec![
        Value::U128(representation),
        Value::U128(validation),
        Value::U128(python_closure),
        Value::U128(rust_closure),
        Value::U128(canonical_identity),
        Value::U128(checkpoint_scope),
        Value::U128(exact_head_evidence),
    ]),
    reference_claim: hash(81),
    composition_claim: hash(82),
}
```

Three outcomes matter:

```text
Accepted      candidate satisfies every declared obligation
Rejected      candidate fails, with a normalized counterexample
Indeterminate checker cannot establish either result
```

An indeterminate result blocks certification. Search does not silently skip it.
This prevents tool failure from being interpreted as evidence against a
candidate.

The minimized experiment used the first failed obligation number as its
counterexample. A production checker should carry enough structured evidence to
replay the exact failure, such as a mutated source fixture, failing invariant,
or refinement mismatch.

## 6. Bind and run the synthesis problem

The complete problem includes the candidate grammar, exact search bound, and
hash bindings for the schema, contract, grammar, algorithm, and checker:

```rust
let problem = SynthesisProblem::try_new(
    SynthesisBindings {
        schema_hash: hash(1),
        contract_hash: hash(2),
        grammar_hash: hash(3),
        algorithm_hash: hash(4),
    },
    holes,
    SearchBudget {
        max_assignments: 648,
    },
)?;

let result = search(&problem, &mut B1B1AtddChecker)?;
```

The run returned:

```text
cardinality=648
problem_hash=1e5a45900e0bca6c7ea9ef0b7d829d2d936a3ca44ba6d25c20b92dd8c0650d26
hole_1=U128(2)
hole_2=U128(1)
hole_3=U128(2)
hole_4=U128(2)
hole_5=U128(1)
hole_6=U128(1)
hole_7=U128(1)
evaluated=576
counterexamples=575
trace_hash=f1ccfd27e9bcbf35c879555e93452bfb0ae899b23379cda12b3230b83340398c
certificate_hash=b7305e96ab812e1e84c8f3f7703bd1bf61c5da0ff596fd205d4fe1d983588157
```

The three hashes identify different layers:

| Hash | Meaning |
| --- | --- |
| Problem hash | The bounded synthesis problem and its declared bindings |
| Trace hash | The canonical sequence of checked assignments and results |
| Certificate hash | The complete selected-result certificate |

The experiment source artifacts were also hashed:

| Artifact | SHA-256 |
| --- | --- |
| `Cargo.toml` | `de5aa62498171fdf7566dedf4df0def327211bbf8dd9dfb0e3be671b1e5171c4` |
| `Cargo.lock` | `00e1764b410e632d34772b7e96983d3c2faf944bf32b5de26a4b675831f1d7cd` |
| `SEARCH_CONTRACT.md` | `f7c7a3d676c930b3cc23a83152ea1e0b7a64a90716d08f221980051b3e0f6e6c` |
| `src/main.rs` | `bb40305c01f2aa7427b4d08fb9f8b9b69ffa78530f696e317a27d8afc45055dd` |

The synthesis kernel source used by the run matched ZenoFCIS commit
[`37faa195`](https://github.com/TheDarkLightX/ZenoFCIS/commit/37faa195a05b7f843d559878ec472d15a6d9de57)
byte for byte. Its `src/lib.rs` SHA-256 was
`125629bfd3b6fc43e9fba3170cc90a5d734f3ba02e724eb8391ec5713cafe70a`.

The example’s `hash(1)`, `hash(2)`, and similar calls are visible stand-ins made
from repeated bytes. They do not hash the actual schema or checker source. A
release-grade experiment must replace every stand-in with the canonical hash of
the real artifact it names. The source hashes above improve reproducibility of
this tutorial; they do not retroactively strengthen the demonstration
certificate’s bindings.

## 7. Use ATDD to define observable success

Acceptance-test-driven development begins before the search. Each important
behavior becomes a stable scenario with a fixed executable command.

The design contract used five core scenarios:

```text
Constructor bypass
  Given a constructor is bypassed or patched
  When admission or encoding consumes the value
  Then standalone point-of-use validation rejects it.

Sibling mutation
  Given a permitted module aliases, replaces, or mutates a carrier
  When the complete closure is imported and audited
  Then the exact mutation is rejected.

Rust construction surface
  Given a carrier gains Default, Deserialize, From, or a builder macro
  When the structural checker runs
  Then the attribute or implementation mismatch is rejected.

Canonical identity
  Given two admitted values have equal canonical bytes
  When complete stored fields are compared
  Then the values are equal.

Unmounted scope
  Given the carrier checkpoint
  When reachability and changed paths are checked
  Then no verifier, transition, receipt, bundle, publication path,
  or value-moving consumer exists.
```

ZenoFCIS’s ATDD registry maps stable scenario identifiers to fixed argument
arrays. Feature prose is explanatory input and never becomes a shell command.
The local snapshot used in this experiment reported:

```text
python3 tools/atdd.py self-test
atdd: self-test PASS (8 hostile or inert-prose mutations checked)

python3 tools/atdd.py check
atdd: registry PASS (21 scenarios)
```

Those counts describe the checked local RC3 snapshot. They are not a release
claim for a different revision.

ATDD and synthesis close different relations:

```text
ATDD:
  scenario ID → fixed commands → observed pass or fail

bounded synthesis:
  finite assignment → deterministic checker → accept, reject, or indeterminate
```

The scenarios tell the checker author what observable behavior matters. The
synthesis kernel explores candidate designs under the resulting predicate.

## 8. Preserve the loop in Research Kernel

A terminal transcript is easy to lose. Research Kernel turns the experiment
into a durable graph of public, reviewable claims and evidence.

The run used this stable identifier:

```text
formal-philosophy-zenofcis-atdd-bounded-design-search-v1
```

Its workflow followed eight tactics.

### Tactic 1: state a research contract

The run declared the exact question, finite-search scope, a 12-atom budget,
success criteria, authority nonclaims, and expected experiment hashes.

### Tactic 2: seed typed atoms

The graph received:

```text
QUESTION  Which canonical candidate is first to satisfy every obligation?
CLAIM     Profile (2,1,2,2,1,1,1) is first, at evaluation 576.
CLAIM     The result depends on the exact grammar, order, and checker.
RISK      A wrong grammar or checker can certify a wrong design.
```

The selected-profile claim depends on the search contract and the explicit
false-positive risk. Scope information remains connected to the claim.

### Tactic 3: retrieve prior failures and contradictions

Retrieval searched local atoms, graph neighbors, failures, contradictions, and
frontier work before evidence promotion. A wording change alone is not a reason
to create a duplicate claim.

### Tactic 4: morph the problem into testable views

Research Kernel generated three candidate reformulations:

```text
invariant extraction
counterexample-surface extraction
workflow compression
```

They remained speculative until separately tested. Reformulation can reveal a
better question; it does not establish the answer.

### Tactic 5: register a refutation plan

The plan attempted to find a lower passing candidate, replay divergence, a
changed trace or certificate hash, a selected field violating an obligation,
or a weakened-checker negative control that admitted an unsafe profile.

No actual counterexample was claimed without a replayed witness.

### Tactic 6: attach source-pinned evidence

The exact command, output, artifact hashes, and replay metadata were attached to
the claim. The final experiment evidence artifact has hash:

```text
sha256:a7894fb2a7bd9192c02b184b99eb2db972e6dce151954fd7d8757fa9aff83f99
```

### Tactic 7: promote fail closed

Early promotion attempts were rejected. The gate required a recognized support
evidence class and an explicit contradiction-search acknowledgment in addition
to provenance, dependencies, refutation, replay, and rationale.

After the replay was attached as an `experiment` and contradiction search was
recorded, promotion succeeded:

```text
claim:     claim-selected-profile
status:    SUPPORTED
promotion: promotion_155e27999b824039
missing:   []
```

The ledger refused to infer support from an unfamiliar evidence label or from
an unstated search step. `SUPPORTED` means that the local Research Kernel gate
passed for this scoped claim. It is not a mathematical proof, protocol
authorization, publication approval, or production-readiness status.

### Tactic 8: report the open frontier

The final report retained the supported claim, replay result,
checker-completeness risk, refutation plan, unproved reformulations, and
explicit nonclaims. Success and unfinished work remain in one graph.

## 9. Treat rejected candidates as a negative corpus

The 575 rejected assignments are more than a counter. Each one records:

```text
(candidate assignment, failed obligation, checker identity, problem identity)
```

This corpus supports several tactics:

1. Cluster candidates by failed obligation.
2. Minimize representative assignments into source-level witnesses.
3. Convert Python alias mutation, Rust `Default`, hidden fields, infallible
   encoding, mounted consumers, and merge-head substitution into permanent
   mutants.
4. Rerun the corpus after checker changes and explain every changed verdict.
5. Train ESSO or another proposer from negative examples while the exact
   checker retains acceptance authority.

The negative corpus is bounded by the declared grammar. It says nothing about
bad designs that the grammar cannot express.

## 10. Add ESSO when the space becomes too large

Direct enumeration is attractive when the Cartesian product fits the stated
budget. ZenoFCIS’s initial synthesis kernel admits at most 1,000,000 complete
assignments. ESSO can help when the search space becomes larger:

```text
1. propose candidate values for a hole
2. evolve a compact grammar from accepted and rejected points
3. rank which bounded subspace should receive exact checking next
```

The safe loop is:

```text
P_t = ESSO(evidence_t, objective, resource_budget)
A_t = normalize_and_bound(P_t)
R_t = exact_checker(A_t)
evidence_(t+1) = evidence_t ∪ {(A_t, R_t, witness_t)}
```

An ESSO fitness score remains advisory. If ESSO selects a subset of a larger
space, the certificate covers that subset. Omitted candidates remain a
nonclaim. Every promoted candidate still passes the exact checker, and any
change to the grammar or objective creates a new synthesis problem identity.

Research Kernel records the proposal, selection rationale, exact verifier
result, and rejected frontier. ZenoFCIS provides deterministic replay for the
bounded subproblem.

## 11. Use Lean and Aristotle for universal laws

The Boolean acceptance predicate is easy to inspect. Valuable Lean work begins
with laws that quantify over all admitted values or executions:

```text
ExactFieldClosure:
  stored_fields(x) = schema_fields

CanonicalInjectivity:
  encode(x) = encode(y) → x = y

PointOfUseSafety:
  encode(x) = Ok(bytes) → validate_fields(x) = Ok

RejectIsNoOp:
  validate_fields(x) = Reject(r) → no authority artifact is produced

SearchDeterminism:
  same problem + same checker semantics → same result and trace
```

Aristotle may search for Lean proof terms or fill proof gaps. The Lean kernel
checks the resulting theorem. Its statement must include every assumption that
the runtime later needs to produce.

The next bridge is refinement:

```text
RuntimeEncode(x) = bytes
  → LeanModelEncode(abstract(x)) = bytes
```

Without this bridge, a theorem about the model and a test of the implementation
remain separate facts. The theorem does not establish that production code
calls the proved function, receives authenticated inputs, or publishes the
result atomically.

## 12. The complete refinement loop

The combined loop can be written compactly:

```text
Q_t
  ──Research Kernel──► scoped question, assumptions, risks, prior failures
  ──ATDD─────────────► executable behavior contract A_t
  ──grammar design───► finite problem G_t and exact verifier V_t
  ──ESSO, optional───► proposed bounded subspace P_t
  ──ZenoFCIS─────────► selected a_t, rejected frontier F_t, certificate C_t
  ──Lean/Aristotle───► checked laws Φ(a_t) under explicit assumptions
  ──runtime tests────► implementation/refinement evidence E_t
  ──exact delivery───► source and artifact identity D_t
  ──Research Kernel──► promote, refute, narrow, or return to Q_(t+1)
```

A scoped design may be promoted when:

```text
DesignSupported(a)
  ⇔ ATDDPasses(a)
   ∧ SearchSelectsFirst(G, V, a)
   ∧ RefutationAttempted(a)
   ∧ ContradictionSearchRecorded(a)
   ∧ EvidenceHasProvenance(a)
   ∧ SourceIdentityMatches(a).
```

Production adoption needs stronger conjuncts:

```text
MayMount(a)
  ⇒ DesignSupported(a)
   ∧ RequiredLeanClaimsCompile(a)
   ∧ RuntimeRefinesModel(a)
   ∧ CurrentAuthorityIsAuthenticated(a)
   ∧ CommitIsAtomicAndRecoverable(a)
   ∧ NoAlternateAuthorityPath(a).
```

The second formula was outside this experiment.

## 13. Replay recipe

The synthesis source can be pinned in a small Rust crate:

```toml
[package]
name = "zenofcis-bounded-design-search"
version = "0.1.0"
edition = "2024"

[dependencies]
zeno-fcis-codec = { git = "https://github.com/TheDarkLightX/ZenoFCIS.git", rev = "37faa195a05b7f843d559878ec472d15a6d9de57" }
zeno-fcis-synthesis = { git = "https://github.com/TheDarkLightX/ZenoFCIS.git", rev = "37faa195a05b7f843d559878ec472d15a6d9de57" }
zeno-fcis-value = { git = "https://github.com/TheDarkLightX/ZenoFCIS.git", rev = "37faa195a05b7f843d559878ec472d15a6d9de57" }
```

Implement the seven holes, checker, and search call shown above, then run:

```bash
cargo +1.97.1 run --locked --quiet
cargo +1.97.1 clippy --locked -- -D warnings
```

For the ZenoFCIS substrate:

```bash
python3 tools/atdd.py self-test
python3 tools/atdd.py check
cargo +1.97.1 test -p zeno-fcis-synthesis --locked
```

The synthesis tests used by the experiment checked four failure boundaries:

```text
truncated budget is incomplete, never no-solution
indeterminate checker blocks certification
declaration order does not change the certificate
complete no-solution retains every counterexample
```

The run reported four passing synthesis tests.

## 14. Mutation tactics for the next iteration

A search contract should attack its own assumptions. High-value mutations for
this example are:

```text
delete one acceptance obligation
change one hole domain without changing the grammar hash
truncate the budget below 648
make the checker return Indeterminate at candidate 575
reorder hole declarations or candidate insertion history
replace exact-head evidence with merge-head evidence
add a Python transitive alias mutation
replace Python __post_init__ from a sibling module
derive Rust Default or Deserialize
delete fallible encoder revalidation
add an unencoded stored field
add a runtime consumer to the unmounted carrier checkpoint
```

Each mutation should produce a stable typed rejection, change the problem or
certificate identity, fail ATDD, fail a Lean theorem, or fail exact-head
delivery verification. An inert prose mutation should leave the certificate
unchanged.

## 15. What the result establishes

| Claim | Status |
| --- | --- |
| The declared space contains 648 candidates | Established by checked cardinality |
| The selected profile is first under the declared canonical order | Supported by deterministic replay |
| The search evaluated 576 candidates and retained 575 rejections | Supported by the trace and certificate |
| The selected profile satisfies the checker’s seven obligations | Established by the checker result |
| Replaying the same source and bindings yields the recorded identities | Supported for the checked experiment |
| The seven-hole grammar contains every relevant design | Not established |
| The acceptance predicate captures every security requirement | Not established |
| The placeholder hashes bind the actual source artifacts | False for this demonstration |
| The selected design is implemented exactly | Requires separate implementation evidence |
| The selected design is mounted as runtime authority | Explicitly excluded |
| The result authorizes M6 promotion | Explicitly excluded |

The durable lesson is methodological:

```text
make choices finite
make requirements executable
make order canonical
make rejection informative
make evidence content-addressed
make promotion fail closed
keep model, implementation, and authority claims separate
```

## Further reading

- [Functional Core, Imperative Shell: How Immutable Values Become Boundaries](../functional-core-imperative-shell-values-as-boundaries/)
- [ZenoFCIS deterministic synthesis](https://github.com/TheDarkLightX/ZenoFCIS/blob/main/docs/DETERMINISTIC_SYNTHESIS.md)
- [ZenoFCIS acceptance testing](https://github.com/TheDarkLightX/ZenoFCIS/blob/main/docs/ACCEPTANCE_TESTING.md)
- [ZenoFCIS repository](https://github.com/TheDarkLightX/ZenoFCIS)
