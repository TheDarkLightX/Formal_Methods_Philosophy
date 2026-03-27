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


def minimal_unique_support_sizes(subset):
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
    return profile, sum(profile[:3])


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
        profile, cost = minimal_unique_support_sizes(representative)
        rows.append(
            {
                "representative": list(representative),
                "orbit_size": len(orbit),
                "profile": list(profile),
                "cost": cost,
                "count_private_roles": sum(value == 1 for value in profile),
                "count_size2_roles": sum(value == 2 for value in profile),
                "count_size3_roles": sum(value == 3 for value in profile),
                "max_support_size": max(profile),
            }
        )
    return sorted(rows, key=lambda row: tuple(row["representative"]))


def exact_on(rows, features, target):
    seen = {}
    for row in rows:
        key = tuple(row[feature] for feature in features)
        value = tuple(row[target]) if isinstance(row[target], list) else row[target]
        if key in seen and seen[key] != value:
            return False
        seen[key] = value
    return True


def build_map(rows, features, target):
    mapping = {}
    for row in rows:
        key = tuple(row[feature] for feature in features)
        value = tuple(row[target]) if isinstance(row[target], list) else row[target]
        mapping[key] = value
    out = []
    for key, value in sorted(mapping.items()):
        item = {"features": list(key)}
        item[target] = list(value) if isinstance(value, tuple) else value
        out.append(item)
    return out


def main():
    rows = orbit_rows()
    feature_names = [
        "count_private_roles",
        "count_size2_roles",
        "count_size3_roles",
        "max_support_size",
    ]
    cost_singleton_exact = [
        name for name in feature_names if exact_on(rows, [name], "cost")
    ]
    profile_singleton_exact = [
        name for name in feature_names if exact_on(rows, [name], "profile")
    ]
    profile_pair_exact = [
        (a, b)
        for i, a in enumerate(feature_names)
        for b in feature_names[i + 1 :]
        if exact_on(rows, [a, b], "profile")
    ]
    chosen_cost = ("count_private_roles",)
    chosen_profile = ("count_private_roles", "max_support_size")
    report = {
        "survivor": "width4 orbit support-count transfer frontier",
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "cube-orbit quotiented width-4 four-role support tables, with "
            "profile-derived support-count coordinates"
        ),
        "holdout_domain": "the full width-4 unlabeled orbit family",
        "orbit_count": len(rows),
        "cost_singleton_exact": cost_singleton_exact,
        "profile_singleton_exact": profile_singleton_exact,
        "profile_pair_exact": [list(item) for item in profile_pair_exact],
        "chosen_cost_scalar": list(chosen_cost),
        "chosen_cost_map": build_map(rows, chosen_cost, "cost"),
        "chosen_profile_pair": list(chosen_profile),
        "chosen_profile_map": build_map(rows, chosen_profile, "profile"),
        "strongest_claim": (
            "On the width-4 unlabeled orbit family, the same support-count "
            "coordinates from v70 and v71 survive unchanged: exact cost is "
            "determined by count_private_roles alone, and the pair "
            "(count_private_roles, max_support_size) reconstructs the full "
            "support profile exactly."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
