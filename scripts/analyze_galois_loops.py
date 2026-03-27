#!/usr/bin/env python3
from __future__ import annotations

import argparse
import itertools
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path


def powerset(n: int):
    for mask in range(1 << n):
        yield frozenset(i for i in range(n) if (mask >> i) & 1)


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

    def good_set(self) -> frozenset[int]:
        return self.phi(frozenset(range(self.y_size)))


def relation_from_mask(x_size: int, y_size: int, mask: int) -> Relation:
    table = []
    bit = 0
    for _x in range(x_size):
        row = []
        for _y in range(y_size):
            row.append(bool((mask >> bit) & 1))
            bit += 1
        table.append(tuple(row))
    return Relation(x_size=x_size, y_size=y_size, table=tuple(table))


def choose_smallest(candidates: frozenset[int]) -> int | None:
    return min(candidates) if candidates else None


def plain_cegis_trace(rel: Relation) -> list[tuple[frozenset[int], frozenset[int]]]:
    discovered = frozenset()
    candidates = rel.phi(discovered)
    trace = [(candidates, discovered)]
    while candidates:
        x = choose_smallest(candidates)
        bad = next((y for y in range(rel.y_size) if not rel.spec(x, y)), None)
        if bad is None:
            break
        discovered = frozenset(set(discovered) | {bad})
        candidates = rel.phi(discovered)
        trace.append((candidates, discovered))
    return trace


def lattice_trace(rel: Relation) -> list[tuple[frozenset[int], frozenset[int]]]:
    intent = rel.psi(rel.phi(frozenset()))
    candidates = rel.phi(intent)
    trace = [(candidates, intent)]
    while candidates:
        x = choose_smallest(candidates)
        bad = next((y for y in range(rel.y_size) if not rel.spec(x, y)), None)
        if bad is None:
            break
        intent = rel.psi(rel.phi(frozenset(set(intent) | {bad})))
        candidates = rel.phi(intent)
        trace.append((candidates, intent))
    return trace


def boc_max_trace(rel: Relation) -> list[tuple[frozenset[int], frozenset[int], frozenset[int]]]:
    candidates = rel.phi(frozenset())
    discharged = rel.psi(candidates)
    uncovered = frozenset(range(rel.y_size)) - discharged
    trace = [(candidates, discharged, uncovered)]
    while candidates:
        x = choose_smallest(candidates)
        bad = next((y for y in range(rel.y_size) if y in uncovered and not rel.spec(x, y)), None)
        if bad is None:
            break
        candidates = frozenset(z for z in candidates if rel.spec(z, bad))
        discharged = rel.psi(candidates)
        uncovered = frozenset(range(rel.y_size)) - discharged
        trace.append((candidates, discharged, uncovered))
    return trace


def verify_galois_laws(rel: Relation) -> None:
    xs = list(powerset(rel.x_size))
    ys = list(powerset(rel.y_size))
    all_x = frozenset(range(rel.x_size))
    all_y = frozenset(range(rel.y_size))

    for c in xs:
        for b in ys:
            left = c.issubset(rel.phi(b))
            right = b.issubset(rel.psi(c))
            if left != right:
                raise AssertionError(("galois", rel, c, b, left, right))

    for b in ys:
        if not b.issubset(rel.psi(rel.phi(b))):
            raise AssertionError(("closure_extensive_y", rel, b))
        if rel.psi(rel.phi(rel.psi(rel.phi(b)))) != rel.psi(rel.phi(b)):
            raise AssertionError(("closure_idempotent_y", rel, b))
        if rel.phi(rel.psi(rel.phi(b))) != rel.phi(b):
            raise AssertionError(("basis_compression_y", rel, b))

    for c in xs:
        if not c.issubset(rel.phi(rel.psi(c))):
            raise AssertionError(("closure_extensive_x", rel, c))
        if rel.phi(rel.psi(rel.phi(rel.psi(c)))) != rel.phi(rel.psi(c)):
            raise AssertionError(("closure_idempotent_x", rel, c))
        if rel.psi(rel.phi(rel.psi(c))) != rel.psi(c):
            raise AssertionError(("basis_compression_x", rel, c))

    for b1 in ys:
        for b2 in ys:
            if b1.issubset(b2):
                if not rel.phi(b2).issubset(rel.phi(b1)):
                    raise AssertionError(("anti_tone_phi", rel, b1, b2))

    for c1 in xs:
        for c2 in xs:
            if c1.issubset(c2):
                if not rel.psi(c2).issubset(rel.psi(c1)):
                    raise AssertionError(("anti_tone_psi", rel, c1, c2))

    if not rel.good_set().issubset(rel.phi(frozenset())):
        raise AssertionError(("good_subset_initial", rel))
    if not rel.psi(rel.good_set()) == all_y:
        raise AssertionError(("good_set_discharges_all", rel))
    if not rel.phi(all_y) == rel.good_set():
        raise AssertionError(("good_def", rel))
    if not rel.psi(all_x).issubset(all_y):
        raise AssertionError(("psi_bounds", rel))


