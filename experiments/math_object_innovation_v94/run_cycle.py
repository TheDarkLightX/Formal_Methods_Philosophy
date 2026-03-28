#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import dataclass
from itertools import product
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "generated" / "report.json"


GUARDS = ("ignore_flag", "return_neg7", "return_neg8")
BOUNDS = ("reject_negative", "clamp_zero", "absolute_value")
TRANSFORMS_SEPARABLE = ("identity", "square", "cube")
TRANSFORMS_COUPLED = ("identity", "add_one", "square")

TESTS = (
    ("guard", True, 0),
    ("bounds", False, -1),
    ("transform", False, 2),
)


@dataclass(frozen=True)
class Patch:
    guard: str
    bounds: str
    transform: str


def apply_guard(guard: str, flag: bool) -> int | None:
    if not flag:
        return None
    if guard == "return_neg7":
        return -7
    if guard == "return_neg8":
        return -8
    return None


def apply_bounds(bounds: str, value: int) -> int:
    if value >= 0:
        return value
    if bounds == "reject_negative":
        return -9
    if bounds == "clamp_zero":
        return 0
    if bounds == "absolute_value":
        return abs(value)
    raise ValueError(bounds)


def apply_transform(transform: str, value: int) -> int:
    if transform == "identity":
        return value
    if transform == "square":
        return value * value
    if transform == "cube":
        return value * value * value
    if transform == "add_one":
        return value + 1
    raise ValueError(transform)


def run_patch(patch: Patch, flag: bool, value: int) -> int:
    guard_value = apply_guard(patch.guard, flag)
    if guard_value is not None:
        return guard_value
    bounded = apply_bounds(patch.bounds, value)
    if bounded == -9:
        return -9
    return apply_transform(patch.transform, bounded)


def patch_family(transforms: tuple[str, ...]) -> list[Patch]:
    return [Patch(g, b, t) for g, b, t in product(GUARDS, BOUNDS, transforms)]


def greedy_monolithic_cost(gold: Patch, family: list[Patch]) -> tuple[int, tuple[str, ...]]:
    outputs = {(name, flag, value): run_patch(gold, flag, value) for name, flag, value in TESTS}
    remaining = set(family)
    unused = list(TESTS)
    order: list[str] = []
    cost = 0
    while len(remaining) > 1 and unused:
        best = None
        best_eliminated = -1
        for test in unused:
            expected = outputs[test]
            eliminated = sum(1 for patch in remaining if run_patch(patch, test[1], test[2]) != expected)
            if eliminated > best_eliminated:
                best_eliminated = eliminated
                best = test
        assert best is not None
        cost += len(remaining)
        expected = outputs[best]
        remaining = {patch for patch in remaining if run_patch(patch, best[1], best[2]) == expected}
        unused.remove(best)
        order.append(best[0])
    return cost, tuple(order)


def local_guard_candidates(gold: Patch) -> tuple[set[str], int]:
    _, flag, value = TESTS[0]
    expected = run_patch(gold, flag, value)
    keep = {guard for guard in GUARDS if run_patch(Patch(guard, "clamp_zero", "identity"), flag, value) == expected}
    return keep, len(GUARDS)


def dependent_guard_candidates(gold: Patch, known_transform: str) -> tuple[set[str], int]:
    _, flag, value = TESTS[0]
    expected = run_patch(gold, flag, value)
    keep = {guard for guard in GUARDS if run_patch(Patch(guard, "clamp_zero", known_transform), flag, value) == expected}
    return keep, len(GUARDS)


def local_transform_candidates(gold: Patch, transforms: tuple[str, ...]) -> tuple[set[str], int]:
    _, flag, value = TESTS[2]
    expected = run_patch(gold, flag, value)
    keep = {transform for transform in transforms if run_patch(Patch("ignore_flag", "absolute_value", transform), flag, value) == expected}
    return keep, len(transforms)


def naive_bounds_candidates(gold: Patch, transforms: tuple[str, ...]) -> tuple[set[str], int]:
    _, flag, value = TESTS[1]
    expected = run_patch(gold, flag, value)
    keep = set()
    evals = 0
    for bounds in BOUNDS:
        for transform in transforms:
            evals += 1
            if run_patch(Patch("ignore_flag", bounds, transform), flag, value) == expected:
                keep.add(bounds)
    return keep, evals


def dependent_bounds_candidates(gold: Patch, known_transform: str) -> tuple[set[str], int]:
    _, flag, value = TESTS[1]
    expected = run_patch(gold, flag, value)
    keep = {bounds for bounds in BOUNDS if run_patch(Patch("ignore_flag", bounds, known_transform), flag, value) == expected}
    return keep, len(BOUNDS)


