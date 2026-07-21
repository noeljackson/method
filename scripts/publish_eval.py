#!/usr/bin/env python3
"""Publish aggregate results from a completed, human-scored compact eval."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

from methodlib import DataError, ROOT, read_json
from render_eval import load_cases
from score_eval import score_decision, score_selection


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def quadratic_weighted_kappa(first: list[int], second: list[int], maximum: int = 9) -> float:
    if len(first) != len(second) or not first:
        raise DataError("reliability requires paired non-empty score arrays")
    observed = sum(((left - right) / maximum) ** 2 for left, right in zip(first, second)) / len(first)
    first_counts = [first.count(value) / len(first) for value in range(maximum + 1)]
    second_counts = [second.count(value) / len(second) for value in range(maximum + 1)]
    expected = sum(
        first_counts[left] * second_counts[right] * ((left - right) / maximum) ** 2
        for left in range(maximum + 1)
        for right in range(maximum + 1)
    )
    return 1.0 if expected == 0 and observed == 0 else 1 - observed / expected


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else math.nan


def validate_human_scores(
    value: object,
    mapping: dict[str, object],
    cases: dict[str, dict[str, object]],
) -> tuple[dict[str, list[dict[str, object]]], dict[str, object]]:
    if not isinstance(value, dict) or set(value) != {"schema_version", "reviewers", "scores"}:
        raise DataError("human scores need schema_version, reviewers, and scores")
    if value["schema_version"] != 1:
        raise DataError("human scores must use schema version 1")
    if not isinstance(value["reviewers"], list) or len(value["reviewers"]) < 2:
        raise DataError("name at least two independent reviewers")
    raw_scores = value["scores"]
    if not isinstance(raw_scores, dict) or set(raw_scores) != set(mapping):
        raise DataError("human scores must cover every anonymous response exactly once")
    scored: dict[str, list[dict[str, object]]] = {}
    paired_first: list[int] = []
    paired_second: list[int] = []
    double_strata: set[tuple[str, str]] = set()
    for response_id, judgments in raw_scores.items():
        if not isinstance(judgments, list) or not 1 <= len(judgments) <= 2:
            raise DataError(f"{response_id}: supply one or two independent judgments")
        metadata = mapping[response_id]
        case = cases[metadata["case_id"]]
        results = [score_decision(case, judgment) for judgment in judgments]
        scored[response_id] = results
        if len(results) == 2:
            paired_first.append(round(results[0]["content_points"]))
            paired_second.append(round(results[1]["content_points"]))
            double_strata.add((case["family"], metadata["arm"]))
    required_strata = {
        (case["family"], arm)
        for case in cases.values()
        for arm in (
            ("neutral", "base") if case["family"] == "core"
            else ("neutral", "base", "explicit", "auto")
        )
    }
    if not required_strata.issubset(double_strata):
        missing = sorted(required_strata - double_strata)
        raise DataError(f"double-scored sample is not stratified; missing {missing}")
    kappa = quadratic_weighted_kappa(paired_first, paired_second)
    reliability = {
        "double_scored_responses": len(paired_first),
        "quadratic_weighted_kappa": round(kappa, 6),
        "threshold": 0.8,
        "passed": kappa >= 0.8,
    }
    return scored, reliability


def aggregate(
    records: list[dict[str, object]],
    mapping: dict[str, object],
    scored: dict[str, list[dict[str, object]]],
    seed: str,
) -> dict[str, object]:
    by_arm: dict[str, list[float]] = defaultdict(list)
    hard_by_arm: dict[str, int] = defaultdict(int)
    by_case_arm: dict[tuple[str, str], list[float]] = defaultdict(list)
    for response_id, metadata in mapping.items():
        results = scored[response_id]
        points = mean([result["content_points"] for result in results])
        arm = metadata["arm"]
        by_arm[arm].append(points)
        by_case_arm[(metadata["case_id"], arm)].append(points)
        hard_by_arm[arm] += int(any(result["hard_failure"] for result in results))
    arms = {
        arm: {
            "responses": len(values),
            "mean_out_of_9": round(mean(values), 6),
            "hard_failure_responses": hard_by_arm[arm],
        }
        for arm, values in sorted(by_arm.items())
    }
    cases = {
        f"{case_id}:{arm}": round(mean(values), 6)
        for (case_id, arm), values in sorted(by_case_arm.items())
    }
    return {"by_arm": arms, "by_case_arm": cases}


def acceptance(
    records: list[dict[str, object]], aggregate_result: dict[str, object]
) -> dict[str, object]:
    cases = load_cases()
    selections = [record for record in records if record["stage"] == "selection"]
    selection_scores = [
        score_selection(cases[record["case_id"]], record["value"])
        for record in selections
    ]
    case_means = aggregate_result["by_case_arm"]
    core_wins = sum(
        case_means[f"{case_id}:base"] > case_means[f"{case_id}:neutral"]
        for case_id, case in cases.items() if case["family"] == "core"
    )
    protocol_cases = [case_id for case_id, case in cases.items() if case["family"] != "core"]
    explicit_deltas = [
        case_means[f"{case_id}:explicit"] - case_means[f"{case_id}:base"]
        for case_id in protocol_cases
    ]
    auto_deltas = [
        case_means[f"{case_id}:auto"] - case_means[f"{case_id}:explicit"]
        for case_id in protocol_cases
    ]
    hard_failures = sum(
        arm["hard_failure_responses"]
        for arm in aggregate_result["by_arm"].values()
    )
    checks = {
        "automatic_required_protocol_recall": all(
            score["required_protocol_recalled"] for score in selection_scores
        ),
        "base_beats_neutral_on_three_of_four_core_cases": core_wins >= 3,
        "explicit_protocol_mean_lift_at_least_half_point": mean(explicit_deltas) >= 0.5,
        "no_protocol_case_regresses_more_than_one_point": min(explicit_deltas) >= -1,
        "automatic_within_half_point_of_explicit": abs(mean(auto_deltas)) <= 0.5,
        "zero_forbidden_endorsement_hard_failures": hard_failures == 0,
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "measurements": {
            "core_case_wins": core_wins,
            "explicit_minus_base_mean": round(mean(explicit_deltas), 6),
            "auto_minus_explicit_mean": round(mean(auto_deltas), 6),
            "hard_failure_responses": hard_failures,
        },
    }


def summary_markdown(
    run: dict[str, object], aggregate_result: dict[str, object],
    reliability: dict[str, object], gate: dict[str, object]
) -> str:
    rows = ["| Arm | Responses | Mean / 9 | Hard failures |", "| --- | ---: | ---: | ---: |"]
    for arm, value in aggregate_result["by_arm"].items():
        rows.append(
            f"| {arm} | {value['responses']} | {value['mean_out_of_9']:.3f} | "
            f"{value['hard_failure_responses']} |"
        )
    checks = "\n".join(
        f"- {'PASS' if passed else 'FAIL'} — `{name}`"
        for name, passed in gate["checks"].items()
    )
    return f"""# {run['batch']['id']} evaluation

