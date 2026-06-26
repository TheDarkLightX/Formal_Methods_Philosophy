---
title: "From False Greedy Theorem to Exact Cross-Pool Routing Oracle"
layout: docs
kicker: Research log
description: "A ZenoDEX research arc: adversarial falsification of a greedy cross-pool routing theorem, the subset-DP exact oracle that replaced it, and the remaining 2^n frontier."
date: 2026-06-26
---

## Abstract

This note records a ZenoDEX research arc in adversarial falsification, dynamic
programming, and scoped algorithm design.

The original conjecture was attractive: for cross-pool batch clearing, split
each intent against current reserves and total output should dominate the
two-phase snapshot decomposition. Moderate random testing supported it. An
adversarial falsification suite broke it.

The failure was useful. It exposed the real problem: greedy per-intent routing
does not compose when each split changes the reserves seen by later intents.
The corrected route was an exact subset-DP oracle for same-direction exact-in
intents over two discrete CPMM pools. It changes the search from explicit
ordering enumeration to subset-lattice exploration:

```text
O(n! * |S| * D)  ->  O(2^n * n * |S| * D)
```

For small and medium batches, that is enough to turn an intractable exact
comparison into a usable advisory oracle. It remains exponential in the number
of distinct intents. The current contribution is a scoped algorithm-engineering
result with replay evidence, not a general mathematical proof of unrestricted
cross-pool optimality.

## The Setting

ZenoDEX clears batches of swap intents against constant-product market maker
(CPMM) pools. When two parallel pools exist for the same asset pair, a natural
implementation splits each intent across pools against a reserve snapshot, then
clears the assigned legs pool by pool.

The snapshot is stale by construction. If intent A moves pool 0's price, intent
B's split was still computed against the pre-A reserves. If A depleted pool 0,
B may route too much to the now-shallow pool and receive worse execution.

The starting question was:

```text
Is two-phase decomposition optimal, or does stale reserve splitting leave
output on the table?
```

## Act I: A Plausible Greedy Theorem

The first hypothesis was a greedy dominance claim.

```text
CPSS-BC dominance, informal:
For any batch of intents and any pool configuration, processing each intent
sequentially against current reserves, with an optimal split at each step,
produces total output at least as high as the two-phase decomposition.
```

The argument seemed clean. A one-step lemma is true: for a single intent,
splitting against current reserves is at least as good as executing a stale
split against those same current reserves. The stale split is feasible, and the
current-reserve optimizer chooses the best feasible split.

The mistaken step was the induction. A 15,000-trial moderate-parameter suite
found no violations and many strict wins. The theorem looked ready to promote.

## Act II: Falsification

The falsification gate required a more hostile distribution before promotion.
The moderate suite used ordinary reserves and low fees. The adversarial suite
expanded to tiny reserves, huge reserves, and fees as high as 9999 bps.

It found counterexamples.

```text
Violations: 10 / 50,000 adversarial trials
Worst delta: -6
```

One representative case:

```text
pools = [(1, 1000, 10), (50, 10000, 5000)]
intents = [32, 20, 235, 332, 392]

Decomposition output = 9303
Greedy sequential output = 9297
delta = -6
```

The per-step lemma survived. The induction failed. After a greedy fresh split,
the resulting reserves can be worse for a later intent than the decomposition's
reserves. A locally optimal split may drain the pool that a future intent needs.

That is the core lesson:

```text
locally optimal split at each step
does not imply
globally optimal reserve trajectory
```

The true joint optimum sometimes sacrifices output on an early intent to keep a
pool deep for a later intent.

## Act III: The Corrected Algorithm

The first corrected algorithm was exhaustive and exact. For each ordering, it
searched early splits and used a simple final-step fact:

```text
Last-intent optimality:
The last intent in a fixed ordering should be split optimally against the
current reserves, because no future intent can benefit from a sacrifice.
```

That gives an exact reference algorithm, but it still carries the factorial
ordering barrier. For `n=10`, there are 3,628,800 orderings before considering
the split domain.

This was a correctness baseline, not the final answer.

