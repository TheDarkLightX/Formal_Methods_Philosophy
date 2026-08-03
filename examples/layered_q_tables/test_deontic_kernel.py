from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from examples.layered_q_tables.deontic_kernel import (
    ABSTAIN_ACTION,
    ESCALATE_ACTION,
    LOGIC_PROFILE_ID,
    LOGIC_SEMANTICS_HASH,
    MAX_EXTENSION_BYTES,
    MAX_PACKET_BYTES,
    NEUTRAL_EVIDENCE_COMPLETION_POLICY_PROFILE,
    PACKET_SCHEMA,
    POLICY_PROFILE_SHA256,
    TRACE_SCHEMA,
    DeonticKernelError,
    ESSOVerificationStatus,
    SchemaError,
    bind_esso_verification_status,
    canonical_json_bytes,
    check_finite_trace,
    compile_esso_ir,
    compile_policy_profile,
    evaluate,
    evaluate_decision_pack,
    evaluate_json,
    evaluate_strict,
    load_decision_pack,
    parse_json,
    validate_packet,
)

PACK_PATH = Path(__file__).with_name("required_decisions.json")


def make_packet(
    *,
    facts: list[str] | None = None,
    rules: list[dict[str, object]] | None = None,
    allow_abstain: bool = False,
    actions: list[str] | None = None,
    decision_id: str = "test-decision",
    false_facts: list[str] | None = None,
    policy_profile: object | None = None,
    logic_profile: str = LOGIC_PROFILE_ID,
    **extra: object,
) -> dict[str, object]:
    selected_profile = policy_profile or NEUTRAL_EVIDENCE_COMPLETION_POLICY_PROFILE.to_data()
    if hasattr(selected_profile, "to_data"):
        selected_profile = selected_profile.to_data()
    packet: dict[str, object] = {
        "schema": PACKET_SCHEMA,
        "decision_id": decision_id,
        "logic_profile": logic_profile,
        "policy_profile": selected_profile,
        "actions": actions or ["cite_answer", "open_source", ABSTAIN_ACTION, ESCALATE_ACTION],
        "context": {"facts": facts or [], "false_facts": false_facts or []},
        "rules": rules or [],
        "allow_abstain": allow_abstain,
        "assumptions": ["Test facts are finite fixture inputs."],
        "extensions": {},
    }
    packet.update(extra)
    return packet


def make_rule(
    identifier: str,
    modality: str,
    action: str,
    predicate: dict[str, object],
    **extra: object,
) -> dict[str, object]:
    rule: dict[str, object] = {
        "id": identifier,
        "modality": modality,
        "action": action,
        "when": predicate,
    }
    rule.update(extra)
    return rule


