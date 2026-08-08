---
title: Tau Coordination Boundary Evidence Base
layout: docs
kicker: Curated Research Kernel Export
description: Supported findings, negative knowledge, primary literature, executable artifacts, and open proof obligations for the Tau coordination-boundary proposal.
permalink: /reviews/tau-coordination-boundary-knowledge-base/
---

This page is the public evidence base for [*Consensus, Decomposed and Reconstructed*]({{ '/reviews/consensus-decomposed-and-reconstructed/' | relative_url }}) and the [proof-carrying coordination architecture]({{ '/reviews/tau-coordination-boundary-technical-addendum/' | relative_url }}).

It is a curated export from Research Kernel runs `tau-coordination-minimization-review-v1-20260808` and `tau-semantic-conflict-hypergraph-v2-20260808`. A raw research graph is a poor public interface because it contains retrieval candidates, superseded formulations, intermediate graph bookkeeping, and failed promotion attempts. This page and its [versioned JSON export]({{ '/assets/data/tau_coordination_boundary_knowledge_base_v1.json' | relative_url }}) retain the useful claims, negative knowledge, evidence paths, and open obligations in a stable format.

## Status vocabulary

| Status | Meaning |
|---|---|
| `SUPPORTED` | The exact scoped claim has independent replay evidence and survived its declared falsification attempt. |
| `REPRODUCED` | A source-pinned output was replayed under the named implementation. |
| `BOUNDED_PROTOTYPE_CHECKED` | A finite reference artifact passed its structural checker and mutation tests. |
| `CANDIDATE` | The proposal is precise enough to test, but the required evidence is incomplete. |
| `OPEN` | A proof, implementation, or measurement obligation remains. |

None of these labels means that a production distributed protocol has been deployed or proved safe.

## Supported and reproduced findings

### Higher-order conflict exists

There are three proposals whose pairs are satisfiable while the full set is not. The result was checked in Tau and by exhaustive independent enumeration of the finite Boolean valuations.

**Status:** `SUPPORTED`

**Evidence:** [Tau addendum receipt]({{ '/assets/data/consensus_decomposed_review_addendum_v1.receipt.json' | relative_url }}) and [Boolean witness receipt]({{ '/assets/data/consensus_decomposed_boolean_witnesses_v1.receipt.json' | relative_url }}).

### One unsatisfiable core is incomplete

Minimal inconsistent sets can overlap. Non-confluence can also produce two different satisfiable outcomes, in which case no unsatisfiable core represents the problem.

**Status:** `SUPPORTED`

**Evidence:** [Tau addendum receipt]({{ '/assets/data/consensus_decomposed_review_addendum_v1.receipt.json' | relative_url }}) and [Boolean witness receipt]({{ '/assets/data/consensus_decomposed_boolean_witnesses_v1.receipt.json' | relative_url }}).

### The reviewed Tau examples reproduce

The exact reviewed source produced its declared 14 normalization values and six temporal codes under the tested Tau build.

**Status:** `REPRODUCED`

**Evidence:** [submission replay receipt]({{ '/assets/data/consensus_decomposed_submission_replay_v1.receipt.json' | relative_url }}).

The replay does not prove semantic compatibility across every Tau release.

### The reference coordination plan fails closed structurally

The ten-operation reference plan contains two overlapping higher-order conflicts, one order-dependent pair, two bounded fast-path operations, and one unsupported operation. Its checker accepted the canonical plan and rejected eight mutations:

1. a changed model binding;
2. changed evidence hidden from the agreement digest;
3. cyclic precedence;
4. admission of a disclosed higher-order conflict;
5. admission of a disclosed invariant violation;
6. admission of an unsupported operation;
7. omission of an operation disposition;
8. a stale plan hash after mutation.

**Status:** `BOUNDED_PROTOTYPE_CHECKED`

**Evidence:** [reference plan]({{ '/examples/tau_coordination_boundary/coordination_plan_v1.json' | relative_url }}), [checker]({{ site.repo_url }}/blob/main/scripts/check_tau_coordination_plan.py), and [receipt]({{ '/assets/data/tau_coordination_plan_v1.receipt.json' | relative_url }}).

The checker validates structure and bindings. It does not validate the semantic proof objects named by certificate hashes, and it does not prove Byzantine safety or liveness.

### The ADD-only implicit resolver passes its bounded checks

