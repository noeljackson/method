#!/usr/bin/env python3
"""Validate v0.3 source, contracts, distribution, routing, and sparse evals."""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import unquote

from methodlib import (
    DataError,
    PROTOCOL_KEYS,
    ROOT,
    context_spec,
    read_json,
    resolve_runtime_envelope,
    validate_project_profile,
    validate_task_request,
)
from render_eval import load_cases, render_decision
from run_eval_batch import call_plan, validate_manifest


LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
SEMVER_RE = re.compile(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)")
BOUNDARY_PATHS = (ROOT / "src", ROOT / "protocols")
FORBIDDEN_BOUNDARY_TERMS = {
    "GitHub",
    "Gitea",
    "Codex",
    "OpenAI",
    "SOPS",
    "Kubernetes",
    "Docker",
    "Codewire",
    "isol8",
    "noeljackson",
}
ACTIVE_DOCS = [
    ROOT / "AGENTS.md",
    ROOT / "README.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "adapters",
    ROOT / "evals/README.md",
    ROOT / "evals/RUBRIC.md",
]
RETIRED_ACTIVE_TERMS = {
    "BASE.md",
    "ContextFlags",
    "dist/NOEL-METHOD.md",
    "templates/work-contract.md",
    "PROJECT-PROFILE.md",
}
KERNEL_SECTIONS = {
    "Runtime input",
    "Observe",
    "Bound",
    "Act",
    "Verify",
    "Report",
    "Permanent secret boundary",
}


def markdown_files() -> list[Path]:
    output: list[Path] = []
    for path in ROOT.rglob("*.md"):
        relative = path.relative_to(ROOT)
        if ".git" in relative.parts:
            continue
        if relative.parts[:2] in {("evals", "runs"), ("evals", "reports")}:
            continue
        output.append(path)
    return sorted(output)


def check_markdown(errors: list[str]) -> None:
    conflict = re.compile(r"^(<<<<<<<|=======|>>>>>>>)")
    for path in markdown_files():
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT)
        for line_number, line in enumerate(text.splitlines(), start=1):
            if line.endswith(" "):
                errors.append(f"{relative}:{line_number}: trailing whitespace")
            if "\t" in line:
                errors.append(f"{relative}:{line_number}: tab character")
            if conflict.match(line):
                errors.append(f"{relative}:{line_number}: conflict marker")
        for match in LINK_RE.finditer(text):
            target = match.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = target.split(maxsplit=1)[0].strip("<>")
            target = unquote(target.split("#", maxsplit=1)[0])
            if target and not (path.parent / target).resolve().exists():
                errors.append(f"{relative}: broken local link: {target}")


def check_normative_boundaries(errors: list[str]) -> None:
    for root in BOUNDARY_PATHS:
        for path in sorted(root.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            for term in FORBIDDEN_BOUNDARY_TERMS:
                if re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE):
                    errors.append(
                        f"{path.relative_to(ROOT)}: local term in normative text: {term}"
                    )
    expected_source = {
        ROOT / "src/KERNEL.md",
        ROOT / "src/contracts.md",
        ROOT / "src/context.json",
    }
    actual_source = {path for path in (ROOT / "src").iterdir() if path.is_file()}
    if actual_source != expected_source:
        errors.append(
            "src inventory differs: "
            + ", ".join(str(path.relative_to(ROOT)) for path in sorted(actual_source))
        )
    expected_protocols = {
        ROOT / "protocols" / f"{name}.md" for name in PROTOCOL_KEYS
    }
    actual_protocols = set((ROOT / "protocols").glob("*.md"))
    if actual_protocols != expected_protocols:
        errors.append("protocol inventory must be exactly program, experiment, secrets")


def _active_paths() -> list[Path]:
    output: list[Path] = []
    for item in ACTIVE_DOCS:
        if item.is_dir():
            output.extend(sorted(item.rglob("*.md")))
        else:
            output.append(item)
    return output


def check_no_retired_interface(errors: list[str]) -> None:
    for path in _active_paths():
        text = path.read_text(encoding="utf-8")
        for term in RETIRED_ACTIVE_TERMS:
            if term in text:
                errors.append(f"{path.relative_to(ROOT)}: retired active term: {term}")


