use crate::{MethodError, Result, parse_json_strict, sha256_hex};
use serde_json::{Value, json};
use std::collections::{BTreeMap, BTreeSet};
use std::fs;
use std::path::{Path, PathBuf};

const PROTOCOLS: [&str; 3] = ["program", "experiment", "secrets"];
const SCHEMAS: [&str; 1] = ["evidence-receipt.schema.json"];
const TEMPLATES: [&str; 2] = ["program-control.md", "evidence-receipt.json"];

pub fn default_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
}

pub fn build_distribution(root: &Path) -> Result<Vec<PathBuf>> {
    let rendered = render_all(root)?;
    let pack = root.join("dist/pack");
    for relative in rendered.keys() {
        validate_output_path(root, &root.join(relative))?;
    }
    let _ = collect_relative_files(&pack)?;
    let mut written = Vec::new();
    for (relative, content) in &rendered {
        let path = root.join(relative);
        prepare_output_path(root, &path)?;
        fs::write(&path, content)?;
        written.push(path);
    }
    let expected = rendered
        .keys()
        .filter_map(|path| path.strip_prefix("dist/pack/").ok())
        .map(PathBuf::from)
        .collect::<BTreeSet<_>>();
    if pack.exists() {
        remove_stale_pack_files(&pack, &expected)?;
    }
    Ok(written)
}

pub fn check_distribution(root: &Path) -> Result<()> {
    let rendered = render_all(root)?;
    for relative in rendered.keys() {
        validate_output_path(root, &root.join(relative))?;
    }
    let mut differences = Vec::new();
    for (relative, expected) in &rendered {
        let path = root.join(relative);
        let actual = match fs::read_to_string(&path) {
            Ok(actual) => actual,
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => {
                differences.push(relative.display().to_string());
                continue;
            }
            Err(error) => return Err(error.into()),
        };
        if actual != *expected {
            differences.push(relative.display().to_string());
        }
    }
    let pack = root.join("dist/pack");
    let expected = rendered
        .keys()
        .filter_map(|path| path.strip_prefix("dist/pack/").ok())
        .map(PathBuf::from)
        .collect::<BTreeSet<_>>();
    let actual = collect_relative_files(&pack)?;
    if actual != expected {
        differences.push("dist/pack file inventory".to_owned());
    }
    if differences.is_empty() {
        Ok(())
    } else {
        Err(MethodError::Data(format!(
            "generated distribution drift: {}",
            differences.join(", ")
        )))
    }
}

fn render_all(root: &Path) -> Result<BTreeMap<PathBuf, String>> {
    let version = read_trimmed(root, "VERSION")?;
    let context = read_json(root.join("src/context.json"))?;
    let kernel = read_trimmed(root, "src/KERNEL.md")?;
    let protocol_text = PROTOCOLS
        .iter()
        .map(|name| Ok((*name, read_trimmed(root, &format!("protocols/{name}.md"))?)))
        .collect::<Result<BTreeMap<_, _>>>()?;
    let mut output = BTreeMap::new();
    output.insert(
        PathBuf::from("dist/MONOLITH.md"),
        format!(
            "{}\n{}\n",
            header(&version),
            join_modules(&kernel, &protocol_text)
        ),
    );
    output.insert(
        PathBuf::from("dist/pack/INDEX.md"),
        render_index(&version, &context)?,
    );
    output.insert(
        PathBuf::from("dist/pack/CONTEXT.json"),
        format!("{}\n", serde_json::to_string_pretty(&context)?),
    );
    output.insert(
        PathBuf::from("dist/pack/KERNEL.md"),
        modular_document(&version, &kernel, ""),
    );
    for protocol in PROTOCOLS {
        output.insert(
            PathBuf::from(format!("dist/pack/protocols/{protocol}.md")),
            modular_document(&version, &protocol_text[protocol], "../"),
        );
    }
    for schema in SCHEMAS {
        output.insert(
            PathBuf::from(format!("dist/pack/schemas/{schema}")),
            fs::read_to_string(root.join("schemas").join(schema))?,
        );
    }
    for template in TEMPLATES {
        output.insert(
            PathBuf::from(format!("dist/pack/templates/{template}")),
            fs::read_to_string(root.join("templates").join(template))?,
        );
    }
    let files = output
        .iter()
        .filter_map(|(path, content)| {
            path.strip_prefix("dist/pack/").ok().map(|relative| {
                json!({"path": relative.to_string_lossy(), "sha256": sha256_hex(content.as_bytes())})
            })
        })
        .collect::<Vec<_>>();
    output.insert(
        PathBuf::from("dist/pack/MANIFEST.json"),
        format!(
            "{}\n",
            serde_json::to_string_pretty(&json!({
                "method": "Noel Method",
                "version": version,
                "entrypoint": "INDEX.md",
                "kernel": "KERNEL.md",
                "protocols": PROTOCOLS,
                "files": files,
            }))?
        ),
    );
    Ok(output)
}

