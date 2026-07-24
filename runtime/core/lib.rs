mod canonical;
mod contracts;
pub mod dist;
mod pack;
mod validation;

pub use canonical::{canonical_json, parse_json_strict, sha256_hex};
pub use contracts::{
    EvidenceReceipt, PolicyAuthorityRegistry, ProgramControl, ProjectPolicy, ProtocolFlags,
    ResolvedPermissions, TaskRequest,
};
pub use pack::{PackFile, PackManifest, PackReport, verify_pack_directory, verify_pack_files};
pub use validation::{
    ValidationKind, context_protocols, project_policy_digest, resolve_permissions,
    validate_authority_registry, validate_evidence_receipt, validate_program_control,
    validate_project_policy, validate_resolved_permissions, validate_task_request,
    verify_project_policy,
};

use std::io;
use thiserror::Error;

pub const METHOD_VERSION: &str = env!("CARGO_PKG_VERSION");

#[derive(Debug, Error)]
pub enum MethodError {
    #[error("{0}")]
    Data(String),
    #[error("{0}")]
    Io(#[from] io::Error),
    #[error("{0}")]
    Json(String),
}

impl From<serde_json::Error> for MethodError {
    fn from(error: serde_json::Error) -> Self {
        Self::Json(error.to_string())
    }
}

pub type Result<T> = std::result::Result<T, MethodError>;
