#!/usr/bin/env python3
from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
OUT = ROOT / "generated" / "report.json"
V49 = REPO_ROOT / "experiments" / "math_object_innovation_v49" / "generated" / "report.json"


def parse_formula(formula: str):
    literals = {}
    for literal in formula.split(" and "):
        negative = literal.startswith("not ")
        feature = literal[4:] if negative else literal
        literals[feature] = not negative
    return literals


def bundle_used(core_formula: str, patch_formula: str):
    core = parse_formula(core_formula)
    patch = parse_formula(patch_formula)
    families = set()
    for feature in sorted(set(core) | set(patch)):
        in_core = feature in core
        in_patch = feature in patch
        if in_core and in_patch:
            if core[feature] != patch[feature]:
                families.add("FLIP_BUNDLE")
        elif in_patch:
            families.add("ADD_BUNDLE")
        else:
            families.add("DROP_BUNDLE")
    return tuple(sorted(families))


def all_set_partitions(values):
    values = list(values)

    def rec(seq):
        if not seq:
            yield []
            return
        first, rest = seq[0], seq[1:]
        for part in rec(rest):
            yield [(first,), *part]
            for index in range(len(part)):
                merged = tuple(sorted((first,) + tuple(part[index])))
                new_part = part[:index] + [merged] + part[index + 1 :]
                canon = tuple(sorted(tuple(sorted(block)) for block in new_part))
                yield [tuple(block) for block in canon]

    seen = set()
    for partition in rec(values):
        canon = tuple(sorted(tuple(sorted(block)) for block in partition))
        if canon in seen:
            continue
        seen.add(canon)
        yield [tuple(block) for block in canon]


def build_report():
    data = json.loads(V49.read_text(encoding="utf-8"))
    cores = data["core_schemas"]
    patches = data["v41_only_schemas"] + data["v46_only_schemas"]
    patch_indexes = tuple(range(len(patches)))
    family_names = ["ADD_BUNDLE", "DROP_BUNDLE", "FLIP_BUNDLE"]

    subset_best = {}
    for size in range(1, len(patches) + 1):
        for subset in combinations(patch_indexes, size):
            best = None
            best_assignment = None
            for family_count in [1, 2, 3]:
                for families in combinations(family_names, family_count):
                    allowed = set(families)
                    assignment = []
                    total_ops = 0
                    ok = True
                    for patch_index in subset:
                        chosen = None
                        for core in cores:
                            used = set(bundle_used(core, patches[patch_index]))
                            if used.issubset(allowed):
                                chosen = (core, tuple(sorted(used)))
                                total_ops += len(used)
                                break
                        if chosen is None:
                            ok = False
                            break
                        assignment.append(chosen)
                    if not ok:
                        continue
                    score = (family_count, total_ops, tuple(sorted(allowed)))
                    if best is None or score < best:
                        best = score
                        best_assignment = assignment
                if best is not None:
                    break
            subset_best[subset] = (best, best_assignment)

    best_partition_score = None
    best_partition = None
    partition_count = 0
    for partition in all_set_partitions(patch_indexes):
        partition_count += 1
        mixed_patch_count = 0
        mixed_fiber_count = 0
        total_family_count = 0
        total_ops = 0
        description = []
        for block in partition:
            (family_count, ops, allowed), assignment = subset_best[block]
            if family_count > 1:
                mixed_patch_count += len(block)
                mixed_fiber_count += 1
            total_family_count += family_count
            total_ops += ops
            description.append((block, allowed, ops, assignment))
        score = (
            mixed_patch_count,
            mixed_fiber_count,
            len(partition),
            total_family_count,
            total_ops,
        )
        if best_partition_score is None or score < best_partition_score:
            best_partition_score = score
            best_partition = description

    mixed_patch_count, mixed_fiber_count, fiber_count, total_family_count, total_ops = best_partition_score

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "explanation-fiber decomposition over the five residual semantic patches "
            "from v49, using bundled macro families ADD_BUNDLE, DROP_BUNDLE, and FLIP_BUNDLE"
        ),
        "holdout_domain": "the five residual patch formulas from the v49 core-plus-patch frontier",
        "survivor": "semantic fiber decomposition frontier",
        "patch_count": len(patches),
        "partition_count": partition_count,
        "best_score": {
            "mixed_patch_count": mixed_patch_count,
            "mixed_fiber_count": mixed_fiber_count,
            "fiber_count": fiber_count,
            "total_family_count": total_family_count,
            "total_ops": total_ops,
        },
        "best_fibers": [
            {
                "patch_indexes": list(block),
                "family_subset": list(allowed),
                "ops": ops,
                "patches": [
                    {
                        "patch": patches[patch_index],
                        "core": core,
                        "used_families": list(used),
                    }
                    for patch_index, (core, used) in zip(block, assignment)
                ],
            }
            for block, allowed, ops, assignment in best_partition
        ],
        "strongest_claim": (
            "The five residual semantic patches admit an exact explanation-fiber "
            "decomposition with only one mixed patch: three patches lie in a pure "
            "FLIP_BUNDLE fiber, one lies in a pure ADD_BUNDLE fiber, and only one "
            "requires a mixed ADD_BUNDLE plus DROP_BUNDLE singleton fiber."
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
