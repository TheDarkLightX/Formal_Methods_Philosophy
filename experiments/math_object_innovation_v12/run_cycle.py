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


def pair_choice(rows, p1, p2):
    current = choose_by_tie_break(rows, p1)

    # The second clause refines the post-p1 choice. Because the original
    # origin classification refers to the v10 default, only `any`-guard clauses
    # are allowed in the second slot of this bounded search.
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
    residual = holdout_residual_cases()
    state_data = collect_state_dataset()
    root_5 = sample_root_dataset(5, 1000, 99)
    root_6 = sample_root_dataset(6, 300, 123)

    candidates = []
    for params in parameter_grid():
        fixed = tuple(int(choose_by_tie_break(item["rows"], params) == item["target"]) for item in residual)
        if any(fixed):
            candidates.append((params, fixed))

    second_slot = [params for params, _fixed in candidates if params["origin_guard"] == "any"]

    bank = []
    iterations = []
    safe_pair = None

    for iteration in range(1, 21):
        viable = []
        for p1, _fixed in candidates:
            for p2 in second_slot:
                good = True
                for item in residual:
                    if pair_choice(item["rows"], p1, p2) != item["target"]:
                        good = False
                        break
                if not good:
                    continue
                for item in bank:
                    if pair_choice(item["rows"], p1, p2) != item["target"]:
                        good = False
                        break
                if good:
                    viable.append((p1, p2))

        iterations.append({
            "iteration": iteration,
            "bank_size": len(bank),
            "viable_pair_count": len(viable),
        })

        if not viable:
            break

        viable.sort(
            key=lambda pair: (
                pair[0]["cut_gain_min"],
                pair[0]["next_size_drop_min"],
                pair[0]["max_child_cut_drop"],
                pair[0]["min_child_sum_drop"],
                pair[0]["min_child_best_singleton_gain"],
                pair[0]["origin_guard"],
                pair[0]["rank"],
                pair[1]["cut_gain_min"],
                pair[1]["next_size_drop_min"],
                pair[1]["max_child_cut_drop"],
                pair[1]["min_child_sum_drop"],
                pair[1]["min_child_best_singleton_gain"],
                pair[1]["rank"],
            )
        )

        p1, p2 = viable[0]
        failure = None
        for item in state_data:
            if pair_choice(item["rows"], p1, p2) != item["target"]:
                failure = item
                break

        if failure is None:
            safe_pair = {
                "clause_1": p1,
                "clause_2": p2,
                "holdout_5_hits": sum(1 for item in root_5 if pair_choice(item["rows"], p1, p2) == item["target"]),
                "holdout_6_hits": sum(1 for item in root_6 if pair_choice(item["rows"], p1, p2) == item["target"]),
            }
            break

        bank.append({
            "mask": failure["mask"],
            "candidates": list(failure["candidates"]),
            "target": failure["target"],
            "rows": failure["rows"],
        })
        iterations[-1]["counterexample"] = {
            "mask": failure["mask"],
            "candidates": list(failure["candidates"]),
            "target": failure["target"],
        }

    return {
        "tier": "descriptive_symbolic_controller",
        "oracle_dependent": False,
        "discovery_domain": "CEGIS over ordered pairs of residual tie-break clauses above the exact bounded two-clause controller",
        "holdout_domain": "sampled 5x5 and 6x6 roots with fixed seeds 99 and 123",
        "survivor": "repair-program CEGIS frontier",
        "candidate_clause_count": len(candidates),
        "second_slot_clause_count": len(second_slot),
        "residual_case_count": len(residual),
        "state_total": len(state_data),
        "iterations": iterations,
        "safe_pair": safe_pair,
        "strongest_claim": (
            "A short repair program over the tie-break clause language does exist: a CEGIS loop finds a safe ordered clause pair after two banked 4x4 counterexamples. "
            "But the lexicographically simplest safe pair generalizes poorly on larger sampled roots, so the next loop must optimize safety and larger-domain ranking separately."
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
