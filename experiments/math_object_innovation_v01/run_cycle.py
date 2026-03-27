#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import random


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "generated" / "report.json"


@dataclass(frozen=True)
class Relation:
    x_size: int
    y_size: int
    table: tuple[tuple[bool, ...], ...]

    def spec(self, x: int, y: int) -> bool:
        return self.table[x][y]

    def phi(self, obligations: frozenset[int]) -> frozenset[int]:
        return frozenset(
            x for x in range(self.x_size)
            if all(self.spec(x, y) for y in obligations)
        )

    def psi(self, candidates: frozenset[int]) -> frozenset[int]:
        return frozenset(
            y for y in range(self.y_size)
            if all(self.spec(x, y) for x in candidates)
        )


def relation_from_mask(x_size: int, y_size: int, mask: int) -> Relation:
    table = []
    bit = 0
    for _ in range(x_size):
        row = []
        for _ in range(y_size):
            row.append(bool((mask >> bit) & 1))
            bit += 1
        table.append(tuple(row))
    return Relation(x_size=x_size, y_size=y_size, table=tuple(table))


def choose_smallest(rel: Relation, candidates: frozenset[int], uncovered: frozenset[int], failing: list[int]) -> int:
    return min(failing)


def pick_min_candidate(rel: Relation, candidates: frozenset[int]) -> int:
    return min(candidates)


def pick_best_singleton_candidate(rel: Relation, candidates: frozenset[int]) -> int:
    best = None
    best_key = None
    for x in candidates:
        key = (-len(rel.psi(frozenset({x}))), x)
        if best_key is None or key < best_key:
            best_key = key
            best = x
    return best


def choose_cut(rel: Relation, candidates: frozenset[int], uncovered: frozenset[int], failing: list[int]) -> int:
    best = None
    best_key = None
    for y in failing:
        next_candidates = frozenset(x for x in candidates if rel.spec(x, y))
        key = (len(next_candidates), y)
        if best_key is None or key < best_key:
            best_key = key
            best = y
    return best


def choose_closure(rel: Relation, candidates: frozenset[int], uncovered: frozenset[int], failing: list[int]) -> int:
    current_closed = len(rel.psi(candidates))
    best = None
    best_key = None
    for y in failing:
        next_candidates = frozenset(x for x in candidates if rel.spec(x, y))
        gain = len(rel.psi(next_candidates)) - current_closed
        key = (-gain, len(next_candidates), y)
        if best_key is None or key < best_key:
            best_key = key
            best = y
    return best


def choose_live(rel: Relation, candidates: frozenset[int], uncovered: frozenset[int], failing: list[int]) -> int:
    best = None
    best_key = None
    all_obligations = frozenset(range(rel.y_size))
    for y in failing:
        next_candidates = frozenset(x for x in candidates if rel.spec(x, y))
        next_uncovered = all_obligations - rel.psi(next_candidates)
        key = (len(next_candidates) + len(next_uncovered), len(next_uncovered), len(next_candidates), y)
        if best_key is None or key < best_key:
            best_key = key
            best = y
    return best


def run_scheduler(rel: Relation, pick_candidate, chooser) -> tuple[int, int]:
    all_obligations = frozenset(range(rel.y_size))
    candidates = rel.phi(frozenset())
    steps = 0
    checks = 0
    while candidates:
        x = pick_candidate(rel, candidates)
        uncovered = all_obligations - rel.psi(candidates)
        failing = [y for y in uncovered if not rel.spec(x, y)]
        checks += len(uncovered)
        if not failing:
            return steps, checks
        y = chooser(rel, candidates, uncovered, failing)
        candidates = frozenset(z for z in candidates if rel.spec(z, y))
        steps += 1
    return steps, checks


def optimal_policy_cost(rel: Relation, pick_candidate, primary: str = "steps") -> tuple[int, int]:
    all_obligations = frozenset(range(rel.y_size))

    if primary == "steps":
        def better(pair: tuple[int, int], incumbent: tuple[int, int]) -> bool:
            return pair < incumbent
    elif primary == "checks":
        def better(pair: tuple[int, int], incumbent: tuple[int, int]) -> bool:
            return (pair[1], pair[0]) < (incumbent[1], incumbent[0])
    else:
        raise ValueError(f"unknown optimization priority: {primary}")

    @lru_cache(None)
    def best(candidates_tuple: tuple[int, ...]) -> tuple[int, int]:
        candidates = frozenset(candidates_tuple)
        if not candidates:
            return (0, 0)
        x = pick_candidate(rel, candidates)
        uncovered = all_obligations - rel.psi(candidates)
        failing = [y for y in uncovered if not rel.spec(x, y)]
        base_checks = len(uncovered)
        if not failing:
            return (0, base_checks)
        best_pair = None
        for y in failing:
            next_candidates = frozenset(z for z in candidates if rel.spec(z, y))
            tail_steps, tail_checks = best(tuple(sorted(next_candidates)))
            pair = (1 + tail_steps, base_checks + tail_checks)
            if best_pair is None or better(pair, best_pair):
                best_pair = pair
        return best_pair

    return best(tuple(sorted(rel.phi(frozenset()))))


