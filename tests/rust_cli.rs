use serde_json::Value;
use std::io::Write;
use std::path::PathBuf;
use std::process::{Command, Output, Stdio};

fn binary() -> &'static str {
    env!("CARGO_BIN_EXE_method")
}

fn root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
}

fn run(args: &[&str]) -> Output {
    Command::new(binary())
        .args(args)
        .current_dir(root())
        .output()
        .unwrap()
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
    serde_json::json!({
        "schema_version": 2,
        "durability_reason": "ephemeral",
        "subject_identity": "tree:0123456789abcdef",
        "environment_identity": "fixture:qemu-single-node-v1",
        "procedure": "run the bounded fixture once",
        "claims": [
            {
                "id": "boot.ready",
                "outcome": "SUPPORTED",
                "observation": "the exact-tree readiness probe passed"
            },
            {
                "id": "runtime.mount",
                "outcome": "INCONCLUSIVE",
                "observation": "the probe produced no terminal mount event"
            }
        ],
        "evidence_ref": "artifact:fixture-run-17",
        "captured_at": "2026-08-12T12:00:00Z",
        "limitations": ["no live environment was mutated"],
        "source_disposition": "not_sensitive"
    })
}

#[test]
fn version_and_pack_commands_report_the_same_verified_identity() {
    let version = run(&["version", "--json"]);
    assert!(version.status.success());
    let version: Value = serde_json::from_slice(&version.stdout).unwrap();
    assert_eq!(version["cli"], "method");
    assert_eq!(version["cli_version"], env!("CARGO_PKG_VERSION"));
    assert_eq!(version["method_version"], env!("CARGO_PKG_VERSION"));
    assert_eq!(version["pack_manifest_sha256"].as_str().unwrap().len(), 64);

    let pack = run(&["pack", "verify", "--json"]);
    assert!(pack.status.success());
    let pack: Value = serde_json::from_slice(&pack.stdout).unwrap();
    assert_eq!(pack["verified"], true);
    assert_eq!(pack["version"], version["method_version"]);
    assert_eq!(pack["manifest_sha256"], version["pack_manifest_sha256"]);
    assert_eq!(pack["trust_anchor_matched"], Value::Null);

    let mismatch = run(&[
        "pack",
        "verify",
        "--expect-manifest-sha256",
        &"0".repeat(64),
    ]);
    assert_eq!(mismatch.status.code(), Some(2));
}

#[test]
fn context_v4_returns_kernel_then_only_explicit_protocols() {
    let direct = run(&["context", "--format", "json"]);
    assert!(direct.status.success());
    let direct: Value = serde_json::from_slice(&direct.stdout).unwrap();
    assert_eq!(direct["schema_version"], 4);
    assert_eq!(direct["selected_protocols"], serde_json::json!([]));
    assert_eq!(direct["modules"].as_array().unwrap().len(), 1);
    assert_eq!(direct["modules"][0]["path"], "KERNEL.md");

    let selected = run(&[
        "context",
        "--program",
        "--experiment",
        "--secrets",
        "--format",
        "json",
    ]);
    assert!(selected.status.success());
    let selected: Value = serde_json::from_slice(&selected.stdout).unwrap();
    assert_eq!(
        selected["selected_protocols"],
        serde_json::json!(["program", "experiment", "secrets"])
    );
    let paths = selected["modules"]
        .as_array()
        .unwrap()
        .iter()
        .map(|module| module["path"].as_str().unwrap())
        .collect::<Vec<_>>();
    assert_eq!(
        paths,
        [
            "KERNEL.md",
            "protocols/program.md",
            "protocols/experiment.md",
            "protocols/secrets.md",
        ]
    );

    let markdown = run(&["context", "--program"]);
    assert!(markdown.status.success());
    let markdown = String::from_utf8(markdown.stdout).unwrap();
    assert!(markdown.contains("# Noel Method Kernel"));
    assert!(markdown.contains("# Program Protocol"));
    assert!(!markdown.contains("# Experiment Protocol"));
}

#[test]
fn removed_resolver_and_generic_contract_interfaces_fail_as_usage_errors() {
    for args in [
        vec!["resolve"],
        vec!["policy", "verify"],
        vec!["validate", "task-request", "-"],
        vec!["context", "--task", "task.json"],
        vec!["context", "--permissions", "permissions.json"],
    ] {
        let output = run(&args);
        assert_eq!(
            output.status.code(),
            Some(2),
            "removed interface unexpectedly accepted: {args:?}\nstdout: {}\nstderr: {}",
            String::from_utf8_lossy(&output.stdout),
            String::from_utf8_lossy(&output.stderr)
        );
    }
}

#[test]
fn program_validate_supports_stdin_json_and_previous_revision() {
    let current = program(2, "ACTIVE", "Open the exact-head pull request.", None);
    let previous = tempfile::NamedTempFile::new().unwrap();
    std::fs::write(
        previous.path(),
        program(1, "ACTIVE", "Implement the bounded change.", None),
    )
    .unwrap();

    let mut child = Command::new(binary())
        .args([
            "program",
            "validate",
            "-",
            "--previous",
            previous.path().to_str().unwrap(),
            "--json",
        ])
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()
        .unwrap();
    child
        .stdin
        .take()
        .unwrap()
        .write_all(current.as_bytes())
        .unwrap();
    let output = child.wait_with_output().unwrap();
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    let value: Value = serde_json::from_slice(&output.stdout).unwrap();
    assert_eq!(value["kind"], "program-control");
    assert_eq!(value["valid"], true);
    assert_eq!(value["metadata"]["control_revision"], 2);
    assert_eq!(value["metadata"]["state"], "ACTIVE");
    assert_eq!(value["transition_checked"], true);
    assert_eq!(value["warnings"], serde_json::json!([]));
}

