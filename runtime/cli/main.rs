use clap::{Args, Parser, Subcommand, ValueEnum};
use include_dir::{Dir, DirEntry, include_dir};
use method_core::{
    METHOD_VERSION, MethodError, ProtocolFlags, context_protocols, parse_json_strict, sha256_hex,
    validate_evidence_receipt, validate_program_document, validate_program_transition,
    verify_pack_directory, verify_pack_files,
};
use serde::Serialize;
use serde_json::{Value, json};
use std::collections::BTreeMap;
use std::fs;
use std::io::{self, Read};
use std::path::{Path, PathBuf};
use std::process::ExitCode;

static EMBEDDED_PACK: Dir<'_> = include_dir!("$CARGO_MANIFEST_DIR/dist/pack");
const BUILD_COMMIT: &str = env!("METHOD_BUILD_COMMIT");

#[derive(Debug, Parser)]
#[command(name = "method", version = METHOD_VERSION)]
#[command(about = "Small runtime tools for the Noel Method")]
struct Cli {
    #[command(subcommand)]
    command: Command,
}

#[derive(Debug, Subcommand)]
enum Command {
    Version(JsonOutput),
    Context(ContextArgs),
    Program {
        #[command(subcommand)]
        command: ProgramCommand,
    },
    Receipt {
        #[command(subcommand)]
        command: ReceiptCommand,
    },
    Pack {
        #[command(subcommand)]
        command: PackCommand,
    },
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
enum ProgramCommand {
    Validate(ProgramValidateArgs),
}

#[derive(Debug, Args)]
struct ProgramValidateArgs {
    path: String,
    #[arg(long)]
    previous: Option<String>,
    #[arg(long)]
    json: bool,
}

#[derive(Debug, Subcommand)]
enum ReceiptCommand {
    Validate(ReceiptValidateArgs),
}

#[derive(Debug, Args)]
struct ReceiptValidateArgs {
    path: String,
    #[arg(long)]
    json: bool,
}

#[derive(Debug, Subcommand)]
enum PackCommand {
    Verify(PackVerifyArgs),
}

#[derive(Debug, Args)]
struct PackVerifyArgs {
    path: Option<PathBuf>,
    #[arg(long)]
    expect_manifest_sha256: Option<String>,
    #[arg(long)]
    json: bool,
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

#[derive(Clone, Copy, Debug, Default, ValueEnum)]
enum ContextFormat {
    #[default]
    Markdown,
    Json,
}

#[derive(Debug, Args)]
struct ContextArgs {
    #[arg(long)]
    program: bool,
    #[arg(long)]
    experiment: bool,
    #[arg(long)]
    secrets: bool,
    #[arg(long, value_enum, default_value_t)]
    format: ContextFormat,
}

fn main() -> ExitCode {
    match run(Cli::parse()) {
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
        Command::Program { command } => match command {
            ProgramCommand::Validate(args) => command_program_validate(args),
        },
        Command::Receipt { command } => match command {
            ReceiptCommand::Validate(args) => command_receipt_validate(args),
        },
        Command::Pack { command } => match command {
            PackCommand::Verify(args) => command_pack_verify(args),
        },
        Command::Dist { command } => command_dist(command),
    }
}

fn command_version(args: JsonOutput) -> method_core::Result<()> {
    let report = verify_pack_files(&embedded_files())?;
    require_embedded_version(&report.version)?;
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

fn command_context(args: ContextArgs) -> method_core::Result<()> {
    let protocols = context_protocols(&ProtocolFlags {
        program: args.program,
        experiment: args.experiment,
        secrets: args.secrets,
    });
    let files = embedded_files();
    let report = verify_pack_files(&files)?;
    require_embedded_version(&report.version)?;
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
                .map(|path| embedded_text(&files, path))
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
                    Ok(json!({
                        "path": path,
                        "sha256": sha256_hex(bytes),
                        "content": embedded_text(&files, path)?,
                    }))
                })
                .collect::<method_core::Result<Vec<_>>>()?;
            print_json(&json!({
                "schema_version": 4,
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

fn command_program_validate(args: ProgramValidateArgs) -> method_core::Result<()> {
    if args.path == "-" && args.previous.as_deref() == Some("-") {
        return Err(MethodError::Data(
            "current and previous Program controls cannot both read stdin".to_owned(),
        ));
    }
    let current = read_text(&args.path)?;
    let transition_checked = args.previous.is_some();
    let document = if let Some(previous) = &args.previous {
        validate_program_transition(&current, &read_text(previous)?)?
    } else {
        validate_program_document(&current)?
    };
    if args.json {
        print_json(&json!({
            "kind": "program-control",
            "valid": true,
            "metadata": document.metadata,
            "word_count": document.word_count,
            "warnings": document.warnings,
            "transition_checked": transition_checked,
        }))?;
    } else {
        println!(
            "valid Program control revision {} ({}, {} words{})",
            document.metadata.control_revision,
            document.metadata.state.as_str(),
            document.word_count,
            if transition_checked {
                ", transition checked"
            } else {
                ""
            }
        );
        for warning in document.warnings {
            eprintln!("warning: {warning}");
        }
    }
    Ok(())
}

fn command_receipt_validate(args: ReceiptValidateArgs) -> method_core::Result<()> {
    let receipt = validate_evidence_receipt(&read_json(&args.path)?)?;
    if args.json {
        print_json(&json!({
            "kind": "evidence-receipt",
            "valid": true,
            "schema_version": receipt.schema_version,
            "claim_count": receipt.claims.len(),
        }))?;
    } else {
        println!(
            "valid EvidenceReceipt v{} ({} claims)",
            receipt.schema_version,
            receipt.claims.len()
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
        validate_digest(expected)?;
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

fn validate_digest(value: &str) -> method_core::Result<()> {
    if value.len() != 64
        || !value
            .chars()
            .all(|character| character.is_ascii_digit() || ('a'..='f').contains(&character))
    {
        return Err(MethodError::Data(
            "--expect-manifest-sha256 must be lowercase SHA-256".to_owned(),
        ));
    }
    Ok(())
}

fn require_embedded_version(version: &str) -> method_core::Result<()> {
    if version != METHOD_VERSION {
        return Err(MethodError::Data(format!(
            "embedded pack version differs from CLI: pack {version}, CLI {METHOD_VERSION}"
        )));
    }
    Ok(())
}

fn read_json(path: &str) -> method_core::Result<Value> {
    parse_json_strict(&read_bytes(path)?)
}

fn read_text(path: &str) -> method_core::Result<String> {
    String::from_utf8(read_bytes(path)?)
        .map_err(|error| MethodError::Data(format!("input is not UTF-8 ({path}): {error}")))
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

fn embedded_text(files: &BTreeMap<String, Vec<u8>>, path: &str) -> method_core::Result<String> {
    let bytes = files
        .get(path)
        .ok_or_else(|| MethodError::Data(format!("embedded pack is missing {path}")))?;
    String::from_utf8(bytes.clone()).map_err(|error| {
        MethodError::Data(format!("embedded pack file is not UTF-8 ({path}): {error}"))
    })
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
                files.insert(normalized_path(file.path()), file.contents().to_vec());
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