fn render_index(version: &str, context: &Value) -> Result<String> {
    let protocols = context
        .get("protocols")
        .and_then(Value::as_object)
        .ok_or_else(|| MethodError::Data("src/context.json protocols are invalid".to_owned()))?;
    let signal = |name: &str| -> Result<&str> {
        protocols
            .get(name)
            .and_then(|value| value.get("task_signal"))
            .and_then(Value::as_str)
            .ok_or_else(|| MethodError::Data(format!("src/context.json {name} signal is invalid")))
    };
    let generated_header = header(version);
    let program = signal("program")?;
    let experiment = signal("experiment")?;
    let secrets = signal("secrets")?;
    Ok(format!(
        r#"{generated_header}
# Noel Method Runtime Pack

Version: `{version}`

Load [Kernel](KERNEL.md). Direct mode is the default: the current request and
canonical project instructions supply authority. Several steps, a remote service,
or work across a conversation do not by themselves require more Method.

Load protocols only when their task signal is present:

| Protocol | Task signal | Module |
| --- | --- | --- |
| `program` | `{program}` | [Program](protocols/program.md) |
| `experiment` | `{experiment}` | [Experiment](protocols/experiment.md) |
| `secrets` | `{secrets}` | [Secrets](protocols/secrets.md) |

Protocols add procedure, never permission. The CLI returns the verified modules:

```sh
method context --program
method context --experiment --format json
```

Program controls use the [human template](templates/program-control.md) and can
be checked across revisions:

```sh
method program validate CONTROL.md
method program validate CONTROL.md --previous PREVIOUS.md
```

Use an [EvidenceReceipt](templates/evidence-receipt.json) only when evidence can
be lost, destroyed, secret-reduced, or cannot be preserved for a successor by
ordinary durable evidence. Crossing sessions alone is insufficient:

```sh
method receipt validate RECEIPT.json
```

Machine-readable routing is in [CONTEXT.json](CONTEXT.json). The receipt schema
is in [`schemas/`](schemas/).

## Single-file fallback

Use [`../MONOLITH.md`](../MONOLITH.md) only when linked modules cannot be loaded.
It contains the same Kernel and all three protocols; it grants no authority.
"#
    ))
}

fn header(version: &str) -> String {
    format!(
        "<!-- Generated by `method dist build`; do not edit directly. -->\n<!-- Noel Method version {version}. -->"
    )
}

fn modular_document(version: &str, content: &str, prefix: &str) -> String {
    format!(
        "{}\n\n[Index]({prefix}INDEX.md) · [Kernel]({prefix}KERNEL.md)\n\n{content}\n",
        header(version)
    )
}

fn join_modules(kernel: &str, protocols: &BTreeMap<&str, String>) -> String {
    std::iter::once(kernel.to_owned())
        .chain(PROTOCOLS.into_iter().map(|name| protocols[name].clone()))
        .collect::<Vec<_>>()
        .join("\n\n---\n\n")
}

fn read_trimmed(root: &Path, relative: &str) -> Result<String> {
    Ok(fs::read_to_string(root.join(relative))?.trim().to_owned())
}