def summarize_family(name: str, transforms: tuple[str, ...]) -> dict[str, object]:
    family = patch_family(transforms)
    monolithic_costs = []
    monolithic_orders = {}
    naive_exact = 0
    dependency_exact = 0
    naive_costs = []
    dependency_costs = []
    naive_ambiguous_examples: list[dict[str, object]] = []

    for gold in family:
        monolithic_cost, order = greedy_monolithic_cost(gold, family)
        monolithic_costs.append(monolithic_cost)
        monolithic_orders[order] = monolithic_orders.get(order, 0) + 1

        guard_keep, guard_cost = local_guard_candidates(gold)
        transform_keep, transform_cost = local_transform_candidates(gold, transforms)
        bounds_keep_naive, bounds_cost_naive = naive_bounds_candidates(gold, transforms)

        naive_products = {
            Patch(guard, bounds, transform)
            for guard, bounds, transform in product(guard_keep, bounds_keep_naive, transform_keep)
        }
        naive_exact_match = naive_products == {gold}
        if naive_exact_match:
            naive_exact += 1
        elif len(naive_ambiguous_examples) < 5:
            naive_ambiguous_examples.append(
                {
                    "gold": {"guard": gold.guard, "bounds": gold.bounds, "transform": gold.transform},
                    "naive_guard_keep": sorted(guard_keep),
                    "naive_bounds_keep": sorted(bounds_keep_naive),
                    "naive_transform_keep": sorted(transform_keep),
                    "naive_product_size": len(naive_products),
                }
            )
        naive_costs.append(guard_cost + bounds_cost_naive + transform_cost)

        # Dependency-aware search: solve transform first, then both guard and bounds conditioned on it.
        assert len(transform_keep) == 1
        known_transform = next(iter(transform_keep))
        guard_keep_dep, guard_cost_dep = dependent_guard_candidates(gold, known_transform)
        bounds_keep_dep, bounds_cost_dep = dependent_bounds_candidates(gold, known_transform)
        dependency_products = {
            Patch(guard, bounds, transform)
            for guard, bounds, transform in product(guard_keep_dep, bounds_keep_dep, transform_keep)
        }
        if dependency_products == {gold}:
            dependency_exact += 1
        dependency_costs.append(guard_cost_dep + bounds_cost_dep + transform_cost)

    best_order = max(monolithic_orders.items(), key=lambda item: item[1])[0]

    return {
        "family": name,
        "candidate_count": len(family),
        "monolithic_average_eval_cost": sum(monolithic_costs) / len(monolithic_costs),
        "monolithic_worst_eval_cost": max(monolithic_costs),
        "monolithic_common_test_order": list(best_order),
        "naive_fiber_average_eval_cost": sum(naive_costs) / len(naive_costs),
        "naive_fiber_exact_gold_count": naive_exact,
        "naive_fiber_exact_gold_ratio": naive_exact / len(family),
        "naive_ambiguous_examples": naive_ambiguous_examples,
        "dependency_fiber_average_eval_cost": sum(dependency_costs) / len(dependency_costs),
        "dependency_fiber_exact_gold_count": dependency_exact,
        "dependency_fiber_exact_gold_ratio": dependency_exact / len(family),
    }


def build_report() -> dict[str, object]:
    separable = summarize_family("separable_patch_family", TRANSFORMS_SEPARABLE)
    coupled = summarize_family("overlap_patch_family", TRANSFORMS_COUPLED)
    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "bounded software-engineering patch corpora with three edit sites "
            "(guard, bounds, transform), compared under monolithic patch search, "
            "naive obligation-fibered repair, and dependency-aware obligation-fibered repair"
        ),
        "holdout_domain": "exhaustive over both 27-patch corpora and all gold patches inside each corpus",
        "survivor": "dependency-aware obligation-fibered repair",
        "strongest_claim": (
            "On a bounded patch corpus with overlapping failure fibers, naive independent fiber repair stops being exact, "
            "but a dependency-aware fiber loop that solves transform before bounds regains exactness while preserving the "
            "low local evaluation cost that makes fibered repair attractive."
        ),
        "families": [separable, coupled],
        "software_loop_ranking_hint": [
            "obligation_fibered_repair",
            "certificate_carrying_repair",
            "minimal_repair_language_discovery",
        ],
    }


def main() -> int:
    report = build_report()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