class DeonticKernelTests(unittest.TestCase):
    def test_required_scenario_pack_covers_all_resolution_paths(self) -> None:
        loaded = load_decision_pack(PACK_PATH)
        self.assertEqual(len(loaded.decisions), 6)
        self.assertEqual(loaded.policy_profile.profile_id, "neutral-evidence-completion-v1")
        raw_pack = json.loads(PACK_PATH.read_text(encoding="utf-8"))
        self.assertTrue(all("policy_profile" not in item["packet"] for item in raw_pack["decisions"]))
        results = dict(evaluate_decision_pack(raw_pack))

        normal = results["normal-obligation"]
        self.assertTrue(normal.valid)
        self.assertEqual(normal.resolution, "allow")
        self.assertIsNone(normal.selected_action)
        self.assertIn("cite_answer", normal.allowed_actions)
        self.assertTrue(normal.obligatory_action_mask[normal.actions.index("cite_answer")])
        self.assertFalse(normal.action_mask_by_action[ESCALATE_ACTION])

        prohibition = results["prohibition"]
        self.assertEqual(prohibition.resolution, "allow")
        self.assertIsNone(prohibition.selected_action)
        self.assertFalse(prohibition.action_mask_by_action["cite_answer"])
        self.assertTrue(prohibition.action_mask_by_action["open_source"])
        self.assertIn("cite_answer", prohibition.prohibitions)

        permission = results["explicit-permission"]
        self.assertEqual(permission.resolution, "allow")
        self.assertIsNone(permission.selected_action)
        self.assertIn("cite_answer", permission.permissions)
        self.assertTrue(permission.action_mask_by_action["cite_answer"])

        conflict = results["conditional-conflict"]
        self.assertEqual(conflict.resolution, "escalate")
        self.assertEqual(conflict.selected_action, ESCALATE_ACTION)
        self.assertTrue(conflict.conflicts)
        self.assertEqual(conflict.allowed_actions, (ESCALATE_ACTION,))

        abstention = results["abstention-allowed-unresolved"]
        self.assertEqual(abstention.resolution, "abstain")
        self.assertEqual(abstention.selected_action, ABSTAIN_ACTION)
        self.assertTrue(abstention.action_mask_by_action[ABSTAIN_ACTION])

        escalation = results["fail-closed-escalation"]
        self.assertEqual(escalation.resolution, "escalate")
        self.assertEqual(escalation.allowed_actions, (ESCALATE_ACTION,))
        self.assertIn("incomplete_context", escalation.unresolved)
        self.assertEqual(escalation.unknown_predicates, ("missing-evidence-gate",))

    def test_obligation_permission_and_prohibition_semantics(self) -> None:
        obligation = evaluate(
            make_packet(
                facts=["ready"],
                rules=[make_rule("must-cite", "O", "cite_answer", {"fact": "ready"})],
            )
        )
        self.assertEqual(obligation.obligations, ("cite_answer",))
        self.assertTrue(obligation.statuses[1].obligation)
        self.assertTrue(obligation.statuses[1].permission)
        self.assertTrue(obligation.action_mask_by_action["cite_answer"])

        permission = evaluate(
            make_packet(
                facts=["ready"],
                rules=[make_rule("may-cite", "P", "cite_answer", {"fact": "ready"})],
            )
        )
        self.assertEqual(permission.permissions, ("cite_answer",))
        self.assertTrue(permission.action_mask_by_action["cite_answer"])

        prohibition = evaluate(
            make_packet(
                facts=["blocked"],
                rules=[make_rule("no-cite", "F", "cite_answer", {"fact": "blocked"})],
            )
        )
        self.assertEqual(prohibition.prohibitions, ("cite_answer",))
        self.assertFalse(prohibition.action_mask_by_action["cite_answer"])
        self.assertEqual(prohibition.resolution, "escalate")

    def test_obligation_and_prohibition_are_quarantined(self) -> None:
        result = evaluate(
            make_packet(
                facts=["urgent", "unreviewed"],
                rules=[
                    make_rule("duty", "O", "cite_answer", {"fact": "urgent"}),
                    make_rule(
                        "ban",
                        "F",
                        "cite_answer",
                        {"all": [{"fact": "unreviewed"}, {"fact": "urgent"}]},
                    ),
                ],
                allow_abstain=True,
            )
        )
        self.assertEqual(result.resolution, "escalate")
        self.assertEqual(result.allowed_actions, (ESCALATE_ACTION,))
        self.assertEqual(result.conflicts[0].action, "cite_answer")
        status = next(item for item in result.statuses if item.action == "cite_answer")
        self.assertTrue(status.obligation)
        self.assertTrue(status.prohibition)
        self.assertTrue(status.permission)
        self.assertFalse(result.obligatory_action_mask[result.actions.index("cite_answer")])
        self.assertTrue(
            all(
                not required or allowed
                for required, allowed in zip(result.obligatory_action_mask, result.action_mask)
            )
        )

    def test_action_mask_is_aligned_and_coherent(self) -> None:
        result = evaluate(
            make_packet(
                facts=["safe"],
                rules=[
                    make_rule("permit-cite", "P", "cite_answer", {"fact": "safe"}),
                    make_rule("forbid-open", "F", "open_source", {"fact": "safe"}),
                ],
            )
        )
        self.assertEqual(tuple(result.action_mask_by_action), result.actions)
        self.assertEqual(len(result.actions), len(result.action_mask))
        self.assertFalse(result.action_mask_by_action[ESCALATE_ACTION])
        self.assertTrue(result.action_mask_by_action["cite_answer"])
        self.assertFalse(result.action_mask_by_action["open_source"])
        self.assertFalse(result.action_mask_by_action[ABSTAIN_ACTION])
        for status in result.statuses:
            if status.obligation and not status.prohibition:
                self.assertTrue(status.permission)
                self.assertTrue(result.action_mask_by_action[status.action])
        self.assertTrue(
            all(
                not required or allowed
                for required, allowed in zip(result.obligatory_action_mask, result.action_mask)
            )
        )

    def test_predicate_evaluation_handles_all_any_not_and_empty_connectives(self) -> None:
        result = evaluate(
            make_packet(
                facts=["a", "b"],
                false_facts=["missing", "blocked"],
                rules=[
                    make_rule("all-true", "P", "cite_answer", {"all": [{"fact": "b"}, {"fact": "a"}]}),
                    make_rule("any-false", "P", "open_source", {"any": [{"fact": "missing"}]}),
                    make_rule("not-missing", "P", "open_source", {"not": {"fact": "blocked"}}),
                    make_rule("empty-all", "P", "open_source", {"all": []}),
                    make_rule("empty-any", "O", "open_source", {"any": []}),
                ],
            )
        )
        applicability = {item.identifier: item.applicable for item in result.rules_examined}
        self.assertEqual(
            applicability,
            {
                "all-true": True,
                "any-false": False,
                "empty-all": True,
                "empty-any": False,
                "not-missing": True,
            },
        )
        self.assertTrue(result.action_mask_by_action["cite_answer"])
        self.assertTrue(result.action_mask_by_action["open_source"])

    def test_unknown_predicates_are_tri_state_and_fail_closed(self) -> None:
        result = evaluate(
            make_packet(
                facts=["known"],
                rules=[make_rule("needs-missing", "P", "cite_answer", {"fact": "missing"})],
                allow_abstain=True,
            )
        )
        self.assertIsNone(result.rules_examined[0].applicable)
        self.assertEqual(result.rules_examined[0].reason, "unknown_predicate_applicability")
        self.assertEqual(result.unknown_predicates, ("needs-missing",))
        self.assertIn("incomplete_context", result.unresolved)
        self.assertEqual(result.resolution, "escalate")
        self.assertEqual(result.allowed_actions, (ESCALATE_ACTION,))

        explicit_false = evaluate(
            make_packet(
                false_facts=["missing"],
                rules=[make_rule("needs-missing", "P", "cite_answer", {"fact": "missing"})],
                allow_abstain=True,
            )
        )
        self.assertFalse(explicit_false.rules_examined[0].applicable)
        self.assertEqual(explicit_false.rules_examined[0].reason, "predicate_false")
        self.assertEqual(explicit_false.resolution, "abstain")

    def test_receipt_and_input_hash_are_deterministic_after_normalization(self) -> None:
        first = make_packet(
            facts=["b", "a"],
            rules=[
                make_rule("z-rule", "P", "open_source", {"any": [{"fact": "b"}, {"fact": "a"}]}),
                make_rule("a-rule", "P", "cite_answer", {"fact": "a"}),
            ],
            actions=[ESCALATE_ACTION, "open_source", ABSTAIN_ACTION, "cite_answer"],
        )
        second = make_packet(
            facts=["a", "b"],
            rules=[
                make_rule("a-rule", "P", "cite_answer", {"fact": "a"}),
                make_rule("z-rule", "P", "open_source", {"any": [{"fact": "a"}, {"fact": "b"}]}),
            ],
            actions=["cite_answer", ABSTAIN_ACTION, ESCALATE_ACTION, "open_source"],
        )
        first_result = evaluate(first)
        second_result = evaluate(second)
        self.assertEqual(first_result.input_sha256, second_result.input_sha256)
        self.assertEqual(first_result.receipt_json, second_result.receipt_json)
        self.assertEqual(first_result.receipt_sha256, second_result.receipt_sha256)
        self.assertEqual(
            first_result.receipt_sha256,
            hashlib.sha256(first_result.receipt_json.encode("ascii")).hexdigest(),
        )
        self.assertEqual(first_result.receipt["input_sha256"], first_result.input_sha256)
        self.assertEqual(first_result.receipt["rules_examined"][0]["id"], "a-rule")

    def test_receipt_contains_derivation_trace_and_limits(self) -> None:
        result = evaluate(
            make_packet(
                facts=["ready"],
                rules=[make_rule("must-cite", "O", "cite_answer", {"fact": "ready"})],
                assumptions=["This assumption is fixture-local."],
            )
        )
        receipt = result.receipt
        for field in (
            "input_sha256",
            "policy_profile_sha256",
            "logic_semantics_sha256",
            "applicable_facts",
            "known_false_facts",
            "rules_examined",
            "rule_reasons",
            "derived_statuses",
            "conflicts",
            "action_mask",
            "resolution",
            "eligible_action_mask",
            "obligatory_action_mask",
            "assumptions",
            "limits",
            "receipt_schema",
            "kernel_version",
            "packet_schema",
        ):
            self.assertIn(field, receipt)
        self.assertEqual(receipt["applicable_facts"], ["ready"])
        self.assertTrue(receipt["rules_examined"][0]["applicable"])
        self.assertEqual(receipt["rules_examined"][0]["reason"], "detached")
        self.assertEqual(receipt["policy_profile_sha256"], POLICY_PROFILE_SHA256)
        self.assertEqual(receipt["logic_semantics_sha256"], LOGIC_SEMANTICS_HASH)
        self.assertTrue(receipt["artifact_distinctions"]["deterministic_derivation_receipt"])
        self.assertTrue(receipt["artifact_distinctions"]["human_explanation"])
        self.assertFalse(receipt["artifact_distinctions"]["machine_checkable_proof_object"])
        self.assertEqual(receipt["derived_statuses"]["cite_answer"], {"O": True, "F": False, "P": True})

    def test_reserved_actions_are_present_and_kernel_owned(self) -> None:
        with self.assertRaises(SchemaError):
            validate_packet(
                make_packet(
                    rules=[make_rule("bad-target", "P", ESCALATE_ACTION, {"all": []})],
                )
            )
        invalid = evaluate({"schema": PACKET_SCHEMA, "unexpected": "field"})
        self.assertFalse(invalid.valid)
        self.assertEqual(invalid.resolution, "escalate")
        self.assertEqual(invalid.selected_action, ESCALATE_ACTION)
        self.assertEqual(invalid.allowed_actions, (ESCALATE_ACTION,))
        self.assertFalse(invalid.action_mask_by_action[ABSTAIN_ACTION])

    def test_policy_and_logic_hashes_are_compilation_bindings(self) -> None:
        packet = make_packet(
            facts=["ready"],
            rules=[make_rule("permit", "P", "cite_answer", {"fact": "ready"})],
        )
        result = evaluate(packet)
        self.assertEqual(result.policy_profile_sha256, POLICY_PROFILE_SHA256)
        self.assertEqual(result.logic_semantics_sha256, LOGIC_SEMANTICS_HASH)
        self.assertEqual(result.receipt["policy_profile_sha256"], POLICY_PROFILE_SHA256)
        self.assertEqual(result.receipt["logic_semantics_sha256"], LOGIC_SEMANTICS_HASH)

        alternate = dict(NEUTRAL_EVIDENCE_COMPLETION_POLICY_PROFILE.to_data())
        alternate["profile_id"] = "neutral-evidence-completion-copy"
        alternate_profile = compile_policy_profile(alternate)
        altered = make_packet(
            facts=["ready"],
            policy_profile=alternate_profile,
            rules=[make_rule("permit", "P", "cite_answer", {"fact": "ready"})],
        )
        altered_result = evaluate(altered)
        self.assertNotEqual(altered_result.policy_profile_sha256, result.policy_profile_sha256)
        self.assertEqual(altered_result.logic_semantics_sha256, result.logic_semantics_sha256)
        self.assertNotEqual(altered_result.receipt_sha256, result.receipt_sha256)

    def test_policy_profile_can_be_reused_as_a_compilation_input(self) -> None:
        profile = compile_policy_profile(NEUTRAL_EVIDENCE_COMPLETION_POLICY_PROFILE.to_data())
        packet = make_packet(
            facts=["ready"],
            rules=[make_rule("permit", "P", "cite_answer", {"fact": "ready"})],
        )
        packet_without_profile = dict(packet)
        packet_without_profile.pop("policy_profile")
        first = evaluate(packet_without_profile, policy_profile=profile)
        second = evaluate(packet, policy_profile=profile)
        self.assertTrue(first.valid)
        self.assertEqual(first.policy_profile_sha256, second.policy_profile_sha256)
        self.assertEqual(first.receipt_json, second.receipt_json)

    def test_utility_selection_is_outside_the_kernel(self) -> None:
        result = evaluate(
            make_packet(
                facts=["ready"],
                actions=["cite_answer", "open_source", ABSTAIN_ACTION, ESCALATE_ACTION],
                rules=[
                    make_rule("permit-cite", "P", "cite_answer", {"fact": "ready"}),
                    make_rule("permit-open", "P", "open_source", {"fact": "ready"}),
                ],
            )
        )
        self.assertIsNone(result.selected_action)
        self.assertEqual(result.allowed_actions, ("cite_answer", "open_source"))
        self.assertEqual(result.obligatory_actions, ())
        self.assertFalse(result.action_mask_by_action[ABSTAIN_ACTION])
        self.assertFalse(result.action_mask_by_action[ESCALATE_ACTION])

    def test_unresolved_case_escalates_without_abstention_permission(self) -> None:
        result = evaluate(make_packet(facts=["unknown"], allow_abstain=False))
        self.assertEqual(result.resolution, "escalate")
        self.assertIn("no_applicable_positive_action", result.unresolved)
        self.assertEqual(result.allowed_actions, (ESCALATE_ACTION,))

    def test_unresolved_case_can_abstain_only_when_packet_allows_it(self) -> None:
        result = evaluate(make_packet(facts=["unknown"], allow_abstain=True))
        self.assertEqual(result.resolution, "abstain")
        self.assertEqual(result.selected_action, ABSTAIN_ACTION)
        self.assertTrue(result.action_mask_by_action[ABSTAIN_ACTION])
        self.assertTrue(result.action_mask_by_action[ESCALATE_ACTION])
        self.assertFalse(result.action_mask_by_action["cite_answer"])

    def test_malformed_oversized_and_unknown_fields_are_rejected(self) -> None:
        unknown = make_packet(extra_field=True)
        with self.assertRaises(SchemaError) as unknown_error:
            validate_packet(unknown)
        self.assertEqual(unknown_error.exception.code, "unknown_field")

        too_many_facts = make_packet(facts=[f"fact_{index}" for index in range(65)])
        with self.assertRaises(SchemaError):
            validate_packet(too_many_facts)

        oversized_json = b"{" + b"\"x\":\"" + b"a" * MAX_PACKET_BYTES + b"\"}"
        with self.assertRaises(SchemaError) as oversized_error:
            parse_json(oversized_json)
        self.assertEqual(oversized_error.exception.code, "input_size_limit")
        invalid = evaluate_json(oversized_json)
        self.assertFalse(invalid.valid)
        self.assertEqual(invalid.resolution, "escalate")

        with self.assertRaises(SchemaError):
            validate_packet(make_packet(allow_abstain=1))

        missing_profile = make_packet()
        missing_profile.pop("policy_profile")
        with self.assertRaises(SchemaError) as profile_error:
            validate_packet(missing_profile)
        self.assertEqual(profile_error.exception.code, "missing_field")
        self.assertFalse(evaluate(missing_profile).valid)

    def test_duplicate_json_fields_are_rejected(self) -> None:
        raw = (
            '{"schema":"glassmind-deontic-decision-v1",'
            '"schema":"glassmind-deontic-decision-v1"}'
        )
        with self.assertRaises(SchemaError) as error:
            parse_json(raw)
        self.assertEqual(error.exception.code, "duplicate_field")

    def test_malicious_predicates_are_rejected_without_dynamic_execution(self) -> None:
        with self.assertRaises(SchemaError):
            validate_packet(
                make_packet(
                    rules=[make_rule("bad-op", "P", "cite_answer", {"call": "open_source"})],
                )
            )
        with self.assertRaises(SchemaError):
            validate_packet(
                make_packet(
                    rules=[make_rule("bad-fact", "P", "cite_answer", {"fact": "__import__"})],
                )
            )
        with self.assertRaises(SchemaError):
            validate_packet(
                make_packet(
                    rules=[
                        make_rule(
                            "too-wide",
                            "P",
                            "cite_answer",
                            {"all": [{"fact": f"f{index}"} for index in range(9)]},
                        )
                    ],
                )
            )
        source = Path(__file__).with_name("deontic_kernel.py").read_text(encoding="utf-8")
        self.assertNotIn("importlib", source)
        self.assertNotIn("eval(", source)
        self.assertNotIn("exec(", source)

    def test_cyclic_python_objects_fail_closed(self) -> None:
        packet = make_packet()
        packet["extensions"] = packet
        with self.assertRaises(SchemaError) as strict_error:
            validate_packet(packet)
        self.assertEqual(strict_error.exception.code, "cyclic_input")
        safe = evaluate(packet)
        self.assertFalse(safe.valid)
        self.assertEqual(safe.resolution, "escalate")
        self.assertEqual(safe.allowed_actions, (ESCALATE_ACTION,))

    def test_extension_fields_are_bounded_metadata(self) -> None:
        known = make_packet(
            extensions={
                "source_refs": ["source-1"],
                "temporal": {"deadline": "future-metadata"},
                "exception_hook": "future-exception-review",
                "priority_hook": "future-priority-review",
                "theorem_refs": ["future-theorem-1"],
                "knowledge_base": {
                    "name": "demo",
                    "snapshot": "v1",
                    "record_refs": ["record-1"],
                },
            }
        )
        self.assertTrue(validate_packet(known).canonical_bytes)

        with self.assertRaises(SchemaError):
            validate_packet(make_packet(extensions={"unregistered": "payload"}))
        with self.assertRaises(SchemaError):
            validate_packet(make_packet(extensions={"source_refs": ["s1", "s2", "s3", "s4", "s5"]}))

        oversized_extension = {
            "source_refs": [f"s{index}" + "s" * 126 for index in range(4)],
            "theorem_refs": [f"t{index}" + "t" * 126 for index in range(4)],
            "exception_hook": "e" * 128,
            "priority_hook": "p" * 128,
            "temporal": {"deadline": "d" * 128, "valid_from": "f" * 128},
            "knowledge_base": {
                "name": "n" * 128,
                "snapshot": "v" * 128,
                "record_refs": ["r" * 128],
            },
        }
        with self.assertRaises(SchemaError) as error:
            validate_packet(make_packet(extensions=oversized_extension))
        self.assertIn(error.exception.code, {"extension_size_limit", "extension_limit"})
        self.assertLessEqual(MAX_EXTENSION_BYTES, 1_024)

    def test_strict_and_safe_boundaries_are_distinct(self) -> None:
        malformed = make_packet(extra_field="reject-me")
        with self.assertRaises(SchemaError):
            evaluate_strict(malformed)
        safe = evaluate(malformed)
        self.assertFalse(safe.valid)
        self.assertEqual(safe.resolution, "escalate")

    def test_multiple_obligations_and_contrary_to_duty_fail_closed(self) -> None:
        multiple = evaluate(
            make_packet(
                facts=["ready"],
                rules=[
                    make_rule("must-cite", "O", "cite_answer", {"fact": "ready"}),
                    make_rule("must-open", "O", "open_source", {"fact": "ready"}),
                ],
            )
        )
        self.assertEqual(multiple.resolution, "escalate")
        self.assertIn("multiple_incompatible_obligations", multiple.unresolved)
        self.assertEqual(multiple.allowed_actions, (ESCALATE_ACTION,))

        ctd = evaluate(
            make_packet(
                facts=["ready"],
                rules=[
                    make_rule(
                        "remedial-duty",
                        "O",
                        "cite_answer",
                        {"fact": "ready"},
                        contrary_to_duty=True,
                    )
                ],
            )
        )
        self.assertEqual(ctd.resolution, "escalate")
        self.assertIn("contrary_to_duty_not_implemented", ctd.unresolved)

    def test_finite_trace_pass_and_counterexamples(self) -> None:
        passing = check_finite_trace(
            {
                "schema": TRACE_SCHEMA,
                "deadline": 2,
                "forbidden_actions": ["delete_source"],
                "steps": [
                    {"step": 0, "state": "pending"},
                    {"step": 1, "state": "resolved", "executed_action": "cite_answer"},
                ],
            }
        )
        self.assertEqual(passing.status, "PASS")
        self.assertIsNone(passing.counterexample)

        forbidden = check_finite_trace(
            {
                "schema": TRACE_SCHEMA,
                "deadline": 1,
                "forbidden_actions": ["delete_source"],
                "steps": [
                    {"step": 0, "state": "pending"},
                    {"step": 1, "state": "resolved", "executed_action": "delete_source"},
                ],
            }
        )
        self.assertEqual(forbidden.status, "FAIL")
        self.assertEqual(forbidden.counterexample["kind"], "forbidden_action")

        terminal_pending = check_finite_trace(
            {
                "schema": TRACE_SCHEMA,
                "deadline": 2,
                "forbidden_actions": [],
                "steps": [
                    {"step": 0, "state": "pending"},
                    {"step": 1, "state": "escalate"},
                    {"step": 2, "state": "pending"},
                ],
            }
        )
        self.assertEqual(terminal_pending.counterexample["kind"], "terminal_to_pending")

        late = check_finite_trace(
            {
                "schema": TRACE_SCHEMA,
                "deadline": 1,
                "forbidden_actions": [],
                "steps": [
                    {"step": 0, "state": "pending"},
                    {"step": 1, "state": "pending"},
                    {"step": 2, "state": "resolved"},
                ],
            }
        )
        self.assertEqual(late.counterexample["kind"], "deadline_liveness")

    def test_trace_step_is_independent_of_q_horizon(self) -> None:
        trace = {
            "schema": TRACE_SCHEMA,
            "deadline": 256,
            "forbidden_actions": [],
            "steps": [
                {"step": index, "state": "resolved" if index == 256 else "pending"}
                for index in range(257)
            ],
        }
        result = check_finite_trace(trace)
        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.checked_steps[-1].step, 256)

    def test_esso_adapter_is_deterministic_and_schema_explicit(self) -> None:
        pack = json.loads(PACK_PATH.read_text(encoding="utf-8"))
        first = compile_esso_ir(pack)
        second = compile_esso_ir(pack)
        self.assertEqual(first.model_sha256, second.model_sha256)
        self.assertEqual(first.ir, second.ir)
        self.assertEqual(first.ir["ir_version"], "esso-ir/v1")
        self.assertEqual(first.verification_status.status, "NOT_RUN")
        self.assertEqual(first.verification_status.model_sha256, first.model_sha256)
        self.assertTrue(first.ir["observables"]["state_vars"])
        self.assertIn("receipt_sha256", first.ir["observables"]["effects"])
        self.assertIn("inv_coherent_obligation_implies_permission", {item["id"] for item in first.ir["invariants"]})
        self.assertIn("inv_conflict_fail_closed_mask", {item["id"] for item in first.ir["invariants"]})
        self.assertIn("inv_incomplete_context_fail_closed_mask", {item["id"] for item in first.ir["invariants"]})
        self.assertTrue(any(item["type"]["kind"] == "enum" for item in first.ir["types"]))
        self.assertTrue(any(item["type"].get("kind") == "bool" for item in first.ir["state_vars"]))

    def test_esso_adapter_canonicalizes_order_and_rejects_mixed_profiles(self) -> None:
        first_result = evaluate(make_packet(decision_id="case:one", allow_abstain=True))
        second_result = evaluate(make_packet(decision_id="case-two", allow_abstain=True))
        forward = compile_esso_ir([first_result, second_result])
        reverse = compile_esso_ir([second_result, first_result])
        self.assertEqual(forward.model_sha256, reverse.model_sha256)
        self.assertTrue(all(":" not in action["id"] for action in forward.ir["actions"]))

        alternate = dict(NEUTRAL_EVIDENCE_COMPLETION_POLICY_PROFILE.to_data())
        alternate["profile_id"] = "neutral-evidence-completion-copy"
        alternate_result = evaluate(
            make_packet(
                decision_id="case-three",
                allow_abstain=True,
                policy_profile=alternate,
            )
        )
        with self.assertRaises(DeonticKernelError):
            compile_esso_ir([first_result, alternate_result])

    def test_esso_verification_status_is_fail_closed_and_hash_bound(self) -> None:
        profile = compile_esso_ir(json.loads(PACK_PATH.read_text(encoding="utf-8")))
        no_evidence_pass = ESSOVerificationStatus(
            model_sha256=profile.model_sha256,
            tool="ESSO",
            commands=(),
            results=(),
            status="PASS",
        )
        self.assertEqual(no_evidence_pass.status, "FAIL")

        mismatch = ESSOVerificationStatus(
            model_sha256="0" * 64,
            tool="ESSO",
            commands=("python -m ESSO validate /tmp/model.yaml",),
            results=({"ok": True},),
            status="PASS",
        )
        bound = bind_esso_verification_status(profile, mismatch)
        self.assertEqual(bound.verification_status.status, "FAIL")
        self.assertEqual(bound.verification_status.model_sha256, profile.model_sha256)
        self.assertIn("different model hash", bound.verification_status.reason)

        incomplete_evidence = ESSOVerificationStatus(
            model_sha256=profile.model_sha256,
            tool="ESSO",
            commands=("python -m ESSO verify-multi /tmp/model.yaml --solvers z3,cvc5",),
            results=({"ok": True, "verdict": "VERIFIED"},),
            status="PASS",
        )
        self.assertEqual(incomplete_evidence.status, "FAIL")

        evidence = ESSOVerificationStatus(
            model_sha256=profile.model_sha256,
            tool="ESSO",
            commands=(
                "python -m ESSO guide --input /tmp/model.yaml --goal verify",
                "python -m ESSO validate /tmp/model.yaml",
                "python -m ESSO verify-multi /tmp/model.yaml --solvers z3,cvc5",
            ),
            results=(
                {"command": "guide", "ok": True},
                {"command": "validate", "ok": True, "errors": []},
                {
                    "command": "verify-multi",
                    "ok": True,
                    "verdict": "VERIFIED",
                    "determinism": True,
                    "solvers_agreed": True,
                    "failed_queries": 0,
                    "inconclusive_queries": 0,
                    "passed_queries": 7,
                    "total_queries": 7,
                    "solvers": ["z3", "cvc5"],
                },
            ),
            status="PASS",
        )
        self.assertEqual(evidence.status, "PASS")
        self.assertEqual(evidence.to_data()["status"], "PASS")

    def test_canonical_json_is_stable(self) -> None:
        self.assertEqual(
            canonical_json_bytes({"b": 2, "a": 1}),
            b'{"a":1,"b":2}',
        )


if __name__ == "__main__":
    unittest.main()
