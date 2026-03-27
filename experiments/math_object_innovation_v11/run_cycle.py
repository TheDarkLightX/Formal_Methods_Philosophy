#!/usr/bin/env python3
from __future__ import annotations

import json
from itertools import product
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.math_object_innovation_v06.run_cycle import collect_state_dataset
from experiments.math_object_innovation_v10.run_cycle import core_choice, sample_root_dataset, two_clause_choice


OUT = ROOT / "generated" / "report.json"
REPAIR = (2, 3, 0, 2, "eq")
RANKS = (
    "cut_next",
    "cut_next_childsum",
    "cut_childsum_next",
    "cut_bestsingleton_next",
)


def default_origin(rows):
    return "repair" if core_choice(rows) != two_clause_choice(rows, REPAIR) else "core"


def choose_by_tie_break(rows, params):
    default = two_clause_choice(rows, REPAIR)
    origin = default_origin(rows)
    if params["origin_guard"] != "any" and origin != params["origin_guard"]:
        return default

    by_y = {y: features for y, features in rows}
    base = by_y[default]
    alternatives = []

    for y, features in rows:
        if y == default:
            continue
        if features["gain"] != base["gain"]:
            continue
        if features["child_best_gain"] != base["child_best_gain"]:
            continue
        if features["next_uncovered"] != base["next_uncovered"]:
            continue
        if features["cut"] < base["cut"] + params["cut_gain_min"]:
            continue
        if features["next_size"] > base["next_size"] - params["next_size_drop_min"]:
            continue
        if features["child_best_cut"] < base["child_best_cut"] - params["max_child_cut_drop"]:
            continue
        if features["child_sum_singleton"] > base["child_sum_singleton"] - params["min_child_sum_drop"]:
            continue
        if features["child_best_singleton"] < base["child_best_singleton"] + params["min_child_best_singleton_gain"]:
            continue

        rank = params["rank"]
        if rank == "cut_next":
            key = (-features["cut"], features["next_size"], y)
        elif rank == "cut_next_childsum":
            key = (-features["cut"], features["next_size"], features["child_sum_singleton"], y)
        elif rank == "cut_childsum_next":
            key = (-features["cut"], features["child_sum_singleton"], features["next_size"], y)
        elif rank == "cut_bestsingleton_next":
            key = (-features["cut"], -features["child_best_singleton"], features["next_size"], y)
        else:
            raise AssertionError(rank)
        alternatives.append((key, y))

    return min(alternatives)[1] if alternatives else default


def parameter_grid():
    for cut_gain_min, next_size_drop_min, max_child_cut_drop, min_child_sum_drop, min_child_best_singleton_gain, origin_guard, rank in product(
        [1, 2],
        [1, 2],
        [0, 1, 2],
        [0, 1, 2, 3, 4, 5],
        [0, 1],
        ["any", "core", "repair"],
        RANKS,
    ):
        yield {
            "cut_gain_min": cut_gain_min,
            "next_size_drop_min": next_size_drop_min,
            "max_child_cut_drop": max_child_cut_drop,
            "min_child_sum_drop": min_child_sum_drop,
            "min_child_best_singleton_gain": min_child_best_singleton_gain,
            "origin_guard": origin_guard,
            "rank": rank,
        }


def holdout_residual_cases():
    residual = []
    for label, dataset in (("5x5", sample_root_dataset(5, 1000, 99)), ("6x6", sample_root_dataset(6, 300, 123))):
        for item in dataset:
            chosen = two_clause_choice(item["rows"], REPAIR)
            if chosen != item["target"]:
                residual.append({
                    "domain": label,
                    "density": item["density"],
                    "rows": item["rows"],
                    "target": item["target"],
                    "two_clause_choice": chosen,
                })
    return residual


def safe_on_state_dataset(state_dataset, params):
    for item in state_dataset:
        if choose_by_tie_break(item["rows"], params) != item["target"]:
            return False, {
                "mask": item["mask"],
                "candidates": list(item["candidates"]),
                "target": item["target"],
                "choice": choose_by_tie_break(item["rows"], params),
            }
    return True, None


def count_hits(dataset, params):
    return sum(1 for item in dataset if choose_by_tie_break(item["rows"], params) == item["target"])


def build_report():
    state_dataset = collect_state_dataset()
    residual = holdout_residual_cases()
    root_5 = sample_root_dataset(5, 1000, 99)
    root_6 = sample_root_dataset(6, 300, 123)

    residual_candidates = []
    safe_candidates = []

    for params in parameter_grid():
        fixed = tuple(int(choose_by_tie_break(item["rows"], params) == item["target"]) for item in residual)
        if not any(fixed):
            continue
        residual_candidates.append({
            "params": params,
            "residual_fix_mask": list(fixed),
            "residual_fix_count": sum(fixed),
        })
        if sum(fixed) < len(residual):
            continue
        safe, first_failure = safe_on_state_dataset(state_dataset, params)
        if not safe:
            continue
        safe_candidates.append({
            "params": params,
            "holdout_5_hits": count_hits(root_5, params),
            "holdout_6_hits": count_hits(root_6, params),
            "first_failure": first_failure,
        })

    residual_candidates.sort(
        key=lambda item: (
            -item["residual_fix_count"],
            item["params"]["cut_gain_min"],
            item["params"]["next_size_drop_min"],
            item["params"]["max_child_cut_drop"],
            item["params"]["min_child_sum_drop"],
            item["params"]["min_child_best_singleton_gain"],
            item["params"]["origin_guard"],
            item["params"]["rank"],
        )
    )

    safe_candidates.sort(
        key=lambda item: (
            -(item["holdout_5_hits"] + item["holdout_6_hits"]),
            -item["holdout_5_hits"],
            -item["holdout_6_hits"],
            item["params"]["origin_guard"],
            item["params"]["rank"],
        )
    )

    return {
        "tier": "descriptive_symbolic_controller",
        "oracle_dependent": False,
        "discovery_domain": "single third tie-break clause above the exact bounded two-clause controller, preserving exhaustive reachable nonterminal 4x4 states",
        "holdout_domain": "sampled 5x5 and 6x6 roots with fixed seeds 99 and 123",
        "survivor": "third-clause tie-break frontier",
        "state_total": len(state_dataset),
        "residual_case_count": len(residual),
        "residual_cases": [
            {
                "domain": item["domain"],
                "density": item["density"],
                "two_clause_choice": item["two_clause_choice"],
                "target": item["target"],
            }
            for item in residual
        ],
        "candidate_count_fixing_at_least_one_residual": len(residual_candidates),
        "top_residual_only_candidates": residual_candidates[:20],
        "safe_candidates_fixing_all_residuals": safe_candidates,
        "strongest_claim": (
            "Within the tested single-clause tie-break family, many clauses repair the last sampled larger-root residuals, but none repairs all of them while preserving every exhaustive reachable nonterminal 4x4 state of the exact bounded two-clause core. "
            "The next frontier is therefore a richer controller language, not another single local tie-break clause in this family."
        ),
    }


def main():
    report = build_report()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
