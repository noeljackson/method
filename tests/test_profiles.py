from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from methodlib import DataError, read_json, validate_accepted_profile  # noqa: E402


class ProfileAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.authorities = read_json(ROOT / "evals" / "fixtures" / "authorities.json")
        cls.path = ROOT / "evals" / "fixtures" / "profiles" / "software.md"
        cls.text = cls.path.read_text(encoding="utf-8")

    def test_independent_fixture_receipt_is_accepted(self) -> None:
        metadata = validate_accepted_profile(self.text, "software", self.authorities)
        self.assertEqual(metadata["status"], "ACCEPTED")

    def test_draft_profile_is_rejected(self) -> None:
        draft = self.text.replace("Profile status: `ACCEPTED`", "Profile status: `DRAFT`")
        with self.assertRaisesRegex(DataError, "status must be ACCEPTED"):
            validate_accepted_profile(draft, "software", self.authorities)

    def test_changed_profile_body_invalidates_acceptance(self) -> None:
        changed = self.text.replace("Synthetic software decision evals", "Changed software decision evals")
        with self.assertRaisesRegex(DataError, "digest is stale"):
            validate_accepted_profile(changed, "software", self.authorities)

    def test_missing_or_forged_receipt_is_rejected(self) -> None:
        with self.assertRaisesRegex(DataError, "receipt does not match"):
            validate_accepted_profile(self.text, "software", {})


if __name__ == "__main__":
    unittest.main()
