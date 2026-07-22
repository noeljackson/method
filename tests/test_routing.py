from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import methodlib  # noqa: E402


class ContextTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = methodlib.context_spec()

    def test_empty_flags_load_no_optional_protocol(self) -> None:
        self.assertEqual(
            methodlib.resolve_context_modules(methodlib.empty_context_flags(), self.spec), []
        )

    def test_all_flags_preserve_canonical_module_order(self) -> None:
        flags = {"secrets": True, "experiment": True, "program": True}
        self.assertEqual(
            methodlib.resolve_context_modules(flags, self.spec),
            [
                "protocols/program.md",
                "protocols/experiment.md",
                "protocols/secrets.md",
            ],
        )

    def test_merge_is_monotonic(self) -> None:
        caller = {"program": True, "experiment": False, "secrets": False}
        profile = {"program": False, "experiment": False, "secrets": True}
        model = {"program": False, "experiment": True, "secrets": False}
        self.assertEqual(
            methodlib.merge_context_flags(caller, profile, model),
            {"program": True, "experiment": True, "secrets": True},
        )

    def test_later_false_cannot_clear_caller_or_profile_true(self) -> None:
        enabled = {"program": True, "experiment": False, "secrets": True}
        all_false = methodlib.empty_context_flags()
        self.assertEqual(methodlib.merge_context_flags(enabled, all_false), enabled)

    def test_malformed_flags_fail_closed(self) -> None:
        malformed = [
            {},
            {"program": False, "experiment": False},
            {"program": False, "experiment": False, "secrets": False, "extra": False},
            {"program": 0, "experiment": False, "secrets": False},
            [False, False, False],
        ]
        for value in malformed:
            with self.subTest(value=value):
                with self.assertRaises(methodlib.DataError):
                    methodlib.validate_context_flags(value)

    def test_generated_context_matches_source(self) -> None:
        generated = methodlib.read_json(ROOT / "dist" / "pack" / "CONTEXT.json")
        self.assertEqual(generated["schema_version"], self.spec["schema_version"])
        self.assertEqual(generated["flags"], self.spec["flags"])

    def test_invalid_profile_fails_and_index_requires_bootstrap(self) -> None:
        profile = ROOT / "evals" / "fixtures" / "profiles" / "software.md"
        authorities = methodlib.read_json(ROOT / "evals" / "fixtures" / "authorities.json")
        text = profile.read_text(encoding="utf-8").replace(
            "Profile status: `ACCEPTED`", "Profile status: `DRAFT`"
        )
        with self.assertRaises(methodlib.DataError):
            methodlib.validate_accepted_profile(text, "software", authorities)
        index = (ROOT / "dist" / "pack" / "INDEX.md").read_text(encoding="utf-8")
        self.assertIn("artifacts/project-profile.md", index)
        self.assertIn("remain read-only", index)

    def test_unsafe_duplicate_directory_and_symlink_paths_are_rejected(self) -> None:
        allowed = set(self.spec["module_order"])
        for value in ("../../evals/RUBRIC.md", "/etc/passwd", "protocols/../BASE.md"):
            with self.subTest(value=value):
                with self.assertRaises(methodlib.DataError):
                    methodlib.validate_module_name(value, allowed | {value})
        with self.assertRaises(methodlib.DataError):
            methodlib.validate_module_list(
                ["protocols/program.md", "protocols/program.md"], allowed
            )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "directory").mkdir()
            outside = root.parent / f"{root.name}-outside.md"
            outside.write_text("outside", encoding="utf-8")
            try:
                (root / "link.md").symlink_to(outside)
                with patch.object(methodlib, "PACK", root):
                    for value in ("directory", "link.md"):
                        with self.assertRaises(methodlib.DataError):
                            methodlib.validate_module_name(value, {value})
            finally:
                outside.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
