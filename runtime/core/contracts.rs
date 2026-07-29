use serde::{Deserialize, Serialize};
use serde_json::{Map, Value};
use std::collections::BTreeMap;

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ProjectPolicy {
    pub schema_version: u64,
    pub method_version: String,
    pub policy_id: String,
    pub policy: PolicyBody,
    pub acceptance: PolicyAcceptance,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct PolicyBody {
    pub scope: Vec<String>,
    pub canonical_sources: Vec<CanonicalSource>,
    pub actions: ActionPolicy,
    pub protocols: ProtocolFlags,
    pub gates: Vec<GateDefinition>,
    pub secrets: SecretControls,
    pub program: ProgramPolicy,
    pub reporting: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct CanonicalSource {
    pub id: String,
    pub owns: String,
    pub precedence: u64,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ActionPolicy {
    pub allowed: Vec<String>,
    pub forbidden: Vec<String>,
}

#[derive(Clone, Debug, Default, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ProtocolFlags {
    pub program: bool,
    pub experiment: bool,
    pub secrets: bool,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct GateDefinition {
    pub id: String,
    pub default: bool,
    pub before: String,
    pub required_evidence: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct SecretControls {
    pub routine_access: String,
    pub approved_references: Vec<String>,
    pub delivery: String,
    pub artifact_scan: String,
    pub exposure_response: String,
    pub forensic_quarantine: String,
    pub clean_context: String,
    pub encrypted_envelopes: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ProgramPolicy {
    pub trigger: String,
    pub repair_authority: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct PolicyAcceptance {
    pub status: String,
    pub policy_sha256: String,
    pub authority_source: String,
    pub accepted_by: String,
    pub accepted_at: String,
    pub receipt: String,
}

pub type PolicyAuthorityRegistry = BTreeMap<String, AuthorityReceipt>;

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct AuthorityReceipt {
    pub policy_id: String,
    pub method_version: String,
    pub policy_sha256: String,
    pub authority_source: String,
    pub accepted_by: String,
    pub accepted_at: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct TaskRequest {
    pub schema_version: u64,
    pub task_id: String,
    pub outcome: String,
    pub scope: TaskScope,
    pub resource_refs: Vec<String>,
    pub requested_actions: Vec<String>,
    pub forbidden_actions: Vec<String>,
    pub signals: TaskSignals,
    pub required_gates: Vec<String>,
    pub baseline_identity: String,
    pub stop_conditions: Vec<String>,
    pub expires_on: Vec<String>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct TaskScope {
    pub include: Vec<String>,
    pub exclude: Vec<String>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct TaskSignals {
    pub persistent_program: bool,
    pub controlled_comparison: bool,
    pub secret_risk: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ResolvedPermissions {
    pub schema_version: u64,
    pub method_version: String,
    pub authority_mode: String,
    pub task_id: String,
    pub task_sha256: String,
    pub policy_verified: bool,
    pub policy_ref: PolicyReference,
    pub canonical_sources: Vec<CanonicalSource>,
    pub allowed_actions: Vec<String>,
    pub forbidden_actions: Vec<String>,
    pub protocols: Vec<String>,
    pub required_gates: Vec<GateDefinition>,
    pub controls: ResolvedControls,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct PolicyReference {
    pub id: String,
    pub policy_sha256: String,
    pub acceptance_receipt: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ResolvedControls {
    pub reporting: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub program_repair_authority: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub secrets: Option<SecretControls>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ProgramControl {
    pub schema_version: u64,
    pub program: String,
    pub state: String,
    pub active_coordinates: Vec<Value>,
    pub accepted_frontiers: Vec<Value>,
    pub authorized_queue: Vec<Value>,
    pub hard_gates: Vec<HardGate>,
    pub forbidden_work: Vec<Value>,
    pub reconciliation_receipt: Map<String, Value>,
    pub stop_condition: String,
    pub resume_condition: String,
    pub terminal_disposition: Option<Map<String, Value>>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct HardGate {
    pub id: String,
    pub blocks: Vec<String>,
    pub state: String,
    pub evidence_receipt: Option<Map<String, Value>>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct EvidenceReceipt {
    pub schema_version: u64,
    pub claim: String,
    pub observation: String,
    pub artifact_identity: String,
    pub environment_identity: String,
    pub method: String,
    pub result: String,
    pub citation: String,
    pub captured_at: String,
    pub limitations: Vec<String>,
    pub superseded_by: String,
}
