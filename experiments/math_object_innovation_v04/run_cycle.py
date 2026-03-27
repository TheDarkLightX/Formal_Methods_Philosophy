#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
import random
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "generated" / "report.json"


def spec(rel: tuple[tuple[bool, ...], ...], x: int, y: int) -> bool:
    return rel[x][y]


def relation_from_mask(mask: int, n: int) -> tuple[tuple[bool, ...], ...]:
    table = []
    bit = 0
    for _ in range(n):
        row = []
        for _ in range(n):
            row.append(bool((mask >> bit) & 1))
            bit += 1
        table.append(tuple(row))
    return tuple(table)


def phi(rel: tuple[tuple[bool, ...], ...], obligations: frozenset[int]) -> frozenset[int]:
    return frozenset(
        x for x in range(len(rel))
        if all(spec(rel, x, y) for y in obligations)
    )


def psi(rel: tuple[tuple[bool, ...], ...], candidates: frozenset[int]) -> frozenset[int]:
    return frozenset(
        y for y in range(len(rel[0]))
        if all(spec(rel, x, y) for x in candidates)
    )


def route_key(rel: tuple[tuple[bool, ...], ...], candidates: frozenset[int], y: int) -> tuple[int, int]:
    witnesses = [x for x in candidates if not spec(rel, x, y)]
    return min((-len(psi(rel, frozenset({x}))), x) for x in witnesses)


def route_selector(rel: tuple[tuple[bool, ...], ...]):
    def sel(candidates: frozenset[int], uncovered: frozenset[int], _value_fn):
        current_closed = len(psi(rel, candidates))
        choices = []
        for y in uncovered:
            witnesses = [x for x in candidates if not spec(rel, x, y)]
            if not witnesses:
                continue
            next_candidates = frozenset(z for z in candidates if spec(rel, z, y))
            gain = len(psi(rel, next_candidates)) - current_closed
            rk = route_key(rel, candidates, y)
            key = (rk[0], -gain, len(next_candidates), rk[1], y)
            choices.append((key, y))
        return min(choices)[1]
    return sel


def make_value_function(rel: tuple[tuple[bool, ...], ...], selector):
    all_obligations = frozenset(range(len(rel[0])))

    @lru_cache(None)
    def value(candidates_tuple: tuple[int, ...]) -> tuple[int, int]:
        candidates = frozenset(candidates_tuple)
        if not candidates:
            return (0, 0)
        uncovered = all_obligations - psi(rel, candidates)
        base_checks = len(uncovered)
        if not uncovered:
            return (0, base_checks)
        y = selector(candidates, uncovered, value)
        next_candidates = frozenset(z for z in candidates if spec(rel, z, y))
        tail_steps, tail_checks = value(tuple(sorted(next_candidates)))
        return (1 + tail_steps, base_checks + tail_checks)

    return value


def improve_selector(rel: tuple[tuple[bool, ...], ...], base_selector):
    base_value = make_value_function(rel, base_selector)

    def sel(candidates: frozenset[int], uncovered: frozenset[int], _value_fn):
        best = None
        for y in uncovered:
            next_candidates = frozenset(z for z in candidates if spec(rel, z, y))
            tail_steps, tail_checks = base_value(tuple(sorted(next_candidates)))
            key = (1 + tail_steps, len(uncovered) + tail_checks, y)
            if best is None or key < best:
                best = key
        return best[2]

    return sel


def optimal_value_function(rel: tuple[tuple[bool, ...], ...]):
    all_obligations = frozenset(range(len(rel[0])))

    @lru_cache(None)
    def value(candidates_tuple: tuple[int, ...]) -> tuple[int, int]:
        candidates = frozenset(candidates_tuple)
        if not candidates:
            return (0, 0)
        uncovered = all_obligations - psi(rel, candidates)
        base_checks = len(uncovered)
        if not uncovered:
            return (0, base_checks)
        best = None
        for y in uncovered:
            next_candidates = frozenset(z for z in candidates if spec(rel, z, y))
            tail_steps, tail_checks = value(tuple(sorted(next_candidates)))
            key = (1 + tail_steps, base_checks + tail_checks)
            if best is None or key < best:
                best = key
        return best

    return value


