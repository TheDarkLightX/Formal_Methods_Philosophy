#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "generated" / "report.json"


EVENTS = [
    {
        "cycle": "v78",
        "intervention_class": "family_comparison",
        "intervention": "minimal witness-language phase diagram on the hard frontier",
        "outcome": "baseline_ordering",
        "gain_events": 0,
        "adds_new_search_axis": True,
        "why": "established the first strict family ladder, 27 -> 22 -> 19, without changing the incumbent yet",
    },
    {
        "cycle": "v79",
        "intervention_class": "comparison_family",
        "intervention": "exact bit-fiber decomposition against the current label-level language",
        "outcome": "boundary",
        "gain_events": 0,
        "adds_new_search_axis": True,
        "why": "showed decomposition is exact but loses, 24/21 versus 22/19",
    },
    {
        "cycle": "v80",
        "intervention_class": "comparison_family",
        "intervention": "strict all-positive certificates against the same hard partition",
        "outcome": "boundary",
        "gain_events": 0,
        "adds_new_search_axis": True,
        "why": "showed strict certification fails exactness on region (10,11)",
    },
    {
        "cycle": "v81",
        "intervention_class": "new_axis",
        "intervention": "residual-budget search on the hard merged partition",
        "outcome": "frontier_gain",
        "gain_events": 5,
        "adds_new_search_axis": True,
        "why": "introduced the residual-budget ladder, 28 -> 26 -> 24 -> 23 -> 22",
    },
    {
        "cycle": "v82",
        "intervention_class": "new_axis",
        "intervention": "global schema sharing on the residual-budget ladder",
        "outcome": "frontier_gain",
        "gain_events": 5,
        "adds_new_search_axis": True,
        "why": "improved every feasible rung by exactly one shared schema, 25 -> 23 -> 21 -> 20 -> 19",
    },
    {
        "cycle": "v83",
        "intervention_class": "new_axis",
        "intervention": "joint partition plus residual-budget search",
        "outcome": "frontier_gain",
        "gain_events": 4,
        "adds_new_search_axis": True,
        "why": "improved shared-schema counts on budgets 1 through 4 by making partition part of the search",
    },
    {
        "cycle": "v84",
        "intervention_class": "grammar_widening",
        "intervention": "local certificate widening from 1..4 to 1..5 literals",
        "outcome": "localized_gain",
        "gain_events": 1,
        "adds_new_search_axis": False,
        "why": "moved exactly one critical region, (10,11), from impossible to exact cost 6",
    },
    {
        "cycle": "v85",
        "intervention_class": "grammar_widening",
        "intervention": "global widened-certificate search on the joint partition-aware frontier",
        "outcome": "frontier_gain",
        "gain_events": 3,
        "adds_new_search_axis": False,
        "why": "opened the low-residual regime globally, adding budget 0 and improving budgets 1 and 2",
    },
    {
        "cycle": "v86",
        "intervention_class": "grammar_widening",
        "intervention": "high-residual widening from 1..5 to 1..6 literals",
        "outcome": "saturation",
        "gain_events": 0,
        "adds_new_search_axis": False,
        "why": "did not move budgets 3 through 5",
    },
    {
        "cycle": "v87",
        "intervention_class": "grammar_widening",
        "intervention": "low-residual widening from 1..5 to 1..6 literals",
        "outcome": "saturation",
        "gain_events": 0,
        "adds_new_search_axis": False,
        "why": "did not move budgets 0 through 2",
    },
    {
        "cycle": "v88",
        "intervention_class": "new_axis",
        "intervention": "transfer the joint partition-aware residual-budget loop to lab-followup",
        "outcome": "frontier_gain",
        "gain_events": 1,
        "adds_new_search_axis": True,
        "why": "produced a new exact transfer object, one merged residual region with best cost 4",
    },
    {
        "cycle": "v89",
        "intervention_class": "grammar_widening",
        "intervention": "lab-followup widened certificates from 1..4 to 1..5 literals",
        "outcome": "saturation",
        "gain_events": 0,
        "adds_new_search_axis": False,
        "why": "did not move any rung of the lab-followup ladder",
    },
    {
        "cycle": "v90",
        "intervention_class": "new_axis",
        "intervention": "score-free semantic explanation search on the full lab-followup unsafe block",
        "outcome": "frontier_gain",
        "gain_events": 1,
        "adds_new_search_axis": True,
        "why": "found an exact earliest-error residual-default law with cost 4 versus best all-positive cost 5",
    },
    {
        "cycle": "v91",
        "intervention_class": "new_axis",
        "intervention": "score-free merged-subunion search on the refill frontier",
        "outcome": "boundary",
        "gain_events": 0,
        "adds_new_search_axis": True,
        "why": "showed refill does not admit a whole-block score-free law, only sparse exact islands up to size 3",
    },
]


