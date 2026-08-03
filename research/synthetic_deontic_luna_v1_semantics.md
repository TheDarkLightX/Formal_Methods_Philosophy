# Synthetic Deontic Luna v1 Semantics

Status: implementable design, not release evidence. The frozen input is the
`synthetic-deontic-luna-template-bank-v1` profile
`sdk-luna-v1-bounded-causal-four-valued`. Every case is synthetic and
non-authoritative.

## 1. Authority and determinism

The pure evaluator is:

```text
evaluate(profile, case_core) -> Reject(code) | DecisionResultV1
```

`Reject` means the bytes are not a member of the closed v1 language.
`DecisionResultV1(status="unresolved")` means the case is well formed but does
not determine an admissible substantive action. Neither result authorizes an
external effect.

Canonical bytes use ASCII JSON, sorted object keys, no insignificant
whitespace, no duplicate keys, no floats, and no non-finite values. IDs match
`[a-z][a-z0-9_]{0,63}`. Hashes are lowercase 64-character SHA-256 values. Lists
are sorted by ID unless the field is explicitly an ordered expression. Unknown
fields, missing fields, duplicate IDs, unresolved references, Boolean values in
integer fields, and noncanonical bytes are rejected.

## 2. Closed case IR

The outer object has exactly these fields:

```text
CaseV1 = {
  schema: "synthetic-deontic-luna-case-v1",
  ordinal: uint16,
  coordinate: Coordinate,
  profile_ref: ProfileRef,
  authority: Authority,
  semantic_core: Core,
  semantic_core_sha256: Hash,
  stable_id: "sdk-luna-v1-" + semantic_core_sha256,
  generator_claim: DecisionResultV1,
  nonclaims: [Nonclaim],
  record_sha256: Hash
}
```

`semantic_core_sha256` hashes canonical `semantic_core`. `record_sha256`
hashes the outer object without `record_sha256`. The independent oracle derives
the coordinate and result. It never trusts the declared coordinate or
`generator_claim`.

```text
Coordinate = {
  domain_code: 0..15, topology_code: 0..15,
  evidence_code: 0..3, state_code: 0..3,
  resolution_code: 0..3, defeater_code: 0..3,
  domain_id: Id, topology_id: Id, evidence_id: Id,
  state_id: Id, resolution_id: Id, defeater_id: Id
}

ordinal = (((((domain_code * 16 + topology_code) * 4 + evidence_code)
              * 4 + state_code) * 4 + resolution_code) * 4 + defeater_code)

ProfileRef = {
  profile_id: Id,
  semantics_spec_sha256: Hash,
  template_bank_sha256: Hash
}

Authority = {
  status: "synthetic_non_authoritative",
  source_kind: "generated_fixture",
  issuer_id: "none",
  truth_status: "not_asserted",
  may_authorize_external_effects: false,
  may_be_cited_as_law: false
}
```

`Core` has exactly these fields:

```text
Core = {
  domain_id: Id,
  actors: [Actor], actions: [Action], relations: [Relation],
  raw_state: [StateCell], facts: [Fact], evidence: [Evidence],
  norms: [Norm], conflicts: [Conflict],
  priority_edges: [PriorityEdge], query: Query
}

Actor = {id: Id, role: Id, kind: Id}
Action = {id: Id, role: "primary"|"safe"|"repair"|"review",
          actor_id: Id, kind: Id}
Relation = {id: Id, kind: Id, source_ref: TypedRef, target_ref: TypedRef}
TypedRef = {kind: "actor"|"action"|"fact"|"norm"|"state", id: Id}
StateCell = {id: Id, type_id: Id, value_id: Id}
Fact = {id: Id, slot: Id, truth: "T"|"F"|"U"|"B",
        evidence_ids: [Id], derivation_rule_id: Id,
        input_state_ids: [Id]}
Evidence = {id: Id, kind: "synthetic_observation",
            target_norm_ids: [Id], truth: "T"|"F"|"U"|"B",
            payload_sha256: Hash,
            authority_status: "synthetic_non_authoritative"}
Norm = {id: Id, operator: "O"|"F"|"P", source_actor_id: Id,
        subject_id: Id, action_id: Id, condition_refs: [ConditionRef], source_id: Id,
        lifecycle: Lifecycle, defeater: Defeater,
        repair_for: "none"|Id}
ConditionRef = {kind: "evidence"|"fact"|"state"|"violation", id: Id}
Lifecycle = {kind: "state", value: "active"|"inactive"|
             "satisfied"|"violated"|"unknown"}
          | {kind: "deadline", value: DeadlineState}
DeadlineState = "before_deadline_unperformed"|
                "deadline_reached_timely_performed"|
                "deadline_reached_late_performed"|
                "deadline_reached_performance_unknown"
Defeater = {kind: "unless", fact_id: Id}
Conflict = {id: Id, left_norm_id: Id, right_norm_id: Id, kind: Id}
PriorityEdge = {higher_norm_id: Id, lower_norm_id: Id}
Query = {mode: "single_action", alternative_action_ids: [Id],
         omission_admissible: false,
         fallback_action_id: Id}
```

