use clap::{Args, Parser, Subcommand, ValueEnum};
use include_dir::{Dir, DirEntry, include_dir};
use method_core::{
    METHOD_VERSION, MethodError, ProtocolFlags, ValidationKind, canonical_json, context_protocols,
    parse_json_strict, project_policy_digest, resolve_permissions, sha256_hex,
    validate_authority_registry, validate_evidence_receipt, validate_program_control,
    validate_project_policy, validate_resolved_permissions, validate_task_request,
    verify_pack_directory, verify_pack_files, verify_project_policy,
};
use serde::Serialize;
use serde_json::{Value, json};
use std::collections::BTreeMap;
use std::fs;
use std::io::{self, Read};
use std::path::{Path, PathBuf};
use std::process::ExitCode;
use std::str::FromStr;

static EMBEDDED_PACK: Dir<'_> = include_dir!("$CARGO_MANIFEST_DIR/dist/pack");
const BUILD_COMMIT: &str = env!("METHOD_BUILD_COMMIT");

#[derive(Debug, Parser)]
#[command(name = "method", version = METHOD_VERSION)]
#[command(about = "Portable runtime tooling for the Noel Method")]
struct Cli {
    #[command(subcommand)]
    command: Command,
}

#[derive(Debug, Subcommand)]
enum Command {
    Version(JsonOutput),
    Context(ContextArgs),
    Validate(ValidateArgs),
    Pack {
        #[command(subcommand)]
        command: PackCommand,
    },
    Policy {
        #[command(subcommand)]
        command: PolicyCommand,
    },
    Resolve(ResolveArgs),
    Dist {
        #[command(subcommand)]
        command: DistCommand,
    },
}

#[derive(Clone, Debug, Args)]
struct JsonOutput {
    #[arg(long)]
    json: bool,
}

#[derive(Debug, Subcommand)]
enum PackCommand {
    Verify(PackVerifyArgs),
}

#[derive(Debug, Subcommand)]
enum DistCommand {
    Build(DistArgs),
    Check(DistArgs),
}

#[derive(Debug, Args)]
struct DistArgs {
    #[arg(long)]
    root: Option<PathBuf>,
}

#[derive(Debug, Args)]
struct PackVerifyArgs {
    path: Option<PathBuf>,
    #[arg(long)]
    expect_manifest_sha256: Option<String>,
    #[arg(long)]
    json: bool,
}

#[derive(Clone, Copy, Debug, Default, ValueEnum)]
enum ContextFormat {
    #[default]
    Markdown,
    Json,
}

#[derive(Debug, Args)]
struct ContextArgs {
    #[arg(long)]
    task: Option<String>,
    #[arg(long)]
    permissions: Option<String>,
    #[arg(long)]
    program: bool,
    #[arg(long)]
    experiment: bool,
    #[arg(long)]
    secrets: bool,
    #[arg(long, value_enum, default_value_t)]
    format: ContextFormat,
}

#[derive(Debug, Args)]
struct ValidateArgs {
    kind: String,
    path: String,
    #[arg(long)]
    json: bool,
}

#[derive(Debug, Subcommand)]
enum PolicyCommand {
    Digest(PolicyDigestArgs),
    Verify(PolicyVerifyArgs),
}

#[derive(Debug, Args)]
struct PolicyDigestArgs {
    policy: String,
    #[arg(long)]
    json: bool,
}

#[derive(Debug, Args)]
struct PolicyVerifyArgs {
    policy: String,
    #[arg(long)]
    authorities: String,
    #[arg(long)]
    json: bool,
}

#[derive(Debug, Args)]
struct ResolveArgs {
    #[arg(long)]
    policy: String,
    #[arg(long)]
    authorities: String,
    #[arg(long)]
    task: String,
    #[arg(long)]
    model_flags: Option<String>,
}

fn main() -> ExitCode {
    let cli = Cli::parse();
    match run(cli) {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) => {
            eprintln!("method: {error}");
            match error {
                MethodError::Data(_) | MethodError::Json(_) => ExitCode::from(2),
                MethodError::Io(_) => ExitCode::from(1),
            }
        }
    }
}

fn run(cli: Cli) -> method_core::Result<()> {
    match cli.command {
        Command::Version(args) => command_version(args),
        Command::Context(args) => command_context(args),
        Command::Validate(args) => command_validate(args),
        Command::Pack { command } => match command {
            PackCommand::Verify(args) => command_pack_verify(args),
        },
        Command::Policy { command } => match command {
            PolicyCommand::Digest(args) => command_policy_digest(args),
            PolicyCommand::Verify(args) => command_policy_verify(args),
        },
        Command::Resolve(args) => command_resolve(args),
        Command::Dist { command } => command_dist(command),
    }
}

