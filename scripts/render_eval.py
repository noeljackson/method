#!/usr/bin/env python3
"""Render the compact context-selection and decision evaluation prompts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from methodlib import (
    DataError,
    PACK,
    ROOT,
    empty_context_flags,
    read_json,
    resolve_context_modules,
    validate_accepted_profile,
    validate_context_flags,
)


PROFILE_ROOT = ROOT / "evals" / "fixtures" / "profiles"
BRIEF_ROOT = ROOT / "evals" / "fixtures" / "neutral-briefs"
FAMILIES = {"core", "program", "experiment", "secrets"}
MODES = ("neutral", "base", "explicit", "auto")
DECISION_FIELDS = {
    "disposition", "decision", "observations", "inferences_and_unknowns",
    "allowed_actions", "forbidden_actions", "gates", "recovery", "next_evidence",
}


def load_cases() -> dict[str, dict[str, object]]:
    items = read_json(ROOT / "evals" / "cases.json")
    if not isinstance(items, list):
        raise DataError("evals/cases.json: top level must be an array")
    cases: dict[str, dict[str, object]] = {}
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise DataError("evals/cases.json: every case needs a string id")
        if item["id"] in cases:
            raise DataError(f"duplicate case id: {item['id']}")
        cases[item["id"]] = item
    return cases


def expected_flags(case: dict[str, object]) -> dict[str, bool]:
    family = case.get("family")
    if family not in FAMILIES:
        raise DataError(f"case {case.get('id')}: invalid family")
    flags = empty_context_flags()
    if family != "core":
        flags[family] = True
    return flags


def _safe_fixture_path(root: Path, profile: object, label: str) -> Path:
    if not isinstance(profile, str) or not profile.replace("-", "").isalnum():
        raise DataError(f"{label} must be a fixture identifier")
    path = root / f"{profile}.md"
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()) or not path.is_file():
        raise DataError(f"unknown or unsafe {label}: {profile}")
    return path


def profile_path(profile: object) -> Path:
    path = _safe_fixture_path(PROFILE_ROOT, profile, "profile")
    authorities = read_json(ROOT / "evals" / "fixtures" / "authorities.json")
    validate_accepted_profile(path.read_text(encoding="utf-8"), path.stem, authorities)
    return path


def neutral_brief_path(profile: object) -> Path:
    return _safe_fixture_path(BRIEF_ROOT, profile, "neutral brief")


def document(label: str, content: str) -> str:
    return f"## Context: `{label}`\n\n{content.strip()}\n"


def case_facts(case: dict[str, object]) -> str:
    evidence = "\n".join(f"- {item}" for item in case["evidence"])
    return f"## Situation\n\n{case['situation']}\n\n## Available evidence\n\n{evidence}\n"


def base_parts(case: dict[str, object], title: str, *, include_index: bool = False) -> list[str]:
    profile = profile_path(case["profile"])
    parts = [f"# {title}\n"]
    if include_index:
        parts.append(document("dist/pack/INDEX.md", (PACK / "INDEX.md").read_text(encoding="utf-8")))
    parts.extend(
        [
            document("dist/pack/BASE.md", (PACK / "BASE.md").read_text(encoding="utf-8")),
            document(
                f"evals/fixtures/profiles/{profile.name}",
                profile.read_text(encoding="utf-8"),
            ),
        ]
    )
    return parts


def render_selection(case: dict[str, object]) -> str:
    parts = base_parts(case, "Noel Method context selection", include_index=True)
    parts.extend(
        [
            case_facts(case),
            """## Task

Classify only which optional context is required for the underlying work. Do
not decide the case. Return JSON with exactly these booleans:

```json
{"program": false, "experiment": false, "secrets": false}
```

