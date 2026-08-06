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
    python3 experiments/qgent_rate_structured_memory_v001/pca_quadratic_replication.py
    python3 experiments/qgent_rate_structured_memory_v001/pca_quadratic_scaling.py
    python3 experiments/qgent_rate_structured_memory_v001/signal_ladder_memory.py
    PYTHONPATH=. pytest -q experiments/qgent_rate_structured_memory_v001/test_rate_structured_memory.py

The runner writes:

    assets/downloads/qgent-decision-quotient-q-v1.qdq
    assets/downloads/qgent-pca-quadratic-feature-model-v1.json
    assets/downloads/qgent-signal-ladder-q-v1.slq
    experiments/qgent_rate_structured_memory_v001/results/qgent_rate_structured_memory_v001.report.json
    experiments/qgent_rate_structured_memory_v001/results/qgent_centroid_feature_probe_v001.report.json
    experiments/qgent_rate_structured_memory_v001/results/qgent_pca_quadratic_feature_probe_v001.report.json
    experiments/qgent_rate_structured_memory_v001/results/qgent_pca_quadratic_replication_v001.report.json
    experiments/qgent_rate_structured_memory_v001/results/qgent_pca_quadratic_scaling_v001.report.json
    experiments/qgent_rate_structured_memory_v001/results/qgent_signal_ladder_v001.report.json

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

## Preregistered replication

The candidate, both controls, gates, and two untouched seed blocks were then
committed before evaluation. On 80 new worlds from the unchanged generator,
the frozen candidate achieved a mean optimal-utility ratio of 0.985967 and a
minimum ratio of 0.961181. The corresponding results were 0.983952 and
0.921910 for the frozen 16-world linear control, and 0.982591 and 0.925703 for
the equal-data 32-world linear control. The candidate won the paired utility
comparison on 52 of 80 worlds against the first control and 57 of 80 against
the second. It selected no forbidden actions.

A separate 40-world stress block rotated population profiles based on
`[1, 1, 8, 12]`, outside the training range of 2 through 6 per population. The
candidate achieved a mean ratio of 0.968483, compared with 0.844722 and
0.836906 for the controls, and won all 40 paired utility comparisons against
both. This is a single-factor synthetic shift, not evidence of broad
distributional robustness.

Exact-action agreement was not a selection gate. On the primary block, the
candidate's 0.861625 agreement was slightly below the frozen control's
0.862750 while its utility was higher. The experiment therefore supports the
declared utility claim, not a claim that the candidate imitates the exact
policy most often.

## Fixed-capacity scaling result

A second preregistration held the PCA rank and 89-feature capacity fixed while
increasing nested exact training worlds through budgets 8, 16, 32, 64, and
128. The evaluation block contained 100 untouched worlds.

The 128-world model improved mean optimal-utility ratio from 0.986147 to
0.987187 and mean gain over myopic from 2265.11 to 2270.87 relative to the
32-world model. Paired utility outcomes were 53 wins, 34 losses, and 13 ties.
The preregistered scaling gate nevertheless failed for two reasons:

- minimum ratio fell from 0.968479 to 0.957595;
- the two-sided exact sign-test value was 0.053003, above the frozen 0.05
  threshold.

The curve was also not monotone because the 64-world mean was slightly below
the 32-world mean. The exact knowledge-scaling hypothesis is therefore
refuted. More rows improved the average, but did not satisfy the declared
robustness and paired-evidence conditions.

The independent equal-data representation gate passed. At 128 training worlds,
the PCA-quadratic model achieved mean and minimum ratios of 0.987187 and
0.957595, compared with 0.982152 and 0.920826 for the 34-feature linear model.
It won 68 paired comparisons, lost 29, tied 3, and selected no forbidden
action. This supports the tested representation inside this generator, not a
general scaling law.

## Boundary

The decision-quotient artifact is a lossy encoding of a compiled score table.
It does not improve the learned policy, discover new facts, or justify using
the decoded scores as Bellman targets. The policy-preservation theorem applies
to greedy deployment under the stored admissibility mask.

The PCA-quadratic file is a separate experimental floating-point model. It has
not replaced the deployed quantized Qgent or been integrated into the
Tau-gated demo. The primary learning claim is limited to disjoint seeds from
the same bounded synthetic generator. The population-shift claim is limited to
the one preregistered population profile family. The failed fixed-capacity
scaling claim is preserved rather than repaired on its consumed test block.

## Signal-Ladder exact lookup result

The Signal-Ladder experiment returns to a literal lookup-table architecture.
Each row's admissible actions are sorted by exact compiled score. The first
rank layer stores the winner. Each later rank layer stores the next action and
its exact adjacent score gap. A final calibration layer stores the row maximum.

The complete artifact passed every frozen engineering gate:

- an 8,365-byte prefix recovers all 27,000 winning actions exactly;
- a 58,267-byte prefix recovers every winner, runner-up, and exact decision
  margin;
- the 348,692-byte full artifact reconstructs every permitted score and
  forbidden cell exactly;
- duplicate builds were byte-identical;
- wrong-source, wrong-magic, and corrupt-stream mutations were rejected.

The full artifact is larger than the 114,690-byte strong monolithic lossless
payload and the 102,799-byte approximate decision-quotient artifact. Its
benefit is progressive exact access, not total compressed size. The 1,458-byte
policy-only payload is smaller than the first Signal-Ladder prefix because it
does not carry a self-describing header or any path to deeper exact values.

The 60,000-byte top-two threshold was chosen after an exploratory stream-size
probe. The final result is therefore a checked engineering confirmation, not a
fresh statistical discovery or a novelty claim.