def check_contracts(errors: list[str]) -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER_RE.fullmatch(version):
        errors.append(f"VERSION is not semantic: {version}")
    kernel = (ROOT / "src/KERNEL.md").read_text(encoding="utf-8")
    headings = set(re.findall(r"^## (?:[1-5]\. )?(.+)$", kernel, re.MULTILINE))
    if headings != KERNEL_SECTIONS:
        errors.append(f"kernel sections differ: {sorted(headings)}")
    contracts = (ROOT / "src/contracts.md").read_text(encoding="utf-8")
    expected_contracts = {
        "ProjectProfile",
        "TaskRequest",
        "RuntimeEnvelope",
        "ControlledAction",
        "EvidenceReceipt",
        "ProgramControl",
    }
    found = set(re.findall(r"^## ([A-Za-z]+)$", contracts, re.MULTILINE))
    if found != expected_contracts:
        errors.append(f"contract headings differ: {sorted(found)}")
    public = read_json(ROOT / "migration/public-api-0.3.0.json")
    if public.get("version") != version:
        errors.append("0.3 public-interface record does not match VERSION")
    if set(public.get("kernel_sections", [])) != KERNEL_SECTIONS:
        errors.append("public-interface kernel sections differ")
    if set(public.get("contracts", [])) != expected_contracts:
        errors.append("public-interface contracts differ")
    if public.get("protocols") != list(PROTOCOL_KEYS):
        errors.append("public-interface protocols differ")


def check_json_and_profiles(errors: list[str]) -> None:
    json_roots = (
        ROOT / "schemas",
        ROOT / "templates",
        ROOT / "profiles",
        ROOT / "migration",
        ROOT / "casebook",
        ROOT / "evals/fixtures",
    )
    for root in json_roots:
        for path in sorted(root.rglob("*.json")):
            try:
                read_json(path)
            except DataError as error:
                errors.append(str(error))
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    for path in sorted((ROOT / "profiles").glob("*.json")):
        try:
            checked = validate_project_profile(
                read_json(path), {}, require_accepted=False
            )
            if checked["method_version"] != version:
                errors.append(f"{path.relative_to(ROOT)}: method version differs")
        except DataError as error:
            errors.append(f"{path.relative_to(ROOT)}: {error}")
    authorities = read_json(ROOT / "evals/fixtures/authorities.json")
    for path in sorted((ROOT / "evals/fixtures/profiles").glob("*.json")):
        try:
            checked = validate_project_profile(read_json(path), authorities)
            if checked["method_version"] != version:
                errors.append(f"{path.relative_to(ROOT)}: method version differs")
        except DataError as error:
            errors.append(f"{path.relative_to(ROOT)}: {error}")
    template_authorities = read_json(ROOT / "templates/profile-authorities.json")
    if not isinstance(template_authorities, dict) or len(template_authorities) != 1:
        errors.append("profile-authorities template must contain one example receipt")


def check_routing_and_evals(errors: list[str]) -> None:
    cases = load_cases()
    authorities = read_json(ROOT / "evals/fixtures/authorities.json")
    for case_id, case in cases.items():
        try:
            profile = read_json(
                ROOT / f"evals/fixtures/profiles/{case['profile']}.json"
            )
            task = read_json(ROOT / f"evals/fixtures/tasks/{case['task']}.json")
            validate_task_request(task)
            envelope = resolve_runtime_envelope(profile, authorities, task)
            if envelope["protocols"] != case["expected_protocols"]:
                errors.append(
                    f"{case_id}: routed {envelope['protocols']} "
                    f"instead of {case['expected_protocols']}"
                )
            for mode in ("neutral", "kernel", "routed", "wrong", "monolith"):
                prompt = render_decision(case, mode)
                if case["expected"]["decision"] in prompt:
                    errors.append(f"{case_id}:{mode}: expected decision leaked")
                for item in [*case["expected"]["required"], *case["forbidden"]]:
                    if item["id"] in prompt:
                        errors.append(f"{case_id}:{mode}: evaluator ID leaked")
        except (DataError, OSError, KeyError, TypeError) as error:
            errors.append(f"{case_id}: {error}")
    manifest = validate_manifest(read_json(ROOT / "evals/manifest.json"))
    plan = call_plan(manifest)
    if plan["calls"] != 8:
        errors.append(f"sparse release plan is {plan['calls']} calls, expected 8")