def exhaustive_domain_report(x_size: int, y_size: int) -> dict[str, object]:
    count = 1 << (x_size * y_size)
    schedulers = {
        "smallest": choose_smallest,
        "cut": choose_cut,
        "closure": choose_closure,
        "live": choose_live,
    }
    totals = {
        name: {"steps_total": 0, "checks_total": 0, "optimal_steps_hits": 0, "optimal_checks_hits": 0}
        for name in schedulers
    }
    first_step_failure = None
    first_check_failure = None

    for mask in range(count):
        rel = relation_from_mask(x_size, y_size, mask)
        optimal_steps, _ = optimal_policy_cost(rel, pick_min_candidate, primary="steps")
        _, optimal_checks = optimal_policy_cost(rel, pick_min_candidate, primary="checks")
        for name, chooser in schedulers.items():
            steps, checks = run_scheduler(rel, pick_min_candidate, chooser)
            totals[name]["steps_total"] += steps
            totals[name]["checks_total"] += checks
            if steps == optimal_steps:
                totals[name]["optimal_steps_hits"] += 1
            elif name == "closure" and first_step_failure is None:
                first_step_failure = {
                    "mask": mask,
                    "closure": {"steps": steps, "checks": checks},
                    "optimal": {"steps": optimal_steps, "checks": optimal_checks},
                    "table": [[int(v) for v in row] for row in rel.table],
                }
            if checks == optimal_checks:
                totals[name]["optimal_checks_hits"] += 1
            elif name == "closure" and first_check_failure is None:
                first_check_failure = {
                    "mask": mask,
                    "closure": {"steps": steps, "checks": checks},
                    "optimal": {"steps": optimal_steps, "checks": optimal_checks},
                    "table": [[int(v) for v in row] for row in rel.table],
                }

    first_failure = first_step_failure or first_check_failure
    summary = {
        "x_size": x_size,
        "y_size": y_size,
        "relation_count": count,
        "fixed_proposer": "pick_min_candidate",
        "optimality_scope": (
            "Verifier policies are compared under the fixed proposer x_t = min(C_t). "
            "Step and check optimality are computed independently, with the non-primary metric used only as a tiebreak."
        ),
        "schedulers": {},
        "closure_first_failure": first_failure,
        "closure_first_step_failure": first_step_failure,
        "closure_first_check_failure": first_check_failure,
    }
    for name, stats in totals.items():
        summary["schedulers"][name] = {
            "avg_steps": stats["steps_total"] / count,
            "avg_checks": stats["checks_total"] / count,
            "optimal_steps_hits": stats["optimal_steps_hits"],
            "optimal_checks_hits": stats["optimal_checks_hits"],
        }
    return summary


