use method_core::{
    ProgramState, ProtocolFlags, context_protocols, parse_json_strict, validate_evidence_receipt,
    validate_program_document, validate_program_transition, verify_pack_directory,
};
use serde_json::Value;
use std::collections::BTreeSet;
use std::fs;
use std::path::{Path, PathBuf};

fn root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
}

fn json(path: impl AsRef<Path>) -> Value {
    parse_json_strict(&fs::read(path).unwrap()).unwrap()
}

fn program(revision: u64, state: &str, next: &str, termination: Option<&str>) -> String {
    let termination = termination
        .map(|reason| format!("termination_reason = \"{reason}\"\n"))
        .unwrap_or_default();
    format!(
        "```toml\nschema_version = 1\ncontrol_revision = {revision}\nstate = \"{state}\"\ncoordinator = \"Codex /root\"\n{termination}```\n\n## Goal\n\nShip one cohesive result.\n\n## Done when\n\nThe accepted checks pass.\n\n## Current\n\nThe exact source is ready.\n\n## Next\n\n{next}\n\n## Needs from human\n\nNone\n\n## Boundaries\n\nDo not mutate production.\n\n## Evidence\n\nExact commit and test output.\n"
    )
}

fn receipt() -> Value {
    json(root().join("templates/evidence-receipt.json"))
}

#[test]
fn explicit_flags_select_protocols_in_runtime_order() {
    assert!(context_protocols(&ProtocolFlags::default()).is_empty());
    assert_eq!(
        context_protocols(&ProtocolFlags {
            program: true,
            experiment: true,
            secrets: true,
        }),
        ["program", "experiment", "secrets"]
    );
    assert_eq!(
        context_protocols(&ProtocolFlags {
            secrets: true,
            ..ProtocolFlags::default()
        }),
        ["secrets"]
    );
}

#[test]
fn program_accepts_crlf_and_ignores_headings_inside_fenced_code() {
    let value = program(7, "ACTIVE", "Open the exact-head pull request.", None).replace(
        "The exact source is ready.",
        "The exact source is ready.\n\n```markdown\n## Goal\n## Not a control section\n```",
    );
    let value = value.replace('\n', "\r\n");
    let document = validate_program_document(&value).unwrap();
    assert_eq!(document.metadata.control_revision, 7);
    assert_eq!(document.metadata.state, ProgramState::Active);
    assert!(document.sections["Current"].contains("## Not a control section"));
    assert!(document.warnings.is_empty());
}

#[test]
fn program_requires_the_toml_header_first_and_exact_ordered_sections() {
    let valid = program(1, "ACTIVE", "Implement the bounded change.", None);
    for invalid in [
        format!("preamble\n{valid}"),
        valid.replacen("```toml", "```TOML", 1),
        valid.replace("## Done when", "## Acceptance"),
        valid.replace("## Done when", "## Next duplicate"),
        valid.replace("## Current", "## Unexpected\n\nNo.\n\n## Current"),
        valid.replace(
            "## Goal\n\nShip one cohesive result.",
            "## Goal\n\nShip one cohesive result.\n\n## Goal\n\nDuplicate.",
        ),
    ] {
        assert!(
            validate_program_document(&invalid).is_err(),
            "invalid Program shape was accepted:\n{invalid}"
        );
    }

    let mut extra_metadata = valid.clone();
    extra_metadata = extra_metadata.replace(
        "coordinator = \"Codex /root\"",
        "coordinator = \"Codex /root\"\nmethod_version = \"0.9.0\"",
    );
    assert!(validate_program_document(&extra_metadata).is_err());
}

