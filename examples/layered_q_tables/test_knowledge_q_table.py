from __future__ import annotations

import copy
import hashlib
import tempfile
import unittest
from pathlib import Path

import numpy as np

from examples.layered_q_tables.knowledge_q_table import (
    ABSTAIN_ACTION_INDEX,
    ABSTAIN_MASK,
    ACTION_NAMES,
    ALL_ACTION_MASK,
    EVIDENCE_STATUS_COMPLETE,
    EVIDENCE_STATUS_INCOMPLETE,
    EVIDENCE_STATUS_NON_APPLICABLE,
    EVIDENCE_STATUS_PADDED,
    NAVIGATION_MASK,
    PROFILES,
    RESOLVE_ACTION_INDEX,
    DeonticAdapterError,
    DeonticConstraints,
    EvidenceCompletionDeonticAdapter,
    FixtureDeonticAdapter,
    SnapshotValidationError,
    UtilityModel,
    _build_cli_parser,
    _cli_adapter,
    adapt_wikidata_snapshot,
    canonical_json_bytes,
    compile_model,
    fixture_config,
    generate_table,
    query,
    verify_table,
)


def _decision(decision_id: str, evidence_bits: int) -> dict[str, object]:
    return {
        "decision_id": decision_id,
        "applicability": {"kind": "always"},
        "obligation_rule_ids": [f"obligation:{decision_id}"],
        "goal": {
            "resolution_alternatives": [
                {
                    "id": f"resolve:{decision_id}",
                    "label": "resolve the bounded alternative",
                }
            ],
            "abstain_or_escalate": {
                "id": "abstain_or_escalate",
                "label": "abstain and request review",
            },
        },
        "required_evidence_bits": evidence_bits,
        "review_triggers": ["missing evidence", "adapter review"],
        "provenance_refs": [f"fixture:{decision_id}"],
    }


def fixture_snapshot() -> tuple[dict[str, object], list[dict[str, object]]]:
    nodes = [
        {
            "id": "oewn-00000001-n",
            "label": "one",
            "description": "fixture node one",
            "provenance": {"source_record": "00000001-n"},
        },
        {
            "id": "oewn-00000002-n",
            "label": "two",
            "description": "fixture node two",
            "provenance": {"source_record": "00000002-n"},
        },
        {
            "id": "oewn-00000003-n",
            "label": "three",
            "description": "fixture node three",
            "provenance": {"source_record": "00000003-n"},
        },
    ]
    edges = [
        {
            "source": "oewn-00000001-n",
            "relation": "hypernym",
            "target": "oewn-00000002-n",
            "source_direction": "wordnet_source_to_target",
            "evidence_bits": 1,
        },
        {
            "source": "oewn-00000002-n",
            "relation": "entails",
            "target": "oewn-00000003-n",
            "source_direction": "wordnet_source_to_target",
            "evidence_bits": 2,
        },
    ]
    graph = {"nodes": nodes, "edges": edges}
    graph_hash = hashlib.sha256(canonical_json_bytes(graph)).hexdigest()
    snapshot: dict[str, object] = {
        "schema": "glassmind-canonical-knowledge-v1",
        "provenance": {
            "source_name": "Open English WordNet fixture",
            "source_url": "fixture:wordnet",
            "retrieved_at": "2026-01-01T00:00:00Z",
            "canonical_graph_sha256": graph_hash,
            "license": "CC-BY-4.0",
            "nonclaims": ["fixture only", "graph edges are not proofs"],
        },
        "counts": {"nodes": 3, "edges": 2},
        "graph": graph,
        "missing_ids": [],
        "truncated": False,
    }
    return snapshot, [_decision("D0", 1), _decision("D1", 3)]


