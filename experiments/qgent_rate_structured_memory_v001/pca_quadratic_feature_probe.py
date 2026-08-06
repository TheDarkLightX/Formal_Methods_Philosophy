"""Replay the frozen PCA-quadratic Qgent representation experiment.

Candidate ranks and training budgets were selected on the original validation
split. The disjoint 40-world confirmation block was then evaluated once. A
plain 32-world linear control was added after that first readout to distinguish
the representation from the larger training budget. No candidate was changed
after confirmation was observed.

The confirmation seeds are now consumed evidence. They must not be used to
retune this or a successor model.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.qgent_rate_structured_memory_v001 import (
    centroid_feature_probe as negative_probe,
)
from experiments.qgent_utilitarian_energy_v001 import (
    utilitarian_energy_lab as qgent,
)

REPORT_SCHEMA = "qgent-pca-quadratic-feature-probe-v1"
MODEL_SCHEMA = "qgent-pca-quadratic-action-conditional-energy-v1"
DEFAULT_REPORT = (
    Path(__file__).with_name("results")
    / "qgent_pca_quadratic_feature_probe_v001.report.json"
)
DEFAULT_MODEL = (
    ROOT
    / "assets"
    / "downloads"
    / "qgent-pca-quadratic-feature-model-v1.json"
)
MAX_RANK = 10
RANKS = (2, 4, 6, 8, 10)
TRAINING_BUDGETS = (16, 32)
CONFIRMATION_SEEDS = tuple(range(810_000, 810_040))


@dataclass(frozen=True)
class Dataset:
    worlds: tuple[negative_probe.PreparedWorld, ...]
    state_rows: np.ndarray
    action_base: tuple[np.ndarray, ...]
    action_targets: tuple[np.ndarray, ...]
    action_weights: tuple[np.ndarray, ...]
    action_state_indices: tuple[np.ndarray, ...]


@dataclass(frozen=True)
class Encoder:
    mean: np.ndarray
    scale: np.ndarray
    components: np.ndarray
    pairs: tuple[tuple[int, int], ...]
    extra_mean: np.ndarray
    extra_scale: np.ndarray

    def normalized_state(
        self,
        scenario: qgent.Scenario,
        context: qgent.ScenarioFeatures,
        day: int,
        state: qgent.State,
    ) -> np.ndarray:
        raw = qgent.feature_vector(
            scenario,
            context,
            day,
            state,
            qgent.HOLD,
        )[negative_probe.STATE_FEATURE_INDICES].astype(np.float64)
        raw /= qgent.FEATURE_SCALE
        return (raw - self.mean) / self.scale

    def all_extras(self, normalized: np.ndarray) -> np.ndarray:
        z = normalized @ self.components.T
        raw = np.asarray([z[i] * z[j] for i, j in self.pairs])
        return (raw - self.extra_mean) / self.extra_scale

    def indices(self, rank: int) -> np.ndarray:
        return np.asarray(
            [
                index
                for index, (i, j) in enumerate(self.pairs)
                if i < rank and j < rank
            ],
            dtype=np.int64,
        )


@dataclass(frozen=True)
class Model:
    encoder: Encoder
    rank: int
    weights: tuple[np.ndarray, ...]
    training_worlds: int
    training_examples: int


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def build_dataset(
    worlds: Sequence[negative_probe.PreparedWorld],
) -> Dataset:
    state_rows: list[np.ndarray] = []
    action_base: list[list[np.ndarray]] = [
        [] for _ in range(qgent.ACTION_COUNT)
    ]
    action_targets: list[list[float]] = [
        [] for _ in range(qgent.ACTION_COUNT)
    ]
    action_weights: list[list[float]] = [
        [] for _ in range(qgent.ACTION_COUNT)
    ]
    action_state_indices: list[list[int]] = [
        [] for _ in range(qgent.ACTION_COUNT)
    ]
    for world in worlds:
        for day, budget, capacity, reserve in world.states:
            state = (budget, capacity, reserve)
            state_index = len(state_rows)
            raw_state = qgent.feature_vector(
                world.scenario,
                world.context,
                day,
                state,
                qgent.HOLD,
            )[negative_probe.STATE_FEATURE_INDICES].astype(np.float64)
            state_rows.append(raw_state / qgent.FEATURE_SCALE)
            exact_row = world.exact_q[(day, *state)]
            allowed = qgent.allowed_actions(state)
            best = max(int(exact_row[action]) for action in allowed)
            for action in allowed:
                base = qgent.feature_vector(
                    world.scenario,
                    world.context,
                    day,
                    state,
                    action,
                ).astype(np.float64)
                base /= qgent.FEATURE_SCALE
                target = float(int(exact_row[action]) - best)
                action_base[action].append(base)
                action_targets[action].append(target)
                action_weights[action].append(
                    2.0 if -20 <= target < 0 else 1.0
                )
                action_state_indices[action].append(state_index)
    return Dataset(
        worlds=tuple(worlds),
        state_rows=np.vstack(state_rows),
        action_base=tuple(np.vstack(items) for items in action_base),
        action_targets=tuple(
            np.asarray(items, dtype=np.float64)
            for items in action_targets
        ),
        action_weights=tuple(
            np.asarray(items, dtype=np.float64)
            for items in action_weights
        ),
        action_state_indices=tuple(
            np.asarray(items, dtype=np.int64)
            for items in action_state_indices
        ),
    )


def raw_quadratics(
    z: np.ndarray,
    pairs: tuple[tuple[int, int], ...],
) -> np.ndarray:
    return np.column_stack([z[:, i] * z[:, j] for i, j in pairs])


def fit_encoder(state_rows: np.ndarray) -> Encoder:
    mean = state_rows.mean(axis=0)
    scale = state_rows.std(axis=0)
    scale[scale < 1e-9] = 1.0
    normalized = (state_rows - mean) / scale
    covariance = normalized.T @ normalized / len(normalized)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    components = eigenvectors[:, order[:MAX_RANK]].T
    z = normalized @ components.T
    pairs = tuple(
        (i, j)
        for i in range(MAX_RANK)
        for j in range(i, MAX_RANK)
    )
    raw = raw_quadratics(z, pairs)
    extra_mean = raw.mean(axis=0)
    extra_scale = raw.std(axis=0)
    extra_scale[extra_scale < 1e-9] = 1.0
    return Encoder(
        mean=mean,
        scale=scale,
        components=components,
        pairs=pairs,
        extra_mean=extra_mean,
        extra_scale=extra_scale,
    )


def fit_model(dataset: Dataset, encoder: Encoder, rank: int) -> Model:
    normalized = (dataset.state_rows - encoder.mean) / encoder.scale
    z = normalized @ encoder.components.T
    extras = (
        raw_quadratics(z, encoder.pairs) - encoder.extra_mean
    ) / encoder.extra_scale
    selected = encoder.indices(rank)
    weights = []
    for action in range(qgent.ACTION_COUNT):
        x = np.concatenate(
            [
                dataset.action_base[action],
                extras[dataset.action_state_indices[action]][:, selected],
            ],
            axis=1,
        )
        y = dataset.action_targets[action]
        sample_weight = dataset.action_weights[action]
        xtx = x.T @ (sample_weight[:, None] * x)
        xty = x.T @ (sample_weight * y)
        regularizer = np.eye(x.shape[1]) * qgent.RIDGE
        regularizer[0, 0] = qgent.RIDGE * 0.01
        weights.append(np.linalg.solve(xtx + regularizer, xty))
    return Model(
        encoder=encoder,
        rank=rank,
        weights=tuple(weights),
        training_worlds=len(dataset.worlds),
        training_examples=sum(len(rows) for rows in dataset.action_targets),
    )


def fit_plain_linear_control(
    worlds: Sequence[negative_probe.PreparedWorld],
) -> qgent.EnergyModel:
    stats = qgent.fresh_stats()
    for world in worlds:
        qgent.add_scenario_to_stats(
            stats,
            world.scenario,
            world.exact_q,
        )
    return qgent.fit_model(stats, len(worlds))


def score(
    model: Model,
    scenario: qgent.Scenario,
    context: qgent.ScenarioFeatures,
    day: int,
    state: qgent.State,
    action: int,
) -> float:
    base = qgent.feature_vector(
        scenario,
        context,
        day,
        state,
        action,
    ).astype(np.float64)
    base /= qgent.FEATURE_SCALE
    normalized = model.encoder.normalized_state(
        scenario,
        context,
        day,
        state,
    )
    extra = model.encoder.all_extras(normalized)[
        model.encoder.indices(model.rank)
    ]
    return float(model.weights[action] @ np.concatenate([base, extra]))


def evaluate(
    model: Model,
    cases: Sequence[qgent.EvaluationCase],
) -> dict[str, float | int]:
    totals = []
    exact_totals = []
    myopic_totals = []
    agreements = []
    forbidden = 0
    for case in cases:

        def policy(
            day: int,
            state: qgent.State,
            selected_scenario: qgent.Scenario = case.scenario,
            selected_context: qgent.ScenarioFeatures = case.context,
        ) -> int:
            allowed = qgent.allowed_actions(state)
            return min(
                allowed,
                key=lambda action: (
                    -score(
                        model,
                        selected_scenario,
                        selected_context,
                        day,
                        state,
                        action,
                    ),
                    action,
                ),
            )

        result = qgent.rollout(
            case.scenario,
            policy,
            exact_q=case.exact_q,
        )
        totals.append(int(result["total_utility"]))
        exact_totals.append(case.exact_total)
        myopic_totals.append(case.myopic_total)
        agreements.append(float(result["exact_action_agreement"]))
        forbidden += int(result["forbidden_selections"])
    ratios = np.asarray(totals) / np.asarray(exact_totals)
    return {
        "scenario_count": len(cases),
        "mean_ratio": float(np.mean(ratios)),
        "minimum_ratio": float(np.min(ratios)),
        "agreement": float(np.mean(agreements)),
        "gain_over_myopic": float(
            np.mean(np.asarray(totals) - np.asarray(myopic_totals))
        ),
        "forbidden_selections": forbidden,
    }


def compact_linear_metrics(metrics: dict[str, Any]) -> dict[str, float | int]:
    return {
        "scenario_count": int(metrics["scenario_count"]),
        "mean_ratio": float(metrics["mean_optimal_utility_ratio"]),
        "minimum_ratio": float(metrics["minimum_optimal_utility_ratio"]),
        "agreement": float(metrics["mean_exact_action_agreement"]),
        "gain_over_myopic": float(metrics["mean_gain_over_myopic"]),
        "forbidden_selections": int(metrics["forbidden_selections"]),
    }


def improves_primary(
    candidate: dict[str, float | int],
    baseline: dict[str, float | int],
) -> bool:
    return (
        candidate["mean_ratio"] > baseline["mean_ratio"]
        and candidate["minimum_ratio"] >= baseline["minimum_ratio"]
        and candidate["gain_over_myopic"] > baseline["gain_over_myopic"]
        and candidate["forbidden_selections"] == 0
    )


def metric_deltas(
    candidate: dict[str, float | int],
    baseline: dict[str, float | int],
) -> dict[str, float]:
    return {
        metric: float(candidate[metric]) - float(baseline[metric])
        for metric in (
            "mean_ratio",
            "minimum_ratio",
            "agreement",
            "gain_over_myopic",
        )
    }


def model_payload(
    model: Model,
    *,
    training_seeds: Sequence[int] | None = None,
) -> dict[str, Any]:
    selected_training_seeds = (
        list(qgent.TRAIN_SEEDS[: model.training_worlds])
        if training_seeds is None
        else [int(seed) for seed in training_seeds]
    )
    if len(selected_training_seeds) != model.training_worlds:
        raise ValueError("training seed count does not match model")
    selected = model.encoder.indices(model.rank)
    payload: dict[str, Any] = {
        "schema": MODEL_SCHEMA,
        "classification": (
            "experimental bounded synthetic PCA-quadratic Q-advantage model"
        ),
        "action_names": list(qgent.ACTION_NAMES),
        "base_feature_names": list(qgent.FEATURE_NAMES),
        "base_feature_scale": qgent.FEATURE_SCALE,
        "state_feature_names": [
            qgent.FEATURE_NAMES[index]
            for index in negative_probe.STATE_FEATURE_INDICES
        ],
        "encoder": {
            "definition": (
                "standardize state features, project onto PCA components, "
                "then standardize all z_i*z_j terms with i<=j"
            ),
            "rank": model.rank,
            "mean": model.encoder.mean.tolist(),
            "scale": model.encoder.scale.tolist(),
            "components": model.encoder.components[: model.rank].tolist(),
            "quadratic_pairs": [
                list(model.encoder.pairs[index]) for index in selected
            ],
            "quadratic_mean": model.encoder.extra_mean[selected].tolist(),
            "quadratic_scale": model.encoder.extra_scale[selected].tolist(),
        },
        "weights": [weights.tolist() for weights in model.weights],
        "feature_count": len(model.weights[0]),
        "training_worlds": model.training_worlds,
        "training_examples": model.training_examples,
        "training_seeds": selected_training_seeds,
        "tie_break": "lowest admissible action identifier",
        "authority_boundary": (
            "The model ranks admissible actions only. The deterministic "
            "environment owns admissibility and utility evaluation."
        ),
    }
    payload["sha256"] = qgent.sha256_bytes(canonical_json_bytes(payload))
    return payload


def build_probe() -> tuple[dict[str, Any], dict[str, Any]]:
    worlds = negative_probe.prepare_training_worlds(qgent.TRAIN_SEEDS)
    datasets = {
        budget: build_dataset(worlds[:budget])
        for budget in TRAINING_BUDGETS
    }
    encoders = {
        budget: fit_encoder(dataset.state_rows)
        for budget, dataset in datasets.items()
    }
    frozen_linear = negative_probe.load_baseline()
    plain_32_linear = fit_plain_linear_control(worlds)
    validation_cases = qgent.prepare_evaluation_cases(
        qgent.VALIDATION_SEEDS
    )
    frozen_validation = compact_linear_metrics(
        qgent.evaluate_model(frozen_linear, validation_cases)
    )
    plain_32_validation = compact_linear_metrics(
        qgent.evaluate_model(plain_32_linear, validation_cases)
    )

    frontier = []
    survivors: list[tuple[Any, ...]] = []
    for budget in TRAINING_BUDGETS:
        for rank in RANKS:
            model = fit_model(datasets[budget], encoders[budget], rank)
            metrics = evaluate(model, validation_cases)
            passed = improves_primary(metrics, frozen_validation)
            row = {
                "training_worlds": budget,
                "pca_rank": rank,
                "feature_count": len(model.weights[0]),
                "metrics": metrics,
                "passed_frozen_selection_gate": passed,
            }
            frontier.append(row)
            if passed:
                survivors.append(
                    (
                        metrics["mean_ratio"],
                        metrics["minimum_ratio"],
                        metrics["agreement"],
                        -len(model.weights[0]),
                        -budget,
                        model,
                        row,
                    )
                )
    if not survivors:
        raise RuntimeError("the frozen validation search has no survivor")
    selected = max(survivors)
    selected_model = selected[-2]
    selected_row = selected[-1]

    confirmation_cases = qgent.prepare_evaluation_cases(
        CONFIRMATION_SEEDS
    )
    frozen_confirmation = compact_linear_metrics(
        qgent.evaluate_model(frozen_linear, confirmation_cases)
    )
    plain_32_confirmation = compact_linear_metrics(
        qgent.evaluate_model(plain_32_linear, confirmation_cases)
    )
    candidate_confirmation = evaluate(
        selected_model,
        confirmation_cases,
    )
    beats_frozen = improves_primary(
        candidate_confirmation,
        frozen_confirmation,
    )
    beats_plain_32 = improves_primary(
        candidate_confirmation,
        plain_32_confirmation,
    )
    supported = beats_frozen and beats_plain_32
    payload = model_payload(selected_model)
    report = {
        "schema": REPORT_SCHEMA,
        "classification": (
            "bounded synthetic representation-learning experiment"
        ),
        "hypothesis": (
            "A low-rank PCA coordinate system with quadratic interactions "
            "improves fresh-world rollout utility over both the frozen "
            "16-world model and a plain 32-world linear control."
        ),
        "protocol": {
            "candidate_budgets": list(TRAINING_BUDGETS),
            "candidate_pca_ranks": list(RANKS),
            "selection_split": "validation",
            "selection_gate": (
                "mean_ratio greater, minimum_ratio no lower, "
                "gain_over_myopic greater, and zero forbidden selections "
                "relative to the frozen 16-world model"
            ),
            "selection_order": (
                "mean ratio, minimum ratio, action agreement, smaller "
                "feature count, then smaller training budget"
            ),
            "agreement_role": (
                "reported diagnostic; not a primary utility gate"
            ),
            "post_confirmation_control": (
                "The plain 32-world linear control was added after the first "
                "confirmation readout. No candidate was changed afterward."
            ),
        },
        "splits": {
            "training_seeds": list(qgent.TRAIN_SEEDS),
            "validation_seeds": list(qgent.VALIDATION_SEEDS),
            "confirmation_seeds": list(CONFIRMATION_SEEDS),
            "disjoint": not (
                set(qgent.TRAIN_SEEDS) & set(qgent.VALIDATION_SEEDS)
                or set(qgent.TRAIN_SEEDS) & set(CONFIRMATION_SEEDS)
                or set(qgent.VALIDATION_SEEDS)
                & set(CONFIRMATION_SEEDS)
            ),
            "confirmation_status": (
                "consumed evidence; frozen against all future retuning"
            ),
        },
        "model": {
            "base_feature_count": qgent.FEATURE_COUNT,
            "selected_training_worlds": selected_model.training_worlds,
            "selected_pca_rank": selected_model.rank,
            "quadratic_feature_count": len(
                selected_model.encoder.indices(selected_model.rank)
            ),
            "selected_feature_count": len(selected_model.weights[0]),
            "model_sha256": payload["sha256"],
        },
        "validation": {
            "frozen_16_world_linear": frozen_validation,
            "plain_32_world_linear": plain_32_validation,
            "selected_candidate": selected_row["metrics"],
            "selected_candidate_spec": {
                key: value
                for key, value in selected_row.items()
                if key != "metrics"
            },
            "frontier": frontier,
        },
        "confirmation": {
            "frozen_16_world_linear": frozen_confirmation,
            "plain_32_world_linear": plain_32_confirmation,
            "pca_quadratic_candidate": candidate_confirmation,
            "candidate_minus_frozen_16": metric_deltas(
                candidate_confirmation,
                frozen_confirmation,
            ),
            "candidate_minus_plain_32": metric_deltas(
                candidate_confirmation,
                plain_32_confirmation,
            ),
            "beats_frozen_16_on_primary_gates": beats_frozen,
            "beats_plain_32_on_primary_gates": beats_plain_32,
        },
        "decision": {
            "status": "SUPPORTED_BOUNDED" if supported else "REFUTED",
            "candidate_promoted_for_lab_comparison": supported,
            "reason": (
                "The frozen candidate improves all three primary rollout "
                "metrics over both controls on the consumed confirmation "
                "block."
                if supported
                else "The candidate fails at least one declared primary "
                "comparison on the confirmation block."
            ),
        },
        "nonclaims": [
            (
                "The extra 32-world control was added after confirmation, so "
                "the result is exploratory evidence rather than a fully "
                "preregistered comparison."
            ),
            (
                "The confirmation worlds come from the same bounded synthetic "
                "generator as training and validation."
            ),
            (
                "The benchmark's declared synthetic utility is not evidence "
                "of real-world welfare, morality, or general intelligence."
            ),
            (
                "The float model has not replaced the deployed quantized "
                "Qgent or been integrated into the Tau-gated demo."
            ),
            (
                "Canonical JSON is hash-stable in this recorded environment; "
                "cross-platform floating-point reproducibility is untested."
            ),
        ],
    }
    return payload, report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-out", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--model-out", type=Path, default=DEFAULT_MODEL)
    args = parser.parse_args(argv)
    model, report = build_probe()
    for path in (args.report_out, args.model_out):
        path.parent.mkdir(parents=True, exist_ok=True)
    args.model_out.write_bytes(canonical_json_bytes(model))
    args.report_out.write_bytes(canonical_json_bytes(report))
    print(
        json.dumps(
            {
                "status": report["decision"]["status"],
                "model_sha256": model["sha256"],
                "selected": report["model"],
                "confirmation": report["confirmation"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if report["decision"]["status"] == "SUPPORTED_BOUNDED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
