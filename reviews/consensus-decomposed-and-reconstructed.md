---
title: Consensus, Decomposed and Reconstructed
layout: docs
kicker: Formal-Methods Peer Review
description: A concise review of Tau's coordination-minimization demo, its higher-order conflict gap, and a proof-carrying partial-order extension.
permalink: /reviews/consensus-decomposed-and-reconstructed/
---

This review examines Tau's [`consensus_decomposed.tau`](https://github.com/taumorrow/tau-lang-demos/blob/4baf38cbad096fdbe7c41c46e4b41d35c9ba44d2/consensus_decomposed.tau) at commit `4baf38cbad096fdbe7c41c46e4b41d35c9ba44d2`.

## Verdict

**Revise and extend.**

The demo's central idea is sound:

> Do not impose a total order when the declared operation semantics prove that order is irrelevant.

The demo correctly separates validity, ordering, finality, and Sybil resistance. Its conjunction examples also show a real coordination-free case. The missing piece is a complete representation of the operations that still require coordination.

## Reproduction

The reviewed source has SHA-256 `869e4cba2f553afd67b0d7ba87e945e6d4826f1d6ab9055176af8c964bec6f5e`.

Under Tau `0.7.0-alpha`, build `401d756b`:

- all 14 declared normalization results matched;
- all six temporal verdict codes matched;
- all 18 additional review formulas matched.

An independent exhaustive Boolean checker reproduced the finite counterexamples. The [receipts and replay commands]({{ '/reviews/tau-coordination-boundary-technical-addendum/#10-executable-review-artifacts' | relative_url }}) are public.

## What the demo proves

If amendments are combined only by conjunction, then:

$$
(C \land A) \land B = (C \land B) \land A,
$$

and:

$$
C \land A \land A = C \land A.
$$

Therefore, order and exact duplicate delivery do not affect the result, provided replicas begin from the same state and eventually evaluate the same finite amendment set.

This supports coordination avoidance for that scoped operation class. It does not establish common delivery, authorization, finality, availability, or Byzantine agreement.

## Main defect: conflicts are not necessarily pairwise

Let:

$$
P=x\lor y, \qquad Q=x\lor\neg y, \qquad R=\neg x.
$$

Every pair is satisfiable:

$$
P\land Q\neq0, \qquad P\land R\neq0, \qquad Q\land R\neq0.
$$

The full set is not:

$$
P\land Q\land R=0.
$$

A pairwise conflict graph misses this case. The residual coordination object must support higher-order conflict sets, represented naturally as hyperedges or unsatisfiable cores.

One core is also not a complete scheduler. Cores may overlap, and non-confluence may occur even when both execution orders remain satisfiable but produce different states.

## Proposed improvement

The proposed extension is a **proof-carrying Tau coordination boundary**:

1. Bind the pre-state, Tau semantics, invariant, transition system, reachable scope, proposal manifest, resolver policy, and resource budget into one canonical epoch capsule.
2. Require a scoped certificate for every fast-path operation class. The certificate must establish enabledness preservation, invariant preservation, and equal outcomes under permitted reorderings.
3. Record the residue as jointly inconsistent sets, order-dependent pairs, invariant violations, and unresolved obligations.
4. Produce a complete plan:

$$
P=(K,X,Q,\prec),
$$

where `K` is admitted, `X` is excluded, `Q` is quarantined, and `≺` is an acyclic precedence relation.

The plan must satisfy:

$$
K\mathbin{\dot\cup}X\mathbin{\dot\cup}Q=T,
$$

and no disclosed inconsistent set may remain entirely inside `K`. Every admitted order-dependent pair must be oriented by `≺`.

The agreement layer can then agree on one content-addressed partial-order plan without inventing an order among certified independent operations.

## What this adds

| Gap in the reviewed demo | Extension | Status |
|---|---|---|
| Higher-order inconsistency | Conflict hyperedges | Finite witnesses reproduced |
| Overlapping conflict cores | Complete admitted, excluded, or quarantined disposition | Bounded plan checked |
| Satisfiable but order-dependent operations | Divergent-diamond witness plus precedence | Bounded structure checked |
| Different proposal universes | Canonical proposal root and epoch capsule | Hash binding checked |
| State-dependent commutativity | Reachable-scope certificate contract | General proof open |
| Handoff to agreement | Content-addressed partial-order plan | Network refinement open |

The reference checker accepted a ten-operation plan and rejected eight targeted mutations. This establishes bounded structural integrity only. It does not verify the mathematical content of every semantic certificate.

## Conclusion

The Tau demo identifies a useful optimization boundary, but pairwise conflicts are too weak and the network handoff is incomplete. The stronger architecture is:

$$
\boxed{
\text{Prove the confluent region, witness the residue, and coordinate only the genuine choices.}
}
$$

The [technical addendum]({{ '/reviews/tau-coordination-boundary-technical-addendum/' | relative_url }}) specifies the architecture. The [public evidence base]({{ '/reviews/tau-coordination-boundary-knowledge-base/' | relative_url }}) contains the checked artifacts, negative knowledge, primary literature, and open proof obligations.

This work does not solve Byzantine agreement, liveness, availability, Sybil resistance, censorship, or fairness.

## Selected references

1. Joseph M. Hellerstein and Peter Alvaro, [“Keeping CALM: When Distributed Consistency is Easy”](https://arxiv.org/abs/1901.01930), 2019.
2. Peter Bailis et al., [“Coordination Avoidance in Database Systems”](https://arxiv.org/abs/1402.2237), 2014.
3. Leslie Lamport, [“Generalized Consensus and Paxos”](https://www.microsoft.com/en-us/research/publication/generalized-consensus-and-paxos/), 2005.
4. Nuno Preguiça, Carlos Baquero, and Marc Shapiro, [“Conflict-free Replicated Data Types”](https://arxiv.org/abs/1805.06358), 2018.
5. Zhenyu Guo et al., [“Paxos Made Parallel”](https://www.microsoft.com/en-us/research/publication/paxos-made-parallel/), 2012.
6. Florian Bridoux, Maximilien Gadouleau, and Guillaume Theyssier, [“Commutative automata networks”](https://arxiv.org/abs/2004.09806), 2020.
