mod canonical;
mod contracts;
pub mod dist;
mod pack;
mod program;
mod validation;

pub use canonical::{parse_json_strict, sha256_hex};
pub use contracts::{
    ClaimOutcome, DurabilityReason, EvidenceClaim, EvidenceReceipt, ProtocolFlags,
    SourceDisposition,
};
pub use pack::{PackFile, PackManifest, PackReport, verify_pack_directory, verify_pack_files};
pub use program::{
    PROGRAM_SECTIONS, ProgramDocument, ProgramMetadata, ProgramState, TerminationReason,
    validate_program_document, validate_program_transition,
};
pub use validation::{context_protocols, validate_evidence_receipt};

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
