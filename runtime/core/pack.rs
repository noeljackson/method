use crate::{MethodError, Result, parse_json_strict, sha256_hex};
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet};
use std::fs;
use std::path::{Component, Path};

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct PackManifest {
    pub method: String,
    pub version: String,
    pub entrypoint: String,
    pub kernel: String,
    pub protocols: Vec<String>,
    pub files: Vec<PackFile>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct PackFile {
    pub path: String,
    pub sha256: String,
}

#[derive(Clone, Debug, Serialize)]
pub struct PackReport {
    pub method: String,
    pub version: String,
    pub manifest_sha256: String,
    pub file_count: usize,
    pub verified: bool,
}

pub fn verify_pack_directory(path: &Path) -> Result<PackReport> {
    let metadata = fs::symlink_metadata(path)?;
    if metadata.file_type().is_symlink() || !metadata.is_dir() {
        return Err(MethodError::Data(format!(
            "pack path is not a regular directory: {}",
            path.display()
        )));
    }
    let mut files = BTreeMap::new();
    collect_files(path, path, &mut files)?;
    verify_pack_files(&files)
}

pub fn verify_pack_files(files: &BTreeMap<String, Vec<u8>>) -> Result<PackReport> {
    let manifest_bytes = files
        .get("MANIFEST.json")
        .ok_or_else(|| MethodError::Data("pack is missing MANIFEST.json".to_owned()))?;
    let value = parse_json_strict(manifest_bytes)?;
    let manifest: PackManifest = serde_json::from_value(value)
        .map_err(|error| MethodError::Data(format!("MANIFEST.json: {error}")))?;
    validate_manifest(&manifest)?;

    let mut expected = BTreeSet::from(["MANIFEST.json".to_owned()]);
    for file in &manifest.files {
        if !expected.insert(file.path.clone()) {
            return Err(MethodError::Data(format!(
                "MANIFEST.json contains duplicate path: {}",
                file.path
            )));
        }
        let bytes = files.get(&file.path).ok_or_else(|| {
            MethodError::Data(format!("pack is missing manifest file: {}", file.path))
        })?;
        let actual = sha256_hex(bytes);
        if actual != file.sha256 {
            return Err(MethodError::Data(format!(
                "pack digest mismatch for {}",
                file.path
            )));
        }
    }
    let actual = files.keys().cloned().collect::<BTreeSet<_>>();
    if actual != expected {
        let extras = actual.difference(&expected).cloned().collect::<Vec<_>>();
        let missing = expected.difference(&actual).cloned().collect::<Vec<_>>();
        return Err(MethodError::Data(format!(
            "pack file set differs from manifest; extra=[{}] missing=[{}]",
            extras.join(", "),
            missing.join(", ")
        )));
    }

    Ok(PackReport {
        method: manifest.method,
        version: manifest.version,
        manifest_sha256: sha256_hex(manifest_bytes),
        file_count: manifest.files.len(),
        verified: true,
    })
}

fn validate_manifest(manifest: &PackManifest) -> Result<()> {
    if manifest.method != "Noel Method" {
        return Err(MethodError::Data(
            "MANIFEST.json method must be Noel Method".to_owned(),
        ));
    }
    nonempty(&manifest.version, "MANIFEST.json version")?;
    safe_relative_path(&manifest.entrypoint)?;
    safe_relative_path(&manifest.kernel)?;
    if manifest.entrypoint != "INDEX.md" || manifest.kernel != "KERNEL.md" {
        return Err(MethodError::Data(
            "MANIFEST.json entrypoint or kernel is invalid".to_owned(),
        ));
    }
    if manifest.protocols != ["program", "experiment", "secrets"] {
        return Err(MethodError::Data(
            "MANIFEST.json protocols must be program, experiment, secrets".to_owned(),
        ));
    }
    if manifest.files.is_empty() {
        return Err(MethodError::Data(
            "MANIFEST.json files must not be empty".to_owned(),
        ));
    }
    for file in &manifest.files {
        safe_relative_path(&file.path)?;
        if file.path == "MANIFEST.json" {
            return Err(MethodError::Data(
                "MANIFEST.json must not list itself".to_owned(),
            ));
        }
        if file.sha256.len() != 64
            || !file
                .sha256
                .chars()
                .all(|value| value.is_ascii_digit() || ('a'..='f').contains(&value))
        {
            return Err(MethodError::Data(format!(
                "invalid manifest SHA-256 for {}",
                file.path
            )));
        }
    }
    Ok(())
}

fn collect_files(
    root: &Path,
    directory: &Path,
    files: &mut BTreeMap<String, Vec<u8>>,
) -> Result<()> {
    let mut entries = fs::read_dir(directory)?.collect::<std::io::Result<Vec<_>>>()?;
    entries.sort_by_key(std::fs::DirEntry::path);
    for entry in entries {
        let path = entry.path();
        let metadata = fs::symlink_metadata(&path)?;
        if metadata.file_type().is_symlink() {
            return Err(MethodError::Data(format!(
                "pack may not contain symlinks: {}",
                path.display()
            )));
        }
        if metadata.is_dir() {
            collect_files(root, &path, files)?;
        } else if metadata.is_file() {
            let relative = path
                .strip_prefix(root)
                .expect("collected path is under pack root");
            let key = relative
                .components()
                .map(|component| component.as_os_str().to_string_lossy())
                .collect::<Vec<_>>()
                .join("/");
            safe_relative_path(&key)?;
            files.insert(key, fs::read(path)?);
        } else {
            return Err(MethodError::Data(format!(
                "pack contains a non-regular file: {}",
                path.display()
            )));
        }
    }
    Ok(())
}

fn safe_relative_path(value: &str) -> Result<()> {
    if value.is_empty() || value.contains('\\') {
        return Err(MethodError::Data(format!("unsafe pack path: {value}")));
    }
    let path = Path::new(value);
    if path.is_absolute()
        || path
            .components()
            .any(|component| !matches!(component, Component::Normal(_)))
    {
        return Err(MethodError::Data(format!("unsafe pack path: {value}")));
    }
    Ok(())
}

fn nonempty(value: &str, label: &str) -> Result<()> {
    if value.trim().is_empty() {
        return Err(MethodError::Data(format!(
            "{label}: must be non-empty text"
        )));
    }
    Ok(())
}
