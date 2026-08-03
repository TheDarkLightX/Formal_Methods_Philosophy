# Synthetic Deontic Problem Bank v1

Status: **`QUARANTINED_CORPUS`**.

This artifact is a finite synthetic semantic problem bank for testing
obligation, prohibition, permission, uncertainty, conflict, deadlines, and
repair. It is not a promoted knowledge base, law, ethics, factual knowledge,
population data, a complete deontic logic, or authority to perform an external
action.

The word *knowledge* applies narrowly here. An independently executed
counterfactual can establish that one bounded input change did or did not
change one bounded result. It cannot establish that a synthetic norm is true
or correct in the world.

## What was built

The v1 generator expands one closed product:

```text
16 typed domains
  x 16 deontic topology programs
  x 4 evidence values
  x 4 topology-local state variants
  x 4 topology-local resolution variants
  x 4 topology-local defeater variants
  = 65,536 records
```

Each canonical record contains typed semantic IR, an explicit synthetic
authority boundary, a candidate decision, a proof trace, stable identifiers,
and content hashes. The four evidence values are supported, refuted, unknown,
and inconsistent. State variants are local to their topology, so a deadline
program does not reuse an unrelated atemporal state merely to fill a grid.

The 16 domains include resource allocation, safety, privacy, governance,
evidence publication, integrity, coordination, workflow, access,
delegation, leases, incident repair, retention, settlement, proof acceptance,
and release promotion. They are synthetic micro-worlds, not observations about
real institutions or people.

The authority flow is:

```text
frozen template + finite semantics
                |
candidate generator
                |
raw canonical records
                |
separate oracle reconstruction
                |
checked effect or invariant classifications
                |
fail-closed promotion reducer
```

The generator cannot assign a release label. The oracle reconstructs the
coordinate and semantic result from raw canonical bytes, then recomputes the
proof trace, hashes, normalized disposition, and counterfactual class. The
release reducer still refuses promotion when required evidence packages are
missing.

## What v0 taught the design

The v0 integrity run was reproducible, but its semantic promotion claim failed.
The failure is retained rather than overwritten.

| v0 negative knowledge | Exact finding | v1 response | Remaining limit |
| --- | --- | --- | --- |
| Admission boundary | Re-sealed hostile nested fields, wrong owners, exceptions, and revisions were accepted. | Closed nested schemas, typed references, and reconstruction from the frozen coordinate. | The complete schema-derived G04 mutation receipt remains `SKIP`. |
| Source binding | Declared template and generator hashes were not recomputed. | Frozen byte digests and explicit command bindings. | Complete G00 and G11 coverage receipts remain `SKIP`. |
| Deadline semantics | V0 ordinal `6304` could not distinguish timely from late performance. | Four explicit deadline states include timely, late, and reached-deadline unknown performance. | The durable G05 law-and-breaker package remains `SKIP`. |
| Contrary-to-duty repair | V0 ordinal `6272` exposed an expired primary action and its repair as exclusive executable obligations. | Repair has a separate four-valued gate, and unresolved cases expose no executable action. | This remains one finite semantics profile, not a complete deontic logic. |
| Negative knowledge | Generic `may_change` statements did not execute a target case. | Every checked pair is classified as `EFFECT` or `INVARIANT` from rebuilt endpoints. | The complete receipt bodies were not retained, so G07 and G10 remain `SKIP`. |
| Behavioral diversity | 65,536 distinct inputs collapsed to 49 role-normalized behaviors, and several axes were mostly inert. | Topology-local axes and explicit causal application targets produce 322 normalized dispositions. | A larger quotient is not proof of novelty or real-world usefulness. |

The detailed v0 counterexamples are in
[`synthetic_deontic_kb_luna_audit_v0.md`](synthetic_deontic_kb_luna_audit_v0.md).

## Exact measured result

The durable raw-corpus report accepted every record and reproduced the earlier
development analyzer result.

| Measurement | Exact result | Scope |
| --- | ---: | --- |
| Accepted raw records | 65,536 | Complete finite corpus |
| Rejected raw records | 0 | This generated corpus, not a hostile mutation set |
| Unique stable IDs | 65,536 | Identity check |
| Unique record hashes | 65,536 | Integrity check |
| Normalized dispositions | 322 | Bounded behavioral quotient, not semantic novelty |
| Domain mutation effects | 32 | Two declared single-field families per domain |
| Distinct domain fingerprints | 16 | Alpha-normalized synthetic dependency structures |
| Distinct topology fingerprints | 16 program and 16 behavior fingerprints | Bounded structural diversity |
| Minimum topology distance | 256 of 256 common variation cells | Measured inside this profile |
| One-axis pairs classified | 393,216 | All unordered pairs in every fixed context |
| Pair effects | 177,600 | 45.166016% of pairs |
| Pair invariants | 215,616 | 54.833984% of pairs |
| Declared spanning-effect witnesses | 3,072 of 3,072 | One declared spanning tree per domain-topology-axis block |
| Resolved outcomes | 8,480 | 12.939453% of records |
| Unresolved with abstention | 18,576 | 28.344727% of records |
| Unresolved with escalation | 38,480 | 58.715820% of records |
| Largest normalized class in a 256-record block | 80 | Below the gate ceiling of 192 |

