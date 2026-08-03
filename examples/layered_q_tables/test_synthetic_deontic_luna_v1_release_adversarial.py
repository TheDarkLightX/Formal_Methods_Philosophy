from __future__ import annotations

import copy
import itertools
import unittest
from dataclasses import replace
from pathlib import Path

from examples.layered_q_tables import synthetic_deontic_luna_v1_oracle as oracle

ROOT = Path(__file__).resolve().parent
TEMPLATE_PATH = ROOT / "synthetic_deontic_luna_v1_templates.json"
SEMANTICS_PATH = ROOT.parents[1] / "research" / "synthetic_deontic_luna_v1_semantics.md"


class SyntheticDeonticLunaV1ReleaseAdversarialTests(unittest.TestCase):
    """Permanent regressions for the four independent review blockers."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.template = oracle.load_template_bank(TEMPLATE_PATH)
        semantics_bytes = oracle.load_bound_semantics(SEMANTICS_PATH)
        cls.semantics_sha256 = oracle.sha256_bytes(semantics_bytes)

    def verified_case(
        self, codes: tuple[int, int, int, int, int, int]
    ) -> oracle.VerifiedCase:
        return oracle.verify_record(
            oracle.encode_reference_record(self.template, codes),
            self.template,
        )

    def assert_oracle_rejects(self, expected_code: str, action: object) -> None:
        self.assertTrue(callable(action))
        with self.assertRaises(oracle.OracleReject) as caught:
            action()
        self.assertEqual(caught.exception.code, expected_code)

    def test_counterfactual_receipt_reconciles_every_verified_endpoint(self) -> None:
        before = self.verified_case((0, 0, 0, 0, 0, 0))
        after = self.verified_case((0, 0, 0, 0, 1, 0))
        honest = oracle.counterfactual_receipt(
            before,
            after,
            axis="resolution",
            template=self.template,
            oracle_source_sha256="1" * 64,
            evaluator_source_sha256="2" * 64,
        )
        self.assertEqual(honest["classification"], "EFFECT")

        forged_values = {
            "ordinal": after.ordinal + 1,
            "domain_id": "forged_domain",
            "topology_id": "forged_topology",
            "stable_id": f"sdk-luna-v1-{'0' * 64}",
            "record_sha256": "0" * 64,
            "result_sha256": "0" * 64,
            # This was the original exploit: a real EFFECT could be relabeled
            # INVARIANT by copying the before endpoint's normalized digest.
            "normalized_sha256": before.normalized_sha256,
            "normalized": {"schema": "forged-normalization"},
            "status": "forged",
            "fallback": "forged",
        }
        for field, forged_value in forged_values.items():
            with self.subTest(endpoint="after", field=field):
                forged_after = replace(after, **{field: forged_value})
                self.assert_oracle_rejects(
                    "verified_case_tamper",
                    lambda forged_after=forged_after: oracle.counterfactual_receipt(
                        before,
                        forged_after,
                        axis="resolution",
                        template=self.template,
                    ),
                )

        forged_before = replace(before, record_sha256="f" * 64)
        self.assert_oracle_rejects(
            "verified_case_tamper",
            lambda: oracle.counterfactual_receipt(
                forged_before,
                after,
                axis="resolution",
                template=self.template,
            ),
        )

    def test_axis_dependency_closure_accepts_only_exact_declared_fields(self) -> None:
        topology = self.template.data["topology_programs"][0]
        axis_indices = {
            "evidence": 2,
            "state": 3,
            "resolution": 4,
            "defeater": 5,
        }
        target_codes = {"evidence": 1, "state": 3, "resolution": 1, "defeater": 1}

        for axis, axis_index in axis_indices.items():
            before_codes = [0, 0, 0, 0, 0, 0]
            after_codes = list(before_codes)
            after_codes[axis_index] = target_codes[axis]
            before_core, _ = oracle.compile_core(self.template, before_codes)
            after_core, _ = oracle.compile_core(self.template, after_codes)
            changed_paths = sorted(
                oracle._all_differences(
                    before_core,
                    after_core,
                    "$.semantic_core",
                )
            )
            with self.subTest(axis=axis, kind="declared_change"):
                self.assertTrue(
                    oracle._axis_change_is_closed(
                        axis,
                        changed_paths,
                        before_core,
                        after_core,
                        topology,
                    )
                )
                self.assertFalse(
                    oracle._axis_change_is_closed(
                        axis,
                        changed_paths[:-1],
                        before_core,
                        after_core,
                        topology,
                    )
                )

        baseline, _ = oracle.compile_core(self.template, (0, 0, 0, 0, 0, 0))

        operator_escape = copy.deepcopy(baseline)
        operator_escape["norms"][0]["operator"] = "P"
        operator_paths = sorted(
            oracle._all_differences(
                baseline,
                operator_escape,
                "$.semantic_core",
            )
        )
        self.assertEqual(operator_paths, ["$.semantic_core.norms[0].operator"])
        self.assertFalse(
            oracle._axis_change_is_closed(
                "state",
                operator_paths,
                baseline,
                operator_escape,
                topology,
            )
        )

        derivation_escape = copy.deepcopy(baseline)
        defeater_index = next(
            index
            for index, fact in enumerate(derivation_escape["facts"])
            if fact["derivation_rule_id"] == "defeater_axis_v1"
        )
        derivation_escape["facts"][defeater_index]["derivation_rule_id"] = (
            "forged_defeater_rule"
        )
        derivation_paths = sorted(
            oracle._all_differences(
                baseline,
                derivation_escape,
                "$.semantic_core",
            )
        )
        self.assertEqual(
            derivation_paths,
            [f"$.semantic_core.facts[{defeater_index}].derivation_rule_id"],
        )
        self.assertFalse(
            oracle._axis_change_is_closed(
                "defeater",
                derivation_paths,
                baseline,
                derivation_escape,
                topology,
            )
        )

    def test_unbound_or_incomplete_release_evidence_never_reports_pass(self) -> None:
        expected = {
            (False, False): "FAIL",
            (False, True): "FAIL",
            (True, False): "FAIL",
            (True, True): "SKIP",
        }
        gate_ids = ("G01", "G03", "G05", "G07", "G10", "G13")
        for gate_id, (complete, precheck) in itertools.product(gate_ids, expected):
            with self.subTest(
                gate_id=gate_id,
                corpus_complete=complete,
                precheck_pass=precheck,
            ):
                status = oracle.unbound_evidence_gate_status(
                    corpus_complete=complete,
                    precheck_pass=precheck,
                )
                self.assertEqual(status, expected[(complete, precheck)])
                self.assertNotEqual(status, "PASS")

        for bad in (0, 1, "true", None):
            with self.subTest(bad_exact_boolean=bad):
                self.assert_oracle_rejects(
                    "wrong_type",
                    lambda bad=bad: oracle.unbound_evidence_gate_status(
                        corpus_complete=bad,
                        precheck_pass=True,
                    ),
                )

        partial = [self.verified_case((0, 0, 0, 0, 0, 0))]
        report = oracle.analyze_verified_cases(
            partial,
            self.template,
            enumerate_counterfactuals=False,
        )
        statuses = {row["gate_id"]: row["status"] for row in report["gate_results"]}
        self.assertEqual(
            {gate_id: statuses[gate_id] for gate_id in gate_ids},
            {gate_id: "FAIL" for gate_id in gate_ids},
        )
        self.assertEqual(statuses["G15"], "FAIL")
        self.assertEqual(
            report["promotion"]["assigned_label"],
            "QUARANTINED_CORPUS",
        )

    def test_deadline_rejections_use_the_exact_d265_codes(self) -> None:
        self.assertEqual(self.semantics_sha256, oracle.EXPECTED_SEMANTICS_SHA256)
        baseline = oracle.build_reference_record(
            self.template,
            (0, 7, 0, 0, 0, 0),
        )
        deadline_indices = [
            index
            for index, norm in enumerate(baseline["semantic_core"]["norms"])
            if norm["lifecycle"]["kind"] == "deadline"
        ]
        self.assertEqual(len(deadline_indices), 2)

        for index in deadline_indices:
            permission = copy.deepcopy(baseline)
            permission["semantic_core"]["norms"][index]["operator"] = "P"
            with self.subTest(index=index, mutant="deadline_permission"):
                self.assert_oracle_rejects(
                    "unsupported_deadline_operator",
                    lambda permission=permission: oracle.verify_record(
                        oracle.canonical_bytes(permission),
                        self.template,
                    ),
                )

            invalid_state = copy.deepcopy(baseline)
            invalid_state["semantic_core"]["norms"][index]["lifecycle"]["value"] = (
                "unknown"
            )
            with self.subTest(index=index, mutant="invalid_deadline_state"):
                self.assert_oracle_rejects(
                    "invalid_deadline_state",
                    lambda invalid_state=invalid_state: oracle.verify_record(
                        oracle.canonical_bytes(invalid_state),
                        self.template,
                    ),
                )


if __name__ == "__main__":
    unittest.main()