For a fixed satisfiable base law and a finite conjunction-only ADD batch, the reference resolver discovers minimal inconsistent sets as needed, solves the resulting weighted hitting-set problem exactly, and globally rechecks the complete accepted remainder. The master problem also enforces proposal dependencies.

The updated replay matched all 15 declared Tau normalization values under Tau `0.7.0-alpha`, build `f7423804`. Seventeen Python tests covered pair and three-way conflicts, seeded comparisons with exhaustive global optimization, dependency closure, inconsistent-base rejection, `UNKNOWN`, resource exhaustion, and semantic-subject binding. They also covered all 24 arrival permutations, identical redelivery, conflicting duplicate identifiers, canonical proposal roots, payload, cost, and dependency mutations, policy and budget mismatches, and resolution-certificate replay.

**Status:** `SUPPORTED` for the exact bounded claims `tau-hg-c-001`, `tau-hg-c-002`, and `tau-hg-c-003`.

**Evidence:** [Tau and Python replay receipt]({{ '/assets/data/tau_semantic_conflict_hypergraph_v1.receipt.json' | relative_url }}), [reference model]({{ site.repo_url }}/blob/main/examples/tau_coordination_boundary/semantic_conflict_hypergraph_v1.py), and [tests]({{ site.repo_url }}/blob/main/examples/tau_coordination_boundary/test_semantic_conflict_hypergraph_v1.py).

This result does not cover non-ADD operations, unbounded tractability, production Tau-oracle soundness, proposal-set agreement, Byzantine safety, liveness, or fairness.

### The sealed epoch is a bounded improvement over the reviewed pair path

