---
title: A Proof-Carrying Tau Coordination Boundary
layout: docs
kicker: Technical Addendum to the Peer Review
description: A falsifiable architecture for compiling Tau transition semantics into scoped certificates, a coordination-obligation complex, and a checked partial-order agreement object.
permalink: /reviews/tau-coordination-boundary-technical-addendum/
---

This addendum develops the constructive recommendation from [*Consensus, Decomposed and Reconstructed*]({{ '/reviews/consensus-decomposed-and-reconstructed/' | relative_url }}). Its evidence graph, negative knowledge, and open gates are available in the [public coordination-boundary knowledge base]({{ '/reviews/tau-coordination-boundary-knowledge-base/' | relative_url }}).

It is an architecture proposal and an executable test packet. It is not a deployed network protocol, a performance result, or a proof that every relevant classification problem is tractable.

## 1. Objective

Given a state space, a declared invariant, transition semantics, and a network model, the compiler should answer:

> Which operation classes are safe to apply without total ordering, and what exact evidence justifies that classification?

The classifier must be sound before it is complete. It is acceptable to return `QUARANTINE_UNKNOWN`. It is not acceptable to treat a timeout, unsupported formula, bounded test, or missing assumption as evidence of confluence.

## 2. Required semantic contract

The input is not merely a Tau formula. It is a versioned contract:

```text
CoordinationModel {
  model_id
  tau_semantics_hash
  state_schema
  initial_state
  invariant(state)
  admissible(state, operation)
  apply(state, operation)
  merge(left_state, right_state)
  reachable_scope
  operation_classes
  delivery_assumptions
  fault_and_timing_profile
  resource_limits
  resolution_policy
}
```

The distinction between `admissible` and `apply` is important. Two operations may each be admissible at one state but become incompatible together. Two applications may also remain admissible while producing different outcomes in different orders.

The `delivery_assumptions` field must state whether the theorem assumes:

- the same finite update set at every replica;
- reliable eventual propagation;
- a fixed epoch manifest;
- causal delivery;
- a common availability certificate;
- or another explicit input model.

Without this field, an algebraic convergence theorem can be mistaken for a message-delivery theorem.

## 3. Canonical epoch capsule

Every classification and agreement decision should refer to one canonical subject. A suggested capsule is:

```text
EpochCapsuleV1 {
  model_hash
  tau_semantics_hash
  pre_state_hash
  invariant_hash
  transition_system_hash
  reachable_scope_hash
  proposal_manifest
  proposal_root
  delivery_model_hash
  fault_profile_hash
  resolver_policy_hash
  resource_budget_hash
}
```

The proposal manifest must use a canonical encoding and a deterministic ordering. Each operation binds its stable identifier, payload hash, and operation-class hash.

This prevents one certificate from being replayed against a different pre-state, proposal universe, invariant, policy, or Tau semantics. It does not prove that the hashed objects are correct. Hash binding depends on the declared canonical encoding and the collision resistance of the chosen hash function.

## 4. Stable independence, not a static label

Suppose operations `a` and `b` are both admissible in a reachable state `s`. A fast-path independence certificate should establish at least:

$$
\operatorname{admissible}(\operatorname{apply}(s,a),b),
$$

$$
\operatorname{admissible}(\operatorname{apply}(s,b),a),
$$

and

$$
\operatorname{apply}(\operatorname{apply}(s,a),b)
\equiv
\operatorname{apply}(\operatorname{apply}(s,b),a).
$$

The equivalence relation must be declared. It may be literal state equality, observational equivalence, or another checked quotient. Both paths must also preserve the declared invariant.

The quantifier over `s` matters. It may range over every reachable state, a formally characterized invariant region, or a finite bounded domain. A witness at one state does not establish stable independence.

