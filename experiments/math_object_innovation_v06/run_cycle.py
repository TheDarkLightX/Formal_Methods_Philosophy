#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.math_object_innovation_v03.run_cycle import improve_selector, make_value_function, phi, psi, relation_from_mask, route_selector, spec
from experiments.math_object_innovation_v05.run_cycle import BASE_FORMULA
from experiments.math_object_innovation_v04.run_cycle import choose_by_formula


OUT = ROOT / "generated" / "report.json"


def row_features(rel: tuple[tuple[bool, ...], ...], candidates: frozenset[int], y: int) -> dict[str, int]:
    current_closed = psi(rel, candidates)
    next_candidates = frozenset(z for z in candidates if spec(rel, z, y))
    next_closed = psi(rel, next_candidates)
    current_uncovered = frozenset(range(len(rel[0]))) - current_closed
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


def row_signature(row: dict[str, int]) -> tuple[int, int, int, int]:
    return (
        row["gain"],
        row["child_best_gain"],
        row["child_best_cut"],
        row["next_uncovered"],
    )


def reachable_candidate_states(rel: tuple[tuple[bool, ...], ...]) -> list[frozenset[int]]:
    n = len(rel[0])
    states = set()
    obligations = list(range(n))
    for mask in range(1 << n):
        basis = frozenset(obligations[i] for i in range(n) if (mask >> i) & 1)
        states.add(phi(rel, basis))
    return sorted(states, key=lambda s: (len(s), tuple(sorted(s))))


def pi2_selector(rel: tuple[tuple[bool, ...], ...]):
    pi0 = route_selector(rel)
    pi1 = improve_selector(rel, pi0)
    return improve_selector(rel, pi1)


def collect_state_dataset() -> list[dict[str, object]]:
    rows = []
    for mask in range(1 << 16):
        rel = relation_from_mask(mask, 4)
        pi2 = pi2_selector(rel)
        value = make_value_function(rel, pi2)
        for candidates in reachable_candidate_states(rel):
            if not candidates:
                continue
            uncovered = frozenset(range(4)) - psi(rel, candidates)
            if not uncovered:
                continue
            state_rows = [(y, row_features(rel, candidates, y)) for y in uncovered]
            target = pi2(candidates, uncovered, value)
            rows.append({
                "mask": mask,
                "candidates": tuple(sorted(candidates)),
                "rows": state_rows,
                "target": target,
            })
    return rows


def motif_from_rows(rows: list[tuple[int, dict[str, int]]]) -> tuple[tuple[int, int, int, int], ...]:
    return tuple(sorted(row_signature(features) for _y, features in rows))


def target_signature(item: dict[str, object]) -> tuple[int, int, int, int]:
    for y, features in item["rows"]:
        if y == item["target"]:
            return row_signature(features)
    raise AssertionError("target signature missing")


def base_choice(item: dict[str, object]) -> int:
    return choose_by_formula(item["rows"], BASE_FORMULA)


def base_plus_motif_choice(item: dict[str, object], motif_map: dict[tuple[tuple[int, int, int, int], ...], tuple[int, int, int, int]]) -> int:
    motif = motif_from_rows(item["rows"])
    target_sig = motif_map.get(motif)
    if target_sig is not None:
        return min(y for y, features in item["rows"] if row_signature(features) == target_sig)
    return base_choice(item)


def build_report() -> dict[str, object]:
    dataset = collect_state_dataset()
    nonterminal_states = len(dataset)

    base_hits = 0
    base_fail_motifs: Counter[tuple[tuple[int, int, int, int], ...]] = Counter()
    motif_to_target_sig: defaultdict[tuple[tuple[int, int, int, int], ...], Counter[tuple[int, int, int, int]]] = defaultdict(Counter)
    first_base_failure = None

    for item in dataset:
        chosen = base_choice(item)
        if chosen == item["target"]:
            base_hits += 1
            continue
        motif = motif_from_rows(item["rows"])
        target_sig = target_signature(item)
        base_fail_motifs[motif] += 1
        motif_to_target_sig[motif][target_sig] += 1
        if first_base_failure is None:
            first_base_failure = {
                "mask": item["mask"],
                "candidates": list(item["candidates"]),
                "chosen": chosen,
                "target": item["target"],
                "rows": item["rows"],
            }

    deterministic_motifs = {}
    for motif, counter in motif_to_target_sig.items():
        if len(counter) == 1:
            deterministic_motifs[motif] = next(iter(counter))

    motif_controller_hits = 0
    motif_controller_first_failure = None
    for item in dataset:
        chosen = base_plus_motif_choice(item, deterministic_motifs)
        if chosen == item["target"]:
            motif_controller_hits += 1
        elif motif_controller_first_failure is None:
            motif_controller_first_failure = {
                "mask": item["mask"],
                "candidates": list(item["candidates"]),
                "chosen": chosen,
                "target": item["target"],
                "rows": item["rows"],
            }

    top_failure_motifs = []
    for motif, count in base_fail_motifs.most_common(10):
        top_failure_motifs.append({
            "count": count,
            "motif": [list(sig) for sig in motif],
            "target_signatures": [[*sig, c] for sig, c in motif_to_target_sig[motif].most_common()],
        })

    return {
        "tier": "descriptive_symbolic_controller",
        "oracle_dependent": False,
        "discovery_domain": "statewise controller distillation on reachable nonterminal states of exhaustive 4x4 boolean relations",
        "survivor": "statewise motif dictionary frontier",
        "nonterminal_state_count": nonterminal_states,
        "base_controller": {
            "formula": list(BASE_FORMULA),
            "hits": base_hits,
            "total": nonterminal_states,
            "first_failure": first_base_failure,
        },
        "failure_motif_count": len(base_fail_motifs),
        "deterministic_failure_motif_count": len(deterministic_motifs),
        "top_failure_motifs": top_failure_motifs,
        "motif_dictionary_controller": {
            "hits": motif_controller_hits,
            "total": nonterminal_states,
            "first_failure": motif_controller_first_failure,
        },
        "strongest_claim": (
            "Across all reachable nonterminal 4x4 candidate states, the flat base controller is not exact. "
            "The next bounded question is whether a finite dictionary of repeated failure motifs is enough to close the full statewise gap."
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
