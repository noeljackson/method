from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from render_eval import load_cases, render_decision, render_key  # noqa: E402
from score_eval import score_decision  # noqa: E402


class EvalToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cases = load_cases()

    def test_suite_is_small_but_covers_all_protocol_families(self) -> None:
        self.assertEqual(len(self.cases), 8)
        selected = {
            protocol
            for case in self.cases.values()
            for protocol in case["expected_protocols"]
        }
        self.assertEqual(selected, {"program", "experiment", "secrets"})

    def test_prompts_never_include_evaluator_only_metadata(self) -> None:
        for case in self.cases.values():
            for mode in ("neutral", "kernel", "routed", "wrong", "monolith"):
                with self.subTest(case=case["id"], mode=mode):
                    prompt = render_decision(case, mode)
                    self.assertNotIn(case["id"], prompt)
                    self.assertNotIn(case["expected"]["decision"], prompt)
                    for item in case["expected"]["required"]:
                        self.assertNotIn(item["id"], prompt)
                    for item in case["forbidden"]:
                        self.assertNotIn(item["id"], prompt)

    def test_routed_and_wrong_modes_load_only_named_modules(self) -> None:
        case = self.cases["interaction-program-secret"]
        routed = render_decision(case, "routed")
        self.assertIn("dist/pack/protocols/program.md", routed)
        self.assertIn("dist/pack/protocols/secrets.md", routed)
        self.assertNotIn("dist/pack/protocols/experiment.md", routed)
        wrong = render_decision(case, "wrong")
        self.assertIn("dist/pack/protocols/program.md", wrong)
        self.assertNotIn("dist/pack/protocols/secrets.md", wrong)
        self.assertNotIn("fixture credential-response owner", wrong)
        neutral = render_decision(case, "neutral")
        self.assertNotIn("dist/pack/KERNEL.md", neutral)

    def test_context_sizes_remain_bounded(self) -> None:
        direct = render_decision(self.cases["direct-bounded-edit"], "routed")
        interaction = render_decision(
            self.cases["interaction-program-secret"], "routed"
        )
        monolith = render_decision(
            self.cases["interaction-program-secret"], "monolith"
        )
        self.assertLess(len(direct.split()), 1300)
        self.assertLess(len(interaction.split()), 2100)
        self.assertLess(len(interaction.split()), len(monolith.split()))

    def test_key_is_separate_and_contains_expected_answer(self) -> None:
        case = self.cases["core-authority-boundary"]
        key = render_key(case)
        self.assertIn(case["expected"]["decision"], key)
        self.assertNotIn(case["expected"]["decision"], render_decision(case, "routed"))

    def test_decision_score_is_nine_points_with_forbidden_hard_failure(self) -> None:
        case = self.cases["core-authority-boundary"]
        judgment = {
            "decision_match": True,
            "evidence_integrity": {
                "observation_inference": True,
                "identity_binding": True,
                "material_limitations": True,
            },
            "required": {
                item["id"]: True for item in case["expected"]["required"]
            },
            "forbidden": {item["id"]: "rejected" for item in case["forbidden"]},
        }
        self.assertEqual(score_decision(case, judgment)["content_points"], 9)
        judgment["forbidden"]["forbidden-1"] = "endorsed"
        self.assertTrue(score_decision(case, judgment)["hard_failure"])


if __name__ == "__main__":
    unittest.main()
