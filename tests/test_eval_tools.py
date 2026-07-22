from __future__ import annotations

import json
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from render_eval import expected_flags, load_cases  # noqa: E402
from score_eval import score_decision, score_selection  # noqa: E402


def render(case_id: str, *arguments: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "render_eval.py"), case_id, *arguments],
        cwd=ROOT,
        text=True,
        input=input_text,
        capture_output=True,
        check=False,
    )


class EvalToolTests(unittest.TestCase):
    def test_active_suite_has_only_the_ten_frozen_cases(self) -> None:
        cases = load_cases()
        self.assertEqual(len(cases), 10)
        self.assertEqual(
            Counter(case["family"] for case in cases.values()),
            Counter({"core": 4, "program": 2, "experiment": 2, "secrets": 2}),
        )

    def test_selection_prompt_contains_no_answer_key(self) -> None:
        case = load_cases()["secrets-bearer-reference"]
        result = render(case["id"], "--stage", "selection")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(case["expected"]["decision"], result.stdout)
        for item in case["forbidden"]:
            self.assertNotIn(item["predicate"], result.stdout)

    def test_base_and_explicit_protocol_context_are_distinct(self) -> None:
        case_id = "secrets-exposure-recovery"
        base = render(case_id, "--stage", "decision", "--mode", "base")
        explicit = render(case_id, "--stage", "decision", "--mode", "explicit")
        self.assertEqual(base.returncode, 0, base.stderr)
        self.assertEqual(explicit.returncode, 0, explicit.stderr)
        self.assertIn("dist/pack/BASE.md", base.stdout)
        self.assertNotIn("dist/pack/protocols/secrets.md", base.stdout)
        self.assertIn("dist/pack/protocols/secrets.md", explicit.stdout)

    def test_auto_context_consumes_actual_flags(self) -> None:
        case_id = "program-owner-cancellation"
        omitted = render(
            case_id,
            "--stage", "decision", "--mode", "auto",
            input_text=json.dumps({"program": False, "experiment": False, "secrets": False}),
        )
        selected = render(
            case_id,
            "--stage", "decision", "--mode", "auto",
            input_text=json.dumps({"program": True, "experiment": False, "secrets": False}),
        )
        self.assertEqual(omitted.returncode, 0, omitted.stderr)
        self.assertEqual(selected.returncode, 0, selected.stderr)
        self.assertNotIn("dist/pack/protocols/program.md", omitted.stdout)
        self.assertIn("dist/pack/protocols/program.md", selected.stdout)

    def test_auto_rejects_malformed_flags(self) -> None:
        result = render(
            "program-owner-cancellation",
            "--stage", "decision", "--mode", "auto",
            input_text=json.dumps({"program": True}),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ContextFlags fields", result.stderr)

    def test_same_session_continuation_does_not_repeat_base_or_facts(self) -> None:
        case = load_cases()["experiment-contaminated-state"]
        result = render(
            case["id"],
            "--stage", "decision", "--mode", "auto", "--continuation",
            input_text=json.dumps(expected_flags(case)),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("dist/pack/BASE.md", result.stdout)
        self.assertNotIn("## Situation", result.stdout)
        self.assertIn("dist/pack/protocols/experiment.md", result.stdout)

    def test_neutral_arm_has_authority_brief_but_no_method(self) -> None:
        result = render(
            "core-authority-bootstrap", "--stage", "decision", "--mode", "neutral"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("neutral-briefs/software.md", result.stdout)
        self.assertNotIn("dist/pack/BASE.md", result.stdout)

    def test_selection_scoring_checks_exactness_and_required_recall(self) -> None:
        case = load_cases()["secrets-bearer-reference"]
        exact = score_selection(case, expected_flags(case))
        self.assertTrue(exact["exact"])
        missed = score_selection(
            case, {"program": False, "experiment": False, "secrets": False}
        )
        self.assertFalse(missed["exact"])
        self.assertFalse(missed["required_protocol_recalled"])

    def test_decision_score_has_nine_content_points_and_no_rule_score(self) -> None:
        case = load_cases()["core-descriptive-normative"]
        judgment = {
            "decision_match": True,
            "evidence_integrity": {
                "observation_inference": True,
                "identity_binding": True,
                "material_limitations": True,
            },
            "required": {item["id"]: True for item in case["expected"]["required"]},
            "forbidden": {item["id"]: "rejected" for item in case["forbidden"]},
        }
        result = score_decision(case, judgment)
        self.assertEqual(result["content_points"], 9)
        self.assertNotIn("rule_traceability", result)
        judgment["forbidden"]["forbidden-1"] = "endorsed"
        self.assertTrue(score_decision(case, judgment)["hard_failure"])


if __name__ == "__main__":
    unittest.main()
