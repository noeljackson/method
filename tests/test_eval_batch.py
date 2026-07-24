from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from methodlib import read_json  # noqa: E402
from publish_eval import (  # noqa: E402
    quadratic_weighted_kappa,
    validate_run_artifacts,
)
from render_eval import load_cases, render_decision  # noqa: E402
from run_eval_batch import MAX_CALLS, call_plan, validate_manifest  # noqa: E402


class EvalBatchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = read_json(ROOT / "evals/manifest.json")

    def test_manifest_stays_within_the_eight_call_ceiling(self) -> None:
        manifest = validate_manifest(self.manifest)
        plan = call_plan(manifest)
        self.assertGreater(plan["calls"], 0)
        self.assertEqual(plan["decisions"], plan["calls"])
        self.assertLessEqual(plan["calls"], 8)
        self.assertLessEqual(plan["calls"], MAX_CALLS)

    def test_budget_or_extra_samples_are_rejected(self) -> None:
        for field, value in (("call_budget", 9), ("samples_per_cell", 2)):
            changed = copy.deepcopy(self.manifest)
            changed[field] = value
            with self.subTest(field=field), self.assertRaises(Exception):
                validate_manifest(changed)

    def test_default_runner_is_render_only(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/run_eval_batch.py")],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["mode"], "render-only")
        self.assertLessEqual(output["calls"], 8)

    def test_execution_requires_exact_explicit_budget_before_any_call(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/run_eval_batch.py"),
                    "--execute",
                    "--call-budget",
                    "7",
                    "--output-dir",
                    str(Path(directory) / "run"),
                    "--codex",
                    "this-command-must-not-run",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--call-budget 8", result.stderr)

    def test_rendered_plan_contains_only_the_declared_sparse_decisions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "prompts"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/run_eval_batch.py"),
                    "--render-dir",
                    str(target),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                len(list(target.glob("*.md"))),
                call_plan(validate_manifest(self.manifest))["calls"],
            )

    def test_human_reliability_metric(self) -> None:
        self.assertEqual(quadratic_weighted_kappa([9, 7, 4], [9, 7, 4]), 1.0)
        self.assertLess(
            quadratic_weighted_kappa([9, 9, 0, 0], [0, 0, 9, 9]), 0.7
        )

    def test_run_artifacts_cannot_be_remapped_after_execution(self) -> None:
        manifest = validate_manifest(self.manifest)
        plan = call_plan(manifest)["items"]
        cases = load_cases()
        records = []
        mapping = {}
        for index, call in enumerate(plan, start=1):
            response_id = f"response-{index:02d}"
            prompt = render_decision(cases[call["case_id"]], call["arm"])
            records.append(
                {
                    **call,
                    "response_id": response_id,
                    "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                    "prompt_words": len(prompt.split()),
                    "elapsed_seconds": 1.0,
                    "value": {},
                }
            )
            mapping[response_id] = call
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory)
            for name, value in (
                ("records.json", records),
                ("blind-map.json", mapping),
            ):
                (run_dir / name).write_text(
                    json.dumps(value, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
            run = {
                "batch": manifest,
                "artifacts": {
                    name: hashlib.sha256((run_dir / name).read_bytes()).hexdigest()
                    for name in ("records.json", "blind-map.json")
                },
            }
            validate_run_artifacts(run_dir, run, records, mapping)
            first, second = "response-01", "response-02"
            mapping[first], mapping[second] = mapping[second], mapping[first]
            (run_dir / "blind-map.json").write_text(
                json.dumps(mapping, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            run["artifacts"]["blind-map.json"] = hashlib.sha256(
                (run_dir / "blind-map.json").read_bytes()
            ).hexdigest()
            with self.assertRaisesRegex(Exception, "record, blind map, and plan"):
                validate_run_artifacts(run_dir, run, records, mapping)


if __name__ == "__main__":
    unittest.main()