fn command_dist(command: DistCommand) -> method_core::Result<()> {
    let (build, args) = match command {
        DistCommand::Build(args) => (true, args),
        DistCommand::Check(args) => (false, args),
    };
    let root = args.root.unwrap_or_else(method_core::dist::default_root);
    if build {
        for path in method_core::dist::build_distribution(&root)? {
            println!("wrote {}", path.display());
        }
    } else {
        method_core::dist::check_distribution(&root)?;
        println!("generated distribution is current");
    }
    Ok(())
}

fn command_version(args: JsonOutput) -> method_core::Result<()> {
    let files = embedded_files();
    let report = verify_pack_files(&files)?;
    if args.json {
        print_json(&json!({
            "cli": "method",
            "cli_version": METHOD_VERSION,
            "method_version": report.version,
            "build_commit": BUILD_COMMIT,
            "pack_manifest_sha256": report.manifest_sha256,
        }))?;
    } else {
        println!(
            "method {} (Noel Method {}, pack {}, commit {})",
            METHOD_VERSION, report.version, report.manifest_sha256, BUILD_COMMIT
        );
    }
    Ok(())
}

fn command_pack_verify(args: PackVerifyArgs) -> method_core::Result<()> {
    let report = if let Some(path) = args.path {
        verify_pack_directory(&path)?
    } else {
        verify_pack_files(&embedded_files())?
    };
    if let Some(expected) = &args.expect_manifest_sha256 {
        if expected.len() != 64
            || !expected
                .chars()
                .all(|value| value.is_ascii_digit() || ('a'..='f').contains(&value))
        {
            return Err(MethodError::Data(
                "--expect-manifest-sha256 must be lowercase SHA-256".to_owned(),
            ));
        }
        if report.manifest_sha256 != *expected {
            return Err(MethodError::Data(format!(
                "pack manifest SHA-256 differs: expected {expected}, got {}",
                report.manifest_sha256
            )));
        }
    }
    if args.json {
        print_json(&json!({
            "method": report.method,
            "version": report.version,
            "manifest_sha256": report.manifest_sha256,
            "file_count": report.file_count,
            "verified": report.verified,
            "expected_manifest_sha256": args.expect_manifest_sha256,
            "trust_anchor_matched": args.expect_manifest_sha256.as_ref().map(|_| true),
        }))?;
    } else {
        println!(
            "verified Noel Method {} pack: {} files, manifest {}",
            report.version, report.file_count, report.manifest_sha256
        );
    }
    Ok(())
}

fn command_context(args: ContextArgs) -> method_core::Result<()> {
    if args.task.as_deref() == Some("-") && args.permissions.as_deref() == Some("-") {
        return Err(MethodError::Data(
            "--task and --permissions cannot both read stdin".to_owned(),
        ));
    }
    let task = args
        .task
        .as_deref()
        .map(read_json)
        .transpose()?
        .as_ref()
        .map(validate_task_request)
        .transpose()?;
    let permissions = args
        .permissions
        .as_deref()
        .map(read_json)
        .transpose()?
        .as_ref()
        .map(validate_resolved_permissions)
        .transpose()?;
    if let (Some(task), Some(permissions)) = (&task, &permissions) {
        let task_value = serde_json::to_value(task)?;
        let digest = sha256_hex(&canonical_json(&task_value)?);
        if task.task_id != permissions.task_id || digest != permissions.task_sha256 {
            return Err(MethodError::Data(
                "TaskRequest does not match ResolvedPermissions".to_owned(),
            ));
        }
    }
    let flags = ProtocolFlags {
        program: args.program,
        experiment: args.experiment,
        secrets: args.secrets,
    };
    let requested_protocols = context_protocols(task.as_ref(), &flags);
    let protocols = ["program", "experiment", "secrets"]
        .into_iter()
        .filter(|protocol| {
            requested_protocols.iter().any(|value| value == protocol)
                || permissions
                    .as_ref()
                    .is_some_and(|value| value.protocols.iter().any(|item| item == protocol))
        })
        .map(str::to_owned)
        .collect::<Vec<_>>();
    let files = embedded_files();
    let report = verify_pack_files(&files)?;
    let mut paths = vec!["KERNEL.md".to_owned()];
    paths.extend(
        protocols
            .iter()
            .map(|protocol| format!("protocols/{protocol}.md")),
    );

    match args.format {
        ContextFormat::Markdown => {
            let content = paths
                .iter()
                .map(|path| {
                    files
                        .get(path)
                        .ok_or_else(|| {
                            MethodError::Data(format!("embedded pack is missing {path}"))
                        })
                        .and_then(|bytes| {
                            String::from_utf8(bytes.clone()).map_err(|error| {
                                MethodError::Data(format!(
                                    "embedded pack file is not UTF-8 ({path}): {error}"
                                ))
                            })
                        })
                })
                .collect::<method_core::Result<Vec<_>>>()?
                .join("\n\n---\n\n");
            print!("{content}");
            if !content.ends_with('\n') {
                println!();
            }
        }
        ContextFormat::Json => {
            let modules = paths
                .iter()
                .map(|path| {
                    let bytes = files.get(path).expect("verified embedded pack file");
                    let content = String::from_utf8(bytes.clone())
                        .expect("generated Markdown in the embedded pack is UTF-8");
                    json!({
                        "path": path,
                        "sha256": sha256_hex(bytes),
                        "content": content,
                    })
                })
                .collect::<Vec<_>>();
            print_json(&json!({
                "method": report.method,
                "version": report.version,
                "pack_manifest_sha256": report.manifest_sha256,
                "selected_protocols": protocols,
                "modules": modules,
            }))?;
        }
    }
    Ok(())
}

