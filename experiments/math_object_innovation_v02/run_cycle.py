#!/usr/bin/env python3
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
import random


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "generated" / "report.json"


def relation_from_mask(x_size: int, y_size: int, mask: int) -> tuple[tuple[bool, ...], ...]:
    table = []
    bit = 0
    for _ in range(x_size):
        row = []
        for _ in range(y_size):
            row.append(bool((mask >> bit) & 1))
            bit += 1
        table.append(tuple(row))
    return tuple(table)


def spec(rel: tuple[tuple[bool, ...], ...], x: int, y: int) -> bool:
    return rel[x][y]


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


def pair_policy(rel: tuple[tuple[bool, ...], ...]) -> tuple[int, int]:
    y_all = frozenset(range(len(rel[0])))
    candidates = phi(rel, frozenset())
    steps = 0
    checks = 0
    while candidates:
        uncovered = y_all - psi(rel, candidates)
        checks += len(uncovered)
        if not uncovered:
            return steps, checks
        current_closed = len(psi(rel, candidates))
        pairs = []
        for x in candidates:
            sx = len(psi(rel, frozenset({x})))
            for y in uncovered:
                if not spec(rel, x, y):
                    next_candidates = frozenset(z for z in candidates if spec(rel, z, y))
                    gain = len(psi(rel, next_candidates)) - current_closed
                    key = (-sx, -gain, len(next_candidates), x, y)
                    pairs.append((key, x, y))
        _key, _x, y = min(pairs)
        candidates = frozenset(z for z in candidates if spec(rel, z, y))
        steps += 1
    return steps, checks


def route_policy(rel: tuple[tuple[bool, ...], ...]) -> tuple[int, int]:
    y_all = frozenset(range(len(rel[0])))
    candidates = phi(rel, frozenset())
    steps = 0
    checks = 0
    while candidates:
        uncovered = y_all - psi(rel, candidates)
        checks += len(uncovered)
        if not uncovered:
            return steps, checks
        current_closed = len(psi(rel, candidates))
        choices = []
        for y in uncovered:
            witnesses = [x for x in candidates if not spec(rel, x, y)]
            if not witnesses:
                continue
            next_candidates = frozenset(z for z in candidates if spec(rel, z, y))
            gain = len(psi(rel, next_candidates)) - current_closed
            best_w = route_key(rel, candidates, y)
            key = (best_w[0], -gain, len(next_candidates), best_w[1], y)
            choices.append((key, y))
        _key, y = min(choices)
        candidates = frozenset(z for z in candidates if spec(rel, z, y))
        steps += 1
    return steps, checks


def optimal_y_policy(rel: tuple[tuple[bool, ...], ...]) -> tuple[int, int]:
    y_all = frozenset(range(len(rel[0])))

    @lru_cache(None)
    def best(candidates_tuple: tuple[int, ...]) -> tuple[int, int]:
        candidates = frozenset(candidates_tuple)
        if not candidates:
            return (0, 0)
        uncovered = y_all - psi(rel, candidates)
        base_checks = len(uncovered)
        if not uncovered:
            return (0, base_checks)
        answer = None
        for y in uncovered:
            next_candidates = frozenset(z for z in candidates if spec(rel, z, y))
            tail_steps, tail_checks = best(tuple(sorted(next_candidates)))
            pair = (1 + tail_steps, base_checks + tail_checks)
            if answer is None or pair < answer:
                answer = pair
        return answer

    return best(tuple(sorted(phi(rel, frozenset()))))


def exhaustive_report() -> dict[str, object]:
    count = 1 << 16
    pair_matches_route = 0
    pair_matches_opt_steps = 0
    pair_matches_opt_checks = 0
    first_opt_failure = None
    for mask in range(count):
        rel = relation_from_mask(4, 4, mask)
        pair_cost = pair_policy(rel)
        route_cost = route_policy(rel)
        opt_cost = optimal_y_policy(rel)
        if pair_cost == route_cost:
            pair_matches_route += 1
        if pair_cost[0] == opt_cost[0]:
            pair_matches_opt_steps += 1
        elif first_opt_failure is None:
            first_opt_failure = {
                "mask": mask,
                "pair_cost": {"steps": pair_cost[0], "checks": pair_cost[1]},
                "opt_cost": {"steps": opt_cost[0], "checks": opt_cost[1]},
                "table": [[int(v) for v in row] for row in rel],
            }
        if pair_cost[1] == opt_cost[1]:
            pair_matches_opt_checks += 1
    return {
        "relation_count": count,
        "pair_matches_route": pair_matches_route,
        "pair_matches_opt_steps": pair_matches_opt_steps,
        "pair_matches_opt_checks": pair_matches_opt_checks,
        "first_opt_failure": first_opt_failure,
    }


def random_holdout_report() -> list[dict[str, object]]:
    rng = random.Random(17)
    rows = []
    for density in [0.3, 0.5, 0.7]:
        pair_route_equal = 0
        pair_opt_steps = 0
        pair_opt_checks = 0
        trials = 1000
        for _ in range(trials):
            rel = tuple(
                tuple(rng.random() < density for _ in range(5))
                for _ in range(5)
            )
            pair_cost = pair_policy(rel)
            route_cost = route_policy(rel)
            opt_cost = optimal_y_policy(rel)
            if pair_cost == route_cost:
                pair_route_equal += 1
            if pair_cost[0] == opt_cost[0]:
                pair_opt_steps += 1
            if pair_cost[1] == opt_cost[1]:
                pair_opt_checks += 1
        rows.append(
            {
                "density": density,
                "trials": trials,
                "pair_matches_route": pair_route_equal,
                "pair_matches_opt_steps": pair_opt_steps,
                "pair_matches_opt_checks": pair_opt_checks,
            }
        )
    return rows


def build_report() -> dict[str, object]:
    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": False,
        "discovery_domain": "obligation-targeted witness routing on exhaustive 4x4 boolean relations",
        "holdout_domain": "random 5x5 boolean relations",
        "strongest_claim": (
            "The closure-guided coupled policy factors exactly into an obligation-only controller plus a witness router. "
            "On exhaustive 4x4 domains, that routed controller preserves the full coupled-policy behavior, and the induced policy remains exact-optimal for total steps, though not for total checks, against the unrestricted obligation-only optimum."
        ),
        "survivor": "obligation-targeted witness routing",
        "exhaustive_4x4": exhaustive_report(),
        "holdout_5x5": random_holdout_report(),
    }


def main() -> int:
    report = build_report()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
