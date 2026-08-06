"""Run the preregistered fixed-capacity PCA-quadratic scaling experiment.

The training budgets, evaluation block, controls, gates, and nonclaims are
frozen in ``research/pca_quadratic_scaling_protocol_v001.json``. A negative
result is a valid completed experiment. Do not alter the protocol after an
evaluation result has been observed.
"""

from __future__ import annotations

import argparse
import gc
import json
import math
import statistics
import sys
from collections.abc import Sequence
from itertools import pairwise
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.qgent_rate_structured_memory_v001 import (
    centroid_feature_probe as training_probe,
)
from experiments.qgent_rate_structured_memory_v001 import (
    pca_quadratic_feature_probe as pca_probe,
)
from experiments.qgent_rate_structured_memory_v001 import (
    pca_quadratic_replication as replication,
)
from experiments.qgent_utilitarian_energy_v001 import (
    utilitarian_energy_lab as qgent,
)

PROTOCOL_SCHEMA = "qgent-pca-quadratic-knowledge-scaling-protocol-v1"
REPORT_SCHEMA = "qgent-pca-quadratic-knowledge-scaling-report-v1"
TRAINING_BUDGETS = (8, 16, 32, 64, 128)
TRAINING_SEEDS = tuple(range(410_000, 410_128))
EVALUATION_SEEDS = tuple(range(930_000, 930_100))
EXPECTED_PUBLISHED_32_CONTENT_SHA256 = (
    "0b3eb747c1582fbfa4ba332c3aea108da4fd9f956a630097d59f9422027e9c48"
)
PROTOCOL_PATH = (
    Path(__file__).with_name("research")
    / "pca_quadratic_scaling_protocol_v001.json"
)
DEFAULT_REPORT = (
    Path(__file__).with_name("results")
    / "qgent_pca_quadratic_scaling_v001.report.json"
)
DEFAULT_MODEL = (
    ROOT
    / "assets/downloads"
    / "qgent-pca-quadratic-feature-model-128-v1.json"
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


def verify_protocol() -> dict[str, Any]:
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    if protocol["schema"] != PROTOCOL_SCHEMA:
        raise ValueError("unexpected scaling protocol schema")
    if protocol["model_family"]["training_budgets"] != list(
        TRAINING_BUDGETS
    ):
        raise ValueError("training budgets disagree with protocol")
    declared_training = protocol["model_family"]["nested_training_seeds"]
    if (
        declared_training["first"] != TRAINING_SEEDS[0]
        or declared_training["last"] != TRAINING_SEEDS[-1]
        or declared_training["count"] != len(TRAINING_SEEDS)
    ):
        raise ValueError("training seeds disagree with protocol")
    declared_evaluation = protocol["evaluation_block"]["seeds"]
    if (
        declared_evaluation["first"] != EVALUATION_SEEDS[0]
        or declared_evaluation["last"] != EVALUATION_SEEDS[-1]
        or declared_evaluation["count"] != len(EVALUATION_SEEDS)
    ):
        raise ValueError("evaluation seeds disagree with protocol")
    if set(TRAINING_SEEDS) & set(EVALUATION_SEEDS):
        raise ValueError("training and evaluation seeds overlap")
    return protocol


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
    candidate_name: str,
    control_name: str,
) -> dict[str, float | int]:
    deltas = [
        int(row["models"][candidate_name]["total_utility"])
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


def evaluate_models(
    cases: Sequence[qgent.EvaluationCase],
    models: dict[int, pca_probe.Model],
    plain_128: qgent.EnergyModel,
) -> list[dict[str, Any]]:
    records = []
    for case in cases:
        outcomes: dict[str, dict[str, Any]] = {}
        for budget, model in models.items():
            outcomes[f"pca_{budget}"] = qgent.rollout(
                case.scenario,
                replication.candidate_policy(model, case),
                exact_q=case.exact_q,
            )
        outcomes["plain_128"] = qgent.rollout(
            case.scenario,
            replication.linear_policy(plain_128, case),
            exact_q=case.exact_q,
        )
        records.append(
            {
                "seed": case.scenario.seed,
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
    ratios = utilities / exact
    return {
        "scenario_count": len(records),
        "mean_total_utility": float(np.mean(utilities)),
        "mean_optimal_utility_ratio": float(np.mean(ratios)),
        "minimum_optimal_utility_ratio": float(np.min(ratios)),
        "mean_gain_over_myopic": float(np.mean(utilities - myopic)),
        "mean_exact_action_agreement": float(np.mean(agreements)),
        "forbidden_selections": sum(
            int(row["models"][model_name]["forbidden_selections"])
            for row in records
        ),
    }


def improves_utility(
    candidate: dict[str, float | int],
    control: dict[str, float | int],
) -> bool:
    return (
        float(candidate["mean_optimal_utility_ratio"])
        > float(control["mean_optimal_utility_ratio"])
        and float(candidate["minimum_optimal_utility_ratio"])
        >= float(control["minimum_optimal_utility_ratio"])
        and float(candidate["mean_gain_over_myopic"])
        > float(control["mean_gain_over_myopic"])
        and int(candidate["forbidden_selections"]) == 0
    )


def build_report() -> tuple[dict[str, Any], dict[str, Any]]:
    protocol = verify_protocol()
    worlds = training_probe.prepare_training_worlds(TRAINING_SEEDS)
    models: dict[int, pca_probe.Model] = {}
    payloads: dict[int, dict[str, Any]] = {}
    for budget in TRAINING_BUDGETS:
        dataset = pca_probe.build_dataset(worlds[:budget])
        encoder = pca_probe.fit_encoder(dataset.state_rows)
        model = pca_probe.fit_model(dataset, encoder, rank=10)
        payload = pca_probe.model_payload(
            model,
            training_seeds=TRAINING_SEEDS[:budget],
        )
        models[budget] = model
        payloads[budget] = payload
        del dataset
        gc.collect()
    if payloads[32]["sha256"] != EXPECTED_PUBLISHED_32_CONTENT_SHA256:
        raise ValueError("32-world curve point does not match published model")

    plain_128 = pca_probe.fit_plain_linear_control(worlds)
    records = evaluate_models(
        replication.prepare_cases(EVALUATION_SEEDS),
        models,
        plain_128,
    )
    model_names = [
        *(f"pca_{budget}" for budget in TRAINING_BUDGETS),
        "plain_128",
    ]
    metrics = {
        model_name: aggregate(records, model_name)
        for model_name in model_names
    }
    scaling_pair = paired_diagnostics(records, "pca_128", "pca_32")
    representation_pair = paired_diagnostics(
        records,
        "pca_128",
        "plain_128",
    )
    knowledge_scaling_gate = (
        improves_utility(metrics["pca_128"], metrics["pca_32"])
        and scaling_pair["wins"] > scaling_pair["losses"]
        and scaling_pair["two_sided_exact_sign_test_p"] < 0.05
        and len(models[128].weights[0]) == len(models[32].weights[0]) == 89
    )
    representation_gate = improves_utility(
        metrics["pca_128"],
        metrics["plain_128"],
    )
    curve_mean_ratios = [
        metrics[f"pca_{budget}"]["mean_optimal_utility_ratio"]
        for budget in TRAINING_BUDGETS
    ]
    adjacent_improvements = [
        float(right) > float(left)
        for left, right in pairwise(curve_mean_ratios)
    ]
    report = {
        "schema": REPORT_SCHEMA,
        "classification": (
            "preregistered fixed-capacity synthetic knowledge-scaling experiment"
        ),
        "protocol": {
            "schema": protocol["schema"],
            "sha256": qgent.sha256_file(PROTOCOL_PATH),
            "anti_tuning_rule": protocol["anti_tuning_rule"],
        },
        "training": {
            "budgets": list(TRAINING_BUDGETS),
            "seeds": list(TRAINING_SEEDS),
            "model_summaries": {
                str(budget): {
                    "feature_count": len(models[budget].weights[0]),
                    "training_examples": models[budget].training_examples,
                    "content_sha256": payloads[budget]["sha256"],
                    "canonical_json_bytes": len(
                        canonical_json_bytes(payloads[budget])
                    ),
                }
                for budget in TRAINING_BUDGETS
            },
        },
        "evaluation": {
            "seeds": list(EVALUATION_SEEDS),
            "metrics": metrics,
            "paired_pca_128_vs_pca_32": scaling_pair,
            "paired_pca_128_vs_plain_128": representation_pair,
            "curve_diagnostics": {
                "mean_ratios_in_budget_order": curve_mean_ratios,
                "adjacent_mean_ratio_improvements": adjacent_improvements,
                "all_adjacent_mean_ratios_improve": all(
                    adjacent_improvements
                ),
            },
            "records": records,
        },
        "decision": {
            "knowledge_scaling_status": (
                "SUPPORTED_BOUNDED"
                if knowledge_scaling_gate
                else "REFUTED"
            ),
            "representation_status": (
                "SUPPORTED_BOUNDED"
                if representation_gate
                else "REFUTED"
            ),
            "knowledge_scaling_gate_passed": knowledge_scaling_gate,
            "representation_gate_passed": representation_gate,
            "runner_completed": True,
        },
        "nonclaims": protocol["nonclaims"],
    }
    return report, payloads[128]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-out", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--model-out", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--protocol-check", action="store_true")
    args = parser.parse_args(argv)
    if args.protocol_check:
        protocol = verify_protocol()
        print(
            json.dumps(
                {
                    "protocol_schema": protocol["schema"],
                    "protocol_sha256": qgent.sha256_file(PROTOCOL_PATH),
                    "status": "FROZEN_AND_CONSISTENT",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    report, model_payload = build_report()
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_bytes(canonical_json_bytes(report))
    if report["decision"]["knowledge_scaling_gate_passed"]:
        args.model_out.parent.mkdir(parents=True, exist_ok=True)
        args.model_out.write_bytes(canonical_json_bytes(model_payload))
    print(
        json.dumps(
            {
                "decision": report["decision"],
                "metrics": report["evaluation"]["metrics"],
                "paired_pca_128_vs_pca_32": report["evaluation"][
                    "paired_pca_128_vs_pca_32"
                ],
                "report_sha256": qgent.sha256_file(args.report_out),
                "model_written": args.model_out.exists(),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
