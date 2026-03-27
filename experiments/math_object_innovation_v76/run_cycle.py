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
        edges = []
        dists = []
        for i in range(4):
            for j in range(i + 1, 4):
                dist = sum(a != b for a, b in zip(signatures[i], signatures[j]))
                dists.append(dist)
                if dist == 1:
                    edges.append((i, j))
                    deg[i] += 1
                    deg[j] += 1
        adj = {idx: set() for idx in range(4)}
        for i, j in edges:
            adj[i].add(j)
            adj[j].add(i)
        seen_vertices = set()
        components = []
        for idx in range(4):
            if idx in seen_vertices:
                continue
            stack = [idx]
            seen_vertices.add(idx)
            component = []
            while stack:
                node = stack.pop()
                component.append(node)
                for nxt in adj[node]:
                    if nxt not in seen_vertices:
                        seen_vertices.add(nxt)
                        stack.append(nxt)
            components.append(len(component))
        rows.append(
            {
                "representative": list(representative),
                "count_private_roles": sum(value == 1 for value in profile),
                "count_size2_roles": sum(value == 2 for value in profile),
                "count_size3_roles": sum(value == 3 for value in profile),
                "max_support_size": max(profile),
                "profile": list(profile),
                "degree_sequence": sorted(deg, reverse=True),
                "component_sizes": sorted(components, reverse=True),
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


def main():
    rows = orbit_rows()
    mixed_features = [
        "count_private_roles",
        "count_size2_roles",
        "count_size3_roles",
        "max_support_size",
        "profile",
        "degree_sequence",
        "component_sizes",
        "distance_multiset",
    ]
    pair_exact = [
        (a, b)
        for i, a in enumerate(mixed_features)
        for b in mixed_features[i + 1 :]
        if exact_on(rows, [a, b])
    ]
    nontrivial_pair_exact = [
        pair for pair in pair_exact if "profile" not in pair
    ]
    report = {
        "survivor": "width4 mixed-basis uniqueness frontier",
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "exact mixed support-plus-geometry pair bases for the width-4 orbit "
            "family, within the widened tuple-aware feature library"
        ),
        "holdout_domain": "the full width-4 unlabeled orbit family",
        "orbit_count": len(rows),
        "mixed_feature_count": len(mixed_features),
        "pair_exact": [list(item) for item in pair_exact],
        "nontrivial_pair_exact": [list(item) for item in nontrivial_pair_exact],
        "strongest_claim": (
            "On the full width-4 unlabeled orbit family, within the searched "
            "mixed tuple-aware library, the only nontrivial exact pair bases are "
            "(count_private_roles, distance_multiset) and "
            "(count_size2_roles, distance_multiset)."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
