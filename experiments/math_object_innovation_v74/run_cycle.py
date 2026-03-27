#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "generated"
OUT_PATH = OUT_DIR / "report.json"


def sig_from_int(x: int, width: int = 4) -> tuple[int, ...]:
    return tuple((x >> idx) & 1 for idx in reversed(range(width)))


def to_int(sig: tuple[int, ...]) -> int:
    out = 0
    for bit in sig:
        out = (out << 1) | bit
    return out


def cube_automorphisms(width: int = 4):
    for perm in itertools.permutations(range(width)):
        for flips in itertools.product([0, 1], repeat=width):
            def transform(sig, perm=perm, flips=flips):
                return tuple(sig[perm[i]] ^ flips[i] for i in range(width))

            yield transform


def minimal_profile(subset):
    signatures = [sig_from_int(value) for value in subset]
    masks = [
        mask
        for size in range(1, 5)
        for mask in itertools.combinations(range(4), size)
    ]
    mins = []
    for i, signature in enumerate(signatures):
        others = [other for j, other in enumerate(signatures) if j != i]
        best = None
        for coords in masks:
            pattern = tuple(signature[idx] for idx in coords)
            if all(tuple(other[idx] for idx in coords) != pattern for other in others):
                best = len(coords)
                break
        if best is None:
            raise RuntimeError("no unique-support witness found")
        mins.append(best)
    return tuple(sorted(mins))


def orbit_rows():
    automorphisms = list(cube_automorphisms())
    seen = set()
    rows = []
    for subset in itertools.combinations(range(16), 4):
        if subset in seen:
            continue
        orbit = set()
        for transform in automorphisms:
            image = tuple(sorted(to_int(transform(sig_from_int(v))) for v in subset))
            orbit.add(image)
        seen |= orbit
        representative = min(orbit)
        profile = minimal_profile(representative)
        signatures = [sig_from_int(value) for value in representative]
        deg = [0] * 4
        dists = []
        for i in range(4):
            for j in range(i + 1, 4):
                dist = sum(a != b for a, b in zip(signatures[i], signatures[j]))
                dists.append(dist)
                if dist == 1:
                    deg[i] += 1
                    deg[j] += 1
        rows.append(
            {
                "representative": list(representative),
                "count_private_roles": sum(value == 1 for value in profile),
                "count_size2_roles": sum(value == 2 for value in profile),
                "max_degree": max(deg),
                "isolated_count": sum(d == 0 for d in deg),
                "diameter": max(dists),
            }
        )
    return sorted(rows, key=lambda row: tuple(row["representative"]))


def exact_on(rows, features):
    seen = {}
    for row in rows:
        key = tuple(row[feature] for feature in features)
        value = tuple(row["representative"])
        if key in seen and seen[key] != value:
            return False
        seen[key] = value
    return True


def build_map(rows, features):
    mapping = {}
    for row in rows:
        key = tuple(row[feature] for feature in features)
        mapping[key] = tuple(row["representative"])
    return [
        {
            "features": list(key),
            "representative": list(value),
        }
        for key, value in sorted(mapping.items())
    ]


def main():
    rows = orbit_rows()
    scalar_features = [
        "count_private_roles",
        "count_size2_roles",
        "max_degree",
        "isolated_count",
        "diameter",
    ]
    singleton_exact = [name for name in scalar_features if exact_on(rows, [name])]
    pair_exact = [
        (a, b)
        for i, a in enumerate(scalar_features)
        for b in scalar_features[i + 1 :]
        if exact_on(rows, [a, b])
    ]
    triple_exact = [
        (a, b, c)
        for i, a in enumerate(scalar_features)
        for j, b in enumerate(scalar_features[i + 1 :], start=i + 1)
        for c in scalar_features[j + 1 :]
        if exact_on(rows, [a, b, c])
    ]
    chosen = ("count_private_roles", "max_degree", "diameter")
    report = {
        "survivor": "width4 orbit scalarized mixed-law frontier",
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "minimal exact scalar support-plus-geometry basis for the width-4 "
            "orbit family, within the searched scalar feature library"
        ),
        "holdout_domain": "the full width-4 unlabeled orbit family",
        "orbit_count": len(rows),
        "singleton_exact": singleton_exact,
        "pair_exact": [list(item) for item in pair_exact],
        "triple_exact": [list(item) for item in triple_exact],
        "chosen_triple": list(chosen),
        "chosen_triple_map": build_map(rows, chosen),
        "strongest_claim": (
            "On the width-4 unlabeled orbit family, no searched singleton or "
            "pair of scalar support-plus-geometry features reconstructs the "
            "orbit class exactly, but the triple "
            "(count_private_roles, max_degree, diameter) does."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
