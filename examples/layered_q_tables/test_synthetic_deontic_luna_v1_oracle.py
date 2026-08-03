from __future__ import annotations

import ast
import copy
import io
import itertools
import json
import tempfile
import unittest
from collections import Counter
from contextlib import redirect_stdout
from dataclasses import replace
from pathlib import Path
from unittest import mock

from examples.layered_q_tables import (
    synthetic_deontic_luna_v1_oracle as oracle,
)

ROOT = Path(__file__).resolve().parent
TEMPLATE_PATH = ROOT / "synthetic_deontic_luna_v1_templates.json"
SEMANTICS_PATH = ROOT.parents[1] / "research" / "synthetic_deontic_luna_v1_semantics.md"
ORACLE_PATH = ROOT / "synthetic_deontic_luna_v1_oracle.py"


def seal_record(
    record: dict[str, object], *, replace_claim: bool = False
) -> dict[str, object]:
    core = record["semantic_core"]
    assert isinstance(core, dict)
    core_hash = oracle.canonical_hash(core)
    record["semantic_core_sha256"] = core_hash
    record["stable_id"] = f"sdk-luna-v1-{core_hash}"
    if replace_claim:
        record["generator_claim"] = oracle.evaluate_core(core)
    record.pop("record_sha256", None)
    record["record_sha256"] = oracle.canonical_hash(record)
    return record


def rename_norms(core: dict[str, object], mapping: dict[str, str]) -> dict[str, object]:
    renamed = copy.deepcopy(core)
    norms = renamed["norms"]
    assert isinstance(norms, list)
    for norm in norms:
        norm["id"] = mapping[norm["id"]]
        if norm["repair_for"] != "none":
            norm["repair_for"] = mapping[norm["repair_for"]]
        for ref in norm["condition_refs"]:
            if ref["kind"] in {"state", "violation"}:
                ref["id"] = mapping[ref["id"]]
        norm["condition_refs"].sort(key=lambda item: (item["kind"], item["id"]))
    norms.sort(key=lambda item: item["id"])
    for evidence in renamed["evidence"]:
        evidence["target_norm_ids"] = sorted(
            mapping[norm_id] for norm_id in evidence["target_norm_ids"]
        )
        payload = {
            "evidence_id": evidence["id"],
            "target_norm_ids": evidence["target_norm_ids"],
            "truth": evidence["truth"],
        }
        evidence["payload_sha256"] = oracle.canonical_hash(payload)
    for conflict in renamed["conflicts"]:
        conflict["left_norm_id"] = mapping[conflict["left_norm_id"]]
        conflict["right_norm_id"] = mapping[conflict["right_norm_id"]]
    for edge in renamed["priority_edges"]:
        edge["higher_norm_id"] = mapping[edge["higher_norm_id"]]
        edge["lower_norm_id"] = mapping[edge["lower_norm_id"]]
    renamed["priority_edges"].sort(
        key=lambda item: (item["higher_norm_id"], item["lower_norm_id"])
    )
    return renamed


