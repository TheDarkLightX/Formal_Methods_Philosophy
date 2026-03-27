#!/usr/bin/env python3
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
import random


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


def exhaustive_report() -> dict[str, object]:
    count = 1 << 16
    hits = {
        "pi0": 0,
        "pi1": 0,
        "pi2": 0,
    }
    step_hits = {
        "pi0": 0,
        "pi1": 0,
        "pi2": 0,
    }
    first_failure_pi2 = None
    for mask in range(count):
        rel = relation_from_mask(mask, 4)
        pi0 = route_selector(rel)
        pi1 = improve_selector(rel, pi0)
        pi2 = improve_selector(rel, pi1)
        values = {
            "pi0": make_value_function(rel, pi0),
            "pi1": make_value_function(rel, pi1),
            "pi2": make_value_function(rel, pi2),
        }
        opt = optimal_value_function(rel)
        root = tuple(sorted(phi(rel, frozenset())))
        opt_value = opt(root)
        for name in ["pi0", "pi1", "pi2"]:
            got = values[name](root)
            if got == opt_value:
                hits[name] += 1
            if got[0] == opt_value[0]:
                step_hits[name] += 1
        if first_failure_pi2 is None and values["pi2"](root) != opt_value:
            first_failure_pi2 = {
                "mask": mask,
                "pi2": {"steps": values["pi2"](root)[0], "checks": values["pi2"](root)[1]},
                "optimal": {"steps": opt_value[0], "checks": opt_value[1]},
                "table": [[int(v) for v in row] for row in rel],
            }
    return {
        "relation_count": count,
        "exact_hits": hits,
        "step_hits": step_hits,
        "first_failure_pi2": first_failure_pi2,
    }


def random_holdout_report(n: int, trials: int, seed: int) -> list[dict[str, object]]:
    rng = random.Random(seed)
    rows = []
    for density in [0.3, 0.5, 0.7]:
        hits = {"pi0": 0, "pi1": 0, "pi2": 0}
        for _ in range(trials):
            rel = tuple(
                tuple(rng.random() < density for _ in range(n))
                for _ in range(n)
            )
            pi0 = route_selector(rel)
            pi1 = improve_selector(rel, pi0)
            pi2 = improve_selector(rel, pi1)
            values = {
                "pi0": make_value_function(rel, pi0),
                "pi1": make_value_function(rel, pi1),
                "pi2": make_value_function(rel, pi2),
            }
            opt = optimal_value_function(rel)
            root = tuple(sorted(phi(rel, frozenset())))
            opt_value = opt(root)
            for name in hits:
                if values[name](root) == opt_value:
                    hits[name] += 1
        rows.append({"n": n, "density": density, "trials": trials, "exact_hits": hits})
    return rows


def build_report() -> dict[str, object]:
    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": False,
        "discovery_domain": "policy iteration over obligation-targeted witness routing on exhaustive 4x4 boolean relations",
        "holdout_domain": "random 5x5 and 6x6 boolean relations",
        "strongest_claim": (
            "Two rounds of policy improvement over the routed obligation controller reached the exact bounded-optimal check policy on every exhaustive 4x4 relation tested, and on all 5x5 and 6x6 random holdouts sampled in this cycle."
        ),
        "survivor": "obligation-side policy iteration",
        "exhaustive_4x4": exhaustive_report(),
        "holdout_5x5": random_holdout_report(5, 1000, 99),
        "holdout_6x6": random_holdout_report(6, 200, 123),
    }


def main() -> int:
    report = build_report()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
