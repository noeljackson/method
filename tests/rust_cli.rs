use serde_json::Value;
use std::io::Write;
use std::path::PathBuf;
use std::process::{Command, Stdio};

fn binary() -> &'static str {
    env!("CARGO_BIN_EXE_method")
}

fn root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
}

#[test]
fn version_and_pack_commands_report_verified_embedded_identity() {
    let version = Command::new(binary())
        .args(["version", "--json"])
        .output()
        .unwrap();
    assert!(version.status.success());
    let version: Value = serde_json::from_slice(&version.stdout).unwrap();
    assert_eq!(version["cli"], "method");
    assert_eq!(version["cli_version"], "0.8.0");
    assert_eq!(version["method_version"], "0.8.0");
    assert_eq!(version["pack_manifest_sha256"].as_str().unwrap().len(), 64);

    let pack = Command::new(binary())
        .args(["pack", "verify", "--json"])
        .output()
        .unwrap();
    assert!(pack.status.success());
    let pack: Value = serde_json::from_slice(&pack.stdout).unwrap();
    assert_eq!(pack["verified"], true);
    assert_eq!(pack["manifest_sha256"], version["pack_manifest_sha256"]);
    assert_eq!(pack["trust_anchor_matched"], Value::Null);

    let mismatch = Command::new(binary())
        .args([
            "pack",
            "verify",
            "--expect-manifest-sha256",
            &"0".repeat(64),
        ])
        .output()
        .unwrap();
    assert_eq!(mismatch.status.code(), Some(2));
}

#[test]
fn context_returns_kernel_then_selected_protocols() {
    let output = Command::new(binary())
        .args(["context", "--program", "--secrets", "--format", "json"])
        .output()
        .unwrap();
    assert!(output.status.success());
    let value: Value = serde_json::from_slice(&output.stdout).unwrap();
    assert_eq!(
        value["selected_protocols"],
        serde_json::json!(["program", "secrets"])
    );
    let paths = value["modules"]
        .as_array()
        .unwrap()
        .iter()
        .map(|module| module["path"].as_str().unwrap())
        .collect::<Vec<_>>();
    assert_eq!(
        paths,
        ["KERNEL.md", "protocols/program.md", "protocols/secrets.md"]
    );
}

#[test]
fn context_accepts_resolved_permissions_and_checks_task_identity() {
    let output = Command::new(binary())
        .args([
            "resolve",
            "--policy",
            "evals/fixtures/policies/software.json",
            "--authorities",
            "evals/fixtures/authorities.json",
            "--task",
            "evals/fixtures/tasks/direct-bounded-edit.json",
        ])
        .current_dir(root())
        .output()
        .unwrap();
    assert!(output.status.success());
    let temp = tempfile::NamedTempFile::new().unwrap();
    std::fs::write(temp.path(), &output.stdout).unwrap();

    let context = Command::new(binary())
        .args([
            "context",
            "--permissions",
            temp.path().to_str().unwrap(),
            "--format",
            "json",
        ])
        .output()
        .unwrap();
    assert!(context.status.success());
    let context: Value = serde_json::from_slice(&context.stdout).unwrap();
    assert_eq!(context["selected_protocols"], serde_json::json!([]));

    let mismatch = Command::new(binary())
        .args([
            "context",
            "--task",
            "evals/fixtures/tasks/core-evidence-identity.json",
            "--permissions",
            temp.path().to_str().unwrap(),
        ])
        .current_dir(root())
        .output()
        .unwrap();
    assert_eq!(mismatch.status.code(), Some(2));
}

#[test]
fn validator_accepts_stdin_and_rejects_invalid_input_with_exit_two() {
    let task = std::fs::read(root().join("evals/fixtures/tasks/direct-bounded-edit.json")).unwrap();
    let mut child = Command::new(binary())
        .args(["validate", "task-request", "-", "--json"])
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()
        .unwrap();
    child.stdin.take().unwrap().write_all(&task).unwrap();
    let output = child.wait_with_output().unwrap();
    assert!(output.status.success());
    let value: Value = serde_json::from_slice(&output.stdout).unwrap();
    assert_eq!(value["schema_valid"], true);
    assert_eq!(value["authority_verified"], false);

    let mut child = Command::new(binary())
        .args(["validate", "task-request", "-"])
        .stdin(Stdio::piped())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .unwrap();
    child
        .stdin
        .take()
        .unwrap()
        .write_all(br#"{"schema_version":1}"#)
        .unwrap();
    let status = child.wait().unwrap();
    assert_eq!(status.code(), Some(2));
}