def verify_loop_relations(rel: Relation) -> dict[str, int]:
    plain = plain_cegis_trace(rel)
    lattice = lattice_trace(rel)
    boc = boc_max_trace(rel)

    plain_candidates = [c for (c, _b) in plain]
    lattice_candidates = [c for (c, _b) in lattice]
    boc_candidates = [c for (c, _d, _u) in boc]

    if plain_candidates != lattice_candidates:
        raise AssertionError(("plain_vs_lattice_candidates", rel, plain, lattice))
    if lattice_candidates != boc_candidates:
        raise AssertionError(("lattice_vs_boc_candidates", rel, lattice, boc))

    for (cand_l, intent), (cand_b, discharged, uncovered) in zip(lattice, boc):
        if cand_l != cand_b:
            raise AssertionError(("candidate_state_mismatch", rel, cand_l, cand_b))
        if intent != discharged:
            raise AssertionError(("intent_discharged_mismatch", rel, intent, discharged))
        if uncovered != frozenset(range(rel.y_size)) - discharged:
            raise AssertionError(("uncovered_complement_mismatch", rel, discharged, uncovered))
        if not discharged.issubset(rel.psi(cand_b)):
            raise AssertionError(("boc_invariant", rel, cand_b, discharged))
        if not rel.good_set().issubset(cand_b):
            raise AssertionError(("good_preservation", rel, cand_b))

    return {
        "plain_steps": len(plain) - 1,
        "lattice_steps": len(lattice) - 1,
        "boc_steps": len(boc) - 1,
        "plain_online_checks": sum(len(range(rel.y_size)) for _ in plain[:-1]),
        "boc_online_checks": sum(len(state[2]) for state in boc[:-1]),
    }


def exhaustive_report(x_size: int, y_size: int) -> dict[str, int]:
    relation_count = 1 << (x_size * y_size)
    totals = {
        "relation_count": relation_count,
        "plain_steps_total": 0,
        "lattice_steps_total": 0,
        "boc_steps_total": 0,
        "plain_online_checks_total": 0,
        "boc_online_checks_total": 0,
    }

    for mask in range(relation_count):
        rel = relation_from_mask(x_size, y_size, mask)
        verify_galois_laws(rel)
        stats = verify_loop_relations(rel)
        for key, value in stats.items():
            totals[f"{key}_total"] = totals.get(f"{key}_total", 0) + value

    totals["plain_steps_avg"] = totals["plain_steps_total"] / relation_count
    totals["lattice_steps_avg"] = totals["lattice_steps_total"] / relation_count
    totals["boc_steps_avg"] = totals["boc_steps_total"] / relation_count
    totals["plain_online_checks_avg"] = totals["plain_online_checks_total"] / relation_count
    totals["boc_online_checks_avg"] = totals["boc_online_checks_total"] / relation_count
    return totals