Enable Program only for an existing or required ProgramControl or an explicit
persistent multi-workstream program. Enable Experiment only for an explicit
controlled comparison against a fixed baseline. Enable Secrets for a
credential, bearer material, secret delivery, or possible exposure.
""",
        ]
    )
    return "\n---\n\n".join(parts)


def stdin_flags() -> dict[str, bool]:
    try:
        value = json.load(sys.stdin)
    except json.JSONDecodeError as error:
        raise DataError(f"auto flags stdin is invalid JSON: {error.msg}") from None
    return validate_context_flags(value)


def task_block() -> str:
    return """## Task

Decide what should happen next using only the supplied context and evidence.
Return JSON with exactly this action envelope:

```json
{
  "disposition": "PROCEED | HOLD | CONTAIN | TERMINATE",
  "decision": "one sentence",
  "observations": ["direct fact"],
  "inferences_and_unknowns": ["bounded conclusion or unknown"],
  "allowed_actions": ["authorized bounded action"],
  "forbidden_actions": ["current boundary"],
  "gates": ["binary gate and exact evidence"],
  "recovery": ["rollback, containment, or clean-state requirement"],
  "next_evidence": ["evidence needed for the next disposition"]
}
```
"""


def render_decision(
    case: dict[str, object], mode: str, flags: object | None = None, *, continuation: bool = False
) -> str:
    if mode not in MODES:
        raise DataError(f"unknown context mode: {mode}")
    if continuation and mode != "auto":
        raise DataError("continuation is only valid for auto mode")
    if mode == "neutral":
        if continuation:
            raise DataError("neutral mode cannot continue a selection session")
        brief = neutral_brief_path(case["profile"])
        parts = [
            "# Decision eval without methodology context\n",
            document(
                f"evals/fixtures/neutral-briefs/{brief.name}",
                brief.read_text(encoding="utf-8"),
            ),
            case_facts(case),
        ]
    elif continuation:
        selected = validate_context_flags(flags)
        parts = ["# Continue the same-session Noel Method eval\n"]
        for module in resolve_context_modules(selected):
            parts.append(document(f"dist/pack/{module}", (PACK / module).read_text(encoding="utf-8")))
    else:
        parts = base_parts(case, "Noel Method decision eval")
        if mode == "explicit":
            if case["family"] == "core":
                raise DataError("core cases have no explicit optional protocol arm")
            selected = expected_flags(case)
        elif mode == "auto":
            selected = validate_context_flags(flags)
        else:
            selected = empty_context_flags()
        for module in resolve_context_modules(selected):
            parts.append(document(f"dist/pack/{module}", (PACK / module).read_text(encoding="utf-8")))
        parts.append(case_facts(case))
    parts.append(task_block())
    return "\n---\n\n".join(parts)


def render_key(case: dict[str, object]) -> str:
    return json.dumps(
        {
            "id": case["id"],
            "family": case["family"],
            "expected_flags": expected_flags(case),
            "expected": case["expected"],
            "forbidden": case["forbidden"],
            "evidence_anchors": {
                "observation_inference": "Separate supplied observations from conclusions.",
                "identity_binding": "Bind claims to the material artifact, environment, control, or authority identity.",
                "material_limitations": "Preserve decisive unknowns, conflicts, and limits."
            },
        },
        indent=2,
    ) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_id")
    parser.add_argument("--stage", choices=("selection", "decision", "key"), required=True)
    parser.add_argument("--mode", choices=MODES)
    parser.add_argument("--continuation", action="store_true")
    args = parser.parse_args()
    try:
        case = load_cases().get(args.case_id)
        if case is None:
            raise DataError(f"unknown case: {args.case_id}")
        if args.stage == "selection":
            if args.mode or args.continuation:
                raise DataError("selection does not accept decision options")
            output = render_selection(case)
        elif args.stage == "key":
            if args.mode or args.continuation:
                raise DataError("key does not accept decision options")
            output = render_key(case)
        else:
            if args.mode is None:
                raise DataError("decision requires --mode")
            flags = stdin_flags() if args.mode == "auto" else None
            output = render_decision(case, args.mode, flags, continuation=args.continuation)
        print(output, end="")
    except (DataError, KeyError, TypeError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
