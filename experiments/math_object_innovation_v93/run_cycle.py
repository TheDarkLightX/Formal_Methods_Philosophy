#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import dataclass
from itertools import permutations, product
from pathlib import Path
from typing import Callable, Iterable


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "generated" / "report.json"


WATCH = 1
REPEAT = 2
REVIEW = 3
ACTIONS = (WATCH, REPEAT, REVIEW)
ACTION_NAMES = {
    WATCH: "watch",
    REPEAT: "repeat_lab",
    REVIEW: "human_review",
}

NORMAL = 0
BORDERLINE = 1
ABNORMAL = 2
INPUTS = tuple(
    (band, fresh, red_flag)
    for band in (NORMAL, BORDERLINE, ABNORMAL)
    for fresh in (0, 1)
    for red_flag in (0, 1)
)

PREDICATE_ORDER = (
    "override",
    "was_review",
    "repeat_and_abnormal",
    "nonzero_result",
)


def spec_action(prev_action: int, inp: tuple[int, int, int]) -> int:
    band, fresh, red_flag = inp
    if red_flag or not fresh:
        return REVIEW
    if prev_action == REVIEW:
        return REVIEW
    if prev_action == REPEAT and band == ABNORMAL:
        return REVIEW
    if band != NORMAL:
        return REPEAT
    return WATCH


def predicate_override(prev_action: int, inp: tuple[int, int, int]) -> bool:
    _, fresh, red_flag = inp
    return bool(red_flag or not fresh)


def predicate_was_review(prev_action: int, inp: tuple[int, int, int]) -> bool:
    return prev_action == REVIEW


def predicate_repeat_and_abnormal(prev_action: int, inp: tuple[int, int, int]) -> bool:
    band, _, _ = inp
    return prev_action == REPEAT and band == ABNORMAL


def predicate_nonzero_result(prev_action: int, inp: tuple[int, int, int]) -> bool:
    band, _, _ = inp
    return band != NORMAL


PREDICATES: dict[str, Callable[[int, tuple[int, int, int]], bool]] = {
    "override": predicate_override,
    "was_review": predicate_was_review,
    "repeat_and_abnormal": predicate_repeat_and_abnormal,
    "nonzero_result": predicate_nonzero_result,
}


@dataclass(frozen=True)
class Candidate:
    order: tuple[str, ...]
    branch_actions: tuple[int, int, int, int]
    default_action: int

    def act(self, prev_action: int, inp: tuple[int, int, int]) -> int:
        for predicate_name, action in zip(self.order, self.branch_actions):
            if PREDICATES[predicate_name](prev_action, inp):
                return action
        return self.default_action

    def short_name(self) -> str:
        rule_text = ", ".join(
            f"{name}->{ACTION_NAMES[action]}"
            for name, action in zip(self.order, self.branch_actions)
        )
        return f"[{rule_text}] else {ACTION_NAMES[self.default_action]}"


def generate_candidates() -> list[Candidate]:
    candidates: list[Candidate] = []
    for order in permutations(PREDICATE_ORDER):
        for action_tuple in product(ACTIONS, repeat=5):
            candidates.append(
                Candidate(
                    order=order,
                    branch_actions=action_tuple[:4],
                    default_action=action_tuple[4],
                )
            )
    return candidates


def flat_trace_obligations() -> tuple[tuple[tuple[int, int, int], tuple[int, int, int]], ...]:
    return tuple((inp1, inp2) for inp1 in INPUTS for inp2 in INPUTS)


def monitor_cells() -> tuple[tuple[int, tuple[int, int, int]], ...]:
    return tuple((prev_action, inp) for prev_action in ACTIONS for inp in INPUTS)


def trace_pass(candidate: Candidate, obligation: tuple[tuple[int, int, int], tuple[int, int, int]]) -> bool:
    inp1, inp2 = obligation
    action1 = candidate.act(WATCH, inp1)
    if action1 != spec_action(WATCH, inp1):
        return False
    action2 = candidate.act(action1, inp2)
    return action2 == spec_action(action1, inp2)


