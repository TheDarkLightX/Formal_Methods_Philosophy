# Synthetic Deontic Knowledge Base v0 Audit

Status: **NO-GO for promotion**.

The v0 corpus is deterministic, finite, and internally reproducible. The
current release claim is still too strong. The independent oracle accepts
resealed records outside the declared seven-axis language, the temporal model
cannot distinguish timely from late performance, and most nominal axis changes
do not change a role-normalized decision trace.

This is a falsification result for the promotion gate, not evidence that the
checked corpus shards are corrupt.

## Frozen audit subject

The audit used these exact file digests:

| Artifact | SHA-256 |
| --- | --- |
| Template bank | `33098cfb0e81596e95b2630b3d10374a508b0fa13a6675ac5a973d34573a0d04` |
| Generator | `927566493ac5f88c4cb7c8b067a680fee5347640250a061be357cd806fb7be35` |
| Oracle | `62e6d564bfc5e4c1ab7e9073afc139fdc188c91e27fbbbc29596a20a7950b9f0` |
| Tests | `e880391bd4f8c50abf8f2fe610eb942c3f270b6ef11454f74975baf391fec737` |
| Manifest | `57bb82e2fc78e6a2597075a97ee17ba55b5b2e485ff0b0fb569f6b787051d267` |
| Verification report | `9188abafba12021ca92cc6dd78fd52a64f35ac3ea48debb037dbf96ae4671e52` |
| Replay report | `9bab5d91c2a40fa37850181389e18157ab40450a940598172f21dea69b34f5b5` |

The audit observed concurrent changes before this freeze. Results from an
earlier oracle revision are not mixed into this decision.

## Evidence that passed

The following statements are supported for the frozen artifacts:

- The independent Python scan accepted all 65,536 current records with zero
  reported errors.
- The corpus contains 65,536 unique ordinals, stable IDs, and semantic-core
  signatures.
- The corpus root is
  `708a66e9585754bdfb71da172d166e498a230876e6e61ca0946eb285837d7fe1`.
- The semantic-set root is
  `8c6cb124b06ca37dc2dc8964e4a5187898880948fede34002c4034a3dbb69912`.
- All seven focused unit tests passed.
- A clean temporary rebuild produced a byte-identical manifest and all 16
  byte-identical gzip shards. A fresh oracle scan of that rebuild passed.
- The stored verification report is canonical JSON and equals a fresh oracle
  result for the frozen source.
- The current template and generator source digests equal the values written in
  the current manifest.
- The oracle does not import the generator module or call its evaluator.
- The authority flags on the current records are synthetic and
  non-authoritative.

These results justify the narrower statement: every current generator-produced
record replayed under the frozen Python oracle. They do not justify the
oracle's stated `closed schema` scope.

## Promotion blockers

### 1. Resealed records outside the declared IR are accepted

The hostile records below recompute the semantic signature, stable ID,
candidate result, negative projection, and record hash after mutation. They are
therefore not simple stale-hash tests. The frozen oracle accepts each one.

| Accepted path or relation | Hostile value |
| --- | --- |
| `semantic_core.world.facts[fact_premise].args` | an unbound actor ID |
| `semantic_core.world.facts[fact_premise].evidence_id` | an unregistered evidence ID |
| `semantic_core.world.facts[fact_exception].predicate` | an arbitrary predicate |
| `semantic_core.world.facts[fact_exception].args` | an unrelated action or actor |
| `semantic_core.world.facts[fact_exception].evidence_id` | an unregistered evidence ID |
| `semantic_core.world.facts[fact_exception].extra` | an unknown nested field |
| `semantic_core.world.facts[fact_primary_performed].predicate` | an arbitrary predicate |
| `semantic_core.world.facts[fact_primary_performed].args` | an unrelated action |
| `semantic_core.world.facts[fact_primary_performed].evidence_id` | an unregistered evidence ID |
| `semantic_core.world.facts[fact_primary_performed].extra` | an unknown nested field |
| `semantic_core.norms[*].subject_id` | a different existing actor that does not own the action |
| `semantic_core.norms[norm_n0].exception` | `{"kind":"forged"}`, an extra field, or an undeclared `unless` clause |
| `semantic_core.norms[norm_n2].exception` | `{"kind":"forged"}` or an undeclared `unless` clause |
| `semantic_core.norms[*].revision.extra` | an unknown nested field |

The premise fact receives an exact top-level field check, but its argument and
evidence bindings are not checked. The other two facts do not receive an exact
nested-shape check. Norm subjects are checked only for membership in the actor
set. Exceptions on `norm_n0` and `norm_n2` are not restricted to their declared
forms. Revision objects permit extra fields.

The current test named `test_semantic_mutation_invalidates_signature` mutates a
record without resealing it. It proves hash binding, but it does not test
whether the semantic admission boundary rejects a hostile producer that can
recompute an unsigned hash.

The following command reproduces representative acceptances without writing a
corpus artifact:

