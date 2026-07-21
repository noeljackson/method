#!/usr/bin/env python3
"""Plan or execute the bounded compact Noel Method evaluation."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from methodlib import (
    DataError,
    ROOT,
    read_json,
    resolve_context_modules,
    validate_context_flags,
)
from render_eval import (
    DECISION_FIELDS,
    expected_flags,
    load_cases,
    render_decision,
    render_selection,
)


CORE_ARMS = ("neutral", "base")
PROTOCOL_ARMS = ("neutral", "base", "explicit", "auto")
MAX_CALLS = 80
REQUIRED_CALL_BUDGET = 76


def validate_manifest(value: object) -> dict[str, Any]:
    fields = {
        "schema_version", "id", "frozen", "created_at", "cases",
        "samples_per_cell", "model", "reasoning_effort", "call_budget",
        "randomization_seed", "limitations",
    }
    if not isinstance(value, dict) or set(value) != fields:
        raise DataError(f"eval manifest fields must be {sorted(fields)}")
    if value["schema_version"] != 1 or value["frozen"] is not True:
        raise DataError("eval manifest must be frozen schema version 1")
    for field in ("id", "created_at", "model", "reasoning_effort", "randomization_seed"):
        if not isinstance(value[field], str) or not value[field]:
            raise DataError(f"{field} must be non-empty text")
    cases = value["cases"]
    known = load_cases()
    if not isinstance(cases, list) or cases != list(known):
        raise DataError("manifest cases must exactly match the frozen active case order")
    if value["samples_per_cell"] != 2:
        raise DataError("compact eval requires exactly two samples per cell")
    if value["call_budget"] != REQUIRED_CALL_BUDGET:
        raise DataError(f"compact eval call_budget must be {REQUIRED_CALL_BUDGET}")
    if value["call_budget"] > MAX_CALLS:
        raise DataError(f"eval call budget exceeds hard cap {MAX_CALLS}")
    if not isinstance(value["limitations"], list) or not all(
        isinstance(item, str) and item for item in value["limitations"]
    ):
        raise DataError("limitations must be a string array")
    return value


def planned_groups(manifest: dict[str, Any]) -> list[list[dict[str, object]]]:
    cases = load_cases()
    groups: list[list[dict[str, object]]] = []
    for case_id in manifest["cases"]:
        family = cases[case_id]["family"]
        for sample in range(1, manifest["samples_per_cell"] + 1):
            arms = CORE_ARMS if family == "core" else PROTOCOL_ARMS[:-1]
            for arm in arms:
                groups.append([{
                    "case_id": case_id,
                    "sample": sample,
                    "arm": arm,
                    "stage": "decision",
                }])
            if family != "core":
                groups.append([
                    {
                        "case_id": case_id,
                        "sample": sample,
                        "arm": "auto",
                        "stage": "selection",
                    },
                    {
                        "case_id": case_id,
                        "sample": sample,
                        "arm": "auto",
                        "stage": "decision",
                        "same_session": True,
                    },
                ])
    random.Random(manifest["randomization_seed"]).shuffle(groups)
    return groups


def call_plan(manifest: dict[str, Any]) -> dict[str, object]:
    groups = planned_groups(manifest)
    calls = [call for group in groups for call in group]
    decisions = [call for call in calls if call["stage"] == "decision"]
    selections = [call for call in calls if call["stage"] == "selection"]
    return {
        "manifest": manifest["id"],
        "mode": "render-only",
        "calls": len(calls),
        "decisions": len(decisions),
        "selections": len(selections),
        "hard_cap": MAX_CALLS,
        "groups": groups,
    }


def render_prompts(manifest: dict[str, Any], output_dir: Path) -> None:
    cases = load_cases()
    output_dir.mkdir(parents=True, exist_ok=True)
    plan = call_plan(manifest)
    (output_dir / "call-plan.json").write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    for group_index, group in enumerate(plan["groups"], start=1):
        for call_index, call in enumerate(group, start=1):
            case = cases[call["case_id"]]
            stem = (
                f"{group_index:03}-{call_index}-{call['case_id']}-"
                f"s{call['sample']}-{call['arm']}-{call['stage']}"
            )
            if call["stage"] == "selection":
                prompt = render_selection(case)
            elif call["arm"] == "auto":
                prompt = (
                    "# Deferred same-session continuation\n\n"
                    "This prompt is rendered only after the selection result is known. "
                    "No answer-key flags are substituted during render-only planning.\n"
                )
            else:
                prompt = render_decision(case, call["arm"])
            (output_dir / f"{stem}.md").write_text(prompt, encoding="utf-8")


def _validate_decision(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != DECISION_FIELDS:
        raise DataError(f"decision output fields must be {sorted(DECISION_FIELDS)}")
    if value["disposition"] not in {"PROCEED", "HOLD", "CONTAIN", "TERMINATE"}:
        raise DataError("invalid disposition")
    if not isinstance(value["decision"], str) or not value["decision"]:
        raise DataError("decision must be non-empty text")
    for field in DECISION_FIELDS - {"disposition", "decision"}:
        if not isinstance(value[field], list) or not all(isinstance(item, str) for item in value[field]):
            raise DataError(f"{field} must be a string array")
    return value


def _session_id(console: str) -> str:
    for line in console.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        for key in ("thread_id", "session_id"):
            if isinstance(event.get(key), str) and event[key]:
                return event[key]
        if isinstance(event.get("thread"), dict) and isinstance(event["thread"].get("id"), str):
            return event["thread"]["id"]
    raise DataError("Codex event stream did not expose a resumable session id")


def _invoke(
    command: list[str], prompt: str, output: Path, log: Path
) -> tuple[dict[str, object], str, float]:
    output.parent.mkdir(parents=True, exist_ok=True)
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
    console = result.stdout + result.stderr
    log.write_text(console, encoding="utf-8")
    if result.returncode:
        raise DataError(f"Codex call failed ({result.returncode}); see {log}")
    return read_json(output), console, elapsed


def _base_command(
    executable: str, workdir: str, manifest: dict[str, Any], schema: Path, output: Path
) -> list[str]:
    return [
        executable, "exec", "--ignore-user-config", "--ignore-rules",
        "--skip-git-repo-check", "--sandbox", "read-only", "--cd", workdir,
        "--model", manifest["model"],
        "--config", f'model_reasoning_effort="{manifest["reasoning_effort"]}"',
        "--output-schema", str(schema), "--output-last-message", str(output), "-",
    ]


def _record(
    call: dict[str, object], prompt: str, value: dict[str, object], elapsed: float
) -> dict[str, object]:
    return {
        **call,
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "prompt_words": len(prompt.split()),
        "elapsed_seconds": round(elapsed, 3),
        "value": value,
    }


def _input_inventory(manifest_path: Path, manifest: dict[str, Any]) -> list[dict[str, str]]:
    cases = load_cases()
    paths = {
        manifest_path,
        ROOT / "evals" / "cases.json",
        ROOT / "evals" / "RUBRIC.md",
        ROOT / "evals" / "schemas" / "context-output.json",
        ROOT / "evals" / "schemas" / "decision-output.json",
        ROOT / "scripts" / "methodlib.py",
        ROOT / "scripts" / "render_eval.py",
        ROOT / "scripts" / "run_eval_batch.py",
        ROOT / "src" / "context.json",
        ROOT / "dist" / "NOEL-METHOD.md",
    }
    paths.update(path for path in (ROOT / "dist" / "pack").rglob("*") if path.is_file())
    for case_id in manifest["cases"]:
        profile = cases[case_id]["profile"]
        paths.add(ROOT / "evals" / "fixtures" / "profiles" / f"{profile}.md")
        paths.add(ROOT / "evals" / "fixtures" / "neutral-briefs" / f"{profile}.md")
    return [
        {
            "path": str(path.relative_to(ROOT)),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        for path in sorted(paths)
    ]


def _anonymous_id(seed: str, call: dict[str, object]) -> str:
    identity = f"{seed}\0{call['case_id']}\0{call['arm']}\0{call['sample']}"
    return "response-" + hashlib.sha256(identity.encode()).hexdigest()[:12]


def execute(
    manifest: dict[str, Any], output_dir: Path, executable: str,
    manifest_path: Path = ROOT / "evals" / "manifest.json",
) -> dict[str, object]:
    cases = load_cases()
    groups = planned_groups(manifest)
    output_dir.mkdir(parents=True, exist_ok=False)
    started_at = datetime.now(timezone.utc).isoformat()
    records: list[dict[str, object]] = []
    call_count = 0
    for group in groups:
        first = group[0]
        case = cases[first["case_id"]]
        if len(group) == 1:
            call = first
            prompt = render_decision(case, call["arm"])
            output = output_dir / "outputs" / (
                f"{call['case_id']}-s{call['sample']}-{call['arm']}.json"
            )
            log = output.with_suffix(".log")
            with tempfile.TemporaryDirectory(prefix="noel-method-eval-") as workdir:
                command = _base_command(
                    executable, workdir, manifest,
                    ROOT / "evals" / "schemas" / "decision-output.json", output,
                )
                command.insert(2, "--ephemeral")
                raw, _, elapsed = _invoke(command, prompt, output, log)
            value = _validate_decision(raw)
            record = _record(call, prompt, value, elapsed)
            record["modules_supplied"] = (
                [] if call["arm"] == "neutral" else ["BASE.md"] + (
                    resolve_context_modules(expected_flags(case))
                    if call["arm"] == "explicit" else []
                )
            )
            records.append(record)
            call_count += 1
        else:
            selection_call, decision_call = group
            selection_prompt = render_selection(case)
            selection_output = output_dir / "outputs" / (
                f"{selection_call['case_id']}-s{selection_call['sample']}-auto-selection.json"
            )
            selection_log = selection_output.with_suffix(".log")
            decision_output = output_dir / "outputs" / (
                f"{decision_call['case_id']}-s{decision_call['sample']}-auto.json"
            )
            decision_log = decision_output.with_suffix(".log")
            with tempfile.TemporaryDirectory(prefix="noel-method-session-") as workdir:
                command = _base_command(
                    executable, workdir, manifest,
                    ROOT / "evals" / "schemas" / "context-output.json", selection_output,
                )
                command.insert(2, "--json")
                raw, console, elapsed = _invoke(
                    command, selection_prompt, selection_output, selection_log
                )
                flags = validate_context_flags(raw)
                conversation = _session_id(console)
                decision_prompt = render_decision(
                    case, "auto", flags, continuation=True
                )
                resume = [
                    executable, "exec", "resume", "--json", "--ignore-user-config",
                    "--ignore-rules", "--skip-git-repo-check", "--model", manifest["model"],
                    "--config", f'model_reasoning_effort="{manifest["reasoning_effort"]}"',
                    "--output-schema", str(ROOT / "evals" / "schemas" / "decision-output.json"),
                    "--output-last-message", str(decision_output), conversation, "-",
                ]
                decision_raw, _, decision_elapsed = _invoke(
                    resume, decision_prompt, decision_output, decision_log
                )
            decision = _validate_decision(decision_raw)
            selection_record = _record(
                selection_call, selection_prompt, flags, elapsed
            )
            selection_record["modules_supplied"] = ["INDEX.md", "BASE.md"]
            decision_record = _record(
                decision_call, decision_prompt, decision, decision_elapsed
            )
            decision_record["context_flags"] = flags
            decision_record["modules_supplied"] = ["BASE.md", *resolve_context_modules(flags)]
            records.extend((selection_record, decision_record))
            call_count += 2
        if call_count > manifest["call_budget"]:
            raise DataError("runtime call count exceeded the accepted budget")
    if call_count != manifest["call_budget"]:
        raise DataError(f"runtime made {call_count} calls; expected {manifest['call_budget']}")

    decisions = [record for record in records if record["stage"] == "decision"]
    bundle = []
    mapping: dict[str, object] = {}
    for record in decisions:
        response_id = _anonymous_id(manifest["randomization_seed"], record)
        bundle.append({
            "response_id": response_id,
            "case_id": record["case_id"],
            "response": record["value"],
        })
        mapping[response_id] = {
            "case_id": record["case_id"], "arm": record["arm"], "sample": record["sample"]
        }
    random.Random(manifest["randomization_seed"] + ":blind").shuffle(bundle)
    (output_dir / "records.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    (output_dir / "blind-bundle.json").write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    (output_dir / "blind-map.json").write_text(json.dumps(mapping, indent=2) + "\n", encoding="utf-8")
    (output_dir / "human-review-key.json").write_text(
        json.dumps({case_id: {"expected": cases[case_id]["expected"], "forbidden": cases[case_id]["forbidden"]} for case_id in manifest["cases"]}, indent=2) + "\n",
        encoding="utf-8",
    )
    summary = {
        "manifest": manifest["id"],
        "calls": call_count,
        "decisions": len(decisions),
        "selections": len(records) - len(decisions),
        "human_scoring_required": True,
        "model_judges_run": 0,
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    git_head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=True
    ).stdout.strip()
    git_status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True, capture_output=True, check=True
    ).stdout.splitlines()
    run_manifest = {
        "batch": manifest,
        "started_at": started_at,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "git": {
            "head": git_head,
            "worktree_clean": not git_status,
            "changed_paths": git_status,
        },
        "input_inventory": _input_inventory(manifest_path.resolve(), manifest),
        "calls": [
            {
                key: record[key]
                for key in (
                    "case_id", "sample", "arm", "stage", "prompt_sha256",
                    "prompt_words", "elapsed_seconds", "modules_supplied"
                )
                if key in record
            }
            | ({"context_flags": record["context_flags"]} if "context_flags" in record else {})
            for record in records
        ],
    }
    (output_dir / "run-manifest.json").write_text(
        json.dumps(run_manifest, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=ROOT / "evals" / "manifest.json")
    parser.add_argument("--render-dir", type=Path)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--call-budget", type=int)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--codex", default="codex")
    args = parser.parse_args()
    try:
        manifest = validate_manifest(read_json(args.manifest.resolve()))
        plan = call_plan(manifest)
        if plan["calls"] != manifest["call_budget"] or plan["calls"] > MAX_CALLS:
            raise DataError("derived plan violates its fixed call budget")
        if args.render_dir:
            render_prompts(manifest, args.render_dir.resolve())
        if not args.execute:
            if args.call_budget is not None or args.output_dir is not None:
                raise DataError("--call-budget and --output-dir require --execute")
            print(json.dumps(plan, indent=2))
            return 0
        if args.call_budget != REQUIRED_CALL_BUDGET:
            raise DataError(
                f"execution requires explicit --call-budget {REQUIRED_CALL_BUDGET}"
            )
        if args.call_budget > MAX_CALLS:
            raise DataError(f"execution exceeds hard cap {MAX_CALLS}")
        if args.output_dir is None:
            raise DataError("execution requires --output-dir")
        print(json.dumps(execute(
            manifest, args.output_dir.resolve(), args.codex, args.manifest.resolve()
        ), indent=2))
    except (DataError, OSError, subprocess.SubprocessError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
