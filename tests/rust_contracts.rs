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
            "43a73a78ca313b879fa8e7e6695558023b79860c18723aa542ca3639ea650cd6",
        ),
        (
            "operations",
            "379501e469dfeac2ec4833ad829bcc9506394e29d4a2c33f22c462b498b2afed",
        ),
        (
            "research",
            "9dc7bdf41f6195f5f26b85699657d9a306317f28daf173395905a2ed2c8a89de",
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
    let normalized_protocol = protocol.split_whitespace().collect::<Vec<_>>().join(" ");
    for required in [
        "smallest readiness pass",
        "one mutation claim",
        "read-only preparation",
        "provisional",
        "Every work item advances a named goal condition",
        "Otherwise omit it",
        "Observe passive gates by transition",
        "end the current observation iteration without terminating",
        "Keep the control `ACTIVE`",
        "Set `STOPPED_FOR_REPLAN` only",
    ] {
        assert!(
            normalized_protocol.contains(required),
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
        "program-concurrent-read-only-support",
        "program-provisional-successor-readiness",
        "program-stale-control-projection",
        "program-ceremony-without-consumer",
        "program-passive-gate-unchanged",
        "program-passive-gate-only-remaining",
        "program-passive-gate-failure",
        "direct-passive-gate-transition",
        "program-bind-once-claim",
        "program-material-transition-reconciliation",
        "program-archived-control-opt-in",
        "program-logical-concerns-one-artifact",
        "automatic-consequence-authority",
        "verification-only-transient-retry",
        "side-effecting-workflow-retry",
        "unclassified-external-failure",
        "failure-layer-before-retry",
        "program-diagnostic-gap-same-claim",
        "recurring-failure-concrete-consumer",
        "one-off-finding-no-guard",
        "program-host-state-not-control",
        "program-diagnosed-repair-continuation",
        "program-terminal-handoff-evidence",
        "program-unknown-bounded-discriminator",
        "program-coordinator-identity",
        "incidental-prerequisite-return",
        "expensive-gate-diagnostic-loop",
        "diagnostic-infrastructure-current-consumer",
        "reducer-preserves-terminal-evidence",
        "finding-changes-contract",
    ] {
        assert!(ids.contains(&required), "missing scenario: {required}");
    }
}

#[test]
fn runtime_text_keeps_v08_semantics_concise() {
    let kernel = fs::read_to_string(root().join("src/KERNEL.md")).unwrap();
    let program = fs::read_to_string(root().join("protocols/program.md")).unwrap();
    let normalized_kernel = kernel.split_whitespace().collect::<Vec<_>>().join(" ");
    let normalized_program = program.split_whitespace().collect::<Vec<_>>().join(" ");
    for required in [
        "automatic consequence only when canonical policy already declares it",
        "Retrying unchanged verification-only work under a canonical transient policy inherits that action",
        "publication, deployment, release, recovery, live mutation, or direct credential handling is separate",
        "Load archived or superseded material only when it bears on a current claim",
        "Report material transitions and decisions; omit unchanged state",
        "Bind a passive gate once to its exact artifact and revision",
        "Use transition-aware observation when early failure or the terminal result matters",
        "Unchanged state creates no work or report",
        "failure, inconsistency, empty output, or credible stall",
        "Keep incidental prerequisites subordinate",
        "localize the failing layer",
        "Expensive clean-room, end-to-end, or destructive gates qualify credible candidates",
        "predicts a discriminating result",
        "An unknown result freezes that action, not read-only diagnosis; run one bounded discriminator",
        "Turn credible recurring failures with a concrete consumer into the smallest in-scope guard",
        "verify outcomes without competing definitions",
    ] {
        assert!(
            normalized_kernel.contains(required),
            "kernel is missing rule: {required}"
        );
    }
    for required in [
        "they may share one control or artifact",
        "Bind each mutation claim once",
        "Routine actions against the same claim and unchanged admission inherit",
        "Apply the Kernel's passive-gate rule",
        "repair, rebase, retry, and verify under the same claim and admission",
        "An unknown result freezes the affected mutation, not read-only diagnosis",
        "cannot turn already-authorized or read-only work into missing authority",
        "Undesignated host goals, timers, and session state may schedule work",
        "A named coordinator must be unambiguous",
        "preserve a terminal external outcome for handoff",
        "proceed directly to one cohesive repair",
    ] {
        assert!(
            normalized_program.contains(required),
            "program is missing rule: {required}"
        );
    }
    assert!(kernel.split_whitespace().count() <= 650);
    assert!(program.split_whitespace().count() <= 800);
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