def best_pi2_choice(rel: tuple[tuple[bool, ...], ...], candidates: frozenset[int]) -> int:
    all_obligations = frozenset(range(len(rel[0])))
    uncovered = all_obligations - psi(rel, candidates)
    pi0 = route_selector(rel)
    pi1 = improve_selector(rel, pi0)
    pi2 = improve_selector(rel, pi1)
    value = make_value_function(rel, pi2)
    return pi2(candidates, uncovered, value)


def best_opt_choice(rel: tuple[tuple[bool, ...], ...], candidates: frozenset[int]) -> int:
    all_obligations = frozenset(range(len(rel[0])))
    uncovered = all_obligations - psi(rel, candidates)
    opt = optimal_value_function(rel)
    best = None
    for y in uncovered:
        next_candidates = frozenset(z for z in candidates if spec(rel, z, y))
        tail_steps, tail_checks = opt(tuple(sorted(next_candidates)))
        key = (1 + tail_steps, len(uncovered) + tail_checks, y)
        if best is None or key < best:
            best = key
    return best[2]


def feature_vector(rel: tuple[tuple[bool, ...], ...], candidates: frozenset[int], y: int) -> dict[str, int]:
    current_closed = psi(rel, candidates)
    current_uncovered = frozenset(range(len(rel[0]))) - current_closed
    next_candidates = frozenset(z for z in candidates if spec(rel, z, y))
    next_closed = psi(rel, next_candidates)
    next_uncovered = frozenset(range(len(rel[0]))) - next_closed
    witnesses = [x for x in candidates if not spec(rel, x, y)]
    witness_singletons = [len(psi(rel, frozenset({x}))) for x in witnesses]
    child_singletons = [len(psi(rel, frozenset({x}))) for x in next_candidates] or [0]
    next_gains = []
    next_cuts = []
    for y2 in next_uncovered:
        next_candidates2 = frozenset(z for z in next_candidates if spec(rel, z, y2))
        next_gains.append(len(psi(rel, next_candidates2)) - len(next_closed))
        next_cuts.append(len(next_candidates) - len(next_candidates2))
    return {
        "next_size": len(next_candidates),
        "next_uncovered": len(next_uncovered),
        "gain": len(next_closed) - len(current_closed),
        "cut": len(candidates) - len(next_candidates),
        "witness_best_singleton": max(witness_singletons),
        "witness_worst_singleton": min(witness_singletons),
        "child_best_singleton": max(child_singletons),
        "child_sum_singleton": sum(child_singletons),
        "child_best_gain": max(next_gains) if next_gains else 0,
        "child_best_cut": max(next_cuts) if next_cuts else 0,
        "y": y,
    }


def signed_feature_names() -> list[tuple[str, str]]:
    base = [
        "next_size",
        "next_uncovered",
        "gain",
        "cut",
        "witness_best_singleton",
        "witness_worst_singleton",
        "child_best_singleton",
        "child_sum_singleton",
        "child_best_gain",
        "child_best_cut",
    ]
    names = []
    for item in base:
        names.append((item, f"min_{item}"))
        names.append((f"neg:{item}", f"max_{item}"))
    return names


def signed_value(features: dict[str, int], name: str) -> int:
    if name.startswith("neg:"):
        return -features[name.split(":", 1)[1]]
    return features[name]


def choose_by_formula(rows: list[tuple[int, dict[str, int]]], formula: tuple[str, ...]) -> int:
    best = None
    best_y = None
    for y, features in rows:
        key = tuple(signed_value(features, name) for name in formula) + (y,)
        if best is None or key < best:
            best = key
            best_y = y
    return best_y


def collect_root_dataset(n: int = 4) -> list[dict[str, object]]:
    dataset = []
    for mask in range(1 << (n * n)):
        rel = relation_from_mask(mask, n)
        candidates = phi(rel, frozenset())
        uncovered = frozenset(range(n)) - psi(rel, candidates)
        if not uncovered:
            continue
        rows = [(y, feature_vector(rel, candidates, y)) for y in uncovered]
        dataset.append({
            "mask": mask,
            "rows": rows,
            "target_pi2": best_pi2_choice(rel, candidates),
            "target_opt": best_opt_choice(rel, candidates),
        })
    return dataset


def sample_dataset(dataset: list[dict[str, object]], size: int, seed: int) -> list[dict[str, object]]:
    rng = random.Random(seed)
    if size >= len(dataset):
        return list(dataset)
    indices = list(range(len(dataset)))
    rng.shuffle(indices)
    return [dataset[i] for i in indices[:size]]