Axis effects expose where context masks a modifier:

| Axis | `EFFECT` | `INVARIANT` |
| --- | ---: | ---: |
| Evidence | 91,136 | 7,168 |
| State | 67,840 | 30,464 |
| Resolution | 1,536 | 96,768 |
| Defeater | 17,088 | 81,216 |

The resolution axis is therefore highly context-dependent in this design. Its
large invariant count is useful negative knowledge about masking. It is not a
defect by itself because all 3,072 declared spanning applications produced an
effect.

The 16 gzip shards contain 20,852,762 compressed bytes and 500,934,455
uncompressed JSONL bytes. These are packaging measurements, not measurements
of knowledge or intelligence. The largest shard is 1,339,822 bytes, below
GitHub's 100 MB per-file limit.

## Negative knowledge found during v1 review

### Generator and oracle disagreed at ordinal 12,336

At coordinate `(3,0,0,3,0,0)`, the first generator revision emitted an extra
`lifecycle_blocked_unknown` reason. The separate oracle emitted only
`unknown_lifecycle`, as required by the frozen semantics. The generator was
corrected, the case was retained as a regression, and the final raw scan
accepted all 65,536 complete candidate results.

This is evidence for the frozen finite differential. It is not proof that the
shared semantics specification is universally correct.

### A forged verified endpoint could affect a receipt

Peer review found that an earlier counterfactual path trusted fields on a
caller-supplied `VerifiedCase`. It could therefore classify a receipt using a
forged normalized hash. The repaired public path rebuilds and reconciles both
endpoints. The full analyzer rebuilds every supplied case once, seals the
canonical set, and uses only that set in the pair loop. Altered fields reject
with `verified_case_tamper`.

Adversarial tests also reject field changes outside the exact axis dependency
closure. No v1 corpus was promoted before these defects were found.

### Exhaustive checking still has performance debt

An exact in-memory `analyze_verified_cases` development benchmark over 65,536
canonical cases and all 393,216 pairs took 915.148 seconds, approximately
15.2525 minutes, on one machine. That duration is machine-specific. It is not
a semantic measurement or a release receipt.

A separate peer execution at the same frozen hashes rebuilt the cases in
334.460 seconds and ran the analyzer in 560.845 seconds, for 895.305 seconds
total. It reproduced every aggregate count and the receipt-set root. This is a
useful rerun of the same implementation, not the independent call-graph and
mutation evidence required for G11.

The implementation already removed 786,432 repeated endpoint rebuilds. The
next safe optimization target is block-local semantic-core, diff, and hash
reuse. Weakening endpoint reconciliation would make the checker faster by
weakening the claim, so it is not an acceptable optimization.

The append-only import outbox is
[`synthetic_deontic_luna_v1_negative_knowledge.jsonl`](synthetic_deontic_luna_v1_negative_knowledge.jsonl),
SHA-256
`1b15477a0177a737d974b4115cd6d36f1236181308a90b78d75a8c67d2701ec0`.
It is a project-local handoff artifact, not a PopperPad or Research Kernel
receipt.

## Why the corpus remains quarantined

The raw analyzer executes useful prechecks, but it does not manufacture missing
release evidence. Its exact gate reduction is:

| Gates | Status | Meaning |
| --- | --- | --- |
| G00-G07 | `SKIP` | The raw checks ran where applicable, but the required frozen-subject, mutation, law-witness, and durable receipt packages are incomplete. |
| G08 | `PASS` | The normalized behavior and topology-diversity thresholds executed and passed. |
| G09 | `PASS` | All 256 domain-topology blocks passed the outcome and dominant-class thresholds. |
| G10-G13 | `SKIP` | Receipt retention, independent-call-graph evidence, full replay binding, and authority-mutation packages are incomplete. |
| G14 | `PASS` | The report contains an explicit honest tool-status table. This does not mean those tools passed. |
| G15 | `FAIL` | Mandatory `SKIP` results veto promotion. |
| Reducer label | **`QUARANTINED_CORPUS`** | No bounded-verified release label is assigned. |

The report marks the decision kernel, Z3, CVC5, ESSO, Tau, Lean, HOL, Research
Kernel, PopperPad, LEAP, Morph, and ZAG as `SKIP` for this exact profile. Julia
and ZenoFCIS also have no execution receipt in this run, so no result from
either is claimed. An unrelated successful tool run cannot be inherited by
this corpus.

