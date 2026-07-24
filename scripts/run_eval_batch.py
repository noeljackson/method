#!/usr/bin/env python3
"""Plan, render, or explicitly execute the sparse Noel Method evaluation."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from methodlib import DataError, ROOT, read_json
from render_eval import DECISION_FIELDS, load_cases, render_decision


RELEASE_ARMS = ("neutral", "routed")
MAX_CALLS = 8
BATCH_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def validate_manifest(value: object) -> dict[str, Any]:
    fields = {
        "schema_version",
        "id",
        "frozen",
        "created_at",
        "cases",
        "arms",
        "samples_per_cell",
        "model",
        "reasoning_effort",
        "call_budget",
        "randomization_seed",
        "limitations",
    }
    if not isinstance(value, dict) or set(value) != fields:
        raise DataError(f"eval manifest fields must be {sorted(fields)}")
    if value["schema_version"] != 2 or value["frozen"] is not True:
        raise DataError("eval manifest must be frozen schema version 2")
    for field in (
        "id",
        "created_at",
        "model",
        "reasoning_effort",
        "randomization_seed",
    ):
        if not isinstance(value[field], str) or not value[field]:
            raise DataError(f"{field} must be non-empty text")
    if not BATCH_ID_RE.fullmatch(value["id"]):
        raise DataError("id must be a safe lowercase identifier")
    known = load_cases()
    cases = value["cases"]
    if (
        not isinstance(cases, list)
        or not cases
        or len(cases) != len(set(cases))
        or any(case_id not in known for case_id in cases)
    ):
        raise DataError("manifest cases must be unique known case IDs")
    if value["arms"] != list(RELEASE_ARMS):
        raise DataError(f"release arms must be exactly {list(RELEASE_ARMS)}")
    if value["samples_per_cell"] != 1:
        raise DataError("the sparse release gate requires one sample per cell")
    calls = len(cases) * len(RELEASE_ARMS)
    if value["call_budget"] != calls or calls > MAX_CALLS:
        raise DataError(f"call_budget must equal sparse plan size {calls} and be <= {MAX_CALLS}")
    if not isinstance(value["limitations"], list) or not all(
        isinstance(item, str) and item for item in value["limitations"]
    ):
        raise DataError("limitations must be a string array")
    return value


def call_plan(manifest: dict[str, Any]) -> dict[str, object]:
    calls = [
        {
            "case_id": case_id,
            "arm": arm,
            "sample": 1,
        }
        for case_id in manifest["cases"]
        for arm in manifest["arms"]
    ]
    random.Random(manifest["randomization_seed"]).shuffle(calls)
    return {"calls": len(calls), "decisions": len(calls), "items": calls}


def _validate_decision(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != DECISION_FIELDS:
        raise DataError(f"decision output fields must be {sorted(DECISION_FIELDS)}")
    if value["disposition"] not in {"PROCEED", "HOLD", "CONTAIN", "TERMINATE"}:
        raise DataError("invalid disposition")
    if not isinstance(value["decision"], str) or not value["decision"]:
        raise DataError("decision must be non-empty text")
    for field in DECISION_FIELDS - {"disposition", "decision"}:
        if not isinstance(value[field], list) or not all(
            isinstance(item, str) for item in value[field]
        ):
            raise DataError(f"{field} must be a string array")
    return value


def render_plan(manifest: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=False)
    cases = load_cases()
    for call in call_plan(manifest)["items"]:
        prompt = render_decision(cases[call["case_id"]], call["arm"])
        path = output_dir / f"{call['case_id']}-{call['arm']}.md"
        path.write_text(prompt, encoding="utf-8")


def _input_inventory(manifest_path: Path, manifest: dict[str, Any]) -> list[dict[str, str]]:
    cases = load_cases()
    paths = {
        manifest_path,
        ROOT / "evals" / "cases.json",
        ROOT / "evals" / "RUBRIC.md",
        ROOT / "evals" / "fixtures" / "authorities.json",
        ROOT / "evals" / "schemas" / "decision-output.json",
        ROOT / "scripts" / "methodlib.py",
        ROOT / "scripts" / "render_eval.py",
        ROOT / "scripts" / "run_eval_batch.py",
        ROOT / "scripts" / "score_eval.py",
        ROOT / "scripts" / "publish_eval.py",
        ROOT / "dist" / "MONOLITH.md",
    }
    paths.update(path for path in (ROOT / "dist" / "pack").rglob("*") if path.is_file())
    for case_id in manifest["cases"]:
        case = cases[case_id]
        paths.add(
            ROOT / "evals" / "fixtures" / "policies"
            / f"{case['policy']}.json"
        )
        paths.add(ROOT / "evals" / "fixtures" / "tasks" / f"{case['task']}.json")
        paths.add(
            ROOT / "evals" / "fixtures" / "neutral-briefs"
            / f"{case['policy']}.md"
        )
    return [
        {
            "path": str(path.relative_to(ROOT)),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        for path in sorted(paths)
    ]


def _git_state() -> dict[str, object]:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    ).stdout
    return {"head": head, "clean": not bool(status.strip())}


def _invoke(
    executable: str,
    manifest: dict[str, Any],
    prompt: str,
    output: Path,
    log: Path,
) -> tuple[dict[str, object], float]:
    with tempfile.TemporaryDirectory(prefix="noel-method-eval-") as workdir:
        command = [
            executable,
            "exec",
            "--ignore-user-config",
            "--ignore-rules",
            "--ephemeral",
            "--skip-git-repo-check",
            "--sandbox",
            "read-only",
            "--cd",
            workdir,
            "--model",
            manifest["model"],
            "--config",
            f'model_reasoning_effort="{manifest["reasoning_effort"]}"',
            "--output-schema",
            str(ROOT / "evals" / "schemas" / "decision-output.json"),
            "--output-last-message",
            str(output),
            "-",
        ]
        started = time.monotonic()
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            input=prompt,
            capture_output=True,
            check=False,
            timeout=1800,
        )
        elapsed = time.monotonic() - started
    log.write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode:
        raise DataError(f"Codex call failed ({result.returncode}); see {log}")
    return _validate_decision(read_json(output)), elapsed


def execute(
    manifest: dict[str, Any],
    output_dir: Path,
    executable: str,
    manifest_path: Path,
) -> dict[str, object]:
    if not _git_state()["clean"]:
        raise DataError("execution requires a clean worktree so inputs are commit-bound")
    output_dir.mkdir(parents=True, exist_ok=False)
    (output_dir / "outputs").mkdir()
    cases = load_cases()
    records: list[dict[str, object]] = []
    blind_map: dict[str, object] = {}
    inventory = _input_inventory(manifest_path, manifest)
    for index, call in enumerate(call_plan(manifest)["items"], start=1):
        prompt = render_decision(cases[call["case_id"]], call["arm"])
        response_id = f"response-{index:02d}"
        output = output_dir / "outputs" / f"{response_id}.json"
        value, elapsed = _invoke(
            executable, manifest, prompt, output, output.with_suffix(".log")
        )
        records.append(
            {
                **call,
                "response_id": response_id,
                "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                "prompt_words": len(prompt.split()),
                "elapsed_seconds": round(elapsed, 3),
                "value": value,
            }
        )
        blind_map[response_id] = call
    if inventory != _input_inventory(manifest_path, manifest):
        raise DataError("evaluation inputs changed during execution")
    for name, value in (("records.json", records), ("blind-map.json", blind_map)):
        (output_dir / name).write_text(
            json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    artifacts = {
        name: hashlib.sha256((output_dir / name).read_bytes()).hexdigest()
        for name in ("records.json", "blind-map.json")
    }
    run = {
        "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "batch": manifest,
        "git": _git_state(),
        "inputs": inventory,
        "artifacts": artifacts,
    }
    (output_dir / "run-manifest.json").write_text(
        json.dumps(run, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return {"mode": "executed", "calls": len(records), "output_dir": str(output_dir)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest", type=Path, default=ROOT / "evals" / "manifest.json"
    )
    parser.add_argument("--render-dir", type=Path)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--call-budget", type=int)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--codex", default="codex")
    args = parser.parse_args()
    try:
        manifest_path = args.manifest.resolve()
        if not manifest_path.is_relative_to(ROOT):
            raise DataError("--manifest must be inside the method repository")
        manifest = validate_manifest(read_json(manifest_path))
        plan = call_plan(manifest)
        if args.execute:
            if args.call_budget != manifest["call_budget"]:
                raise DataError(
                    f"execution requires explicit --call-budget {manifest['call_budget']}"
                )
            if args.output_dir is None:
                raise DataError("execution requires --output-dir")
            result = execute(
                manifest, args.output_dir.resolve(), args.codex, manifest_path
            )
        else:
            if args.call_budget is not None or args.output_dir is not None:
                raise DataError("--call-budget and --output-dir require --execute")
            if args.render_dir is not None:
                render_plan(manifest, args.render_dir.resolve())
            result = {
                "mode": "render-only",
                "calls": plan["calls"],
                "decisions": plan["decisions"],
                "items": plan["items"],
            }
        print(json.dumps(result, indent=2))
    except (DataError, OSError, subprocess.SubprocessError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
