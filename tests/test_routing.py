from __future__ import annotations

import copy
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from methodlib import (  # noqa: E402
    DataError,
    context_spec,
    read_json,
    resolve_context_modules,
    resolve_runtime_envelope,
    validate_module_name,
    validate_program_control,
)
from render_eval import load_cases  # noqa: E402


class RoutingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.authorities = read_json(ROOT / "evals/fixtures/authorities.json")
        self.cases = load_cases()

    def resolve(self, case_id: str, flags: object | None = None) -> dict[str, object]:
        case = self.cases[case_id]
        profile = read_json(
            ROOT / f"evals/fixtures/profiles/{case['profile']}.json"
        )
        task = read_json(ROOT / f"evals/fixtures/tasks/{case['task']}.json")
        return resolve_runtime_envelope(profile, self.authorities, task, flags)

    def test_every_case_routes_exactly_from_structured_signals(self) -> None:
        for case_id, case in self.cases.items():
            with self.subTest(case_id=case_id):
                self.assertEqual(
                    self.resolve(case_id)["protocols"], case["expected_protocols"]
                )

    def test_model_may_only_escalate_protocols(self) -> None:
        envelope = self.resolve(
            "direct-bounded-edit",
            {"program": False, "experiment": False, "secrets": True},
        )
        self.assertEqual(envelope["protocols"], ["secrets"])
        with self.assertRaises(DataError):
            self.resolve(
                "direct-bounded-edit",
                {"program": False, "experiment": False},
            )

    def test_requested_actions_and_gates_fail_closed(self) -> None:
        case = self.cases["direct-bounded-edit"]
        profile = read_json(ROOT / "evals/fixtures/profiles/software.json")
        task = read_json(ROOT / f"evals/fixtures/tasks/{case['task']}.json")
        unknown_action = copy.deepcopy(task)
        unknown_action["requested_actions"].append("deployment.mutate")
        with self.assertRaisesRegex(DataError, "not allowed"):
            resolve_runtime_envelope(profile, self.authorities, unknown_action)
        unknown_gate = copy.deepcopy(task)
        unknown_gate["required_gates"].append("imaginary-gate")
        with self.assertRaisesRegex(DataError, "unknown gates"):
            resolve_runtime_envelope(profile, self.authorities, unknown_gate)

    def test_program_route_requires_a_control_reference(self) -> None:
        case = self.cases["program-revoked-repair"]
        profile = read_json(ROOT / "evals/fixtures/profiles/operations.json")
        task = read_json(ROOT / f"evals/fixtures/tasks/{case['task']}.json")
        task["resource_refs"] = [
            reference
            for reference in task["resource_refs"]
            if not reference.startswith("program-control:")
        ]
        with self.assertRaisesRegex(DataError, "program-control"):
            resolve_runtime_envelope(profile, self.authorities, task)

    def test_envelope_is_compact_and_controls_are_progressive(self) -> None:
        direct = self.resolve("direct-bounded-edit")
        self.assertEqual(
            set(direct),
            {
                "schema_version",
                "method_version",
                "task_id",
                "profile_verified",
                "policy_ref",
                "canonical_sources",
                "authority",
                "forbidden",
                "protocols",
                "required_gates",
                "controls",
            },
        )
        self.assertEqual(set(direct["controls"]), {"reporting"})
        secret = self.resolve("secrets-known-exposure")
        self.assertIn("secrets", secret["controls"])
        self.assertNotIn("program_repair_authority", secret["controls"])
        interaction = self.resolve("interaction-program-secret")
        self.assertIn("secrets", interaction["controls"])
        self.assertIn("program_repair_authority", interaction["controls"])

    def test_module_resolution_order_and_path_validation(self) -> None:
        modules = resolve_context_modules(["secrets", "program"])
        self.assertEqual(
            modules, ["protocols/program.md", "protocols/secrets.md"]
        )
        allowed = set(modules)
        self.assertEqual(
            validate_module_name("protocols/program.md", allowed),
            "protocols/program.md",
        )
        with self.assertRaises(DataError):
            validate_module_name("../KERNEL.md", allowed)
        malformed = copy.deepcopy(context_spec())
        malformed["protocols"]["program"]["module"] = "../../outside.md"
        with self.assertRaisesRegex(DataError, "unsafe modular-pack path"):
            resolve_context_modules(["program"], malformed)

    def test_terminal_program_control_cannot_dispatch(self) -> None:
        control = read_json(ROOT / "templates/program-control.json")
        control["state"] = "COMPLETE"
        control["active_coordinates"] = []
        control["authorized_queue"] = []
        validate_program_control(control)
        control["authorized_queue"] = ["late work"]
        with self.assertRaisesRegex(DataError, "cannot dispatch"):
            validate_program_control(control)

    def test_packaged_resolver_is_self_contained(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            isolated = Path(directory) / "method-runtime"
            shutil.copytree(ROOT / "dist/pack", isolated)
            result = subprocess.run(
                [
                    sys.executable,
                    str(isolated / "tools/noel_method.py"),
                    "resolve",
                    "--profile",
                    str(ROOT / "evals/fixtures/profiles/software.json"),
                    "--authorities",
                    str(ROOT / "evals/fixtures/authorities.json"),
                    "--task",
                    str(ROOT / "evals/fixtures/tasks/direct-bounded-edit.json"),
                ],
                cwd=isolated,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"profile_verified": true', result.stdout)

    def test_active_program_control_requires_reconciliation_and_gates(self) -> None:
        control = read_json(ROOT / "templates/program-control.json")
        control["state"] = "ACTIVE"
        with self.assertRaisesRegex(DataError, "reconciliation receipt"):
            validate_program_control(control)

    def test_satisfied_program_gate_requires_a_receipt(self) -> None:
        control = read_json(ROOT / "templates/program-control.json")
        control["hard_gates"] = [
            {
                "id": "release-evidence",
                "state": "SATISFIED",
                "evidence_receipt": {},
            }
        ]
        with self.assertRaisesRegex(DataError, "requires evidence receipt"):
            validate_program_control(control)


if __name__ == "__main__":
    unittest.main()
