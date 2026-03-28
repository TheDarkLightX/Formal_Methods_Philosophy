#!/usr/bin/env python3
from __future__ import annotations

import json
from itertools import chain, combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "generated" / "report.json"


FIELDS = ("guard", "bounds", "transform")
OBS = ("guard_obs", "bounds_obs", "transform_obs")
EDGE_UNIVERSE = tuple((obs, field) for field in FIELDS for obs in OBS)

SEPARABLE = frozenset(
    {
        ("guard_obs", "guard"),
        ("bounds_obs", "bounds"),
        ("transform_obs", "transform"),
    }
)
OVERLAP = frozenset(set(SEPARABLE) | {("transform_obs", "bounds")})
TARGETS = {
    "separable_patch_family": SEPARABLE,
    "overlap_patch_family": OVERLAP,
}


def powerset(items):
    seq = tuple(items)
    for r in range(len(seq) + 1):
        for subset in combinations(seq, r):
            yield frozenset(subset)


def format_edges(edges: frozenset[tuple[str, str]]) -> list[str]:
    return [f"{src}->{dst}" for src, dst in sorted(edges)]


def best_additive_template():
    best = None
    rows = []
    for base in powerset(EDGE_UNIVERSE):
        deltas = {}
        feasible = True
        total_delta = 0
        for name, target in TARGETS.items():
            if not base.issubset(target):
                feasible = False
                break
            delta = target - base
            deltas[name] = delta
            total_delta += len(delta)
        if not feasible:
            continue
        cost = len(base) + total_delta
        row = {
            "base_cost": len(base),
            "delta_cost": total_delta,
            "total_cost": cost,
            "base_edges": format_edges(base),
            "family_deltas": {name: format_edges(delta) for name, delta in deltas.items()},
        }
        rows.append(row)
        if best is None or cost < best["total_cost"]:
            best = row
    assert best is not None
    best_rows = [row for row in rows if row["total_cost"] == best["total_cost"]]
    return best, best_rows


def best_signed_template():
    best = None
    rows = []
    for base in powerset(EDGE_UNIVERSE):
        edits = {}
        total_edit = 0
        for name, target in TARGETS.items():
            adds = target - base
            removes = base - target
            edits[name] = {"add": adds, "remove": removes}
            total_edit += len(adds) + len(removes)
        cost = len(base) + total_edit
        row = {
            "base_cost": len(base),
            "edit_cost": total_edit,
            "total_cost": cost,
            "base_edges": format_edges(base),
            "family_edits": {
                name: {
                    "add": format_edges(edit["add"]),
                    "remove": format_edges(edit["remove"]),
                }
                for name, edit in edits.items()
            },
        }
        rows.append(row)
        if best is None or cost < best["total_cost"]:
            best = row
    assert best is not None
    best_rows = [row for row in rows if row["total_cost"] == best["total_cost"]]
    return best, best_rows


def build_report() -> dict[str, object]:
    additive_best, additive_all = best_additive_template()
    signed_best, signed_all = best_signed_template()
    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "exact compression of the v96 software repair decoders into a shared repair-language template "
            "plus family-specific deltas"
        ),
        "holdout_domain": "exhaustive over all 512 possible decoder-edge bases on the 9-edge universe",
        "survivor": "shared repair-language template",
        "strongest_claim": (
            "The two exact decoder graphs from v96 compress to one shared local-decoder base plus one family-specific "
            "delta edge. Under both additive and signed-edit template models, the unique minimum is the local base "
            "decoder with one extra overlap edge transform_obs->bounds."
        ),
        "targets": {name: format_edges(target) for name, target in TARGETS.items()},
        "additive_template_best": additive_best,
        "additive_template_minima_count": len(additive_all),
        "signed_template_best": signed_best,
        "signed_template_minima_count": len(signed_all),
    }


def main() -> int:
    report = build_report()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