## Act IV: The Subset-DP Breakthrough

The breakthrough was to replace explicit ordering search with a subset DP.

For two pools, define:

```text
subset = processed intent bitmask
a      = total input sent to pool 0 so far
y0r    = current output reserve of pool 0
t      = total output accumulated so far
```

Given `subset`, `a`, `y0r`, and the retained DP value `t`, both pool states are
determined:

```text
x0'  = x0 + a
x1'  = x1 + (S_subset - a)
y1r  = y1 - t + (y0 - y0r)
```

The subset DP state is:

```text
dp[subset][(a, y0r)] = max total output t
```

The transition tries every unprocessed intent and every feasible split:

```text
for each unprocessed intent i:
  for split b in [0, amount_i]:
    out0 = q(x0 + a, y0r, b, fee0)
    out1 = q(x1 + S_subset - a, y1r, amount_i - b, fee1)
    update dp[subset union {i}][(a + b, y0r - out0)]
```

This explores every ordering implicitly through the subset lattice.

```text
explicit ordering search: O(n! * |S| * D)
subset DP search        : O(2^n * n * |S| * D)
```

For `n=10`, `|S|=100`, and `D=100`, the rough comparison is:

```text
Anticipatory reference: about 360M transition-scale evaluations
Subset DP            : about 10M transition-scale evaluations
```

The exact constants depend on the reachable state count, but the qualitative
change is clear: the factorial factor is gone.

## Why the Compressed State Is Plausible

The compressed key omits pool 1's output reserve `y1r`. That looks dangerous at
first, because future output from pool 1 depends on `y1r`.

The conservation identity reconstructs it for the retained path:

```text
y1r = y1 - t + (y0 - y0r)
```

If two paths collide on `(subset, a, y0r)`, the path with larger retained output
has lower reconstructed `y1r`. The pruning rule keeps the larger `t`. The proof
obligation is that the retained output advantage covers any future advantage
the discarded path could obtain from its higher pool-1 reserve.

The implementation includes a full-state reference oracle that keeps
`(subset, a, y0r, y1r)` and compares it against the compressed solver on
hostile cases. That gives pressure evidence for the pruning rule. A machine
proof of the pruning theorem remains future work.

## Evidence

The ZenoDEX repository currently includes:

- a compressed subset-DP solver,
- a full-state reference oracle,
- a factorial brute-force oracle for small cases,
- a deterministic witness script,
- focused pytest regressions,
- a benchmark script,
- an advisory wrapper and CLI.

The checked local evidence includes:

| Check | Result |
|---|---:|
| Subset DP vs brute force, 3-intent moderate corpus | 500 / 500 match |
| Subset DP vs brute force, 4-intent moderate corpus | 100 / 100 match |
| Subset DP vs brute force, 3-intent adversarial corpus | 2,000 / 2,000 match |
| Compressed DP vs full-state oracle | 226 / 226 match |
| Advisor and core pytest checks | 10 / 10 passed |

One high-collision regression has:

```text
pool0   = (5, 10, 5000)
pool1   = (2, 1000, 5000)
intents = [4, 6, 5, 3, 7]

compressed oracle output = 780
full-state oracle output = 780
```

The full-state oracle reports compressed-key collisions in this case, so it
directly pressures the pruning rule.

## Generalizations

The research run also explored extensions.

### k-Pool Subset DP

For `k` pools, the state expands to track the first `k-1` pools, with the last
pool determined by conservation:

```text
(subset, a_0, ..., a_{k-2}, y0r_0, ..., y0r_{k-2})
```

The inner split enumeration costs `O(D^(k-1))` per state. This is exact in the
modeled domain but quickly becomes expensive as `k` and `D` grow.

### Multi-Set DP

When many intents have the same amount, the identities of those intents can be
quotiented away. If the amount classes have counts `c_d`, the subset factor can
drop from:

```text
2^n
```

to:

```text
product over d of (c_d + 1)
```

This is valuable for repeated-size batches, because duplicate amounts become a
real compression object.

### Beam Search