fn command_validate(args: ValidateArgs) -> method_core::Result<()> {
    let kind = ValidationKind::from_str(&args.kind)?;
    let value = read_json(&args.path)?;
    match kind {
        ValidationKind::ProjectPolicy => {
            validate_project_policy(&value)?;
        }
        ValidationKind::PolicyAuthorities => {
            validate_authority_registry(&value)?;
        }
        ValidationKind::TaskRequest => {
            validate_task_request(&value)?;
        }
        ValidationKind::ResolvedPermissions => {
            validate_resolved_permissions(&value)?;
        }
        ValidationKind::ProgramControl => {
            validate_program_control(&value)?;
        }
        ValidationKind::EvidenceReceipt => {
            validate_evidence_receipt(&value)?;
        }
    }
    if args.json {
        print_json(&json!({
            "kind": kind.as_str(),
            "schema_valid": true,
            "authority_verified": false,
        }))?;
    } else {
        println!(
            "{} is structurally valid (authority not verified)",
            kind.as_str()
        );
    }
    Ok(())
}

fn command_policy_digest(args: PolicyDigestArgs) -> method_core::Result<()> {
    let digest = project_policy_digest(&read_json(&args.policy)?)?;
    if args.json {
        print_json(&json!({"policy_sha256": digest}))?;
    } else {
        println!("{digest}");
    }
    Ok(())
}

fn command_policy_verify(args: PolicyVerifyArgs) -> method_core::Result<()> {
    let policy = read_json(&args.policy)?;
    let authorities = read_json(&args.authorities)?;
    let verified = verify_project_policy(&policy, &authorities)?;
    let output = json!({
        "policy_id": verified.policy_id,
        "method_version": verified.method_version,
        "policy_sha256": verified.policy_sha256,
        "verified": true,
        "acceptance_receipt": verified.acceptance_receipt,
    });
    if args.json {
        print_json(&output)?;
    } else {
        println!(
            "verified policy {} ({}) with receipt {}",
            output["policy_id"].as_str().unwrap_or_default(),
            output["policy_sha256"].as_str().unwrap_or_default(),
            output["acceptance_receipt"].as_str().unwrap_or_default(),
        );
    }
    Ok(())
}

fn command_resolve(args: ResolveArgs) -> method_core::Result<()> {
    let flags = args
        .model_flags
        .as_deref()
        .map(read_json)
        .transpose()?
        .map(|value| {
            serde_json::from_value::<ProtocolFlags>(value)
                .map_err(|error| MethodError::Data(format!("model flags: {error}")))
        })
        .transpose()?;
    let permissions = resolve_permissions(
        &read_json(&args.policy)?,
        &read_json(&args.authorities)?,
        &read_json(&args.task)?,
        flags,
    )?;
    print_json(&permissions)
}

fn read_json(path: &str) -> method_core::Result<Value> {
    let bytes = read_bytes(path)?;
    parse_json_strict(&bytes)
}

fn read_bytes(path: &str) -> method_core::Result<Vec<u8>> {
    if path == "-" {
        let mut bytes = Vec::new();
        io::stdin().read_to_end(&mut bytes)?;
        Ok(bytes)
    } else {
        Ok(fs::read(path)?)
    }
}

fn print_json(value: &impl Serialize) -> method_core::Result<()> {
    println!("{}", serde_json::to_string_pretty(value)?);
    Ok(())
}

fn embedded_files() -> BTreeMap<String, Vec<u8>> {
    let mut files = BTreeMap::new();
    collect_embedded(&EMBEDDED_PACK, &mut files);
    files
}

fn collect_embedded(directory: &Dir<'_>, files: &mut BTreeMap<String, Vec<u8>>) {
    for entry in directory.entries() {
        match entry {
            DirEntry::Dir(directory) => collect_embedded(directory, files),
            DirEntry::File(file) => {
                let path = normalized_path(file.path());
                files.insert(path, file.contents().to_vec());
            }
        }
    }
}

fn normalized_path(path: &Path) -> String {
    path.components()
        .map(|component| component.as_os_str().to_string_lossy())
        .collect::<Vec<_>>()
        .join("/")
}