The [reviewed commit](https://github.com/taumorrow/tau-lang-demos/commit/4baf38cbad096fdbe7c41c46e4b41d35c9ba44d2) routes conflicts pairwise and changes guarded `ADD` state on arrival. The repaired reference path stores proposals in a pending set, seals one content-bound manifest, detects minimal inconsistent sets of arbitrary finite size, resolves them under one declared deterministic policy, globally rechecks the accepted remainder, and emits a subject-bound certificate.

For the exact four-proposal reference epoch, all 24 arrival permutations produced the same proposal-set root, accepted and rejected sets, and resolution root. The demonstrated size-three conflict is invisible to every pair check. This establishes a strict improvement only inside the fixed-base, finite, conjunction-only `ADD` model.

**Status:** `SUPPORTED` by the local Research Kernel promotion gate for `tau-hg-c-003`.

The promotion status records evidence and falsification checks inside Research Kernel. It is not an external proof of a production network protocol.

## Architecture candidate

The proposed object is a **proof-carrying coordination plan**.

Let `T` be the proposal set. The semantic classifier produces a coordination-obligation complex containing:

- certified independence relations;
- jointly inconsistent hyperedges;
- order-dependent pairs;
- invariant-violating branch witnesses;
- unresolved obligations.

A policy then produces a plan:

$$
P = (K, X, Q, \prec),
$$

where:

- `K` is the admitted set;
- `X` is the excluded set;
- `Q` is the quarantined set;
- `≺` is an acyclic precedence relation over admitted operations.

The structural acceptance conditions include:

$$
K \mathbin{\dot\cup} X \mathbin{\dot\cup} Q = T,
$$

$$
\forall U \in \mathcal{U},\quad U \nsubseteq K,
$$

and every admitted order-dependent pair must be oriented by `≺`. Here `U` is the disclosed family of jointly inconsistent sets.

The agreement mechanism receives one content-addressed digest of the selected plan. It does not need to receive an invented total order over certified independent operations.

**Status:** `CANDIDATE`, with a bounded structural prototype.

## Negative knowledge retained

### Pairwise tests do not establish batch safety

A conflict graph can miss a higher-order inconsistent set. The residual object may require hyperedges.

### One core does not establish conflict coverage

Minimal unsatisfiable subsets can be exponentially numerous. A core enumerator must report whether coverage is complete within a declared bound or incomplete at budget exhaustion.

### Satisfiable does not mean confluent

Two execution orders can both remain valid and still produce unequal states. Order witnesses and invariant-merge witnesses are separate evidence types.

### Local commutativity does not automatically become global commutativity

The *Commutative automata networks* results distinguish local and global schedule independence. A static independence label is therefore insufficient when enabledness or effects change with state.

A fast-path certificate should establish, over its exact reachable-state scope:

1. both operations remain enabled after either order;
2. the two execution diamonds join to equivalent states;
3. the declared invariant is preserved;
4. independently certified classes satisfy cross-class composition obligations.

### Deterministic checking does not establish a common input

Two replicas can run the same checker over different proposal universes and derive different states. The model, epoch, pre-state, proposal manifest, policy, resource limits, and semantic version must be content-addressed.

### Logical repair must preserve dependencies

A minimum hitting set can be logically satisfiable while retaining a proposal whose prerequisite was rejected. Dependency closure must be a constraint of the resolver's master problem, not an optional check after optimization.

### Conflict identities must bind their semantic subject

An edge hash over only an epoch label and member IDs can be replayed under a different domain, base law, proposal set, or oracle implementation. The edge identity must bind all of those fields through a canonical encoding.

### One supplied paper was not relevant

[arXiv:1901.00193](https://arxiv.org/abs/1901.00193) studies cohomology of algebraic surfaces. It was excluded from the distributed-coordination argument.

## Literature map

| Source | What it contributes | What it does not establish here |
|---|---|---|
| [CALM](https://arxiv.org/abs/1901.01930) | Logical monotonicity as the boundary for coordination-free consistency in its model. | That an arbitrary Tau transition system is monotone. |
| [Invariant confluence](https://arxiv.org/abs/1402.2237) | A necessary and sufficient coordination-avoidance criterion relative to declared invariants and transactions. | Applicability without mapping Tau states, transitions, merge, and reachability to the paper's model. |
| [Generalized Paxos](https://www.microsoft.com/en-us/research/publication/generalized-consensus-and-paxos/) | Agreement need not impose order on commuting commands. | A universal network protocol for every fault and timing model. |
| [Paxos Made Parallel](https://www.microsoft.com/en-us/research/publication/paxos-made-parallel/) | Replication can agree on partial-order traces rather than total request sequences. | That the proposed Tau independence relation is semantically sound. |
| [CRDTs](https://arxiv.org/abs/1805.06358) | Deterministic convergence after replicas receive the same update set. | Authentication, common epoch selection, or availability by algebra alone. |
| [MUS enumeration](https://arxiv.org/abs/1708.00400) | Complete conflict enumeration can face exponentially many minimal cores. | A tractable complete resolver for arbitrary Tau constraints. |
| [Commutative automata networks](https://arxiv.org/abs/2004.09806) | Local and global commutativity are distinct notions. | A direct theorem about Tau without a checked semantic translation. |

TheoremSearch supplied retrieval-only statement shapes for trace monoids and a breaker query that led to the local-versus-global commutativity source. Its formal-declaration query returned no direct result. The claims on this page rely on the linked primary sources and local executable evidence, not on retrieval scores.

## Open gates

1. **Semantic soundness:** independently verify every fast certificate against the exact model hash and reachable-state scope.
2. **Composition:** prove or refute cross-class independence instead of composing local certificates automatically.
3. **Conflict coverage:** distinguish a complete bounded conflict family from a partial set of discovered cores.
4. **Network refinement:** prove that agreement on the plan digest refines to common execution and checkpoint selection under a named fault and timing model.
5. **Differential semantics:** replay the same capsule across independent Tau implementations.
6. **Workload evidence:** measure false serialization, coordination amplification, messages, latency, certificate cost, and timeout rates on source-pinned workloads.
7. **Resolver refinement:** prove that the production epoch state machine implements the bounded ADD resolver's mathematical contract, including dependency closure and typed deferment.

## Replay

```bash
python3 scripts/check_consensus_decomposed_review.py --tau tau --json
python3 scripts/check_consensus_decomposed_boolean_witnesses.py --json
python3 scripts/check_tau_coordination_plan.py --self-test --json
python3 scripts/check_tau_semantic_conflict_hypergraph_v1.py --tau tau --json
```

The first and fourth commands require a separately installed Tau executable. The other two use only the Python standard library.

## Public export

The [machine-readable knowledge base]({{ '/assets/data/tau_coordination_boundary_knowledge_base_v1.json' | relative_url }}) is intended for independent review, archival, and future benchmarks. It preserves claim boundaries so that a checked finite example cannot silently become a claim about an unbounded or deployed system.