Every action actor, norm source actor, norm subject, condition, evidence,
conflict, priority, and repair reference must resolve. `subject_id` must equal
the selected action's `actor_id`. This profile has no object that can delegate
that subject binding. The template field `source_actor_role` names
the norm's source or issuer role and compiles to `source_actor_id`; it is not the
deontic subject. Every fact and evidence object is exact and registry bound. A
repair norm has exactly one `repair_for` primary; the primary has
`repair_for="none"`. Repair edges are acyclic. The compiler must reproduce the
selected frozen domain and topology exactly, including nonempty
`application_targets`; arbitrary extra exceptions or facts are outside the
lattice. A non-repair norm has no `violation` condition. Every repair norm has
exactly one `violation` condition, and that condition names its `repair_for`
primary. The primary must have `repair_for="none"`. A repair family is the
nonempty set of norms that name the same primary. It contains at most one O
norm. That O norm, when present, is the family's repair provider; linked F and P
norms are constraints, not providers.

### Frozen-template compilation

Compilation is exact, not heuristic:

- `evidence:e0` becomes evidence ID `e0`, takes the selected global evidence
  truth, and targets exactly the sorted norm IDs in
  `application_targets.evidence`. Its payload hash is SHA-256 over canonical
  JSON `{ "evidence_id": "e0", "target_norm_ids": [...], "truth": code }`,
  using the ordinary canonical key ordering and compact separators.
- `domain:<slot>` resolves the unique domain predicate with that slot. Its fact
  ID is the predicate ID, its rule ID is the same predicate ID, its inputs are
  the expression's state fields, and its truth is recomputed from raw state.
- `state:<norm>` is a required integrity mirror. It must name the same norm
  that contains the reference and binds that norm to the selected lifecycle
  variant. It is checked structurally, but is not included in the guard
  conjunction. The lifecycle evaluator separately distinguishes active,
  inactive, satisfied, violated, and unknown dispositions.
- `violation:<norm>` compiles as the repair gate defined in Section 3. It is
  never folded into the ordinary guard conjunction.
- Defeater fact IDs are the topology slot IDs `d0`, `d1`, and `d2`. Selected
  `slot_truths` supply listed values; an unlisted declared slot is F. Their rule
  ID is `defeater_axis_v1` and their input-state list is empty.
- The template's `source_actor_role` compiles via
  `actor_role_bindings` to `source_actor_id`. `action_id` is the unique action
  with `role=action_role`, and `subject_id` is that action's `actor_id`. A typed
  relation role reference is resolved through the same registries.
- A norm bound to an ordinary lifecycle slot compiles its selected `norm_states`
  value to a state lifecycle. Only norms bound to a deadline-typed lifecycle
  slot compile state codes 0, 1, 2, and 3 respectively to the four
  `DeadlineState` values in declaration order. A topology may mix both slot
  kinds. In the frozen deadline topology, `deadline0` is deadline typed, while
  `deadline_review0` is ordinary; its P review norm therefore receives a state
  lifecycle and is not subject to the deadline-P rejection rule. The timely and
  late tags are explicit synthetic event-order assertions: timely asserts that
  performance occurred no later than the deadline, while late asserts that
  performance occurred after it. A bare `performed` observation or the current
  observation time cannot establish either assertion.