def check_word_budgets(errors: list[str]) -> None:
    limits = {
        ROOT / "src/KERNEL.md": 700,
        ROOT / "protocols/program.md": 600,
        ROOT / "protocols/experiment.md": 300,
        ROOT / "protocols/secrets.md": 650,
        ROOT / "dist/MONOLITH.md": 1900,
        ROOT / "dist/pack/INDEX.md": 350,
    }
    for path, limit in limits.items():
        count = len(path.read_text(encoding="utf-8").split())
        if count > limit:
            errors.append(f"{path.relative_to(ROOT)}: {count} words exceeds {limit}")
    cases = load_cases()
    direct = len(render_decision(cases["direct-bounded-edit"], "routed").split())
    interaction = len(
        render_decision(cases["interaction-program-secret"], "routed").split()
    )
    monolith = len(
        render_decision(cases["interaction-program-secret"], "monolith").split()
    )
    if direct > 1300:
        errors.append(f"direct representative prompt is too large: {direct}")
    if interaction > 2100:
        errors.append(f"multi-protocol representative prompt is too large: {interaction}")
    if interaction >= monolith:
        errors.append("multi-protocol route is not smaller than monolith")


def check_provenance(errors: list[str]) -> None:
    inventory = read_json(ROOT / "migration/source-inventory.json")
    source_ids = {
        item["id"]
        for collection in inventory.values()
        for item in collection
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    case_ids = set(load_cases())
    entries = read_json(ROOT / "casebook/kernel-provenance.json")
    if not isinstance(entries, list):
        errors.append("kernel provenance must be an array")
        return
    sections = {entry.get("section") for entry in entries if isinstance(entry, dict)}
    if sections != KERNEL_SECTIONS:
        errors.append(f"kernel provenance sections differ: {sorted(sections)}")
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {
            "section",
            "source_ids",
            "failure_prevented",
            "eval_ids",
        }:
            errors.append("kernel provenance entry has wrong fields")
            continue
        if not entry["source_ids"] or not set(entry["source_ids"]) <= source_ids:
            errors.append(f"{entry['section']}: unknown or empty source provenance")
        if not entry["eval_ids"] or not set(entry["eval_ids"]) <= case_ids:
            errors.append(f"{entry['section']}: unknown or empty eval provenance")
        if not isinstance(entry["failure_prevented"], str) or not entry["failure_prevented"]:
            errors.append(f"{entry['section']}: missing failure rationale")


def check_pack_manifest(errors: list[str]) -> None:
    manifest_path = ROOT / "dist/pack/MANIFEST.json"
    manifest = read_json(manifest_path)
    files = manifest.get("files") if isinstance(manifest, dict) else None
    if not isinstance(files, list):
        errors.append("pack manifest files must be an array")
        return
    declared: set[str] = set()
    for item in files:
        if (
            not isinstance(item, dict)
            or set(item) != {"path", "sha256"}
            or not isinstance(item["path"], str)
            or not isinstance(item["sha256"], str)
        ):
            errors.append("pack manifest entry is malformed")
            continue
        pure = PurePosixPath(item["path"])
        if pure.is_absolute() or ".." in pure.parts or str(pure) != item["path"]:
            errors.append(f"unsafe pack manifest path: {item['path']}")
            continue
        if item["path"] in declared:
            errors.append(f"duplicate pack manifest path: {item['path']}")
            continue
        declared.add(item["path"])
        path = ROOT / "dist/pack" / item["path"]
        if not path.is_file():
            errors.append(f"manifest file missing: {item['path']}")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != item["sha256"]:
            errors.append(f"manifest hash mismatch: {item['path']}")
    actual = {
        str(path.relative_to(ROOT / "dist/pack"))
        for path in (ROOT / "dist/pack").rglob("*")
        if path.is_file() and path.name != "MANIFEST.json"
    }
    if declared != actual:
        errors.append(
            f"pack manifest coverage differs: missing={sorted(actual-declared)}, "
            f"extra={sorted(declared-actual)}"
        )


def check_generated(errors: list[str]) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/build_dist.py"), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        errors.append("generated distribution drift:\n" + result.stdout + result.stderr)


def main() -> int:
    errors: list[str] = []
    checks = (
        check_markdown,
        check_normative_boundaries,
        check_no_retired_interface,
        check_contracts,
        check_json_and_profiles,
        check_routing_and_evals,
        check_word_budgets,
        check_provenance,
        check_pack_manifest,
        check_generated,
    )
    try:
        context_spec()
        for check in checks:
            check(errors)
    except (DataError, OSError, KeyError, TypeError, ValueError) as error:
        errors.append(str(error))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("documentation and distribution checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