A beam-search variant keeps only the top `K` states per level. It scales much
further, and the local experiments found near-exact behavior under some
settings. It remains a heuristic unless every discarded state is justified by a
sound dominance rule.

## The 2^n Frontier

The subset DP removes the factorial barrier and leaves the subset barrier.
Several attempted reductions did not produce an exact polynomial algorithm:

- meet-in-the-middle lost optimal interleavings,
- fixed chunks lost cross-chunk orderings,
- same-`a` dominance pruned very little,
- invariant-based dominance became unsound under fees,
- marginal-rate dominance was too rare,
- continuous-guided splitting failed on large or high-fee domains.

There is strong computational evidence that the subset identity matters. Random
and constructed cases force many different processed subsets to appear on
optimal paths. This supports the working belief that the `2^n` factor is a real
barrier for the general all-distinct case.

That statement is intentionally scoped. A formal lower bound would need a clean
problem model and reduction. The current result is evidence-guided algorithm
engineering, not a proved complexity lower bound.

## The Advisory Oracle

The subset DP is implemented as a bounded research and UX advisory oracle. It
reports:

- the exact modeled optimum for a given two-pool, exact-in batch,
- an optional candidate route's missed output,
- the candidate gap in basis points,
- solver-cost telemetry,
- explicit non-authority flags.

The packet includes:

```text
production_security_claim = false
settlement_authority = false
solver_authorizes_settlement = false
```

If the exact-search limits are exceeded, it returns `exact_unavailable` with no
exact output. The verifier or settlement path remains authoritative.

The known counterexample:

```text
pool0   = (1, 2, 0)
pool1   = (2, 2, 0)
intents = [1, 1, 2]
candidate_amount_out_total = 1
```

reports:

```text
exact_amount_out_total = 2
missed_output          = 1
candidate_gap_bps      = 5000
```

That is the practical UX value: a candidate route can be compared against a
bounded exact oracle, and the missed output can be shown directly.

## Honest Limits

The exact claim is narrow:

```text
For same-direction exact-in intents routed across two discrete CPMM pools,
the compressed subset-DP state appears sufficient for exact joint batch
optimization on the tested bounds, with brute-force and full-state oracle
pressure supporting the pruning rule.
```

The remaining limits matter:

- The compressed-state pruning rule still needs a formal proof.
- The algorithm is exponential in the number of distinct intents.
- The implementation is an advisory oracle, not settlement authority.
- Exact-out intents are outside the current model.
- k-pool and multi-set extensions should be documented with their own evidence
  bundles before being treated as equally mature.

## The Research Arc

The sequence was the important part:

1. State a plausible greedy theorem.
2. Test it on moderate random cases.
3. Require adversarial falsification before promotion.
4. Find counterexamples.
5. Explain the failure mode.
6. Build an exact but expensive corrected oracle.
7. Compress the factorial ordering search into subset DP.
8. Pressure-test the compressed state against brute-force and full-state
   oracles.
9. Productize the result as a fail-closed advisory comparator.
10. Record the remaining frontier rather than inflating the claim.

The falsification gate did the decisive work. It prevented a false theorem from
being promoted and forced the research loop toward a better object. The subset
DP is the algorithmic reward for taking the counterexample seriously.

## Reproduction Pointers

The implementation and evidence live in the ZenoDEX repository:

```text
src/core/cross_pool_subset_dp.py
src/agents/cross_pool_subset_dp_advisor.py
tools/cross_pool_subset_dp_advisor.py
tools/benchmark_cross_pool_subset_dp.py
docs/research/cpss_bc_witness.py
```

Useful replay commands:

```bash
python3 docs/research/cpss_bc_witness.py
pytest -q tests/agents/test_cross_pool_subset_dp_advisor.py tests/core/test_cross_pool_subset_dp.py
python3 tools/benchmark_cross_pool_subset_dp.py
```

The public lesson is broader than the DEX-specific algorithm: when an apparently
clean greedy proof depends on a reserve trajectory, adversarial state divergence
is the first place to look for the counterexample.
