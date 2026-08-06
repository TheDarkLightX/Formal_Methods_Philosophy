# Decision-Quotient Q Memory v0.1

This experiment applies a representation-learning idea to the compiled Q-table
from the 100-step synthetic utilitarian energy lab. It removes a deployment
symmetry before compression:

    Q(s, a) and Q(s, a) + c(s)
    select the same greedy action.

For each state, the codec stores a quantized common value and quantized
relative advantages. Exact maxima remain zero. Strictly smaller scores are
rounded downward and remain negative. This preserves the source table's
deterministic greedy action, including its tie order.

The report compares the candidate with:

- the raw signed-32 table;
- ordinary zlib;
- a strong lossless Q control that removes deterministic forbidden cells,
  takes temporal deltas, byte-shuffles, and applies zlib;
- a policy-only nibble control that is much smaller but cannot recover the
  scores of alternative actions.

## Reproduce

From the repository root:

    python3 experiments/qgent_rate_structured_memory_v001/rate_structured_memory.py
    python3 experiments/qgent_rate_structured_memory_v001/centroid_feature_probe.py
    python3 experiments/qgent_rate_structured_memory_v001/pca_quadratic_feature_probe.py
    PYTHONPATH=. pytest -q experiments/qgent_rate_structured_memory_v001/test_rate_structured_memory.py

The runner writes:

    assets/downloads/qgent-decision-quotient-q-v1.qdq
    assets/downloads/qgent-pca-quadratic-feature-model-v1.json
    experiments/qgent_rate_structured_memory_v001/results/qgent_rate_structured_memory_v001.report.json
    experiments/qgent_rate_structured_memory_v001/results/qgent_centroid_feature_probe_v001.report.json
    experiments/qgent_rate_structured_memory_v001/results/qgent_pca_quadratic_feature_probe_v001.report.json

## Negative result

The centroid feature probe adds nine distances from a state representation to
optimal-action centroids. It improves all four declared metrics on the
validation split, then worsens all four on a disjoint 40-world confirmation
block. The candidate is rejected, and that confirmation block is now
diagnostic rather than fresh evidence.

## Bounded positive result

The PCA-quadratic probe standardizes 29 state features, learns principal
coordinates from training worlds, and appends pairwise products among the
first coordinates. Validation selected rank 10, which adds 55 quadratic terms
to the 34 original features.

On a separate 40-world confirmation block, the selected 89-feature model
improved all three primary rollout metrics over both the frozen 16-world model
and an equal-data 32-world linear control. It also selected zero forbidden
actions. Exact-action agreement was diagnostic rather than a primary utility
gate, and it improved against both controls on confirmation.

The equal-data control was added after the first confirmation readout. No
candidate was changed afterward. This timing makes the result useful bounded
evidence, but not a fully preregistered comparison. The confirmation seeds are
now consumed and cannot be used to retune another candidate.

## Boundary

The decision-quotient artifact is a lossy encoding of a compiled score table.
It does not improve the learned policy, discover new facts, or justify using
the decoded scores as Bellman targets. The policy-preservation theorem applies
to greedy deployment under the stored admissibility mask.

The PCA-quadratic file is a separate experimental floating-point model. It has
not replaced the deployed quantized Qgent or been integrated into the
Tau-gated demo. All learning claims are limited to disjoint seeds from the same
bounded synthetic generator.
