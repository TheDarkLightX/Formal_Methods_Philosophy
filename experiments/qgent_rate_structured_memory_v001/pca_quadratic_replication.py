"""Run the preregistered PCA-quadratic Qgent replication exactly once.

The candidate, controls, gates, seed blocks, and population-shift profiles are
frozen in ``research/pca_quadratic_replication_protocol_v001.json``. A negative
result is a valid completed experiment. Do not change this file after observing
either evaluation block without recording a protocol amendment and treating
the observed block as consumed.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.qgent_rate_structured_memory_v001 import (
    centroid_feature_probe as negative_probe,
)
from experiments.qgent_rate_structured_memory_v001 import (
    pca_quadratic_feature_probe as pca_probe,
)
from experiments.qgent_utilitarian_energy_v001 import (
    utilitarian_energy_lab as qgent,
)

PROTOCOL_SCHEMA = "qgent-pca-quadratic-preregistered-replication-protocol-v1"
REPORT_SCHEMA = "qgent-pca-quadratic-preregistered-replication-report-v1"
EXPECTED_MODEL_CONTENT_SHA256 = (
    "0b3eb747c1582fbfa4ba332c3aea108da4fd9f956a630097d59f9422027e9c48"
)
EXPECTED_MODEL_FILE_SHA256 = (
    "68c264f7017d484f4bd3757313466be9be6741ed6996ffe30849c47c51a9f82c"
)
PRIMARY_SEEDS = tuple(range(910_000, 910_080))
SHIFT_SEEDS = tuple(range(920_000, 920_040))
SHIFT_BASE_POPULATIONS = (1, 1, 8, 12)
PROTOCOL_PATH = (
    Path(__file__).with_name("research")
    / "pca_quadratic_replication_protocol_v001.json"
)
DEFAULT_REPORT = (
    Path(__file__).with_name("results")
    / "qgent_pca_quadratic_replication_v001.report.json"
)
PUBLISHED_MODEL = (
    ROOT
    / "assets"
    / "downloads"
    / "qgent-pca-quadratic-feature-model-v1.json"
)


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


def rotate(values: tuple[int, ...], offset: int) -> tuple[int, ...]:
    selected = offset % len(values)
    return values[selected:] + values[:selected]


def shifted_populations(seed: int) -> tuple[int, int, int, int]:
    offset = seed - SHIFT_SEEDS[0]
    return rotate(SHIFT_BASE_POPULATIONS, offset)


def prepare_cases(
    seeds: Sequence[int],
    population_fn: Callable[[int], tuple[int, int, int, int]] | None = None,
) -> list[qgent.EvaluationCase]:
    cases = []
    for seed in seeds:
        populations = population_fn(seed) if population_fn else None
        scenario = qgent.make_scenario(seed, populations=populations)
        _, exact_q = qgent.solve_exact(scenario)
        exact = qgent.rollout(
            scenario,
            lambda day, state, selected_q=exact_q: (
                qgent.greedy_action_from_row(
                    selected_q[(day, *state)],
                    qgent.allowed_actions(state),
                )
            ),
        )
        myopic = qgent.rollout(
            scenario,
            lambda day, state, selected_scenario=scenario: (
                qgent.myopic_action(selected_scenario, day, state)
            ),
        )
        cases.append(
            qgent.EvaluationCase(
                scenario=scenario,
                exact_q=exact_q,
                context=qgent.build_scenario_features(scenario),
                exact_total=int(exact["total_utility"]),
                myopic_total=int(myopic["total_utility"]),
            )
        )
    return cases


def candidate_policy(
    model: pca_probe.Model,
    case: qgent.EvaluationCase,
) -> Callable[[int, qgent.State], int]:
    def policy(day: int, state: qgent.State) -> int:
        allowed = qgent.allowed_actions(state)
        return min(
            allowed,
            key=lambda action: (
                -pca_probe.score(
                    model,
                    case.scenario,
                    case.context,
                    day,
                    state,
                    action,
                ),
                action,
            ),
        )

    return policy


def linear_policy(
    model: qgent.EnergyModel,
    case: qgent.EvaluationCase,
) -> Callable[[int, qgent.State], int]:
    def policy(day: int, state: qgent.State) -> int:
        return qgent.model_action(
            model,
            case.scenario,
            case.context,
            day,
            state,
        )

    return policy


def evaluate_cases(
    cases: Sequence[qgent.EvaluationCase],
    candidate: pca_probe.Model,
    frozen_linear: qgent.EnergyModel,
    plain_32_linear: qgent.EnergyModel,
) -> list[dict[str, Any]]:
    records = []
    for case in cases:
        policies = {
            "candidate": candidate_policy(candidate, case),
            "frozen_16": linear_policy(frozen_linear, case),
            "plain_32": linear_policy(plain_32_linear, case),
        }
        outcomes = {
            name: qgent.rollout(
                case.scenario,
                policy,
                exact_q=case.exact_q,
            )
            for name, policy in policies.items()
        }
        records.append(
            {
                "seed": case.scenario.seed,
                "populations": list(case.scenario.populations),
                "exact_total": case.exact_total,
                "myopic_total": case.myopic_total,
                "models": {
                    name: {
                        "total_utility": int(outcome["total_utility"]),
                        "exact_action_agreement": float(
                            outcome["exact_action_agreement"]
                        ),
                        "forbidden_selections": int(
                            outcome["forbidden_selections"]
                        ),
                    }
                    for name, outcome in outcomes.items()
                },
            }
        )
    return records


def aggregate(
    records: Sequence[dict[str, Any]],
    model_name: str,
) -> dict[str, float | int]:
    utilities = np.asarray(
        [row["models"][model_name]["total_utility"] for row in records],
        dtype=np.float64,
    )
    exact = np.asarray(
        [row["exact_total"] for row in records],
        dtype=np.float64,
    )
    myopic = np.asarray(
        [row["myopic_total"] for row in records],
        dtype=np.float64,
    )
    agreements = np.asarray(
        [
            row["models"][model_name]["exact_action_agreement"]
            for row in records
        ],
        dtype=np.float64,
    )
    return {
        "scenario_count": len(records),
        "mean_total_utility": float(np.mean(utilities)),
        "mean_optimal_utility_ratio": float(np.mean(utilities / exact)),
        "minimum_optimal_utility_ratio": float(np.min(utilities / exact)),
        "mean_gain_over_myopic": float(np.mean(utilities - myopic)),
        "mean_exact_action_agreement": float(np.mean(agreements)),
        "forbidden_selections": sum(
            int(row["models"][model_name]["forbidden_selections"])
            for row in records
        ),
    }


def exact_sign_test_two_sided(wins: int, losses: int) -> float:
    trials = wins + losses
    if trials == 0:
        return 1.0
    extreme = max(wins, losses)
    one_tail = sum(
        math.comb(trials, successes)
        for successes in range(extreme, trials + 1)
    ) / (2**trials)
    return min(1.0, 2.0 * one_tail)


def paired_diagnostics(
    records: Sequence[dict[str, Any]],
    control_name: str,
) -> dict[str, float | int]:
    deltas = [
        int(row["models"]["candidate"]["total_utility"])
        - int(row["models"][control_name]["total_utility"])
        for row in records
    ]
    wins = sum(delta > 0 for delta in deltas)
    ties = sum(delta == 0 for delta in deltas)
    losses = sum(delta < 0 for delta in deltas)
    return {
        "wins": wins,
        "ties": ties,
        "losses": losses,
        "mean_utility_delta": float(statistics.fmean(deltas)),
        "median_utility_delta": float(statistics.median(deltas)),
        "minimum_utility_delta": min(deltas),
        "maximum_utility_delta": max(deltas),
        "two_sided_exact_sign_test_p": exact_sign_test_two_sided(
            wins,
            losses,
        ),
    }


def passes_gate(
    candidate: dict[str, float | int],
    controls: Sequence[dict[str, float | int]],
) -> bool:
    return (
        int(candidate["forbidden_selections"]) == 0
        and all(
            float(candidate["mean_optimal_utility_ratio"])
            > float(control["mean_optimal_utility_ratio"])
            for control in controls
        )
        and all(
            float(candidate["minimum_optimal_utility_ratio"])
            >= float(control["minimum_optimal_utility_ratio"])
            for control in controls
        )
        and all(
            float(candidate["mean_gain_over_myopic"])
            > float(control["mean_gain_over_myopic"])
            for control in controls
        )
    )


def verify_protocol() -> dict[str, Any]:
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    if protocol["schema"] != PROTOCOL_SCHEMA:
        raise ValueError("unexpected replication protocol schema")
    if protocol["candidate"]["content_sha256"] != EXPECTED_MODEL_CONTENT_SHA256:
        raise ValueError("protocol candidate content hash changed")
    if (
        protocol["candidate"]["published_file_sha256"]
        != EXPECTED_MODEL_FILE_SHA256
    ):
        raise ValueError("protocol candidate file hash changed")
    if qgent.sha256_file(PUBLISHED_MODEL) != EXPECTED_MODEL_FILE_SHA256:
        raise ValueError("published candidate model file changed")
    if (
        protocol["primary_block"]["seeds"]["count"] != len(PRIMARY_SEEDS)
        or protocol["primary_block"]["seeds"]["first"] != PRIMARY_SEEDS[0]
        or protocol["primary_block"]["seeds"]["last"] != PRIMARY_SEEDS[-1]
    ):
        raise ValueError("primary seed block disagrees with protocol")
    if (
        protocol["population_shift_block"]["seeds"]["count"]
        != len(SHIFT_SEEDS)
        or protocol["population_shift_block"]["seeds"]["first"]
        != SHIFT_SEEDS[0]
        or protocol["population_shift_block"]["seeds"]["last"]
        != SHIFT_SEEDS[-1]
    ):
        raise ValueError("shift seed block disagrees with protocol")
    return protocol


def build_report() -> dict[str, Any]:
    protocol = verify_protocol()
    worlds = negative_probe.prepare_training_worlds(qgent.TRAIN_SEEDS)
    dataset = pca_probe.build_dataset(worlds)
    encoder = pca_probe.fit_encoder(dataset.state_rows)
    candidate = pca_probe.fit_model(dataset, encoder, rank=10)
    candidate_payload = pca_probe.model_payload(candidate)
    if candidate_payload["sha256"] != EXPECTED_MODEL_CONTENT_SHA256:
        raise ValueError("refitted candidate does not match frozen content hash")
    frozen_linear = negative_probe.load_baseline()
    plain_32_linear = pca_probe.fit_plain_linear_control(worlds)

    primary_records = evaluate_cases(
        prepare_cases(PRIMARY_SEEDS),
        candidate,
        frozen_linear,
        plain_32_linear,
    )
    shift_records = evaluate_cases(
        prepare_cases(SHIFT_SEEDS, shifted_populations),
        candidate,
        frozen_linear,
        plain_32_linear,
    )

    def summarize(records: Sequence[dict[str, Any]]) -> dict[str, Any]:
        metrics = {
            name: aggregate(records, name)
            for name in ("candidate", "frozen_16", "plain_32")
        }
        return {
            "metrics": metrics,
            "paired_candidate_vs_frozen_16": paired_diagnostics(
                records,
                "frozen_16",
            ),
            "paired_candidate_vs_plain_32": paired_diagnostics(
                records,
                "plain_32",
            ),
            "gate_passed": passes_gate(
                metrics["candidate"],
                [metrics["frozen_16"], metrics["plain_32"]],
            ),
            "records": list(records),
        }

    primary = summarize(primary_records)
    population_shift = summarize(shift_records)
    return {
        "schema": REPORT_SCHEMA,
        "classification": (
            "preregistered bounded synthetic replication and population-shift stress test"
        ),
        "protocol": {
            "schema": protocol["schema"],
            "sha256": qgent.sha256_file(PROTOCOL_PATH),
            "anti_tuning_rule": protocol["anti_tuning_rule"],
        },
        "frozen_candidate": {
            "content_sha256": candidate_payload["sha256"],
            "published_file_sha256": qgent.sha256_file(PUBLISHED_MODEL),
            "feature_count": len(candidate.weights[0]),
            "pca_rank": candidate.rank,
            "training_worlds": candidate.training_worlds,
        },
        "primary_default_generator": primary,
        "secondary_population_shift": population_shift,
        "decision": {
            "primary_status": (
                "SUPPORTED_BOUNDED"
                if primary["gate_passed"]
                else "REFUTED"
            ),
            "population_shift_status": (
                "SUPPORTED_BOUNDED"
                if population_shift["gate_passed"]
                else "REFUTED"
            ),
            "runner_completed": True,
        },
        "nonclaims": protocol["nonclaims"],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-out", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--protocol-check", action="store_true")
    args = parser.parse_args(argv)
    if args.protocol_check:
        protocol = verify_protocol()
        print(
            json.dumps(
                {
                    "protocol_schema": protocol["schema"],
                    "protocol_sha256": qgent.sha256_file(PROTOCOL_PATH),
                    "published_model_sha256": qgent.sha256_file(PUBLISHED_MODEL),
                    "status": "FROZEN_AND_CONSISTENT",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    report = build_report()
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_bytes(canonical_json_bytes(report))
    print(
        json.dumps(
            {
                "decision": report["decision"],
                "primary_metrics": report["primary_default_generator"][
                    "metrics"
                ],
                "population_shift_metrics": report[
                    "secondary_population_shift"
                ]["metrics"],
                "report_sha256": qgent.sha256_file(args.report_out),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