- The query alternatives are all four sorted domain action IDs. The review-role
  action is `fallback_action_id`.

## 3. Four-valued evaluation

Represent truth as `(positive, negative)`:

```text
T=(1,0)  F=(0,1)  U=(0,0)  B=(1,1)
not(a,b)=(b,a)
(a,b) and (c,d)=(a and c, b or d)
(a,b) or  (c,d)=(a or c, b and d)
```

This gives the complete tables:

| `and` | T | F | U | B |
|---|---|---|---|---|
| T | T | F | U | B |
| F | F | F | F | F |
| U | U | F | U | F |
| B | B | F | F | B |

| `or` | T | F | U | B |
|---|---|---|---|---|
| T | T | T | T | T |
| F | T | F | U | B |
| U | T | U | U | T |
| B | T | B | T | B |

`not(T)=F`, `not(F)=T`, `not(U)=U`, and `not(B)=B`. Domain expressions use
these operations. Equality to a concrete allowed value is T when equal and F
when unequal; a raw value `unknown` produces U and `both` produces B.

For a norm `n`, `ordinary_guard(n)` is the conjunction of its `evidence` and
`fact` conditions, with the empty conjunction equal to T. `state` is the
structural mirror described above. `violation` is a separate repair gate. Thus
neither `state` nor `violation` participates in `ordinary_guard`.

The closed norm disposition set is:

```text
NormDisposition = "inactive"|"active"|"satisfied"|"violated"|
                  "defeated"|"blocked_unknown"|"blocked_inconsistent"
```

For a non-repair norm, or a repair norm whose gate is T, evaluate in this exact
precedence order. An ordinary guard F gives `inactive`, U gives
`blocked_unknown` and `unknown_condition`, and B gives
`blocked_inconsistent` and `inconsistent_condition`. Only a T guard reaches the
defeater. A defeater T gives `defeated`, U gives `blocked_unknown` and
`unknown_defeater`, and B gives `blocked_inconsistent` and
`inconsistent_defeater`. Only defeater F reaches the lifecycle. This defines all
16 guard-defeater pairs without allowing U or B to authorize an action.

After a norm has been evaluated, its derived violation truth is total:

| Norm disposition | `violation:<norm>` |
|---|---|
| `violated` | T |
| `inactive`, `active`, `satisfied`, or `defeated` | F |
| `blocked_unknown` | U |
| `blocked_inconsistent` | B |

The repair gate uses the primary's stage-3 disposition. This equals the truth
derived after conflict resolution because a conflict can only change `active`
to `defeated`, and both map to F. Result fields use the frozen final
dispositions.

For a repair norm, this truth is checked before the ordinary guard. Gate F gives
the repair `inactive` with reason `primary_not_violated`. Gate U gives
`blocked_unknown` plus `unknown_primary_violation`; gate B gives
`blocked_inconsistent` plus `inconsistent_primary_violation`. Only gate T
evaluates the ordinary guard, defeater, and lifecycle. The evaluator may compute
the residual guard for the trace, but a residual F cannot mask a U or B repair
gate. This special precedence is what prevents an uncertain or inconsistent
primary from silently disabling its repair.

## 4. Ordered evaluator

The following order is normative:

```text
1 decode_exact_and_bind_profile(case)
2 recompute_domain_predicates_from_raw_state()
3 evaluate non-repair norms in sorted norm ID order
4 derive the four-valued violation truth of each primary
5 evaluate repair gates, then activated repairs, in sorted norm ID order
6 resolve active declared conflicts simultaneously
7 freeze final norm dispositions
8 derive each repair family's final availability
9 derive modal sets and single-action admissibility
10 build trace, result hash, and compare generator_claim
```

An applicable state lifecycle maps `inactive`, `active`, `satisfied`, and
`violated` to the identically named disposition. Its `unknown` value maps to
`blocked_unknown` and adds `unknown_lifecycle`. The deadline mapping is exact:

| `DeadlineState` | O disposition | F disposition | blocker |
|---|---|---|---|
| `before_deadline_unperformed` | `active` | `active` | none |
| `deadline_reached_timely_performed` | `satisfied` | `violated` | none |
| `deadline_reached_late_performed` | `violated` | `violated` | none |
| `deadline_reached_performance_unknown` | `blocked_unknown` | `blocked_unknown` | `unknown_deadline` |

Deadline P is rejected as `unsupported_deadline_operator`. Any other deadline
value is rejected as `invalid_deadline_state`; it is not converted into a
runtime blocker. The reached-unknown row therefore witnesses uncertainty with
a known reached deadline, rather than an unknown clock.

When a primary's violation truth is T, every linked repair norm is included in
`activated_repair_norm_ids`, and its separate gate permits ordinary evaluation.
The violated primary remains in `violated_norm_ids` and is never reactivated.
The primary and repair are not exclusive merely because they are linked. Only
an explicit active `Conflict` creates a conflict.

For each active conflict `(l,r)`, compute reachability in the complete priority
graph. If only `l` reaches `r`, defeat `r`; if only `r` reaches `l`, defeat
`l`; if neither reaches the other, add `unresolved_priority`; if both reach
each other, add `relevant_priority_cycle`. A priority cycle is blocking only
when both endpoints of an active declared conflict are mutually reachable.
Dormant cycles do not change a decision. Losers from all conflicts are removed
simultaneously, so conflict iteration order cannot change the result.

Repair availability is computed after those simultaneous losses. A family
exists exactly when one or more norms link to a primary through `repair_for`.
No prose-level topology flag is consulted. Let `v` be the primary's violation
truth and let `p` be the family's unique O provider, if one exists. The following
table is the complete rule:

| `v` | final provider disposition | family availability | added family blocker |
|---|---|---|---|
| F | any or absent | `not_triggered` | none |
| U | any or absent | `blocked_unknown` | `unknown_primary_violation`, `unknown_repair_availability` |
| B | any or absent | `blocked_inconsistent` | `inconsistent_primary_violation`, `inconsistent_repair_availability` |
| T | provider absent | `absent` | `repair_unavailable` |
| T | `active` | `active` | none |
| T | `satisfied` | `satisfied` | none |
| T | `violated` | `violated` | `repair_unavailable` |
| T | `defeated` | `defeated` | `repair_unavailable` |
| T | `inactive` | `inactive` | `repair_unavailable` |
| T | `blocked_unknown` | `blocked_unknown` | `unknown_repair_availability` |
| T | `blocked_inconsistent` | `blocked_inconsistent` | `inconsistent_repair_availability` |

The provider's own condition, defeater, lifecycle, and conflict blockers remain
in `blocker_codes`; the last column adds the family-level conclusion. A blocked
provider is epistemically unresolved, not falsely labeled confirmed
unavailable. Linked F and P constraints are evaluated normally and may produce
their own blocker or modal conflict, but they never count as a provider. A
primary with no linked norms has no repair family, no `RepairStep`, and no
repair-availability blocker.

After resolution, O produces required actions, P produces explicitly permitted
actions, O implies permission, and F produces forbidden actions. A surviving
required or permitted action that is also forbidden adds `modal_conflict`.
More than one distinct required action adds `single_action_cardinality_conflict`;
it is not called exclusivity. With no blocker, one required action is the sole
admissible action. With no required action, each explicitly permitted and
non-forbidden action is admissible.

Any blocker makes `status="unresolved"`, `fallback="escalate"`, and all
`executable_required_action_ids`, `executable_permitted_action_ids`, and
`admissible_action_ids` empty. Consequently every alternative is rejected. If
there is no blocker but no positive norm, status is unresolved, fallback is
`abstain`, and the same empty-action rule applies. Otherwise status is
resolved and fallback is `none`.

## 5. Result and proof trace

`DecisionResultV1` has exactly:

```text
{schema, status, fallback, blocker_codes,
 active_norm_ids, defeated_norm_ids, satisfied_norm_ids,
 violated_norm_ids, activated_repair_norm_ids,
 norm_violation_truths, repair_availability,
 diagnostic_required_action_ids, diagnostic_permitted_action_ids,
 diagnostic_forbidden_action_ids,
 executable_required_action_ids, executable_permitted_action_ids,
 admissible_action_ids, rejected_action_ids,
 proof_trace, proof_trace_sha256, result_sha256}
```

