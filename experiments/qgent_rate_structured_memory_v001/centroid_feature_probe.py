"""Replay the rejected centroid-distance feature hypothesis.

The probe asks whether distances to optimal-action centroids improve the
existing 34-feature Qgent. Model selection uses the original validation split.
The selected candidate is then evaluated once on a disjoint 40-world
confirmation block.

This file preserves a negative result. It must not be used to retune against
the confirmation block.
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

from experiments.qgent_utilitarian_energy_v001 import (
    utilitarian_energy_lab as q,
)

REPORT_SCHEMA = "qgent-centroid-feature-negative-probe-v1"
DEFAULT_REPORT = (
    Path(__file__).with_name("results")
    / "qgent_centroid_feature_probe_v001.report.json"
)
TRAINING_SEEDS = q.TRAIN_SEEDS[:16]
CONFIRMATION_SEEDS = tuple(range(710_000, 710_040))
STATE_FEATURE_INDICES = np.asarray(
    [1, 2, 3, 4, 5, *range(10, q.FEATURE_COUNT)],
    dtype=np.int64,
)


@dataclass(frozen=True)
class PreparedWorld:
    scenario: q.Scenario
    exact_q: np.ndarray
    context: q.ScenarioFeatures
    states: tuple[tuple[int, int, int, int], ...]


@dataclass(frozen=True)
class CentroidEncoder:
    mean: np.ndarray
    scale: np.ndarray
    centroids: np.ndarray
    distance_mean: np.ndarray
    distance_scale: np.ndarray

    def state_vector(
        self,
        scenario: q.Scenario,
        context: q.ScenarioFeatures,
        day: int,
        state: q.State,
    ) -> np.ndarray:
        raw = q.feature_vector(scenario, context, day, state, q.HOLD)[
            STATE_FEATURE_INDICES
        ].astype(np.float64)
        raw /= q.FEATURE_SCALE
        return (raw - self.mean) / self.scale

    def raw_distances(self, normalized: np.ndarray) -> np.ndarray:
        delta = self.centroids - normalized[None, :]
        return np.sum(delta * delta, axis=1) / delta.shape[1]

    def distances(self, normalized: np.ndarray) -> np.ndarray:
        return (
            self.raw_distances(normalized) - self.distance_mean
        ) / self.distance_scale


@dataclass(frozen=True)
class CentroidModel:
    encoder: CentroidEncoder
    weights: np.ndarray


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


def prepare_training_worlds(
    seeds: Sequence[int],
) -> list[PreparedWorld]:
    worlds = []
    for seed in seeds:
        scenario = q.make_scenario(seed)
        _, exact_q = q.solve_exact(scenario)
        worlds.append(
            PreparedWorld(
                scenario=scenario,
                exact_q=exact_q,
                context=q.build_scenario_features(scenario),
                states=q.sample_training_states(scenario, exact_q),
            )
        )
    return worlds


def state_training_rows(
    worlds: Sequence[PreparedWorld],
) -> tuple[np.ndarray, np.ndarray]:
    rows = []
    labels = []
    for world in worlds:
        for day, budget, capacity, reserve in world.states:
            state = (budget, capacity, reserve)
            raw = q.feature_vector(
                world.scenario,
                world.context,
                day,
                state,
                q.HOLD,
            )[STATE_FEATURE_INDICES].astype(np.float64)
            rows.append(raw / q.FEATURE_SCALE)
            labels.append(
                q.greedy_action_from_row(
                    world.exact_q[(day, *state)],
                    q.allowed_actions(state),
                )
            )
    return np.vstack(rows), np.asarray(labels, dtype=np.int8)


def fit_encoder(rows: np.ndarray, labels: np.ndarray) -> CentroidEncoder:
    mean = rows.mean(axis=0)
    scale = rows.std(axis=0)
    scale[scale < 1e-9] = 1.0
    normalized = (rows - mean) / scale
    centroids = []
    for action in range(q.ACTION_COUNT):
        members = normalized[labels == action]
        if len(members) == 0:
            raise ValueError(f"action {action} has no centroid examples")
        centroids.append(members.mean(axis=0))
    centroid_matrix = np.vstack(centroids)
    delta = normalized[:, None, :] - centroid_matrix[None, :, :]
    distances = np.sum(delta * delta, axis=2) / normalized.shape[1]
    distance_mean = distances.mean(axis=0)
    distance_scale = distances.std(axis=0)
    distance_scale[distance_scale < 1e-9] = 1.0
    return CentroidEncoder(
        mean=mean,
        scale=scale,
        centroids=centroid_matrix,
        distance_mean=distance_mean,
        distance_scale=distance_scale,
    )


def candidate_features(
    encoder: CentroidEncoder,
    scenario: q.Scenario,
    context: q.ScenarioFeatures,
    day: int,
    state: q.State,
    action: int,
) -> np.ndarray:
    base = q.feature_vector(scenario, context, day, state, action).astype(np.float64)
    base /= q.FEATURE_SCALE
    normalized = encoder.state_vector(scenario, context, day, state)
    return np.concatenate([base, encoder.distances(normalized)])


def fit_candidate(
    worlds: Sequence[PreparedWorld],
    encoder: CentroidEncoder,
) -> CentroidModel:
    dimension = q.FEATURE_COUNT + q.ACTION_COUNT
    xtx = np.zeros((q.ACTION_COUNT, dimension, dimension))
    xty = np.zeros((q.ACTION_COUNT, dimension))
    for world in worlds:
        for day, budget, capacity, reserve in world.states:
            state = (budget, capacity, reserve)
            allowed = q.allowed_actions(state)
            exact_row = world.exact_q[(day, *state)]
            best = max(int(exact_row[action]) for action in allowed)
            for action in allowed:
                target = float(int(exact_row[action]) - best)
                features = candidate_features(
                    encoder,
                    world.scenario,
                    world.context,
                    day,
                    state,
                    action,
                )
                weight = 2.0 if -20 <= target < 0 else 1.0
                xtx[action] += weight * np.outer(features, features)
                xty[action] += weight * features * target
    weights = np.zeros((q.ACTION_COUNT, dimension))
    for action in range(q.ACTION_COUNT):
        regularizer = np.eye(dimension) * q.RIDGE
        regularizer[0, 0] = q.RIDGE * 0.01
        weights[action] = np.linalg.solve(
            xtx[action] + regularizer,
            xty[action],
        )
    return CentroidModel(encoder=encoder, weights=weights)


def candidate_score(
    model: CentroidModel,
    scenario: q.Scenario,
    context: q.ScenarioFeatures,
    day: int,
    state: q.State,
    action: int,
) -> float:
    return float(
        model.weights[action]
        @ candidate_features(
            model.encoder,
            scenario,
            context,
            day,
            state,
            action,
        )
    )


def load_baseline() -> q.EnergyModel:
    payload = json.loads(
        (ROOT / "assets/data/qgent_utilitarian_energy_100_v1.model.json").read_text(
            encoding="utf-8"
        )
    )
    return q.EnergyModel(
        weights_q=np.asarray(payload["weights_q"], dtype=np.int64),
        training_scenarios=int(payload["training_scenarios"]),
        training_examples=int(payload["training_examples"]),
        model_sha256=str(payload["sha256"]),
    )


def compact_baseline_metrics(metrics: dict[str, Any]) -> dict[str, float]:
    return {
        "mean_optimal_utility_ratio": float(metrics["mean_optimal_utility_ratio"]),
        "minimum_optimal_utility_ratio": float(
            metrics["minimum_optimal_utility_ratio"]
        ),
        "mean_exact_action_agreement": float(metrics["mean_exact_action_agreement"]),
        "mean_gain_over_myopic": float(metrics["mean_gain_over_myopic"]),
    }


def evaluate_candidate(
    model: CentroidModel,
    cases: Sequence[q.EvaluationCase],
) -> dict[str, float]:
    totals = []
    exact_totals = []
    myopic_totals = []
    agreements = []
    for case in cases:

        def policy(
            day: int,
            state: q.State,
            selected_scenario: q.Scenario = case.scenario,
            selected_context: q.ScenarioFeatures = case.context,
        ) -> int:
            allowed = q.allowed_actions(state)
            return min(
                allowed,
                key=lambda action: (
                    -candidate_score(
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

        result = q.rollout(
            case.scenario,
            policy,
            exact_q=case.exact_q,
        )
        totals.append(int(result["total_utility"]))
        exact_totals.append(case.exact_total)
        myopic_totals.append(case.myopic_total)
        agreements.append(float(result["exact_action_agreement"]))
    ratios = np.asarray(totals) / np.asarray(exact_totals)
    return {
        "mean_optimal_utility_ratio": float(np.mean(ratios)),
        "minimum_optimal_utility_ratio": float(np.min(ratios)),
        "mean_exact_action_agreement": float(np.mean(agreements)),
        "mean_gain_over_myopic": float(
            np.mean(np.asarray(totals) - np.asarray(myopic_totals))
        ),
    }


def improves_every_gate(
    candidate: dict[str, float],
    baseline: dict[str, float],
) -> bool:
    return (
        candidate["mean_optimal_utility_ratio"] > baseline["mean_optimal_utility_ratio"]
        and candidate["minimum_optimal_utility_ratio"]
        >= baseline["minimum_optimal_utility_ratio"]
        and candidate["mean_exact_action_agreement"]
        >= baseline["mean_exact_action_agreement"]
        and candidate["mean_gain_over_myopic"] > baseline["mean_gain_over_myopic"]
    )


def build_probe_report() -> dict[str, Any]:
    worlds = prepare_training_worlds(TRAINING_SEEDS)
    rows, labels = state_training_rows(worlds)
    encoder = fit_encoder(rows, labels)
    candidate = fit_candidate(worlds, encoder)
    baseline = load_baseline()
    validation_cases = q.prepare_evaluation_cases(q.VALIDATION_SEEDS)
    confirmation_cases = q.prepare_evaluation_cases(CONFIRMATION_SEEDS)
    validation_baseline = compact_baseline_metrics(
        q.evaluate_model(baseline, validation_cases)
    )
    validation_candidate = evaluate_candidate(candidate, validation_cases)
    confirmation_baseline = compact_baseline_metrics(
        q.evaluate_model(baseline, confirmation_cases)
    )
    confirmation_candidate = evaluate_candidate(candidate, confirmation_cases)
    validation_passed = improves_every_gate(validation_candidate, validation_baseline)
    confirmation_passed = improves_every_gate(
        confirmation_candidate, confirmation_baseline
    )
    return {
        "schema": REPORT_SCHEMA,
        "classification": ("refuted representation-feature hypothesis"),
        "hypothesis": (
            "Nine optimal-action centroid-distance features improve mean and "
            "minimum sequential utility ratio, exact-action agreement, and "
            "gain over myopic on a fresh confirmation block."
        ),
        "model": {
            "baseline_feature_count": q.FEATURE_COUNT,
            "added_centroid_distance_features": q.ACTION_COUNT,
            "candidate_feature_count": int(candidate.weights.shape[1]),
            "training_worlds": len(TRAINING_SEEDS),
            "training_state_rows": len(rows),
        },
        "splits": {
            "training_seeds": list(TRAINING_SEEDS),
            "validation_seeds": list(q.VALIDATION_SEEDS),
            "confirmation_seeds": list(CONFIRMATION_SEEDS),
            "disjoint": not (
                set(TRAINING_SEEDS) & set(q.VALIDATION_SEEDS)
                or set(TRAINING_SEEDS) & set(CONFIRMATION_SEEDS)
                or set(q.VALIDATION_SEEDS) & set(CONFIRMATION_SEEDS)
            ),
            "confirmation_status": (
                "frozen negative evidence; do not use for retuning"
            ),
        },
        "validation": {
            "baseline": validation_baseline,
            "candidate": validation_candidate,
            "all_gates_improved": validation_passed,
        },
        "confirmation": {
            "baseline": confirmation_baseline,
            "candidate": confirmation_candidate,
            "all_gates_improved": confirmation_passed,
        },
        "decision": {
            "status": "REFUTED",
            "candidate_promoted": False,
            "reason": (
                "The candidate improved the validation split but worsened "
                "every declared aggregate on the disjoint confirmation block."
            ),
        },
        "negative_knowledge": [
            (
                "A positive coding-rate or class-separation signal does not by "
                "itself imply better sequential rollout decisions."
            ),
            (
                "Adding optimal-action centroid distances to this linear head "
                "can increase validation performance while reducing fresh-block "
                "robustness."
            ),
            (
                "The confirmation block is now diagnostic and cannot serve as "
                "fresh evidence for a redesigned candidate."
            ),
        ],
        "nonclaims": [
            (
                "This result does not refute representation learning, MCR2, "
                "centroid methods, or nonlinear Q models in general."
            ),
            (
                "No real-world welfare or moral conclusion follows from the "
                "synthetic utility benchmark."
            ),
        ],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-out", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args(argv)
    report = build_probe_report()
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_bytes(canonical_json_bytes(report))
    print(
        json.dumps(
            {
                "status": report["decision"]["status"],
                "validation_all_gates_improved": report["validation"][
                    "all_gates_improved"
                ],
                "confirmation_all_gates_improved": report["confirmation"][
                    "all_gates_improved"
                ],
                "confirmation_baseline": report["confirmation"]["baseline"],
                "confirmation_candidate": report["confirmation"]["candidate"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
