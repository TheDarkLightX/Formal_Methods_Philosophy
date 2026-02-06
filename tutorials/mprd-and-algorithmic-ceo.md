---
title: MPRD and the Algorithmic CEO
layout: docs
kicker: Tutorial 6
description: MPRD turns "model proposes, rules decide" into a checkable control architecture. The algorithmic CEO proposes within bounded menus, while policy gates, invariant rails, and verification decide what executes.
---

This tutorial maps one concrete system to the architecture from [Tutorial 5]({{ '/tutorials/reformulation-and-gates/' | relative_url }}), "propose, then gate with evidence".

The system is **MPRD** (Model Proposes, Rules Decide). The proposer is an **Algorithmic CEO**: a deterministic, IO-free controller that searches a pre-computed decision graph. The gate is **policy evaluation**. In MPRD, the policy artifact is a **Tau specification stored on Tau Net**. **Policy Algebra** is the authoring and certification rail used to build and validate gate logic. The witness loop is an **invariant rail** with counterexample minimization.

The central claim is narrow and testable: MPRD separates candidate generation from execution authority. Better proposers can expand search quality, but they do not gain permission to execute without passing formal gates.

Source scope: the public MPRD repository at [github.com/TheDarkLightX/MPRD](https://github.com/TheDarkLightX/MPRD).

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Mental pictures to keep</p>
  <ul>
    <li>A CEO as a planner with zero execution keys</li>
    <li>A menu graph as a safe decision lattice, traversal is limited to pre-computed edges</li>
    <li>Invariant rails as guardrails on a mountain road: the road is narrow on purpose</li>
    <li>Policy as the gate, represented as Tau specs on Tau Net</li>
    <li>The neuro-symbolic loop from Tutorial 5, realized: propose, gate, witness, refine</li>
  </ul>
</div>

## Part I: the philosophy (intelligence as a commodity, policy as control)

A precise historical analogy is industrial mechanization plus cloud compute. Mechanization made physical labor increasingly schedulable and meterable at scale. Cloud schedulers made compute a governed utility through quotas, admission control, and deterministic execution contracts.

MPRD applies the same structural idea to intelligence output. Candidate generation is treated as abundant, while permission to mutate economic state is treated as scarce and formally governed.

Assumption A (explicit): model inference and search remain cheaper than governance failures. If Assumption A holds, design effort should concentrate on policy gates, execution boundaries, and invariant rails, not on granting proposers direct authority.

This connects directly to two earlier tutorials:

- [Tutorial 4 (world models)]({{ '/tutorials/world-models/' | relative_url }}): a learned system that updates at runtime needs formal rails to prevent drift. If the model can change itself, then something outside the model must define what counts as "out of bounds". MPRD is one answer to that design problem.
- [Tutorial 5, Part VIII (neuro-symbolic gates)]({{ '/tutorials/reformulation-and-gates/' | relative_url }}#part-viii-neuro-symbolic-programming-propose-then-gate-with-evidence): the abstract pattern is "propose, gate, refine". MPRD is the concrete instantiation of that pattern for economic governance.

### The MPRD invariant

The top-level safety property is stated as a universal claim:

$$
\forall \text{executed\_action}.\; Allowed(\text{policy}, \text{state}, \text{action}) = \text{true}
$$

### Exact logic form in MPRD artifacts

In the MPRD repository, the same safety claim appears in a stricter execution form:

$$
\forall p,s,a.\; ExecCalled(p,s,a) \Rightarrow Allowed(p,s,a)
$$

Here, \(p\) is the policy artifact. In the governance deployment described by MPRD, \(p\) is the Tau policy specification stored on Tau Net.

The lifecycle spec then adds two always-invariants:

$$
\Box(\mathrm{verdict} = \mathrm{Denied} \Rightarrow \mathrm{exec} = \mathtt{skipped})
$$

$$
\Box(\mathrm{exec} \in \{\mathtt{success}, \mathtt{failed}\} \Rightarrow \mathrm{proof} = \mathtt{verified})
$$

In the production ZK profile, the execution gate is phrased as:

$$
\operatorname{Execute}(\mathrm{bundle}) \Rightarrow \operatorname{ValidDecision}(\mathrm{bundle}, \mathrm{registry\_state}) = \mathrm{true}
$$

with selector correctness scoped as:

$$
\operatorname{Sel}(\mathrm{policy}, \mathrm{state}, \mathrm{candidates}) = \mathrm{action}
\Rightarrow
\mathrm{action} \in \mathrm{candidates} \land \operatorname{Allowed}(\mathrm{policy}, \mathrm{state}, \mathrm{action})
$$

Plain-text mirror of the same invariants:

```text
InvSafety: ExecCalled(p,s,a) => Allowed(p,s,a)
InvDeniedImpliesSkipped: verdict = Denied => exec = skipped
InvExecRequiresVerified: exec in {success, failed} => proof = verified
InvExecuteRequiresValidDecision: Execute(bundle) => ValidDecision(bundle, registry_state) = true
InvSelectorContract: Sel(policy, state, candidates) = action
                     => action in candidates and Allowed(policy, state, action)
```

This is not a guideline. It is enforced through five architectural constraints:

1. **Proposer isolation.** Models generate candidates without execution capability.
2. **Single execution path.** All actions funnel through one guarded channel.
3. **Token requirement.** Actions execute only with valid governance tokens.
4. **Deterministic minting.** Tokens issue exclusively when rules permit.
5. **Verifiable attestation.** Proofs enable third-party validation without trusting the proposer.

### Three-layer architecture

The architecture separates into three layers with distinct trust profiles:

| Layer | Role | Trust |
|---|---|---|
| **Proposer** | Generates candidate actions | Untrusted, unbounded |
| **Governor (Policy on Tau Net)** | Evaluates candidates against policy | Trusted, bounded, deterministic |
| **Executor** | Performs only approved actions | Guarded, single-path |

The separation matters because it makes the safety claim local: trust depends on the governor and execution boundary, not on the proposer internals. A stronger or more creative proposer does not weaken safety, it can only propose more candidates for the gate to filter.

This is the same principle behind the CEGIS loop from [Tutorial 1, Part IV]({{ '/tutorials/approximate-state-tracking/' | relative_url }}#counterexample-guided-synthesis-cegis): the synthesizer can be arbitrarily creative, because the verifier decides what passes.

## Part II: the Algorithmic CEO (the bounded proposer)

The Algorithmic CEO is a deterministic, IO-free controller. It is a bounded local-search optimizer over a pre-computed **menu graph**.

The word "CEO" is metaphorical. This is not general intelligence. It is a bounded optimizer that searches a finite graph under formal constraints. The metaphor is: a CEO who can suggest moves but cannot act without board approval, and who can only suggest moves that are edges in a pre-approved decision lattice.

### CEO loop in one recurrence

At each step \(t\), the proposer computes:

$$
\text{target}_t = \arg\max_{n \in N_h(x_t)} Score(n, \theta_t), \quad
\text{action}_t = StepTowards(x_t, \text{target}_t)
$$

where \(x_t\) is current state, \(N_h(x_t)\) is the bounded neighborhood of radius \(h\), and \(\theta_t\) is objective configuration.

Execution is then gated by policy:

$$
x_{t+1} =
\begin{cases}
Apply(x_t, \text{action}_t), & Allowed(p_t, x_t, \text{action}_t) \\
x_t, & \text{otherwise}
\end{cases}
$$

This is the key control split: the CEO computes proposals, policy grants authority.

### CEO interface in practice

Per decision epoch, the Algorithmic CEO is a deterministic function:

- **Inputs**: current state snapshot, fixed menu graph, objective configuration, horizon bound.
- **Output**: one `ActionId` (or NOOP) that corresponds to a valid graph edge.
- **No authority**: no direct state mutation and no bypass path around policy evaluation.

This interface is what turns "intelligence as commodity" into an engineering object. Different proposers can be swapped in, but every proposer must emit the same bounded action type and pass the same policy gate.

### Why this is an algorithmic breakthrough

The Algorithmic CEO is not one trick. It is a stack of algorithmic choices that make bounded autonomy practical:

1. **Decision-space compilation.** Continuous controls are compiled into a finite lattice of valid states, so invalid states are unrepresentable.
2. **Geometry shortcut with proof.** A Lean-checked result shows \(L_\infty\) distance equals shortest-path length in the menu graph, removing the need for runtime graph search.
3. **Deterministic total ordering.** Candidate choice is fully deterministic (score, then distance, then key), making runs replayable and auditable.
4. **Numerically safe scoring.** Saturating arithmetic and hard constraint sentinels make objective evaluation fail-bounded.
5. **Scalable planning upgrades.** The simplex extension adds partial-order and symmetry reductions, so larger action spaces remain searchable under fixed budgets.

The net effect is that the CEO behaves like a deterministic solver, not a black-box agent.

### The menu graph

The decision space is pre-computed as a directed graph.

**Nodes** are valid setpoint configurations. In the v6 tokenomics, each node is a `MenuNode` consisting of three bounded parameters:

- **BurnPct**: burn surplus allocation (5,000–9,500 bps, in 100 bps steps, yielding 46 unit values)
- **AuctionPct**: auction surplus allocation (500–5,000 bps, in 100 bps steps, yielding 46 unit values)
- **DripStep**: drip rate (5–100 bps, in 5 bps steps, yielding 20 unit values)

A **split cap** constraint enforces `burn_bps + auction_bps ≤ 10,000`. Nodes that violate the cap are never created.

**Edges** are feasible one-step transitions. Each step changes at most one unit in each dimension (burn, auction, drip), giving 27 possible deltas per node (3 choices per dimension: step up, step down, or hold). An `ActionId` encodes each delta as an index from 0 to 26, with `ActionId(13)` as NOOP.

The graph itself is the safety boundary. You cannot propose a move that is not an edge. The `MenuGraph::generate()` method enumerates all valid lattice points, sorts them canonically by key, and builds the full adjacency matrix. The canonical hash uses domain-separated SHA-256 (`MPRD_CEO_MENU_GRAPH_V1`) for deterministic audit trails.

This is a reformulation move in the sense of [Tutorial 5, Part III]({{ '/tutorials/reformulation-and-gates/' | relative_url }}#decomposition-why-good-interfaces-shrink-both-learning-and-search): a continuous parameter space has been decomposed into a discrete, searchable lattice. The decomposition makes invalid states unrepresentable and search bounded.

### Greedy algorithm

The `GreedyCeo` implements a single-step greedy planner:

1. **Enumerate** reachable nodes within an L∞ ball of radius `horizon` (max 8, giving at most $(2h+1)^3 = 4{,}913$ candidates).
2. **Score** each candidate using a deterministic objective function.
3. **Select** the best target with deterministic tie-breaking: higher score → smaller L∞ distance → smaller L1 distance → smaller key.
4. **Return** one safe step toward the target using `step_towards_key`.

The L∞ distance equals the exact shortest-path length in the safe-menu graph (proved in the Lean artifact `internal/specs/mprd_ceo_menu_shortest_path_proofs.lean`). This means the planner can navigate without running a full graph search: sign-directed one-step movement reaches the target in exactly `dist_inf` steps.

### Pseudocode view

```text
INPUT: state x, objective config θ, horizon h
R := neighborhood(x, h)                // bounded candidate set
best := argmax_total_order(R, Score(·, θ))
return step_towards_key(x, best.key)   // one valid edge
```

The important point is not only optimization quality. The point is that every operation in this loop is bounded, deterministic, and auditable.

### Multi-objective evaluation

Three objective regimes are available:

- **ProfitUtility**: scores based on cashflow, auction revenue, and burn, penalized by risk and churn.
- **OpiFirst**: prioritizes OPI (operator profitability index) health, with a revenue floor constraint.
- **Hybrid**: weighted combination of the two, where `profit_weight_bps + opi_weight_bps = 10,000`.

All scoring uses **saturating arithmetic** (`add_i64_saturating`, `sub_i64_saturating`, `mul_bps_i64`), so overflow produces bounded values rather than panics or wraps. Reserve floor violations and revenue floor violations produce `CONSTRAINT_VIOLATION_SCORE = i64::MIN / 4`, a sentinel that deterministically ranks any violating configuration below all feasible alternatives.

Objective configuration changes are gated by a cooldown: `can_update(now, cooldown_epochs)` rejects updates until enough epochs have elapsed since the last change. This prevents oscillation.

The connection to [Tutorial 5, Part III]({{ '/tutorials/reformulation-and-gates/' | relative_url }}#canonicalizers-and-quotients-remove-redundant-degrees-of-freedom) is that the menu graph decomposes a continuous parameter space into a discrete lattice, and the objective function turns a multi-criteria optimization into a single deterministic score. Both are canonicalization moves that reduce the effective search space.

## Part III: policy gate, Tau storage, and Policy Algebra rail

In MPRD, the gate is the policy itself. The canonical policy artifact is a Tau specification stored on Tau Net. Every state transition on a trust boundary requires explicit, deterministic, fail-closed policy evaluation before execution.

Policy Algebra is the rail around that gate: it structures policy logic, canonicalizes it, and supports certification workflows (including Tau emission and semantic checks).

### AST

The policy expression language is a small, bounded tree:

```
PolicyExpr ::= True | False
             | Atom(name)
             | Not(child)
             | All(children)      -- conjunction
             | Any(children)      -- disjunction
             | Threshold(k, children)
             | DenyIf(name)       -- absorbing veto
```

Bounds are enforced by `PolicyLimits`: max 64 children per node, max 1,024 nodes per tree, max 64-character atom names. These are safety rails against denial-of-service and non-termination, not tokenomics parameters.

### DenyIf as absorbing veto

`DenyIf` is the central safety mechanism. It is evaluated in a separate first phase, before the rest of the tree:

1. **Phase 1**: Extract all `DenyIf` atoms from the entire tree. For each, check the signal. If any `DenyIf` atom is **true** (the dangerous condition holds) or **missing** (the signal is absent), the entire policy evaluates to `DenyVeto`. No further evaluation occurs.
2. **Phase 2**: If all `DenyIf` atoms are false (the dangerous conditions are confirmed absent), evaluate the rest of the tree normally.

This is fail-closed by design. Missing data does not default to "allow". It defaults to "veto".

### 4-valued outcomes

Policy evaluation produces one of four outcomes, not two:

| Outcome | Meaning |
|---|---|
| `Allow` | All conditions met, action permitted |
| `DenySoft` | Normal denial, conditions not met |
| `DenyVeto` | Absorbing veto, DenyIf fired or signal missing |
| `Neutral` | No opinion (used internally for DenyIf atoms in Phase 2) |

This is not standard boolean algebra. Classical laws can fail in the presence of `DenyIf`:

- **Idempotence can fail**: `All([DenyIf("x"), DenyIf("x")])` is not the same as `DenyIf("x")` in all contexts, because the tree structure affects Phase 1 collection.
- **Excluded middle can fail**: `Any([Atom("x"), Not(Atom("x"))])` need not be `Allow` if a `DenyIf` elsewhere fires first.
- **Non-contradiction can fail**: the 4-valued output means a policy can be neither `Allow` nor `DenySoft`, it can be `DenyVeto` or `Neutral`.

This is intentional. Safety overrides algebraic convenience. The evaluation semantics are designed so that no composition of `Allow`-producing sub-policies can override a `DenyVeto`.

### Canonicalization and hashing

The `CanonicalPolicy` type normalizes policy expressions into a stable canonical form:

- **Flatten** nested `All`/`Any` (associativity).
- **Remove** identity elements (`True` in `All`, `False` in `Any`).
- **Eliminate** contradictions and complements (only when no `DenyIf` is present, safety-preserving).
- **Absorb** redundant sub-expressions.
- **Sort** children by `deny_if_rank` then by encoded bytes, giving a total canonical order.
- **Deduplicate** children in `All`/`Any`; preserve multiplicity in `Threshold`.

The canonical form is then serialized and hashed with domain separation. Two policies that are semantically equivalent under the 4-valued semantics will have the same canonical hash. This enables deterministic audit trails: if a policy changes, the hash changes, and a diff with concrete counterexample inputs can be produced automatically.

This is canonicalization in the sense of [Tutorial 5, Part III]({{ '/tutorials/reformulation-and-gates/' | relative_url }}#canonicalizers-and-quotients-remove-redundant-degrees-of-freedom): pick one representative per equivalence class, so comparison and search work on unique representatives instead of redundant variants.

### Concrete example: the CEO gate

Before the Algorithmic CEO can change tokenomics parameters, its proposed action must pass through a policy gate. A typical gate policy might look like:

```
All([
  Atom("opi_healthy"),         -- OPI above threshold
  Atom("reserve_sufficient"),  -- reserve covers floor
  Atom("cooldown_elapsed"),    -- enough epochs since last change
  DenyIf("emergency_freeze")  -- absolute veto if emergency detected
])
```

If `emergency_freeze` is true, or if its signal is missing, the entire policy evaluates to `DenyVeto`, regardless of whether OPI is healthy, reserves are sufficient, and cooldown has elapsed. The `DenyIf` absorbs everything.

The `PolicyGateV6` trait defines the interface:

```rust
pub trait PolicyGateV6 {
    fn check(&self, eng: &TokenomicsV6, action: &ActionV6) -> Result<()>;
}
```

An `Err` result means the action is denied. The executor will not proceed.

## Part IV: invariant rails and counterexample minimization

### The invariant rail

The invariant rail runs after every state transition. It checks three categories of properties:

**1. No mutation on error.** If an action returns `Err`, the state hash must not change. If it did, the engine violated its own contract.

**2. Tokenomics invariants.** After every successful action, `TokenomicsV6::check_invariants_v1` validates engine-level properties (balance conservation, bound consistency, etc.).

**3. Transition-level conservation.** Specific action outcomes must satisfy conservation laws. For example, after `SettleOpsPayroll`:

$$
\text{payout\_total} + \text{carry\_to\_reserve} = \text{ops\_payroll\_pool}
$$

If any invariant fails, the rail returns an `InvariantCounterexampleV6` containing the violation ID, the step index, the state hash, and the full action trace.

This connects to the counterexample analysis from [Tutorial 1, Part IV]({{ '/tutorials/approximate-state-tracking/' | relative_url }}#counterexample-guided-synthesis-cegis): a single concrete trace that violates an "always" claim is the most informative kind of failure evidence.

### Counterexample minimization

When a violation is found, the trace may be longer than necessary. The `minimize_counterexample_v1` function reduces it to a minimal failing trace using deterministic delta-debugging:

1. **Verify** the provided trace reproduces the violation.
2. **Initialize** chunk size $n = 2$.
3. **Loop**: divide the action sequence into $n$ chunks. For each chunk, try removing it. If the reduced trace still triggers the same invariant ID:
   - Accept the reduction.
   - Reset chunk size toward 2.
   - Restart.
4. If no chunk removal preserves the violation, double $n$ (up to sequence length).
5. Return the minimized counterexample.

The result is a minimal witness: the shortest sub-trace that triggers the specific invariant violation. This is the "minimized witness" concept from [Tutorial 1, Part V]({{ '/tutorials/approximate-state-tracking/' | relative_url }}#zooming-out-counterexample-analysis-and-what-it-gives-you): a counterexample becomes more useful when it carries less irrelevant context.

### Testing strategy: LTLf and bounded model checking

The invariant rail is complemented by temporal property checking using **LTLf (Linear Temporal Logic over finite traces)** with **bounded model checking (BMC)**.

The `ltlf` module implements a minimal LTLf monitor with:

- **Formula constructors**: `always(φ)`, `eventually(φ)`, `until(φ, ψ)`, `release(φ, ψ)`, `next(φ)`, `weak_next(φ)`.
- **Progression semantics**: `progress(f, valuation)` advances a formula by one step.
- **BMC**: `bmc_find_violation(spec, initial, max_steps, step)` performs explicit-state search for counterexample traces.
- **Best-effort synthesis**: `synthesize_bounded(spec, initial, max_steps, actions, step)` implements a two-player game between the system and an adversarial environment, producing `Guaranteed`, `Possible`, or `Impossible` verdicts.

Concrete temporal properties tested against the tokenomics engine include:

- **Settlement ordering**: settlements must precede certain epoch-close operations.
- **No mutation on error**: temporal invariant version of the per-step check.
- **Epoch-close forbids open actions**: after settlements close an epoch, drip and service actions must fail.

The synthesis mode distinguishes between **deterministic** environments (where the system controls all choices) and **adversarial** environments (where some steps may fail non-deterministically). A `Guaranteed` verdict means the spec holds against all environment choices. A `Possible` verdict means the spec holds along some path but not all.

This connects to [Tutorial 3 (Tau specifications)]({{ '/tutorials/tau-language/' | relative_url }}): Tau specs define what must hold at every step, and the temporal checker searches for violations.

## Part V: simplex planning (bounded-horizon search with symmetry)

The simplex CEO extends the greedy CEO to multi-step planning over a generalized k-way allocation.

### k-way simplex

In the simplex model, allocations are a bounded vector of $k$ non-negative integers, each capped individually, optionally constrained to sum to a constant $T$. Actions are **transfers**: move one unit from bucket $i$ to bucket $j$, subject to:

- Source has at least 1 unit: $x[\text{src}] > 0$
- Destination is below cap: $x[\text{dst}] < \text{cap}[\text{dst}]$

If a transfer is disabled (preconditions not met), it acts as a no-op. The sum is preserved by construction, every transfer subtracts 1 from one bucket and adds 1 to another. This is **correct by construction (CBC)**: invalid states are unrepresentable because the transfer semantics make it impossible to violate the sum constraint or the per-bucket bounds.

For $k$ buckets with total $T$, the number of distinct states is the stars-and-bars count $\binom{T+k-1}{k-1}$, further reduced by per-bucket caps. For 3–4 buckets with moderate totals, this is manageable. Beyond that, coarser granularity or symmetry reduction is needed.

### Three planning modes

The simplex planner supports three modes, each a reformulation insight:

**TracePor** (Mazurkiewicz-style partial-order reduction):

Two transfers **commute** if executing them in either order produces the same state. The POR oracle `stable_enabled_ineq` gives a closed-form sufficient condition:

- If two transfers share a source, we need at least 2 units there so both can fire independently.
- If two transfers share a destination, we need at least 2 slack (cap minus current) so both can fit.

When transfers commute, only one ordering needs to be explored. TracePor canonicalizes traces by certified swaps: given a trace of transfers, rebuild it by inserting each new action at the canonical position (determined by the independence oracle). The canonical trace represents an equivalence class of all orderings that produce the same final state.

This is canonicalization from [Tutorial 5, Part III]({{ '/tutorials/reformulation-and-gates/' | relative_url }}#canonicalizers-and-quotients-remove-redundant-degrees-of-freedom) applied to action sequences: many execution orders that reach the same state are collapsed to one canonical representative, and search only visits representatives.

**StateSymmetry** (quotient by symmetry classes):

When buckets are **interchangeable**, same cap, same objective weight, same role, the state space can be quotiented by permutations within each class. The `symmetry_key` function computes a canonical key:

1. Group buckets by `(cap, weight)`.
2. Within each group, sort the bucket values.
3. The sorted group vectors form the canonical key.

Two states that differ only by a permutation of interchangeable buckets will have the same key. Search visits one representative per equivalence class.

This is the quotient search from [Tutorial 5, Part III]({{ '/tutorials/reformulation-and-gates/' | relative_url }}#canonicalizers-and-quotients-remove-redundant-degrees-of-freedom): instead of searching raw states, search equivalence classes.

**AmplePorDfsC2** (depth-first with ample-set POR and C2 cycle proviso):

This mode uses a more aggressive POR strategy with depth-first search:

- At each state, compute an **ample set**: a subset of enabled actions sufficient to represent all behaviors (under the POR independence assumptions).
- Use a **DFS stack** to detect cycles and apply the C2 proviso: if a cycle would be created, expand the ample set to full to avoid missing reachable states.
- A **safety visibility contract** prevents reduction at states where any enabled action would change the linear objective score, ensuring the optimization criterion is fully visible to the planner.

Five ample-set strategies are implemented (`None`, `MinOnly`, `MinPlusDependentsOfMin`, `MinPlusDependencyClosure`, `DfsC2`), with exhaustive bounded counterexample mining to validate each.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Assumption hygiene: POR soundness is bounded, not universal</p>
  <p>
    The simplex ample-set module explicitly states: "This module makes <em>no</em> global soundness claim by default. Any pruning rule must be validated by (a) bounded exhaustive checks and/or (b) Lean proofs."
    Tests include dedicated counterexample miners that compare POR-reduced reachability against full reachability on small instances. Some strategies (<code>MinOnly</code>, <code>MinPlusDependencyClosure</code>) have known counterexamples and are not promoted.
  </p>
</div>

### Bounded exploration

All planning modes are bounded by two parameters:

- **Horizon**: maximum depth of the search.
- **Expansion budget**: maximum number of states expanded.

The planner terminates deterministically when either bound is reached. Tie-breaking for the best plan follows the same total order as the greedy CEO: score descending → depth ascending → first-action key ascending → target state lexicographic ascending.

### Combinatorics and the connection to VC dimension

For $k$ buckets with total $T$, the unreduced state count is $\binom{T+k-1}{k-1}$. For 3 buckets with $T=10{,}000$ bps, that is $\binom{10002}{2} = 50{,}015{,}001$ states, tractable with POR but large enough to motivate symmetry reduction. For 4 buckets, it grows to $\binom{10003}{3} \approx 1.67 \times 10^{11}$, which requires coarser granularity or aggressive quotienting.

This connects to the hypothesis space analysis from [Tutorial 5, Part III]({{ '/tutorials/reformulation-and-gates/' | relative_url }}#vc-dimension-and-shattering-what-the-definition-checks): the effective size of the search space determines how much evidence (search budget) is needed to find a good plan, and reformulation techniques (POR, symmetry) reduce that effective size without losing reachable optima.

## Part VI: the link back (MPRD as the neuro-symbolic loop, realized)

[Tutorial 5, Part VIII]({{ '/tutorials/reformulation-and-gates/' | relative_url }}#part-viii-neuro-symbolic-programming-propose-then-gate-with-evidence) defined the neuro-symbolic gate as an architecture:

> A model proposes candidates. A formal checker decides which candidates are allowed, and returns counterexamples when a candidate is wrong.

MPRD is this pattern instantiated for economic governance:

| Loop role | MPRD component |
|---|---|
| **Proposer** | Algorithmic CEO (greedy/simplex planner over menu graph) |
| **Gate** | Policy evaluation (Tau policy on Tau Net, fail-closed) |
| **Witness** | Invariant rail violation (minimized counterexample trace) |
| **Refinement** | PID controllers adjusting setpoints toward objectives |

### The safety controller as Simplex architecture

The `SafetyController` implements a constrained PID loop:

- **Normal operation**: given setpoints (target burn, auction, drip) from the CEO or external input, compute a one-step action toward the target, constrained to valid graph transitions.
- **Fallback**: if the state is corrupted or the graph version mismatches, fall back to NOOP, do nothing rather than do something wrong.
- **Split cap enforcement**: after PID computation, `enforce_split_cap_preserve_burn` ensures the resulting allocation respects the global constraint, favoring burn preservation.

This is a Simplex-style architecture (in the control-theory sense): a normal controller proposes, a safety controller constrains the proposal to the valid operating region, and a fallback ensures graceful degradation.

### What MPRD adds beyond the abstract pattern

The abstract "propose, gate, witness" loop from Tutorial 5 is a template. MPRD fills it in with specific engineering choices:

**1. The decision space is pre-computed.**
The menu graph is generated once and its canonical hash is fixed. The CEO searches within this graph, not over an unbounded space. This is the difference between "propose anything and let the gate filter" and "propose only from a pre-validated lattice and let the gate confirm".

**2. Policy is owned by Tau Net, not by operators.**
The separation is not just proposer-vs-gate but also governance-of-policy-vs-governance-of-operations. Policy changes go through their own governance path (committee quorum, timelock, escalation), distinct from the CEO's operating path.

**3. Proofs are machine-checked.**
Lean 4 artifacts prove properties of the menu graph geometry and simplex POR. Kani harnesses verify Rust kernel invariants. ROBDD certification verifies policy algebra semantics. This is not "we tested it", it is "a proof assistant checked the claim".

**4. Everything is deterministic and IO-free at the kernel.**
The CEO, the policy evaluator, and the invariant rail perform no I/O, no randomness, and no floating-point arithmetic. Audit trails are reproducible from first principles: given the same inputs, the same outputs are guaranteed.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Assumption hygiene: what the CEO is and is not</p>
  <p>
    The Algorithmic CEO is not general intelligence. It is a bounded optimizer searching a pre-computed graph under formal constraints. The safety claim is scoped and explicit: actions that pass through the governor satisfy the policy at evaluation time. The system does not claim that the policy is complete (it might miss hazards), that the objective is correct (it might optimize the wrong thing), or that external inputs are trustworthy (they might be manipulated).
  </p>
  <p>
    These are explicitly documented as assumptions A1–A4 in the MPRD repository. The engineering response is not to wish the assumptions away, but to stress-test them: policy diffs with counterexamples, oracle lockstep checks, symmetry class validation, and signed state attestations.
  </p>
</div>

## Part VII: what is proved, what is empirical, what is exploratory

MPRD maintains explicit boundaries between three evidence categories:

**Machine-checked formal claims:**
- Lean theorem bundles for CEO simplex POR (commutation conditions, swap-equivalence invariance, trace canonicalization invariance, reachability equivalence under canonicalization).
- Lean artifact for v6 menu shortest-path geometry (L∞ distance equals shortest-path length).
- Kani harnesses for Rust verified kernels (no-mutation-on-error, conservation laws, anti-replay).
- ROBDD certification for policy algebra (semantic hashing, semantic diff with concrete counterexamples).

One precision: the simplex POR Lean artifact explicitly notes a disjoint-endpoint commutation lemma as an axiom. This is a named remaining proof obligation, not a gap swept under the rug.

**Deterministic empirical rails:**
- Bounded exhaustive sweeps comparing POR-reduced reachability against full reachability on small instances.
- Counterexample miners that actively search for strategy failures.
- CI-style scripts (`check_ceo_simplex_rail.sh`) that verify oracle definitions match formal predicates.

**Exploratory modeling:**
- Simulation tools (e.g., `ceo_simulation.py`) explicitly marked as "IDEA-ONLY".
- Strategy comparison notebooks for studying controller behavior under scenarios.

Keeping these categories separate prevents a failure mode discussed in [Tutorial 5, Part VII (the Lighthill report)]({{ '/tutorials/reformulation-and-gates/' | relative_url }}#part-vii-the-lighthill-report-a-warning-about-demos-without-guarantees): treating simulation success as a proof.

## References

- MPRD repository: <https://github.com/TheDarkLightX/MPRD>
- MPRD README (core invariant and architecture): <https://github.com/TheDarkLightX/MPRD/blob/main/README.md>
- Algorithmic CEO menu modes: <https://github.com/TheDarkLightX/MPRD/blob/main/docs/CEO_MENU_MODES.md>
- CEO simplex POR integration: <https://github.com/TheDarkLightX/MPRD/blob/main/docs/CEO_SIMPLEX_POR_INTEGRATION.md>
- Policy algebra: <https://github.com/TheDarkLightX/MPRD/blob/main/docs/POLICY_ALGEBRA.md>
- Policy certification rail: <https://github.com/TheDarkLightX/MPRD/blob/main/docs/POLICY_CERTIFICATION.md>
- Production ZK and registry-bound verification: <https://github.com/TheDarkLightX/MPRD/blob/main/docs/PRODUCTION_ZK.md>
- [Tutorial 1: Approximate state tracking]({{ '/tutorials/approximate-state-tracking/' | relative_url }}), counterexamples, CEGIS, minimized witnesses
- [Tutorial 3: Tau Language]({{ '/tutorials/tau-language/' | relative_url }}), executable policy semantics
- [Tutorial 4: World models and continuous learning]({{ '/tutorials/world-models/' | relative_url }}), adaptation versus drift, formal rails for learning systems
- [Tutorial 5: Reformulation and compression]({{ '/tutorials/reformulation-and-gates/' | relative_url }}), neuro-symbolic gates, canonicalization, decomposition, VC dimension