`schema` is `synthetic-deontic-luna-result-v1`; `status` is `resolved` or
`unresolved`; `fallback` is `none`, `abstain`, or `escalate`. The closed blocker
set is `unknown_condition`, `inconsistent_condition`, `unknown_defeater`,
`inconsistent_defeater`, `unknown_lifecycle`, `unknown_deadline`,
`unknown_primary_violation`, `inconsistent_primary_violation`,
`unknown_repair_availability`, `inconsistent_repair_availability`,
`repair_unavailable`, `unresolved_priority`, `relevant_priority_cycle`,
`modal_conflict`, and
`single_action_cardinality_conflict`.

`norm_violation_truths` contains one `NormViolationTruth` per norm, sorted by
norm ID. `repair_availability` contains one `RepairAvailability` per declared
repair family, sorted by primary norm ID. They are semantic result fields, not
optional diagnostics:

```text
NormViolationTruth = {norm_id: Id, truth: "T"|"F"|"U"|"B"}
RepairAvailability = {
  primary_norm_id: Id,
  primary_violation_truth: "T"|"F"|"U"|"B",
  linked_norm_ids: [Id],
  provider_norm_id: "none"|Id,
  provider_disposition: "none"|NormDisposition,
  availability: "not_triggered"|"absent"|"active"|"satisfied"|
                "violated"|"defeated"|"inactive"|
                "blocked_unknown"|"blocked_inconsistent"
}
```

The proof trace shapes are exact:

```text
ProofTrace = {predicate_steps: [PredicateStep], norm_steps: [NormStep],
 repair_steps: [RepairStep], conflict_steps: [ConflictStep],
 admissibility_steps: [AdmissibilityStep]}
PredicateStep = {fact_id, rule_id, input_state_ids, input_values, truth}
NormStep = {norm_id, repair_gate_truth, ordinary_guard_truth, defeater_truth,
 lifecycle_value, pre_conflict_disposition, final_disposition, reason_codes}
RepairStep = {primary_norm_id, primary_violation_truth, linked_norm_ids,
 provider_norm_id, provider_disposition, availability, reason_codes}
ConflictStep = {conflict_id, left_active, right_active,
 left_reaches_right, right_reaches_left, disposition, defeated_norm_id}
AdmissibilityStep = {action_id, required, permitted, forbidden,
 admitted, reason_codes}
```

For a non-repair NormStep, `repair_gate_truth` is `none`; for a repair it is one
of T, F, U, or B. `ordinary_guard_truth` and `defeater_truth` are always
recorded even when gate or guard precedence makes them non-operative. A
conflict loser changes only `final_disposition` to `defeated` and appends
`priority_defeated`. A RepairStep is the corresponding RepairAvailability plus
the single reason `repair_` followed by its availability value. IDs and reasons
in each step are sorted. `defeated_norm_id` is `none` when no norm loses.
`proof_trace_sha256` hashes the canonical trace.
`result_sha256` hashes the result without `result_sha256`. The trace is an
executable derivation record, not a machine proof.

## 6. Executed counterfactual and invariance receipts

Vague expectations such as `may_change` are forbidden. For every unordered
pair that differs in exactly one of evidence, state, resolution, or defeater,
the checker emits:

```text
CounterfactualReceiptV1 = {
  schema, receipt_id, changed_axis,
  before: {ordinal, stable_id, record_sha256, result_sha256},
  after:  {ordinal, stable_id, record_sha256, result_sha256},
  unchanged_coordinate_fields, changed_semantic_paths,
  allowed_dependency_closure, normalized_before_sha256,
  normalized_after_sha256, classification: "EFFECT"|"INVARIANT",
  semantics_spec_sha256, template_bank_sha256,
  oracle_source_sha256, evaluator_source_sha256,
  receipt_sha256
}
```

The lower ordinal is `before`. `receipt_id` is the receipt hash with both hash
fields omitted; `receipt_sha256` hashes the object without itself. The checker
rebuilds both cases, verifies that only the named coordinate changed, checks
that semantic changes remain inside the topology's declared dependency
closure, executes the independent oracle, and recomputes both results.
Normalization is the following closed object:

```text
NormalizedDispositionV1 = {
  schema: "synthetic-deontic-luna-normalized-disposition-v1",
  status, fallback, blocker_codes,
  norms: [NormalizedNorm],
  activated_repair_norm_roles: [NormRole],
  conflicts: [NormalizedConflict],
  repair_families: [NormalizedRepairFamily],
  actions: [NormalizedAction]
}
NormalizedNorm = {
  role: NormRole, operator, source_actor_role, action_role,
  repair_for_role: "none"|NormRole,
  repair_gate_truth: "none"|"T"|"F"|"U"|"B",
  evaluated_lifecycle_category: "none"|Id,
  pre_conflict_disposition: NormDisposition,
  final_disposition: NormDisposition,
  violation_truth: "T"|"F"|"U"|"B"
}
NormalizedConflict = {
  left_role: NormRole, right_role: NormRole,
  operational_disposition: "dormant"|"left_wins"|"right_wins"|
                           "unresolved"|"cycle",
  defeated_role: "none"|NormRole
}
NormalizedRepairFamily = {
  primary_role: NormRole,
  primary_violation_truth: "T"|"F"|"U"|"B",
  linked_roles: [NormRole], provider_role: "none"|NormRole,
  provider_disposition: "none"|NormDisposition,
  availability: "not_triggered"|"absent"|"active"|"satisfied"|
                "violated"|"defeated"|"inactive"|
                "blocked_unknown"|"blocked_inconsistent"
}
NormalizedAction = {
  role: "primary"|"safe"|"repair"|"review",
  diagnostic_required, diagnostic_permitted, diagnostic_forbidden,
  executable_required, executable_permitted, admissible, rejected
}
NormRole = uint8
```

`evaluated_lifecycle_category` is `none` unless evaluation reaches the
lifecycle. An ordinary reached lifecycle records `state:<value>`; a deadline
lifecycle records `deadline:<DeadlineState>`. A conflict is `dormant` unless
both endpoints were active immediately before conflict resolution. Dormant
priority reachability and a defeater value hidden by an earlier gate are not
behavior and do not enter this object.

Action and source-actor IDs map to their declared structural role strings.
Norm IDs are alpha-normalized: enumerate every permutation of the finite norm
set, replace every norm reference by its candidate integer role, sort norm,
conflict, repair-family, and activated-repair rows by those roles, encode the
complete object as compact canonical ASCII JSON, and select the
lexicographically least byte string. Action rows use the fixed order primary,
safe, repair, review. Blocker codes are sorted. The selected canonical bytes
are hashed for the receipt.

Raw predicate steps, ordinary-guard truth, raw defeater truth, evidence and
fact IDs, source IDs, dormant reachability, reason strings, record IDs, hashes,
and proof-step ordering metadata are excluded. Their operational consequences
remain through blockers, dispositions, repair fields, and action fields.
EFFECT requires unequal normalized hashes; INVARIANT requires equal hashes.

The complete 65,536-case lattice has 393,216 such unordered one-axis receipts:
four axes times 16,384 fixed contexts times six pairs. Release also requires at
least three EFFECT edges forming a four-variant spanning tree for each of 16
domains, 16 topologies, and four axes, for at least 3,072 causal witnesses.
Receipt counts and a sorted receipt-set root are recomputed from raw receipts.

## 7. Provenance, parity, and nonclaims

The release manifest binds the template bank, this specification, generator,
independent oracle, evaluator, corpus root, semantic-set root, and receipt-set
root by hash. A record profile hash must equal the manifest and the verifier's
explicit expected hash. Merely being structurally projectable never establishes
kernel parity. Only an executed parity receipt binding compiler hash, kernel
revision, input packet hash, normalized oracle result hash, normalized kernel
result hash, and zero mismatch paths may use `executed_parity_pass`.

Explicit nonclaims: this profile is not law, ethics, external authority, world
truth, population evidence, a complete deontic logic, general intelligence, a
production policy, or permission to execute an action. Bounded exhaustive
checking establishes only the frozen finite model. Matching implementations
can still share a mistaken specification.