def evidence_adapter(
    *,
    logic_semantics: str = "deontic-kernel-evidence-completion-v1",
    profile: str = "production-fixture-v1",
    logic_digest: str = "1a95da0066a4bdb8a8fb6cfde4629eab95ac35d3b814bfcaf21e10328ed355df",
    profile_digest: str = "4046ef1d6377f9eed77d86b76f7f813268d51bef6af8b2fd5a93c355b8c51efa",
    evidence_digest: str = "a" * 64,
) -> EvidenceCompletionDeonticAdapter:
    return EvidenceCompletionDeonticAdapter(
        logic_semantics=logic_semantics,
        logic_semantics_sha256=logic_digest,
        profile=profile,
        profile_sha256=profile_digest,
        esso_evidence_hashes={
            "esso-ir": evidence_digest,
            "esso-model": "b" * 64,
        },
    )


class _PermissiveAdapter:
    def constraints(self, state):
        del state
        return DeonticConstraints(ALL_ACTION_MASK, 0)


class _MalformedAdapter:
    def constraints(self, state):
        del state
        return {"permitted_mask": 1, "forbidden_mask": 0}


class _ConflictAdapter:
    def constraints(self, state):
        del state
        reasons = [[] for _ in ACTION_NAMES]
        reasons[ABSTAIN_ACTION_INDEX] = ["kernel:conflict-quarantine"]
        return {
            "action_mask": tuple(
                index == ABSTAIN_ACTION_INDEX for index in range(len(ACTION_NAMES))
            ),
            "status": "conflict",
            "reason_ids": reasons,
        }