def score_formula(dataset: list[dict[str, object]], target_key: str, formula: tuple[str, ...]) -> dict[str, object]:
    hits = 0
    for item in dataset:
        chosen = choose_by_formula(item["rows"], formula)
        if chosen == item[target_key]:
            hits += 1
    return {
        "raw_formula": list(formula),
        "hits": hits,
        "total": len(dataset),
    }


def search_formulas(
    dataset: list[dict[str, object]],
    target_key: str,
    max_len: int = 3,
    beam_width: int = 8,
    top_k: int = 32,
) -> tuple[list[dict[str, object]], int]:
    signed = signed_feature_names()
    raw_names = [name for name, _label in signed]
    label_map = {name: label for name, label in signed}
    explored = 0
    layer = [tuple([name]) for name in raw_names]
    frontier: list[tuple[str, ...]] = []
    scored_map: dict[tuple[str, ...], dict[str, object]] = {}
    for depth in range(1, max_len + 1):
        layer_scores = []
        for formula in layer:
            explored += 1
            scored = score_formula(dataset, target_key, formula)
            scored_map[formula] = scored
            layer_scores.append((scored["hits"], formula))
        layer_scores.sort(key=lambda item: (-item[0], len(item[1]), [label_map[name] for name in item[1]]))
        best_layer = [formula for _hits, formula in layer_scores[:beam_width]]
        frontier.extend(best_layer)
        next_layer = []
        for formula in best_layer:
            used = set(formula)
            for name in raw_names:
                if name in used:
                    continue
                next_layer.append(formula + (name,))
        layer = next_layer
    scored = []
    for formula in dict.fromkeys(frontier):
        item = scored_map.get(formula)
        if item is None:
            item = score_formula(dataset, target_key, formula)
            explored += 1
        scored.append({
            "formula": [label_map[name] for name in formula],
            "raw_formula": list(formula),
            "hits": item["hits"],
            "total": item["total"],
        })
    scored.sort(key=lambda item: (-item["hits"], len(item["formula"]), item["formula"]))
    return scored[:top_k], explored


def validate_formulas(dataset: list[dict[str, object]], formulas: list[dict[str, object]], target_key: str) -> list[dict[str, object]]:
    validated = []
    for item in formulas:
        raw = tuple(item["raw_formula"])
        hits = 0
        first_failure = None
        for row in dataset:
            chosen = choose_by_formula(row["rows"], raw)
            if chosen == row[target_key]:
                hits += 1
            elif first_failure is None:
                first_failure = {
                    "mask": row["mask"],
                    "chosen": chosen,
                    "target": row[target_key],
                }
        validated.append({
            "formula": item["formula"],
            "hits": hits,
            "total": len(dataset),
            "first_failure": first_failure,
        })
    validated.sort(key=lambda item: (-item["hits"], len(item["formula"]), item["formula"]))
    return validated


def build_report() -> dict[str, object]:
    exhaustive = collect_root_dataset(4)
    sample = sample_dataset(exhaustive, size=2048, seed=17)
    top_pi2, explored_pi2 = search_formulas(sample, "target_pi2")
    top_opt, explored_opt = search_formulas(sample, "target_opt")
    validated_pi2 = validate_formulas(exhaustive, top_pi2[:12], "target_pi2")
    validated_opt = validate_formulas(exhaustive, top_opt[:12], "target_opt")
    best_pi2 = validated_pi2[0]
    best_opt = validated_opt[0]
    return {
        "tier": "frontier_probe",
        "oracle_dependent": False,
        "discovery_domain": "controller compression for improved obligation policies on exhaustive 4x4 roots",
        "survivor": "controller compression frontier",
        "dataset_size": len(exhaustive),
        "sample_size": len(sample),
        "search_family": {
            "formula_depth_max": 3,
            "feature_count": 10,
            "signed_feature_count": 20,
            "beam_width": 8,
            "explored_formulas_pi2": explored_pi2,
            "explored_formulas_opt": explored_opt,
        },
        "best_pi2_formula": best_pi2,
        "best_opt_formula": best_opt,
        "top_pi2_formulas": validated_pi2[:5],
        "top_opt_formulas": validated_opt[:5],
        "strongest_claim": (
            "Within the tested family of local lexicographic obligation scores of depth at most 3, "
            "no direct score exactly reproduced the improved controller on exhaustive 4x4 roots. "
            "The best formulas came close, which turns controller compression into the next concrete frontier."
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