def exhaustive_coupled_policy_report(x_size: int, y_size: int) -> dict[str, object]:
    count = 1 << (x_size * y_size)
    exact_hits_steps = 0
    exact_hits_checks = 0
    first_step_failure = None
    first_check_failure = None
    steps_total = 0
    checks_total = 0
    for mask in range(count):
        rel = relation_from_mask(x_size, y_size, mask)
        got_steps, got_checks = run_scheduler(rel, pick_best_singleton_candidate, choose_closure)
        opt_steps, _ = optimal_policy_cost(rel, pick_best_singleton_candidate, primary="steps")
        _, opt_checks = optimal_policy_cost(rel, pick_best_singleton_candidate, primary="checks")
        steps_total += got_steps
        checks_total += got_checks
        if got_steps == opt_steps:
            exact_hits_steps += 1
        elif first_step_failure is None:
            first_step_failure = {
                "mask": mask,
                "mode": "steps",
                "got": {"steps": got_steps, "checks": got_checks},
                "optimal": {"steps": opt_steps, "checks": opt_checks},
                "table": [[int(v) for v in row] for row in rel.table],
            }
        if got_checks == opt_checks:
            exact_hits_checks += 1
        elif first_check_failure is None:
            first_check_failure = {
                "mask": mask,
                "mode": "checks",
                "got": {"steps": got_steps, "checks": got_checks},
                "optimal": {"steps": opt_steps, "checks": opt_checks},
                "table": [[int(v) for v in row] for row in rel.table],
            }
    first_failure = first_step_failure or first_check_failure
    return {
        "x_size": x_size,
        "y_size": y_size,
        "relation_count": count,
        "fixed_proposer": "pick_best_singleton_candidate",
        "optimality_scope": (
            "The coupled policy is compared against the bounded optimum under the fixed singleton-closure proposer. "
            "Step and check optimality are computed independently, with the non-primary metric used only as a tiebreak."
        ),
        "avg_steps": steps_total / count,
        "avg_checks": checks_total / count,
        "optimal_steps_hits": exact_hits_steps,
        "optimal_checks_hits": exact_hits_checks,
        "first_failure": first_failure,
        "first_step_failure": first_step_failure,
        "first_check_failure": first_check_failure,
    }


def random_holdout_report(x_size: int, y_size: int, trials: int, seed: int) -> list[dict[str, object]]:
    rng = random.Random(seed)
    schedulers = {
        "smallest": choose_smallest,
        "cut": choose_cut,
        "closure": choose_closure,
        "live": choose_live,
    }
    densities = [0.3, 0.5, 0.7]
    rows = []
    for density in densities:
        totals = {name: {"steps_total": 0, "checks_total": 0} for name in schedulers}
        coupled_total = {"steps_total": 0, "checks_total": 0}
        for _ in range(trials):
            table = tuple(
                tuple(rng.random() < density for _ in range(y_size))
                for _ in range(x_size)
            )
            rel = Relation(x_size=x_size, y_size=y_size, table=table)
            for name, chooser in schedulers.items():
                steps, checks = run_scheduler(rel, pick_min_candidate, chooser)
                totals[name]["steps_total"] += steps
                totals[name]["checks_total"] += checks
            steps, checks = run_scheduler(rel, pick_best_singleton_candidate, choose_closure)
            coupled_total["steps_total"] += steps
            coupled_total["checks_total"] += checks
        row = {"x_size": x_size, "y_size": y_size, "trials": trials, "density": density, "schedulers": {}}
        for name, stats in totals.items():
            row["schedulers"][name] = {
                "avg_steps": stats["steps_total"] / trials,
                "avg_checks": stats["checks_total"] / trials,
            }
        row["coupled_closure"] = {
            "avg_steps": coupled_total["steps_total"] / trials,
            "avg_checks": coupled_total["checks_total"] / trials,
        }
        rows.append(row)
    return rows


def build_report() -> dict[str, object]:
    exhaustive = [
        exhaustive_domain_report(3, 3),
        exhaustive_domain_report(3, 4),
        exhaustive_domain_report(4, 4),
    ]
    coupled = exhaustive_coupled_policy_report(4, 4)
    holdout = [
        {"domain": "5x5", "rows": random_holdout_report(5, 5, trials=1000, seed=17)},
        {"domain": "6x6", "rows": random_holdout_report(6, 6, trials=500, seed=23)},
    ]
    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": False,
        "discovery_domain": "finite boolean relations Spec : X x Y -> {0,1} with exhaustive scheduler comparison on 3x3, 3x4, and 4x4 domains",
        "holdout_domain": "random boolean relations on 5x5 and 6x6 domains",
        "scope_notes": [
            "The exhaustive verifier-policy tables hold the proposer fixed to x_t = min(C_t).",
            "The coupled 4x4 table holds the proposer fixed to the singleton-closure chooser.",
            "Step and check optimality are computed independently, with the other metric used only as a tiebreak.",
        ],
        "strongest_claim": (
            "In the bounded domains checked here, closure geometry matters twice: "
            "with a fixed min-candidate proposer, closure-gain and live-burden scheduling tie as the strongest tested local verifier policies, "
            "and with the singleton-closure proposer held fixed, the coupled closure policy matches the bounded step-optimal and check-optimal results on every 4x4 relation checked exhaustively."
        ),
        "survivor": "closure-guided coupled policy",
        "failed_branch": "state representation alone as the primary source of leverage",
        "exhaustive": exhaustive,
        "coupled_exhaustive": coupled,
        "holdout": holdout,
    }


def main() -> int:
    report = build_report()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
