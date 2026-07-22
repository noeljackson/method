from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class NormativeContractTests(unittest.TestCase):
    def test_profile_acceptance_and_nonwaivable_core_are_normative(self) -> None:
        contracts = (ROOT / "src" / "40-contracts.md").read_text(encoding="utf-8")
        preamble = (ROOT / "src" / "00-preamble.md").read_text(encoding="utf-8")
        for field in (
            "`profile_status`", "`authority_source`", "`profile_digest`",
            "`accepted_by`", "`accepted_at`", "`acceptance_receipt`",
        ):
            self.assertIn(field, contracts)
        self.assertIn("non-waivable hard core", preamble)
        self.assertIn("labeled nonconforming fork", preamble)
        self.assertNotIn("DeviationReceipt", contracts)

    def test_program_contract_represents_concurrency_and_termination(self) -> None:
        vocabulary = (ROOT / "src" / "20-vocabulary.md").read_text(encoding="utf-8")
        contracts = (ROOT / "src" / "40-contracts.md").read_text(encoding="utf-8")
        template = (ROOT / "templates" / "program-control.md").read_text(encoding="utf-8")
        self.assertIn("`active_coordinates`", contracts)
        self.assertIn("`accepted_frontiers`", contracts)
        self.assertNotIn("`current_coordinate`", contracts)
        self.assertNotIn("`accepted_boundary`", contracts)
        for disposition in ("OWNER_CANCELLED", "ABANDONED", "SUPERSEDED", "SAFETY"):
            self.assertIn(disposition, vocabulary)
            self.assertIn(disposition, template)
        self.assertIn("A terminated control cannot resume", template)

    def test_emergency_containment_does_not_resume_program_lane(self) -> None:
        core = (ROOT / "src" / "10-core.md").read_text(encoding="utf-8")
        program = (ROOT / "protocols" / "program.md").read_text(encoding="utf-8")
        self.assertIn("separate pre-existing\nauthority", core)
        self.assertIn("program remains `STOPPED_FOR_REPLAN`", program)

    def test_secret_recovery_closes_path_and_context(self) -> None:
        secrets = (ROOT / "protocols" / "secrets.md").read_text(encoding="utf-8")
        for phrase in (
            "non-secret canary or dry run",
            "continue only in a clean context",
            "authorized quarantine",
            "profile-approved destination-encrypted envelope",
        ):
            self.assertIn(phrase, secrets)


if __name__ == "__main__":
    unittest.main()
