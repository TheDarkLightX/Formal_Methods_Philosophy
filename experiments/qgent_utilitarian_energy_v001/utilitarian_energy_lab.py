"""Train and verify a 100-step utilitarian energy-ranked Qagent.

The benchmark is deliberately finite and synthetic. Each day, an agent chooses
one resource-allocation action for four communities. The declared objective is
the undiscounted sum of synthetic person-welfare increments over 100 days.

An exact dynamic program labels state-action comparisons in training worlds.
A small action-conditional linear energy model distils those comparisons. At
inference, its quantized scores are compiled into a literal lookup Q-table.
Tau composes Boolean receipts from deterministic utility, ranking, resource,
sequence, and commitment checkers. The learned model proposes; the simulator
and Tau policy decide whether a proposal is admissible.

This is not a claim that the synthetic scores measure real welfare or that
total utilitarianism is morally correct or complete.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import zipfile
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
TAU_POLICY = Path(__file__).with_name("utilitarian_policy_v1.tau")
TAU_NOTICE = Path(__file__).with_name("TAU_DISTRIBUTION_NOTICE.md")
LOCAL_LAUNCH_GUIDE = Path(__file__).with_name("LOCAL_LAUNCH.md")
LAB_PAGE = ROOT / "qgent_utilitarian_energy_lab.html"
LAB_STYLESHEET = ROOT / "assets" / "css" / "qgent-lab.css"
TAU_BRIDGE = ROOT / "scripts" / "tau_local_bridge.py"
LAB_LAUNCHER = ROOT / "scripts" / "launch_qgent_utilitarian_lab.py"

SCHEMA = "qgent-utilitarian-energy-100-v1"
MODEL_SCHEMA = "qgent-action-conditional-linear-energy-v1"
TABLE_SCHEMA = "qgent-100-step-compiled-q-table-v1"
HORIZON = 100
COMMUNITIES = ("harbor", "hills", "river", "central")
ACTION_NAMES = (
    "aid_harbor",
    "aid_hills",
    "aid_river",
    "aid_central",
    "invest_prevention",
    "stockpile_supplies",
    "release_reserve",
    "community_care",
    "hold_resources",
)
ACTION_COUNT = len(ACTION_NAMES)
AID_ACTIONS = tuple(range(4))
PREVENTION = 4
STOCKPILE = 5
RELEASE = 6
COMMUNITY_CARE = 7
HOLD = 8

BUDGET_MAX = 8
CAPACITY_MAX = 5
RESERVE_MAX = 4
DAILY_REFILL = 2
STATE_SHAPE = (BUDGET_MAX + 1, CAPACITY_MAX + 1, RESERVE_MAX + 1)
FORBIDDEN_Q = np.int32(-(2**30))
FEATURE_SCALE = 1_000
WEIGHT_SCALE = 1_000_000
MILLIUTILITY_SCALE = 1_000
RIDGE = 0.75
PUBLIC_SCENARIO_SEED = 730_021
TRAIN_SEEDS = tuple(range(410_000, 410_032))
VALIDATION_SEEDS = tuple(range(510_000, 510_012))
TEST_SEEDS = tuple(range(610_000, 610_020))
TRAINING_BUDGETS = (1, 4, 16, 32)

FEATURE_NAMES = (
    "bias",
    "day_fraction",
    "remaining_fraction",
    "budget",
    "capacity",
    "reserve",
    "immediate_utility",
    "next_budget",
    "next_capacity",
    "next_reserve",
    "need_harbor",
    "need_hills",
    "need_river",
    "need_central",
    "weighted_need_harbor",
    "weighted_need_hills",
    "weighted_need_river",
    "weighted_need_central",
    "future_5_harbor",
    "future_5_hills",
    "future_5_river",
    "future_5_central",
    "future_20_harbor",
    "future_20_hills",
    "future_20_river",
    "future_20_central",
    "future_remaining_harbor",
    "future_remaining_hills",
    "future_remaining_river",
    "future_remaining_central",
    "shock_now",
    "shock_next_10",
    "capacity_by_remaining",
    "reserve_by_future_shock",
)
FEATURE_COUNT = len(FEATURE_NAMES)

State = tuple[int, int, int]


@dataclass(frozen=True)
class Scenario:
    seed: int
    populations: tuple[int, int, int, int]
    needs: tuple[tuple[int, int, int, int], ...]
    shock_groups: tuple[int, ...]


@dataclass(frozen=True)
class Step:
    next_state: State
    welfare: tuple[int, int, int, int]
    total_utility: int
    cost: int
    reserve_target: int | None


@dataclass(frozen=True)
class ScenarioFeatures:
    weighted_needs: np.ndarray
    future_5: np.ndarray
    future_20: np.ndarray
    future_remaining: np.ndarray
    shock_next_10: np.ndarray


@dataclass(frozen=True)
class EnergyModel:
    weights_q: np.ndarray
    training_scenarios: int
    training_examples: int
    model_sha256: str


@dataclass(frozen=True)
class EvaluationCase:
    scenario: Scenario
    exact_q: np.ndarray
    context: ScenarioFeatures
    exact_total: int
    myopic_total: int


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def keyed_int(*parts: object, modulus: int) -> int:
    payload = ":".join(str(part) for part in parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big") % modulus


def make_scenario(
    seed: int,
    *,
    populations: tuple[int, int, int, int] | None = None,
) -> Scenario:
    selected_populations = populations or tuple(
        2 + keyed_int("population", seed, group, modulus=5)
        for group in range(4)
    )
    if len(selected_populations) != 4 or any(
        value <= 0 for value in selected_populations
    ):
        raise ValueError("a scenario requires four positive population units")
    needs: list[tuple[int, int, int, int]] = []
    shocks: list[int] = []
    for day in range(HORIZON):
        shock = (
            keyed_int("shock-present", seed, day, modulus=7) == 0
        )
        shock_group = (
            keyed_int("shock-group", seed, day, modulus=4) if shock else -1
        )
        day_needs = []
        for group in range(4):
            base = 1 + keyed_int("need", seed, day, group, modulus=7)
            cycle = 5 + group
            phase = keyed_int("phase", seed, group, modulus=cycle)
            seasonal = 2 if (day + phase) % cycle in (0, 1) else 0
            shock_increment = 3 if shock_group == group else 0
            day_needs.append(min(9, base + seasonal + shock_increment))
        needs.append(tuple(day_needs))
        shocks.append(shock_group)
    return Scenario(
        seed=seed,
        populations=selected_populations,
        needs=tuple(needs),
        shock_groups=tuple(shocks),
    )


def scenario_manifest(scenario: Scenario) -> dict[str, Any]:
    payload = {
        "seed": scenario.seed,
        "horizon": HORIZON,
        "communities": list(COMMUNITIES),
        "populations_in_hundreds": list(scenario.populations),
        "needs": [list(row) for row in scenario.needs],
        "shock_groups": list(scenario.shock_groups),
    }
    return {**payload, "sha256": sha256_bytes(canonical_json_bytes(payload))}


def allowed_actions(state: State) -> tuple[int, ...]:
    budget, capacity, reserve = state
    allowed: list[int] = [HOLD]
    if budget >= 2:
        allowed.extend(AID_ACTIONS)
    if budget >= 3 and capacity < CAPACITY_MAX:
        allowed.append(PREVENTION)
    if budget >= 2 and reserve < RESERVE_MAX:
        allowed.append(STOCKPILE)
    if reserve > 0:
        allowed.append(RELEASE)
    if budget >= 1:
        allowed.append(COMMUNITY_CARE)
    return tuple(sorted(allowed))


def action_cost(action: int) -> int:
    if action in AID_ACTIONS or action == STOCKPILE:
        return 2
    if action == PREVENTION:
        return 3
    if action == COMMUNITY_CARE:
        return 1
    return 0


def transition(scenario: Scenario, day: int, state: State, action: int) -> Step:
    if not 0 <= day < HORIZON:
        raise ValueError("day is outside the declared 100-step horizon")
    if action not in allowed_actions(state):
        raise ValueError("action is not admitted by the resource mask")
    budget, capacity, reserve = state
    populations = scenario.populations
    needs = scenario.needs[day]
    shock_group = scenario.shock_groups[day]
    welfare = [0, 0, 0, 0]
    reserve_target: int | None = None
    next_capacity = capacity
    next_reserve = reserve

    if action in AID_ACTIONS:
        group = action
        welfare[group] = populations[group] * (needs[group] + 2 + capacity)
    elif action == PREVENTION:
        next_capacity += 1
        welfare = list(populations)
    elif action == STOCKPILE:
        next_reserve += 1
    elif action == RELEASE:
        reserve_target = min(
            range(4),
            key=lambda group: (
                -populations[group]
                * (
                    2 * needs[group]
                    + capacity
                    + (4 if shock_group == group else 0)
                ),
                group,
            ),
        )
        welfare[reserve_target] = populations[reserve_target] * (
            2 * needs[reserve_target]
            + capacity
            + (4 if shock_group == reserve_target else 0)
        )
        next_reserve -= 1
    elif action == COMMUNITY_CARE:
        welfare = [
            population * (1 + int(need >= 7))
            for population, need in zip(populations, needs, strict=True)
        ]

    cost = action_cost(action)
    next_budget = min(BUDGET_MAX, budget - cost + DAILY_REFILL)
    next_state = (next_budget, next_capacity, next_reserve)
    return Step(
        next_state=next_state,
        welfare=tuple(welfare),
        total_utility=sum(welfare),
        cost=cost,
        reserve_target=reserve_target,
    )


def solve_exact(scenario: Scenario) -> tuple[np.ndarray, np.ndarray]:
    values = np.zeros((HORIZON + 1, *STATE_SHAPE), dtype=np.int32)
    q_values = np.full(
        (HORIZON, *STATE_SHAPE, ACTION_COUNT),
        FORBIDDEN_Q,
        dtype=np.int32,
    )
    for day in range(HORIZON - 1, -1, -1):
        for budget in range(BUDGET_MAX + 1):
            for capacity in range(CAPACITY_MAX + 1):
                for reserve in range(RESERVE_MAX + 1):
                    state = (budget, capacity, reserve)
                    for action in allowed_actions(state):
                        step = transition(scenario, day, state, action)
                        q_values[day, budget, capacity, reserve, action] = (
                            step.total_utility
                            + values[(day + 1, *step.next_state)]
                        )
                    values[day, budget, capacity, reserve] = np.max(
                        q_values[day, budget, capacity, reserve]
                    )
    return values, q_values


def build_scenario_features(scenario: Scenario) -> ScenarioFeatures:
    needs = np.asarray(scenario.needs, dtype=np.float64)
    populations = np.asarray(scenario.populations, dtype=np.float64)
    weighted = needs * populations

    def future_mean(window: int | None) -> np.ndarray:
        result = np.zeros_like(weighted)
        prefix = np.vstack([np.zeros((1, 4)), np.cumsum(weighted, axis=0)])
        for day in range(HORIZON):
            end = HORIZON if window is None else min(HORIZON, day + window)
            length = max(1, end - day)
            result[day] = (prefix[end] - prefix[day]) / length
        return result

    shock = np.asarray(
        [int(group >= 0) for group in scenario.shock_groups], dtype=np.float64
    )
    shock_next = np.zeros(HORIZON, dtype=np.float64)
    prefix_shock = np.concatenate([[0.0], np.cumsum(shock)])
    for day in range(HORIZON):
        end = min(HORIZON, day + 10)
        shock_next[day] = (prefix_shock[end] - prefix_shock[day]) / (end - day)
    return ScenarioFeatures(
        weighted_needs=weighted,
        future_5=future_mean(5),
        future_20=future_mean(20),
        future_remaining=future_mean(None),
        shock_next_10=shock_next,
    )


def _scaled(value: float, maximum: float) -> int:
    if maximum <= 0:
        raise ValueError("feature maximum must be positive")
    return round(FEATURE_SCALE * value / maximum)


def feature_vector(
    scenario: Scenario,
    context: ScenarioFeatures,
    day: int,
    state: State,
    action: int,
) -> np.ndarray:
    step = transition(scenario, day, state, action)
    budget, capacity, reserve = state
    next_budget, next_capacity, next_reserve = step.next_state
    needs = scenario.needs[day]
    weighted = context.weighted_needs[day]
    shock_now = int(scenario.shock_groups[day] >= 0)
    values = [
        FEATURE_SCALE,
        _scaled(day, HORIZON - 1),
        _scaled(HORIZON - day, HORIZON),
        _scaled(budget, BUDGET_MAX),
        _scaled(capacity, CAPACITY_MAX),
        _scaled(reserve, RESERVE_MAX),
        _scaled(step.total_utility, 220),
        _scaled(next_budget, BUDGET_MAX),
        _scaled(next_capacity, CAPACITY_MAX),
        _scaled(next_reserve, RESERVE_MAX),
    ]
    values.extend(_scaled(value, 9) for value in needs)
    values.extend(_scaled(float(value), 60) for value in weighted)
    values.extend(_scaled(float(value), 60) for value in context.future_5[day])
    values.extend(_scaled(float(value), 60) for value in context.future_20[day])
    values.extend(
        _scaled(float(value), 60) for value in context.future_remaining[day]
    )
    values.extend(
        (
            shock_now * FEATURE_SCALE,
            _scaled(float(context.shock_next_10[day]), 1),
            _scaled(capacity * (HORIZON - day), CAPACITY_MAX * HORIZON),
            _scaled(
                reserve * float(context.shock_next_10[day]), RESERVE_MAX
            ),
        )
    )
    if len(values) != FEATURE_COUNT:
        raise AssertionError("feature vector does not match declared schema")
    return np.asarray(values, dtype=np.int32)


def greedy_action_from_row(row: Sequence[int], allowed: Sequence[int]) -> int:
    return min(allowed, key=lambda action: (-int(row[action]), action))


def myopic_action(scenario: Scenario, day: int, state: State) -> int:
    allowed = allowed_actions(state)
    return min(
        allowed,
        key=lambda action: (
            -transition(scenario, day, state, action).total_utility,
            action,
        ),
    )


def sample_training_states(
    scenario: Scenario,
    q_values: np.ndarray,
    exploration_rollouts: int = 20,
) -> tuple[tuple[int, int, int, int], ...]:
    states: set[tuple[int, int, int, int]] = set()

    def run(policy: Callable[[int, State], int]) -> None:
        state: State = (6, 0, 0)
        for day in range(HORIZON):
            states.add((day, *state))
            action = policy(day, state)
            state = transition(scenario, day, state, action).next_state

    run(
        lambda day, state: greedy_action_from_row(
            q_values[(day, *state)], allowed_actions(state)
        )
    )
    run(lambda day, state: myopic_action(scenario, day, state))
    for rollout in range(exploration_rollouts):
        def exploratory(day: int, state: State, rollout_id: int = rollout) -> int:
            allowed = allowed_actions(state)
            if keyed_int(
                "expert-choice", scenario.seed, rollout_id, day, modulus=100
            ) < 35:
                return greedy_action_from_row(q_values[(day, *state)], allowed)
            return allowed[
                keyed_int(
                    "explore-choice",
                    scenario.seed,
                    rollout_id,
                    day,
                    modulus=len(allowed),
                )
            ]

        run(exploratory)

    for day in range(HORIZON):
        for sample in range(8):
            states.add(
                (
                    day,
                    keyed_int("grid-budget", scenario.seed, day, sample, modulus=9),
                    keyed_int("grid-capacity", scenario.seed, day, sample, modulus=6),
                    keyed_int("grid-reserve", scenario.seed, day, sample, modulus=5),
                )
            )
    return tuple(sorted(states))


def fresh_stats() -> dict[str, np.ndarray]:
    return {
        "xtx": np.zeros((ACTION_COUNT, FEATURE_COUNT, FEATURE_COUNT)),
        "xty": np.zeros((ACTION_COUNT, FEATURE_COUNT)),
        "counts": np.zeros(ACTION_COUNT, dtype=np.int64),
    }


def add_scenario_to_stats(
    stats: dict[str, np.ndarray],
    scenario: Scenario,
    q_values: np.ndarray,
) -> dict[str, int]:
    context = build_scenario_features(scenario)
    states = sample_training_states(scenario, q_values)
    rows: list[list[np.ndarray]] = [[] for _ in range(ACTION_COUNT)]
    targets: list[list[float]] = [[] for _ in range(ACTION_COUNT)]
    hard_negative_count = 0
    myopic_trap_count = 0
    for day, budget, capacity, reserve in states:
        state = (budget, capacity, reserve)
        allowed = allowed_actions(state)
        row = q_values[(day, *state)]
        best = max(int(row[action]) for action in allowed)
        exact_action = greedy_action_from_row(row, allowed)
        immediate_action = myopic_action(scenario, day, state)
        if immediate_action != exact_action:
            myopic_trap_count += 1
        for action in allowed:
            target = float(int(row[action]) - best)
            rows[action].append(feature_vector(scenario, context, day, state, action))
            targets[action].append(target)
            if action != exact_action and target >= -20:
                hard_negative_count += 1
    for action in range(ACTION_COUNT):
        if not rows[action]:
            continue
        x = np.asarray(rows[action], dtype=np.float64) / FEATURE_SCALE
        y = np.asarray(targets[action], dtype=np.float64)
        weights = np.where((y < 0) & (y >= -20), 2.0, 1.0)
        weighted_x = x * weights[:, None]
        stats["xtx"][action] += x.T @ weighted_x
        stats["xty"][action] += x.T @ (weights * y)
        stats["counts"][action] += len(y)
    return {
        "sampled_states": len(states),
        "state_action_examples": int(sum(len(items) for items in targets)),
        "hard_negative_examples": hard_negative_count,
        "myopic_trap_states": myopic_trap_count,
    }


def fit_model(
    stats: dict[str, np.ndarray], training_scenarios: int
) -> EnergyModel:
    weights = np.zeros((ACTION_COUNT, FEATURE_COUNT), dtype=np.float64)
    for action in range(ACTION_COUNT):
        regularizer = np.eye(FEATURE_COUNT) * RIDGE
        regularizer[0, 0] = RIDGE * 0.01
        weights[action] = np.linalg.solve(
            stats["xtx"][action] + regularizer,
            stats["xty"][action],
        )
    weights_q = np.rint(weights * WEIGHT_SCALE).astype(np.int64)
    payload = {
        "schema": MODEL_SCHEMA,
        "feature_scale": FEATURE_SCALE,
        "weight_scale": WEIGHT_SCALE,
        "feature_names": list(FEATURE_NAMES),
        "action_names": list(ACTION_NAMES),
        "weights_q": weights_q.tolist(),
        "training_scenarios": training_scenarios,
        "training_examples": int(np.sum(stats["counts"])),
    }
    return EnergyModel(
        weights_q=weights_q,
        training_scenarios=training_scenarios,
        training_examples=int(np.sum(stats["counts"])),
        model_sha256=sha256_bytes(canonical_json_bytes(payload)),
    )


def model_payload(model: EnergyModel) -> dict[str, Any]:
    return {
        "schema": MODEL_SCHEMA,
        "energy_definition": "negative_quantized_predicted_q_advantage",
        "feature_scale": FEATURE_SCALE,
        "weight_scale": WEIGHT_SCALE,
        "score_scale": "milli-person-welfare-units",
        "feature_names": list(FEATURE_NAMES),
        "action_names": list(ACTION_NAMES),
        "weights_q": model.weights_q.tolist(),
        "training_scenarios": model.training_scenarios,
        "training_examples": model.training_examples,
        "sha256": model.model_sha256,
    }


def predicted_score_milli(
    model: EnergyModel,
    scenario: Scenario,
    context: ScenarioFeatures,
    day: int,
    state: State,
    action: int,
    *,
    weight_action: int | None = None,
) -> int:
    features = feature_vector(scenario, context, day, state, action)
    selected_weights = action if weight_action is None else weight_action
    raw = int(
        np.dot(model.weights_q[selected_weights], features.astype(np.int64))
    )
    return round(raw / WEIGHT_SCALE)


def model_action(
    model: EnergyModel,
    scenario: Scenario,
    context: ScenarioFeatures,
    day: int,
    state: State,
) -> int:
    allowed = allowed_actions(state)
    return min(
        allowed,
        key=lambda action: (
            -predicted_score_milli(
                model, scenario, context, day, state, action
            ),
            action,
        ),
    )


def rollout(
    scenario: Scenario,
    policy: Callable[[int, State], int],
    *,
    include_trace: bool = False,
    model: EnergyModel | None = None,
    exact_q: np.ndarray | None = None,
) -> dict[str, Any]:
    state: State = (6, 0, 0)
    group_totals = [0, 0, 0, 0]
    total = 0
    forbidden = 0
    exact_matches = 0
    rows: list[dict[str, Any]] = []
    context = build_scenario_features(scenario) if model is not None else None
    for day in range(HORIZON):
        allowed = allowed_actions(state)
        action = policy(day, state)
        if action not in allowed:
            forbidden += 1
            action = HOLD
        step = transition(scenario, day, state, action)
        if exact_q is not None:
            exact = greedy_action_from_row(exact_q[(day, *state)], allowed)
            exact_matches += int(action == exact)
        for group, value in enumerate(step.welfare):
            group_totals[group] += value
        total += step.total_utility
        if include_trace:
            action_scores = None
            if model is not None and context is not None:
                action_scores = [
                    {
                        "action": ACTION_NAMES[candidate],
                        "score_milli": predicted_score_milli(
                            model, scenario, context, day, state, candidate
                        ),
                        "energy_milli": -predicted_score_milli(
                            model, scenario, context, day, state, candidate
                        ),
                        "immediate_utility": transition(
                            scenario, day, state, candidate
                        ).total_utility,
                    }
                    for candidate in allowed
                ]
            rows.append(
                {
                    "step": day + 1,
                    "day": day,
                    "state": {
                        "budget": state[0],
                        "preventive_capacity": state[1],
                        "reserve": state[2],
                    },
                    "needs": dict(zip(COMMUNITIES, scenario.needs[day], strict=True)),
                    "shock_community": (
                        COMMUNITIES[scenario.shock_groups[day]]
                        if scenario.shock_groups[day] >= 0
                        else None
                    ),
                    "allowed_actions": [ACTION_NAMES[item] for item in allowed],
                    "action_scores": action_scores,
                    "selected_action": ACTION_NAMES[action],
                    "selected_action_id": action,
                    "cost": step.cost,
                    "welfare": dict(zip(COMMUNITIES, step.welfare, strict=True)),
                    "step_total_utility": step.total_utility,
                    "cumulative_total_utility": total,
                    "next_state": {
                        "budget": step.next_state[0],
                        "preventive_capacity": step.next_state[1],
                        "reserve": step.next_state[2],
                    },
                    "reserve_target": (
                        COMMUNITIES[step.reserve_target]
                        if step.reserve_target is not None
                        else None
                    ),
                }
            )
        state = step.next_state
    return {
        "steps": HORIZON,
        "total_utility": total,
        "community_utility": dict(zip(COMMUNITIES, group_totals, strict=True)),
        "forbidden_selections": forbidden,
        "exact_action_agreement": (
            exact_matches / HORIZON if exact_q is not None else None
        ),
        "trace": rows if include_trace else None,
    }


def evaluate_model(
    model: EnergyModel,
    cases: Sequence[EvaluationCase],
    *,
    permute_actions: bool = False,
) -> dict[str, Any]:
    learned_totals: list[int] = []
    exact_totals: list[int] = []
    myopic_totals: list[int] = []
    agreements: list[float] = []
    forbidden = 0
    for case in cases:
        scenario = case.scenario
        exact_q = case.exact_q
        context = case.context

        def learned_policy(
            day: int,
            state: State,
            *,
            selected_scenario: Scenario = scenario,
            selected_context: ScenarioFeatures = context,
        ) -> int:
            allowed = allowed_actions(state)
            scores = {
                action: predicted_score_milli(
                    model,
                    selected_scenario,
                    selected_context,
                    day,
                    state,
                    action,
                    weight_action=(action + 1) % ACTION_COUNT
                    if permute_actions
                    else action,
                )
                for action in allowed
            }
            return min(allowed, key=lambda action: (-scores[action], action))

        learned = rollout(scenario, learned_policy, exact_q=exact_q)
        learned_totals.append(int(learned["total_utility"]))
        exact_totals.append(case.exact_total)
        myopic_totals.append(case.myopic_total)
        agreements.append(float(learned["exact_action_agreement"]))
        forbidden += int(learned["forbidden_selections"])
    ratios = [
        learned / exact if exact else 1.0
        for learned, exact in zip(learned_totals, exact_totals, strict=True)
    ]
    improvements = [
        learned - myopic
        for learned, myopic in zip(learned_totals, myopic_totals, strict=True)
    ]
    return {
        "scenario_count": len(cases),
        "mean_total_utility": float(np.mean(learned_totals)),
        "minimum_total_utility": min(learned_totals),
        "mean_exact_utility": float(np.mean(exact_totals)),
        "mean_myopic_utility": float(np.mean(myopic_totals)),
        "mean_optimal_utility_ratio": float(np.mean(ratios)),
        "minimum_optimal_utility_ratio": min(ratios),
        "mean_gain_over_myopic": float(np.mean(improvements)),
        "scenarios_beating_myopic": sum(value > 0 for value in improvements),
        "mean_exact_action_agreement": float(np.mean(agreements)),
        "forbidden_selections": forbidden,
        "all_episodes_100_steps": True,
    }


def prepare_evaluation_cases(seeds: Sequence[int]) -> list[EvaluationCase]:
    cases = []
    for seed in seeds:
        scenario = make_scenario(seed)
        _, exact_q = solve_exact(scenario)
        exact = rollout(
            scenario,
            lambda day, state, selected_q=exact_q: greedy_action_from_row(
                selected_q[(day, *state)], allowed_actions(state)
            ),
        )
        myopic = rollout(
            scenario,
            lambda day, state, selected_scenario=scenario: myopic_action(
                selected_scenario, day, state
            ),
        )
        cases.append(
            EvaluationCase(
                scenario=scenario,
                exact_q=exact_q,
                context=build_scenario_features(scenario),
                exact_total=int(exact["total_utility"]),
                myopic_total=int(myopic["total_utility"]),
            )
        )
    return cases


def compile_table(model: EnergyModel, scenario: Scenario) -> np.ndarray:
    context = build_scenario_features(scenario)
    table = np.full(
        (HORIZON, *STATE_SHAPE, ACTION_COUNT),
        FORBIDDEN_Q,
        dtype=np.dtype("<i4"),
    )
    for day in range(HORIZON):
        for budget in range(BUDGET_MAX + 1):
            for capacity in range(CAPACITY_MAX + 1):
                for reserve in range(RESERVE_MAX + 1):
                    state = (budget, capacity, reserve)
                    for action in allowed_actions(state):
                        table[(day, *state, action)] = predicted_score_milli(
                            model, scenario, context, day, state, action
                        )
    return table


def tau_expected(step: dict[str, int]) -> dict[str, int]:
    action_accept = int(all(step[f"i{index}"] == 1 for index in range(1, 10)))
    plan_accept = int(action_accept == 1 and step["i10"] == 1)
    selected = action_accept if step["i11"] == 0 else plan_accept
    return {"o1": action_accept, "o2": plan_accept, "o3": selected}


def tau_cases() -> list[dict[str, Any]]:
    base_action = {f"i{index}": 1 for index in range(1, 11)}
    base_action["i10"] = 0
    base_action["i11"] = 0
    cases: list[dict[str, Any]] = []
    for step in range(HORIZON):
        cases.append(
            {
                "name": f"accept_verified_action_{step + 1:03d}",
                "step": dict(base_action),
                "expected_accept": 1,
            }
        )
    complete = {f"i{index}": 1 for index in range(1, 12)}
    cases.append(
        {
            "name": "accept_complete_100_step_plan",
            "step": complete,
            "expected_accept": 1,
        }
    )
    mutant_names = {
        "i1": "malformed_receipt",
        "i2": "unbound_world",
        "i3": "incorrect_utility_sum",
        "i4": "nonminimal_energy",
        "i5": "nonmaximal_q_score",
        "i6": "inadmissible_action",
        "i7": "stale_table_root",
        "i8": "stale_model_root",
        "i9": "stale_sequence",
    }
    for flag, name in mutant_names.items():
        mutant = dict(base_action)
        mutant[flag] = 0
        cases.append(
            {
                "name": f"deny_{name}",
                "step": mutant,
                "expected_accept": 0,
            }
        )
    incomplete = dict(complete)
    incomplete["i10"] = 0
    cases.append(
        {
            "name": "deny_incomplete_plan",
            "step": incomplete,
            "expected_accept": 0,
        }
    )
    return cases


def run_tau_gate(cases: list[dict[str, Any]]) -> dict[str, Any]:
    if str(ROOT / "scripts") not in sys.path:
        sys.path.insert(0, str(ROOT / "scripts"))
    from tau_local_bridge import find_tau_bin, run_tau_spec_steps_spec_mode_with_trace

    tau_bin = find_tau_bin()
    if not tau_bin:
        return {"status": "unavailable", "reason": "Tau binary not found"}
    outputs, stdout, stderr, normalized_spec, input_text = (
        run_tau_spec_steps_spec_mode_with_trace(
            tau_bin=tau_bin,
            spec_path=TAU_POLICY,
            steps=[case["step"] for case in cases],
            timeout_s=30.0,
            severity="error",
        )
    )
    rows = []
    mismatches = []
    for index, case in enumerate(cases):
        actual = {key: int(value) for key, value in outputs[index].items()}
        expected = tau_expected(case["step"])
        matched = actual == expected and actual["o3"] == case["expected_accept"]
        row = {
            "name": case["name"],
            "inputs": case["step"],
            "expected": expected,
            "actual": actual,
            "matched": matched,
        }
        rows.append(row)
        if not matched:
            mismatches.append(row)
    return {
        "status": "passed" if not mismatches else "failed",
        "tau_binary": Path(tau_bin).name,
        "policy_sha256": sha256_file(TAU_POLICY),
        "case_count": len(rows),
        "accepted_case_count": sum(row["actual"]["o3"] for row in rows),
        "denied_case_count": sum(1 - row["actual"]["o3"] for row in rows),
        "mismatch_count": len(mismatches),
        "trace_sha256": sha256_bytes(
            (normalized_spec + input_text + stdout + stderr).encode("utf-8")
        ),
        "cases": rows,
    }


def train_models() -> tuple[dict[int, EnergyModel], dict[str, Any]]:
    stats = fresh_stats()
    models: dict[int, EnergyModel] = {}
    totals = {
        "sampled_states": 0,
        "state_action_examples": 0,
        "hard_negative_examples": 0,
        "myopic_trap_states": 0,
    }
    per_scenario = []
    for index, seed in enumerate(TRAIN_SEEDS, start=1):
        scenario = make_scenario(seed)
        _, exact_q = solve_exact(scenario)
        counts = add_scenario_to_stats(stats, scenario, exact_q)
        per_scenario.append({"seed": seed, **counts})
        for key in totals:
            totals[key] += counts[key]
        if index in TRAINING_BUDGETS:
            models[index] = fit_model(stats, index)
    return models, {
        "training_seed_sha256": sha256_bytes(canonical_json_bytes(TRAIN_SEEDS)),
        "training_budgets": list(TRAINING_BUDGETS),
        "totals": totals,
        "per_scenario": per_scenario,
    }


def build_report(
    *,
    run_tau: bool,
) -> tuple[bytes, dict[str, Any], dict[str, Any]]:
    models, training = train_models()
    validation_cases = prepare_evaluation_cases(VALIDATION_SEEDS)
    validation = {
        str(budget): evaluate_model(model, validation_cases)
        for budget, model in models.items()
    }
    selected_budget = max(
        TRAINING_BUDGETS,
        key=lambda budget: (
            validation[str(budget)]["mean_optimal_utility_ratio"],
            -budget,
        ),
    )
    full_model = models[selected_budget]
    test_cases = prepare_evaluation_cases(TEST_SEEDS)
    test = evaluate_model(full_model, test_cases)
    permuted = evaluate_model(full_model, test_cases, permute_actions=True)
    public_scenario = make_scenario(
        PUBLIC_SCENARIO_SEED,
        populations=(4, 4, 4, 4),
    )
    _, public_exact_q = solve_exact(public_scenario)
    public_context = build_scenario_features(public_scenario)
    learned = rollout(
        public_scenario,
        lambda day, state: model_action(
            full_model, public_scenario, public_context, day, state
        ),
        include_trace=True,
        model=full_model,
        exact_q=public_exact_q,
    )
    exact = rollout(
        public_scenario,
        lambda day, state: greedy_action_from_row(
            public_exact_q[(day, *state)], allowed_actions(state)
        ),
    )
    myopic = rollout(
        public_scenario,
        lambda day, state: myopic_action(public_scenario, day, state),
    )
    table = compile_table(full_model, public_scenario)
    table_bytes = table.tobytes(order="C")
    duplicate_table = compile_table(full_model, public_scenario).tobytes(order="C")
    table_sha = sha256_bytes(table_bytes)
    cases = tau_cases()
    tau_result = (
        run_tau_gate(cases)
        if run_tau
        else {"status": "skipped", "reason": "--skip-tau was supplied"}
    )

    scaling_values = [validation[str(value)]["mean_optimal_utility_ratio"] for value in TRAINING_BUDGETS]
    knowledge_scaling = (
        scaling_values[-1] > scaling_values[0] + 0.01
        and validation[str(selected_budget)]["mean_gain_over_myopic"] > 0
    )
    performance_gate = (
        test["mean_optimal_utility_ratio"] >= 0.97
        and test["minimum_optimal_utility_ratio"] >= 0.93
        and test["mean_gain_over_myopic"] > 0
        and test["scenarios_beating_myopic"] >= math.ceil(0.8 * len(TEST_SEEDS))
        and test["forbidden_selections"] == 0
        and test["mean_optimal_utility_ratio"]
        > permuted["mean_optimal_utility_ratio"] + 0.02
    )
    tau_gate = tau_result.get("status") == "passed"
    artifact_gate = table_bytes == duplicate_table and len(table_bytes) < 2_000_000
    accepted = knowledge_scaling and performance_gate and tau_gate and artifact_gate

    model = model_payload(full_model)
    report = {
        "schema": SCHEMA,
        "classification": "bounded synthetic total-utilitarian policy-distillation benchmark",
        "normative_profile": {
            "id": "equal-person-total-utilitarian-100-v1",
            "objective": "maximize the undiscounted sum of declared synthetic person-welfare increments over 100 steps",
            "formula": "U(trace) = sum_t sum_group synthetic_person_welfare_delta(t, group)",
            "person_weight": "one equal unit per represented person",
            "discount": 1,
            "horizon": HORIZON,
            "authority": "Tau accepts only receipts satisfying the declared policy; the learned energy is advisory",
        },
        "world": {
            "communities": list(COMMUNITIES),
            "actions": list(ACTION_NAMES),
            "state_shape": list(STATE_SHAPE),
            "state_count_per_day": int(np.prod(STATE_SHAPE)),
            "horizon": HORIZON,
            "reward_source": "deterministic synthetic consequence function",
        },
        "model": model,
        "training": training,
        "split": {
            "training_scenarios": len(TRAIN_SEEDS),
            "validation_scenarios": len(VALIDATION_SEEDS),
            "test_scenarios": len(TEST_SEEDS),
            "seed_sets_disjoint": not (
                set(TRAIN_SEEDS) & set(VALIDATION_SEEDS)
                or set(TRAIN_SEEDS) & set(TEST_SEEDS)
                or set(VALIDATION_SEEDS) & set(TEST_SEEDS)
            ),
            "validation_seed_sha256": sha256_bytes(
                canonical_json_bytes(VALIDATION_SEEDS)
            ),
            "test_seed_sha256": sha256_bytes(canonical_json_bytes(TEST_SEEDS)),
        },
        "benchmark": {
            "validation_scaling": validation,
            "validation_selected_training_scenarios": selected_budget,
            "selection_rule": "highest validation mean optimal-utility ratio, then smallest model on ties",
            "held_out_test": test,
            "action_permuted_control": permuted,
        },
        "public_scenario": {
            "profile": "equal population units for an interpretable public replay; held-out tests retain varied populations",
            "manifest": scenario_manifest(public_scenario),
            "learned": learned,
            "exact": exact,
            "myopic": myopic,
            "gain_over_myopic": learned["total_utility"] - myopic["total_utility"],
            "regret_to_exact": exact["total_utility"] - learned["total_utility"],
        },
        "compiled_q_table": {
            "schema": TABLE_SCHEMA,
            "shape": list(table.shape),
            "dtype": "<i4",
            "bytes": len(table_bytes),
            "sha256": table_sha,
            "forbidden_sentinel": int(FORBIDDEN_Q),
            "score_unit": "milli-person-welfare predicted advantage",
            "energy_relation": "energy = -compiled_q_score",
            "deterministic_duplicate": table_bytes == duplicate_table,
        },
        "tau_policy": {
            "role": "fail-closed composition of deterministic utilitarian, ranking, admissibility, sequence, and commitment receipts",
            "receipt_semantics": {
                "i1": "action and receipt shape well formed",
                "i2": "state and consequence vector bound to the declared world",
                "i3": "total utility equals the sum of declared person-welfare changes",
                "i4": "selected energy no greater than every admitted alternative",
                "i5": "selected compiled Q score no less than every admitted alternative",
                "i6": "selected action admitted by the resource mask",
                "i7": "compiled Q-table root current",
                "i8": "energy-model root current",
                "i9": "step and sequence current",
                "i10": "complete 100-step rollout receipt valid",
                "i11": "mode, zero for one action and one for complete plan",
            },
            "run": tau_result,
        },
        "license_boundary": {
            "tau_framework_bundled": False,
            "tau_binary_bundled": False,
            "tau_source_or_library_bundled": False,
            "independently_authored_loopback_launcher_bundled": True,
            "launcher_downloads_or_installs_tau": False,
            "independently_authored_policy_included": True,
            "official_license_url": "https://github.com/IDNI/tau-lang/blob/main/LICENSE.md",
            "official_repository": "https://github.com/IDNI/tau-lang",
            "reviewed_upstream_head": "7cbec4f7d04fa6952c2f507c2aa988d776ac47ad",
            "reviewed_date": "2026-08-05",
            "notice": "Tau must be obtained separately from IDNI AG and used under its current terms. This report is not legal advice.",
        },
        "acceptance": {
            "knowledge_scaling_gate_passed": knowledge_scaling,
            "held_out_performance_gate_passed": performance_gate,
            "tau_mutation_gate_passed": tau_gate,
            "artifact_gate_passed": artifact_gate,
            "demo_accepted": accepted,
        },
        "assumptions": [
            "Synthetic person-welfare increments are treated as cardinal and interpersonally comparable inside this model.",
            "Every represented person receives equal weight in the declared sum.",
            "The deterministic transition function is treated as the complete world for this benchmark.",
            "Training and test scenario generators are assumed to represent the same bounded family.",
        ],
        "nonclaims": [
            "The benchmark does not establish that its synthetic numbers measure real welfare.",
            "The benchmark does not establish that total utilitarianism is correct, complete, fair, or safe for real governance.",
            "The energy model does not authorize actions and does not prove global optimality.",
            "The Tau policy checks supplied receipts; it does not prove the external world model true.",
            "No comparison with human participants was performed.",
            "No Tau Net deployment or external effect was performed.",
        ],
        "provenance": {
            "generator_sha256": sha256_file(Path(__file__)),
            "tau_policy_sha256": sha256_file(TAU_POLICY),
        },
    }
    return table_bytes, model, report


def write_bundle(
    *,
    bundle_path: Path,
    table_path: Path,
    model_path: Path,
    report_path: Path,
    notice_path: Path,
) -> None:
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    entries = (
        (table_path, f"assets/data/{table_path.name}", 0o100644),
        (model_path, f"assets/data/{model_path.name}", 0o100644),
        (report_path, f"assets/data/{report_path.name}", 0o100644),
        (LAB_PAGE, LAB_PAGE.name, 0o100644),
        (LAB_STYLESHEET, "assets/css/qgent-lab.css", 0o100644),
        (
            TAU_POLICY,
            "experiments/qgent_utilitarian_energy_v001/utilitarian_policy_v1.tau",
            0o100644,
        ),
        (
            notice_path,
            "experiments/qgent_utilitarian_energy_v001/TAU_DISTRIBUTION_NOTICE.md",
            0o100644,
        ),
        (
            LOCAL_LAUNCH_GUIDE,
            "LOCAL_LAUNCH.md",
            0o100644,
        ),
        (
            Path(__file__),
            "experiments/qgent_utilitarian_energy_v001/utilitarian_energy_lab.py",
            0o100644,
        ),
        (TAU_BRIDGE, "scripts/tau_local_bridge.py", 0o100755),
        (
            LAB_LAUNCHER,
            "scripts/launch_qgent_utilitarian_lab.py",
            0o100755,
        ),
    )
    with zipfile.ZipFile(
        bundle_path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for path, archive_name, mode in entries:
            info = zipfile.ZipInfo(archive_name)
            info.date_time = (2026, 8, 5, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = mode << 16
            archive.writestr(info, path.read_bytes())


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--table-out",
        type=Path,
        default=Path("assets/data/qgent_utilitarian_energy_100_v1.qtable"),
    )
    parser.add_argument(
        "--model-out",
        type=Path,
        default=Path("assets/data/qgent_utilitarian_energy_100_v1.model.json"),
    )
    parser.add_argument(
        "--report-out",
        type=Path,
        default=Path("assets/data/qgent_utilitarian_energy_100_v1.report.json"),
    )
    parser.add_argument(
        "--bundle-out",
        type=Path,
        default=Path("assets/downloads/qgent-utilitarian-energy-100-v1.zip"),
    )
    parser.add_argument(
        "--notice",
        type=Path,
        default=Path(
            "experiments/qgent_utilitarian_energy_v001/TAU_DISTRIBUTION_NOTICE.md"
        ),
    )
    parser.add_argument("--skip-tau", action="store_true")
    args = parser.parse_args(argv)

    table, model, report = build_report(run_tau=not args.skip_tau)
    for path in (args.table_out, args.model_out, args.report_out):
        path.parent.mkdir(parents=True, exist_ok=True)
    args.table_out.write_bytes(table)
    args.model_out.write_bytes(canonical_json_bytes(model))
    args.report_out.write_bytes(canonical_json_bytes(report))
    write_bundle(
        bundle_path=args.bundle_out,
        table_path=args.table_out,
        model_path=args.model_out,
        report_path=args.report_out,
        notice_path=args.notice,
    )
    summary = {
        "accepted": report["acceptance"]["demo_accepted"],
        "test_optimal_ratio": report["benchmark"]["held_out_test"][
            "mean_optimal_utility_ratio"
        ],
        "test_gain_over_myopic": report["benchmark"]["held_out_test"][
            "mean_gain_over_myopic"
        ],
        "public_utility": report["public_scenario"]["learned"]["total_utility"],
        "public_steps": report["public_scenario"]["learned"]["steps"],
        "tau_status": report["tau_policy"]["run"]["status"],
        "table_sha256": report["compiled_q_table"]["sha256"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if report["acceptance"]["demo_accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