Status: **{'RELEASE GATE PASSED' if gate['passed'] else 'RELEASE GATE FAILED'}**

- Method commit: `{run['git']['head']}`
- Model: `{run['batch']['model']}` at `{run['batch']['reasoning_effort']}`
- Calls: 76; decisions: 64; model judges: 0
- Human double-scored responses: {reliability['double_scored_responses']}
- Quadratic weighted kappa: {reliability['quadratic_weighted_kappa']:.3f}

## Decision results

{chr(10).join(rows)}

## Acceptance checks

{checks}

The report is aggregate evidence. Raw prompts, decisions, logs, human
judgments, and the unblinding map remain in the ignored local run directory.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_directory", type=Path)
    parser.add_argument("human_scores", type=Path)
    parser.add_argument("--reports-root", type=Path, default=ROOT / "evals" / "reports")
    args = parser.parse_args()
    try:
        run_dir = args.run_directory.resolve()
        run = read_json(run_dir / "run-manifest.json")
        summary = read_json(run_dir / "summary.json")
        records = read_json(run_dir / "records.json")
        mapping = read_json(run_dir / "blind-map.json")
        human = read_json(args.human_scores.resolve())
        if not isinstance(run, dict) or not isinstance(summary, dict):
            raise DataError("run manifest and summary must be objects")
        if summary.get("calls") != 76 or summary.get("decisions") != 64:
            raise DataError("only a completed 76-call compact run can be published")
        if not isinstance(records, list) or not isinstance(mapping, dict):
            raise DataError("run records or blind map are malformed")
        cases = load_cases()
        scored, reliability = validate_human_scores(human, mapping, cases)
        if not reliability["passed"]:
            raise DataError(
                "inter-rater reliability is below 0.8; reconcile the rubric before publishing"
            )
        aggregate_result = aggregate(
            records, mapping, scored, run["batch"]["randomization_seed"]
        )
        gate = acceptance(records, aggregate_result)
        report_id = run["batch"]["id"]
        destination = args.reports_root.resolve() / report_id
        if destination.exists():
            raise DataError(f"report directory already exists: {destination}")
        destination.mkdir(parents=True)
        results = {
            "batch_id": report_id,
            "method_commit": run["git"]["head"],
            "aggregate": aggregate_result,
            "reliability": reliability,
            "acceptance": gate,
            "limitations": run["batch"]["limitations"],
        }
        write_json(destination / "results.json", results)
        write_json(destination / "run-manifest.json", run)
        (destination / "SUMMARY.md").write_text(
            summary_markdown(run, aggregate_result, reliability, gate), encoding="utf-8"
        )
        hashes = {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in destination.iterdir() if path.is_file()
        }
        write_json(destination / "SHA256SUMS.json", hashes)
        print(destination)
    except (DataError, KeyError, OSError, TypeError, ValueError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
