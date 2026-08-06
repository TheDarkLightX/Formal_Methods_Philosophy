from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from experiments.qgent_rate_structured_memory_v001.pca_quadratic_feature_probe import (
    canonical_json_bytes as canonical_model_json_bytes,
)
from experiments.qgent_rate_structured_memory_v001.rate_structured_memory import (
    MAX_SCORE_ERROR,
    ArtifactError,
    build_artifact,
    build_experiment,
    decode_artifact,
    greedy_actions,
    sha256_bytes,
)

ROOT = Path(__file__).resolve().parents[2]
SENTINEL = -(2**30)


def tiny_table() -> np.ndarray:
    return np.asarray(
        [
            [[10, 7, SENTINEL], [4, 4, 1]],
            [[12, 11, SENTINEL], [3, 2, -5]],
            [[9, -2, SENTINEL], [8, 8, 7]],
        ],
        dtype="<i4",
    )


def test_quotient_preserves_maxima_and_bounds_score_error() -> None:
    source = tiny_table()
    source_hash = sha256_bytes(source.tobytes())
    artifact = build_artifact(
        source, sentinel=SENTINEL, step=4, source_sha256=source_hash
    )
    rebuilt, _ = decode_artifact(artifact, expected_source_sha256=source_hash)
    assert np.array_equal(
        greedy_actions(source, SENTINEL),
        greedy_actions(rebuilt, SENTINEL),
    )
    assert np.array_equal(source == SENTINEL, rebuilt == SENTINEL)
    permitted = source != SENTINEL
    assert int(np.max(np.abs(source[permitted] - rebuilt[permitted]))) <= 5


def test_artifact_is_deterministic_and_source_bound() -> None:
    source = tiny_table()
    source_hash = sha256_bytes(source.tobytes())
    first = build_artifact(source, sentinel=SENTINEL, step=4, source_sha256=source_hash)
    second = build_artifact(
        source, sentinel=SENTINEL, step=4, source_sha256=source_hash
    )
    assert first == second
    with pytest.raises(ArtifactError):
        decode_artifact(first, expected_source_sha256="0" * 64)


def test_corrupt_artifact_fails_closed() -> None:
    source = tiny_table()
    source_hash = sha256_bytes(source.tobytes())
    artifact = bytearray(
        build_artifact(source, sentinel=SENTINEL, step=4, source_sha256=source_hash)
    )
    artifact[-1] ^= 1
    with pytest.raises(ArtifactError):
        decode_artifact(bytes(artifact), expected_source_sha256=source_hash)


def test_full_experiment_beats_strong_lossless_control() -> None:
    artifact, report = build_experiment()
    selected = report["selected"]
    exact = report["controls"]["strong_lossless_q_control"]
    assert report["acceptance"]["experiment_accepted"] is True
    assert selected["maximum_absolute_score_error"] <= MAX_SCORE_ERROR
    assert selected["greedy_action_mismatches"] == 0
    assert selected["forbidden_mask_changes"] == 0
    assert len(artifact) < exact["payload_only_bytes"]
    assert sha256_bytes(artifact) == selected["sha256"]
    nearest = report["controls"]["nearest_rounding_counterexample"]
    assert nearest["strict_negative_cells_rounded_to_zero"] > 0
    assert nearest["greedy_action_mismatches"] > 0


def test_published_report_and_artifact_match_when_present() -> None:
    artifact_path = ROOT / "assets/downloads/qgent-decision-quotient-q-v1.qdq"
    report_path = (
        ROOT
        / "experiments/qgent_rate_structured_memory_v001/results"
        / "qgent_rate_structured_memory_v001.report.json"
    )
    if not artifact_path.exists() or not report_path.exists():
        pytest.skip("generated public artifacts are not present")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    artifact = artifact_path.read_bytes()
    assert sha256_bytes(artifact) == report["selected"]["sha256"]
    assert len(artifact) == report["selected"]["artifact_bytes"]
    assert report["acceptance"]["experiment_accepted"] is True


def test_centroid_feature_probe_is_preserved_as_negative_knowledge() -> None:
    report_path = (
        ROOT
        / "experiments/qgent_rate_structured_memory_v001/results"
        / "qgent_centroid_feature_probe_v001.report.json"
    )
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["validation"]["all_gates_improved"] is True
    assert report["confirmation"]["all_gates_improved"] is False
    assert report["decision"]["status"] == "REFUTED"
    assert report["decision"]["candidate_promoted"] is False
    baseline = report["confirmation"]["baseline"]
    candidate = report["confirmation"]["candidate"]
    assert (
        candidate["mean_optimal_utility_ratio"] < baseline["mean_optimal_utility_ratio"]
    )
    assert (
        candidate["minimum_optimal_utility_ratio"]
        < baseline["minimum_optimal_utility_ratio"]
    )


def test_pca_quadratic_probe_beats_both_confirmation_controls() -> None:
    report_path = (
        ROOT
        / "experiments/qgent_rate_structured_memory_v001/results"
        / "qgent_pca_quadratic_feature_probe_v001.report.json"
    )
    report = json.loads(report_path.read_text(encoding="utf-8"))
    confirmation = report["confirmation"]
    assert report["decision"]["status"] == "SUPPORTED_BOUNDED"
    assert report["decision"]["candidate_promoted_for_lab_comparison"] is True
    assert confirmation["beats_frozen_16_on_primary_gates"] is True
    assert confirmation["beats_plain_32_on_primary_gates"] is True
    assert confirmation["pca_quadratic_candidate"]["forbidden_selections"] == 0
    for control in ("frozen_16_world_linear", "plain_32_world_linear"):
        assert (
            confirmation["pca_quadratic_candidate"]["mean_ratio"]
            > confirmation[control]["mean_ratio"]
        )
        assert (
            confirmation["pca_quadratic_candidate"]["minimum_ratio"]
            >= confirmation[control]["minimum_ratio"]
        )
        assert (
            confirmation["pca_quadratic_candidate"]["gain_over_myopic"]
            > confirmation[control]["gain_over_myopic"]
        )


def test_pca_quadratic_model_is_content_bound() -> None:
    model_path = (
        ROOT
        / "assets/downloads/qgent-pca-quadratic-feature-model-v1.json"
    )
    model = json.loads(model_path.read_text(encoding="utf-8"))
    claimed_hash = model.pop("sha256")
    assert sha256_bytes(canonical_model_json_bytes(model)) == claimed_hash
    assert model["feature_count"] == 89
    assert model["encoder"]["rank"] == 10
    assert len(model["encoder"]["quadratic_pairs"]) == 55
    assert len(model["weights"]) == 9
    assert all(len(row) == 89 for row in model["weights"])


def test_tutorial_uses_scoped_measured_claims_and_public_paths() -> None:
    tutorial = (
        ROOT
        / "tutorials/finding-hidden-structure-representation-learning-compression.md"
    ).read_text(encoding="utf-8")
    assert "102,799" in tutorial
    assert "114,690" in tutorial
    assert "101 greedy-action mismatches" in tutorial
    assert "0.91959" in tutorial
    assert "0.98426" in tutorial
    assert "does not improve the learned policy or" in tutorial
    assert "/home/" not in tutorial
    assert "/tmp/" not in tutorial
    assert "trevormoc" not in tutorial