fn read_json(path: PathBuf) -> Result<Value> {
    parse_json_strict(&fs::read(path)?)
}

fn collect_relative_files(root: &Path) -> Result<BTreeSet<PathBuf>> {
    match fs::symlink_metadata(root) {
        Ok(metadata) if metadata.file_type().is_symlink() || !metadata.is_dir() => {
            return Err(MethodError::Data(format!(
                "distribution path is not a regular directory: {}",
                root.display()
            )));
        }
        Ok(_) => {}
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => {
            return Ok(BTreeSet::new());
        }
        Err(error) => return Err(error.into()),
    }
    let mut files = BTreeSet::new();
    collect_files(root, root, &mut files)?;
    Ok(files)
}

fn collect_files(root: &Path, directory: &Path, files: &mut BTreeSet<PathBuf>) -> Result<()> {
    for entry in fs::read_dir(directory)? {
        let entry = entry?;
        let path = entry.path();
        let metadata = fs::symlink_metadata(&path)?;
        if metadata.file_type().is_symlink() {
            return Err(MethodError::Data(format!(
                "distribution may not contain symlinks: {}",
                path.display()
            )));
        }
        if metadata.is_dir() {
            collect_files(root, &path, files)?;
        } else if metadata.is_file() {
            files.insert(
                path.strip_prefix(root)
                    .expect("contained path")
                    .to_path_buf(),
            );
        } else {
            return Err(MethodError::Data(format!(
                "distribution contains a non-regular file: {}",
                path.display()
            )));
        }
    }
    Ok(())
}

fn validate_output_path(root: &Path, path: &Path) -> Result<()> {
    let relative = path.strip_prefix(root).map_err(|_| {
        MethodError::Data(format!(
            "distribution output escapes root: {}",
            path.display()
        ))
    })?;
    let root_metadata = fs::symlink_metadata(root)?;
    if root_metadata.file_type().is_symlink() || !root_metadata.is_dir() {
        return Err(MethodError::Data(format!(
            "distribution root is not a regular directory: {}",
            root.display()
        )));
    }
    let mut current = root.to_path_buf();
    let components = relative.components().collect::<Vec<_>>();
    for component in components.iter().take(components.len().saturating_sub(1)) {
        current.push(component.as_os_str());
        match fs::symlink_metadata(&current) {
            Ok(metadata) if metadata.file_type().is_symlink() || !metadata.is_dir() => {
                return Err(MethodError::Data(format!(
                    "distribution parent is not a regular directory: {}",
                    current.display()
                )));
            }
            Ok(_) => {}
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(()),
            Err(error) => return Err(error.into()),
        }
    }
    match fs::symlink_metadata(path) {
        Ok(metadata) if metadata.file_type().is_symlink() || !metadata.is_file() => {
            Err(MethodError::Data(format!(
                "distribution output is not a regular file: {}",
                path.display()
            )))
        }
        Ok(_) => Ok(()),
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(()),
        Err(error) => Err(error.into()),
    }
}

fn prepare_output_path(root: &Path, path: &Path) -> Result<()> {
    let relative = path
        .strip_prefix(root)
        .expect("validated output under root");
    let mut current = root.to_path_buf();
    let components = relative.components().collect::<Vec<_>>();
    for component in components.iter().take(components.len().saturating_sub(1)) {
        current.push(component.as_os_str());
        match fs::symlink_metadata(&current) {
            Ok(metadata) if metadata.file_type().is_symlink() || !metadata.is_dir() => {
                return Err(MethodError::Data(format!(
                    "distribution parent is not a regular directory: {}",
                    current.display()
                )));
            }
            Ok(_) => {}
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => {
                fs::create_dir(&current)?;
            }
            Err(error) => return Err(error.into()),
        }
    }
    validate_output_path(root, path)
}

fn remove_stale_pack_files(pack: &Path, expected: &BTreeSet<PathBuf>) -> Result<()> {
    for relative in collect_relative_files(pack)? {
        if !expected.contains(&relative) {
            fs::remove_file(pack.join(relative))?;
        }
    }
    Ok(())
}