def random_report(x_size: int, y_size: int, trials: int, seed: int) -> list[dict[str, float]]:
    rng = random.Random(seed)
    densities = [0.3, 0.5, 0.7]
    rows = []
    for density in densities:
        totals = {
            "density": density,
            "trials": trials,
            "plain_steps_total": 0,
            "lattice_steps_total": 0,
            "boc_steps_total": 0,
            "plain_online_checks_total": 0,
            "boc_online_checks_total": 0,
        }
        for _ in range(trials):
            table = tuple(
                tuple(rng.random() < density for _ in range(y_size))
                for _ in range(x_size)
            )
            rel = Relation(x_size=x_size, y_size=y_size, table=table)
            stats = verify_loop_relations(rel)
            for key, value in stats.items():
                totals[f"{key}_total"] += value
        totals["plain_steps_avg"] = totals["plain_steps_total"] / trials
        totals["lattice_steps_avg"] = totals["lattice_steps_total"] / trials
        totals["boc_steps_avg"] = totals["boc_steps_total"] / trials
        totals["plain_online_checks_avg"] = totals["plain_online_checks_total"] / trials
        totals["boc_online_checks_avg"] = totals["boc_online_checks_total"] / trials
        rows.append(totals)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze Galoisized CEGIS loop laws on finite relations.")
    parser.add_argument("--exhaustive-x", type=int, default=3)
    parser.add_argument("--exhaustive-y", type=int, default=3)
    parser.add_argument("--random-x", type=int, default=6)
    parser.add_argument("--random-y", type=int, default=8)
    parser.add_argument("--random-trials", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--write-json",
        type=Path,
        help="Optional path to write the JSON report to disk.",
    )
    parser.add_argument(
        "--allow-large-exhaustive",
        action="store_true",
        help="Allow exhaustive runs above 12 relation cells. Disabled by default to avoid accidental blowups.",
    )
    args = parser.parse_args()

    exhaustive_cells = args.exhaustive_x * args.exhaustive_y
    if exhaustive_cells > 12 and not args.allow_large_exhaustive:
        parser.error(
            "refusing exhaustive run with more than 12 cells; "
            "pass --allow-large-exhaustive if that cost is intentional"
        )

    exhaustive = exhaustive_report(args.exhaustive_x, args.exhaustive_y)
    random_rows = random_report(args.random_x, args.random_y, args.random_trials, args.seed)

    report = {
        "exhaustive": exhaustive,
        "random": random_rows,
    }

    report_text = json.dumps(report, indent=2, sort_keys=True)

    if args.write_json is not None:
        args.write_json.parent.mkdir(parents=True, exist_ok=True)
        args.write_json.write_text(report_text + "\n", encoding="utf-8")

    if args.json:
        print(report_text)
        return 0

    print("Exhaustive finite check")
    print(
        f"  universe: X={args.exhaustive_x}, Y={args.exhaustive_y}, "
        f"relations={exhaustive['relation_count']}"
    )
    print(
        f"  avg steps: plain={exhaustive['plain_steps_avg']:.3f}, "
        f"lattice={exhaustive['lattice_steps_avg']:.3f}, "
        f"boc={exhaustive['boc_steps_avg']:.3f}"
    )
    print(
        f"  avg online obligation checks: plain={exhaustive['plain_online_checks_avg']:.3f}, "
        f"boc={exhaustive['boc_online_checks_avg']:.3f}"
    )
    print()
    print("Random stress test")
    print(
        f"  universe: X={args.random_x}, Y={args.random_y}, "
        f"trials-per-density={args.random_trials}, seed={args.seed}"
    )
    for row in random_rows:
        print(
            f"  density={row['density']:.1f} | "
            f"steps plain={row['plain_steps_avg']:.3f}, "
            f"lattice={row['lattice_steps_avg']:.3f}, "
            f"boc={row['boc_steps_avg']:.3f} | "
            f"checks plain={row['plain_online_checks_avg']:.3f}, "
            f"boc={row['boc_online_checks_avg']:.3f}"
        )
    print()
    print("Verified:")
    print("  - Galois equivalence")
    print("  - closure extensivity and idempotence")
    print("  - anti-tone laws for Φ and Ψ")
    print("  - candidate-trace equality: plain CEGIS = lattice CEGIS = BOC-max")
    print("  - state equality: lattice intent = BOC-max discharged obligations")
    print("  - good-set preservation at every loop step")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
