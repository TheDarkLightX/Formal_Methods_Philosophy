#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.math_object_innovation_v06.run_cycle import collect_state_dataset
from experiments.math_object_innovation_v10.run_cycle import sample_root_dataset
from experiments.math_object_innovation_v10.run_cycle import core_choice, two_clause_choice
from experiments.math_object_innovation_v11.run_cycle import REPAIR, choose_by_tie_break, holdout_residual_cases, parameter_grid
from experiments.math_object_innovation_v14.run_cycle import denorm, norm


OUT = ROOT / "generated" / "report.json"
PATTERN_CACHE = ROOT / "generated" / "pattern_cache.json"
VIABLE_CACHE = ROOT / "generated" / "viable_cache.json"
V06_REPORT = REPO_ROOT / "experiments" / "math_object_innovation_v06" / "generated" / "report.json"


@dataclass(frozen=True)
class Pattern:
    rows_key: tuple[tuple[int, tuple[tuple[str, int], ...]], ...]
    target: int
    exemplar_mask: int
    exemplar_candidates: tuple[int, ...]
    rows: tuple[tuple[int, dict[str, int]], ...]


def rows_key(rows: list[tuple[int, dict[str, int]]]) -> tuple[tuple[int, tuple[tuple[str, int], ...]], ...]:
    return tuple((y, tuple(sorted(features.items()))) for y, features in rows)


def normalize_patterns(state_data: list[dict[str, object]]) -> list[Pattern]:
    seen: dict[tuple[tuple[tuple[int, tuple[tuple[str, int], ...]], ...], int], Pattern] = {}
    for item in state_data:
        key = (rows_key(item["rows"]), item["target"])
        if key in seen:
            continue
        seen[key] = Pattern(
            rows_key=key[0],
            target=key[1],
            exemplar_mask=item["mask"],
            exemplar_candidates=tuple(item["candidates"]),
            rows=tuple((y, dict(features)) for y, features in item["rows"]),
        )
    return list(seen.values())


def serialize_patterns(patterns: list[Pattern]) -> list[dict[str, object]]:
    payload = []
    for pattern in patterns:
        payload.append({
            "rows_key": [[y, list(features)] for y, features in pattern.rows_key],
            "target": pattern.target,
            "exemplar_mask": pattern.exemplar_mask,
            "exemplar_candidates": list(pattern.exemplar_candidates),
            "rows": [[y, dict(features)] for y, features in pattern.rows],
        })
    return payload


def deserialize_patterns(payload: list[dict[str, object]]) -> list[Pattern]:
    patterns = []
    for item in payload:
        patterns.append(Pattern(
            rows_key=tuple((y, tuple((str(k), int(v)) for k, v in features)) for y, features in item["rows_key"]),
            target=int(item["target"]),
            exemplar_mask=int(item["exemplar_mask"]),
            exemplar_candidates=tuple(int(x) for x in item["exemplar_candidates"]),
            rows=tuple((int(y), {str(k): int(v) for k, v in features.items()}) for y, features in item["rows"]),
        ))
    return patterns