def cell_pass(candidate: Candidate, obligation: tuple[int, tuple[int, int, int]]) -> bool:
    prev_action, inp = obligation
    return candidate.act(prev_action, inp) == spec_action(prev_action, inp)


def behavior_signature(
    candidates: Iterable[Candidate],
    obligations: Iterable,
    evaluator: Callable[[Candidate, object], bool],
) -> dict[Candidate, tuple[int, ...]]:
    obligation_list = tuple(obligations)
    return {
        candidate: tuple(int(evaluator(candidate, obligation)) for obligation in obligation_list)
        for candidate in candidates
    }


def greedy_yes_only_checks(
    signatures: dict[Candidate, tuple[int, ...]],
    perfect_candidates: set[Candidate],
) -> dict[str, object]:
    remaining = set(signatures)
    used: set[int] = set()
    trajectory: list[dict[str, int]] = []
    width = len(next(iter(signatures.values())))
    while len(remaining) > len(perfect_candidates):
        best_index = None
        best_failures = -1
        for index in range(width):
            if index in used:
                continue
            failures = sum(1 for candidate in remaining if signatures[candidate][index] == 0)
            if failures > best_failures:
                best_failures = failures
                best_index = index
        if best_index is None or best_failures <= 0:
            break
        used.add(best_index)
        before = len(remaining)
        remaining = {candidate for candidate in remaining if signatures[candidate][best_index] == 1}
        trajectory.append(
            {
                "obligation_index": best_index,
                "before": before,
                "after": len(remaining),
                "eliminated": before - len(remaining),
            }
        )
    return {
        "checks": len(trajectory),
        "remaining": len(remaining),
        "trajectory": trajectory,
    }


def find_spec_controllers(candidates: Iterable[Candidate], cell_signatures: dict[Candidate, tuple[int, ...]]) -> list[Candidate]:
    perfect = [candidate for candidate in candidates if all(cell_signatures[candidate])]
    return sorted(perfect, key=lambda candidate: candidate.short_name())


