from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from methodlib import (  # noqa: E402
    DataError,
    project_policy_digest,
    read_json,
    validate_project_policy,
)


class ProjectPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.authorities = read_json(ROOT / "evals/fixtures/authorities.json")

    def policy(self, name: str = "software") -> dict[str, object]:
        return read_json(ROOT / f"evals/fixtures/policies/{name}.json")

    def test_all_accepted_fixture_policies_verify(self) -> None:
        for name in ("software", "operations", "research"):
            with self.subTest(name=name):
                result = validate_project_policy(
                    self.policy(name), self.authorities
                )
                self.assertTrue(result["accepted"])
                self.assertEqual(result["policy_id"], name)

    def test_policy_mutation_invalidates_acceptance(self) -> None:
        policy = self.policy()
        policy["policy"]["reporting"] = "a changed destination"
        with self.assertRaisesRegex(DataError, "digest is stale"):
            validate_project_policy(policy, self.authorities)

    def test_acceptance_metadata_must_match_external_receipt(self) -> None:
        policy = self.policy()
        policy["acceptance"]["accepted_by"] = "another actor"
        with self.assertRaisesRegex(DataError, "receipt does not match"):
            validate_project_policy(policy, self.authorities)

    def test_malformed_unrelated_authority_receipt_fails_closed(self) -> None:
        authorities = copy.deepcopy(self.authorities)
        authorities["approval:malformed"] = {"policy_id": "software"}
        with self.assertRaisesRegex(DataError, "fields must be exactly"):
            validate_project_policy(self.policy(), authorities)

    def test_draft_cannot_resolve_as_accepted(self) -> None:
        policy = self.policy()
        policy["acceptance"]["status"] = "draft"
        with self.assertRaisesRegex(DataError, "must be accepted"):
            validate_project_policy(policy, self.authorities)

    def test_unknown_and_duplicate_fields_fail_closed(self) -> None:
        policy = self.policy()
        policy["unreviewed"] = True
        with self.assertRaisesRegex(DataError, "fields must be exactly"):
            validate_project_policy(policy, self.authorities)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text('{"policy_id":"a","policy_id":"b"}', encoding="utf-8")
            with self.assertRaisesRegex(DataError, "duplicate JSON field"):
                read_json(path)
            path.write_text('{"value": NaN}', encoding="utf-8")
            with self.assertRaisesRegex(DataError, "non-finite JSON"):
                read_json(path)

    def test_digest_excludes_acceptance_but_covers_all_policy(self) -> None:
        policy = self.policy()
        original = project_policy_digest(policy)
        changed_acceptance = copy.deepcopy(policy)
        changed_acceptance["acceptance"]["accepted_at"] = "later"
        self.assertEqual(project_policy_digest(changed_acceptance), original)
        changed_policy = copy.deepcopy(policy)
        changed_policy["policy"]["scope"].append("another boundary")
        self.assertNotEqual(project_policy_digest(changed_policy), original)

    def test_noncanonical_json_representation_has_same_digest(self) -> None:
        policy = self.policy()
        reparsed = json.loads(json.dumps(policy, indent=7, sort_keys=False))
        self.assertEqual(
            project_policy_digest(policy), project_policy_digest(reparsed)
        )


if __name__ == "__main__":
    unittest.main()