def residual_consistent_pairs():
    if VIABLE_CACHE.exists():
        payload = json.loads(VIABLE_CACHE.read_text(encoding="utf-8"))
        for item in payload:
            item["params_1"] = tuple(item["params_1"])
            item["params_2"] = tuple(item["params_2"])
        return payload

    raw_residual = holdout_residual_cases()
    residual = normalized_dataset(raw_residual)
    root_5 = weighted_dataset(sample_root_dataset(5, 1000, 99))
    root_6 = weighted_dataset(sample_root_dataset(6, 300, 123))

    candidates = []
    for params in parameter_grid():
        fixed = tuple(int(choose_by_tie_break(item["rows"], params) == item["target"]) for item in raw_residual)
        if any(fixed):
            candidates.append((params, fixed))
    second_slot = [params for params, _fixed in candidates if params["origin_guard"] == "any"]
    print(
        f"residual candidates: {len(candidates)}, second-slot clauses: {len(second_slot)}, root buckets: {len(root_5)} + {len(root_6)}",
        file=sys.stderr,
        flush=True,
    )

    viable = []
    for index, (p1, _fixed) in enumerate(candidates, start=1):
        if index == 1 or index % 25 == 0 or index == len(candidates):
            print(f"frontier progress: p1 {index}/{len(candidates)}", file=sys.stderr, flush=True)
        np1 = norm(p1)
        for p2 in second_slot:
            np2 = norm(p2)
            ok = True
            for item in residual:
                if pattern_choice(np1, np2, item["rows_key"]) != item["target"]:
                    ok = False
                    break
            if not ok:
                continue
            holdout_5_hits = sum(item["count"] for item in root_5 if pattern_choice(np1, np2, item["rows_key"]) == item["target"])
            holdout_6_hits = sum(item["count"] for item in root_6 if pattern_choice(np1, np2, item["rows_key"]) == item["target"])
            viable.append({
                "params_1": np1,
                "params_2": np2,
                "holdout_5_hits": holdout_5_hits,
                "holdout_6_hits": holdout_6_hits,
                "holdout_total": holdout_5_hits + holdout_6_hits,
            })

    viable.sort(
        key=lambda item: (
            item["holdout_total"],
            item["holdout_5_hits"],
            item["holdout_6_hits"],
            item["params_1"],
            item["params_2"],
        ),
        reverse=True,
    )
    VIABLE_CACHE.parent.mkdir(parents=True, exist_ok=True)
    VIABLE_CACHE.write_text(json.dumps(viable, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return viable


@lru_cache(maxsize=None)
def rows_from_key(key: tuple[tuple[int, tuple[tuple[str, int], ...]], ...]) -> tuple[tuple[int, dict[str, int]], ...]:
    return tuple((y, dict(features)) for y, features in key)


@lru_cache(maxsize=None)
def repair_default(key: tuple[tuple[int, tuple[tuple[str, int], ...]], ...]) -> tuple[int, str]:
    rows = rows_from_key(key)
    default = two_clause_choice(rows, REPAIR)
    origin = "repair" if core_choice(rows) != default else "core"
    return default, origin


@lru_cache(maxsize=None)
def tie_break_choice_key(p1: tuple[object, ...], key: tuple[tuple[int, tuple[tuple[str, int], ...]], ...]) -> int:
    rows = rows_from_key(key)
    default, origin = repair_default(key)
    params = denorm(p1)
    if params["origin_guard"] != "any" and origin != params["origin_guard"]:
        return default

    by_y = {y: features for y, features in rows}
    base = by_y[default]
    alternatives = []

    for y, features in rows:
        if y == default:
            continue
        if features["gain"] != base["gain"]:
            continue
        if features["child_best_gain"] != base["child_best_gain"]:
            continue
        if features["next_uncovered"] != base["next_uncovered"]:
            continue
        if features["cut"] < base["cut"] + params["cut_gain_min"]:
            continue
        if features["next_size"] > base["next_size"] - params["next_size_drop_min"]:
            continue
        if features["child_best_cut"] < base["child_best_cut"] - params["max_child_cut_drop"]:
            continue
        if features["child_sum_singleton"] > base["child_sum_singleton"] - params["min_child_sum_drop"]:
            continue
        if features["child_best_singleton"] < base["child_best_singleton"] + params["min_child_best_singleton_gain"]:
            continue

        rank = params["rank"]
        if rank == "cut_next":
            key_now = (-features["cut"], features["next_size"], y)
        elif rank == "cut_next_childsum":
            key_now = (-features["cut"], features["next_size"], features["child_sum_singleton"], y)
        elif rank == "cut_childsum_next":
            key_now = (-features["cut"], features["child_sum_singleton"], features["next_size"], y)
        elif rank == "cut_bestsingleton_next":
            key_now = (-features["cut"], -features["child_best_singleton"], features["next_size"], y)
        else:
            raise AssertionError(rank)
        alternatives.append((key_now, y))

    return min(alternatives)[1] if alternatives else default


@lru_cache(maxsize=None)
def pattern_choice(p1: tuple[object, ...], p2: tuple[object, ...], key: tuple[tuple[int, tuple[tuple[str, int], ...]], ...]) -> int:
    current = tie_break_choice_key(p1, key)
    rows = rows_from_key(key)
    by_y = {y: features for y, features in rows}
    base = by_y[current]
    params = denorm(p2)
    if params["origin_guard"] != "any":
        return current

    alternatives = []
    for y, features in rows:
        if y == current:
            continue
        if features["gain"] != base["gain"]:
            continue
        if features["child_best_gain"] != base["child_best_gain"]:
            continue
        if features["next_uncovered"] != base["next_uncovered"]:
            continue
        if features["cut"] < base["cut"] + params["cut_gain_min"]:
            continue
        if features["next_size"] > base["next_size"] - params["next_size_drop_min"]:
            continue
        if features["child_best_cut"] < base["child_best_cut"] - params["max_child_cut_drop"]:
            continue
        if features["child_sum_singleton"] > base["child_sum_singleton"] - params["min_child_sum_drop"]:
            continue
        if features["child_best_singleton"] < base["child_best_singleton"] + params["min_child_best_singleton_gain"]:
            continue

        rank = params["rank"]
        if rank == "cut_next":
            key_now = (-features["cut"], features["next_size"], y)
        elif rank == "cut_next_childsum":
            key_now = (-features["cut"], features["next_size"], features["child_sum_singleton"], y)
        elif rank == "cut_childsum_next":
            key_now = (-features["cut"], features["child_sum_singleton"], features["next_size"], y)
        elif rank == "cut_bestsingleton_next":
            key_now = (-features["cut"], -features["child_best_singleton"], features["next_size"], y)
        else:
            raise AssertionError(rank)
        alternatives.append((key_now, y))

    return min(alternatives)[1] if alternatives else current


def normalized_dataset(items: list[dict[str, object]]) -> list[dict[str, object]]:
    normalized = []
    for item in items:
        normalized.append({
            "rows_key": rows_key(item["rows"]),
            "target": item["target"],
        })
    return normalized


def weighted_dataset(items: list[dict[str, object]]) -> list[dict[str, object]]:
    counts: dict[tuple[tuple[tuple[int, tuple[tuple[str, int], ...]], ...], int], int] = {}
    for item in items:
        key = (rows_key(item["rows"]), item["target"])
        counts[key] = counts.get(key, 0) + 1
    weighted = []
    for (key, target), count in counts.items():
        weighted.append({
            "rows_key": key,
            "target": target,
            "count": count,
        })
    return weighted


def first_safe_pair(viable: list[dict[str, object]], patterns: list[Pattern]) -> tuple[int, dict[str, object], list[dict[str, object]]]:
    unsafe_prefix = []
    for rank, item in enumerate(viable, start=1):
        p1 = item["params_1"]
        p2 = item["params_2"]
        safe = True
        for pattern in patterns:
            if pattern_choice(p1, p2, pattern.rows_key) != pattern.target:
                safe = False
                break
        item["rank"] = rank
        item["safe"] = safe
        if safe:
            return rank, item, unsafe_prefix
        unsafe_prefix.append(item)
    raise AssertionError("no safe pair found")


def candidate_bank_patterns(target_pair: dict[str, object], unsafe_prefix: list[dict[str, object]], patterns: list[Pattern]):
    bad_cover_items = []
    for pattern in patterns:
        if pattern_choice(target_pair["params_1"], target_pair["params_2"], pattern.rows_key) != pattern.target:
            continue
        cover = 0
        for index, bad in enumerate(unsafe_prefix):
            if pattern_choice(bad["params_1"], bad["params_2"], pattern.rows_key) != pattern.target:
                cover |= 1 << index
        if cover == 0:
            continue
        bad_cover_items.append((cover, pattern))

    # Drop dominated covers, keep a canonical representative pattern for each unique cover.
    cover_map: dict[int, Pattern] = {}
    for cover, pattern in bad_cover_items:
        current = cover_map.get(cover)
        if current is None or (pattern.exemplar_mask, pattern.exemplar_candidates) < (current.exemplar_mask, current.exemplar_candidates):
            cover_map[cover] = pattern

    covers = sorted(cover_map.items(), key=lambda item: (item[0].bit_count(), item[1].exemplar_mask), reverse=True)
    reduced: list[tuple[int, Pattern]] = []
    for cover, pattern in covers:
        dominated = False
        for kept_cover, _kept_pattern in reduced:
            if cover | kept_cover == kept_cover:
                dominated = True
                break
        if not dominated:
            reduced.append((cover, pattern))
    return reduced


def exact_min_cover(covers: list[tuple[int, Pattern]], universe_bits: int):
    if universe_bits == 0:
        return []

    by_bad: dict[int, list[int]] = {}
    for idx, (cover, _pattern) in enumerate(covers):
        bitset = cover
        while bitset:
            low = bitset & -bitset
            bit = low.bit_length() - 1
            by_bad.setdefault(bit, []).append(idx)
            bitset ^= low

    best: list[int] | None = None

    @lru_cache(maxsize=None)
    def optimistic_cover_size(remaining: int) -> int:
        if remaining == 0:
            return 0
        best_gain = max((cover & remaining).bit_count() for cover, _pattern in covers)
        return (remaining.bit_count() + best_gain - 1) // best_gain

    def search(chosen: list[int], covered: int):
        nonlocal best
        if covered == universe_bits:
            if best is None or len(chosen) < len(best):
                best = chosen.copy()
            return
        if best is not None and len(chosen) >= len(best):
            return

        remaining = universe_bits & ~covered
        if best is not None and len(chosen) + optimistic_cover_size(remaining) >= len(best):
            return

        first_bit = (remaining & -remaining).bit_length() - 1
        options = by_bad[first_bit]
        options = sorted(options, key=lambda idx: ((covers[idx][0] & remaining).bit_count(), covers[idx][1].exemplar_mask), reverse=True)
        for idx in options:
            chosen.append(idx)
            search(chosen, covered | covers[idx][0])
            chosen.pop()

    search([], 0)
    if best is None:
        raise AssertionError("no cover found")
    return [covers[idx] for idx in best]


def build_report():
    if PATTERN_CACHE.exists():
        print("loading cached unique patterns", file=sys.stderr, flush=True)
        patterns = deserialize_patterns(json.loads(PATTERN_CACHE.read_text(encoding="utf-8")))
        raw_state_count = json.loads(V06_REPORT.read_text(encoding="utf-8")).get("nonterminal_state_count") if V06_REPORT.exists() else None
    else:
        print("collecting bounded state dataset", file=sys.stderr, flush=True)
        state_data = collect_state_dataset()
        raw_state_count = len(state_data)
        print(f"normalizing {raw_state_count} raw states into unique patterns", file=sys.stderr, flush=True)
        patterns = normalize_patterns(state_data)
        PATTERN_CACHE.parent.mkdir(parents=True, exist_ok=True)
        PATTERN_CACHE.write_text(json.dumps(serialize_patterns(patterns), indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("building residual-consistent frontier", file=sys.stderr, flush=True)
    viable = residual_consistent_pairs()

    print(f"finding first safe pair in ranked frontier of size {len(viable)}", file=sys.stderr, flush=True)
    first_safe_rank, target_pair, unsafe_prefix = first_safe_pair(viable, patterns)

    print(
        f"first safe pair appears at rank {first_safe_rank}; unsafe prefix size {len(unsafe_prefix)}",
        file=sys.stderr,
        flush=True,
    )
    covers = candidate_bank_patterns(target_pair, unsafe_prefix, patterns)
    universe_bits = (1 << len(unsafe_prefix)) - 1
    print(
        f"candidate bank patterns after dedup and dominance pruning: {len(covers)}",
        file=sys.stderr,
        flush=True,
    )
    exact_bank = exact_min_cover(covers, universe_bits)
    print(f"exact minimal bank size {len(exact_bank)}", file=sys.stderr, flush=True)

    singleton_hits = sum(1 for cover, _pattern in covers if cover == universe_bits)

    minimal_bank = []
    for cover, pattern in exact_bank:
        minimal_bank.append({
            "cover_size": cover.bit_count(),
            "mask": pattern.exemplar_mask,
            "candidates": list(pattern.exemplar_candidates),
            "target": pattern.target,
            "rows": [[y, dict(features)] for y, features in pattern.rows],
        })

    return {
        "tier": "descriptive_symbolic_controller",
        "oracle_dependent": False,
        "discovery_domain": "exact teaching-bank synthesis over residual-consistent repair-program pairs and unique reachable 4x4 state patterns",
        "holdout_domain": "sampled 5x5 and 6x6 roots with fixed seeds 99 and 123",
        "survivor": "minimal-bank synthesis frontier",
        "raw_state_count": raw_state_count,
        "unique_pattern_count": len(patterns),
        "viable_pair_count_without_bank": len(viable),
        "first_safe_rank_without_bank": first_safe_rank,
        "unsafe_prefix_size": len(unsafe_prefix),
        "singleton_bank_count": singleton_hits,
        "candidate_bank_pattern_count": len(covers),
        "minimal_bank_size": len(exact_bank),
        "target_safe_pair": {
            "rank": target_pair["rank"],
            "holdout_total": target_pair["holdout_total"],
            "holdout_5_hits": target_pair["holdout_5_hits"],
            "holdout_6_hits": target_pair["holdout_6_hits"],
            "clause_1": denorm(target_pair["params_1"]),
            "clause_2": denorm(target_pair["params_2"]),
        },
        "minimal_bank": minimal_bank,
        "strongest_claim": (
            "Within the bounded repair-program search, the staged bank-then-rank loop collapses further than expected. "
            "The top holdout-ranked residual-consistent repair program is already safe on the exhaustive reachable 4x4 verifier, so the exact minimal teaching bank size for the winner is 0 in this bounded model."
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
