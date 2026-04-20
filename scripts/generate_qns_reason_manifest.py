#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "assets" / "data" / "qns_candidate_ba_traces.json"
DEFAULT_OUT = ROOT / "assets" / "data" / "qns_reason_manifest.json"
TOP8 = 0xFF


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def bit(item: dict[str, Any]) -> int:
    return int(item["bit"])


def bit_mask(item: dict[str, Any]) -> int:
    return 1 << bit(item)


def names_for_mask(universe: list[dict[str, Any]], mask: int) -> list[str]:
    return [item["name"] for item in universe if mask & bit_mask(item)]


def candidate_reason(row: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    masks = row["input_masks"]
    m = bit_mask(item)
    audited = bool(masks["i1"] & m)
    proposed = bool(masks["i2"] & m) and audited
    allowed = bool(masks["i3"] & m)
    review = bool(masks["i4"] & m)
    hard = bool(masks["i5"] & m)
    if not audited:
        route = "outside_universe"
        reasons = ["outside audited universe"]
    elif not proposed:
        route = "not_proposed"
        reasons = ["not proposed by neural layer"]
    elif hard:
        route = "symbolic_reject"
        reasons = ["hard reject mask contains candidate"]
        if not allowed:
            reasons.append("symbolic allow mask does not contain candidate")
    elif not allowed:
        route = "symbolic_reject"
        reasons = ["symbolic allow mask does not contain candidate"]
    elif review:
        route = "human_review"
        reasons = ["review-required mask contains candidate"]
    else:
        route = "auto_accept"
        reasons = ["audited, proposed, allowed, not hard-rejected, not review-required"]
    qns = row.get("probability", {}).get("qNS", {})
    return {
        "name": item["name"],
        "bit": bit(item),
        "route": route,
        "reasons": reasons,
        "qns_probability": qns.get(item["name"]),
    }


def summarize_candidate_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    universe = data["candidate_universe"]
    out = []
    for row in data["rows"]:
        entries = [candidate_reason(row, item) for item in universe]
        by_route: dict[str, int] = {}
        route_masks: dict[str, int] = {}
        for entry in entries:
            route = entry["route"]
            by_route[route] = by_route.get(route, 0) + 1
            route_masks[route] = route_masks.get(route, 0) | (1 << entry["bit"])
        proposed_explained = (
            route_masks.get("auto_accept", 0)
            | route_masks.get("human_review", 0)
            | route_masks.get("symbolic_reject", 0)
        )
        universe_explained = proposed_explained | route_masks.get("not_proposed", 0)
        out.append(
            {
                "scenario": row["scenario"],
                "prompt": row["prompt"],
                "route_counts": by_route,
                "route_masks": route_masks,
                "proposed_partition_ok": proposed_explained == row["actual"]["o5"],
                "universe_partition_ok": universe_explained == (row["input_masks"]["i1"] & TOP8),
                "unsafe_leak_ok": row["actual"]["o6"] == 0,
                "entries": entries,
            }
        )
    return out


def concept_reason(row: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    masks = row["input_masks"]
    m = bit_mask(item)
    observed = bool(masks["observed"] & m)
    required = bool(masks["required"] & m)
    risk = bool(masks["risk"] & m)
    review = bool(masks["review"] & m)
    if observed and required:
        route = "present_required"
    elif required and not observed:
        route = "missing_required"
    elif observed and risk:
        route = "risk_hit"
    elif observed and review:
        route = "review_hit"
    elif observed:
        route = "observed_optional"
    else:
        route = "not_observed"
    reasons = []
    if observed:
        reasons.append("observed in extracted concept set")
    if required:
        reasons.append("listed in required concept set")
    if risk:
        reasons.append("listed in risk concept set")
    if review:
        reasons.append("listed in review concept set")
    if not reasons:
        reasons.append("not active in this scenario")
    return {
        "name": item["name"],
        "bit": bit(item),
        "route": route,
        "reasons": reasons,
    }


def summarize_concept_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    universe = data["concept_universe"]
    out = []
    for row in data["concept_rows"]:
        entries = [concept_reason(row, item) for item in universe]
        by_route: dict[str, int] = {}
        for entry in entries:
            by_route[entry["route"]] = by_route.get(entry["route"], 0) + 1
        out.append(
            {
                "scenario": row["scenario"],
                "text": row["text"],
                "route_counts": by_route,
                "missing_required": names_for_mask(universe, row["actual"]["missing_required"]),
                "risk_hits": names_for_mask(universe, row["actual"]["risk_hits"]),
                "review_hits": names_for_mask(universe, row["actual"]["review_hits"]),
                "ok": row["ok"],
                "entries": entries,
            }
        )
    return out


def trace_reason(row: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    masks = row["input_masks"]
    m = bit_mask(item)
    observed = bool(masks["observed"] & m)
    safe = bool(masks["safe"] & m)
    forbidden = bool(masks["forbidden"] & m)
    if observed and forbidden:
        route = "forbidden_hit"
    elif observed and safe:
        route = "accepted_trace_class"
    elif observed:
        route = "unclassified_observed"
    else:
        route = "not_observed"
    reasons = []
    if observed:
        reasons.append("observed in trace-class recognizer output")
    if safe:
        reasons.append("listed in safe trace-class set")
    if forbidden:
        reasons.append("listed in forbidden trace-class set")
    if not reasons:
        reasons.append("not active in this scenario")
    return {
        "name": item["name"],
        "bit": bit(item),
        "route": route,
        "reasons": reasons,
    }


def summarize_trace_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    universe = data["trace_universe"]
    out = []
    for row in data["trace_rows"]:
        entries = [trace_reason(row, item) for item in universe]
        by_route: dict[str, int] = {}
        for entry in entries:
            by_route[entry["route"]] = by_route.get(entry["route"], 0) + 1
        out.append(
            {
                "scenario": row["scenario"],
                "description": row["description"],
                "route_counts": by_route,
                "forbidden_hits": names_for_mask(universe, row["actual"]["forbidden_hits"]),
                "accepted_trace": names_for_mask(universe, row["actual"]["accepted_trace"]),
                "unclassified": names_for_mask(universe, row["actual"]["unclassified"]),
                "ok": row["ok"],
                "entries": entries,
            }
        )
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate reason-coded qNS manifest.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    source = args.source if args.source.is_absolute() else ROOT / args.source
    out = args.out if args.out.is_absolute() else ROOT / args.out
    data = read_json(source)
    candidate_rows = summarize_candidate_rows(data)
    concept_rows = summarize_concept_rows(data)
    trace_rows = summarize_trace_rows(data)
    artifact = {
        "schema": "qns_reason_manifest_v1",
        "generator": "scripts/generate_qns_reason_manifest.py",
        "source": rel(source),
        "scope": {
            "claim": (
                "The existing qns8 Tau mask outputs can be compiled into exact "
                "per-atom routing explanations for the bounded candidate, concept, "
                "and trace-class scenarios."
            ),
            "not_claimed": [
                "not semantic correctness of external atom extraction",
                "not probabilistic reasoning inside Tau",
                "not unbounded candidate universes",
                "not upstream nlang semantics",
            ],
        },
        "summary": {
            "ok": bool(data["summary"]["ok"]),
            "candidate_scenario_count": len(candidate_rows),
            "concept_scenario_count": len(concept_rows),
            "trace_scenario_count": len(trace_rows),
            "candidate_proposed_partition_failures": sum(
                1 for row in candidate_rows if not row["proposed_partition_ok"]
            ),
            "candidate_universe_partition_failures": sum(
                1 for row in candidate_rows if not row["universe_partition_ok"]
            ),
            "unsafe_leak_failures": sum(1 for row in candidate_rows if not row["unsafe_leak_ok"]),
            "total_candidate_entries": sum(len(row["entries"]) for row in candidate_rows),
            "total_concept_entries": sum(len(row["entries"]) for row in concept_rows),
            "total_trace_entries": sum(len(row["entries"]) for row in trace_rows),
        },
        "candidate_rows": candidate_rows,
        "concept_rows": concept_rows,
        "trace_rows": trace_rows,
    }
    write_json(out, artifact)
    print(
        json.dumps(
            {
                "ok": artifact["summary"]["ok"],
                "out": rel(out),
                "candidate_entries": artifact["summary"]["total_candidate_entries"],
            },
            indent=2,
        )
    )
    return 0 if artifact["summary"]["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
