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


def pi2_selector(rel):
    pi0 = route_selector(rel)
    pi1 = improve_selector(rel, pi0)
    return improve_selector(rel, pi1)


def dominance_choice(rows, gain_loss: int, child_gain_min: int, child_cut_min: int, next_delta: int, next_mode: str):
    base_y = choose_by_formula(rows, BASE_FORMULA)
    by_y = {y: features for y, features in rows}
    base = by_y[base_y]
    alternatives = []
    for y, features in rows:
        if y == base_y:
            continue
        gain_ok = features["gain"] == base["gain"] - gain_loss
        child_gain_ok = features["child_best_gain"] >= base["child_best_gain"] + child_gain_min
        child_cut_ok = features["child_best_cut"] >= base["child_best_cut"] + child_cut_min
        if next_mode == "eq":
            next_ok = features["next_uncovered"] == base["next_uncovered"] + next_delta
        else:
            next_ok = features["next_uncovered"] >= base["next_uncovered"] + next_delta
        if gain_ok and child_gain_ok and child_cut_ok and next_ok:
            alternatives.append((-features["child_best_gain"], -features["child_best_cut"], features["gain"], y))
    if alternatives:
        return min(alternatives)[3]
    return base_y


def evaluate_clause_on_states(state_dataset, params):
    hits = 0
    for item in state_dataset:
        if dominance_choice(item["rows"], *params) == item["target"]:
            hits += 1
    return hits


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


def evaluate_clause_on_root_sample(root_dataset, params):
    hits = 0
    by_bucket = {}
    for item in root_dataset:
        if dominance_choice(item["rows"], *params) == item["target"]:
            hits += 1
            key = (item["n"], item["density"])
            by_bucket[key] = by_bucket.get(key, 0) + 1
    return hits, by_bucket


def build_report() -> dict[str, object]:
    state_dataset = collect_state_dataset()
    root_5 = sample_root_dataset(5, 1000, 99)
    root_6 = sample_root_dataset(6, 300, 123)
    total_states = len(state_dataset)
    total_5 = len(root_5)
    total_6 = len(root_6)

    clauses = []
    for gain_loss, child_gain_min, child_cut_min, next_delta, next_mode in product(
        [1],
        [1, 2, 3],
        [0, 1, 2],
        [1],
        ["eq", "ge"],
    ):
        params = (gain_loss, child_gain_min, child_cut_min, next_delta, next_mode)
        state_hits = evaluate_clause_on_states(state_dataset, params)
        hits_5, buckets_5 = evaluate_clause_on_root_sample(root_5, params)
        hits_6, buckets_6 = evaluate_clause_on_root_sample(root_6, params)
        clauses.append({
            "params": {
                "gain_loss": gain_loss,
                "child_gain_min": child_gain_min,
                "child_cut_min": child_cut_min,
                "next_delta": next_delta,
                "next_mode": next_mode,
            },
            "state_hits": state_hits,
            "state_total": total_states,
            "holdout_5_hits": hits_5,
            "holdout_5_total": total_5,
            "holdout_6_hits": hits_6,
            "holdout_6_total": total_6,
            "holdout_5_buckets": {f"{n}:{density}": count for (n, density), count in buckets_5.items()},
            "holdout_6_buckets": {f"{n}:{density}": count for (n, density), count in buckets_6.items()},
        })

    exact = [c for c in clauses if c["state_hits"] == total_states]
    exact.sort(key=lambda c: (-c["holdout_5_hits"] - c["holdout_6_hits"], -c["holdout_5_hits"], -c["holdout_6_hits"], c["params"]["gain_loss"], c["params"]["child_gain_min"], c["params"]["child_cut_min"], c["params"]["next_delta"], c["params"]["next_mode"]))
    all_ranked = sorted(
        clauses,
        key=lambda c: (-c["state_hits"], -c["holdout_5_hits"] - c["holdout_6_hits"], -c["holdout_5_hits"], -c["holdout_6_hits"]),
    )

    return {
        "tier": "descriptive_symbolic_controller",
        "oracle_dependent": False,
        "discovery_domain": "search over a small family of lookahead-dominance clauses",
        "survivor": "dominance-clause family frontier",
        "state_total": total_states,
        "holdout_5_total": total_5,
        "holdout_6_total": total_6,
        "searched_clause_count": len(clauses),
        "exact_on_4x4_state_count": len(exact),
        "best_exact_clause": exact[0] if exact else None,
        "top_exact_clauses": exact[:10],
        "top_overall_clauses": all_ranked[:10],
        "strongest_claim": (
            "The mined lookahead-dominance controller is not an isolated exact clause. "
            "A small family of nearby dominance clauses stays exact on exhaustive 4x4 states, and some members generalize better than others on larger sampled roots."
        ) if exact else (
            "Within the searched family, no clause stayed exact on exhaustive 4x4 states."
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
