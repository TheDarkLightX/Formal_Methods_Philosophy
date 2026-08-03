# Synthetic Deontic Luna v1 Content Design

Status: implemented candidate with a generated corpus and a complete raw-corpus
analysis. The fail-closed release label is **`QUARANTINED_CORPUS`**.

The machine-readable source is
`examples/layered_q_tables/synthetic_deontic_luna_v1_templates.json`.
It defines exactly 16 typed domains and 16 deontic topology programs. The
remaining four coordinates each have four values:

```text
16 domains
  x 16 topology programs
  x 4 evidence values
  x 4 topology-local state variants
  x 4 topology-local resolution variants
  x 4 topology-local defeater variants
  = 65,536 records
```

This document remains the content specification. The candidate generator,
separate oracle, and measured diversity report now exist. Promotion remains
blocked because several mandatory durable mutation, receipt-retention,
independence, replay, and authority packages have not been produced.

## Why v1 changes the lattice

The v0 corpus was deterministic and replayable, but several global axes were
usually behaviorally inert. A global time coordinate was attached even to
atemporal programs. A global priority coordinate was attached to programs
without a relevant conflict. Domain-specific actors and predicates were typed,
but the evaluator did not consume their domain relations when deciding an
action.

V1 removes those invalid combinations by giving every topology its own four
valid state labels. The refined deadline topology contains exactly:

1. before deadline and unperformed;
2. deadline reached with timely performance;
3. deadline reached with late performance; and
4. deadline reached with performance unknown.

The two deadline norms use that closed lifecycle. A third review permission
uses an ordinary lifecycle in the same topology. This mixed, typed support norm
is necessary for the local outcome floor and does not reinterpret a deadline
state as an atemporal state. Delegation, capability, lease, capacity,
transaction, proof, and contrary-to-duty programs likewise expose local states
that fit their own semantics.

Every topology also names a real conflict target for resolution and real norm
slots for defeaters. Equal rank, left-source priority, right-source priority,
and a priority cycle are therefore compiled against a declared conflict. The
cycle is a blocker when both conflicting norms are active. Defeaters can defeat
the left norm, defeat the right norm, be absent, or have unknown support.

## Causal DomainSpec contract

Each domain contains:

- typed actor and action registries with four stable action roles;
- a typed relation that explains the domain constraint;
- a closed raw-state schema;
- two derived four-valued predicates, `primary_gate` and `safe_gate`;
- four raw-state witnesses whose expected gate values are `T/T`, `T/F`,
  `F/T`, and `U/U`; and
- two named causal mutations with nonempty disposition targets.

The topology conditions consume `domain:primary_gate` and
`domain:safe_gate`. The fields are therefore part of the decision dependency
graph, not descriptive metadata. In the template bank,
`raw_state_fields` is the raw-state schema,
`derived_predicates[].consumed_by` records dependency edges, and
`causal_mutations` records the mutation families.

The W5 refinement gives all 16 domains alpha-distinct expression and mutation
graphs. It uses four primary-gate forms crossed with four safe-gate forms,
with one four-field delegation graph occupying its own family. The forms vary
actual operator trees and dependency sharing, not labels. Exhaustive witness
evaluation confirms `T/T`, `T/F`, `F/T`, and `U/U` in every domain. Each of the
32 retained mutations changes exactly one raw field and changes its declared
gate from T to F.

The domain fingerprint erases IDs, summaries, and literal spellings, enumerates
all raw-field renamings, and selects the lexicographically least canonical
form. It retains the raw-field count, complete expression operator trees,
predicate slots, mutation endpoints, changed-field incidence, and declared
truth deltas. Thus a renamed copy cannot create a new fingerprint.

The 16 domains are:

1. resource allocation;
2. safety hazard control;
3. privacy disclosure;
4. governance enactment;
5. evidence publication;
6. integrity commit;
7. coordination assignment;
8. workflow transition;
9. access authorization;
10. capability delegation;
11. concurrent lease commit;
12. incident repair;
13. data retention;
14. financial settlement;
15. proof acceptance; and
16. release promotion.

Their two gates depend on domain-specific raw state. Examples include capacity
and reservation state, hazard and guard state, purpose and disclosure basis,
quorum and timelock state, version and root state, capability scope and depth,
lease holder and epoch, nullifier freshness, proof binding, and artifact
binding. These are synthetic micro-worlds. They do not assert facts about a
real institution or person.

## TopologySpec contract

Each topology contains closed norm templates, an explicit conflict, exactly
four state variants, exactly four resolution variants, exactly four defeater
variants, and nonempty application targets for every modifier axis.

The 16 programs, described by their authoritative operator and action-role
shapes, are:

1. same-action dual obligation;
2. exclusive dual obligation;
3. primary permission versus primary obligation;
4. safe permission versus safe obligation;
5. emergency obligation versus baseline permission;
6. exceptional permission versus general permission;
7. superseding primary obligation and safe permission;
8. deadline obligation versus prohibition with ordinary review support;
9. contrary-to-duty repair versus repair prohibition;
10. delegated primary obligation versus principal repair obligation;
11. capability permission versus safe-action scope obligation;
12. publication obligation versus review permission;
13. lease commit conflict;
14. capacity allocation versus reserve preservation;
15. transaction commit versus stale-state prohibition; and
16. proof acceptance versus reverification guard.

Template IDs are opaque coordinate identifiers retained from the initial W4
bank. Some retain words such as `prohibition` even where W5 changed an operator.
The `norms[].operator` and `norms[].action_role` fields, not an identifier or
display string, are authoritative.

The topology fingerprint likewise minimizes over all norm-ID permutations. It
erases display strings but retains modalities, source and action roles,
condition-reference sorts and gate slots, lifecycle classes, repair edges,
conflict incidence, state dispositions, priority graphs, and defeater truth
assignments. This normalization produces 16 distinct program fingerprints.

The template-level `repair_for` field identifies a contrary-to-duty relation.
It is not evaluator authority. A runtime compiler must emit the exact CTD shape
defined by the operational-semantics specification and must activate a repair
only from a confirmed primary violation. Repair is not treated as an exclusive
alternative to the original action merely because both names occur in one
record.

`application_targets` is metadata for validation and counterfactual closure.
It must compile into changed semantic fields. It cannot directly decide a
result.

## Four-valued evidence and failure behavior

The evidence values are supported (`T`), refuted (`F`), unknown (`U`), and
inconsistent (`B`). Unknown or inconsistent safety-relevant inputs do not
authorize an action. A reached deadline with unknown performance does not
resolve. A relevant active priority cycle does not select either side.
Unresolved decisions admit no action and must carry an abstain or escalate
disposition under the operational-semantics specification.

The expression language is deliberately small. Domain predicates use equality,
conjunction, disjunction, and negation over closed typed fields. Extending that
language changes the profile and requires a new verifier-bound version.

## Executed counterfactuals

Generic text such as "this axis may change the result" is not negative
knowledge. For each record, a counterfactual checker must rebuild a neighbor,
re-evaluate it, and bind:

- source and target stable IDs;
- the single changed coordinate;
- changed semantic-IR paths;
- source and target result hashes;
- the observed disposition delta; and
- an explicit masking reason when the result is invariant.

The machine contract declares all six unordered code pairs exactly as
`[0,1]`, `[0,2]`, `[0,3]`, `[1,2]`, `[1,3]`, and `[2,3]`. Its spanning tree is
the three edges from variant 0 to variants 1, 2, and 3. This gives:

```text
16 x 16 x 4 modifier axes x 3 edges = 3,072 basis checks
```

The exhaustive report must also classify all unordered one-axis pairs while
holding the other coordinates fixed:

```text
4 axes x 16,384 fixed contexts x 6 unordered value pairs = 393,216 pairs
```

Each pair is labeled either `EFFECT` with a checked delta or
`CHECKED_INVARIANT` with a checked masking explanation. Only executed
behavior-changing counterfactuals and concrete rejected-action witnesses count
as negative knowledge.

Each modifier axis also has a machine-declared application predicate. The
predicate holds the other three modifier codes at zero and requires the
independently normalized source and target results to differ for every spanning
edge. A reference projection found an effect for all 192 topology-axis-edge
applications. Since each predicate applies to all 16 domains, this predicts all
`16 * 192 = 3,072` required spanning effects. The release oracle must re-run
these predicates. A predicted difference is not an executed receipt.

## Measurable content gates

Before generation, structural validation must establish:

- exactly 16 unique domain IDs and 16 unique topology IDs;
- exactly four values for evidence and each topology-local modifier;
- no empty evidence, state, resolution, or defeater target list;
- all actor, action, norm, conflict, lifecycle, and defeater references close;
- all witness raw values belong to the declared field type;
- all derived predicates are consumed by a norm or admissibility check;
- at least two causal mutation families per domain, at least 32 total; and
- the factorization product is exactly 65,536.

After generation, measured gates require:

- zero invalid typed combinations;
- at least four normalized behavior classes per topology;
- 16 distinct topology fingerprints after alpha-renaming identifiers;
- a checked domain mutation witness for every declared mutation family;
- all 3,072 basis counterfactuals executed;
- all 393,216 unordered one-axis pairs classified;
- replay-identical canonical records, shards, roots, and reports; and
- an independent oracle that recomputes labels from semantic IR rather than
  trusting generator output.

Unique hashes and exact record count are integrity checks, not evidence of
knowledge diversity. The release report must separately publish normalized
behavior counts, per-axis causal influence, masking rates, outcome and fallback
distributions, negative-knowledge uniqueness, and current-kernel support.
Thresholds are release-policy decisions and belong in the release-gate
specification, not in the content bank.

