use crate::{MethodError, Result, parse_json_strict, sha256_hex};
use serde_json::{Value, json};
use std::collections::{BTreeMap, BTreeSet};
use std::fs;
use std::path::{Path, PathBuf};

const PROTOCOLS: [&str; 3] = ["program", "experiment", "secrets"];
const SCHEMAS: [&str; 6] = [
    "project-policy.schema.json",
    "policy-authorities.schema.json",
    "task-request.schema.json",
    "resolved-permissions.schema.json",
    "program-control.schema.json",
    "evidence-receipt.schema.json",
];

pub fn default_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
}

pub fn build_distribution(root: &Path) -> Result<Vec<PathBuf>> {
    let rendered = render_all(root)?;
    let pack = root.join("dist/pack");
    let mut written = Vec::new();
    for (relative, content) in &rendered {
        let path = root.join(relative);
        if let Some(parent) = path.parent() {
            fs::create_dir_all(parent)?;
        }
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
    let mut differences = Vec::new();
    for (relative, expected) in &rendered {
        let actual = fs::read_to_string(root.join(relative)).unwrap_or_default();
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
    Ok(format!(
        "{}\n# Noel Method Runtime Pack\n\nVersion: `{version}`\n\n## Default: direct mode\n\nLoad [Kernel](KERNEL.md). The current request and canonical project\ninstructions supply authority. Direct mode may include external or persistent\nwork when those sources authorize its scope, actions, gates, and prohibitions.\nDo not create Method artifacts merely because work has several steps, uses a\nremote service, or persists across a conversation.\n\nLoad protocols by task shape:\n\n| Protocol | Task signal | Module |\n| --- | --- | --- |\n| `program` | `{}` | [Program](protocols/program.md) |\n| `experiment` | `{}` | [Experiment](protocols/experiment.md) |\n| `secrets` | `{}` | [Secrets](protocols/secrets.md) |\n\nProtocols add procedure, never permission.\n\nThe CLI returns embedded verified modules as Markdown or stable JSON:\n\n```sh\nmethod context --program\nmethod context --experiment --format json\n```\n\n## Optional: resolved mode\n\nUse resolved mode only when the project, current request, or consuming host\nexplicitly selects it. The host authenticates the TaskRequest, protects the\naccepted ProjectPolicy and authority registry, runs the deterministic resolver,\nand enforces ResolvedPermissions:\n\n```sh\nmethod resolve \\\n  --policy PROJECT-POLICY.json \\\n  --authorities POLICY-AUTHORITIES.json \\\n  --task TASK-REQUEST.json > RESOLVED-PERMISSIONS.json\n\nmethod context --permissions RESOLVED-PERMISSIONS.json\n```\n\nLoad [Kernel](KERNEL.md), TaskRequest, ResolvedPermissions, and exactly the\nprotocol modules named by `protocols`. If resolved mode is selected and its\npermissions are missing, unverified, expired, or inconsistent with current\nstate, remain read-only.\n\nWhen Program is selected, separately validate and supply the ProgramControl\nnamed by the TaskRequest:\n\n```sh\nmethod validate program-control PROGRAM-CONTROL.json\n```\n\nThis validates structure and terminal-state invariants only. The harness must\nstill bind the control to current canonical state and authority.\n\nThe model may request another protocol when risk emerges. Only the resolver may\nissue updated ResolvedPermissions in resolved mode; the model cannot remove a\nprotocol, widen actions, or downgrade the authority mode.\n\nMachine-readable routing and schemas are in [CONTEXT.json](CONTEXT.json) and\n[`schemas/`](schemas/). Install the matching `method` release to resolve or\nvalidate structured controls.\n\n## Single-file fallback\n\nUse [`../MONOLITH.md`](../MONOLITH.md) only when linked modules cannot be\nloaded. It contains the same Kernel and all three protocols. It does not grant\nproject authority or select resolved mode.\n",
        header(version),
        signal("program")?,
        signal("experiment")?,
        signal("secrets")?
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
    if !root.exists() {
        return Ok(BTreeSet::new());
    }
    let mut files = BTreeSet::new();
    collect_files(root, root, &mut files)?;
    Ok(files)
}

fn collect_files(root: &Path, directory: &Path, files: &mut BTreeSet<PathBuf>) -> Result<()> {
    for entry in fs::read_dir(directory)? {
        let entry = entry?;
        let path = entry.path();
        if path.is_dir() {
            collect_files(root, &path, files)?;
        } else if path.is_file() {
            files.insert(
                path.strip_prefix(root)
                    .expect("contained path")
                    .to_path_buf(),
            );
        }
    }
    Ok(())
}

fn remove_stale_pack_files(pack: &Path, expected: &BTreeSet<PathBuf>) -> Result<()> {
    for relative in collect_relative_files(pack)? {
        if !expected.contains(&relative) {
            fs::remove_file(pack.join(relative))?;
        }
    }
    Ok(())
}