#[test]
fn program_validate_rejects_bad_documents_transitions_and_double_stdin() {
    let invalid = tempfile::NamedTempFile::new().unwrap();
    std::fs::write(
        invalid.path(),
        program(1, "COMPLETE", "There is still work.", None),
    )
    .unwrap();
    let output = run(&["program", "validate", invalid.path().to_str().unwrap()]);
    assert_eq!(output.status.code(), Some(2));

    let previous = tempfile::NamedTempFile::new().unwrap();
    let skipped = tempfile::NamedTempFile::new().unwrap();
    std::fs::write(previous.path(), program(2, "ACTIVE", "Continue.", None)).unwrap();
    std::fs::write(skipped.path(), program(4, "COMPLETE", "None", None)).unwrap();
    let output = run(&[
        "program",
        "validate",
        skipped.path().to_str().unwrap(),
        "--previous",
        previous.path().to_str().unwrap(),
    ]);
    assert_eq!(output.status.code(), Some(2));

    let output = run(&["program", "validate", "-", "--previous", "-"]);
    assert_eq!(output.status.code(), Some(2));
}

#[test]
fn receipt_validate_supports_stdin_and_reports_claim_count() {
    let bytes = serde_json::to_vec(&receipt()).unwrap();
    let mut child = Command::new(binary())
        .args(["receipt", "validate", "-", "--json"])
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()
        .unwrap();
    child.stdin.take().unwrap().write_all(&bytes).unwrap();
    let output = child.wait_with_output().unwrap();
    assert!(output.status.success());
    let value: Value = serde_json::from_slice(&output.stdout).unwrap();
    assert_eq!(value["kind"], "evidence-receipt");
    assert_eq!(value["valid"], true);
    assert_eq!(value["schema_version"], 2);
    assert_eq!(value["claim_count"], 2);

    let mut old_receipt = receipt();
    old_receipt["schema_version"] = Value::from(1);
    let old_file = tempfile::NamedTempFile::new().unwrap();
    std::fs::write(old_file.path(), serde_json::to_vec(&old_receipt).unwrap()).unwrap();
    let output = run(&["receipt", "validate", old_file.path().to_str().unwrap()]);
    assert_eq!(output.status.code(), Some(2));
}

#[test]
fn missing_input_is_an_io_error() {
    let output = run(&[
        "program",
        "validate",
        "tests/this-program-control-does-not-exist.md",
    ]);
    assert_eq!(output.status.code(), Some(1));
}

#[test]
fn dist_build_and_check_operate_on_an_explicit_root() {
    let temp = tempfile::tempdir().unwrap();
    std::fs::copy(root().join("VERSION"), temp.path().join("VERSION")).unwrap();
    for directory in ["src", "protocols", "schemas", "templates"] {
        copy_directory(&root().join(directory), &temp.path().join(directory));
    }

    let build = Command::new(binary())
        .args(["dist", "build", "--root", temp.path().to_str().unwrap()])
        .output()
        .unwrap();
    assert!(
        build.status.success(),
        "{}",
        String::from_utf8_lossy(&build.stderr)
    );
    assert!(temp.path().join("dist/pack/MANIFEST.json").is_file());

    let check = Command::new(binary())
        .args(["dist", "check", "--root", temp.path().to_str().unwrap()])
        .output()
        .unwrap();
    assert!(
        check.status.success(),
        "{}",
        String::from_utf8_lossy(&check.stderr)
    );
}

#[cfg(unix)]
#[test]
fn dist_build_rejects_output_symlinks_without_touching_the_target() {
    use std::os::unix::fs::symlink;

    let temp = tempfile::tempdir().unwrap();
    std::fs::copy(root().join("VERSION"), temp.path().join("VERSION")).unwrap();
    for directory in ["src", "protocols", "schemas", "templates"] {
        copy_directory(&root().join(directory), &temp.path().join(directory));
    }
    let outside = tempfile::tempdir().unwrap();
    let sentinel = outside.path().join("program.md");
    std::fs::write(&sentinel, "do not overwrite").unwrap();
    std::fs::create_dir_all(temp.path().join("dist/pack")).unwrap();
    symlink(outside.path(), temp.path().join("dist/pack/protocols")).unwrap();

    let build = Command::new(binary())
        .args(["dist", "build", "--root", temp.path().to_str().unwrap()])
        .output()
        .unwrap();
    assert_eq!(build.status.code(), Some(2));
    assert_eq!(
        std::fs::read_to_string(sentinel).unwrap(),
        "do not overwrite"
    );
}

fn copy_directory(source: &std::path::Path, destination: &std::path::Path) {
    std::fs::create_dir_all(destination).unwrap();
    for entry in std::fs::read_dir(source).unwrap() {
        let entry = entry.unwrap();
        let target = destination.join(entry.file_name());
        if entry.file_type().unwrap().is_dir() {
            copy_directory(&entry.path(), &target);
        } else {
            std::fs::copy(entry.path(), target).unwrap();
        }
    }
}