## Reference projection and executed v1 result

The following table was first computed as a reference projection over each
256-cell domain-topology block. Domain witnesses have the same four gate truth
pairs, so the counts repeat across all 16 domains. The final raw-corpus analyzer
recomputed all 256 blocks under the refined finite semantics, including mixed
deadline lifecycles and four-valued repair gates, and reproduced these outcome
counts.

| Code | Topology ID | Resolved | Abstain | Escalate |
|---:|---|---:|---:|---:|
| 0 | `same_action_obligation_prohibition` | 26 | 72 | 158 |
| 1 | `exclusive_dual_obligation` | 26 | 88 | 142 |
| 2 | `primary_permission_prohibition` | 26 | 88 | 142 |
| 3 | `safe_permission_prohibition` | 26 | 88 | 142 |
| 4 | `emergency_obligation_baseline_prohibition` | 26 | 88 | 142 |
| 5 | `exceptional_permission_general_prohibition` | 26 | 88 | 142 |
| 6 | `superseding_primary_safe_obligations` | 26 | 88 | 142 |
| 7 | `deadline_obligation_prohibition` | 34 | 64 | 158 |
| 8 | `ctd_repair_prohibition` | 29 | 80 | 147 |
| 9 | `delegated_obligation_principal_prohibition` | 26 | 88 | 142 |
| 10 | `capability_permission_scope_prohibition` | 26 | 88 | 142 |
| 11 | `publication_obligation_evidence_hold` | 26 | 88 | 142 |
| 12 | `lease_commit_conflict` | 62 | 20 | 174 |
| 13 | `capacity_allocate_reserve_conflict` | 62 | 20 | 174 |
| 14 | `transaction_commit_rollback_conflict` | 21 | 93 | 142 |
| 15 | `proof_acceptance_reverification_conflict` | 62 | 20 | 174 |

Every row sums to 256 and clears the local floors of 16 resolved, 16 abstain,
and 16 escalate. The minimums are 21, 20, and 142 respectively. The raw report
found 8,480 resolved cases, 18,576 unresolved abstentions, and 38,480 unresolved
escalations. Its largest normalized class in any block was 80, below the gate
ceiling of 192.

The analyzer found 16 alpha-normalized domain graph fingerprints, 16 topology
program fingerprints, 16 topology behavior fingerprints, and a minimum
pairwise topology distance of 256 over the 256 common variation cells. It
classified all 393,216 unordered one-axis pairs:

| Axis | `EFFECT` | `INVARIANT` |
| --- | ---: | ---: |
| Evidence | 91,136 | 7,168 |
| State | 67,840 | 30,464 |
| Resolution | 1,536 | 96,768 |
| Defeater | 17,088 | 81,216 |
| **Total** | **177,600** | **215,616** |

All 3,072 declared spanning applications produced an effect. The normalized
behavior quotient contains 322 dispositions. These are bounded measurements,
not proof of semantic novelty. An earlier compact projection omitted fields
later made mandatory by the closed normalization schema, so its pair and class
counts remain withdrawn.

Validation snapshot for this refinement:

- template bank SHA-256:
  `eadfeeb5a464f89a878800d21e84acd2ce8f3844a75cc49234bccde95b16c3c9`;
- finite semantics SHA-256:
  `d265a71141d3b5f0291a971c2997d085efe53c91851359f181b0682d7fd6f371`;
- exact JSON parsing, closed references, all 32 mutation deltas, both
  alpha-normalization procedures, all 256 projected cells per topology, and
  all 3,072 spanning applications passed the local reference checks;
- the complete report-file SHA-256 is
  `38b6b3fd208e89c6cba7d4c3911f74326325e628b513d3fef217d75b5590460a`;
- the executed counterfactual receipt-set root is
  `9ccf9ae8d13c9b4fb12cee0503af4010a35ac73c75b3457c4fda528c21a0c2ab`;
  and
- the reducer label is `QUARANTINED_CORPUS` because the complete receipt bodies
  and other mandatory release packages remain unbound or unretained.

## Authority and tool boundaries

All records are synthetic and non-authoritative. They cannot authorize an
external effect, establish law or ethics, or assert world truth. Frequencies in
the factorial design are experimental coverage, not population frequencies.

The template bank does not claim equivalence with an existing decision kernel.
`kernel_projection` is therefore `unclaimed_without_execution` for every
topology. Python, SMT, ESSO, Lean, Tau, or other tool support must be reported
only when that tool ran against the exact generated artifact and its receipt is
bound to the artifact hash.

## Residual nonclaims

This design is not a complete deontic logic, a legal code, an ethical theory,
a world model, a production authorization system, or proof of semantic
novelty. It specifies a bounded falsification and training fixture whose claims
remain conditional on implementation, independent verification, replay, and
measured causal diversity.
