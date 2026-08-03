#!/usr/bin/env python3
"""Build and inspect GlassMind-256 layered Q-tables.

GlassMind is a deliberately bounded deterministic planner.  Layer h stores the
finite-horizon action-value function Q_h for a synthetic emergency-routing
grid.  Every value is produced by backward dynamic programming from a frozen
transition and reward model.

The engineering nickname "deterministic thinker" refers only to this checked
finite planning behavior.  The artifact is not evidence of general
intelligence or of performance in an unmodelled real environment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np


GENERATOR_VERSION = "glassmind-256-v3"
CANONICALIZER_VERSION = "glassmind-canonicalizer-v1"
CHALLENGE_CORPUS_VERSION = "glassmind-challenge-corpus-v1"
ACTIONS = ("north", "east", "south", "west")
DEFAULT_SCENARIO_PACK = Path(__file__).with_name("glassmind_scenario_pack.json")


@dataclass(frozen=True)
class Config:
    """Frozen definition of one GlassMind planning problem."""

    layers: int
    width: int
    height: int
    actions: int = 4
    gamma: float = 0.99
    seed: int = 20260801
    goal_reward: float = 1000.0
    boundary_penalty: float = 25.0
    goal_spacing_x: int = 256
    goal_spacing_y: int = 128

    @property
    def states(self) -> int:
        return self.width * self.height

    @property
    def values(self) -> int:
        return self.layers * self.states * self.actions

    @property
    def data_bytes(self) -> int:
        return self.values * np.dtype("<f4").itemsize

    def validate(self) -> None:
        if self.layers <= 0 or self.width <= 0 or self.height <= 0:
            raise ValueError("layers, width, and height must be positive")
        if self.actions != len(ACTIONS):
            raise ValueError("GlassMind v1 has exactly four cardinal actions")
        if not 0.0 <= self.gamma < 1.0:
            raise ValueError("gamma must satisfy 0 <= gamma < 1")
        if self.goal_spacing_x <= 0 or self.goal_spacing_y <= 0:
            raise ValueError("goal spacing must be positive")


PROFILES: dict[str, Config] = {
    # 256 * 12,288 * 4 * 4 = 50,331,648 bytes (48 MiB) of float32 data.
    "public": Config(layers=256, width=128, height=96),
    # 256 * 131,072 * 4 * 4 = 536,870,912 bytes (512 MiB) of float32 data.
    "full": Config(layers=256, width=512, height=256),
}


@dataclass(frozen=True)
class Environment:
    risk: np.ndarray
    goals: np.ndarray
    next_states: np.ndarray
    rewards: np.ndarray
    next_is_goal: np.ndarray


def canonicalize_proposals(
    config: Config, scenario_pack: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Canonicalize untrusted proposal records without executing generated code.

    Coordinates are the only accepted state representation.  Duplicate state
    proposals collapse to row-major keys, actions use the frozen ACTIONS order,
    and malformed or out-of-bounds trajectory references are quarantined in the
    evidence report.  The bounded counts make this stage suitable for replay.
    """

    config.validate()
    raw_states = scenario_pack.get("proposed_states", [])
    raw_actions = scenario_pack.get("proposed_actions", list(ACTIONS))
    raw_trajectories = scenario_pack.get("proposed_trajectories", [])
    if not isinstance(raw_states, list) or not isinstance(raw_actions, list):
        raise ValueError("proposal state and action collections must be lists")
    if not isinstance(raw_trajectories, list):
        raise ValueError("proposal trajectories must be a list")
    max_proposals = 4096
    if len(raw_states) > max_proposals or len(raw_actions) > max_proposals:
        raise ValueError("proposal collection exceeds the bounded canonicalizer")

    quarantined = 0
    state_ids: set[int] = set()
    valid_state_proposals = 0
    for proposal in raw_states:
        if not isinstance(proposal, dict):
            quarantined += 1
            continue
        x, y = proposal.get("x"), proposal.get("y")
        if (
            not isinstance(x, int)
            or isinstance(x, bool)
            or not isinstance(y, int)
            or isinstance(y, bool)
            or not (0 <= x < config.width)
            or not (0 <= y < config.height)
        ):
            quarantined += 1
            continue
        valid_state_proposals += 1
        state_ids.add(y * config.width + x)

    canonical_states = [
        {"key": f"s{state:06d}", "state": state,
         "coordinate": [state % config.width, state // config.width]}
        for state in sorted(state_ids)
    ]
    valid_actions = [action for action in raw_actions if action in ACTIONS]
    proposed_actions = sorted(
        set(valid_actions),
        key=ACTIONS.index,
    )
    invalid_actions = sum(action not in ACTIONS for action in raw_actions)

    canonical_trajectories: list[list[str]] = []
    for trajectory in raw_trajectories[:max_proposals]:
        if not isinstance(trajectory, list) or len(trajectory) > 256:
            quarantined += 1
            continue
        keys: list[str] = []
        valid = True
        for state in trajectory:
            if not isinstance(state, int) or isinstance(state, bool) or not 0 <= state < config.states:
                valid = False
                break
            keys.append(f"s{state:06d}")
        if valid:
            canonical_trajectories.append(keys)
        else:
            quarantined += 1

    canonical = dict(scenario_pack)
    canonical["accepted_motifs"] = sorted(
        scenario_pack["accepted_motifs"], key=lambda motif: motif["id"]
    )
    evidence = {
        "version": CANONICALIZER_VERSION,
        "input_state_proposals": len(raw_states),
        "canonical_state_count": len(canonical_states),
        "duplicate_state_proposals": valid_state_proposals - len(state_ids),
        "quarantined_state_or_trajectory_proposals": quarantined,
        "canonical_states": canonical_states,
        "canonical_actions": proposed_actions,
        "invalid_action_proposals": invalid_actions,
        "canonical_trajectories": canonical_trajectories,
        "trajectory_count": len(canonical_trajectories),
    }
    canonical["canonicalization"] = evidence
    return canonical, evidence


def load_scenario_pack(path: Path = DEFAULT_SCENARIO_PACK) -> dict[str, Any]:
    """Load and strictly validate the bounded LLM proposal language."""

    pack = json.loads(path.read_text(encoding="utf-8"))
    if pack.get("schema") != "glassmind-llm-scenario-pack-v1":
        raise ValueError("unsupported scenario-pack schema")
    motifs = pack.get("accepted_motifs")
    if not isinstance(motifs, list) or not motifs:
        raise ValueError("scenario pack must contain accepted_motifs")
    identifiers = [motif.get("id") for motif in motifs]
    if any(not isinstance(identifier, str) or not identifier for identifier in identifiers):
        raise ValueError("every accepted motif needs a non-empty string id")
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("accepted motif ids must be unique")
    if not isinstance(pack.get("quarantined_proposals"), list):
        raise ValueError("scenario pack must preserve quarantined proposals")
    challenge_grammar = pack.get("challenge_grammar", [])
    if not isinstance(challenge_grammar, list) or not challenge_grammar:
        raise ValueError("scenario pack must contain challenge_grammar")
    challenge_ids = [challenge.get("id") for challenge in challenge_grammar if isinstance(challenge, dict)]
    if len(challenge_ids) != len(set(challenge_ids)):
        raise ValueError("challenge grammar ids must be unique")
    for challenge in challenge_grammar:
        if not isinstance(challenge, dict) or not isinstance(challenge.get("id"), str):
            raise ValueError("every challenge grammar entry needs a string id")
        if challenge.get("stratum") not in {
            "boundary", "rare_risk", "goal_distance", "motif_intersection",
            "horizon_sensitive",
        }:
            raise ValueError(f"unsupported challenge stratum {challenge.get('stratum')!r}")
        if not isinstance(challenge.get("count"), int) or not 1 <= challenge["count"] <= 512:
            raise ValueError("challenge count must be between 1 and 512")

    for motif in motifs:
        motif_type = motif.get("type")
        parameters = motif.get("parameters")
        risk_delta = motif.get("risk_delta")
        if motif_type not in {"linear_band", "checker_patch", "axis_corridor"}:
            raise ValueError(f"unsupported motif type {motif_type!r}")
        if not isinstance(parameters, dict):
            raise ValueError(f"motif {motif['id']} parameters must be an object")
        if not isinstance(risk_delta, int) or not -15 <= risk_delta <= 15:
            raise ValueError(f"motif {motif['id']} has an invalid risk_delta")

        if motif_type == "linear_band":
            required = {"x_weight", "y_weight", "phase", "modulus", "width"}
            if set(parameters) != required:
                raise ValueError(f"motif {motif['id']} has invalid linear_band fields")
            if not 2 <= parameters["modulus"] <= 4096:
                raise ValueError("linear-band modulus is outside the bounded schema")
            if not 1 <= parameters["width"] < parameters["modulus"]:
                raise ValueError("linear-band width must be inside its modulus")
        elif motif_type == "checker_patch":
            required = {"cell_width", "cell_height", "period", "phase"}
            if set(parameters) != required:
                raise ValueError(f"motif {motif['id']} has invalid checker fields")
            if not 1 <= parameters["cell_width"] <= 1024:
                raise ValueError("checker cell_width is outside the bounded schema")
            if not 1 <= parameters["cell_height"] <= 1024:
                raise ValueError("checker cell_height is outside the bounded schema")
            if not 2 <= parameters["period"] <= 4096:
                raise ValueError("checker period is outside the bounded schema")
        else:
            required = {"axis", "spacing", "width", "offset"}
            if set(parameters) != required:
                raise ValueError(f"motif {motif['id']} has invalid corridor fields")
            if parameters["axis"] not in {"x", "y"}:
                raise ValueError("corridor axis must be x or y")
            if not 1 <= parameters["spacing"] <= 4096:
                raise ValueError("corridor spacing is outside the bounded schema")
            if not 1 <= parameters["width"] <= parameters["spacing"]:
                raise ValueError("corridor width is outside its spacing")
    return pack


def scenario_pack_sha256(pack: dict[str, Any]) -> str:
    canonical = json.dumps(pack, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _motif_mask(
    x: np.ndarray, y: np.ndarray, motif: dict[str, Any]
) -> np.ndarray:
    parameters = motif["parameters"]
    if motif["type"] == "linear_band":
        phase = (
            parameters["x_weight"] * x
            + parameters["y_weight"] * y
            + parameters["phase"]
        ) % parameters["modulus"]
        return phase < parameters["width"]
    if motif["type"] == "checker_patch":
        cell_x = x // parameters["cell_width"]
        cell_y = y // parameters["cell_height"]
        return (cell_x + cell_y + parameters["phase"]) % parameters["period"] == 0
    coordinate = x if parameters["axis"] == "x" else y
    return ((coordinate - parameters["offset"]) % parameters["spacing"]) < parameters["width"]


def motif_activity_report(
    config: Config, scenario_pack: dict[str, Any], base_risk: np.ndarray | None = None
) -> list[dict[str, Any]]:
    """Measure each accepted motif and fail closed on inert proposals."""

    states = np.arange(config.states, dtype=np.int64)
    x, y = states % config.width, states // config.width
    if base_risk is None:
        keyed = states.astype(np.uint64) ^ np.uint64(config.seed) ^ np.uint64(0x9E3779B97F4A7C15)
        base_risk = (_mix64(keyed) & np.uint64(3)).astype(np.int16)
    report = []
    motifs = sorted(scenario_pack["accepted_motifs"], key=lambda item: item["id"])
    for index, motif in enumerate(motifs):
        mask = _motif_mask(x, y, motif)
        with_motif = _risk_from_scenario(x, y, base_risk, {"accepted_motifs": motifs})
        without = _risk_from_scenario(
            x, y, base_risk, {"accepted_motifs": motifs[:index] + motifs[index + 1:]}
        )
        active_count = int(np.count_nonzero(mask))
        influence_count = int(np.count_nonzero(with_motif != without))
        if active_count == 0 or influence_count == 0:
            raise ValueError(f"accepted motif {motif['id']} is inert on this grid")
        report.append({
            "id": motif["id"],
            "active_cell_count": active_count,
            "ablation_changed_cell_count": influence_count,
            "risk_delta": motif["risk_delta"],
        })
    return report


def _risk_from_scenario(
    x: np.ndarray,
    y: np.ndarray,
    base_risk: np.ndarray,
    scenario_pack: dict[str, Any],
) -> np.ndarray:
    """Expand the finite proposal DSL without executing generated code."""

    risk = base_risk.astype(np.int16, copy=True)
    for motif in sorted(scenario_pack["accepted_motifs"], key=lambda item: item["id"]):
        active = _motif_mask(x, y, motif)
        risk += active.astype(np.int16) * np.int16(motif["risk_delta"])
    return np.clip(risk, 0, 15).astype(np.int16)


def _mix64(values: np.ndarray) -> np.ndarray:
    """Vectorized SplitMix64 finalizer with intentional modulo-2^64 math."""

    z = np.asarray(values, dtype=np.uint64).copy()
    z ^= z >> np.uint64(30)
    np.multiply(z, np.uint64(0xBF58476D1CE4E5B9), out=z)
    z ^= z >> np.uint64(27)
    np.multiply(z, np.uint64(0x94D049BB133111EB), out=z)
    z ^= z >> np.uint64(31)
    return z


def _goal_axis(length: int, spacing: int) -> np.ndarray:
    """Place goals regularly, falling back to the midpoint for a small map."""

    first = spacing // 2
    if first >= length:
        return np.asarray([length // 2], dtype=np.int64)
    return np.arange(first, length, spacing, dtype=np.int64)


def build_environment(
    config: Config,
    scenario_pack: dict[str, Any] | None = None,
) -> Environment:
    """Construct the frozen deterministic grid, transitions, and rewards."""

    config.validate()
    scenario_pack = load_scenario_pack() if scenario_pack is None else scenario_pack
    scenario_pack, _ = canonicalize_proposals(config, scenario_pack)
    states = np.arange(config.states, dtype=np.int64)
    x = states % config.width
    y = states // config.width

    keyed = states.astype(np.uint64)
    keyed ^= np.uint64(config.seed)
    keyed ^= np.uint64(0x9E3779B97F4A7C15)
    noise = (_mix64(keyed) & np.uint64(3)).astype(np.int16)

    risk = _risk_from_scenario(x, y, noise, scenario_pack)
    motif_activity_report(config, scenario_pack, noise)

    goal_x = _goal_axis(config.width, config.goal_spacing_x)
    goal_y = _goal_axis(config.height, config.goal_spacing_y)
    goals = np.isin(x, goal_x) & np.isin(y, goal_y)
    risk = risk.copy()
    risk[goals] = 0

    next_states = np.empty((config.states, config.actions), dtype=np.int32)
    rewards = np.empty((config.states, config.actions), dtype=np.float32)
    next_is_goal = np.empty((config.states, config.actions), dtype=bool)

    deltas = ((0, -1), (1, 0), (0, 1), (-1, 0))
    for action, (dx, dy) in enumerate(deltas):
        raw_x = x + dx
        raw_y = y + dy
        invalid = (
            (raw_x < 0)
            | (raw_x >= config.width)
            | (raw_y < 0)
            | (raw_y >= config.height)
        )
        nx = np.clip(raw_x, 0, config.width - 1)
        ny = np.clip(raw_y, 0, config.height - 1)
        destination = (ny * config.width + nx).astype(np.int32)
        destination_goal = goals[destination]

        reward = -1.0 - risk[destination].astype(np.float32)
        reward -= invalid.astype(np.float32) * np.float32(config.boundary_penalty)
        reward += destination_goal.astype(np.float32) * np.float32(config.goal_reward)

        destination = destination.copy()
        reward = reward.copy()
        destination[goals] = states[goals].astype(np.int32)
        reward[goals] = 0.0

        next_states[:, action] = destination
        rewards[:, action] = reward
        next_is_goal[:, action] = destination_goal | goals

    return Environment(
        risk=risk,
        goals=goals,
        next_states=next_states,
        rewards=rewards,
        next_is_goal=next_is_goal,
    )


def _select_evenly(states: np.ndarray, count: int) -> np.ndarray:
    states = np.unique(np.asarray(states, dtype=np.int64))
    if len(states) <= count:
        return states
    return states[np.linspace(0, len(states) - 1, count, dtype=np.int64)]


def expand_challenge_corpus(
    config: Config,
    env: Environment,
    scenario_pack: dict[str, Any],
    table: np.ndarray | None = None,
) -> dict[str, Any]:
    """Expand the compact challenge grammar into stable, deduplicated states."""

    states = np.arange(config.states, dtype=np.int64)
    x, y = states % config.width, states // config.width
    edge = (
        (x == 0) | (x == config.width - 1) | (y == 0) | (y == config.height - 1)
    )
    risk_counts = np.bincount(env.risk, minlength=16)
    rare_levels = np.flatnonzero(
        (risk_counts > 0) & (risk_counts <= max(1, int(np.median(risk_counts[risk_counts > 0]))))
    )
    rare_risk = np.isin(env.risk, rare_levels)
    goal_x = _goal_axis(config.width, config.goal_spacing_x)
    goal_y = _goal_axis(config.height, config.goal_spacing_y)
    distance = np.min(np.abs(x[:, None] - goal_x[None, :]), axis=1)
    distance += np.min(np.abs(y[:, None] - goal_y[None, :]), axis=1)
    distance_bands = (distance <= np.percentile(distance, 25)) | (
        distance >= np.percentile(distance, 75)
    )
    motif_masks = np.stack([
        _motif_mask(x, y, motif)
        for motif in sorted(scenario_pack["accepted_motifs"], key=lambda item: item["id"])
    ])
    intersections = np.sum(motif_masks, axis=0) >= 2
    horizons = tuple(
        h for h in (1, 4, 16, 32, 64, 128, 256) if h <= config.layers
    )
    horizon_sensitive = np.zeros(config.states, dtype=bool)
    if table is not None and len(horizons) >= 2:
        policies = np.argmax(table[np.asarray(horizons) - 1], axis=2)
        horizon_sensitive = np.any(policies[1:] != policies[:-1], axis=0)

    masks = {
        "boundary": edge,
        "rare_risk": rare_risk,
        "goal_distance": distance_bands,
        "motif_intersection": intersections,
        "horizon_sensitive": horizon_sensitive,
    }
    rows: list[dict[str, Any]] = []
    quarantined = 0
    for proposal in scenario_pack["challenge_grammar"]:
        stratum = proposal["stratum"]
        candidates = states[masks[stratum] & ~env.goals]
        if not len(candidates):
            quarantined += 1
            continue
        selected = _select_evenly(candidates, proposal["count"])
        rows.extend({"key": f"s{int(state):06d}", "state": int(state), "stratum": stratum,
                     "proposal_id": proposal["id"]} for state in selected)
    unique: dict[int, dict[str, Any]] = {}
    for row in rows:
        unique.setdefault(row["state"], row)
    return {
        "version": CHALLENGE_CORPUS_VERSION,
        "grammar_proposal_count": len(scenario_pack["challenge_grammar"]),
        "expanded_row_count": len(rows),
        "canonical_unique_state_count": len(unique),
        "duplicate_expanded_rows": len(rows) - len(unique),
        "quarantined_challenge_proposals": quarantined,
        "selected_horizons": list(horizons),
        "rows": [unique[state] for state in sorted(unique)],
    }


def challenge_metrics(
    table: np.ndarray, config: Config, env: Environment, corpus: dict[str, Any]
) -> dict[str, Any]:
    """Compute vectorized policy, action-gap, and horizon-change evidence."""

    selected = np.asarray([row["state"] for row in corpus["rows"]], dtype=np.int64)
    horizons = np.asarray(corpus["selected_horizons"], dtype=np.int64)
    if len(selected) == 0 or len(horizons) == 0:
        return {"corpus_state_count": int(len(selected)), "action_distribution": {},
                "ambiguous_decision_count": 0, "states_changing_greedy_action": 0,
                "horizon_change_count_by_transition": {}}
    q = np.asarray(table[horizons - 1][:, selected, :], dtype=np.float32)
    policies = np.argmax(q, axis=2)
    grid_policies = np.argmax(np.asarray(table[horizons - 1], dtype=np.float32), axis=2)
    partitioned = np.partition(q, -2, axis=2)
    gaps = partitioned[:, :, -1] - partitioned[:, :, -2]
    action_counts = np.bincount(policies.ravel(), minlength=config.actions)
    changes = np.any(policies[1:] != policies[:-1], axis=0) if len(horizons) > 1 else np.zeros(len(selected), dtype=bool)
    return {
        "corpus_state_count": int(len(selected)),
        "action_distribution": {ACTIONS[i]: int(action_counts[i]) for i in range(config.actions)},
        "action_gap_min": float(np.min(gaps)),
        "action_gap_median": float(np.median(gaps)),
        "ambiguous_gap_threshold": 1.0,
        "ambiguous_decision_count": int(np.count_nonzero(gaps <= 1.0)),
        "ambiguous_decision_fraction": float(np.mean(gaps <= 1.0)),
        "states_changing_greedy_action": int(np.count_nonzero(changes)),
        "grid_states_changing_greedy_action": int(
            np.count_nonzero(np.any(grid_policies[1:] != grid_policies[:-1], axis=0))
        ) if len(horizons) > 1 else 0,
        "horizon_change_count_by_transition": {
            f"{int(horizons[i])}->{int(horizons[i + 1])}": int(np.count_nonzero(policies[i] != policies[i + 1]))
            for i in range(len(horizons) - 1)
        },
        "grid_horizon_change_count_by_transition": {
            f"{int(horizons[i])}->{int(horizons[i + 1])}": int(
                np.count_nonzero(grid_policies[i] != grid_policies[i + 1])
            )
            for i in range(len(horizons) - 1)
        },
    }


def environment_sha256(
    config: Config,
    env: Environment,
    scenario_pack: dict[str, Any] | None = None,
) -> str:
    """Bind the semantic arrays used to derive the table."""

    digest = hashlib.sha256()
    scenario_pack = load_scenario_pack() if scenario_pack is None else scenario_pack
    scenario_pack, _ = canonicalize_proposals(config, scenario_pack)
    digest.update(json.dumps(asdict(config), sort_keys=True).encode("utf-8"))
    digest.update(scenario_pack_sha256(scenario_pack).encode("ascii"))
    for array in (env.risk, env.goals, env.next_states, env.rewards, env.next_is_goal):
        digest.update(array.dtype.str.encode("ascii"))
        digest.update(str(array.shape).encode("ascii"))
        digest.update(np.ascontiguousarray(array).tobytes())
    return digest.hexdigest()


def file_sha256(path: Path, chunk_bytes: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_bytes):
            digest.update(chunk)
    return digest.hexdigest()


def source_sha256() -> str:
    return file_sha256(Path(__file__).resolve())


def _expected_layer(
    env: Environment,
    previous_value: np.ndarray,
    gamma: float,
) -> np.ndarray:
    continuation = previous_value[env.next_states]
    continuation = np.where(env.next_is_goal, 0.0, continuation)
    q_values = env.rewards + np.float32(gamma) * continuation
    q_values[env.goals, :] = 0.0
    return np.asarray(q_values, dtype=np.float32)


def generate_table(
    path: Path,
    config: Config,
    *,
    force: bool = False,
    progress: bool = True,
    scenario_pack: dict[str, Any] | None = None,
) -> float:
    """Generate Q_1 through Q_H by exact finite-horizon dynamic programming."""

    config.validate()
    if path.exists() and not force:
        raise FileExistsError(f"refusing to overwrite {path}; pass --force")
    path.parent.mkdir(parents=True, exist_ok=True)
    env = build_environment(config, scenario_pack)

    started = time.perf_counter()
    table = np.lib.format.open_memmap(
        path,
        mode="w+",
        dtype="<f4",
        shape=(config.layers, config.states, config.actions),
    )
    previous_value = np.zeros(config.states, dtype=np.float32)
    for layer in range(config.layers):
        q_values = _expected_layer(env, previous_value, config.gamma)
        table[layer, :, :] = q_values
        previous_value = np.max(q_values, axis=1)
        if progress and ((layer + 1) % 32 == 0 or layer + 1 == config.layers):
            print(f"generated layer {layer + 1}/{config.layers}", flush=True)
    table.flush()
    del table
    return time.perf_counter() - started


def _load_table(path: Path) -> np.memmap:
    table = np.load(path, mmap_mode="r")
    if not isinstance(table, np.memmap):
        raise TypeError("expected a memory-mapped NumPy array")
    return table


def verify_table(
    path: Path,
    config: Config,
    *,
    progress: bool = True,
    scenario_pack: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Independently replay every Bellman layer and compare every stored value."""

    started = time.perf_counter()
    table = _load_table(path)
    expected_shape = (config.layers, config.states, config.actions)
    if table.shape != expected_shape:
        raise ValueError(f"shape {table.shape} does not match {expected_shape}")
    if table.dtype != np.dtype("<f4"):
        raise ValueError(f"dtype {table.dtype} is not little-endian float32")

    env = build_environment(config, scenario_pack)
    previous_value = np.zeros(config.states, dtype=np.float32)
    max_error = 0.0
    all_finite = True
    terminal_rows_zero = True
    for layer in range(config.layers):
        expected = _expected_layer(env, previous_value, config.gamma)
        stored = np.asarray(table[layer])
        difference = np.abs(stored - expected)
        max_error = max(max_error, float(np.max(difference)))
        all_finite = all_finite and bool(np.all(np.isfinite(stored)))
        terminal_rows_zero = terminal_rows_zero and bool(
            np.all(stored[env.goals, :] == 0.0)
        )
        previous_value = np.max(stored, axis=1)
        if progress and ((layer + 1) % 64 == 0 or layer + 1 == config.layers):
            print(f"verified layer {layer + 1}/{config.layers}", flush=True)

    counterexamples = search_counterexamples(table, config, env)
    effective_pack = load_scenario_pack() if scenario_pack is None else scenario_pack
    effective_pack, _ = canonicalize_proposals(config, effective_pack)
    challenge_corpus = expand_challenge_corpus(config, env, effective_pack, table)
    challenge_evidence = challenge_metrics(table, config, env, challenge_corpus)
    _, canonicalization = canonicalize_proposals(
        config, effective_pack
    )
    coverage = {
        "table_layers": config.layers,
        "table_states": config.states,
        "table_actions": config.actions,
        "q_values_with_deterministic_labels": config.values,
        "canonical_proposed_states": canonicalization["canonical_state_count"],
        "canonical_proposed_actions": canonicalization["canonical_actions"],
        "canonical_trajectory_count": canonicalization["trajectory_count"],
        "coverage_fraction": 1.0,
        "proposed_state_coverage_fraction": canonicalization["canonical_state_count"] / config.states,
        "uncertainty_note": "Exact in-model Q labels have no sampling uncertainty; model mismatch and out-of-domain inputs remain uncertain.",
        "motif_activity": motif_activity_report(config, effective_pack),
        "challenge_corpus": challenge_corpus,
        "challenge_metrics": challenge_evidence,
    }
    elapsed = time.perf_counter() - started
    return {
        "method": "full independent Bellman replay",
        "checked_layers": config.layers,
        "checked_state_rows": config.layers * config.states,
        "checked_q_values": config.values,
        "max_abs_bellman_error": max_error,
        "all_values_finite": all_finite,
        "terminal_rows_zero": terminal_rows_zero,
        "counterexample_search": counterexamples,
        "challenge_corpus": challenge_corpus,
        "challenge_metrics": challenge_evidence,
        "coverage": coverage,
        "passed": max_error == 0.0 and all_finite and terminal_rows_zero and counterexamples["passed"],
        "seconds": elapsed,
    }


def search_counterexamples(
    table: np.ndarray, config: Config, env: Environment, *, limit: int = 512
) -> dict[str, Any]:
    """Probe sparse and high-risk rows for label or policy contradictions.

    This is deliberately complementary to full replay: it chooses rare-risk,
    boundary, and goal states first, then checks every horizon for those rows.
    Any disagreement is retained as a small deterministic counterexample set.
    """

    risk_counts = np.bincount(env.risk, minlength=16)
    rare_order = np.argsort(risk_counts[env.risk], kind="stable")
    boundary = np.flatnonzero(
        (np.arange(config.states) % config.width == 0)
        | (np.arange(config.states) % config.width == config.width - 1)
        | (np.arange(config.states) < config.width)
        | (np.arange(config.states) >= config.states - config.width)
    )
    goals = np.flatnonzero(env.goals)
    candidates = np.unique(np.concatenate((rare_order[:limit], boundary, goals)))[:limit]
    previous_value = np.zeros(config.states, dtype=np.float32)
    contradictions: list[dict[str, Any]] = []
    checked = 0
    for layer in range(config.layers):
        expected = _expected_layer(env, previous_value, config.gamma)
        stored = np.asarray(table[layer])
        for state in candidates:
            checked += config.actions
            mismatch = np.flatnonzero(stored[state] != expected[state])
            policy_mismatch = int(np.argmax(stored[state])) != int(np.argmax(expected[state]))
            if len(mismatch) or policy_mismatch:
                if len(contradictions) < 16:
                    contradictions.append({
                        "layer": layer + 1,
                        "state_key": f"s{int(state):06d}",
                        "risk": int(env.risk[state]),
                        "mismatched_actions": [ACTIONS[int(action)] for action in mismatch],
                        "stored_policy": ACTIONS[int(np.argmax(stored[state]))],
                        "simulator_policy": ACTIONS[int(np.argmax(expected[state]))],
                    })
        previous_value = np.max(expected, axis=1)
    return {
        "method": "rare-risk, boundary, and goal state probes",
        "candidate_state_count": int(len(candidates)),
        "checked_q_values": checked,
        "rare_risk_levels": [int(level) for level, count in enumerate(risk_counts) if count <= max(1, int(np.median(risk_counts)))],
        "contradiction_count": len(contradictions),
        "counterexamples": contradictions,
        "passed": not contradictions,
    }


def _rollout(
    table: np.ndarray,
    config: Config,
    env: Environment,
    start_state: int,
    horizon: int,
    *,
    include_steps: bool = False,
) -> dict[str, Any]:
    if not 0 <= start_state < config.states:
        raise ValueError("start state is outside the grid")
    if not 1 <= horizon <= config.layers:
        raise ValueError("horizon must be between 1 and the number of layers")

    state = int(start_state)
    discounted_return = 0.0
    discount = 1.0
    risk_sum = 0
    steps: list[dict[str, Any]] = []
    reached_goal = bool(env.goals[state])
    steps_taken = 0

    for step_index in range(horizon):
        if reached_goal:
            break
        remaining = horizon - step_index
        q_values = np.asarray(table[remaining - 1, state, :], dtype=np.float32)
        action = int(np.argmax(q_values))
        next_state = int(env.next_states[state, action])
        reward = float(env.rewards[state, action])
        discounted_return += discount * reward
        discount *= config.gamma
        risk_sum += int(env.risk[next_state])
        reached_goal = bool(env.goals[next_state])
        steps_taken += 1

        if include_steps:
            steps.append(
                {
                    "step": step_index,
                    "horizon_layer": remaining,
                    "state": state,
                    "coordinate": [state % config.width, state // config.width],
                    "risk": int(env.risk[state]),
                    "q_values": [round(float(value), 6) for value in q_values],
                    "action": ACTIONS[action],
                    "reward": reward,
                    "next_state": next_state,
                    "next_coordinate": [
                        next_state % config.width,
                        next_state // config.width,
                    ],
                    "reached_goal": reached_goal,
                }
            )
        state = next_state

    result: dict[str, Any] = {
        "start_state": int(start_state),
        "start_coordinate": [
            int(start_state % config.width),
            int(start_state // config.width),
        ],
        "horizon": horizon,
        "steps_taken": steps_taken,
        "end_state": state,
        "end_coordinate": [state % config.width, state // config.width],
        "reached_goal": reached_goal,
        "discounted_return": round(discounted_return, 6),
        "cumulative_risk": risk_sum,
    }
    if include_steps:
        result["steps"] = steps
    return result


def _sample_states(config: Config, env: Environment, count: int) -> np.ndarray:
    candidates = np.linspace(0, config.states - 1, num=max(count * 2, 2), dtype=np.int64)
    candidates = np.unique(candidates[~env.goals[candidates]])
    return candidates[:count]


def evaluate_rollouts(
    table: np.ndarray,
    config: Config,
    env: Environment,
    count: int,
) -> dict[str, Any]:
    starts = _sample_states(config, env, count)
    results = [
        _rollout(table, config, env, int(state), config.layers)
        for state in starts
    ]
    successes = [result for result in results if result["reached_goal"]]
    steps = [int(result["steps_taken"]) for result in successes]
    returns = [float(result["discounted_return"]) for result in results]
    return {
        "sample_rule": "evenly spaced non-goal state ids",
        "sample_count": len(results),
        "reached_goal_count": len(successes),
        "reached_goal_rate": len(successes) / len(results) if results else 0.0,
        "median_steps_when_successful": float(np.median(steps)) if steps else None,
        "maximum_steps_when_successful": max(steps) if steps else None,
        "mean_discounted_return": float(np.mean(returns)) if returns else None,
    }


def select_deliberation_example(
    table: np.ndarray,
    config: Config,
    env: Environment,
) -> dict[str, Any]:
    requested = (1, 4, 16, 32, 64, 128, 256)
    horizons = [h for h in requested if h <= config.layers]
    policies = np.stack(
        [np.argmax(table[h - 1, :, :], axis=1) for h in horizons],
        axis=0,
    )
    switches = np.sum(policies[1:] != policies[:-1], axis=0)
    switches[env.goals] = -1
    state = int(np.argmax(switches))
    decisions = []
    for index, horizon in enumerate(horizons):
        q_values = np.asarray(table[horizon - 1, state, :], dtype=np.float32)
        action = int(policies[index, state])
        decisions.append(
            {
                "horizon": horizon,
                "action": ACTIONS[action],
                "q_values": [round(float(value), 6) for value in q_values],
            }
        )
    return {
        "selection_rule": "lowest state id with the most policy changes across reported horizons",
        "state": state,
        "coordinate": [state % config.width, state // config.width],
        "policy_change_count": int(switches[state]),
        "decisions": decisions,
    }


def benchmark_queries(
    table: np.ndarray,
    config: Config,
    *,
    count: int,
) -> dict[str, Any]:
    count = max(1, count)
    indices = np.arange(count + 64, dtype=np.uint64)
    states = (_mix64(indices ^ np.uint64(config.seed)) % np.uint64(config.states)).astype(
        np.int64
    )
    horizons = (
        _mix64(indices ^ np.uint64(config.seed + 1)) % np.uint64(config.layers) + 1
    ).astype(np.int64)

    # Warm the Python path and a small deterministic subset of mapped pages.
    for state, horizon in zip(states[:64], horizons[:64]):
        int(np.argmax(table[int(horizon) - 1, int(state), :]))

    timings = np.empty(count, dtype=np.int64)
    checksum = 0
    for index, (state, horizon) in enumerate(zip(states[64:], horizons[64:])):
        started = time.perf_counter_ns()
        action = int(np.argmax(table[int(horizon) - 1, int(state), :]))
        timings[index] = time.perf_counter_ns() - started
        checksum = (checksum * 5 + action + 1) % 1_000_000_007

    return {
        "method": "warm random memory-mapped row lookup plus NumPy argmax",
        "query_count": count,
        "q_values_read_per_query": config.actions,
        "median_microseconds": float(np.median(timings)) / 1000.0,
        "p95_microseconds": float(np.percentile(timings, 95)) / 1000.0,
        "maximum_microseconds": float(np.max(timings)) / 1000.0,
        "decision_checksum": checksum,
        "warning": "Timing depends on hardware, operating-system cache state, and Python overhead.",
    }


def build_manifest(
    artifact_path: Path,
    config: Config,
    generation_seconds: float,
    verification: dict[str, Any],
    rollouts: dict[str, Any],
    deliberation: dict[str, Any],
    benchmark: dict[str, Any],
    scenario_pack: dict[str, Any],
    scenario_pack_filename: str,
) -> dict[str, Any]:
    env = build_environment(config, scenario_pack)
    _, canonicalization = canonicalize_proposals(config, scenario_pack)
    file_bytes = artifact_path.stat().st_size
    return {
        "schema": "glassmind-artifact-manifest-v1",
        "generator_version": GENERATOR_VERSION,
        "generator_source_sha256": source_sha256(),
        "artifact": {
            "filename": artifact_path.name,
            "format": "NumPy .npy",
            "shape": [config.layers, config.states, config.actions],
            "axis_meaning": ["remaining_horizon", "grid_state", "action"],
            "dtype": "little-endian float32",
            "q_values": config.values,
            "data_bytes": config.data_bytes,
            "file_bytes": file_bytes,
            "decimal_megabytes": file_bytes / 1_000_000,
            "mebibytes": file_bytes / (1024 * 1024),
            "sha256": file_sha256(artifact_path),
        },
        "config": asdict(config),
        "llm_scenario_pack": {
            "filename": scenario_pack_filename,
            "schema": scenario_pack["schema"],
            "sha256": scenario_pack_sha256(scenario_pack),
            "authorship": scenario_pack["authorship"],
            "accepted_motif_ids": [
                motif["id"] for motif in scenario_pack["accepted_motifs"]
            ],
            "quarantined_proposal_ids": [
                proposal["id"] for proposal in scenario_pack["quarantined_proposals"]
            ],
            "canonicalization": canonicalization,
        },
        "environment": {
            "name": "synthetic deterministic emergency-routing grid",
            "states": config.states,
            "actions": list(ACTIONS),
            "goal_count": int(np.count_nonzero(env.goals)),
            "transition": "cardinal move, boundary moves remain in place",
            "reward": "-1 - destination risk - boundary penalty + terminal goal reward",
            "risk": "deterministic background plus schema-checked LLM-proposed motifs, clipped to 0..15",
            "sha256": environment_sha256(config, env, scenario_pack),
        },
        "recurrence": {
            "base": "V_0(s) = 0",
            "step": "Q_h(s,a) = r(s,a) + gamma * 1[nonterminal] * V_(h-1)(T(s,a))",
            "value": "V_h(s) = max_a Q_h(s,a)",
            "tie_break": "first maximum in north, east, south, west order",
        },
        "measurements": {
            "generation_seconds": generation_seconds,
            "verification": verification,
            "rollouts": rollouts,
            "deliberation_example": deliberation,
            "query_benchmark": benchmark,
        },
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "claims": {
            "demonstrates": [
                "256 distinct finite-horizon Q layers",
                "deterministic generation and content hashing",
                "full Bellman replay over every stored Q value",
                "bounded canonicalization and targeted counterexample probes",
                "replayable finite-horizon decisions in the frozen synthetic model",
            ],
            "does_not_demonstrate": [
                "general intelligence",
                "transfer to unseen state representations",
                "real emergency-routing safety or performance",
                "that file size equals useful learned knowledge",
            ],
        },
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def load_config_from_manifest(path: Path) -> tuple[Config, dict[str, Any]]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    return Config(**manifest["config"]), manifest


def make_trace(
    table_path: Path,
    config: Config,
    *,
    start_state: int | None = None,
    horizon: int | None = None,
    scenario_pack: dict[str, Any] | None = None,
) -> dict[str, Any]:
    table = _load_table(table_path)
    scenario_pack = load_scenario_pack() if scenario_pack is None else scenario_pack
    env = build_environment(config, scenario_pack)
    deliberation = select_deliberation_example(table, config, env)
    selected_state = deliberation["state"] if start_state is None else start_state
    selected_horizon = config.layers if horizon is None else horizon
    return {
        "schema": "glassmind-decision-trace-v1",
        "generator_version": GENERATOR_VERSION,
        "artifact_filename": table_path.name,
        "artifact_sha256": file_sha256(table_path),
        "scenario_pack_sha256": scenario_pack_sha256(scenario_pack),
        "environment_sha256": environment_sha256(config, env, scenario_pack),
        "deliberation_example": deliberation,
        "rollout": _rollout(
            table,
            config,
            env,
            selected_state,
            selected_horizon,
            include_steps=True,
        ),
    }


def _profile(name: str) -> Config:
    try:
        return PROFILES[name]
    except KeyError as error:
        raise ValueError(f"unknown profile {name!r}") from error


def command_build(args: argparse.Namespace) -> int:
    config = _profile(args.profile)
    scenario_path = Path(args.scenario_pack)
    scenario_pack = load_scenario_pack(scenario_path)
    output = Path(args.output)
    manifest_path = Path(args.manifest)
    generation_seconds = generate_table(
        output,
        config,
        force=args.force,
        scenario_pack=scenario_pack,
    )
    verification = verify_table(output, config, scenario_pack=scenario_pack)
    if not verification["passed"]:
        raise RuntimeError(f"verification failed: {verification}")

    table = _load_table(output)
    env = build_environment(config, scenario_pack)
    rollouts = evaluate_rollouts(table, config, env, args.rollout_samples)
    deliberation = select_deliberation_example(table, config, env)
    benchmark = benchmark_queries(table, config, count=args.benchmark_queries)
    manifest = build_manifest(
        output,
        config,
        generation_seconds,
        verification,
        rollouts,
        deliberation,
        benchmark,
        scenario_pack,
        scenario_path.name,
    )
    write_json(manifest_path, manifest)
    if args.trace:
        write_json(
            Path(args.trace),
            make_trace(output, config, scenario_pack=scenario_pack),
        )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def command_verify(args: argparse.Namespace) -> int:
    config, manifest = load_config_from_manifest(Path(args.manifest))
    scenario_pack = load_scenario_pack(Path(args.scenario_pack))
    table_path = Path(args.table)
    expected_hash = manifest["artifact"]["sha256"]
    actual_hash = file_sha256(table_path)
    verification = verify_table(table_path, config, scenario_pack=scenario_pack)
    expected_scenario_hash = manifest["llm_scenario_pack"]["sha256"]
    actual_scenario_hash = scenario_pack_sha256(scenario_pack)
    verification["expected_sha256"] = expected_hash
    verification["actual_sha256"] = actual_hash
    verification["hash_matches"] = actual_hash == expected_hash
    verification["scenario_pack_hash_matches"] = (
        actual_scenario_hash == expected_scenario_hash
    )
    verification["passed"] = (
        verification["passed"]
        and verification["hash_matches"]
        and verification["scenario_pack_hash_matches"]
    )
    print(json.dumps(verification, indent=2, sort_keys=True))
    return 0 if verification["passed"] else 1


def command_trace(args: argparse.Namespace) -> int:
    config, _ = load_config_from_manifest(Path(args.manifest))
    scenario_pack = load_scenario_pack(Path(args.scenario_pack))
    result = make_trace(
        Path(args.table),
        config,
        start_state=args.start_state,
        horizon=args.horizon,
        scenario_pack=scenario_pack,
    )
    if args.output:
        write_json(Path(args.output), result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build", help="generate, replay, benchmark, and report")
    build.add_argument("--profile", choices=sorted(PROFILES), required=True)
    build.add_argument("--output", required=True)
    build.add_argument("--manifest", required=True)
    build.add_argument("--trace")
    build.add_argument("--scenario-pack", default=str(DEFAULT_SCENARIO_PACK))
    build.add_argument("--force", action="store_true")
    build.add_argument("--rollout-samples", type=int, default=256)
    build.add_argument("--benchmark-queries", type=int, default=4096)
    build.set_defaults(function=command_build)

    verify = subparsers.add_parser("verify", help="check a table against its manifest")
    verify.add_argument("--table", required=True)
    verify.add_argument("--manifest", required=True)
    verify.add_argument("--scenario-pack", default=str(DEFAULT_SCENARIO_PACK))
    verify.set_defaults(function=command_verify)

    trace = subparsers.add_parser("trace", help="emit one replayable decision trace")
    trace.add_argument("--table", required=True)
    trace.add_argument("--manifest", required=True)
    trace.add_argument("--scenario-pack", default=str(DEFAULT_SCENARIO_PACK))
    trace.add_argument("--start-state", type=int)
    trace.add_argument("--horizon", type=int)
    trace.add_argument("--output")
    trace.set_defaults(function=command_trace)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.function(args))


if __name__ == "__main__":
    raise SystemExit(main())