NEXT_FAMILIES = [
    {
        "rank": 1,
        "family": "temporal_monitor_cell_obligation_carving",
        "new_axis": "temporal obligation cells rather than flat examples or static score regions",
        "first_experiment": "bounded monitor-cell carving on medical_retest_protocol_tracker_v1.tau, comparing flat trace counterexamples against monitor-cell carving",
    },
    {
        "rank": 2,
        "family": "temporal_minimal_witness_language_discovery",
        "new_axis": "minimal witness languages over monitor cells, prefix cylinders, and residual-default temporal contracts",
        "first_experiment": "phase diagram over temporal witness contracts on the retest tracker safety fragment",
    },
    {
        "rank": 3,
        "family": "semantic_predicate_invention",
        "new_axis": "invent new exact predicates when literal-width sweeps saturate",
        "first_experiment": "search a tiny semantic predicate grammar that enlarges the maximal exact refill merged subset beyond (9,10,12)",
    },
    {
        "rank": 4,
        "family": "explanation_fiber_decomposition_for_temporal_specs",
        "new_axis": "decompose temporal specs into override, transition, and progress fibers before witness search",
        "first_experiment": "split the retest tracker into three fibers and search exact local witness languages on each",
    },
]


def aggregate():
    by_class = defaultdict(lambda: {"cycles": 0, "gain_cycles": 0, "gain_events": 0, "boundary_cycles": 0, "saturation_cycles": 0})
    by_axis = defaultdict(lambda: {"cycles": 0, "gain_cycles": 0, "gain_events": 0})
    outcome_counts = Counter()
    for event in EVENTS:
        cls = by_class[event["intervention_class"]]
        cls["cycles"] += 1
        cls["gain_events"] += event["gain_events"]
        if event["outcome"] in {"frontier_gain", "localized_gain"}:
            cls["gain_cycles"] += 1
        if event["outcome"] == "boundary":
            cls["boundary_cycles"] += 1
        if event["outcome"] == "saturation":
            cls["saturation_cycles"] += 1

        axis = "new_search_axis" if event["adds_new_search_axis"] else "same_axis_widening"
        axis_stats = by_axis[axis]
        axis_stats["cycles"] += 1
        axis_stats["gain_events"] += event["gain_events"]
        if event["outcome"] in {"frontier_gain", "localized_gain"}:
            axis_stats["gain_cycles"] += 1

        outcome_counts[event["outcome"]] += 1
    return by_class, by_axis, outcome_counts


def build_report():
    by_class, by_axis, outcome_counts = aggregate()
    strongest_classes = sorted(
        (
            {
                "intervention_class": name,
                **stats,
            }
            for name, stats in by_class.items()
        ),
        key=lambda item: (-item["gain_events"], -item["gain_cycles"], item["intervention_class"]),
    )

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "meta-analysis of frontier-moving interventions across the mature witness-language, residual-budget, "
            "transfer, and explanatory-law line from v78 to v91"
        ),
        "holdout_domain": "the published exact hard-frontier and lab-followup frontier cycles from v78 to v91",
        "survivor": "unlock taxonomy for the mature witness-language line",
        "event_count": len(EVENTS),
        "outcome_counts": dict(outcome_counts),
        "axis_summary": {
            name: stats for name, stats in sorted(by_axis.items())
        },
        "class_summary": strongest_classes,
        "events": EVENTS,
        "next_family_ranking": NEXT_FAMILIES,
        "strongest_claim": (
            "Across the mature witness-language line from v78 to v91, the biggest exact frontier gains came from "
            "adding new structural search axes, residual budgets, global schema sharing, joint partition search, "
            "transfer as a first-class object, and semantic explanation search, rather than from widening the "
            "existing formula grammar. New-axis interventions account for 5 of the 6 frontier-gain cycles and 16 "
            "of the 21 gain-events in this bounded corpus, while grammar widening yields only one local slice gain, "
            "one partial global gain, and then saturates. The next honest rabbit hole is therefore temporal "
            "obligation geometry, especially monitor-cell obligation carving on Tau specs."
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
