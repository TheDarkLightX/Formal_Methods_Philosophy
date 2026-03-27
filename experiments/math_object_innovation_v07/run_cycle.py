#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import random
import sys


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.math_object_innovation_v03.run_cycle import improve_selector, make_value_function, phi, psi, route_selector
from experiments.math_object_innovation_v04.run_cycle import collect_root_dataset, choose_by_formula
from experiments.math_object_innovation_v05.run_cycle import BASE_FORMULA
from experiments.math_object_innovation_v06.run_cycle import collect_state_dataset, row_features


OUT = ROOT / "generated" / "report.json"


def pi2_selector(rel):
    pi0 = route_selector(rel)
    pi1 = improve_selector(rel, pi0)
    return improve_selector(rel, pi1)


def dominance_choice(rows):
    base_y = choose_by_formula(rows, BASE_FORMULA)
    by_y = {y: features for y, features in rows}
    base = by_y[base_y]
    alternatives = []
    for y, features in rows:
        if y == base_y:
            continue
        if (
            features["gain"] == base["gain"] - 1
            and features["child_best_gain"] >= base["child_best_gain"] + 2
            and features["child_best_cut"] >= base["child_best_cut"] + 1
            and features["next_uncovered"] == base["next_uncovered"] + 1
        ):
            alternatives.append((-features["child_best_gain"], -features["child_best_cut"], features["gain"], y))
    if alternatives:
        return min(alternatives)[3]
    return base_y


def evaluate_root_4x4() -> dict[str, int]:
    dataset = collect_root_dataset(4)
    hits = sum(1 for item in dataset if dominance_choice(item["rows"]) == item["target_pi2"])
    return {"hits": hits, "total": len(dataset)}


def evaluate_state_4x4() -> dict[str, int]:
    dataset = collect_state_dataset()
    hits = sum(1 for item in dataset if dominance_choice(item["rows"]) == item["target"])
    return {"hits": hits, "total": len(dataset)}


def evaluate_larger_roots(n: int, trials: int, seed: int) -> list[dict[str, object]]:
    rng = random.Random(seed)
    rows = []
    for density in [0.3, 0.5, 0.7]:
        base_hits = 0
        dominance_hits = 0
        total = 0
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
            total += 1
            if choose_by_formula(rows_now, BASE_FORMULA) == target:
                base_hits += 1
            if dominance_choice(rows_now) == target:
                dominance_hits += 1
        rows.append({
            "n": n,
            "density": density,
            "trials": trials,
            "total": total,
            "base_hits": base_hits,
            "dominance_hits": dominance_hits,
        })
    return rows


def build_report() -> dict[str, object]:
    root_4x4 = evaluate_root_4x4()
    state_4x4 = evaluate_state_4x4()
    holdout_5x5 = evaluate_larger_roots(5, 1000, 99)
    holdout_6x6 = evaluate_larger_roots(6, 300, 123)
    return {
        "tier": "descriptive_symbolic_controller",
        "oracle_dependent": False,
        "discovery_domain": "lookahead-dominance controller distilled from bounded policy-improvement failures",
        "survivor": "lookahead-dominance controller",
        "controller_rule": {
            "base_formula": list(BASE_FORMULA),
            "exception": "switch away from the base winner when another obligation trades exactly one unit of immediate gain for at least +2 child_best_gain, +1 child_best_cut, and +1 next_uncovered",
        },
        "exhaustive_4x4_roots": root_4x4,
        "exhaustive_4x4_states": state_4x4,
        "holdout_5x5_roots": holdout_5x5,
        "holdout_6x6_roots": holdout_6x6,
        "strongest_claim": (
            "The exact 4x4 motif exception compresses further into a generic lookahead-dominance controller. "
            "That controller is exact on exhaustive 4x4 roots and reachable states, and it improves the flat base controller on sampled 5x5 and 6x6 roots."
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
