#!/usr/bin/env python3
from __future__ import annotations

import json
from functools import lru_cache
from itertools import combinations
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
RANK_ORDER = {
    "cut_next": 0,
    "cut_next_childsum": 1,
    "cut_childsum_next": 2,
    "cut_bestsingleton_next": 3,
}
ORIGIN_ORDER = {
    "any": 0,
    "core": 1,
    "repair": 2,
}


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


def pair_feature(pair):
    p1, p2 = map(denorm, pair)
    return {
        "simplicity": sum(
            p1[key]
            for key in (
                "cut_gain_min",
                "next_size_drop_min",
                "max_child_cut_drop",
                "min_child_sum_drop",
                "min_child_best_singleton_gain",
            )
        )
        + sum(
            p2[key]
            for key in (
                "cut_gain_min",
                "next_size_drop_min",
                "max_child_cut_drop",
                "min_child_sum_drop",
                "min_child_best_singleton_gain",
            )
        ),
        "singleton": p1["min_child_best_singleton_gain"] + p2["min_child_best_singleton_gain"],
        "childsum": p1["min_child_sum_drop"] + p2["min_child_sum_drop"],
        "cut": p1["cut_gain_min"] + p2["cut_gain_min"],
        "nextdrop": p1["next_size_drop_min"] + p2["next_size_drop_min"],
        "rankscore": RANK_ORDER[p1["rank"]] + RANK_ORDER[p2["rank"]],
    }


def proposer_family():
    return {
        "lex": lambda pair: pair,
        "singleton": lambda pair: (
            -pair_feature(pair)["singleton"],
            pair_feature(pair)["simplicity"],
            -pair_feature(pair)["rankscore"],
            pair,
        ),
        "childsum": lambda pair: (
            -pair_feature(pair)["childsum"],
            pair_feature(pair)["simplicity"],
            -pair_feature(pair)["rankscore"],
            pair,
        ),
        "aggressive": lambda pair: (
            -(pair_feature(pair)["cut"] + pair_feature(pair)["nextdrop"]),
            pair_feature(pair)["simplicity"],
            -pair_feature(pair)["singleton"],
            pair,
        ),
        "bestsingleton_rank": lambda pair: (
            -pair_feature(pair)["rankscore"],
            -pair_feature(pair)["singleton"],
            pair_feature(pair)["simplicity"],
            pair,
        ),
    }


def build_pair_space():
    residual = holdout_residual_cases()
    candidates = []
    for params in parameter_grid():
        fixed = tuple(int(choose_by_tie_break(item["rows"], params) == item["target"]) for item in residual)
        if any(fixed):
            candidates.append((params, fixed))
    second_slot = [params for params, _fixed in candidates if params["origin_guard"] == "any"]
    pairs = []
    for p1, _fixed in candidates:
        for p2 in second_slot:
            if all(pair_choice(item["rows"], p1, p2) == item["target"] for item in residual):
                pairs.append((norm(p1), norm(p2)))
    return pairs


@lru_cache(None)
def verifier_state_bank():
    return {
        (item["mask"], tuple(item["candidates"]), item["target"]): item
        for item in collect_state_dataset()
    }


@lru_cache(None)
def verify(pair):
    for item in verifier_state_bank().values():
        if pair_choice(item["rows"], pair[0], pair[1]) != item["target"]:
            return False, (item["mask"], tuple(item["candidates"]), item["target"])
    return True, None


def consistent_with_bank(pair, bank):
    for counterexample in bank:
        item = verifier_state_bank()[counterexample]
        if pair_choice(item["rows"], pair[0], pair[1]) != item["target"]:
            return False
    return True


