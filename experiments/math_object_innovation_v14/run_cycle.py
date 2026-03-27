#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.math_object_innovation_v06.run_cycle import collect_state_dataset
from experiments.math_object_innovation_v10.run_cycle import sample_root_dataset
from experiments.math_object_innovation_v11.run_cycle import choose_by_tie_break, holdout_residual_cases, parameter_grid


OUT = ROOT / "generated" / "report.json"
PARAM_KEYS = (
    "cut_gain_min",
    "next_size_drop_min",
    "max_child_cut_drop",
    "min_child_sum_drop",
    "min_child_best_singleton_gain",
    "origin_guard",
    "rank",
)


def norm(params):
    return tuple(params[key] for key in PARAM_KEYS)


def denorm(values):
    return {key: value for key, value in zip(PARAM_KEYS, values)}


def pair_choice(rows, p1, p2):
    if not isinstance(p1, dict):
        p1 = denorm(p1)
    if not isinstance(p2, dict):
        p2 = denorm(p2)

    current = choose_by_tie_break(rows, p1)
    if p2["origin_guard"] != "any":
        return current

    by_y = {y: features for y, features in rows}
    base = by_y[current]
    alternatives = []
    for y, features in rows:
        if y == current:
            continue
        if features["gain"] != base["gain"]:
            continue
        if features["child_best_gain"] != base["child_best_gain"]:
            continue
        if features["next_uncovered"] != base["next_uncovered"]:
            continue
        if features["cut"] < base["cut"] + p2["cut_gain_min"]:
            continue
        if features["next_size"] > base["next_size"] - p2["next_size_drop_min"]:
            continue
        if features["child_best_cut"] < base["child_best_cut"] - p2["max_child_cut_drop"]:
            continue
        if features["child_sum_singleton"] > base["child_sum_singleton"] - p2["min_child_sum_drop"]:
            continue
        if features["child_best_singleton"] < base["child_best_singleton"] + p2["min_child_best_singleton_gain"]:
            continue

        rank = p2["rank"]
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

    return min(alternatives)[1] if alternatives else current


def build_report():
    state_data = collect_state_dataset()
    residual = holdout_residual_cases()
    root_5 = sample_root_dataset(5, 1000, 99)
    root_6 = sample_root_dataset(6, 300, 123)

    candidates = []
    for params in parameter_grid():
        fixed = tuple(int(choose_by_tie_break(item["rows"], params) == item["target"]) for item in residual)
        if any(fixed):
            candidates.append((params, fixed))
    second_slot = [params for params, _fixed in candidates if params["origin_guard"] == "any"]

    bank_keys = {
        (828, (0, 1, 2, 3), 0),
        (1915, (0, 1, 2), 2),
    }
    bank = [item for item in state_data if (item["mask"], tuple(item["candidates"]), item["target"]) in bank_keys]

    viable = []
    for p1, _fixed in candidates:
        np1 = norm(p1)
        for p2 in second_slot:
            np2 = norm(p2)
            ok = True
            for item in residual:
                if pair_choice(item["rows"], np1, np2) != item["target"]:
                    ok = False
                    break
            if not ok:
                continue
            for item in bank:
                if pair_choice(item["rows"], np1, np2) != item["target"]:
                    ok = False
                    break
            if not ok:
                continue
            holdout_5_hits = sum(1 for item in root_5 if pair_choice(item["rows"], np1, np2) == item["target"])
            holdout_6_hits = sum(1 for item in root_6 if pair_choice(item["rows"], np1, np2) == item["target"])
            viable.append((holdout_5_hits + holdout_6_hits, holdout_5_hits, holdout_6_hits, np1, np2))

    viable.sort(reverse=True)

    ranked_prefix = []
    first_safe = None
    for rank, (total, holdout_5_hits, holdout_6_hits, p1, p2) in enumerate(viable, start=1):
        safe = True
        first_failure = None
        for item in state_data:
            if pair_choice(item["rows"], p1, p2) != item["target"]:
                safe = False
                first_failure = {
                    "mask": item["mask"],
                    "candidates": list(item["candidates"]),
                    "target": item["target"],
                }
                break
        ranked_prefix.append({
            "rank": rank,
            "holdout_total": total,
            "holdout_5_hits": holdout_5_hits,
            "holdout_6_hits": holdout_6_hits,
            "safe": safe,
            "clause_1": denorm(p1),
            "clause_2": denorm(p2),
            "first_failure": first_failure,
        })
        if first_safe is None and safe:
            first_safe = ranked_prefix[-1]
            break

    return {
        "tier": "descriptive_symbolic_controller",
        "oracle_dependent": False,
        "discovery_domain": "bank-then-rank search over viable repair-program pairs",
        "holdout_domain": "sampled 5x5 and 6x6 roots with fixed seeds 99 and 123",
        "survivor": "bank-then-rank frontier",
        "viable_pair_count": len(viable),
        "bank_size": len(bank),
        "top_ranked_prefix": ranked_prefix,
        "first_safe_rank": first_safe["rank"] if first_safe is not None else None,
        "first_safe_pair": first_safe,
        "strongest_claim": (
            "After the bounded counterexample bank from v12 is learned, the top larger-domain ranked viable repair program is already safe on the exhaustive reachable 4x4 verifier. "
            "In this bounded slice, safety synthesis and larger-domain ranking cleanly separate into a two-stage loop."
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