def build_report() -> dict[str, object]:
    candidates = generate_candidates()
    trace_space = flat_trace_obligations()
    cell_space = monitor_cells()

    trace_signatures = behavior_signature(candidates, trace_space, trace_pass)
    cell_signatures = behavior_signature(candidates, cell_space, cell_pass)

    trace_partition = {candidate: trace_signatures[candidate] for candidate in candidates}
    cell_partition = {candidate: cell_signatures[candidate] for candidate in candidates}

    partition_matches = True
    mismatch_examples: list[dict[str, object]] = []
    for left_index, left in enumerate(candidates):
        left_trace = trace_partition[left]
        left_cell = cell_partition[left]
        for right in candidates[left_index + 1 :]:
            same_trace = left_trace == trace_partition[right]
            same_cell = left_cell == cell_partition[right]
            if same_trace != same_cell:
                partition_matches = False
                mismatch_examples.append(
                    {
                        "left": left.short_name(),
                        "right": right.short_name(),
                        "same_trace": same_trace,
                        "same_cell": same_cell,
                    }
                )
                if len(mismatch_examples) >= 5:
                    break
        if mismatch_examples:
            break

    perfect_trace = {candidate for candidate in candidates if all(trace_signatures[candidate])}
    perfect_cell = {candidate for candidate in candidates if all(cell_signatures[candidate])}
    spec_controllers = find_spec_controllers(candidates, cell_signatures)

    trace_greedy = greedy_yes_only_checks(trace_signatures, perfect_trace)
    cell_greedy = greedy_yes_only_checks(cell_signatures, perfect_cell)

    step1_safe = {
        candidate
        for candidate in candidates
        if all(candidate.act(WATCH, inp) == spec_action(WATCH, inp) for inp in INPUTS)
    }
    step1_trace_signatures = {candidate: trace_signatures[candidate] for candidate in step1_safe}
    step1_cell_signatures = {candidate: cell_signatures[candidate] for candidate in step1_safe}
    staged_partition_matches = True
    staged_mismatch_examples: list[dict[str, object]] = []
    staged_candidates = sorted(step1_safe, key=lambda candidate: candidate.short_name())
    for left_index, left in enumerate(staged_candidates):
        left_trace = step1_trace_signatures[left]
        left_cell = step1_cell_signatures[left]
        for right in staged_candidates[left_index + 1 :]:
            same_trace = left_trace == step1_trace_signatures[right]
            same_cell = left_cell == step1_cell_signatures[right]
            if same_trace != same_cell:
                staged_partition_matches = False
                staged_mismatch_examples.append(
                    {
                        "left": left.short_name(),
                        "right": right.short_name(),
                        "same_trace": same_trace,
                        "same_cell": same_cell,
                    }
                )
                if len(staged_mismatch_examples) >= 5:
                    break
        if staged_mismatch_examples:
            break

    staged_perfect_trace = {candidate for candidate in step1_safe if all(step1_trace_signatures[candidate])}
    staged_perfect_cell = {candidate for candidate in step1_safe if all(step1_cell_signatures[candidate])}
    staged_trace_greedy = greedy_yes_only_checks(step1_trace_signatures, staged_perfect_trace)
    staged_cell_greedy = greedy_yes_only_checks(step1_cell_signatures, staged_perfect_cell)

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "bounded temporal controller family for the medical retest tracker safety fragment, "
            "using ordered decision lists over override, was_review, repeat_and_abnormal, and nonzero_result"
        ),
        "holdout_domain": "exhaustive over the same bounded family and all two-step traces from the watch initial state",
        "survivor": "staged temporal monitor-cell obligation quotient",
        "strongest_claim": (
            "On the bounded retest-tracker controller family, raw symbolic monitor cells are too strong if applied "
            "to all candidates at once, but after flat step-1 carving the remaining 144 concrete two-step prefixes "
            "collapse exactly to 36 symbolic monitor cells without changing the spec-equivalence partition."
        ),
        "candidate_count": len(candidates),
        "trace_obligation_count": len(trace_space),
        "monitor_cell_count": len(cell_space),
        "trace_behavior_class_count": len(set(trace_signatures.values())),
        "cell_behavior_class_count": len(set(cell_signatures.values())),
        "partition_matches": partition_matches,
        "partition_mismatch_examples": mismatch_examples,
        "spec_trace_class_size": len(perfect_trace),
        "spec_cell_class_size": len(perfect_cell),
        "trace_and_cell_perfect_sets_match": perfect_trace == perfect_cell,
        "spec_controller_count": len(spec_controllers),
        "spec_controller_examples": [candidate.short_name() for candidate in spec_controllers[:6]],
        "trace_greedy_yes_only": trace_greedy,
        "cell_greedy_yes_only": cell_greedy,
        "step1_safe_candidate_count": len(step1_safe),
        "staged_trace_behavior_class_count": len(set(step1_trace_signatures.values())),
        "staged_cell_behavior_class_count": len(set(step1_cell_signatures.values())),
        "staged_partition_matches": staged_partition_matches,
        "staged_partition_mismatch_examples": staged_mismatch_examples,
        "staged_spec_trace_class_size": len(staged_perfect_trace),
        "staged_spec_cell_class_size": len(staged_perfect_cell),
        "staged_trace_and_cell_perfect_sets_match": staged_perfect_trace == staged_perfect_cell,
        "staged_trace_greedy_yes_only": staged_trace_greedy,
        "staged_cell_greedy_yes_only": staged_cell_greedy,
        "monitor_cell_reduction": {
            "raw_obligations": len(trace_space),
            "cell_obligations": len(cell_space),
            "reduction": len(trace_space) - len(cell_space),
            "ratio": round(len(trace_space) / len(cell_space), 3),
        },
    }


def main() -> int:
    report = build_report()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
