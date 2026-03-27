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
    profile = tuple(sorted(mins))
    return profile


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
        dists = []
        for i in range(4):
            for j in range(i + 1, 4):
                dists.append(sum(a != b for a, b in zip(signatures[i], signatures[j])))
        rows.append(
            {
                "representative": list(representative),
                "profile": list(profile),
                "count_private_roles": sum(value == 1 for value in profile),
                "count_size2_roles": sum(value == 2 for value in profile),
                "distance_multiset": sorted(dists),
            }
        )
    return sorted(rows, key=lambda row: tuple(row["representative"]))


def exact_on(rows, features):
    seen = {}
    for row in rows:
        key = tuple(
            tuple(row[feature]) if isinstance(row[feature], list) else row[feature]
            for feature in features
        )
        value = tuple(row["representative"])
        if key in seen and seen[key] != value:
            return False
        seen[key] = value
    return True


def build_map(rows, features):
    mapping = {}
    for row in rows:
        key = tuple(
            tuple(row[feature]) if isinstance(row[feature], list) else row[feature]
            for feature in features
        )
        mapping[key] = tuple(row["representative"])
    out = []
    for key, value in sorted(mapping.items()):
        item = {"features": [list(v) if isinstance(v, tuple) else v for v in key]}
        item["representative"] = list(value)
        out.append(item)
    return out


def main():
    rows = orbit_rows()
    feature_names = [
        "count_private_roles",
        "count_size2_roles",
        "distance_multiset",
    ]
    singleton_exact = [name for name in feature_names if exact_on(rows, [name])]
    pair_exact = [
        (a, b)
        for i, a in enumerate(feature_names)
        for b in feature_names[i + 1 :]
        if exact_on(rows, [a, b])
    ]
    chosen = ("count_private_roles", "distance_multiset")
    report = {
        "survivor": "width4 orbit mixed-basis frontier",
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "minimal exact mixed support-plus-geometry basis for the width-4 "
            "orbit family, within the searched support-count and distance library"
        ),
        "holdout_domain": "the full width-4 unlabeled orbit family",
        "orbit_count": len(rows),
        "singleton_exact": singleton_exact,
        "pair_exact": [list(item) for item in pair_exact],
        "chosen_pair": list(chosen),
        "chosen_pair_map": build_map(rows, chosen),
        "strongest_claim": (
            "On the width-4 unlabeled orbit family, support counts alone do not "
            "determine the orbit class, but the pair "
            "(count_private_roles, distance_multiset) does so exactly."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