This requirement is supported by a useful negative result in the literature: [*Commutative automata networks*](https://arxiv.org/abs/2004.09806) distinguishes local from global commutativity and shows that the local notion has substantially weaker consequences. Accordingly, separately certified operation classes do not compose automatically. Their union needs cross-class enabledness, diamond, and invariant obligations.

## 5. Receipt algebra

The output should be a tagged union. A verifier must reject unknown tags and missing bindings.

```text
ClassificationReceipt =
    FastConfluent
  | SlowJointUnsat
  | SlowOrderDependent
  | SlowInvariantViolation
  | RejectInvalid
  | QuarantineUnknown
```

### `FastConfluent`

```text
FastConfluent {
  model_hash
  operation_class_hash
  proof_kind
  proof_scope
  assumptions
  certificate
  checker_version
}
```

Permitted `proof_kind` values should be an allowlist, such as:

- `ACI_SEMILATTICE`;
- `CALM_MONOTONICITY`;
- `INVARIANT_CONFLUENCE`;
- `TERMINATING_CRITICAL_PAIRS`;
- `BOUNDED_EXHAUSTIVE`.

`BOUNDED_EXHAUSTIVE` must display its finite domain and must not be presented as an unbounded theorem.

### `SlowJointUnsat`

```text
SlowJointUnsat {
  model_hash
  proposal_set_root
  core_members
  unsat_certificate
  minimality_status
}
```

Minimality should be one of `PROVED_MINIMAL`, `CORE_ONLY`, or `UNKNOWN`. An unsatisfiable core need not be minimal, and minimal cores need not be unique.

### `SlowOrderDependent`

```text
SlowOrderDependent {
  model_hash
  witness_state
  operation_a
  operation_b
  state_after_a_then_b
  state_after_b_then_a
  inequality_certificate
}
```

This receipt covers non-confluence when both outcomes remain satisfiable.

### `SlowInvariantViolation`

```text
SlowInvariantViolation {
  model_hash
  common_ancestor
  left_history
  right_history
  left_state_valid
  right_state_valid
  merged_state
  invariant_counterexample
}
```

This is the direct invariant-confluence witness: two individually valid branches from a common ancestor merge into an invalid state.

### `RejectInvalid`

```text
RejectInvalid {
  model_hash
  state_hash
  operation_hash
  violated_rule
  countermodel
}
```

This outcome says that the declared admissibility relation rejects the operation. It does not authorize an agreement mechanism to override the relation.

### `QuarantineUnknown`

```text
QuarantineUnknown {
  model_hash
  obligation
  reason
  bounded_work_completed
  missing_evidence
}
```

Typical reasons include `TIMEOUT`, `UNSUPPORTED_FRAGMENT`, `UNBOUNDED_REACHABILITY`, `MISSING_TERMINATION`, `MISSING_DELIVERY_ASSUMPTION`, and `SEMANTIC_VERSION_MISMATCH`.

## 6. Coordination-obligation complex and plan

The classifier receipts should be compiled into one object, rather than handed to the network as an unrelated list.

Let `T` be the operation instances in the canonical proposal manifest. Define the coordination-obligation complex:

$$
\mathcal{C} = (T,\mathcal{I},\mathcal{U},\mathcal{D},\mathcal{V},\mathcal{N}),
$$

where:

- `I` contains scoped, certified independence relations;
- `U` contains jointly inconsistent hyperedges;
- `D` contains order-dependent pairs with divergent-path witnesses;
- `V` contains invariant-violating branch or merge witnesses;
- `N` contains unresolved obligations.

A versioned resolver policy compiles this evidence into:

$$
P = (K,X,Q,\prec),
$$

where `K` is admitted, `X` is excluded, `Q` is quarantined, and `≺` is an acyclic precedence relation over admitted operations.

The structural verifier requires complete disposition:

$$
K \mathbin{\dot\cup} X \mathbin{\dot\cup} Q = T.
$$

Every disclosed jointly inconsistent set must be hit by an exclusion or quarantine:

$$
\forall U \in \mathcal{U},\quad U \nsubseteq K.
$$

If both members of an order-dependent pair remain admitted, the plan must orient them through `≺`. Every admitted operation needs either a valid fast certificate or a checked slow-lane resolution. Every member of `N` remains quarantined.

The result is a **proof-carrying coordination plan**. Its agreement digest binds the complete semantic subject, proposal root, evidence root, dispositions, precedence constraints, slow-path justifications, and resolver policy. The network can agree on that digest without inventing a total order for unrelated operations.

The supplied structural checker verifies these representation-level conditions. Semantic certificate verification remains a separate gate.

## 7. Classification pipeline

```text
canonical model and proposal manifest
                 |
                 v
       schema, authority, and cost checks
                 |
          +------+------+
          |             |
        reject       continue
                        |
                        v
             prove a global fast-path rule
                        |
          +-------------+-------------+
          |                           |
      certificate                 no certificate
          |                           |
          v                           v
  FAST_CONFLUENT          search for typed counterexample
                                      |
                      +---------------+---------------+
                      |               |               |
                    UNSAT           order          invariant
                     core         dependence       violation
                      |               |               |
                      +---------------+---------------+
                                      |
                                      v
                                SLOW_CONFLICT

If neither proof nor counterexample completes within the declared budget:

                            QUARANTINE_UNKNOWN
```

### Gate 1: canonical subject

Every decision must bind the model, Tau semantics, proposal manifest, and policy versions. Two validators checking different proposal sets can each behave deterministically and still derive different states.

### Gate 2: cheap algebraic proofs

Conjunction-only amendments can use associativity, commutativity, and idempotence. This proves order and exact-duplicate invariance for the same amendment set.

It does not prove:

- that all replicas receive that set;
- that every amendment is authorized;
- that unique spam is cheap;
- or that state-dependent guarded adoption remains commutative.

### Gate 3: monotonicity

Where the program fits the CALM model, a monotonicity proof can justify coordination-free consistency. Applicability to the exact Tau semantics must be established rather than inferred from vocabulary.

### Gate 4: invariant confluence

For transaction-like state changes, attempt the stronger condition from invariant-confluence research. Relative to the declared invariant and reachable states, ask whether every pair of valid branches from a common ancestor merges to another valid state.

### Gate 5: critical pairs

Critical pairs are valuable counterexample generators. They become a global proof method only with a justified lifting theorem. For ordinary Newman's lemma, this includes termination. Without the required global hypothesis, successful local checks remain local evidence.

## 8. Conflict sets require a resolution problem

Suppose a proposal batch is unsatisfiable. Extracting one core answers:

> Why can this particular subset not coexist?

It does not answer:

> Which proposals should be retained?

Nor does it prove that proposals outside that core are conflict-free.

The batch may contain a family of cores:

$$
\mathcal{U} = \{U_1,U_2,\ldots,U_k\}.
$$

The architecture needs a declared resolution objective, for example:

- choose a maximal satisfiable subset;
- remove a minimal correction set;
- maximize a versioned priority or utility function subject to satisfiability;
- apply a pre-agreed deterministic priority rule;
- or submit the genuine choice surface to BFT, Generalized Paxos, a DAG protocol, or a vote.

These objectives are not equivalent. A deterministic tie-breaker can also be strategically manipulated, for example through identifier grinding, unless its fairness properties are analyzed.

The receipt should therefore separate:

1. **fact:** the checked conflict structure;
2. **policy:** the rule for selecting among compatible outcomes;
3. **agreement:** the network mechanism that makes the selected policy outcome common.

## 9. Partial order instead of total order

The slow lane should not automatically serialize the entire batch.

Let operations be vertices. Add a hyperedge for each jointly inconsistent set and a directed constraint for each required ordering relation. Operations unrelated by either relation may remain unordered.

The agreement object is then a conflict-aware partial order or a selected compatible subset, not necessarily one global sequence. [*Paxos Made Parallel*](https://www.microsoft.com/en-us/research/publication/paxos-made-parallel/) similarly uses partial-order traces rather than totally ordered requests.

This follows the direction of Generalized Paxos, which avoids ordering commuting commands, but adds application-level Tau evidence for why operations were classified as independent or conflicting.

The trace interpretation can be stated precisely. Two linear histories are equivalent when one can be obtained from the other by repeatedly swapping adjacent operations whose stable-independence certificate applies at that prefix. The desired soundness theorem is:

> Every topological ordering of an accepted plan produces an equivalent final state, provided every performed swap satisfies its scoped enabledness, diamond, and invariant obligations.

This theorem is a target, not a result of the reference checker. In particular, a static pairwise label is not enough when an operation changes whether another operation remains enabled.

The network mechanism still needs a stated model. At minimum it must address:

- authenticated identities or another admission rule;
- proposal availability;
- equivocation;
- duplicate and replay handling;
- timing or partial-synchrony assumptions;
- fault thresholds;
- liveness;
- deterministic interpretation of receipts;
- and canonical checkpoint selection.

## 10. Executable review packet

The addendum is available as:

- [`examples/tau/consensus_decomposed_review_addendum_v1.tau`]({{ '/examples/tau/consensus_decomposed_review_addendum_v1.tau' | relative_url }});
- [`scripts/check_consensus_decomposed_review.py`]({{ site.repo_url }}/blob/main/scripts/check_consensus_decomposed_review.py);
- [`scripts/check_consensus_decomposed_boolean_witnesses.py`]({{ site.repo_url }}/blob/main/scripts/check_consensus_decomposed_boolean_witnesses.py);
- [submission replay receipt]({{ '/assets/data/consensus_decomposed_submission_replay_v1.receipt.json' | relative_url }});
- [Tau addendum replay receipt]({{ '/assets/data/consensus_decomposed_review_addendum_v1.receipt.json' | relative_url }});
- [independent Boolean-witness receipt]({{ '/assets/data/consensus_decomposed_boolean_witnesses_v1.receipt.json' | relative_url }});
- [proof-carrying reference plan]({{ '/examples/tau_coordination_boundary/coordination_plan_v1.json' | relative_url }});
- [`scripts/check_tau_coordination_plan.py`]({{ site.repo_url }}/blob/main/scripts/check_tau_coordination_plan.py);
- [coordination-plan receipt]({{ '/assets/data/tau_coordination_plan_v1.receipt.json' | relative_url }});
- [curated Research Kernel export]({{ '/reviews/tau-coordination-boundary-knowledge-base/' | relative_url }}).

Replay with a locally installed Tau executable:

```bash
python3 scripts/check_consensus_decomposed_review.py --tau tau --json
```

The expected result vector is:

```text
T T F F F T T T F T F F F T F F F F
```

The reviewed run used Tau `0.7.0-alpha`, build `401d756b`, and matched all 18 values.

The same checker replayed the reviewed submission at commit `4baf38cbad096fdbe7c41c46e4b41d35c9ba44d2`. Its 14 normalization values and six temporal verdict codes also matched. Together, the two receipts record 38 checked outputs. The count measures replay coverage only, not protocol completeness.

The independent Python checker exhaustively enumerates the four valuations of each two-variable witness and the eight valuations of each three-variable witness. It confirms the finite propositional structure without depending on Tau's parser or solver. It does not replace the Tau replay because it does not validate Tau implementation semantics.

To replay a separately obtained copy of the reviewed submission:

```bash
python3 scripts/check_consensus_decomposed_review.py \
  --tau tau \
  --spec ../tau-lang-demos/consensus_decomposed.tau \
  --json

python3 scripts/check_consensus_decomposed_boolean_witnesses.py --json
python3 scripts/check_tau_coordination_plan.py --self-test --json
```

The coordination-plan checker accepted the canonical ten-operation plan and rejected eight mutations: changed model binding, changed evidence hidden from the agreement digest, cyclic precedence, admission of a disclosed higher-order conflict, admission of a disclosed invariant violation, admission of an unsupported operation, incomplete disposition, and stale plan hashing. The structural mutations were rehashed before validation, except for the two tests that intentionally target stale agreement or plan hashes. This prevents an unrelated stale hash from supplying the expected rejection. This is structural evidence only. The certificate hashes in the fixture are not proofs of Tau semantics.

## 11. Acceptance tests for an implementation

### Semantic soundness

1. Every `FAST_CONFLUENT` receipt verifies against its exact model hash.
2. Mutating the invariant, transition definition, Tau version, or proposal root invalidates the receipt.
3. A higher-order conflict invisible to all pair checks reaches the slow lane.
4. Satisfiable but unequal operation orders reach the slow lane.
5. A timeout or missing termination argument reaches `QUARANTINE_UNKNOWN`.
6. A fast certificate proves enabledness preservation, diamond equality, and invariant preservation over its exact reachable-state scope.
7. Two separately accepted operation classes remain uncomposed until their cross-class obligations pass.

### Batch conflict handling

1. Multiple overlapping cores are either enumerated within budget or explicitly reported as incomplete.
2. No proposal is classified safe merely because it lies outside the first extracted core.
3. The resolution objective and tie-breaking policy are versioned and replayable.

### Plan integrity

1. Admitted, excluded, and quarantined sets form a complete disjoint partition of the proposal manifest.
2. No disclosed inconsistent hyperedge is a subset of the admitted set.
3. Every admitted order-dependent pair is oriented by an acyclic precedence relation.
4. Every admitted operation has a fast certificate or a checked slow-lane justification.
5. Every unresolved operation is quarantined.
6. Mutating any bound subject, disposition, or precedence edge invalidates the plan digest.

### Distributed integration

1. Two replicas given the same canonical manifest and receipt set derive the same admitted partial order.
2. Different manifests do not silently share one certificate.
3. Withheld proposal data prevents promotion rather than producing a guessed result.
4. Cross-implementation Tau disagreements fail closed.
5. Byzantine, crash, and network-delay tests are evaluated under an explicit fault model.

### Resource control

1. Proposal size, solver fuel, memory, and receipt size are bounded.
2. Exact duplicates may be semantically idempotent but are still metered for transport and verification cost.
3. Timeouts produce typed uncertainty rather than implicit acceptance.

## 12. Benchmark quantities

Raw state count is not the principal measure. The useful quantities are:

- fraction of operations admitted to the fast lane;
- fraction of batches containing a conflict;
- core-size and core-overlap distributions;
- fraction of proposals retained by the declared resolution objective;
- false-serialization rate;
- coordination amplification, meaning operations serialized per operation participating in a genuine conflict;
- checker latency and timeout distributions;
- receipt size and verification cost;
- cross-implementation semantic disagreement;
- network bytes, messages, and latency attributable specifically to slow-lane agreement.

Each measurement must name its workload, concurrency window, state distribution, invariant, transition family, network model, and policy version.

## 13. Formal theorem targets

The architecture suggests six theorem families.

### Same-set semilattice theorem

For a finite update set combined by an associative, commutative, and idempotent operation, every permutation and exact duplicate expansion has the same fold result.

### Classifier soundness

If the verifier accepts a `FAST_CONFLUENT` receipt for model `M` and scope `D`, then every execution admitted by `D` preserves `M`'s invariant and produces the equivalence of outcomes promised by the receipt.

This should be a soundness theorem, not a completeness theorem. Unsupported safe cases may remain quarantined.

### Counterexample soundness

Every slow-lane receipt decodes to an actual checked witness in the bound model: an inconsistent set, unequal operation orders, or an invariant-violating merge.

### Composition theorem

If two fast-lane classes are separately certified, their union is not automatically certified. Composition requires an additional cross-class commutativity and invariant-preservation obligation.

This final theorem prevents a common modularity error: local safety proofs do not automatically compose into global coordination freedom.

### Trace soundness

If two topological orderings of an accepted plan differ only by adjacent swaps covered by applicable stable-independence certificates, executing either ordering from the bound pre-state produces equivalent final states and preserves the invariant.

### Plan and network refinement

The structural verifier should prove that an accepted plan completely disposes of the bound manifest, excludes every disclosed inconsistent hyperedge, orients every admitted order witness, quarantines unresolved operations, and contains no precedence cycle.

A separate protocol theorem must then state the fault, timing, authentication, and availability assumptions under which agreement on the plan digest yields common execution and checkpoint selection. The structural theorem cannot substitute for that network theorem.

## Conclusion

The proposed architecture does not eliminate consensus. It gives consensus a smaller and better-specified input.

The fast lane carries only operations whose independence has an applicable, state-scoped certificate. The slow lane carries typed evidence of genuine choice. A versioned policy turns those obligations into a selected compatible subset and an acyclic partial order. Invalid operations are rejected by the declared rules. Unknown cases remain quarantined.

The bounded reference plan and checker establish that this representation can fail closed structurally. They do not yet establish semantic-certificate soundness or a network protocol. The [public evidence base]({{ '/reviews/tau-coordination-boundary-knowledge-base/' | relative_url }}) records the supported findings, negative knowledge, executable artifacts, literature map, and remaining gates.

This preserves the strongest insight in `consensus_decomposed.tau` while adding higher-order conflict handling, stable independence, complete disposition, canonical binding, partial-order agreement, and explicit network boundaries.