class KnowledgeQTableTests(unittest.TestCase):
    def setUp(self) -> None:
        self.snapshot, self.decisions = fixture_snapshot()
        self.config = fixture_config(layers=4, decisions=2, node_slots=4, chunk_size=3)
        self.adapter = FixtureDeonticAdapter()

    def _generate(
        self, directory: str, name: str = "table.npy", adapter=None, utility=None
    ):
        table = Path(directory) / name
        manifest = Path(directory) / (name + ".manifest.json")
        value = generate_table(
            table,
            self.snapshot,
            self.decisions,
            config=self.config,
            adapter=self.adapter if adapter is None else adapter,
            utility=UtilityModel() if utility is None else utility,
            manifest=manifest,
        )
        return table, manifest, value

    def _targeted_decisions(self) -> list[dict[str, object]]:
        decisions = copy.deepcopy(self.decisions)
        decisions[0]["applicability"] = {
            "kind": "node_ids",
            "node_ids": ["oewn-00000001-n"],
        }
        return decisions

    def test_profile_shape_arithmetic_is_exact(self) -> None:
        self.assertEqual(PROFILES["public"].shape, (256, 6144, 8))
        self.assertEqual(PROFILES["public"].raw_data_bytes, 50_331_648)
        self.assertEqual(PROFILES["full"].shape, (256, 65_536, 8))
        self.assertEqual(PROFILES["full"].raw_data_bytes, 536_870_912)
        self.assertEqual(self.config.state_count, 2 * 4 * 4)
        self.assertEqual(len(ACTION_NAMES), 8)

    def test_source_neutral_ids_and_directional_predicate_are_preserved(self) -> None:
        model = compile_model(
            self.snapshot, self.decisions, config=self.config, adapter=self.adapter
        )
        self.assertEqual(model.node_ids[0], "oewn-00000001-n")
        forward = model.navigation[0][0]
        self.assertEqual(forward.relation, "hypernym")
        self.assertEqual(forward.relation_source_id, "oewn-00000001-n")
        self.assertEqual(forward.relation_target_id, "oewn-00000002-n")
        reverse = next(
            slot
            for slot in model.navigation[1]
            if slot and slot.browse_direction == "reverse"
        )
        self.assertEqual(reverse.source_id, "oewn-00000002-n")
        self.assertEqual(reverse.target_id, "oewn-00000001-n")
        self.assertEqual(reverse.relation_source_id, "oewn-00000001-n")
        self.assertEqual(reverse.relation_target_id, "oewn-00000002-n")

    def test_wikidata_adapter_maps_qids_and_pids_at_the_boundary(self) -> None:
        legacy = {
            "snapshot_version": 1,
            "provenance": {
                "endpoint": "fixture:wikidata",
                "license": "CC0-1.0",
                "nonclaims": ["fixture claims are not proofs"],
            },
            "graph": {
                "nodes": [
                    {"qid": "Q1", "label": "one", "revision": {"lastrevid": 1}},
                    {"qid": "Q2", "label": "two", "revision": {"lastrevid": 2}},
                ],
                "edges": [{"source": "Q1", "pid": "P31", "target": "Q2"}],
            },
            "missing_qids": [],
            "truncated": False,
        }
        neutral = adapt_wikidata_snapshot(legacy)
        self.assertEqual(neutral["schema"], "glassmind-canonical-knowledge-v1")
        self.assertEqual(neutral["graph"]["nodes"][0]["id"], "Q1")
        self.assertEqual(neutral["graph"]["edges"][0]["relation"], "P31")
        self.assertEqual(
            neutral["graph"]["edges"][0]["source_direction"],
            "wikidata_claim_source_to_target",
        )

    def test_generation_is_byte_reproducible_and_manifest_counts_padding(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first, first_manifest, first_value = self._generate(directory, "first.npy")
            second, _, second_value = self._generate(directory, "second.npy")
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(
                first_value["output"]["sha256"], second_value["output"]["sha256"]
            )
            self.assertEqual(
                first_value["output"]["raw_data_bytes"], self.config.raw_data_bytes
            )
            self.assertEqual(first_value["padding_counts"]["padded_graph_slots"], 1)
            self.assertEqual(
                first_value["truncation_counts"][
                    "navigation_candidates_dropped_after_six_slots"
                ],
                0,
            )
            self.assertEqual(
                first_manifest.read_bytes(), canonical_json_bytes(first_value)
            )

    def test_successful_resolution_and_reverse_browse_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            table, manifest, _ = self._generate(directory)
            receipt = query(
                table,
                self.snapshot,
                decision_id="D0",
                start_node_id="oewn-00000001-n",
                layer=3,
                required_decisions=self.decisions,
                config=self.config,
                adapter=self.adapter,
                manifest=manifest,
            )
            self.assertEqual(receipt["terminal"]["kind"], "resolution")
            self.assertEqual(receipt["path"][0]["action"], "navigate_0")
            self.assertEqual(
                receipt["evidence_traversed"][0]["browse_direction"], "forward"
            )
            self.assertIn("fixture:navigate_0:allow", receipt["deontic_reason_ids"])
            self.assertTrue(receipt["finite_trace_gate"]["passed"])

            reverse_receipt = query(
                table,
                self.snapshot,
                decision_id="D0",
                start_node_id="oewn-00000002-n",
                layer=3,
                required_decisions=self.decisions,
                config=self.config,
                adapter=self.adapter,
            )
            self.assertEqual(reverse_receipt["terminal"]["kind"], "resolution")
            self.assertTrue(
                any(
                    item["browse_direction"] == "reverse"
                    for item in reverse_receipt["evidence_traversed"]
                )
            )

    def test_required_evidence_precondition_controls_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            table, _, _ = self._generate(directory)
            missing = query(
                table,
                self.snapshot,
                decision_id="D0",
                start_node_id="oewn-00000002-n",
                evidence_mask=0,
                layer=0,
                required_decisions=self.decisions,
                config=self.config,
                adapter=self.adapter,
            )
            self.assertEqual(missing["terminal"]["kind"], "abstain_or_escalate")
            present = query(
                table,
                self.snapshot,
                decision_id="D0",
                start_node_id="oewn-00000002-n",
                evidence_mask=1,
                layer=0,
                required_decisions=self.decisions,
                config=self.config,
                adapter=self.adapter,
            )
            self.assertEqual(present["terminal"]["kind"], "resolution")

    def test_forbidden_action_is_not_selected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            adapter = FixtureDeonticAdapter(["navigate_0"])
            table, _, _ = self._generate(directory, adapter=adapter)
            receipt = query(
                table,
                self.snapshot,
                decision_id="D0",
                start_node_id="oewn-00000001-n",
                layer=3,
                required_decisions=self.decisions,
                config=self.config,
                adapter=adapter,
            )
            self.assertEqual(receipt["terminal"]["kind"], "abstain_or_escalate")
            self.assertEqual(receipt["chosen_action"], "abstain_or_escalate")

    def test_conflict_status_is_quarantined_before_q_ranking(self) -> None:
        adapter = _ConflictAdapter()
        model = compile_model(
            self.snapshot, self.decisions, config=self.config, adapter=adapter
        )
        self.assertTrue(all(status == "conflict" for status in model.deontic_statuses))
        self.assertTrue(
            np.all(np.flatnonzero(model.base_allowed[0]) == [ABSTAIN_ACTION_INDEX])
        )
        with tempfile.TemporaryDirectory() as directory:
            table, _, manifest = self._generate(directory, adapter=adapter)
            receipt = query(
                table,
                self.snapshot,
                decision_id="D0",
                start_node_id="oewn-00000001-n",
                layer=3,
                required_decisions=self.decisions,
                config=self.config,
                adapter=adapter,
            )
            self.assertEqual(receipt["chosen_action"], "abstain_or_escalate")
            self.assertEqual(receipt["deontic_statuses"], ["conflict"])
            self.assertGreater(manifest["counts"]["deontic_conflict_states"], 0)

    def test_obligatory_mask_takes_precedence_over_permitted_actions(self) -> None:
        constraint = DeonticConstraints.from_value(
            {
                "action_mask": tuple(True for _ in ACTION_NAMES),
                "obligatory_action_mask": tuple(
                    index == ABSTAIN_ACTION_INDEX for index in range(len(ACTION_NAMES))
                ),
                "reason_ids": ["kernel:obligation"],
            }
        )
        self.assertEqual(constraint.allowed_mask, 1 << ABSTAIN_ACTION_INDEX)
        self.assertEqual(constraint.obligatory_mask, 1 << ABSTAIN_ACTION_INDEX)

    def test_utility_model_is_separately_hashed_and_changes_q_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            default_table, _, default_manifest = self._generate(
                directory, "default.npy"
            )
            changed = UtilityModel(resolve_reward=0.5)
            changed_table, _, changed_manifest = self._generate(
                directory, "changed.npy", utility=changed
            )
            self.assertNotEqual(default_table.read_bytes(), changed_table.read_bytes())
            self.assertNotEqual(
                default_manifest["input"]["utility_model_sha256"],
                changed_manifest["input"]["utility_model_sha256"],
            )
            self.assertNotEqual(
                default_manifest["input"]["input_sha256"],
                changed_manifest["input"]["input_sha256"],
            )

    def test_adapter_absence_malformed_and_unsafe_permission_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            table = Path(directory) / "table.npy"
            with self.assertRaises(DeonticAdapterError):
                generate_table(
                    table,
                    self.snapshot,
                    self.decisions,
                    config=self.config,
                    adapter=None,
                )
            with self.assertRaises(DeonticAdapterError):
                generate_table(
                    table,
                    self.snapshot,
                    self.decisions,
                    config=self.config,
                    adapter=_MalformedAdapter(),
                )
            with self.assertRaises(DeonticAdapterError):
                generate_table(
                    table,
                    self.snapshot,
                    self.decisions,
                    config=self.config,
                    adapter=_PermissiveAdapter(),
                )

    def test_padding_is_explicit_and_abstain_only(self) -> None:
        model = compile_model(
            self.snapshot, self.decisions, config=self.config, adapter=self.adapter
        )
        self.assertEqual(model.padded_graph_slots, 1)
        padded_state = model.state_index(0, 3, 0)
        self.assertEqual(
            np.flatnonzero(model.base_allowed[padded_state]).tolist(),
            [ABSTAIN_ACTION_INDEX],
        )
        with tempfile.TemporaryDirectory() as directory:
            table, _, _ = self._generate(directory)
            receipt = query(
                table,
                self.snapshot,
                decision_id="D0",
                start_node_slot=3,
                layer=3,
                required_decisions=self.decisions,
                config=self.config,
                adapter=self.adapter,
            )
            self.assertEqual(receipt["terminal"]["kind"], "abstain_or_escalate")
            self.assertEqual(receipt["chosen_action"], "abstain_or_escalate")

    def test_evidence_completion_adapter_uses_current_node_target_semantics(
        self,
    ) -> None:
        decisions = self._targeted_decisions()
        adapter = evidence_adapter()
        model = compile_model(
            self.snapshot, decisions, config=self.config, adapter=adapter
        )

        padded_ref = model.state_ref(model.state_index(0, 3, 0))
        non_target_ref = model.state_ref(model.state_index(0, 1, 0))
        incomplete_ref = model.state_ref(model.state_index(0, 0, 0))
        complete_ref = model.state_ref(model.state_index(0, 0, 1))
        self.assertFalse(padded_ref.applicable)
        self.assertTrue(padded_ref.padded)
        self.assertFalse(non_target_ref.applicable)
        self.assertFalse(non_target_ref.padded)
        self.assertTrue(incomplete_ref.applicable)
        self.assertTrue(complete_ref.applicable)

        padded = adapter.constraints(padded_ref)
        non_target = adapter.constraints(non_target_ref)
        incomplete = adapter.constraints(incomplete_ref)
        complete = adapter.constraints(complete_ref)
        self.assertEqual(padded.status, EVIDENCE_STATUS_PADDED)
        self.assertEqual(padded.allowed_mask, ABSTAIN_MASK)
        self.assertEqual(non_target.status, EVIDENCE_STATUS_NON_APPLICABLE)
        self.assertEqual(non_target.allowed_mask, NAVIGATION_MASK | ABSTAIN_MASK)
        self.assertEqual(incomplete.status, EVIDENCE_STATUS_INCOMPLETE)
        self.assertEqual(incomplete.allowed_mask, NAVIGATION_MASK | ABSTAIN_MASK)
        self.assertEqual(complete.status, EVIDENCE_STATUS_COMPLETE)
        self.assertEqual(complete.allowed_mask, 1 << RESOLVE_ACTION_INDEX)
        self.assertEqual(complete.obligatory_mask, 1 << RESOLVE_ACTION_INDEX)
        self.assertFalse(complete.allows(ABSTAIN_ACTION_INDEX))

        def mask(row: np.ndarray) -> int:
            return sum(1 << index for index, permitted in enumerate(row) if permitted)

        padded_index = model.state_index(0, 3, 0)
        non_target_index = model.state_index(0, 1, 0)
        incomplete_index = model.state_index(0, 0, 0)
        complete_index = model.state_index(0, 0, 1)
        self.assertEqual(mask(model.base_allowed[padded_index]), ABSTAIN_MASK)
        self.assertEqual(
            mask(model.normative_allowed[non_target_index]),
            NAVIGATION_MASK | ABSTAIN_MASK,
        )
        self.assertEqual(
            mask(model.normative_allowed[incomplete_index]),
            NAVIGATION_MASK | ABSTAIN_MASK,
        )
        for state_index, node_slot in (
            (non_target_index, 1),
            (incomplete_index, 0),
        ):
            structural_navigation = sum(
                1 << action_index
                for action_index, slot in enumerate(model.navigation[node_slot])
                if slot is not None
            )
            self.assertEqual(
                mask(model.base_allowed[state_index]),
                structural_navigation | ABSTAIN_MASK,
            )
            self.assertFalse(model.resolve_available[state_index])
        self.assertEqual(
            mask(model.normative_allowed[complete_index]), 1 << RESOLVE_ACTION_INDEX
        )
        self.assertEqual(
            mask(model.base_allowed[complete_index]), 1 << RESOLVE_ACTION_INDEX
        )
        self.assertTrue(model.resolve_available[complete_index])
        self.assertFalse(model.abstain_available[complete_index])

    def test_evidence_completion_production_resolution_receipt(self) -> None:
        decisions = self._targeted_decisions()
        adapter = evidence_adapter()
        with tempfile.TemporaryDirectory() as directory:
            table = Path(directory) / "evidence.npy"
            manifest = Path(directory) / "evidence.manifest.json"
            generate_table(
                table,
                self.snapshot,
                decisions,
                config=self.config,
                adapter=adapter,
                manifest=manifest,
            )
            receipt = query(
                table,
                self.snapshot,
                decision_id="D0",
                start_node_id="oewn-00000001-n",
                evidence_mask=1,
                layer=0,
                required_decisions=decisions,
                config=self.config,
                adapter=adapter,
                manifest=manifest,
            )
            self.assertEqual(receipt["terminal"]["kind"], "resolution")
            self.assertEqual(receipt["chosen_action"], "resolve")
            self.assertEqual(receipt["deontic_statuses"], [EVIDENCE_STATUS_COMPLETE])
            self.assertIn(
                "evidence_completion:complete:obligatory",
                receipt["deontic_reason_ids"],
            )

    def test_adapter_provenance_binds_logic_profile_and_esso_identity(self) -> None:
        base = evidence_adapter()
        changed_adapters = (
            evidence_adapter(logic_semantics="deontic-kernel-evidence-completion-v2"),
            evidence_adapter(profile="production-fixture-v2"),
            evidence_adapter(logic_digest="c" * 64),
            evidence_adapter(profile_digest="d" * 64),
            evidence_adapter(evidence_digest="b" * 64),
        )
        base_model = compile_model(
            self.snapshot, self.decisions, config=self.config, adapter=base
        )
        for changed in changed_adapters:
            with self.subTest(provenance=changed.provenance_record()):
                changed_model = compile_model(
                    self.snapshot,
                    self.decisions,
                    config=self.config,
                    adapter=changed,
                )
                self.assertNotEqual(
                    base_model.provenance["deontic_adapter_provenance_sha256"],
                    changed_model.provenance["deontic_adapter_provenance_sha256"],
                )
                self.assertNotEqual(
                    base_model.provenance["input_sha256"],
                    changed_model.provenance["input_sha256"],
                )
        with tempfile.TemporaryDirectory() as directory:
            _, _, base_manifest = self._generate(directory, "base.npy", adapter=base)
            _, _, changed_manifest = self._generate(
                directory, "changed.npy", adapter=changed_adapters[1]
            )
            self.assertNotEqual(
                base_manifest["output"]["artifact_identity_sha256"],
                changed_manifest["output"]["artifact_identity_sha256"],
            )
            self.assertNotEqual(
                base_manifest["input"]["deontic_adapter_provenance_sha256"],
                changed_manifest["input"]["deontic_adapter_provenance_sha256"],
            )
            self.assertEqual(
                base_manifest["provenance"]["deontic_adapter"]["profile"],
                "production-fixture-v1",
            )
            bound = base_manifest["provenance"]["deontic_adapter"]
            self.assertEqual(
                bound["logic_semantics_sha256"],
                "1a95da0066a4bdb8a8fb6cfde4629eab95ac35d3b814bfcaf21e10328ed355df",
            )
            self.assertEqual(
                bound["profile_sha256"],
                "4046ef1d6377f9eed77d86b76f7f813268d51bef6af8b2fd5a93c355b8c51efa",
            )
            self.assertEqual(
                set(bound["esso_evidence_hashes"]), {"esso-ir", "esso-model"}
            )

    def test_evidence_adapter_rejects_malformed_or_non_sha256_provenance(self) -> None:
        invalid_adapters = (
            lambda: evidence_adapter(evidence_digest="not-a-sha256"),
            lambda: EvidenceCompletionDeonticAdapter(
                logic_semantics="kernel-v1",
                profile="profile-v1",
                esso_evidence_hashes={},
            ),
            lambda: EvidenceCompletionDeonticAdapter(
                logic_semantics="kernel-v1",
                profile="profile-v1",
                esso_evidence_hashes={"esso-ir": "a" * 64},
            ),
            lambda: EvidenceCompletionDeonticAdapter(
                logic_semantics="kernel-v1",
                logic_semantics_sha256="a" * 64,
                profile="profile-v1",
                esso_evidence_hashes={"esso-ir": "b" * 64},
            ),
            lambda: EvidenceCompletionDeonticAdapter(
                logic_semantics="kernel-v1",
                profile="profile-v1",
                esso_evidence_hashes={"evidence": "a" * 64},
                logic_semantics_sha256="not-a-sha256",
                profile_sha256="b" * 64,
            ),
            lambda: EvidenceCompletionDeonticAdapter(
                provenance={
                    "schema": "evidence-completion-deontic-provenance-v1",
                    "logic_semantics": "kernel-v1",
                    "profile": "profile-v1",
                    "esso_evidence_hashes": {"evidence": "A" * 64},
                }
            ),
            lambda: EvidenceCompletionDeonticAdapter(
                provenance={
                    "schema": "evidence-completion-deontic-provenance-v1",
                    "logic_semantics": "kernel-v1",
                    "profile": "profile-v1",
                }
            ),
        )
        for factory in invalid_adapters:
            with (
                self.subTest(factory=factory),
                self.assertRaises(DeonticAdapterError),
            ):
                factory()

    def test_cli_deontic_modes_are_mutually_exclusive(self) -> None:
        with self.assertRaises(SystemExit) as raised:
            _build_cli_parser().parse_args(
                [
                    "build",
                    "--snapshot",
                    "snapshot.json",
                    "--output",
                    "table.npy",
                    "--manifest",
                    "manifest.json",
                    "--fixture-deontic",
                    "--evidence-deontic",
                ]
            )
        self.assertEqual(raised.exception.code, 2)

    def test_cli_accepts_explicit_verification_and_receipt_outputs(self) -> None:
        parser = _build_cli_parser()
        verify_args = parser.parse_args(
            [
                "verify",
                "--snapshot",
                "snapshot.json",
                "--fixture-deontic",
                "--table",
                "table.npy",
                "--report",
                "verify.json",
            ]
        )
        query_args = parser.parse_args(
            [
                "query",
                "--snapshot",
                "snapshot.json",
                "--fixture-deontic",
                "--table",
                "table.npy",
                "--receipt",
                "receipt.json",
            ]
        )
        self.assertEqual(verify_args.report, Path("verify.json"))
        self.assertEqual(query_args.receipt, Path("receipt.json"))

    def test_cli_evidence_mode_requires_and_binds_all_content_hashes(self) -> None:
        parser = _build_cli_parser()
        base_args = [
            "build",
            "--snapshot",
            "snapshot.json",
            "--output",
            "table.npy",
            "--manifest",
            "manifest.json",
            "--evidence-deontic",
            "--deontic-logic-semantics",
            "deontic-kernel-evidence-completion-v1",
            "--deontic-logic-semantics-sha256",
            "1a95da0066a4bdb8a8fb6cfde4629eab95ac35d3b814bfcaf21e10328ed355df",
            "--deontic-profile",
            "policy-profile-v1",
            "--deontic-profile-sha256",
            "4046ef1d6377f9eed77d86b76f7f813268d51bef6af8b2fd5a93c355b8c51efa",
            "--esso-evidence-hash",
            f"esso-model={'a' * 64}",
            "--esso-evidence-hash",
            f"esso-ir={'b' * 64}",
        ]
        adapter = _cli_adapter(parser.parse_args(base_args))
        provenance = adapter.provenance_record()
        self.assertEqual(
            provenance["logic_semantics_sha256"],
            "1a95da0066a4bdb8a8fb6cfde4629eab95ac35d3b814bfcaf21e10328ed355df",
        )
        self.assertEqual(
            provenance["profile_sha256"],
            "4046ef1d6377f9eed77d86b76f7f813268d51bef6af8b2fd5a93c355b8c51efa",
        )
        self.assertEqual(
            provenance["esso_evidence_hashes"],
            {"esso-ir": "b" * 64, "esso-model": "a" * 64},
        )

        missing_logic_hash = base_args.copy()
        flag_index = missing_logic_hash.index("--deontic-logic-semantics-sha256")
        del missing_logic_hash[flag_index : flag_index + 2]
        with self.assertRaisesRegex(
            DeonticAdapterError, "--deontic-logic-semantics-sha256"
        ):
            _cli_adapter(parser.parse_args(missing_logic_hash))

        malformed_profile_hash = base_args.copy()
        digest_index = malformed_profile_hash.index("--deontic-profile-sha256") + 1
        malformed_profile_hash[digest_index] = "not-a-sha256"
        with self.assertRaisesRegex(
            DeonticAdapterError, "profile_sha256 must be a lowercase SHA-256"
        ):
            _cli_adapter(parser.parse_args(malformed_profile_hash))

        no_esso = base_args[: base_args.index("--esso-evidence-hash")]
        with self.assertRaisesRegex(
            DeonticAdapterError, "at least one ESSO evidence hash"
        ):
            _cli_adapter(parser.parse_args(no_esso))

    def test_silent_padding_and_graph_schema_errors_are_rejected(self) -> None:
        strict_config = fixture_config(
            layers=4,
            decisions=2,
            node_slots=4,
            chunk_size=3,
            allow_explicit_padding=False,
        )
        with self.assertRaises(SnapshotValidationError):
            compile_model(
                self.snapshot,
                self.decisions,
                config=strict_config,
                adapter=self.adapter,
            )

        duplicate = copy.deepcopy(self.snapshot)
        duplicate["graph"]["nodes"].append(
            copy.deepcopy(duplicate["graph"]["nodes"][0])
        )
        duplicate["counts"]["nodes"] = 4
        with self.assertRaises(SnapshotValidationError):
            compile_model(
                duplicate, self.decisions, config=self.config, adapter=self.adapter
            )

        malformed_evidence = copy.deepcopy(self.snapshot)
        malformed_evidence["graph"]["edges"][0]["evidence_bits"] = 4
        with self.assertRaises(SnapshotValidationError):
            compile_model(
                malformed_evidence,
                self.decisions,
                config=self.config,
                adapter=self.adapter,
            )

    def test_corrupt_table_is_detected_by_exhaustive_replay(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            table, _, _ = self._generate(directory)
            mapped = np.load(table, mmap_mode="r+")
            mapped[1, 0, 7] = np.float32(mapped[1, 0, 7] + np.float32(0.25))
            mapped.flush()
            result = verify_table(
                table,
                self.snapshot,
                self.decisions,
                config=self.config,
                adapter=self.adapter,
                chunk_size=2,
            )
            self.assertFalse(result["passed"])
            self.assertGreater(result["mismatch_count"], 0)
            self.assertGreater(result["max_abs_bellman_error"], 0.0)

    def test_exhaustive_replay_passes_fixture_table(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            table, manifest, _ = self._generate(directory)
            result = verify_table(
                table,
                self.snapshot,
                self.decisions,
                config=self.config,
                adapter=self.adapter,
                manifest=manifest,
                chunk_size=2,
            )
            self.assertTrue(result["passed"])
            self.assertTrue(result["exhaustive"])
            self.assertEqual(result["replayed_layers"], self.config.layers)
            self.assertEqual(
                result["checked_values"],
                self.config.layers * self.config.state_count * 8,
            )
            self.assertEqual(result["mismatch_count"], 0)
            self.assertEqual(result["max_abs_bellman_error"], 0.0)
            self.assertTrue(result["finite_trace_gate"]["passed"])
            self.assertEqual(result["finite_trace_gate"]["forbidden_choice_count"], 0)
            self.assertEqual(
                result["finite_trace_gate"]["nonterminating_choice_count"], 0
            )
            self.assertLessEqual(
                result["finite_trace_gate"]["maximum_observed_terminal_steps"],
                self.config.layers,
            )


if __name__ == "__main__":
    unittest.main()
