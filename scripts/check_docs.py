#!/usr/bin/env python3
"""Dependency-free structural checks for the Noel Method repository."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
NORMATIVE_DIRS = (ROOT / "src", ROOT / "protocols")
BOUNDARY_PATHS = (*NORMATIVE_DIRS, ROOT / "dist")
FORBIDDEN_TERMS = (
    "isol8",
    "codewire",
    "xen",
    "kubernetes",
    "codex",
    "claude",
    "gitea",
    "hetzner",
    "infisical",
)
EXPECTED_RULES = {f"C{number}" for number in range(1, 8)}
EXPECTED_CONTRACTS = {
    "WorkContract",
    "EvidenceRecord",
    "ProjectProfile",
    "ProgramControl",
}
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")


def markdown_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.md")
        if ".git" not in path.parts and "lychee" not in path.parts
    )


def check_markdown(errors: list[str]) -> None:
    marker_re = re.compile(r"^(<<<<<<<|=======|>>>>>>>)")
    for path in markdown_files():
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT)
        if text and not text.endswith("\n"):
            errors.append(f"{relative}: missing final newline")
        if text.endswith("\n\n"):
            errors.append(f"{relative}: extra blank line at end of file")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if line.rstrip() != line:
                errors.append(f"{relative}:{line_number}: trailing whitespace")
            if "\t" in line:
                errors.append(f"{relative}:{line_number}: tab character")
            if marker_re.match(line):
                errors.append(f"{relative}:{line_number}: conflict marker")

        for match in LINK_RE.finditer(text):
            target = match.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = target.split(maxsplit=1)[0].strip("<>")
            target = unquote(target.split("#", maxsplit=1)[0])
            if not target or "<" in target or ">" in target:
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                errors.append(f"{relative}: broken local link: {target}")


def check_boundaries(errors: list[str]) -> None:
    paths: list[Path] = []
    for boundary in BOUNDARY_PATHS:
        if boundary.is_dir():
            paths.extend(sorted(boundary.rglob("*.md")))
        elif boundary.exists():
            paths.append(boundary)

    for path in paths:
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT)
        for term in FORBIDDEN_TERMS:
            if re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE):
                errors.append(f"{relative}: project/tool term leaked into core: {term}")
        if IP_RE.search(text):
            errors.append(f"{relative}: infrastructure address leaked into core")


def check_public_interface(errors: list[str]) -> None:
    core = (ROOT / "src" / "10-core.md").read_text(encoding="utf-8")
    rules = re.findall(r"^## (C\d+) —", core, re.MULTILINE)
    if set(rules) != EXPECTED_RULES or len(rules) != len(EXPECTED_RULES):
        errors.append(f"hard-core rule IDs mismatch: {rules}")

    contracts = (ROOT / "src" / "40-contracts.md").read_text(encoding="utf-8")
    names = set(re.findall(r"^## ([A-Za-z]+)$", contracts, re.MULTILINE))
    if names != EXPECTED_CONTRACTS:
        errors.append(f"public contract headings mismatch: {sorted(names)}")


def check_migration(errors: list[str]) -> None:
    inventory = json.loads(
        (ROOT / "migration" / "source-inventory.json").read_text(encoding="utf-8")
    )
    expected = {
        item["id"]
        for source_items in inventory.values()
        for item in source_items
    }
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    mapped = re.findall(r"^\| ([ICA]-\d{3}) \|", migration, re.MULTILINE)
    counts = Counter(mapped)
    duplicates = sorted(identifier for identifier, count in counts.items() if count != 1)
    missing = sorted(expected - set(mapped))
    unexpected = sorted(set(mapped) - expected)
    if missing:
        errors.append(f"migration IDs missing: {', '.join(missing)}")
    if unexpected:
        errors.append(f"migration IDs unexpected: {', '.join(unexpected)}")
    if duplicates:
        errors.append(f"migration IDs duplicated: {', '.join(duplicates)}")


def check_scenarios(errors: list[str]) -> None:
    scenarios = json.loads(
        (ROOT / "evals" / "scenarios.json").read_text(encoding="utf-8")
    )
    required = {"id", "situation", "expected", "forbidden"}
    identifiers: list[str] = []
    for index, scenario in enumerate(scenarios):
        if set(scenario) != required:
            errors.append(f"scenario {index} fields must be {sorted(required)}")
        identifiers.append(scenario.get("id", f"missing-{index}"))
    if len(scenarios) < 8:
        errors.append("at least eight decision scenarios are required")
    if len(identifiers) != len(set(identifiers)):
        errors.append("scenario IDs must be unique")

    incidents = json.loads(
        (ROOT / "evals" / "incidents.json").read_text(encoding="utf-8")
    )
    incident_fields = {
        "id",
        "origin",
        "category",
        "profile",
        "modules",
        "situation",
        "evidence",
        "expected",
        "forbidden",
        "rules",
    }
    incident_ids: set[str] = set()
    for index, incident in enumerate(incidents):
        if set(incident) != incident_fields:
            errors.append(
                f"incident {index} fields must be {sorted(incident_fields)}"
            )
        identifier = incident.get("id", f"missing-incident-{index}")
        incident_ids.add(identifier)
        check_structured_case(incident, f"incident {identifier}", errors)
    if len(incidents) < 6:
        errors.append("at least six incident-derived evals are required")
    if len(incident_ids) != len(incidents):
        errors.append("incident eval IDs must be unique")

    variants = json.loads(
        (ROOT / "evals" / "variants.json").read_text(encoding="utf-8")
    )
    variant_fields = {
        "id",
        "derived_from",
        "category",
        "profile",
        "modules",
        "situation",
        "evidence",
        "expected",
        "forbidden",
        "rules",
    }
    variant_ids: set[str] = set()
    for index, variant in enumerate(variants):
        if set(variant) != variant_fields:
            errors.append(f"variant {index} fields must be {sorted(variant_fields)}")
        identifier = variant.get("id", f"missing-variant-{index}")
        variant_ids.add(identifier)
        check_structured_case(variant, f"variant {identifier}", errors)
        if variant.get("derived_from") not in incident_ids:
            errors.append(
                f"variant {identifier}: unknown incident origin "
                f"{variant.get('derived_from')}"
            )
    if len(variants) < 4:
        errors.append("at least four synthetic variants are required")
    if len(variant_ids) != len(variants):
        errors.append("variant eval IDs must be unique")

    for identifier in sorted(incident_ids | variant_ids):
        for stage in ("route", "decision", "key"):
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "render_eval.py"),
                    identifier,
                    "--stage",
                    stage,
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            if result.returncode or not result.stdout.strip():
                errors.append(f"{identifier}: failed to render {stage} eval stage")


def check_structured_case(
    case: dict[str, object],
    label: str,
    errors: list[str],
) -> None:
    modules = case.get("modules", [])
    if not isinstance(modules, list) or not modules:
        errors.append(f"{label}: modules must be a non-empty list")
    else:
        for module in modules:
            if not isinstance(module, str) or not (ROOT / "dist" / "pack" / module).exists():
                errors.append(f"{label}: unknown modular-pack path {module}")

    profile = case.get("profile")
    if not isinstance(profile, str) or not (ROOT / "profiles" / f"{profile}.md").exists():
        errors.append(f"{label}: unknown example profile {profile}")

    expected = case.get("expected")
    if not isinstance(expected, dict) or set(expected) != {"decision", "required"}:
        errors.append(f"{label}: expected must contain decision and required")
    elif not isinstance(expected["required"], list) or not expected["required"]:
        errors.append(f"{label}: expected.required must be a non-empty list")

    rules = case.get("rules", [])
    if not isinstance(rules, list) or not set(rules).issubset(EXPECTED_RULES):
        errors.append(f"{label}: rules must reference only C1-C7")

    for field in ("evidence", "forbidden"):
        value = case.get(field, [])
        if not isinstance(value, list) or not value:
            errors.append(f"{label}: {field} must be a non-empty list")


def check_distribution(errors: list[str]) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_dist.py"), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        errors.append("generated distribution is stale:\n" + result.stdout)


def main() -> int:
    errors: list[str] = []
    check_markdown(errors)
    check_boundaries(errors)
    check_public_interface(errors)
    check_migration(errors)
    check_scenarios(errors)
    check_distribution(errors)

    if errors:
        print("documentation checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("documentation checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
