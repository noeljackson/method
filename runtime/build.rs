use std::env;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

fn main() {
    let root = PathBuf::from(env::var_os("CARGO_MANIFEST_DIR").expect("manifest directory"));
    let package_version = env::var("CARGO_PKG_VERSION").expect("package version");
    let method_version = fs::read_to_string(root.join("VERSION"))
        .expect("read VERSION")
        .trim()
        .to_owned();
    assert_eq!(
        package_version, method_version,
        "Cargo package version must match VERSION"
    );

    let manifest_path = root.join("dist/pack/MANIFEST.json");
    let manifest: serde_json::Value =
        serde_json::from_slice(&fs::read(&manifest_path).expect("read generated pack manifest"))
            .expect("parse generated pack manifest");
    assert_eq!(
        manifest.get("version").and_then(serde_json::Value::as_str),
        Some(method_version.as_str()),
        "generated pack version must match VERSION"
    );

    println!("cargo:rerun-if-changed={}", root.join("VERSION").display());
    emit_pack_reruns(&root.join("dist/pack"));

    let commit = Command::new("git")
        .args(["rev-parse", "HEAD"])
        .current_dir(&root)
        .output()
        .ok()
        .filter(|output| output.status.success())
        .and_then(|output| String::from_utf8(output.stdout).ok())
        .map(|value| value.trim().to_owned())
        .unwrap_or_else(|| "unknown".to_owned());
    println!("cargo:rustc-env=METHOD_BUILD_COMMIT={commit}");
}

fn emit_pack_reruns(path: &Path) {
    let mut entries = fs::read_dir(path)
        .expect("read generated pack directory")
        .collect::<Result<Vec<_>, _>>()
        .expect("read generated pack entries");
    entries.sort_by_key(|entry| entry.path());
    for entry in entries {
        let path = entry.path();
        if path.is_dir() {
            emit_pack_reruns(&path);
        } else {
            println!("cargo:rerun-if-changed={}", path.display());
        }
    }
}
