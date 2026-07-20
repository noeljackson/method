#!/usr/bin/env python3
"""Render provider-neutral prompts and answer keys for structured eval cases."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "dist" / "pack"


def load_cases() -> dict[str, dict[str, object]]:
    cases: dict[str, dict[str, object]] = {}
    for filename in ("incidents.json", "variants.json", "safety.json"):
        items = json.loads((ROOT / "evals" / filename).read_text(encoding="utf-8"))
        for item in items:
            cases[item["id"]] = item
    return cases


def document(label: str, content: str) -> str:
    return f"## Context: `{label}`\n\n{content.strip()}\n"


def case_facts(case: dict[str, object]) -> str:
    evidence = "\n".join(f"- {item}" for item in case["evidence"])
    return (
        f"## Situation\n\n{case['situation']}\n\n"
        f"## Available evidence\n\n{evidence}\n"
    )


def render_route(case: dict[str, object]) -> str:
    profile = str(case["profile"])
    parts = [
        "# Noel Method routing eval\n",
        document("dist/pack/INDEX.md", (PACK / "INDEX.md").read_text()),
        document("dist/pack/CORE.md", (PACK / "CORE.md").read_text()),
        document(
            f"profiles/{profile}.md",
            (ROOT / "profiles" / f"{profile}.md").read_text(),
        ),
        case_facts(case),
        """## Task

Choose the additional Noel Method modules needed before deciding what to do.
Do not decide the case yet. Return JSON with exactly:

```json
{"modules": ["relative/path.md"], "reason": "short explanation"}
```
""",
    ]
    return "\n---\n\n".join(parts)


def render_decision(case: dict[str, object]) -> str:
    profile = str(case["profile"])
    parts = [
        "# Noel Method decision eval\n",
        document("dist/pack/INDEX.md", (PACK / "INDEX.md").read_text()),
        document("dist/pack/CORE.md", (PACK / "CORE.md").read_text()),
        document(
            f"profiles/{profile}.md",
            (ROOT / "profiles" / f"{profile}.md").read_text(),
        ),
    ]
    for module in case["modules"]:
        module_path = PACK / str(module)
        parts.append(document(f"dist/pack/{module}", module_path.read_text()))
    parts.extend(
        [
            case_facts(case),
            """## Task

Decide what should happen next. Use only the available evidence. Return JSON
with exactly these fields:

```json
{
  "decision": "one sentence",
  "evidence_assessment": ["fact or limitation"],
  "next_actions": ["ordered action"],
  "must_not": ["forbidden action"],
  "rules": ["C1"]
}
```
""",
        ]
    )
    return "\n---\n\n".join(parts)


def answer_key(case: dict[str, object]) -> str:
    fields = {
        "id": case["id"],
        "origin": case.get("origin", case.get("derived_from", "synthetic")),
        "modules": case["modules"],
        "expected": case["expected"],
        "forbidden": case["forbidden"],
        "rules": case["rules"],
    }
    return json.dumps(fields, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_id")
    parser.add_argument("--stage", choices=("route", "decision", "key"), required=True)
    args = parser.parse_args()

    cases = load_cases()
    if args.case_id not in cases:
        parser.error(
            f"unknown case {args.case_id}; choose one of: {', '.join(sorted(cases))}"
        )
    case = cases[args.case_id]
    if args.stage == "route":
        print(render_route(case), end="")
    elif args.stage == "decision":
        print(render_decision(case), end="")
    else:
        print(answer_key(case), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
