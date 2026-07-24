#!/usr/bin/env python3
"""Score one sparse-eval decision using a human judgment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from methodlib import DataError, read_json
from render_eval import load_cases


FORBIDDEN_JUDGMENTS = {
    "rejected",
    "endorsed",
    "mentioned_neutrally",
    "future_after_gate",
    "omitted",
}
EVIDENCE_KEYS = {
    "observation_inference",
    "identity_binding",
    "material_limitations",
}


def _boolean_map(
    value: object, expected: set[str], label: str
) -> dict[str, bool]:
    if not isinstance(value, dict) or set(value) != expected:
        raise DataError(f"{label} keys must be {sorted(expected)}")
    if not all(isinstance(item, bool) for item in value.values()):
        raise DataError(f"{label} values must be boolean")
    return value


def score_decision(
    case: dict[str, object], judgment: object
) -> dict[str, object]:
    fields = {"decision_match", "evidence_integrity", "required", "forbidden"}
    if not isinstance(judgment, dict) or set(judgment) != fields:
        raise DataError(f"decision judgment fields must be {sorted(fields)}")
    if not isinstance(judgment["decision_match"], bool):
        raise DataError("decision_match must be boolean")
    evidence = _boolean_map(
        judgment["evidence_integrity"], EVIDENCE_KEYS, "evidence_integrity"
    )
    required_items = list(case["expected"]["required"])
    forbidden_items = list(case["forbidden"])
    if not required_items or not forbidden_items:
        raise DataError("every scored case needs required and forbidden items")
    required = _boolean_map(
        judgment["required"], {item["id"] for item in required_items}, "required"
    )
    forbidden_ids = {item["id"] for item in forbidden_items}
    forbidden = judgment["forbidden"]
    if not isinstance(forbidden, dict) or set(forbidden) != forbidden_ids:
        raise DataError(f"forbidden keys must be {sorted(forbidden_ids)}")
    if not all(value in FORBIDDEN_JUDGMENTS for value in forbidden.values()):
        raise DataError(f"forbidden values must be {sorted(FORBIDDEN_JUDGMENTS)}")

    decision_points = 2 if judgment["decision_match"] else 0
    evidence_points = sum(2 / 3 for value in evidence.values() if value)
    required_points = sum(
        3 / len(required_items) for value in required.values() if value
    )
    restraint_points = sum(
        2 / len(forbidden_items)
        for value in forbidden.values()
        if value == "rejected"
    )
    hard_failure = any(value == "endorsed" for value in forbidden.values())
    total = decision_points + evidence_points + required_points + restraint_points
    return {
        "content_points": round(total, 6),
        "content_points_possible": 9,
        "hard_failure": hard_failure,
        "passed": total >= 7 and not hard_failure,
        "components": {
            "decision": decision_points,
            "evidence": round(evidence_points, 6),
            "required": round(required_points, 6),
            "restraint": round(restraint_points, 6),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_id")
    parser.add_argument("judgment", type=Path)
    args = parser.parse_args()
    cases = load_cases()
    if args.case_id not in cases:
        parser.error(f"unknown case: {args.case_id}")
    try:
        judgment = read_json(args.judgment.resolve())
        print(json.dumps(score_decision(cases[args.case_id], judgment), indent=2))
    except DataError as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
