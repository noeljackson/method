use method_core::{
    MethodError, ProtocolFlags, parse_json_strict, project_policy_digest, resolve_permissions,
    validate_evidence_receipt, validate_program_control, validate_resolved_permissions,
    verify_pack_directory, verify_project_policy,
};
use serde_json::Value;
use std::fs;
use std::path::{Path, PathBuf};

fn root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
}

fn json(path: impl AsRef<Path>) -> Value {
    parse_json_strict(&fs::read(path).unwrap()).unwrap()
}

#[test]
fn accepted_policy_fixtures_verify_with_expected_digests() {
    let authorities = json(root().join("evals/fixtures/authorities.json"));
    let expected = [
        (
            "software",
            "62ddf64d9672ec54fa8f19f728331879ab0a495666be190c80f22f96909b2be1",
        ),
        (
            "operations",
            "e948cf714bcda60c2ab8ec61bb1fbd790cfce524d670e2e85de4c8a79a59d875",
        ),
        (
            "research",
            "26403ff0db824cd45cc54263245a453fe965c914ed4414142479a2114fa4c97b",
        ),
    ];
    for (name, digest) in expected {
        let policy = json(
            root()
                .join("evals/fixtures/policies")
                .join(format!("{name}.json")),
        );
        assert_eq!(project_policy_digest(&policy).unwrap(), digest);
        let verified = verify_project_policy(&policy, &authorities).unwrap();
        assert_eq!(verified.policy_id, name);
        assert_eq!(verified.policy_sha256, digest);
    }
}

#[test]
fn all_eval_cases_route_to_the_expected_protocols() {
    let authorities = json(root().join("evals/fixtures/authorities.json"));
    let cases = json(root().join("evals/cases.json"));
    for case in cases.as_array().unwrap() {
        let case_id = case["id"].as_str().unwrap();
        let policy_name = case["policy"].as_str().unwrap();
        let task_name = case["task"].as_str().unwrap();
        let policy = json(
            root()
                .join("evals/fixtures/policies")
                .join(format!("{policy_name}.json")),
        );
        let task = json(
            root()
                .join("evals/fixtures/tasks")
                .join(format!("{task_name}.json")),
        );
        let permissions =
            resolve_permissions(&policy, &authorities, &task, None).unwrap_or_else(|error| {
                panic!("{case_id}: {error}");
            });
        let expected = case["expected_protocols"]
            .as_array()
            .unwrap()
            .iter()
            .map(|value| value.as_str().unwrap().to_owned())
            .collect::<Vec<_>>();
        assert_eq!(permissions.protocols, expected, "{case_id}");
    }
}

#[test]
fn resolver_rejects_unknown_actions_and_gates() {
    let authorities = json(root().join("evals/fixtures/authorities.json"));
    let policy = json(root().join("evals/fixtures/policies/software.json"));
    let mut task = json(root().join("evals/fixtures/tasks/direct-bounded-edit.json"));
    task["requested_actions"]
        .as_array_mut()
        .unwrap()
        .push(Value::String("deployment.mutate".to_owned()));
    assert!(matches!(
        resolve_permissions(&policy, &authorities, &task, None),
        Err(MethodError::Data(message)) if message.contains("not allowed")
    ));

    let mut task = json(root().join("evals/fixtures/tasks/direct-bounded-edit.json"));
    task["required_gates"]
        .as_array_mut()
        .unwrap()
        .push(Value::String("imaginary-gate".to_owned()));
    assert!(matches!(
        resolve_permissions(&policy, &authorities, &task, None),
        Err(MethodError::Data(message)) if message.contains("unknown gates")
    ));
}

#[test]
fn model_flags_only_add_protocols() {
    let authorities = json(root().join("evals/fixtures/authorities.json"));
    let policy = json(root().join("evals/fixtures/policies/software.json"));
    let task = json(root().join("evals/fixtures/tasks/direct-bounded-edit.json"));
    let permissions = resolve_permissions(
        &policy,
        &authorities,
        &task,
        Some(ProtocolFlags {
            secrets: true,
            ..ProtocolFlags::default()
        }),
    )
    .unwrap();
    assert_eq!(permissions.protocols, ["secrets"]);
}

