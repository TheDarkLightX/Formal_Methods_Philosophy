from __future__ import annotations

import ast
import copy
import gzip
import hashlib
import itertools
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from examples.layered_q_tables.synthetic_deontic_luna_v1 import (
    AUTHORITY,
    EXPECTED_RECORD_COUNT,
    EXPECTED_SEMANTICS_SHA256,
    EXPECTED_TEMPLATE_SHA256,
    GeneratorReject,
    build_corpus,
    canonical_hash,
    canonical_json_bytes,
    compile_core,
    deterministic_gzip,
    encode_record,
    evaluate_core,
    generate_record,
    load_template_bank,
    rank_coordinate,
    truth_all,
    truth_any,
    truth_not,
    unrank_ordinal,
    validate_template_bank,
    verify_semantics_spec,
)

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent.parent
TEMPLATE = ROOT / "synthetic_deontic_luna_v1_templates.json"
SEMANTICS = REPO_ROOT / "research" / "synthetic_deontic_luna_v1_semantics.md"


class SyntheticDeonticLunaV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.template = load_template_bank(TEMPLATE)

    def test_frozen_input_hashes_and_closed_template(self) -> None:
        self.assertEqual(self.template.sha256, EXPECTED_TEMPLATE_SHA256)
        self.assertEqual(verify_semantics_spec(SEMANTICS), EXPECTED_SEMANTICS_SHA256)
        self.assertEqual(len(self.template.data["domains"]), 16)
        self.assertEqual(len(self.template.data["topology_programs"]), 16)
        self.assertEqual(
            self.template.data["factorization"]["record_count"],
            EXPECTED_RECORD_COUNT,
        )

    def test_exact_lattice_round_trip_and_type_rejection(self) -> None:
        for ordinal in range(EXPECTED_RECORD_COUNT):
            self.assertEqual(rank_coordinate(unrank_ordinal(ordinal)), ordinal)
        for invalid in (-1, EXPECTED_RECORD_COUNT, True, "0"):
            with self.subTest(invalid=invalid), self.assertRaises(GeneratorReject):
                unrank_ordinal(invalid)  # type: ignore[arg-type]
        with self.assertRaises(GeneratorReject):
            rank_coordinate((0, 0, 0, 0, 0))
        with self.assertRaises(GeneratorReject):
            rank_coordinate((0, 0, 0, 0, 0, True))

    def test_complete_four_valued_truth_tables(self) -> None:
        values = ("T", "F", "U", "B")
        expected_and = {
            ("T", "T"): "T", ("T", "F"): "F", ("T", "U"): "U", ("T", "B"): "B",
            ("F", "T"): "F", ("F", "F"): "F", ("F", "U"): "F", ("F", "B"): "F",
            ("U", "T"): "U", ("U", "F"): "F", ("U", "U"): "U", ("U", "B"): "F",
            ("B", "T"): "B", ("B", "F"): "F", ("B", "U"): "F", ("B", "B"): "B",
        }
        expected_or = {
            ("T", "T"): "T", ("T", "F"): "T", ("T", "U"): "T", ("T", "B"): "T",
            ("F", "T"): "T", ("F", "F"): "F", ("F", "U"): "U", ("F", "B"): "B",
            ("U", "T"): "T", ("U", "F"): "U", ("U", "U"): "U", ("U", "B"): "T",
            ("B", "T"): "T", ("B", "F"): "B", ("B", "U"): "T", ("B", "B"): "B",
        }
        for left, right in itertools.product(values, repeat=2):
            with self.subTest(left=left, right=right):
                self.assertEqual(truth_all([left, right]), expected_and[(left, right)])
                self.assertEqual(truth_any([left, right]), expected_or[(left, right)])
        self.assertEqual(
            {value: truth_not(value) for value in values},
            {"T": "F", "F": "T", "U": "U", "B": "B"},
        )

    def test_template_validator_kills_structural_and_typed_mutants(self) -> None:
        mutants: list[tuple[str, dict[str, object], str]] = []

        extra = copy.deepcopy(self.template.data)
        extra["domains"][0]["unknown_field"] = "x"
        mutants.append(("extra nested field", extra, "field_set_mismatch"))

        mutation = copy.deepcopy(self.template.data)
        mutation["domains"][0]["causal_mutations"][0]["changed_field_ids"] = [
            "capacity_state",
            "reserve_state",
        ]
        mutants.append(("multifield mutation", mutation, "mutation_delta_mismatch"))

        repair = copy.deepcopy(self.template.data)
        repair["topology_programs"][8]["norms"][1]["condition_refs"][0] = "violation:n2"
        mutants.append(("wrong repair gate", repair, "repair_gate_mismatch"))

        deadline = copy.deepcopy(self.template.data)
        deadline["topology_programs"][7]["norms"][0]["operator"] = "P"
        mutants.append(("deadline permission", deadline, "unsupported_deadline_operator"))

        evidence = copy.deepcopy(self.template.data)
        evidence["topology_programs"][0]["application_targets"]["evidence"] = ["n0"]
        mutants.append(("evidence target omission", evidence, "evidence_target_mismatch"))

        pair = copy.deepcopy(self.template.data)
        pair["counterfactual_contract"]["unordered_value_pairs"].pop()
        mutants.append(("missing unordered pair", pair, "unordered_pair_mismatch"))

        for name, mutant, code in mutants:
            with self.subTest(name=name), self.assertRaisesRegex(GeneratorReject, code):
                validate_template_bank(mutant)

    def test_compiler_binds_subject_evidence_and_state_mirrors(self) -> None:
        for coordinate in (
            (0, 0, 0, 0, 0, 0),
            (0, 7, 0, 3, 0, 0),
            (0, 8, 0, 0, 0, 0),
            (15, 15, 3, 3, 3, 3),
        ):
            with self.subTest(coordinate=coordinate):
                core, declared = compile_core(self.template, coordinate)
                action_actor = {action["id"]: action["actor_id"] for action in core["actions"]}
                evidence_targets = set(core["evidence"][0]["target_norm_ids"])
                for norm in core["norms"]:
                    self.assertEqual(norm["subject_id"], action_actor[norm["action_id"]])
                    self.assertIn(
                        {"kind": "state", "id": norm["id"]},
                        norm["condition_refs"],
                    )
                    if {"kind": "evidence", "id": "e0"} in norm["condition_refs"]:
                        self.assertIn(norm["id"], evidence_targets)
                self.assertEqual(declared["domain_code"], coordinate[0])
                self.assertEqual(declared["topology_code"], coordinate[1])

    def test_record_identity_authority_and_replay(self) -> None:
        for ordinal in (0, 48, 1840, 2048, 2056, 32767, 65535):
            with self.subTest(ordinal=ordinal):
                first = generate_record(self.template, ordinal)
                second = generate_record(self.template, ordinal)
                self.assertEqual(first, second)
                self.assertEqual(encode_record(self.template, ordinal), canonical_json_bytes(first))
                self.assertEqual(first["authority"], AUTHORITY)
                self.assertFalse(first["authority"]["may_authorize_external_effects"])
                self.assertEqual(first["semantic_core_sha256"], canonical_hash(first["semantic_core"]))
                self.assertEqual(first["stable_id"], f"sdk-luna-v1-{first['semantic_core_sha256']}")
                without_record_hash = {key: value for key, value in first.items() if key != "record_sha256"}
                self.assertEqual(first["record_sha256"], canonical_hash(without_record_hash))
                claim_without_hash = {
                    key: value for key, value in first["generator_claim"].items() if key != "result_sha256"
                }
                self.assertEqual(
                    first["generator_claim"]["result_sha256"],
                    canonical_hash(claim_without_hash),
                )

    def test_exact_outcome_rows_and_unresolved_empty_action_law(self) -> None:
        expected = [
            (26, 72, 158),
            (26, 88, 142),
            (26, 88, 142),
            (26, 88, 142),
            (26, 88, 142),
            (26, 88, 142),
            (26, 88, 142),
            (34, 64, 158),
            (29, 80, 147),
            (26, 88, 142),
            (26, 88, 142),
            (26, 88, 142),
            (62, 20, 174),
            (62, 20, 174),
            (21, 93, 142),
            (62, 20, 174),
        ]
        observed: list[tuple[int, int, int]] = []
        for topology in range(16):
            counts: Counter[tuple[str, str]] = Counter()
            for evidence, state, resolution, defeater in itertools.product(range(4), repeat=4):
                core, _ = compile_core(
                    self.template,
                    (0, topology, evidence, state, resolution, defeater),
                )
                result = evaluate_core(core)
                counts[(result["status"], result["fallback"])] += 1
                if result["status"] == "unresolved":
                    self.assertEqual(result["executable_required_action_ids"], [])
                    self.assertEqual(result["executable_permitted_action_ids"], [])
                    self.assertEqual(result["admissible_action_ids"], [])
            observed.append(
                (
                    counts[("resolved", "none")],
                    counts[("unresolved", "abstain")],
                    counts[("unresolved", "escalate")],
                )
            )
        self.assertEqual(observed, expected)
        self.assertEqual(
            tuple(sum(row[index] for row in observed) * 16 for index in range(3)),
            (8_480, 18_576, 38_480),
        )

    def test_unknown_and_inconsistent_evidence_never_resolve(self) -> None:
        for topology, evidence, state, resolution, defeater in itertools.product(
            range(16), (2, 3), range(4), range(4), range(4)
        ):
            core, _ = compile_core(
                self.template,
                (0, topology, evidence, state, resolution, defeater),
            )
            result = evaluate_core(core)
            self.assertEqual(result["status"], "unresolved")
            self.assertIn(result["fallback"], {"abstain", "escalate"})
            self.assertEqual(result["admissible_action_ids"], [])

    def test_deadline_lifecycle_and_relevant_cycle_witnesses(self) -> None:
        timely = evaluate_core(compile_core(self.template, (0, 7, 0, 1, 0, 0))[0])
        late = evaluate_core(compile_core(self.template, (0, 7, 0, 2, 0, 0))[0])
        unknown = evaluate_core(compile_core(self.template, (0, 7, 0, 3, 0, 0))[0])
        self.assertIn("n0", timely["satisfied_norm_ids"])
        self.assertIn("n0", late["violated_norm_ids"])
        self.assertIn("n1", late["violated_norm_ids"])
        self.assertEqual(
            set(unknown["blocker_codes"]),
            {"unknown_deadline", "unknown_lifecycle"},
        )
        for step in unknown["proof_trace"]["norm_steps"]:
            if step["final_disposition"] == "blocked_unknown":
                self.assertNotIn("lifecycle_blocked_unknown", step["reason_codes"])

        # Differential-regression witness from the independent oracle.
        ordinary_unknown = evaluate_core(
            compile_core(self.template, (3, 0, 0, 3, 0, 0))[0]
        )
        self.assertEqual(rank_coordinate((3, 0, 0, 3, 0, 0)), 12_336)
        self.assertEqual(
            [step["reason_codes"] for step in ordinary_unknown["proof_trace"]["norm_steps"]],
            [["unknown_lifecycle"], ["unknown_lifecycle"]],
        )

        active_cycle = evaluate_core(compile_core(self.template, (0, 0, 0, 0, 3, 0))[0])
        dormant_cycle = evaluate_core(compile_core(self.template, (0, 0, 0, 1, 3, 0))[0])
        self.assertIn("relevant_priority_cycle", active_cycle["blocker_codes"])
        self.assertNotIn("relevant_priority_cycle", dormant_cycle["blocker_codes"])

    def test_repair_gate_precedence_and_unavailable_provider(self) -> None:
        uncertain = evaluate_core(compile_core(self.template, (0, 8, 2, 1, 0, 0))[0])
        self.assertIn("unknown_primary_violation", uncertain["blocker_codes"])
        self.assertIn("unknown_repair_availability", uncertain["blocker_codes"])
        self.assertEqual(
            uncertain["repair_availability"][0]["availability"],
            "blocked_unknown",
        )

        unavailable = evaluate_core(compile_core(self.template, unrank_ordinal(2056))[0])
        self.assertIn("n0", unavailable["violated_norm_ids"])
        self.assertEqual(set(unavailable["activated_repair_norm_ids"]), {"n1", "n2"})
        self.assertEqual(unavailable["repair_availability"][0]["availability"], "defeated")
        self.assertIn("repair_unavailable", unavailable["blocker_codes"])

    def test_deterministic_gzip_has_zero_mtime_and_empty_filename(self) -> None:
        payload = b'{"ordinal":0}\n{"ordinal":1}\n'
        first = deterministic_gzip(payload)
        second = deterministic_gzip(payload)
        self.assertEqual(first, second)
        self.assertEqual(gzip.decompress(first), payload)
        self.assertEqual(first[4:8], b"\x00\x00\x00\x00")
        self.assertEqual(first[3] & 0x08, 0)

    def test_hash_binding_and_existing_output_fail_closed(self) -> None:
        with self.assertRaisesRegex(GeneratorReject, "template_hash_mismatch"):
            load_template_bank(TEMPLATE, expected_sha256="0" * 64)
        with self.assertRaisesRegex(GeneratorReject, "semantics_hash_mismatch"):
            verify_semantics_spec(SEMANTICS, expected_sha256="0" * 64)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            existing = root / "corpus"
            existing.mkdir()
            with self.assertRaisesRegex(GeneratorReject, "output_exists"):
                build_corpus(TEMPLATE, SEMANTICS, existing, root / "manifest.json")

    def test_generator_source_does_not_import_oracle(self) -> None:
        source_path = ROOT / "synthetic_deontic_luna_v1.py"
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)
        self.assertFalse(any("oracle" in name for name in imports))

    def test_canonical_json_rejects_nonfinite_values(self) -> None:
        with self.assertRaises(GeneratorReject):
            canonical_json_bytes({"bad": float("nan")})
        payload = canonical_json_bytes({"z": 1, "a": 2})
        self.assertEqual(payload, b'{"a":2,"z":1}')
        self.assertEqual(hashlib.sha256(payload).hexdigest(), canonical_hash({"z": 1, "a": 2}))


if __name__ == "__main__":
    unittest.main()