Research Kernel methods and the PopperPad executable were not available in the
active checkout. Their absence is recorded as a gap, not converted into
support.

## Frozen evidence

| Artifact | SHA-256 |
| --- | --- |
| Template bank | `eadfeeb5a464f89a878800d21e84acd2ce8f3844a75cc49234bccde95b16c3c9` |
| Finite semantics | `d265a71141d3b5f0291a971c2997d085efe53c91851359f181b0682d7fd6f371` |
| Release gates | `4dd3d794f501723eb2bcd06d09e1140418a1956edce2214c245d175bd1b72cb3` |
| Generator | `5500d3bef50e17a66cf9a081d0a1f9ef103c67b5c4de8feffbf740f84c9ef9bf` |
| Separate oracle implementation | `ae62aecbfe0f3a60c16c23e60f621981644ada5af6192ded59bd173a55fe44a0` |
| Generator tests | `a079a9d9af0c83d39913ce33c9fd97193070b814e092f44546bf079fd81011ed` |
| Oracle tests | `3a0d59b032353cad190dec07c6c0493cac4dede9e0809961b5c63b9d5b835322` |
| Adversarial tests | `6551f8951b41bb2124feb1e8702520753b1f9d11269f9d7bd225f6698d9e63e9` |
| Candidate manifest | `62968f1afad2b65fccb951032b5cc1396b8de3f3410205cf8347c757080e0565` |
| Corpus root | `8d6e01eb644b1a4a89760918862db41a4fffd3bff09afb57d76d3ad6d8bb6c58` |
| Semantic-set root | `8f482f34dde85cea6d5943847450a5e3a4a101d2858332c93719c385eb3b222d` |
| Counterfactual receipt-set root | `9ccf9ae8d13c9b4fb12cee0503af4010a35ac73c75b3457c4fda528c21a0c2ab` |
| Report's internal canonical digest | `04f51f5102c5c35b0ccb80b4911ffc084ab5773030921c3b2fd516d6d4b87150` |
| Complete verification-report file | `38b6b3fd208e89c6cba7d4c3911f74326325e628b513d3fef217d75b5590460a` |

The report's internal digest covers the canonical report object before its
self-digest field is added. The file digest covers the complete stored JSON
bytes, including that field.

A local replay comparison produced the same manifest and all 16 shards
byte-for-byte. This is useful reproducibility evidence, but G12 remains `SKIP`
because the comparison was not retained as a complete pinned two-build replay
receipt with a second full oracle report.

## Reproduce the candidate

Validate the frozen inputs:

```bash
python3 -m examples.layered_q_tables.synthetic_deontic_luna_v1 \
  validate-template \
  --template-bank examples/layered_q_tables/synthetic_deontic_luna_v1_templates.json \
  --semantics-spec research/synthetic_deontic_luna_v1_semantics.md
```

Build and analyze all records in one fresh ignored directory. The generator and
report writer are no-overwrite by design, so the published artifact paths are
not suitable reproduction targets:

```bash
mkdir -p artifacts/local
run_dir="$(mktemp -d artifacts/local/sdk-luna-v1.XXXXXX)"

python3 -m examples.layered_q_tables.synthetic_deontic_luna_v1 \
  build \
  --template-bank examples/layered_q_tables/synthetic_deontic_luna_v1_templates.json \
  --semantics-spec research/synthetic_deontic_luna_v1_semantics.md \
  --output-dir "$run_dir/corpus" \
  --manifest "$run_dir/manifest.json"

python3 -m examples.layered_q_tables.synthetic_deontic_luna_v1_oracle \
  --template examples/layered_q_tables/synthetic_deontic_luna_v1_templates.json \
  --semantics research/synthetic_deontic_luna_v1_semantics.md \
  --release-gates research/synthetic_deontic_luna_v1_release_gates.md \
  analyze "$run_dir/corpus" \
  --report "$run_dir/verify.json"
```

The analyzer deliberately writes the report only after the complete analysis
succeeds.

Run the focused checker tests:

```bash
PYTHONPATH=. pytest -q \
  examples/layered_q_tables/test_synthetic_deontic_luna_v1.py \
  examples/layered_q_tables/test_synthetic_deontic_luna_v1_oracle.py \
  examples/layered_q_tables/test_synthetic_deontic_luna_v1_release_adversarial.py
```

The current frozen files pass 44 focused tests. That test count is local
development evidence, not a release label.

## Residual nonclaims

The useful result is not that 65,536 records were generated. The useful result
is a bounded semantic test surface with retained counterexamples, explicit
invariance measurements, and a checker that can refuse promotion. The current
result does not establish law, ethics, world truth, population frequency,
general intelligence, semantic novelty, decision-kernel parity, formal proof,
or production readiness.
