use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Default, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ProtocolFlags {
    pub program: bool,
    pub experiment: bool,
    pub secrets: bool,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct EvidenceReceipt {
    pub schema_version: u64,
    pub durability_reason: DurabilityReason,
    pub subject_identity: String,
    pub environment_identity: String,
    pub procedure: String,
    pub claims: Vec<EvidenceClaim>,
    pub evidence_ref: String,
    pub captured_at: String,
    pub limitations: Vec<String>,
    pub source_disposition: SourceDisposition,
    pub supersedes: Option<String>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct EvidenceClaim {
    pub id: String,
    pub outcome: ClaimOutcome,
    pub observation: String,
}

#[derive(Clone, Copy, Debug, Deserialize, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum DurabilityReason {
    Ephemeral,
    DestructiveOutput,
    SecretReduced,
    SuccessorGap,
}

#[derive(Clone, Copy, Debug, Deserialize, Serialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum ClaimOutcome {
    Supported,
    Rejected,
    Inconclusive,
}

#[derive(Clone, Copy, Debug, Deserialize, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum SourceDisposition {
    NotSensitive,
    RetainedProtected,
    ReducedAndDestroyed,
}
