#!/usr/bin/env python3
"""Validate source documents, generated context, contracts, and compact evals."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote

from methodlib import (
    CONTEXT_KEYS,
    DataError,
    ROOT,
    allowed_context_modules,
    context_spec,
    read_json,
    resolve_context_modules,
    validate_accepted_profile,
)
from render_eval import expected_flags, load_cases, render_decision, render_key, render_selection
from run_eval_batch import call_plan, validate_manifest


LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
RULE_RE = re.compile(r"^## (C\d+) —", re.MULTILINE)
CONTRACT_RE = re.compile(r"^## ([A-Za-z]+)$", re.MULTILINE)
SEMVER_RE = re.compile(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)")
EXPECTED_RULES = {f"C{number}" for number in range(1, 9)}
EXPECTED_CONTRACTS = {
    "WorkContract", "ActionEnvelope", "EvidenceRecord", "ProjectProfile", "ProgramControl"
}
ACTIVE_NO_LEGACY = [
    ROOT / "src", ROOT / "protocols", ROOT / "templates", ROOT / "profiles",
    ROOT / "dist",
]
BOUNDARY_PATHS = [ROOT / "src", ROOT / "protocols"]
FORBIDDEN_BOUNDARY_TERMS = {
    "GitHub", "Codex", "OpenAI", "SOPS", "Kubernetes", "Docker", "noeljackson"
}
WORK_FIELDS = {
    "outcome", "disposition", "scope", "authority", "evidence", "gates",
    "next_evidence", "reporting",
}
ACTION_FIELDS = {
    "disposition", "observations", "inferences_and_unknowns", "allowed_actions",
    "forbidden_actions", "gates", "recovery", "next_evidence",
}


def markdown_files() -> list[Path]:
    output: list[Path] = []
    for path in ROOT.rglob("*.md"):
        relative = path.relative_to(ROOT)
        if ".git" in relative.parts or relative.parts[:2] == ("evals", "runs"):
            continue
        output.append(path)
    return sorted(output)


def check_markdown(errors: list[str]) -> None:
    marker = re.compile(r"^(<<<<<<<|=======|>>>>>>>)")
    for path in markdown_files():
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT)
        for line_number, line in enumerate(text.splitlines(), start=1):
            if line.endswith(" "):
                errors.append(f"{relative}:{line_number}: trailing whitespace")
            if "\t" in line:
                errors.append(f"{relative}:{line_number}: tab character")
            if marker.match(line):
                errors.append(f"{relative}:{line_number}: conflict marker")
        for match in LINK_RE.finditer(text):
            target = match.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = target.split(maxsplit=1)[0].strip("<>")
            target = unquote(target.split("#", maxsplit=1)[0])
            if target and not (path.parent / target).resolve().exists():
                errors.append(f"{relative}: broken local link: {target}")


def check_boundaries(errors: list[str]) -> None:
    for root in BOUNDARY_PATHS:
        for path in sorted(root.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            for term in FORBIDDEN_BOUNDARY_TERMS:
                if re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE):
                    errors.append(f"{path.relative_to(ROOT)}: project/tool term in normative text: {term}")


def section_fields(text: str, heading: str) -> set[str]:
    match = re.search(
        rf"^## {re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if not match:
        return set()
    return set(re.findall(r"^- `([^`]+)`", match.group("body"), re.MULTILINE))


def check_public_interface(errors: list[str]) -> None:
    core = (ROOT / "src" / "10-core.md").read_text(encoding="utf-8")
    rules = RULE_RE.findall(core)
    if set(rules) != EXPECTED_RULES or len(rules) != 8:
        errors.append(f"hard-core rule IDs mismatch: {rules}")
    contracts = (ROOT / "src" / "40-contracts.md").read_text(encoding="utf-8")
    headings = set(CONTRACT_RE.findall(contracts))
    if headings != EXPECTED_CONTRACTS:
        errors.append(f"public contract headings mismatch: {sorted(headings)}")
    if section_fields(contracts, "WorkContract") != WORK_FIELDS:
        errors.append("WorkContract required fields do not match the compact public contract")
    if section_fields(contracts, "ActionEnvelope") != ACTION_FIELDS:
        errors.append("ActionEnvelope fields do not match the stable action envelope")
    for conditional in ("recovery", "secrets", "program", "experiment"):
        if f"`{conditional}`" not in re.search(
            r"^## WorkContract\n(.*?)(?=^## )", contracts, re.MULTILINE | re.DOTALL
        ).group(1):
            errors.append(f"WorkContract missing conditional section {conditional}")
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER_RE.fullmatch(version):
        errors.append(f"VERSION is not strict SemVer: {version}")


def check_legacy_removal(errors: list[str]) -> None:
    for root in ACTIVE_NO_LEGACY:
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in {".md", ".json"}:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for legacy in ("TaskDescriptor", "CoreDeviationReceipt"):
                if legacy in text:
                    errors.append(f"{path.relative_to(ROOT)}: retired public concept remains: {legacy}")


def check_context(errors: list[str]) -> None:
    try:
        spec = context_spec()
        if tuple(spec["flags"]) != CONTEXT_KEYS:
            errors.append("context flags have unexpected order")
        all_true = {key: True for key in CONTEXT_KEYS}
        if resolve_context_modules(all_true, spec) != spec["module_order"]:
            errors.append("context flag resolution does not preserve module order")
        allowed_context_modules(spec)
    except DataError as error:
        errors.append(str(error))


def check_profiles(errors: list[str]) -> set[str]:
    authorities = read_json(ROOT / "evals" / "fixtures" / "authorities.json")
    profiles: set[str] = set()
    root = ROOT / "evals" / "fixtures" / "profiles"
    for path in sorted(root.glob("*.md")):
        try:
            validate_accepted_profile(path.read_text(encoding="utf-8"), path.stem, authorities)
        except DataError as error:
            errors.append(f"{path.relative_to(ROOT)}: {error}")
        profiles.add(path.stem)
        brief = ROOT / "evals" / "fixtures" / "neutral-briefs" / path.name
        if not brief.is_file():
            errors.append(f"{path.stem}: missing neutral authority brief")
    return profiles


def _atomic_items(value: object, label: str, errors: list[str], *, forbidden: bool = False) -> None:
    fields = {"id", "predicate", "when"} if forbidden else {"id", "predicate"}
    if not isinstance(value, list) or not value:
        errors.append(f"{label}: must be a non-empty array")
        return
    identifiers: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict) or set(item) != fields:
            errors.append(f"{label}[{index}]: fields must be {sorted(fields)}")
            continue
        if not all(isinstance(item[field], str) and item[field] for field in fields):
            errors.append(f"{label}[{index}]: fields must be non-empty text")
            continue
        identifiers.append(item["id"])
    if len(identifiers) != len(set(identifiers)):
        errors.append(f"{label}: IDs must be unique")


def check_evals(errors: list[str]) -> None:
    profiles = check_profiles(errors)
    try:
        cases = load_cases()
    except DataError as error:
        errors.append(str(error))
        return
    if len(cases) != 10:
        errors.append(f"active compact eval must contain exactly 10 cases, found {len(cases)}")
    counts = Counter(case.get("family") for case in cases.values())
    if counts != Counter({"core": 4, "program": 2, "experiment": 2, "secrets": 2}):
        errors.append(f"active case family counts are invalid: {dict(counts)}")
    case_fields = {"id", "family", "profile", "situation", "evidence", "expected", "forbidden"}
    for identifier, case in cases.items():
        label = f"eval case {identifier}"
        if set(case) != case_fields:
            errors.append(f"{label}: fields must be {sorted(case_fields)}")
        if case.get("profile") not in profiles:
            errors.append(f"{label}: unknown accepted profile")
        if not isinstance(case.get("situation"), str) or not case.get("situation"):
            errors.append(f"{label}: situation must be non-empty text")
        evidence = case.get("evidence")
        if (
            not isinstance(evidence, list) or not evidence
            or not all(isinstance(item, str) and item for item in evidence)
            or len(evidence) != len(set(evidence))
        ):
            errors.append(f"{label}: evidence must be a unique non-empty string array")
        expected = case.get("expected")
        if not isinstance(expected, dict) or set(expected) != {"decision", "required"}:
            errors.append(f"{label}: expected fields are invalid")
        else:
            if not isinstance(expected["decision"], str) or not expected["decision"]:
                errors.append(f"{label}: expected decision must be text")
            _atomic_items(expected["required"], f"{label}.required", errors)
        _atomic_items(case.get("forbidden"), f"{label}.forbidden", errors, forbidden=True)
        try:
            selection = render_selection(case)
            key = render_key(case)
            neutral = render_decision(case, "neutral")
            base = render_decision(case, "base")
            for prompt in (selection, neutral, base):
                if not prompt.strip():
                    errors.append(f"{label}: rendered an empty prompt")
            if case["family"] != "core":
                explicit = render_decision(case, "explicit")
                continuation = render_decision(
                    case, "auto", expected_flags(case), continuation=True
                )
                if "dist/pack/BASE.md" in continuation or "## Situation" in continuation:
                    errors.append(f"{label}: auto continuation repeats base context or facts")
                if not explicit.strip() or not key.strip():
                    errors.append(f"{label}: protocol render failed")
        except (DataError, KeyError, TypeError, OSError) as error:
            errors.append(f"{label}: render failed: {error}")
    try:
        manifest = validate_manifest(read_json(ROOT / "evals" / "manifest.json"))
        plan = call_plan(manifest)
        if (plan["calls"], plan["decisions"], plan["selections"]) != (76, 64, 12):
            errors.append(f"compact eval plan counts are invalid: {plan['calls']}/{plan['decisions']}/{plan['selections']}")
        if plan["calls"] > plan["hard_cap"]:
            errors.append("compact eval exceeds its hard call cap")
    except DataError as error:
        errors.append(str(error))


def check_manifest(errors: list[str]) -> None:
    manifest = read_json(ROOT / "dist" / "pack" / "MANIFEST.json")
    if not isinstance(manifest, dict) or not isinstance(manifest.get("files"), list):
        errors.append("generated manifest is malformed")
        return
    paths: list[str] = []
    for item in manifest["files"]:
        if not isinstance(item, dict) or set(item) != {"path", "sha256"}:
            errors.append("generated manifest has an invalid file entry")
            continue
        path = ROOT / "dist" / "pack" / item["path"]
        paths.append(item["path"])
        if not path.is_file():
            errors.append(f"manifest file missing: {item['path']}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            errors.append(f"manifest digest mismatch: {item['path']}")
    if len(paths) != len(set(paths)):
        errors.append("generated manifest paths must be unique")


def words(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").split())


def check_word_budgets(errors: list[str]) -> None:
    pack = ROOT / "dist" / "pack"
    profile_root = ROOT / "evals" / "fixtures" / "profiles"
    base = words(pack / "BASE.md")
    largest_profile = max(words(path) for path in profile_root.glob("*.md"))
    budgets = {
        "Base plus profile": (base + largest_profile, 2300),
        "Program": (words(pack / "protocols" / "program.md"), 800),
        "Experiment": (words(pack / "protocols" / "experiment.md"), 400),
        "Secrets": (words(pack / "protocols" / "secrets.md"), 800),
        "Monolith": (words(ROOT / "dist" / "NOEL-METHOD.md"), 4500),
    }
    for label, (actual, limit) in budgets.items():
        if actual > limit:
            errors.append(f"{label} word budget exceeded: {actual} > {limit}")


def check_migration(errors: list[str]) -> None:
    inventory = read_json(ROOT / "migration" / "source-inventory.json")
    if not isinstance(inventory, dict) or not all(isinstance(items, list) for items in inventory.values()):
        errors.append("migration/source-inventory.json: expected object of arrays")
        return
    expected = {
        item.get("id") for items in inventory.values() for item in items if isinstance(item, dict)
    }
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    mapped = re.findall(r"^\| ([ICA]-\d{3}) \|", migration, re.MULTILINE)
    counts = Counter(mapped)
    if expected - set(mapped):
        errors.append(f"migration IDs missing: {', '.join(sorted(expected - set(mapped)))}")
    if set(mapped) - expected:
        errors.append(f"migration IDs unexpected: {', '.join(sorted(set(mapped) - expected))}")
    duplicates = [identifier for identifier, count in counts.items() if count != 1]
    if duplicates:
        errors.append(f"migration IDs duplicated: {', '.join(sorted(duplicates))}")


def check_provenance(errors: list[str]) -> None:
    registry = read_json(ROOT / "casebook" / "rule-provenance.json")
    if not isinstance(registry, list):
        errors.append("rule provenance must be an array")
        return
    seen: list[str] = []
    for index, item in enumerate(registry):
        fields = {"rule", "observation", "insufficiency", "migration_id", "introduced_in", "eval_ids"}
        if not isinstance(item, dict) or set(item) != fields:
            errors.append(f"rule provenance {index}: invalid fields")
            continue
        seen.append(item["rule"])
        if item["observation"] != item["migration_id"]:
            errors.append(f"rule provenance {item['rule']}: observation and migration ID differ")
        if not isinstance(item["insufficiency"], str) or not item["insufficiency"]:
            errors.append(f"rule provenance {item['rule']}: missing insufficiency")
        if not isinstance(item["eval_ids"], list) or not item["eval_ids"]:
            errors.append(f"rule provenance {item['rule']}: missing eval IDs")
    if set(seen) != EXPECTED_RULES or len(seen) != 8:
        errors.append("every hard-core rule must have one provenance record")


def main() -> int:
    errors: list[str] = []
    for check in (
        check_markdown,
        check_boundaries,
        check_public_interface,
        check_legacy_removal,
        check_context,
        check_evals,
        check_manifest,
        check_word_budgets,
        check_migration,
        check_provenance,
    ):
        try:
            check(errors)
        except (DataError, OSError, KeyError, TypeError, ValueError) as error:
            errors.append(f"{check.__name__}: {error}")
    generated = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_dist.py"), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if generated.returncode:
        errors.append("generated distribution is stale:\n" + generated.stdout.strip())
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("documentation, context, contracts, provenance, and compact evals are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