```bash
python3 -B - <<'PY'
import copy
import hashlib
import json
from pathlib import Path

from examples.layered_q_tables.synthetic_deontic_kb import (
    generate_record,
    load_template_bank,
    rank_coordinate,
)
import examples.layered_q_tables.synthetic_deontic_oracle as oracle

bank = load_template_bank(
    Path("examples/layered_q_tables/synthetic_deontic_templates.json")
)

def canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")

def fact(record, fact_id):
    return next(
        row for row in record["semantic_core"]["world"]["facts"]
        if row["id"] == fact_id
    )

def norm(record, norm_id):
    return next(
        row for row in record["semantic_core"]["norms"]
        if row["id"] == norm_id
    )

def reseal(record):
    signature = hashlib.sha256(canonical(record["semantic_core"])).hexdigest()
    record["semantic_signature_sha256"] = signature
    record["stable_id"] = "sdk1-" + signature
    result = oracle.oracle_result(record["semantic_core"])
    record["generator_candidate_result"] = result
    record["negative_knowledge"] = oracle._expected_negative(record, result)
    without_hash = dict(record)
    without_hash.pop("record_sha256", None)
    record["record_sha256"] = hashlib.sha256(canonical(without_hash)).hexdigest()
    return record

base = generate_record(bank, 0)
graph7 = generate_record(bank, rank_coordinate((0, 7, 0, 0, 0, 0, 0)))

mutants = {}

value = copy.deepcopy(base)
fact(value, "fact_premise")["args"] = ["unbound_actor"]
mutants["premise_args_unbound"] = value

value = copy.deepcopy(base)
fact(value, "fact_exception")["predicate"] = "forged_predicate"
mutants["exception_predicate_forged"] = value

value = copy.deepcopy(base)
fact(value, "fact_primary_performed")["extra"] = "forged"
mutants["performed_extra_field"] = value

value = copy.deepcopy(base)
norm(value, "norm_n0")["subject_id"] = "resource_owner"
mutants["subject_not_action_owner"] = value

value = copy.deepcopy(base)
norm(value, "norm_n0")["exception"] = {"kind": "forged"}
mutants["n0_unknown_exception_kind"] = value

value = copy.deepcopy(graph7)
norm(value, "norm_n2")["exception"] = {
    "kind": "unless", "fact_id": "fact_exception"
}
mutants["n2_undeclared_exception"] = value

value = copy.deepcopy(base)
norm(value, "norm_n0")["revision"]["extra"] = "forged"
mutants["revision_extra_field"] = value

for name, value in mutants.items():
    try:
        oracle.validate_record(reseal(value))
    except Exception as error:
        print(name, "REJECT", type(error).__name__, str(error))
    else:
        print(name, "ACCEPT")
PY
```

Expected output for the frozen oracle is `ACCEPT` for all seven named mutants.

### 2. Source hashes are recorded but not enforced

The manifest loader verifies that every digest is a 64-character hexadecimal
value. It does not recompute the template-bank or generator-source digest.
Replacing either declared digest with 64 zeroes in a canonical temporary
manifest still produces a full-corpus `PASS`. Replacing the generator-profile
digest does fail because each record is compared with that manifest field.

This is a checker gap, not a current mismatch. The current source files happen
to match the current manifest. A future source edit could make the release
receipt stale without changing the oracle verdict.

The following command reproduces both accepted source-hash mutations. It uses a
temporary manifest and does not alter the corpus:

```bash
python3 -B - <<'PY'
import copy
import json
import tempfile
from pathlib import Path

import examples.layered_q_tables.synthetic_deontic_oracle as oracle

corpus = Path("assets/data/glassmind_synthetic_deontic_65536")
source = Path("assets/data/glassmind_synthetic_deontic_65536.manifest.json")
manifest = json.loads(source.read_text(encoding="ascii"))

with tempfile.TemporaryDirectory(prefix="sdk-v0-source-hash-") as directory:
    for field in ("template_bank_sha256", "generator_source_sha256"):
        mutant = copy.deepcopy(manifest)
        mutant["hashes"][field] = "0" * 64
        path = Path(directory) / (field + ".json")
        path.write_bytes(oracle._cjson(mutant))
        result = oracle.verify_corpus(corpus, path)
        print(field, "PASS" if result["passed"] else "FAIL")
PY
```

Expected output for both fields is `PASS`.

### 3. Deadline evidence cannot distinguish timely and late performance

The `after_deadline_performed` state records `now_tick = 3`,
`deadline_tick = 2`, and `performance = performed`. It has no performance
timestamp and no fact stating that performance occurred by the deadline. The
evaluator nevertheless classifies the obligation as satisfied.

The exact v0 witness is ordinal `6304`, coordinate
`(0, 6, 0, 5, 0, 0, 0)`. It reports
`deadline_obligation_satisfied`, no violation, and no activated repair.

This result is valid only under the unstated premise that `performed` means
`performed by the deadline`. V1 must encode that premise as data or distinguish
`performed_at_tick` from the observation time.

### 4. The CTD result exposes the wrong action relationship

