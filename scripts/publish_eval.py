#!/usr/bin/env python3
"""Publish aggregate results from a completed sparse eval."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path, PurePosixPath

from methodlib import DataError, ROOT, read_json
from render_eval import load_cases, render_decision
from run_eval_batch import call_plan, validate_manifest
from score_eval import score_decision


def quadratic_weighted_kappa(
    first: list[int], second: list[int], maximum: int = 9
) -> float:
    if len(first) != len(second) or not first:
        raise DataError("reliability requires paired non-empty score arrays")
    observed = sum(
        ((left - right) / maximum) ** 2
        for left, right in zip(first, second)
    ) / len(first)
    first_counts = [
        first.count(value) / len(first) for value in range(maximum + 1)
    ]
    second_counts = [
        second.count(value) / len(second) for value in range(maximum + 1)
    ]
    expected = sum(
        first_counts[left]
        * second_counts[right]
        * ((left - right) / maximum) ** 2
        for left in range(maximum + 1)
        for right in range(maximum + 1)
    )
    return 1.0 if expected == 0 and observed == 0 else 1 - observed / expected


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else math.nan


def _current_input_hashes(run: dict[str, object]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    if not isinstance(run.get("inputs"), list):
        raise DataError("run inputs are malformed")
    for item in run["inputs"]:
        if (
            not isinstance(item, dict)
            or set(item) != {"path", "sha256"}
            or not isinstance(item["path"], str)
        ):
            raise DataError("run input entry is malformed")
        pure = PurePosixPath(item["path"])
        if pure.is_absolute() or ".." in pure.parts or str(pure) != item["path"]:
            raise DataError(f"unsafe run input path: {item['path']}")
        candidate = ROOT / item["path"]
        path = candidate.resolve()
        if (
            not path.is_relative_to(ROOT.resolve())
            or candidate.is_symlink()
            or any(
                parent.is_symlink()
                for parent in candidate.parents
                if parent != ROOT.parent
            )
            or not path.is_file()
        ):
            raise DataError(f"run input is not a contained regular file: {item['path']}")
        output.append(
            {
                "path": item["path"],
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    return output


def validate_run_artifacts(
    run_dir: Path,
    run: dict[str, object],
    records: object,
    mapping: object,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    artifacts = run.get("artifacts")
    if not isinstance(artifacts, dict) or set(artifacts) != {
        "records.json",
        "blind-map.json",
    }:
        raise DataError("run artifact hashes are missing")
    for name, expected in artifacts.items():
        if (
            not isinstance(expected, str)
            or hashlib.sha256((run_dir / name).read_bytes()).hexdigest() != expected
        ):
            raise DataError(f"run artifact hash mismatch: {name}")
    if not isinstance(records, list) or not isinstance(mapping, dict):
        raise DataError("run records or blind map are malformed")
    manifest = validate_manifest(run.get("batch"))
    plan = call_plan(manifest)["items"]
    if len(records) != len(plan) or len(mapping) != len(plan):
        raise DataError("run is incomplete")
    cases = load_cases()
    record_fields = {
        "case_id",
        "arm",
        "sample",
        "response_id",
        "prompt_sha256",
        "prompt_words",
        "elapsed_seconds",
        "value",
    }
    for index, (record, expected_call) in enumerate(zip(records, plan), start=1):
        response_id = f"response-{index:02d}"
        if not isinstance(record, dict) or set(record) != record_fields:
            raise DataError(f"{response_id}: malformed record")
        call = {
            "case_id": record["case_id"],
            "arm": record["arm"],
            "sample": record["sample"],
        }
        if (
            record["response_id"] != response_id
            or call != expected_call
            or mapping.get(response_id) != expected_call
        ):
            raise DataError(f"{response_id}: record, blind map, and plan differ")
        prompt = render_decision(cases[record["case_id"]], record["arm"])
        if (
            record["prompt_sha256"] != hashlib.sha256(prompt.encode()).hexdigest()
            or record["prompt_words"] != len(prompt.split())
        ):
            raise DataError(f"{response_id}: prompt binding differs")
    return records, mapping


def validate_human_scores(
    value: object,
    mapping: dict[str, object],
    cases: dict[str, dict[str, object]],
) -> tuple[dict[str, list[dict[str, object]]], float]:
    if not isinstance(value, dict) or set(value) != {"schema_version", "scores"}:
        raise DataError("human scores need schema_version and scores")
    if value["schema_version"] != 2:
        raise DataError("human scores must use schema version 2")
    if not isinstance(value["scores"], dict) or set(value["scores"]) != set(mapping):
        raise DataError("human scores must cover every blind response exactly once")
    scored: dict[str, list[dict[str, object]]] = {}
    first: list[int] = []
    second: list[int] = []
    for response_id, entries in value["scores"].items():
        if not isinstance(entries, list) or len(entries) != 2:
            raise DataError(f"{response_id}: exactly two reviews are required")
        reviewer_ids: list[str] = []
        results: list[dict[str, object]] = []
        for entry in entries:
            if not isinstance(entry, dict) or set(entry) != {"reviewer_id", "judgment"}:
                raise DataError(
                    f"{response_id}: reviews need reviewer_id and judgment"
                )
            reviewer = entry["reviewer_id"]
            if not isinstance(reviewer, str) or not reviewer:
                raise DataError(f"{response_id}: reviewer_id must be non-empty")
            reviewer_ids.append(reviewer)
            case = cases[mapping[response_id]["case_id"]]
            results.append(score_decision(case, entry["judgment"]))
        if len(set(reviewer_ids)) != 2:
            raise DataError(f"{response_id}: reviewers must be distinct")
        scored[response_id] = results
        first.append(round(results[0]["content_points"]))
        second.append(round(results[1]["content_points"]))
    return scored, quadratic_weighted_kappa(first, second)


def aggregate(
    mapping: dict[str, object],
    scored: dict[str, list[dict[str, object]]],
) -> dict[str, object]:
    points: dict[str, list[float]] = defaultdict(list)
    hard: dict[str, int] = defaultdict(int)
    case_arm: dict[tuple[str, str], float] = {}
    for response_id, metadata in mapping.items():
        results = scored[response_id]
        value = _mean([result["content_points"] for result in results])
        arm = metadata["arm"]
        points[arm].append(value)
        hard[arm] += int(any(result["hard_failure"] for result in results))
        case_arm[(metadata["case_id"], arm)] = value
    routed_wins = sum(
        case_arm[(case_id, "routed")] >= case_arm[(case_id, "neutral")]
        for case_id in {metadata["case_id"] for metadata in mapping.values()}
    )
    return {
        "arms": {
            arm: {
                "responses": len(values),
                "mean_out_of_9": round(_mean(values), 6),
                "hard_failures": hard[arm],
            }
            for arm, values in sorted(points.items())
        },
        "routed_noninferior_cases": routed_wins,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_directory", type=Path)
    parser.add_argument("human_scores", type=Path)
    parser.add_argument(
        "--reports-root", type=Path, default=ROOT / "evals" / "reports"
    )
    args = parser.parse_args()
    try:
        run_dir = args.run_directory.resolve()
        run = read_json(run_dir / "run-manifest.json")
        records = read_json(run_dir / "records.json")
        mapping = read_json(run_dir / "blind-map.json")
        human = read_json(args.human_scores.resolve())
        if not isinstance(run, dict) or run.get("schema_version") != 2:
            raise DataError("sparse run files are malformed")
        records, mapping = validate_run_artifacts(run_dir, run, records, mapping)
        if run["inputs"] != _current_input_hashes(run):
            raise DataError("current inputs differ from the executed run")
        cases = load_cases()
        scored, kappa = validate_human_scores(human, mapping, cases)
        result = aggregate(mapping, scored)
        arms = result["arms"]
        checks = {
            "distinct_double_review": True,
            "quadratic_weighted_kappa_at_least_0_7": kappa >= 0.7,
            "zero_routed_hard_failures": arms["routed"]["hard_failures"] == 0,
            "routed_mean_not_below_neutral": (
                arms["routed"]["mean_out_of_9"] >= arms["neutral"]["mean_out_of_9"]
            ),
            "routed_noninferior_on_three_of_four_cases": (
                result["routed_noninferior_cases"] >= 3
            ),
        }
        report = {
            "schema_version": 2,
            "run_id": run["batch"]["id"],
            "reliability": {"quadratic_weighted_kappa": round(kappa, 6)},
            "results": result,
            "release_gate": {"passed": all(checks.values()), "checks": checks},
            "limitations": run["batch"]["limitations"],
        }
        destination = args.reports_root.resolve() / run["batch"]["id"]
        if destination.exists():
            raise DataError(f"report directory already exists: {destination}")
        destination.mkdir(parents=True)
        (destination / "results.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(json.dumps(report, indent=2))
    except (DataError, OSError, KeyError, TypeError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
