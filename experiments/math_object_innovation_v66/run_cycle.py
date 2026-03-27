#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "generated"
OUT_PATH = OUT_DIR / "report.json"
LABELS = ("A", "B", "C", "D")


def sig_from_int(x: int, width: int) -> tuple[int, ...]:
    return tuple((x >> idx) & 1 for idx in reversed(range(width)))


def atom_pool(width: int, max_literals: int):
    atoms = []
    for size in range(1, max_literals + 1):
        for chosen in itertools.combinations(range(width), size):
            for vals in itertools.product([0, 1], repeat=size):
                atoms.append(tuple(zip(chosen, vals)))
    return atoms


def atom_text(atom) -> str:
    return " and ".join(
        f"s{idx}" if value else f"not s{idx}"
        for idx, value in atom
    )


def satisfies(signature, atom) -> bool:
    return all(signature[idx] == value for idx, value in atom)


def private_literal_star(signatures: dict[str, tuple[int, ...]]):
    width = len(next(iter(signatures.values())))
    for default in LABELS:
        others = [label for label in LABELS if label != default]
        for perm in itertools.permutations(others):
            witnesses = []
            ok = True
            for target in perm:
                private = []
                for idx in range(width):
                    value = signatures[target][idx]
                    if all(
                        signatures[other][idx] != value
                        for other in LABELS
                        if other != target
                    ):
                        private.append((idx, value))
                if not private:
                    ok = False
                    break
                witnesses.append((target, private))
            if ok:
                return {
                    "default_label": default,
                    "branches": [
                        {
                            "label": label,
                            "all_private_literals": literals,
                        }
                        for label, literals in witnesses
                    ],
                }
    return None


def minimal_compiler(signatures: dict[str, tuple[int, ...]], max_literals: int = 2):
    width = len(next(iter(signatures.values())))
    atoms = atom_pool(width, max_literals)
    best_cost = None
    best_witness = None
    for default in LABELS:
        others = [label for label in LABELS if label != default]
        for perm in itertools.permutations(others):
            options = []
            for label in perm:
                exact = []
                for atom in atoms:
                    if satisfies(signatures[label], atom) and all(
                        not satisfies(signatures[other], atom)
                        for other in LABELS
                        if other != label
                    ):
                        exact.append(atom)
                if not exact:
                    options = None
                    break
                options.append(exact)
            if not options:
                continue
            for chosen in itertools.product(*options):
                if len(set(chosen)) < len(chosen):
                    continue
                cost = sum(len(atom) for atom in chosen)
                if best_cost is None or cost < best_cost:
                    best_cost = cost
                    best_witness = {
                        "default_label": default,
                        "branches": [
                            {"label": label, "atom": atom_text(atom), "literal_count": len(atom)}
                            for label, atom in zip(perm, chosen)
                        ],
                    }
    return best_cost, best_witness


def width_summary(width: int):
    values = list(range(1 << width))
    total = 0
    star_count = 0
    cost_hist = {}
    first_examples = {}
    for chosen in itertools.permutations(values, len(LABELS)):
        signatures = {
            label: sig_from_int(value, width)
            for label, value in zip(LABELS, chosen)
        }
        total += 1
        star = private_literal_star(signatures)
        if star is not None:
            star_count += 1
        cost, witness = minimal_compiler(signatures, max_literals=2)
        cost_hist[cost] = cost_hist.get(cost, 0) + 1
        first_examples.setdefault(
            cost,
            {
                "signatures": {label: list(sig) for label, sig in signatures.items()},
                "witness": witness,
            },
        )
    return {
        "width": width,
        "table_count": total,
        "single_literal_star_count": star_count,
        "minimal_total_literal_cost_histogram": [
            {"cost": cost, "count": count}
            for cost, count in sorted(cost_hist.items())
        ],
        "first_examples": {
            str(cost): info
            for cost, info in sorted(first_examples.items())
        },
    }


def main():
    width2 = width_summary(2)
    width3 = width_summary(3)
    report = {
        "survivor": "four-role support cost frontier",
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "labeled four-role support tables with one distinct realized signature "
            "per role, exhaustively for widths 2 and 3"
        ),
        "holdout_domain": "abstract support-table family only",
        "width2": width2,
        "width3": width3,
        "strongest_claim": (
            "The three-role support law fails immediately for four roles. At width "
            "2, all 24 labeled tables require total literal cost 6. At width 3, "
            "the exact minimal total-literal-cost ladder is {3: 192, 4: 576, 5: "
            "576, 6: 336}, with 192 single-literal star cases."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