Ordinal `6272`, coordinate `(0, 6, 0, 4, 0, 0, 0)`, represents an unperformed
primary obligation after its deadline. V0 returns both the late primary action
and the contrary-to-duty repair as required, then escalates with
`multiple_exclusive_obligations`.

A repair obligation is not automatically an exclusive alternative to the
violated primary action. V1 needs a separate repair phase or typed repair
disposition. The primary violation should remain in the trace without forcing
the expired primary action into the executable action set. An unresolved result
must not expose required or permitted executable actions.

### 5. Declared counterfactuals are not executed negative knowledge

Each v0 record repeats four generic statements such as
`condition_or_quarantine_may_change`. The generator function receives the axis
coordinate but does not use it to construct an observed counterfactual. The
oracle checks that the same declarations are present. It does not execute the
mutation, bind a target record, or compare before and after results.

The reported `negative_knowledge_item_count` counts rejected actions and
unresolved reason codes. It does not count a verified counterfactual result.
The current counterfactual rows should therefore be described as experiment
proposals, not established negative knowledge.

## Measured behavioral quotient

Semantic-signature uniqueness measures distinct canonical inputs. It does not
measure distinct decision behavior.

For this audit, action IDs were mapped to their structural roles
`primary`, `safe`, `repair`, and `review`. Domain IDs, record IDs, hashes, and
ordinals were excluded. The full candidate result retained status, fallback,
required, forbidden, and permitted roles, active and defeated norms, satisfied
and violated norms, activated repairs, and reason codes.

The exact counts are:

| Quotient | Distinct values |
| --- | ---: |
| Canonical semantic-core signatures | 65,536 |
| Exact candidate-result JSON objects | 252 |
| Modal outcome tuples before role normalization | 138 |
| Role-normalized full decision traces | **49** |

The one-axis analysis fixes all other coordinates, gathers each axis fiber,
and asks whether at least two role-normalized traces differ. Pairwise influence
compares every unordered pair inside each fiber.

| Axis | Fibers | Active fibers | Inert fibers | Active-fiber rate | Changed unordered pairs |
| --- | ---: | ---: | ---: | ---: | ---: |
| Domain | 8,192 | 0 | 8,192 | 0.000000% | 0 / 229,376, 0.000000% |
| Norm graph | 8,192 | 8,192 | 0 | 100.000000% | 112,512 / 229,376, 49.051339% |
| Premise truth | 16,384 | 14,336 | 2,048 | 87.500000% | 86,016 / 98,304, 87.500000% |
| Time | 8,192 | 256 | 7,936 | 3.125000% | 6,400 / 229,376, 2.790179% |
| Priority | 16,384 | 288 | 16,096 | 1.757812% | 1,440 / 98,304, 1.464844% |
| Exception | 16,384 | 3,200 | 13,184 | 19.531250% | 16,000 / 98,304, 16.276042% |
| Revision | 32,768 | 32,768 | 0 | 100.000000% | 32,768 / 32,768, 100.000000% |

The domain axis is a typed renaming under this quotient. Time, priority, and
exception are inert in most contexts because the Cartesian product applies
them where the selected topology cannot consume them. V1 should use
topology-local variants and explicit application predicates rather than count
these inert combinations as knowledge growth.

## Outcome skew

The frozen corpus contains:

| Outcome | Records |
| --- | ---: |
| Resolved | 6,944 |
| Unresolved | 58,592 |
| Fallback `none` | 6,944 |
| Fallback `abstain` | 25,472 |
| Fallback `escalate` | 33,120 |
| Exact current-kernel projections | 1,152 |
| Unsupported current-kernel projections | 64,384 |

This distribution is not a population estimate. It primarily reflects the
inert Cartesian design and deliberate conflict or uncertainty injection.

## Tool and authority boundary

The verification report correctly marks raw-record Z3/CVC5, ESSO, Tau, Lean,
and HOL checks `SKIP`. No execution evidence was found for those lanes. The
kernel projection is metadata generated by the corpus pipeline. It is not a
kernel parity run.

The corpus does not establish law, ethics, factual truth, deontic completeness,
production readiness, or authority to perform an external effect.

## Minimal repair order

1. Define exact nested schemas for every fact, exception, revision, norm, and
   proof-trace object. Reject unknown and malformed-present fields.
2. Bind fact arguments and evidence references to typed registries. Require a
   norm subject to match the declared action owner or an explicit delegation.
3. Encode performance time or performance-by-deadline evidence. Separate CTD
   repair from the expired primary action set.
4. Retain every accepted v0 hostile record as a resealed regression mutant.
5. Recompute template and generator source hashes inside the release checker.
6. Replace generic counterfactual suggestions with executed, content-addressed
   effect or invariance receipts.
7. Measure causal influence and normalized behavior before assigning a v1
   promotion label.

The quantitative v1 requirements are defined in
[Synthetic Deontic Luna v1 Release Gates](synthetic_deontic_luna_v1_release_gates.md).