def simulate_single(name, ordered_pairs):
    root_5 = sample_root_dataset(5, 1000, 99)
    root_6 = sample_root_dataset(6, 300, 123)
    bank = []
    calls = 0
    for pair in ordered_pairs:
        if not consistent_with_bank(pair, bank):
            continue
        calls += 1
        ok, counterexample = verify(pair)
        if ok:
            return {
                "calls": calls,
                "bank_size": len(bank),
                "holdout_5_hits": sum(1 for item in root_5 if pair_choice(item["rows"], pair[0], pair[1]) == item["target"]),
                "holdout_6_hits": sum(1 for item in root_6 if pair_choice(item["rows"], pair[0], pair[1]) == item["target"]),
                "safe_pair": {
                    "clause_1": denorm(pair[0]),
                    "clause_2": denorm(pair[1]),
                },
            }
        bank.append(counterexample)
    raise AssertionError(f"no safe pair found for proposer {name}")


def simulate_portfolio(name_a, ordered_a, name_b, ordered_b):
    root_5 = sample_root_dataset(5, 1000, 99)
    root_6 = sample_root_dataset(6, 300, 123)
    bank = []
    seen = set()
    idx_a = 0
    idx_b = 0
    calls = 0
    rounds = 0

    while rounds < 32:
        rounds += 1
        batch = []
        while idx_a < len(ordered_a):
            pair = ordered_a[idx_a]
            idx_a += 1
            if pair in seen or not consistent_with_bank(pair, bank):
                continue
            batch.append(pair)
            seen.add(pair)
            break
        while idx_b < len(ordered_b):
            pair = ordered_b[idx_b]
            idx_b += 1
            if pair in seen or not consistent_with_bank(pair, bank):
                continue
            batch.append(pair)
            seen.add(pair)
            break
        if not batch:
            break
        for pair in batch:
            calls += 1
            ok, counterexample = verify(pair)
            if ok:
                return {
                    "calls": calls,
                    "rounds": rounds,
                    "bank_size": len(bank),
                    "holdout_5_hits": sum(1 for item in root_5 if pair_choice(item["rows"], pair[0], pair[1]) == item["target"]),
                    "holdout_6_hits": sum(1 for item in root_6 if pair_choice(item["rows"], pair[0], pair[1]) == item["target"]),
                    "safe_pair": {
                        "clause_1": denorm(pair[0]),
                        "clause_2": denorm(pair[1]),
                    },
                }
            bank.append(counterexample)
    raise AssertionError(f"no safe pair found for portfolio {name_a}+{name_b}")


def build_report():
    pairs = build_pair_space()
    proposers = proposer_family()
    ordered = {name: sorted(pairs, key=key_fn) for name, key_fn in proposers.items()}

    singles = {}
    for name, ordered_pairs in ordered.items():
        singles[name] = simulate_single(name, ordered_pairs)

    portfolios = {}
    for name_a, name_b in combinations(proposers.keys(), 2):
        portfolios[f"{name_a}+{name_b}"] = simulate_portfolio(
            name_a, ordered[name_a], name_b, ordered[name_b]
        )

    best_single_name = min(singles, key=lambda name: (singles[name]["calls"], singles[name]["bank_size"], name))
    best_portfolio_name = min(
        portfolios,
        key=lambda name: (portfolios[name]["calls"], portfolios[name]["rounds"], portfolios[name]["bank_size"], name),
    )

    return {
        "tier": "descriptive_symbolic_controller",
        "oracle_dependent": False,
        "discovery_domain": "multi-proposer search over residual-consistent repair-program pairs with a shared exhaustive 4x4 verifier bank",
        "survivor": "shared-bank multi-proposer frontier",
        "pair_count": len(pairs),
        "single_proposers": singles,
        "portfolios": portfolios,
        "best_single_proposer": {
            "name": best_single_name,
            **singles[best_single_name],
        },
        "best_two_proposer_portfolio": {
            "name": best_portfolio_name,
            **portfolios[best_portfolio_name],
        },
        "strongest_claim": (
            "In this bounded repair-program search, proposer multiplicity helps only when it adds ranking diversity. "
            "A shared counterexample bank lets all proposers reuse refutations, but the best single proposer still dominates most portfolios in exact verifier calls."
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
