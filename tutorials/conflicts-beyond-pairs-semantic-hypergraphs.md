---
title: "When conflicts need more than pairs"
layout: docs
kicker: Hypergraphs, minimal conflicts, and safe resolution
description: "A picture-first introduction to higher-order conflicts, minimal inconsistent sets, hitting sets, and a bounded Tau coordination architecture."
---

## Three cards that fool a pair checker

Place three proposal cards on a table:

```text
P: turn switch a on

Q: turn switch b on

R: if switch a is on, switch b must be off
```

Now inspect every pair.

### Pair `P, Q`

Both switches may be on. This pair is consistent.

### Pair `P, R`

Switch `a` may be on while switch `b` is off. This pair is consistent.

### Pair `Q, R`

Switch `a` may be off while switch `b` is on. This pair is consistent.

Every pair passes. But all three cards together require switch `b` to be both on and off.

```text
P + Q + R = inconsistent
```

The conflict has size three. No pairwise conflict detector can see it.

<figure class="fp-figure">
  <p class="fp-figure-title">The hidden three-way conflict</p>
  {% include diagrams/hypergraph-three-way-conflict.svg %}
  <figcaption class="fp-figure-caption">
    A graph records pair relations. The curved boundary on the right is one hyperedge containing all three proposals.
  </figcaption>
</figure>

## What this repairs in the reviewed Tau demo