#[test]
fn program_metadata_and_state_semantics_are_strict() {
    assert!(validate_program_document(&program(1, "ACTIVE", "Continue.", None)).is_ok());
    assert!(
        validate_program_document(&program(
            1,
            "STOPPED_FOR_REPLAN",
            "Repair the live control.",
            None,
        ))
        .is_ok()
    );
    assert!(validate_program_document(&program(1, "COMPLETE", "None", None)).is_ok());
    assert!(
        validate_program_document(&program(1, "TERMINATED", "None", Some("SUPERSEDED"),)).is_ok()
    );

    for invalid in [
        program(1, "ACTIVE", "None", None),
        program(1, "STOPPED_FOR_REPLAN", "None", None),
        program(1, "COMPLETE", "More work.", None),
        program(1, "COMPLETE", "None", Some("SAFETY")),
        program(1, "TERMINATED", "None", None),
        program(1, "TERMINATED", "More work.", Some("OWNER_CANCELLED")),
        program(0, "ACTIVE", "Continue.", None),
        program(1, "PAUSED", "Continue.", None),
        program(1, "TERMINATED", "None", Some("UNKNOWN_REASON")),
    ] {
        assert!(validate_program_document(&invalid).is_err());
    }

    let blank_coordinator = program(1, "ACTIVE", "Continue.", None)
        .replace("coordinator = \"Codex /root\"", "coordinator = \"   \"");
    assert!(validate_program_document(&blank_coordinator).is_err());
}

#[test]
fn program_transitions_increment_once_and_terminal_controls_do_not_resume() {
    let first = program(3, "ACTIVE", "Continue.", None);
    let next = program(4, "ACTIVE", "Open the pull request.", None);
    assert!(validate_program_transition(&next, &first).is_ok());
    assert!(validate_program_transition(&program(5, "ACTIVE", "Continue.", None), &first).is_err());
    assert!(validate_program_transition(&first, &first).is_err());

    let complete = program(4, "COMPLETE", "None", None);
    assert!(validate_program_transition(&complete, &first).is_ok());
    assert!(
        validate_program_transition(&program(5, "ACTIVE", "Resume.", None), &complete,).is_err()
    );
}

#[test]
fn long_program_controls_warn_without_becoming_invalid() {
    let words = std::iter::repeat_n("current", 710)
        .collect::<Vec<_>>()
        .join(" ");
    let value =
        program(1, "ACTIVE", "Continue.", None).replace("The exact source is ready.", &words);
    let document = validate_program_document(&value).unwrap();
    assert!(document.word_count > 700);
    assert_eq!(document.warnings.len(), 1);
}

#[test]
fn evidence_receipt_v2_supports_claim_scoped_outcomes() {
    let mut value = receipt();
    value["durability_reason"] = Value::from("successor_gap");
    value["claims"] = serde_json::json!([
        {
            "id": "cache.manifest",
            "outcome": "SUPPORTED",
            "observation": "the exact installer manifest exists"
        },
        {
            "id": "cache.blob",
            "outcome": "REJECTED",
            "observation": "one referenced blob is absent"
        },
        {
            "id": "guest.pull",
            "outcome": "INCONCLUSIVE",
            "observation": "the guest did not reach this claim"
        }
    ]);
    let receipt = validate_evidence_receipt(&value).unwrap();
    assert_eq!(receipt.schema_version, 2);
    assert_eq!(receipt.claims.len(), 3);
}

#[test]
fn evidence_receipt_rejects_legacy_ambiguous_or_duplicate_data() {
    let mut cases = Vec::new();

    let mut old = receipt();
    old["schema_version"] = Value::from(1);
    cases.push(old);

    let mut no_claims = receipt();
    no_claims["claims"] = serde_json::json!([]);
    cases.push(no_claims);

    let mut duplicate_claim = receipt();
    duplicate_claim["claims"] = serde_json::json!([
        {"id": "same", "outcome": "SUPPORTED", "observation": "one"},
        {"id": "same", "outcome": "REJECTED", "observation": "two"}
    ]);
    cases.push(duplicate_claim);

    let mut invalid_id = receipt();
    invalid_id["claims"][0]["id"] = Value::from("not portable");
    cases.push(invalid_id);

    let mut duplicate_limit = receipt();
    duplicate_limit["limitations"] = serde_json::json!(["same", "same"]);
    cases.push(duplicate_limit);

    let mut unknown = receipt();
    unknown["result"] = Value::from("PASS");
    cases.push(unknown);

    let mut broad_outcome = receipt();
    broad_outcome["claims"][0]["outcome"] = Value::from("UNCLASSIFIED");
    cases.push(broad_outcome);

    let mut session_alone = receipt();
    session_alone["durability_reason"] = Value::from("cross_session");
    cases.push(session_alone);

    for value in cases {
        assert!(
            validate_evidence_receipt(&value).is_err(),
            "invalid receipt was accepted: {value}"
        );
    }
}