class SyntheticDeonticLunaV1OracleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.template = oracle.load_template_bank(TEMPLATE_PATH)
        oracle.load_bound_semantics(SEMANTICS_PATH)

    def reference(
        self, codes: tuple[int, int, int, int, int, int]
    ) -> dict[str, object]:
        return oracle.build_reference_record(self.template, codes)

    def verify(self, record: dict[str, object]) -> oracle.VerifiedCase:
        return oracle.verify_record(oracle.canonical_bytes(record), self.template)

    def assert_rejects(self, record: dict[str, object], expected_code: str) -> None:
        with self.assertRaises(oracle.OracleReject) as caught:
            self.verify(record)
        self.assertEqual(caught.exception.code, expected_code)

    def test_frozen_sources_and_template_validate(self) -> None:
        self.assertEqual(self.template.sha256, oracle.EXPECTED_TEMPLATE_SHA256)
        self.assertEqual(
            oracle.sha256_bytes(SEMANTICS_PATH.read_bytes()),
            oracle.EXPECTED_SEMANTICS_SHA256,
        )
        self.assertEqual(len(self.template.data["domains"]), 16)
        self.assertEqual(len(self.template.data["topology_programs"]), 16)
        self.assertEqual(
            [
                len(domain["causal_mutations"])
                for domain in self.template.data["domains"]
            ],
            [2] * 16,
        )
        self.assertTrue(
            all(
                len(mutation["changed_field_ids"]) == 1
                for domain in self.template.data["domains"]
                for mutation in domain["causal_mutations"]
            )
        )

    def test_rank_unrank_is_exact_and_rejects_boolean_aliases(self) -> None:
        for ordinal in range(oracle.RECORD_COUNT):
            self.assertEqual(
                oracle.rank_coordinate(oracle.unrank_ordinal(ordinal)), ordinal
            )
        for bad in (-1, oracle.RECORD_COUNT, True, "0"):
            with self.subTest(bad=bad), self.assertRaises(oracle.OracleReject):
                oracle.unrank_ordinal(bad)  # type: ignore[arg-type]

    def test_reference_records_round_trip_across_semantic_frontiers(self) -> None:
        coordinates = (
            (0, 0, 0, 0, 0, 0),
            (15, 15, 3, 3, 3, 3),
            (4, 7, 0, 1, 2, 0),
            (4, 7, 0, 2, 0, 0),
            (4, 7, 0, 3, 0, 0),
            (9, 8, 0, 0, 1, 0),
            (9, 8, 0, 0, 2, 0),
            (9, 14, 0, 2, 0, 0),
        )
        for codes in coordinates:
            with self.subTest(codes=codes):
                raw = oracle.encode_reference_record(self.template, codes)
                verified = oracle.verify_record(raw, self.template)
                self.assertEqual(verified.codes, codes)
                self.assertEqual(verified.ordinal, oracle.rank_coordinate(codes))
                self.assertEqual(len(verified.normalized_sha256), 64)

    def test_four_valued_truth_tables_are_complete(self) -> None:
        expected_and = {
            "T": {"T": "T", "F": "F", "U": "U", "B": "B"},
            "F": {"T": "F", "F": "F", "U": "F", "B": "F"},
            "U": {"T": "U", "F": "F", "U": "U", "B": "F"},
            "B": {"T": "B", "F": "F", "U": "F", "B": "B"},
        }
        expected_or = {
            "T": {"T": "T", "F": "T", "U": "T", "B": "T"},
            "F": {"T": "T", "F": "F", "U": "U", "B": "B"},
            "U": {"T": "T", "F": "U", "U": "U", "B": "T"},
            "B": {"T": "T", "F": "B", "U": "T", "B": "B"},
        }
        for left, right in itertools.product(oracle.TRUTHS, repeat=2):
            self.assertEqual(oracle.truth_all([left, right]), expected_and[left][right])
            self.assertEqual(oracle.truth_any([left, right]), expected_or[left][right])
        self.assertEqual(
            [oracle.truth_not(value) for value in oracle.TRUTHS],
            ["F", "T", "U", "B"],
        )

    def test_deadline_and_lifecycle_uncertainty_are_executed(self) -> None:
        deadline = self.reference(oracle.unrank_ordinal(1840))["generator_claim"]
        self.assertIn("unknown_deadline", deadline["blocker_codes"])
        self.assertIn("unknown_lifecycle", deadline["blocker_codes"])
        self.assertEqual(deadline["status"], "unresolved")
        self.assertEqual(deadline["fallback"], "escalate")

        ordinary = self.reference(oracle.unrank_ordinal(48))["generator_claim"]
        self.assertIn("unknown_lifecycle", ordinary["blocker_codes"])
        self.assertNotIn("unknown_deadline", ordinary["blocker_codes"])

        timely = self.reference((0, 7, 0, 1, 0, 0))["generator_claim"]
        late = self.reference((0, 7, 0, 2, 0, 0))["generator_claim"]
        self.assertIn("n0", timely["satisfied_norm_ids"])
        self.assertIn("n1", timely["violated_norm_ids"])
        self.assertIn("n0", late["violated_norm_ids"])
        self.assertIn("n1", late["violated_norm_ids"])

    def test_ctd_repair_gate_and_final_availability(self) -> None:
        active = self.reference((0, 8, 0, 0, 1, 0))["generator_claim"]
        self.assertIn("n0", active["violated_norm_ids"])
        self.assertEqual(active["activated_repair_norm_ids"], ["n1", "n2"])
        self.assertEqual(active["repair_availability"][0]["availability"], "active")
        self.assertEqual(active["status"], "resolved")

        defeated = self.reference(oracle.unrank_ordinal(2056))["generator_claim"]
        family = defeated["repair_availability"][0]
        self.assertEqual(family["provider_norm_id"], "n1")
        self.assertEqual(family["provider_disposition"], "defeated")
        self.assertEqual(family["availability"], "defeated")
        self.assertIn("repair_unavailable", defeated["blocker_codes"])
        self.assertEqual(defeated["fallback"], "escalate")

        uncertain = self.reference((0, 8, 2, 3, 0, 0))["generator_claim"]
        self.assertIn("unknown_primary_violation", uncertain["blocker_codes"])
        self.assertIn("unknown_repair_availability", uncertain["blocker_codes"])
        self.assertEqual(
            uncertain["repair_availability"][0]["availability"],
            "blocked_unknown",
        )

    def test_unknown_and_inconsistent_evidence_never_authorize(self) -> None:
        for topology, evidence, state, resolution, defeater in itertools.product(
            range(16), (2, 3), range(4), range(4), range(4)
        ):
            core, _ = oracle.compile_core(
                self.template,
                (0, topology, evidence, state, resolution, defeater),
            )
            result = oracle.evaluate_core(core)
            with self.subTest(
                topology=topology,
                evidence=evidence,
                state=state,
                resolution=resolution,
                defeater=defeater,
            ):
                self.assertEqual(result["status"], "unresolved")
                self.assertIn(result["fallback"], {"abstain", "escalate"})
                self.assertEqual(result["executable_required_action_ids"], [])
                self.assertEqual(result["executable_permitted_action_ids"], [])
                self.assertEqual(result["admissible_action_ids"], [])

    def test_active_priority_cycles_block_but_dormant_cycles_do_not(self) -> None:
        for topology in range(16):
            active = self.reference((0, topology, 0, 0, 3, 0))["generator_claim"]
            self.assertIn("relevant_priority_cycle", active["blocker_codes"])
            self.assertEqual(active["fallback"], "escalate")
            dormant_zero = self.reference((0, topology, 0, 1, 0, 0))
            dormant_cycle = self.reference((0, topology, 0, 1, 3, 0))
            left = oracle.normalize_result(
                dormant_zero["generator_claim"], dormant_zero["semantic_core"]
            )
            right = oracle.normalize_result(
                dormant_cycle["generator_claim"], dormant_cycle["semantic_core"]
            )
            self.assertEqual(left, right)

    def test_exact_normalization_counts_for_one_domain(self) -> None:
        hashes: dict[tuple[int, int, int, int, int], str] = {}
        for topology, evidence, state, resolution, defeater in itertools.product(
            range(16), range(4), range(4), range(4), range(4)
        ):
            core, _ = oracle.compile_core(
                self.template,
                (0, topology, evidence, state, resolution, defeater),
            )
            normalized = oracle.normalize_result(oracle.evaluate_core(core), core)
            hashes[(topology, evidence, state, resolution, defeater)] = (
                oracle.canonical_hash(normalized)
            )
        self.assertEqual(len(set(hashes.values())), 322)

        counts = {axis: Counter() for axis in oracle.AXES}
        for axis_offset, axis in enumerate(oracle.AXES):
            other_indices = [index for index in range(4) if index != axis_offset]
            for topology in range(16):
                for held in itertools.product(range(4), repeat=3):
                    base = [0, 0, 0, 0]
                    for index, value in zip(other_indices, held, strict=True):
                        base[index] = value
                    variants = []
                    for value in range(4):
                        coordinate = list(base)
                        coordinate[axis_offset] = value
                        variants.append(hashes[(topology, *coordinate)])
                    for left, right in itertools.combinations(range(4), 2):
                        counts[axis][
                            "EFFECT"
                            if variants[left] != variants[right]
                            else "INVARIANT"
                        ] += 1
        self.assertEqual(counts["evidence"], Counter(EFFECT=5696, INVARIANT=448))
        self.assertEqual(counts["state"], Counter(EFFECT=4240, INVARIANT=1904))
        self.assertEqual(counts["resolution"], Counter(EFFECT=96, INVARIANT=6048))
        self.assertEqual(counts["defeater"], Counter(EFFECT=1068, INVARIANT=5076))
        self.assertEqual(sum(row["EFFECT"] for row in counts.values()), 11_100)
        self.assertEqual(sum(row["INVARIANT"] for row in counts.values()), 13_476)

    def test_alpha_normalization_erases_norm_ids(self) -> None:
        core, _ = oracle.compile_core(self.template, (0, 8, 0, 0, 1, 0))
        original = oracle.normalize_result(oracle.evaluate_core(core), core)
        renamed = rename_norms(core, {"n0": "q2", "n1": "q0", "n2": "q1"})
        oracle._validate_core_shape(renamed)
        renamed_result = oracle.evaluate_core(renamed)
        self.assertEqual(original, oracle.normalize_result(renamed_result, renamed))

    def test_masked_inputs_are_invariant_but_operational_changes_are_effects(
        self,
    ) -> None:
        def normalized(codes: tuple[int, int, int, int, int, int]) -> str:
            core, _ = oracle.compile_core(self.template, codes)
            return oracle.canonical_hash(
                oracle.normalize_result(oracle.evaluate_core(core), core)
            )

        self.assertEqual(
            normalized((0, 0, 0, 1, 0, 0)),
            normalized((0, 0, 0, 1, 3, 0)),
        )
        self.assertEqual(
            normalized((0, 0, 1, 0, 0, 0)),
            normalized((0, 0, 1, 0, 0, 3)),
        )
        self.assertEqual(
            normalized((0, 1, 1, 0, 0, 0)),
            normalized((0, 1, 1, 3, 0, 0)),
        )
        self.assertNotEqual(
            normalized((0, 0, 0, 0, 0, 0)),
            normalized((0, 0, 0, 0, 1, 0)),
        )
        self.assertNotEqual(
            normalized((0, 0, 0, 0, 0, 0)),
            normalized((0, 0, 0, 3, 0, 0)),
        )

    def test_counterfactual_receipts_rebuild_and_classify(self) -> None:
        effect_before = self.verify(self.reference((0, 0, 0, 0, 0, 0)))
        effect_after = self.verify(self.reference((0, 0, 0, 0, 1, 0)))
        effect = oracle.counterfactual_receipt(
            effect_before,
            effect_after,
            axis="resolution",
            template=self.template,
            oracle_source_sha256="1" * 64,
            evaluator_source_sha256="2" * 64,
        )
        self.assertEqual(effect["classification"], "EFFECT")
        self.assertTrue(
            all(
                path.startswith("$.semantic_core.priority_edges")
                for path in effect["changed_semantic_paths"]
            )
        )
        receipt_hash = effect.pop("receipt_sha256")
        self.assertEqual(receipt_hash, oracle.canonical_hash(effect))
        receipt_id = effect.pop("receipt_id")
        self.assertEqual(receipt_id, oracle.canonical_hash(effect))

        invariant_before = self.verify(self.reference((0, 0, 0, 1, 0, 0)))
        invariant_after = self.verify(self.reference((0, 0, 0, 1, 3, 0)))
        invariant = oracle.counterfactual_receipt(
            invariant_before,
            invariant_after,
            axis="resolution",
            template=self.template,
            oracle_source_sha256="1" * 64,
            evaluator_source_sha256="2" * 64,
        )
        self.assertEqual(invariant["classification"], "INVARIANT")

        wrong_axis = self.verify(self.reference((0, 0, 1, 1, 0, 0)))
        with self.assertRaisesRegex(oracle.OracleReject, "not_one_axis_pair"):
            oracle.counterfactual_receipt(
                invariant_before,
                wrong_axis,
                axis="resolution",
                template=self.template,
            )

    def test_counterfactual_receipts_reject_forged_verified_cases(self) -> None:
        before = self.verify(self.reference((0, 0, 0, 0, 0, 0)))
        after = self.verify(self.reference((0, 0, 0, 0, 1, 0)))
        for field, value in (
            ("normalized_sha256", before.normalized_sha256),
            ("result_sha256", "0" * 64),
            ("record_sha256", "1" * 64),
        ):
            forged = replace(after, **{field: value})
            with (
                self.subTest(field=field),
                self.assertRaisesRegex(oracle.OracleReject, "verified_case_tamper"),
            ):
                oracle.counterfactual_receipt(
                    before,
                    forged,
                    axis="resolution",
                    template=self.template,
                )

    def test_analyzer_reconciles_once_and_rejects_forged_verified_case(self) -> None:
        before = self.verify(self.reference((0, 0, 0, 0, 0, 0)))
        after = self.verify(self.reference((0, 0, 0, 0, 0, 1)))
        forged = replace(after, result_sha256="0" * 64)
        with mock.patch.object(
            oracle, "_reference_case", wraps=oracle._reference_case
        ) as rebuild:
            with self.assertRaisesRegex(oracle.OracleReject, "verified_case_tamper"):
                oracle.analyze_verified_cases(
                    (before, forged),
                    self.template,
                    enumerate_counterfactuals=False,
                )
            self.assertEqual(rebuild.call_count, 2)

    def test_private_receipt_path_uses_only_reconciled_cases(self) -> None:
        before = self.verify(self.reference((0, 0, 0, 0, 0, 0)))
        after = self.verify(self.reference((0, 0, 0, 0, 1, 0)))
        reconciled = oracle._reconcile_verified_cases((before, after), self.template)
        with mock.patch.object(
            oracle,
            "_reference_case",
            side_effect=AssertionError("receipt path rebuilt an admitted endpoint"),
        ):
            receipt = oracle._counterfactual_receipt_reconciled(
                reconciled,
                before.ordinal,
                after.ordinal,
                axis="resolution",
                template=self.template,
                oracle_source_sha256="1" * 64,
                evaluator_source_sha256="2" * 64,
            )
        self.assertEqual(receipt["classification"], "EFFECT")

    def test_axis_dependency_closure_is_field_exact(self) -> None:
        topology = self.template.data["topology_programs"][0]

        legitimate_codes = {
            "evidence": ((0, 0, 0, 0, 0, 0), (0, 0, 1, 0, 0, 0)),
            "state": ((0, 0, 0, 0, 0, 0), (0, 0, 0, 3, 0, 0)),
            "resolution": ((0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 1, 0)),
            "defeater": ((0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 1)),
        }
        for axis, (before_codes, after_codes) in legitimate_codes.items():
            before_core, _ = oracle.compile_core(self.template, before_codes)
            after_core, _ = oracle.compile_core(self.template, after_codes)
            changed = sorted(
                oracle._all_differences(before_core, after_core, "$.semantic_core")
            )
            with self.subTest(axis=axis):
                self.assertTrue(
                    oracle._axis_change_is_closed(
                        axis, changed, before_core, after_core, topology
                    )
                )

        before_core, _ = oracle.compile_core(self.template, (0, 0, 0, 0, 0, 0))
        hostile_state = copy.deepcopy(before_core)
        hostile_state["norms"][0]["operator"] = "F"
        state_paths = sorted(
            oracle._all_differences(before_core, hostile_state, "$.semantic_core")
        )
        self.assertFalse(
            oracle._axis_change_is_closed(
                "state", state_paths, before_core, hostile_state, topology
            )
        )

        hostile_defeater = copy.deepcopy(before_core)
        defeater_fact = next(
            fact
            for fact in hostile_defeater["facts"]
            if fact["derivation_rule_id"] == "defeater_axis_v1"
        )
        defeater_fact["derivation_rule_id"] = "hostile_rule"
        defeater_paths = sorted(
            oracle._all_differences(before_core, hostile_defeater, "$.semantic_core")
        )
        self.assertFalse(
            oracle._axis_change_is_closed(
                "defeater",
                defeater_paths,
                before_core,
                hostile_defeater,
                topology,
            )
        )

    def test_deadline_shape_rejections_use_frozen_error_codes(self) -> None:
        baseline = self.reference((0, 7, 0, 0, 0, 0))

        unsupported_operator = copy.deepcopy(baseline)
        deadline_norm = next(
            norm
            for norm in unsupported_operator["semantic_core"]["norms"]
            if norm["lifecycle"]["kind"] == "deadline"
        )
        deadline_norm["operator"] = "P"
        seal_record(unsupported_operator)
        self.assert_rejects(unsupported_operator, "unsupported_deadline_operator")

        invalid_state = copy.deepcopy(baseline)
        deadline_norm = next(
            norm
            for norm in invalid_state["semantic_core"]["norms"]
            if norm["lifecycle"]["kind"] == "deadline"
        )
        deadline_norm["lifecycle"]["value"] = "active"
        seal_record(invalid_state)
        self.assert_rejects(invalid_state, "invalid_deadline_state")

    def test_exact_decoder_kills_hostile_json_encodings(self) -> None:
        with self.assertRaisesRegex(oracle.OracleReject, "duplicate_json_key"):
            oracle.parse_json_exact(
                b'{"schema":"a","schema":"b"}', canonical=True, max_bytes=100
            )
        with self.assertRaisesRegex(oracle.OracleReject, "json_float_forbidden"):
            oracle.parse_json_exact(b'{"x":1.0}', canonical=True, max_bytes=100)
        with self.assertRaisesRegex(oracle.OracleReject, "json_nonfinite_forbidden"):
            oracle.parse_json_exact(b'{"x":NaN}', canonical=True, max_bytes=100)
        raw = oracle.encode_reference_record(self.template, (0, 0, 0, 0, 0, 0))
        with self.assertRaisesRegex(oracle.OracleReject, "noncanonical_bytes"):
            oracle.verify_record(raw + b"\n", self.template)
        with self.assertRaisesRegex(oracle.OracleReject, "non_ascii_json"):
            oracle.parse_json_exact(b'{"x":"\xff"}', canonical=True, max_bytes=100)

    def test_unknown_missing_and_wrong_type_fields_are_killed(self) -> None:
        baseline = self.reference((0, 0, 0, 0, 0, 0))

        extra = copy.deepcopy(baseline)
        extra["unexpected"] = 1
        self.assert_rejects(extra, "unknown_field")

        missing = copy.deepcopy(baseline)
        missing.pop("authority")
        self.assert_rejects(missing, "missing_field")

        boolean_ordinal = copy.deepcopy(baseline)
        boolean_ordinal["ordinal"] = False
        self.assert_rejects(boolean_ordinal, "wrong_type")

        numeric_ordinal = copy.deepcopy(baseline)
        numeric_ordinal["ordinal"] = "0"
        self.assert_rejects(numeric_ordinal, "wrong_type")

        nested_extra = copy.deepcopy(baseline)
        nested_extra["semantic_core"]["norms"][0]["implicit_delegation"] = True
        self.assert_rejects(nested_extra, "unknown_field")

        reordered = copy.deepcopy(baseline)
        reordered["semantic_core"]["actors"].reverse()
        self.assert_rejects(reordered, "noncanonical_order")

    def test_authority_profile_coordinate_and_hash_mutants_are_killed(self) -> None:
        baseline = self.reference((0, 0, 0, 0, 0, 0))

        authority = copy.deepcopy(baseline)
        authority["authority"]["may_authorize_external_effects"] = True
        self.assert_rejects(authority, "authority_boundary_mismatch")

        authority_alias = copy.deepcopy(baseline)
        authority_alias["authority"]["may_authorize_external_effects"] = 0
        self.assert_rejects(authority_alias, "wrong_type")

        profile = copy.deepcopy(baseline)
        profile["profile_ref"]["semantics_spec_sha256"] = "0" * 64
        profile["record_sha256"] = oracle.canonical_hash(
            {key: value for key, value in profile.items() if key != "record_sha256"}
        )
        self.assert_rejects(profile, "profile_hash_mismatch")

        coordinate = copy.deepcopy(baseline)
        coordinate["coordinate"]["evidence_code"] = 1
        coordinate["record_sha256"] = oracle.canonical_hash(
            {key: value for key, value in coordinate.items() if key != "record_sha256"}
        )
        self.assert_rejects(coordinate, "coordinate_mismatch")

        ordinal = copy.deepcopy(baseline)
        ordinal["ordinal"] = 1
        ordinal["record_sha256"] = oracle.canonical_hash(
            {key: value for key, value in ordinal.items() if key != "record_sha256"}
        )
        self.assert_rejects(ordinal, "ordinal_mismatch")

        core_hash = copy.deepcopy(baseline)
        core_hash["semantic_core_sha256"] = "0" * 64
        self.assert_rejects(core_hash, "semantic_core_hash_mismatch")

        record_hash = copy.deepcopy(baseline)
        record_hash["record_sha256"] = "0" * 64
        self.assert_rejects(record_hash, "record_hash_mismatch")

    def test_typed_reference_payload_and_owner_mutants_are_killed(self) -> None:
        baseline = self.reference((0, 0, 0, 0, 0, 0))

        wrong_owner = copy.deepcopy(baseline)
        wrong_owner["semantic_core"]["norms"][0]["subject_id"] = wrong_owner[
            "semantic_core"
        ]["actors"][0]["id"]
        if (
            wrong_owner["semantic_core"]["norms"][0]["subject_id"]
            == wrong_owner["semantic_core"]["actions"][0]["actor_id"]
        ):
            wrong_owner["semantic_core"]["norms"][0]["subject_id"] = wrong_owner[
                "semantic_core"
            ]["actors"][1]["id"]
        seal_record(wrong_owner)
        self.assert_rejects(wrong_owner, "wrong_owner_reference")

        dangling = copy.deepcopy(baseline)
        dangling["semantic_core"]["norms"][0]["defeater"]["fact_id"] = "missing_fact"
        seal_record(dangling)
        self.assert_rejects(dangling, "wrong_sort_reference")

        state_mirror = copy.deepcopy(baseline)
        state_mirror["semantic_core"]["norms"][0]["condition_refs"][-1]["id"] = "n1"
        state_mirror["semantic_core"]["norms"][0]["condition_refs"].sort(
            key=lambda item: (item["kind"], item["id"])
        )
        seal_record(state_mirror)
        self.assert_rejects(state_mirror, "state_mirror_mismatch")

        payload = copy.deepcopy(baseline)
        payload["semantic_core"]["evidence"][0]["payload_sha256"] = "0" * 64
        seal_record(payload)
        self.assert_rejects(payload, "payload_hash_mismatch")

    def test_semantic_and_generator_claim_mutants_survive_rehashing_but_not_oracle(
        self,
    ) -> None:
        baseline = self.reference((0, 0, 0, 0, 0, 0))

        semantic = copy.deepcopy(baseline)
        derived = next(
            fact
            for fact in semantic["semantic_core"]["facts"]
            if fact["derivation_rule_id"] != "defeater_axis_v1"
        )
        derived["truth"] = "F" if derived["truth"] != "F" else "T"
        seal_record(semantic, replace_claim=True)
        with self.assertRaises(oracle.OracleReject) as caught:
            self.verify(semantic)
        self.assertIn(
            caught.exception.code,
            {"semantic_core_mismatch", "state_axis_ambiguous"},
        )

        claim = copy.deepcopy(baseline)
        claim["generator_claim"]["fallback"] = "abstain"
        claim["generator_claim"].pop("result_sha256")
        claim["generator_claim"]["result_sha256"] = oracle.canonical_hash(
            claim["generator_claim"]
        )
        claim["record_sha256"] = oracle.canonical_hash(
            {key: value for key, value in claim.items() if key != "record_sha256"}
        )
        self.assert_rejects(claim, "generator_claim_mismatch")

    def test_partial_analyzer_is_honestly_quarantined(self) -> None:
        cases = [
            self.verify(self.reference((0, 0, 0, 0, 0, 0))),
            self.verify(self.reference((0, 0, 0, 0, 0, 1))),
        ]
        report = oracle.analyze_verified_cases(
            cases,
            self.template,
            enumerate_counterfactuals=False,
        )
        gates = {row["gate_id"]: row["status"] for row in report["gate_results"]}
        self.assertEqual(gates["G01"], "FAIL")
        self.assertEqual(gates["G03"], "FAIL")
        self.assertEqual(gates["G05"], "FAIL")
        self.assertEqual(gates["G07"], "FAIL")
        self.assertEqual(gates["G10"], "FAIL")
        self.assertEqual(gates["G13"], "FAIL")
        self.assertEqual(gates["G04"], "SKIP")
        self.assertEqual(gates["G11"], "SKIP")
        self.assertEqual(gates["G12"], "SKIP")
        self.assertEqual(report["promotion"]["assigned_label"], "QUARANTINED_CORPUS")

    def test_complete_but_unbound_gate_precheck_cannot_pass(self) -> None:
        self.assertEqual(
            oracle.unbound_evidence_gate_status(
                corpus_complete=True, precheck_pass=True
            ),
            "SKIP",
        )
        self.assertEqual(
            oracle.unbound_evidence_gate_status(
                corpus_complete=True, precheck_pass=False
            ),
            "FAIL",
        )
        self.assertEqual(
            oracle.unbound_evidence_gate_status(
                corpus_complete=False, precheck_pass=True
            ),
            "FAIL",
        )

    def test_analyze_report_option_is_atomic_canonical_and_no_overwrite(self) -> None:
        report: dict[str, object] = {
            "metrics": {"accepted_records": 2},
            "promotion": {"assigned_label": "QUARANTINED_CORPUS"},
            "counterfactuals": {"receipt_set_root": "2" * 64},
        }
        report["report_sha256"] = oracle.canonical_hash(report)
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "oracle-report.json"
            argv = [
                "--template",
                str(TEMPLATE_PATH),
                "--semantics",
                str(SEMANTICS_PATH),
                "analyze",
                "unused.jsonl",
                "--skip-counterfactuals",
                "--report",
                str(output),
            ]
            stdout = io.StringIO()
            with (
                mock.patch.object(
                    oracle, "analyze_raw_records", return_value=report
                ) as analyze,
                redirect_stdout(stdout),
            ):
                self.assertEqual(oracle.main(argv), 0)
                canonical_report = output.read_bytes()
                self.assertEqual(canonical_report, oracle.canonical_bytes(report))
                summary = json.loads(stdout.getvalue())
                self.assertEqual(summary["status"], "PASS")
                self.assertEqual(summary["report_sha256"], report["report_sha256"])
                self.assertEqual(summary["counterfactual_receipt_set_root"], "2" * 64)
                with self.assertRaisesRegex(oracle.OracleReject, "report_exists"):
                    oracle.main(argv)
                analyze.assert_called_once()
            self.assertEqual(output.read_bytes(), canonical_report)

    def test_oracle_dependency_closure_does_not_import_generator(self) -> None:
        tree = ast.parse(ORACLE_PATH.read_text(encoding="utf-8"))
        imported: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.append(node.module)
        self.assertFalse(
            any(
                name.endswith("synthetic_deontic_luna_v1")
                or "synthetic_deontic_luna_v1." in name
                for name in imported
            ),
            imported,
        )


if __name__ == "__main__":
    unittest.main()