The reviewed [`consensus_decomposed.tau` commit](https://github.com/taumorrow/tau-lang-demos/commit/4baf38cbad096fdbe7c41c46e4b41d35c9ba44d2) establishes an important result: compatible amendments joined by conjunction do not need a total arrival order. Its conflict path, however, is explicitly described as checking proposals “pair by pair” and producing “one verdict per pair.” Its guarded `ADD` path also changes the active law as each proposal arrives.

That leaves two concrete failures in the bounded `ADD` case:

1. every pair may pass while a larger set fails;
2. changing the active law on arrival can make arrival order determine which otherwise admissible proposal survives.

The repaired path delays activation until a finite proposal epoch has been sealed.

| Reviewed path | Repaired bounded `ADD` path |
|---|---|
| Check conflicts as pairs | Check the complete batch and extract minimal inconsistent sets of any size |
| Mutate the active law on arrival | Add authenticated records only to a pending set |
| No canonical proposal-set commitment | Seal a sorted, content-bound proposal manifest |
| No deterministic batch-repair certificate | Bind the resolution to the domain, epoch, base, proposal root, Tau semantics, policy, and resource budget |
| Pair verdicts guide routing | A final whole-batch `SAT` result owns activation |

This is a strict improvement only under the declared model: a fixed satisfiable base, a finite set of conjunction-only `ADD` proposals, and agreement on the same sealed manifest. Establishing that common manifest still requires a network protocol. The resolver does not solve censorship, availability, Byzantine agreement, or liveness.

## The rubber-band rule

Imagine placing a rubber band around the smallest collection of cards that fails together.

```text
one card inside      unary conflict

two cards inside     pair conflict

three or more        higher-order conflict
```

The cards are the **vertices**. Each rubber band is a **hyperedge**.

A graph edge joins two vertices. A hypergraph edge may contain any finite number of vertices. That extra freedom is exactly what the example requires.

This rubber-band picture is a representation, not a proof. The logical checker establishes which collections are inconsistent. The picture records the result.

## Fix the world before drawing the hypergraph

The conflict structure depends on its base law. Fix:

- a satisfiable base law `C`;
- a finite proposal set `V`;
- one logical formula `φ(v)` for each proposal `v`.

For a selected proposal set `S`, define:

$$
\operatorname{Law}_C(S)
=
C \land \bigwedge_{v\in S}\varphi(v).
$$

Read the formula exactly:

> “The law relative to base `C` and selected set `S` equals `C` and the conjunction of `φ(v)` for every `v` in `S`.”

The set is consistent when the combined law is satisfiable:

$$
\operatorname{Cons}_C(S)
\quad\Longleftrightarrow\quad
\operatorname{Law}_C(S)\neq 0.
$$

Here `0` means the always-false specification. Therefore `Law_C(S) ≠ 0` means that at least one assignment satisfies the entire law.

## What makes a conflict edge minimal?

A useful conflict edge contains no unnecessary proposal.

$$
e\in E_C
\quad\Longleftrightarrow\quad
\neg\operatorname{Cons}_C(e)
\ \land\
\forall v\in e,\
\operatorname{Cons}_C(e\setminus\{v\}).
$$

Read it exactly:

> “A set `e` belongs to the edge family `E_C` exactly when `e` is inconsistent relative to `C`, and, for every member `v` of `e`, removing `v` makes the remaining set consistent relative to `C`.”

This is a **minimal inconsistent set**. Minimal means that no member can be removed while preserving the conflict. It does not necessarily mean smallest cardinality among all conflicts.

For the switch example:

```text
{P, Q, R}       inconsistent

{P, Q}          consistent

{P, R}          consistent

{Q, R}          consistent
```

Therefore `{P,Q,R}` is one hyperedge.

## The consistency complex

Let `I_C` contain every consistent proposal set:

$$
\mathcal I_C
=
\{S\subseteq V: \operatorname{Cons}_C(S)\}.
$$

This family is downward closed. If a conjunction is satisfiable, removing some of its requirements cannot make it unsatisfiable.

$$
S\in\mathcal I_C
\ \land\
T\subseteq S
\quad\Longrightarrow\quad
T\in\mathcal I_C.
$$

The consistent sets form an abstract simplicial complex. The conflict hyperedges are its minimal missing faces.

That gives a reconstruction rule:

$$
\operatorname{Cons}_C(S)
\quad\Longleftrightarrow\quad
\forall e\in E_C,\ e\nsubseteq S.
$$

Read it exactly:

> “`S` is consistent relative to `C` exactly when, for every conflict edge `e`, `e` is not a subset of `S`.”

In plain language, a batch is safe exactly when it does not contain every member of any complete conflict edge.

This equivalence assumes a finite proposal set, conjunction-only additions, and a satisfiable fixed base. It is not a theorem about arbitrary state-changing operations.

## Repair means hitting every conflict

Suppose `R` is the set of rejected proposals. The accepted set is:

$$
A=V\setminus R.
$$

The rejection set repairs every known conflict exactly when it intersects every hyperedge:

$$
\forall e\in E_C,\quad R\cap e\neq\varnothing.
$$

Such an `R` is called a **hitting set**.

```text
conflict edge       a combination that cannot all survive

hitting set         at least one rejection from every conflict

accepted set        everything not rejected
```

Logic identifies the conflicting sets. It does not decide which proposal should lose. That requires a declared policy.

For nonnegative rejection costs `w(v)`, one possible policy is:

$$
\underset{R\subseteq V}{\operatorname{argmin}}
\sum_{v\in R}w(v)
$$

subject to:

$$
\forall e\in E_C,\quad R\cap e\neq\varnothing.
$$

This asks for a cheapest hitting set under the declared costs. Different policies may produce different legitimate repairs. The costs are governance inputs, not facts discovered by logic.

## The whole hypergraph need not be known first

Complete enumeration of all minimal inconsistent sets can be expensive. A bounded resolver can discover only the conflicts it needs:

```text
known conflicts := none

repeat:
    choose the cheapest rejection set
    that hits every known conflict

    accepted := all proposals minus rejected proposals

    check the complete accepted batch

    if SAT:
        return the accepted and rejected sets

    if UNKNOWN or budget exhausted:
        defer without activation

    if UNSAT:
        shrink the failing batch to a minimal conflict
        add that conflict to the known hypergraph
```

Each newly discovered edge adds one necessary rule:

> At least one proposal inside this edge must be rejected.

The final whole-batch satisfiability check remains the safety boundary. A partial hypergraph is useful for explanation and optimization, but it must not be mistaken for a complete description unless completeness has been proved separately.

## Why dependencies belong inside the resolver

Suppose proposal `q` depends on proposal `p`.

```text
p: create a permission

q: use that permission
```

A resolver that considers only logical conflict might reject `p` while retaining `q`. The result could be satisfiable as a formula yet invalid as a proposal package.

Let `K` be the accepted set and `Dep(q)` the declared dependencies of `q`. The accepted set must be dependency-closed:

$$
q\in K
\ \land\
p\in\operatorname{Dep}(q)
\quad\Longrightarrow\quad
p\in K.
$$

Read it exactly:

> “If `q` belongs to the accepted set `K`, and `p` belongs to the declared dependencies of `q`, then `p` belongs to `K`.”

Accepting a dependent proposal requires accepting all of its declared prerequisites.

## What happens when the checker cannot decide?

The checker interface needs three outcomes:

```text
SAT       at least one satisfying assignment was established

UNSAT     inconsistency was established

UNKNOWN   neither result was established within the declared method
```

A timeout, unsupported formula, implementation error, or exhausted bound is not evidence for either `SAT` or `UNSAT`.

```text
UNKNOWN → defer the epoch
```

This fail-closed rule preserves the distinction between lack of evidence and negative evidence.

## The bounded Tau specialization

For one fixed, satisfiable base and one finite set of conjunction-only `ADD` proposals, the architecture can use Tau as the consistency oracle and a deterministic hitting-set solver as the repair optimizer.

The state transition is split into six steps:

```text
receive proposal records
        ↓
store in a pending set without changing the active law
        ↓
seal one canonical proposal manifest
        ↓
run global Tau checks and discover minimal conflicts as needed
        ↓
apply the declared deterministic repair policy
        ↓
globally recheck, certify, then activate the accepted conjunction
```

The implementation must also bind every edge and resolution certificate to:

```text
domain
epoch
base-law root
proposal-set root
Tau semantics identifier
sorted proposal identifiers
resource limits
resolution policy
```

This prevents a valid conflict record from being replayed under a different logical subject.

The public reference packet includes:

- the [Tau three-way-conflict example]({{ '/examples/tau/consensus_hypergraph_v1.tau' | relative_url }});
- the [bounded Python resolver]({{ site.repo_url }}/blob/main/examples/tau_coordination_boundary/semantic_conflict_hypergraph_v1.py);
- its [unit tests]({{ site.repo_url }}/blob/main/examples/tau_coordination_boundary/test_semantic_conflict_hypergraph_v1.py);
- the [replay receipt]({{ '/assets/data/tau_semantic_conflict_hypergraph_v1.receipt.json' | relative_url }});
- and the complete [technical architecture]({{ '/reviews/tau-coordination-boundary-technical-addendum/' | relative_url }}).

The current replay matched all 15 declared Tau results under Tau `0.7.0-alpha`, build `f7423804`. All 17 Python tests passed. Those tests include every one of the 24 arrival permutations of the four-proposal example. Every permutation produced the same proposal-set root, accepted set, rejected set, and resolution root. Rehashed mutations of the payload, cost, dependencies, epoch subject, policy, budget, and certificate semantics were rejected.

The Research Kernel promotion gate accepted the exact bounded improvement claim after evidence attachment, refutation planning, contradiction retrieval, and replay. That status records a local evidence gate. It is not an external proof of a production protocol.

The bounded packet checks the reference model. It does not establish that arbitrary minimal-conflict enumeration is efficient or that a distributed protocol is safe.

## Where the hypergraph stops

The construction in this tutorial is deliberately narrow.

It applies to:

```text
fixed base law
finite proposal snapshot
conjunction-only ADD proposals
deterministic canonical semantics
declared finite resource bounds
```

It does not by itself solve:

```text
payments or double spends
REPLACE and DELETE operations
satisfiable operations whose order changes the state
proposal censorship or data availability
Byzantine agreement
liveness or fairness
the soundness of the underlying Tau implementation
```

Those cases need the broader proof-carrying coordination architecture, including order-dependence witnesses, invariant checks, partial orders, and a stated network model.

## The deepest picture

```text
pairwise graph
    asks whether two things conflict

semantic hypergraph
    records the smallest whole sets that conflict

hitting set
    chooses at least one removal from every conflict

global checker
    verifies that the complete remainder is truly safe
```

The lesson is not that every distributed problem is a hypergraph problem.

The lesson is:

> When failure can emerge only from a whole combination, the mathematical object must be able to represent the whole combination.

The next tutorial changes games but keeps the same habit. [Chess and Tetris hide mathematical structures inside play]({{ '/tutorials/chess-tetris-and-the-math-before-math/' | relative_url }}). The first task is to discover which structure the game is actually teaching.

## Sources and further reading

- [The exact reviewed Tau commit](https://github.com/taumorrow/tau-lang-demos/commit/4baf38cbad096fdbe7c41c46e4b41d35c9ba44d2), which motivates the bounded repair.
- [*Keeping CALM: When Distributed Consistency is Easy*](https://arxiv.org/abs/1901.01930), for the monotonicity and coordination boundary in its declared model.
- [*Coordination Avoidance in Database Systems*](https://arxiv.org/abs/1402.2237), for invariant confluence relative to declared transactions and invariants.
- Leslie Lamport, [*Generalized Consensus and Paxos*](https://www.microsoft.com/en-us/research/publication/generalized-consensus-and-paxos/), for the principle that commands need ordering when they interfere rather than merely because they are concurrent.
- Mark H. Liffiton, Alessandro Previti, Ammar Malik, and Joao Marques-Silva, [*Fast, flexible MUS enumeration*](https://doi.org/10.1007/s10601-015-9183-0), for the cost and algorithmics of enumerating minimal inconsistent sets.
- [*Consensus, Decomposed and Reconstructed*]({{ '/reviews/consensus-decomposed-and-reconstructed/' | relative_url }}), the concise peer review that motivated this specialization.