#[test]
fn context_and_pack_expose_only_the_v09_contracts() {
    let context = json(root().join("src/context.json"));
    assert_eq!(context["schema_version"], 4);
    assert_eq!(context["default"], "direct");
    assert_eq!(
        context["contracts"]
            .as_object()
            .unwrap()
            .keys()
            .collect::<Vec<_>>(),
        ["evidence_receipt", "program_control"]
    );
    for removed in [
        "resolved_mode",
        "project_policy",
        "task_request",
        "resolved_permissions",
        "policy_authorities",
    ] {
        assert!(
            context.get(removed).is_none(),
            "obsolete context key: {removed}"
        );
    }

    assert_eq!(
        directory_files(&root().join("dist/pack/schemas")),
        BTreeSet::from(["evidence-receipt.schema.json".to_owned()])
    );
    assert_eq!(
        directory_files(&root().join("dist/pack/templates")),
        BTreeSet::from([
            "evidence-receipt.json".to_owned(),
            "program-control.md".to_owned(),
        ])
    );
}

#[test]
fn external_pack_verification_detects_changes_and_extra_files() {
    let changed = tempfile::tempdir().unwrap();
    copy_directory(&root().join("dist/pack"), changed.path());
    assert!(verify_pack_directory(changed.path()).is_ok());
    fs::write(changed.path().join("KERNEL.md"), "changed").unwrap();
    assert!(verify_pack_directory(changed.path()).is_err());

    let extra = tempfile::tempdir().unwrap();
    copy_directory(&root().join("dist/pack"), extra.path());
    fs::write(extra.path().join("EXTRA.txt"), "extra").unwrap();
    assert!(verify_pack_directory(extra.path()).is_err());

    let incomplete = tempfile::tempdir().unwrap();
    copy_directory(&root().join("dist/pack"), incomplete.path());
    let manifest_path = incomplete.path().join("MANIFEST.json");
    let mut manifest = json(&manifest_path);
    manifest["files"]
        .as_array_mut()
        .unwrap()
        .retain(|file| file["path"] != "KERNEL.md");
    fs::write(
        &manifest_path,
        format!("{}\n", serde_json::to_string_pretty(&manifest).unwrap()),
    )
    .unwrap();
    fs::remove_file(incomplete.path().join("KERNEL.md")).unwrap();
    assert!(verify_pack_directory(incomplete.path()).is_err());

    let forged_version = tempfile::tempdir().unwrap();
    copy_directory(&root().join("dist/pack"), forged_version.path());
    let manifest_path = forged_version.path().join("MANIFEST.json");
    let mut manifest = json(&manifest_path);
    manifest["version"] = Value::from("0.9.0\nforged");
    fs::write(
        manifest_path,
        format!("{}\n", serde_json::to_string_pretty(&manifest).unwrap()),
    )
    .unwrap();
    assert!(verify_pack_directory(forged_version.path()).is_err());
}

#[test]
fn generated_distribution_is_current_and_has_no_executable_fallback() {
    method_core::dist::check_distribution(&root()).unwrap();
    assert!(!root().join("dist/pack/tools/noel_method.py").exists());
}

#[test]
fn normative_modules_have_stable_structure_and_small_runtime_budgets() {
    let expected = [
        (
            "src/KERNEL.md",
            525,
            vec![
                "# Noel Method Kernel",
                "## Understand",
                "## Act",
                "## Learn efficiently",
                "## Finish",
                "## Secret boundary",
            ],
        ),
        (
            "protocols/program.md",
            625,
            vec![
                "# Program Protocol",
                "## One human control",
                "## Dispatch cohesive outcomes",
                "## Repair without ceremony",
                "## Evidence and completion",
            ],
        ),
        (
            "protocols/experiment.md",
            180,
            vec!["# Experiment Protocol"],
        ),
        (
            "protocols/secrets.md",
            450,
            vec![
                "# Secrets Protocol",
                "## Before access",
                "## Deliver opaquely",
                "## Verify without revealing",
                "## Respond",
            ],
        ),
    ];

    for (relative, maximum_words, expected_headings) in expected {
        let text = fs::read_to_string(root().join(relative)).unwrap();
        let headings = text
            .lines()
            .filter(|line| line.starts_with('#'))
            .collect::<Vec<_>>();
        assert_eq!(
            headings, expected_headings,
            "unexpected headings in {relative}"
        );
        let words = text.split_whitespace().count();
        assert!(
            words <= maximum_words,
            "{relative} is {words} words; maximum is {maximum_words}"
        );
    }
}

