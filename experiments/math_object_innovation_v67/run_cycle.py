#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "generated"
OUT_PATH = OUT_DIR / "report.json"
LABELS = ("A", "B", "C", "D")


def sig_from_int(x: int, width: int = 3) -> tuple[int, ...]:
    return tuple((x >> idx) & 1 for idx in reversed(range(width)))


def to_int(sig: tuple[int, ...]) -> int:
    out = 0
    for bit in sig:
        out = (out << 1) | bit
    return out


def cube_automorphisms(width: int = 3):
    for perm in itertools.permutations(range(width)):
        for flips in itertools.product([0, 1], repeat=width):
            def transform(sig, perm=perm, flips=flips):
                return tuple(sig[perm[i]] ^ flips[i] for i in range(width))

            yield transform


def atom_pool(width: int = 3, max_literals: int = 2):
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


def minimal_compiler(ordered_subset):
    signatures = {
        label: sig_from_int(value)
        for label, value in zip(LABELS, ordered_subset)
    }
    atoms = atom_pool()
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


def induced_edge_count(subset):
    signatures = [sig_from_int(value) for value in subset]
    edges = 0
    for i in range(4):
        for j in range(i + 1, 4):
            if sum(a != b for a, b in zip(signatures[i], signatures[j])) == 1:
                edges += 1
    return edges


def orbit_partition():
    automorphisms = list(cube_automorphisms())
    vertices = list(range(8))
    seen = set()
    orbits = []
    for subset in itertools.combinations(vertices, 4):
        if subset in seen:
            continue
        orbit = set()
        for transform in automorphisms:
            image = tuple(sorted(to_int(transform(sig_from_int(v))) for v in subset))
            orbit.add(image)
        seen |= orbit
        rep = min(orbit)
        orbits.append((rep, orbit))
    return sorted(orbits)


def summarize_orbits():
    atlas = []
    cost_hist = {}
    for representative, orbit in orbit_partition():
        orbit_costs = {}
        sample = {}
        for subset in orbit:
            for ordered in itertools.permutations(subset):
                cost, witness = minimal_compiler(ordered)
                orbit_costs[cost] = orbit_costs.get(cost, 0) + 1
                sample.setdefault(cost, {"ordered_subset": ordered, "witness": witness})
                cost_hist[cost] = cost_hist.get(cost, 0) + 1
        if len(orbit_costs) != 1:
            raise RuntimeError(f"orbit {representative} not uniform: {orbit_costs}")
        (cost, count), = orbit_costs.items()
        atlas.append(
            {
                "representative": list(representative),
                "orbit_size": len(orbit),
                "edge_count": induced_edge_count(representative),
                "uniform_cost": cost,
                "labeled_table_count": count,
                "sample_witness": sample[cost],
            }
        )
    return atlas, cost_hist


def main():
    atlas, cost_hist = summarize_orbits()
    report = {
        "survivor": "width3 four-role geometry frontier",
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "labeled four-role support tables with one distinct realized support "
            "signature per role at width 3, quotiented by cube automorphisms"
        ),
        "holdout_domain": "the width-3 abstract support-table family from v66",
        "orbit_count": len(atlas),
        "orbit_atlas": atlas,
        "cost_histogram": [
            {"cost": cost, "count": count}
            for cost, count in sorted(cost_hist.items())
        ],
        "strongest_claim": (
            "The width-3 four-role support frontier collapses exactly to six "
            "cube-orbit classes, and each orbit has a uniform exact minimal "
            "compiler cost. The v66 cost ladder is therefore a small exact "
            "geometry atlas, not just a histogram."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
