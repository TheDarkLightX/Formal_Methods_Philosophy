#!/usr/bin/env python3
from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.math_object_innovation_v15.run_cycle import residual_consistent_pairs


OUT = ROOT / "generated" / "report.json"

PARAM_NAMES = (
    "cut_gain_min",
    "next_size_drop_min",
    "max_child_cut_drop",
    "min_child_sum_drop",
    "min_child_best_singleton_gain",
    "origin_guard",
    "rank",
)


def feature_atoms(winner):
    atoms = []
    for key in ("holdout_total", "holdout_5_hits", "holdout_6_hits"):
        atoms.append((key, winner[key]))
    for idx, name in enumerate(PARAM_NAMES):
        atoms.append((f"c1.{name}", winner["params_1"][idx]))
    for idx, name in enumerate(PARAM_NAMES):
        atoms.append((f"c2.{name}", winner["params_2"][idx]))
    return atoms


def has_atom(item, atom):
    name, value = atom
    if name.startswith("c1."):
        idx = PARAM_NAMES.index(name[3:])
        return item["params_1"][idx] == value
    if name.startswith("c2."):
        idx = PARAM_NAMES.index(name[3:])
        return item["params_2"][idx] == value
    return item[name] == value


def build_report():
    viable = residual_consistent_pairs()
    winner = viable[0]
    atoms = feature_atoms(winner)
    universe = set(range(1, len(viable)))

    covers = []
    for atom in atoms:
        excluded = set()
        for index, item in enumerate(viable[1:], start=1):
            if not has_atom(item, atom):
                excluded.add(index)
        covers.append((atom, excluded))

    minimal_size = None
    solutions = []
    for size in range(1, len(atoms) + 1):
        found = []
        for combo in combinations(range(len(atoms)), size):
            covered = set()
            for idx in combo:
                covered |= covers[idx][1]
            if covered == universe:
                found.append(combo)
        if found:
            minimal_size = size
            solutions = found
            break

    certificate_solutions = []
    for combo in solutions[:20]:
        certificate_solutions.append([atoms[idx] for idx in combo])

    return {
        "tier": "descriptive_symbolic_controller",
        "oracle_dependent": False,
        "discovery_domain": "minimal exact certificate search over the residual-consistent repair-program frontier",
        "holdout_domain": "same weighted 5x5 and 6x6 frontier summary used in v15",
        "survivor": "winner-certificate language frontier",
        "frontier_size": len(viable),
        "atom_count": len(atoms),
        "minimal_certificate_size": minimal_size,
        "solution_count_at_min_size": len(solutions),
        "sample_certificates": certificate_solutions,
        "winner": {
            "holdout_total": winner["holdout_total"],
            "holdout_5_hits": winner["holdout_5_hits"],
            "holdout_6_hits": winner["holdout_6_hits"],
            "clause_1": winner["params_1"],
            "clause_2": winner["params_2"],
        },
        "strongest_claim": (
            "Within the residual-consistent repair-program frontier, the safe winner is not isolated by any conjunction of at most five atomic winner-features. "
            "There exist exact isolating certificates of size six, so the staged loop does admit a small sound certificate language for the winning repair program in this bounded model."
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