#[test]
fn v09_behavior_has_named_scenarios_and_provenance() {
    let scenarios = json(root().join("evals/scenarios.json"));
    let scenario_ids = scenarios
        .as_array()
        .unwrap()
        .iter()
        .map(|scenario| scenario["id"].as_str().unwrap())
        .collect::<BTreeSet<_>>();
    for required in [
        "tentative-assent-bounded",
        "question-does-not-pause-objective",
        "failed-approach-not-blocker",
        "program-host-state-not-control",
        "program-one-canonical-control",
        "expensive-gate-diagnostic-loop",
        "unrelated-failure-plane",
        "missing-observation-not-defect",
        "instrumentation-requires-decision-consumer",
        "safe-invariant-before-perfect-causation",
        "claim-scoped-result",
        "reducer-preserves-terminal-evidence",
        "incidental-prerequisite-return",
        "authoritative-contradiction-resets-model",
    ] {
        assert!(
            scenario_ids.contains(required),
            "missing scenario: {required}"
        );
    }

    let provenance = json(root().join("casebook/rule-provenance.json"));
    let all_eval_ids = collect_eval_ids(&root().join("evals"));
    let v09 = provenance
        .as_array()
        .unwrap()
        .iter()
        .filter(|entry| {
            entry["introduced_in"]
                .as_str()
                .is_some_and(|version| version.starts_with("0.9."))
        })
        .collect::<Vec<_>>();
    assert!(!v09.is_empty(), "v0.9 rules require casebook provenance");
    for entry in v09 {
        for field in ["rule", "observation", "insufficiency"] {
            assert!(
                entry[field]
                    .as_str()
                    .is_some_and(|value| !value.trim().is_empty()),
                "v0.9 provenance is missing {field}: {entry}"
            );
        }
        let eval_ids = entry["eval_ids"].as_array().unwrap();
        assert!(!eval_ids.is_empty(), "v0.9 rule has no eval: {entry}");
        for eval_id in eval_ids {
            let eval_id = eval_id.as_str().unwrap();
            assert!(
                all_eval_ids.contains(eval_id),
                "provenance references unknown eval ID {eval_id}"
            );
        }
    }
}

fn directory_files(path: &Path) -> BTreeSet<String> {
    fs::read_dir(path)
        .unwrap()
        .map(|entry| {
            entry
                .unwrap()
                .file_name()
                .into_string()
                .expect("portable test file name")
        })
        .collect()
}

fn copy_directory(source: &Path, destination: &Path) {
    for entry in fs::read_dir(source).unwrap() {
        let entry = entry.unwrap();
        let target = destination.join(entry.file_name());
        if entry.file_type().unwrap().is_dir() {
            fs::create_dir_all(&target).unwrap();
            copy_directory(&entry.path(), &target);
        } else {
            fs::copy(entry.path(), target).unwrap();
        }
    }
}

fn collect_eval_ids(path: &Path) -> BTreeSet<String> {
    let mut ids = BTreeSet::new();
    collect_eval_ids_from_directory(path, &mut ids);
    ids
}

fn collect_eval_ids_from_directory(path: &Path, ids: &mut BTreeSet<String>) {
    for entry in fs::read_dir(path).unwrap() {
        let entry = entry.unwrap();
        let path = entry.path();
        if path.is_dir() {
            collect_eval_ids_from_directory(&path, ids);
        } else if path.extension().and_then(|value| value.to_str()) == Some("json") {
            if let Ok(value) = parse_json_strict(&fs::read(&path).unwrap()) {
                collect_ids(&value, ids);
            }
        }
    }
}

fn collect_ids(value: &Value, ids: &mut BTreeSet<String>) {
    match value {
        Value::Array(values) => {
            for value in values {
                collect_ids(value, ids);
            }
        }
        Value::Object(values) => {
            if let Some(id) = values.get("id").and_then(Value::as_str) {
                ids.insert(id.to_owned());
            }
            for value in values.values() {
                collect_ids(value, ids);
            }
        }
        _ => {}
    }
}