#[test]
fn resolved_controls_match_selected_protocols() {
    let authorities = json(root().join("evals/fixtures/authorities.json"));
    let policy = json(root().join("evals/fixtures/policies/software.json"));
    let task = json(root().join("evals/fixtures/tasks/secrets-latent-helper.json"));
    let permissions = resolve_permissions(&policy, &authorities, &task, None).unwrap();
    let mut value = serde_json::to_value(permissions).unwrap();
    assert!(validate_resolved_permissions(&value).is_ok());

    value["controls"].as_object_mut().unwrap().remove("secrets");
    assert!(validate_resolved_permissions(&value).is_err());
}

#[test]
fn program_terminal_and_evidence_contracts_are_enforced() {
    let mut control = json(root().join("templates/program-control.json"));
    control["state"] = Value::String("COMPLETE".to_owned());
    control["active_coordinates"] = Value::Array(Vec::new());
    control["authorized_queue"] = Value::Array(Vec::new());
    assert!(validate_program_control(&control).is_ok());
    control["authorized_queue"] = Value::Array(vec![Value::String("late work".to_owned())]);
    assert!(validate_program_control(&control).is_err());

    let receipt = json(root().join("templates/evidence-receipt.json"));
    assert!(validate_evidence_receipt(&receipt).is_ok());
}

#[test]
fn program_hard_gates_name_what_they_block() {
    let mut control = json(root().join("templates/program-control.json"));
    control["state"] = Value::String("ACTIVE".to_owned());
    control["active_coordinates"] = serde_json::json!(["Program / Wave 1 / Workstream / WI-1"]);
    control["hard_gates"] = serde_json::json!([{
        "id": "candidate-acceptance",
        "blocks": ["accept candidate"],
        "state": "UNSATISFIED",
        "evidence_receipt": null
    }]);
    control["reconciliation_receipt"] = serde_json::json!({"state": "current"});
    assert!(validate_program_control(&control).is_ok());

    control["hard_gates"][0]["blocks"] = serde_json::json!([]);
    let error = validate_program_control(&control).unwrap_err();
    assert!(
        error
            .to_string()
            .contains("ProgramControl.hard_gates.blocks")
    );
}

#[test]
fn external_pack_verification_detects_changes_and_extras() {
    let temp = tempfile::tempdir().unwrap();
    copy_directory(&root().join("dist/pack"), temp.path());
    assert!(verify_pack_directory(temp.path()).is_ok());

    fs::write(temp.path().join("KERNEL.md"), "changed").unwrap();
    assert!(verify_pack_directory(temp.path()).is_err());

    copy_directory(&root().join("dist/pack"), temp.path());
    fs::write(temp.path().join("EXTRA.txt"), "extra").unwrap();
    assert!(verify_pack_directory(temp.path()).is_err());
}

#[test]
fn generated_distribution_is_current_and_contains_no_executable_fallback() {
    method_core::dist::check_distribution(&root()).unwrap();
    assert!(!root().join("dist/pack/tools/noel_method.py").exists());
}

#[test]
fn program_protocol_distinguishes_bounded_repair_from_replan() {
    let protocol = fs::read_to_string(root().join("protocols/program.md")).unwrap();
    for required in [
        "smallest readiness pass",
        "same prerequisites and\nrecovery boundary",
        "only that action's prerequisite gates",
        "Keep the ProgramControl `ACTIVE`",
        "materially invalidates the\nlive ProgramControl",
    ] {
        assert!(
            protocol.contains(required),
            "program protocol is missing decision rule: {required}"
        );
    }

    let scenarios = json(root().join("evals/scenarios.json"));
    let ids = scenarios
        .as_array()
        .unwrap()
        .iter()
        .filter_map(|scenario| scenario["id"].as_str())
        .collect::<Vec<_>>();
    for required in [
        "program-bounded-coordinate-repair",
        "program-independent-coordinate",
        "finding-changes-contract",
    ] {
        assert!(ids.contains(&required), "missing scenario: {required}");
    }
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
