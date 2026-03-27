#!/usr/bin/env python3
from __future__ import annotations

import json
from itertools import product
from pathlib import Path
import random
import sys


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.math_object_innovation_v03.run_cycle import improve_selector, make_value_function, phi, psi, route_selector
from experiments.math_object_innovation_v04.run_cycle import choose_by_formula
from experiments.math_object_innovation_v05.run_cycle import BASE_FORMULA
from experiments.math_object_innovation_v06.run_cycle import collect_state_dataset, row_features


OUT = ROOT / "generated" / "report.json"

CORE = {
    "gain_loss": 1,
    "child_gain_min": 2,
    "child_cut_min": 0,
    "next_delta": 1,
    "next_mode": "eq",
}


def pi2_selector(rel):
    pi0 = route_selector(rel)
    pi1 = improve_selector(rel, pi0)
    return improve_selector(rel, pi1)


def apply_clause(rows, params, default_choice):
    by_y = {y: features for y, features in rows}
    base = by_y[default_choice]
    alternatives = []
    for y, features in rows:
        if y == default_choice:
            continue
        gain_ok = features["gain"] == base["gain"] - params["gain_loss"]
        child_gain_ok = features["child_best_gain"] >= base["child_best_gain"] + params["child_gain_min"]
        child_cut_ok = features["child_best_cut"] >= base["child_best_cut"] + params["child_cut_min"]
        if params["next_mode"] == "eq":
            next_ok = features["next_uncovered"] == base["next_uncovered"] + params["next_delta"]
        else:
            next_ok = features["next_uncovered"] >= base["next_uncovered"] + params["next_delta"]
        if gain_ok and child_gain_ok and child_cut_ok and next_ok:
            alternatives.append((-features["child_best_gain"], -features["child_best_cut"], features["gain"], y))
    if alternatives:
        return min(alternatives)[3]
    return default_choice


def core_choice(rows):
    return apply_clause(rows, CORE, choose_by_formula(rows, BASE_FORMULA))


def repaired_choice(rows, repair_params):
    return apply_clause(rows, repair_params, core_choice(rows))


def sample_root_dataset(n: int, trials: int, seed: int):
    rng = random.Random(seed)
    rows = []
    for density in [0.3, 0.5, 0.7]:
        for _ in range(trials):
            rel = tuple(
                tuple(rng.random() < density for _ in range(n))
                for _ in range(n)
            )
            candidates = phi(rel, frozenset())
            if not candidates:
                continue
            uncovered = frozenset(range(n)) - psi(rel, candidates)
            if not uncovered:
                continue
            pi2 = pi2_selector(rel)
            value = make_value_function(rel, pi2)
            target = pi2(candidates, uncovered, value)
            rows_now = [(y, row_features(rel, candidates, y)) for y in uncovered]
            rows.append({
                "n": n,
                "density": density,
                "rows": rows_now,
                "target": target,
            })
    return rows


def build_report() -> dict[str, object]:
    state_dataset = collect_state_dataset()
    root_5 = sample_root_dataset(5, 1000, 99)
    root_6 = sample_root_dataset(6, 300, 123)
    total_states = len(state_dataset)
    total_5 = len(root_5)
    total_6 = len(root_6)

    core_state_hits = sum(1 for item in state_dataset if core_choice(item["rows"]) == item["target"])
    assert core_state_hits == total_states

    candidates = []
    for gain_loss, child_gain_min, child_cut_min, next_delta, next_mode in product(
        [1],
        [1, 2],
        [0, 1],
        [1],
        ["eq", "ge"],
    ):
        params = {
            "gain_loss": gain_loss,
            "child_gain_min": child_gain_min,
            "child_cut_min": child_cut_min,
            "next_delta": next_delta,
            "next_mode": next_mode,
        }
        state_hits = 0
        changed_states = 0
        first_core_violation = None
        for item in state_dataset:
            chosen = repaired_choice(item["rows"], params)
            if chosen != core_choice(item["rows"]):
                changed_states += 1
            if chosen == item["target"]:
                state_hits += 1
            elif first_core_violation is None:
                first_core_violation = {
                    "mask": item["mask"],
                    "candidates": list(item["candidates"]),
                    "chosen": chosen,
                    "target": item["target"],
                }
                break
        safe = state_hits == total_states
        holdout_5_hits = 0
        holdout_6_hits = 0
        buckets_5 = {}
        buckets_6 = {}
        if safe:
            for item in root_5:
                if repaired_choice(item["rows"], params) == item["target"]:
                    holdout_5_hits += 1
                    key = f"{item['n']}:{item['density']}"
                    buckets_5[key] = buckets_5.get(key, 0) + 1
            for item in root_6:
                if repaired_choice(item["rows"], params) == item["target"]:
                    holdout_6_hits += 1
                    key = f"{item['n']}:{item['density']}"
                    buckets_6[key] = buckets_6.get(key, 0) + 1
        candidates.append({
            "repair_params": params,
            "safe_on_4x4": safe,
            "changed_state_count": changed_states if safe else None,
            "holdout_5_hits": holdout_5_hits if safe else None,
            "holdout_5_total": total_5 if safe else None,
            "holdout_6_hits": holdout_6_hits if safe else None,
            "holdout_6_total": total_6 if safe else None,
            "holdout_5_buckets": buckets_5 if safe else None,
            "holdout_6_buckets": buckets_6 if safe else None,
            "first_core_violation": None if safe else first_core_violation,
        })

    safe_candidates = [c for c in candidates if c["safe_on_4x4"]]
    safe_candidates.sort(
        key=lambda c: (
            -(c["holdout_5_hits"] + c["holdout_6_hits"]),
            -c["holdout_5_hits"],
            -c["holdout_6_hits"],
            c["repair_params"]["gain_loss"],
            c["repair_params"]["child_gain_min"],
            c["repair_params"]["child_cut_min"],
            c["repair_params"]["next_delta"],
            c["repair_params"]["next_mode"],
        )
    )

    return {
        "tier": "descriptive_symbolic_controller",
        "oracle_dependent": False,
        "discovery_domain": "bounded-core-preserving repair over a small family of second dominance clauses",
        "survivor": "core-preserving repair frontier",
        "core_clause": CORE,
        "state_total": total_states,
        "holdout_5_total": total_5,
        "holdout_6_total": total_6,
        "searched_repair_count": len(candidates),
        "safe_repair_count": len(safe_candidates),
        "best_safe_repair": safe_candidates[0] if safe_candidates else None,
        "top_safe_repairs": safe_candidates[:10],
        "strongest_claim": (
            "An exact bounded dominance clause can be treated as a verified core, and a second repair clause can be searched under the hard constraint that it never changes any exhaustive 4x4 state. "
            "The best safe repair, if any, improves sampled 5x5/6x6 roots without weakening the verified core."
        ),
    }


def main() -> int:
    report = build_report()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
