from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from methodlib import read_json  # noqa: E402
from publish_eval import quadratic_weighted_kappa  # noqa: E402
from run_eval_batch import MAX_CALLS, call_plan, validate_manifest  # noqa: E402


class EvalBatchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = read_json(ROOT / "evals" / "manifest.json")

    def test_frozen_manifest_and_call_counts(self) -> None:
        manifest = validate_manifest(self.manifest)
        plan = call_plan(manifest)
        self.assertEqual(plan["calls"], 76)
        self.assertEqual(plan["decisions"], 64)
        self.assertEqual(plan["selections"], 12)
        self.assertLessEqual(plan["calls"], MAX_CALLS)

    def test_wrong_schema_unfrozen_or_budget_is_rejected(self) -> None:
        for field, value in (("schema_version", 2), ("frozen", False), ("call_budget", 77)):
            with self.subTest(field=field):
                changed = copy.deepcopy(self.manifest)
                changed[field] = value
                with self.assertRaises(Exception):
                    validate_manifest(changed)

    def test_default_runner_is_render_only(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "run_eval_batch.py")],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["mode"], "render-only")
        self.assertEqual(output["calls"], 76)

    def test_execution_requires_exact_explicit_budget_before_any_call(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "run_eval_batch.py"),
                    "--execute",
                    "--call-budget", "75",
                    "--output-dir", str(Path(directory) / "run"),
                    "--codex", "this-command-must-not-run",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--call-budget 76", result.stderr)

    def test_rendered_auto_decision_is_deferred_without_oracle_flags(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "run_eval_batch.py"),
                    "--render-dir", str(target),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            auto = list(target.glob("*-auto-decision.md"))
            self.assertEqual(len(auto), 12)
            self.assertTrue(all("Deferred same-session" in path.read_text() for path in auto))

    def test_human_reliability_metric(self) -> None:
        self.assertEqual(quadratic_weighted_kappa([9, 7, 4], [9, 7, 4]), 1.0)
        self.assertLess(quadratic_weighted_kappa([9, 9, 0, 0], [0, 0, 9, 9]), 0.8)


if __name__ == "__main__":
    unittest.main()
