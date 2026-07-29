use crate::canonical::{canonical_json, sha256_hex};
use crate::contracts::*;
use crate::{METHOD_VERSION, MethodError, Result};
use serde::de::DeserializeOwned;
use serde_json::Value;
use std::collections::{BTreeSet, HashMap, HashSet};
use std::str::FromStr;

const PROTOCOLS: [&str; 3] = ["program", "experiment", "secrets"];

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ValidationKind {
    ProjectPolicy,
    PolicyAuthorities,
    TaskRequest,
    ResolvedPermissions,
    ProgramControl,
    EvidenceReceipt,
}

impl ValidationKind {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::ProjectPolicy => "project-policy",
            Self::PolicyAuthorities => "policy-authorities",
            Self::TaskRequest => "task-request",
            Self::ResolvedPermissions => "resolved-permissions",
            Self::ProgramControl => "program-control",
            Self::EvidenceReceipt => "evidence-receipt",
        }
    }
}

impl FromStr for ValidationKind {
    type Err = MethodError;

    fn from_str(value: &str) -> Result<Self> {
        match value {
            "project-policy" => Ok(Self::ProjectPolicy),
            "policy-authorities" => Ok(Self::PolicyAuthorities),
            "task-request" => Ok(Self::TaskRequest),
            "resolved-permissions" => Ok(Self::ResolvedPermissions),
            "program-control" => Ok(Self::ProgramControl),
            "evidence-receipt" => Ok(Self::EvidenceReceipt),
            _ => Err(MethodError::Data(format!(
                "unknown validation kind: {value}"
            ))),
        }
    }
}

#[derive(Clone, Debug)]
pub struct VerifiedProjectPolicy {
    pub policy_id: String,
    pub method_version: String,
    pub policy_sha256: String,
    pub acceptance_receipt: String,
    pub policy: PolicyBody,
}

pub fn validate_project_policy(value: &Value) -> Result<ProjectPolicy> {
    let policy: ProjectPolicy = decode(value, "ProjectPolicy")?;
    if policy.schema_version != 1 {
        return data("ProjectPolicy.schema_version: must be 1");
    }
    validate_method_version(&policy.method_version, "ProjectPolicy.method_version")?;
    identifier(&policy.policy_id, "ProjectPolicy.policy_id", true)?;
    validate_policy_body(&policy.policy)?;
    match policy.acceptance.status.as_str() {
        "draft" | "accepted" => {}
        _ => return data("ProjectPolicy.acceptance.status: invalid value"),
    }
    Ok(policy)
}

pub fn validate_authority_registry(value: &Value) -> Result<PolicyAuthorityRegistry> {
    let authorities: PolicyAuthorityRegistry = decode(value, "PolicyAuthorityRegistry")?;
    for (receipt_id, receipt) in &authorities {
        identifier(receipt_id, "authority receipt id", false)?;
        identifier(&receipt.policy_id, "authority receipt policy_id", true)?;
        validate_method_version(&receipt.method_version, "authority receipt method_version")?;
        lowercase_sha256(&receipt.policy_sha256, "authority receipt policy_sha256")?;
        nonempty(
            &receipt.authority_source,
            "authority receipt authority_source",
        )?;
        nonempty(&receipt.accepted_by, "authority receipt accepted_by")?;
        nonempty(&receipt.accepted_at, "authority receipt accepted_at")?;
    }
    Ok(authorities)
}

pub fn project_policy_digest(value: &Value) -> Result<String> {
    let policy = validate_project_policy(value)?;
    let mut payload = serde_json::to_value(policy)?;
    payload
        .as_object_mut()
        .expect("serialized ProjectPolicy is an object")
        .remove("acceptance");
    Ok(sha256_hex(&canonical_json(&payload)?))
}

pub fn verify_project_policy(
    policy_value: &Value,
    authorities_value: &Value,
) -> Result<VerifiedProjectPolicy> {
    let policy = validate_project_policy(policy_value)?;
    if policy.acceptance.status != "accepted" {
        return data("ProjectPolicy.acceptance.status: must be accepted");
    }
    let digest = project_policy_digest(policy_value)?;
    lowercase_sha256(
        &policy.acceptance.policy_sha256,
        "ProjectPolicy.acceptance.policy_sha256",
    )?;
    if policy.acceptance.policy_sha256 != digest {
        return data("ProjectPolicy acceptance digest is stale");
    }
    nonempty(
        &policy.acceptance.authority_source,
        "ProjectPolicy.acceptance.authority_source",
    )?;
    nonempty(
        &policy.acceptance.accepted_by,
        "ProjectPolicy.acceptance.accepted_by",
    )?;
    nonempty(
        &policy.acceptance.accepted_at,
        "ProjectPolicy.acceptance.accepted_at",
    )?;
    nonempty(
        &policy.acceptance.receipt,
        "ProjectPolicy.acceptance.receipt",
    )?;

    let authorities = validate_authority_registry(authorities_value)?;
    let expected = AuthorityReceipt {
        policy_id: policy.policy_id.clone(),
        method_version: policy.method_version.clone(),
        policy_sha256: digest.clone(),
        authority_source: policy.acceptance.authority_source.clone(),
        accepted_by: policy.acceptance.accepted_by.clone(),
        accepted_at: policy.acceptance.accepted_at.clone(),
    };
    if authorities.get(&policy.acceptance.receipt) != Some(&expected) {
        return data("ProjectPolicy authority receipt does not match");
    }

    Ok(VerifiedProjectPolicy {
        policy_id: policy.policy_id,
        method_version: policy.method_version,
        policy_sha256: digest,
        acceptance_receipt: policy.acceptance.receipt,
        policy: policy.policy,
    })
}

pub fn validate_task_request(value: &Value) -> Result<TaskRequest> {
    let task: TaskRequest = decode(value, "TaskRequest")?;
    if task.schema_version != 1 {
        return data("TaskRequest.schema_version: must be 1");
    }
    identifier(&task.task_id, "TaskRequest.task_id", false)?;
    nonempty(&task.outcome, "TaskRequest.outcome")?;
    strings(&task.scope.include, "TaskRequest.scope.include", false)?;
    strings(&task.scope.exclude, "TaskRequest.scope.exclude", true)?;
    strings(&task.resource_refs, "TaskRequest.resource_refs", true)?;
    strings(
        &task.requested_actions,
        "TaskRequest.requested_actions",
        true,
    )?;
    strings(
        &task.forbidden_actions,
        "TaskRequest.forbidden_actions",
        true,
    )?;
    match task.signals.secret_risk.as_str() {
        "none" | "possible" | "required" => {}
        _ => return data("TaskRequest.signals.secret_risk: invalid value"),
    }
    strings(&task.required_gates, "TaskRequest.required_gates", true)?;
    nonempty(&task.baseline_identity, "TaskRequest.baseline_identity")?;
    strings(&task.stop_conditions, "TaskRequest.stop_conditions", false)?;
    strings(&task.expires_on, "TaskRequest.expires_on", false)?;
    Ok(task)
}

pub fn validate_resolved_permissions(value: &Value) -> Result<ResolvedPermissions> {
    let permissions: ResolvedPermissions = decode(value, "ResolvedPermissions")?;
    if permissions.schema_version != 1 {
        return data("ResolvedPermissions.schema_version: must be 1");
    }
    validate_method_version(
        &permissions.method_version,
        "ResolvedPermissions.method_version",
    )?;
    if permissions.authority_mode != "resolved" {
        return data("ResolvedPermissions.authority_mode: must be resolved");
    }
    if !permissions.policy_verified {
        return data("ResolvedPermissions.policy_verified: must be true");
    }
    nonempty(&permissions.task_id, "ResolvedPermissions.task_id")?;
    lowercase_sha256(&permissions.task_sha256, "ResolvedPermissions.task_sha256")?;
    nonempty(
        &permissions.policy_ref.id,
        "ResolvedPermissions.policy_ref.id",
    )?;
    lowercase_sha256(
        &permissions.policy_ref.policy_sha256,
        "ResolvedPermissions.policy_ref.policy_sha256",
    )?;
    nonempty(
        &permissions.policy_ref.acceptance_receipt,
        "ResolvedPermissions.policy_ref.acceptance_receipt",
    )?;
    validate_sources(&permissions.canonical_sources)?;
    strings(
        &permissions.allowed_actions,
        "ResolvedPermissions.allowed_actions",
        true,
    )?;
    strings(
        &permissions.forbidden_actions,
        "ResolvedPermissions.forbidden_actions",
        true,
    )?;
    protocol_list(&permissions.protocols)?;
    validate_gates(&permissions.required_gates, true)?;
    nonempty(
        &permissions.controls.reporting,
        "ResolvedPermissions.controls.reporting",
    )?;
    let has_program = permissions.protocols.iter().any(|value| value == "program");
    let has_secrets = permissions.protocols.iter().any(|value| value == "secrets");
    if has_program != permissions.controls.program_repair_authority.is_some() {
        return data(
            "ResolvedPermissions.controls.program_repair_authority must match Program selection",
        );
    }
    if has_secrets != permissions.controls.secrets.is_some() {
        return data("ResolvedPermissions.controls.secrets must match Secrets selection");
    }
    if let Some(value) = &permissions.controls.program_repair_authority {
        nonempty(
            value,
            "ResolvedPermissions.controls.program_repair_authority",
        )?;
    }
    if let Some(secrets) = &permissions.controls.secrets {
        validate_secret_controls(secrets)?;
    }
    Ok(permissions)
}

pub fn validate_program_control(value: &Value) -> Result<ProgramControl> {
    let control: ProgramControl = decode(value, "ProgramControl")?;
    if control.schema_version != 2 {
        return data("ProgramControl.schema_version: must be 2");
    }
    nonempty(&control.program, "ProgramControl.program")?;
    match control.state.as_str() {
        "ACTIVE" | "STOPPED_FOR_REPLAN" | "COMPLETE" | "TERMINATED" => {}
        _ => return data("ProgramControl.state: invalid state"),
    }
    let active = control
        .active_coordinates
        .iter()
        .map(|value| {
            value
                .as_str()
                .ok_or_else(|| {
                    MethodError::Data(
                        "ProgramControl.active_coordinates entries must be strings".to_owned(),
                    )
                })
                .map(ToOwned::to_owned)
        })
        .collect::<Result<Vec<_>>>()?;
    strings(&active, "ProgramControl.active_coordinates", true)?;

    let mut gate_ids = HashSet::new();
    for gate in &control.hard_gates {
        identifier(&gate.id, "ProgramControl.hard_gates.id", false)?;
        if !gate_ids.insert(gate.id.as_str()) {
            return data("ProgramControl.hard_gates: IDs must be unique");
        }
        strings(&gate.blocks, "ProgramControl.hard_gates.blocks", false)?;
        match gate.state.as_str() {
            "SATISFIED" => {
                if gate
                    .evidence_receipt
                    .as_ref()
                    .is_none_or(serde_json::Map::is_empty)
                {
                    return data("ProgramControl hard gate: SATISFIED requires evidence receipt");
                }
            }
            "UNSATISFIED" => {
                if gate.evidence_receipt.is_some() {
                    return data(
                        "ProgramControl hard gate: UNSATISFIED evidence receipt must be null",
                    );
                }
            }
            _ => return data("ProgramControl hard gate: invalid state"),
        }
    }
    nonempty(&control.stop_condition, "ProgramControl.stop_condition")?;
    nonempty(&control.resume_condition, "ProgramControl.resume_condition")?;
    if matches!(control.state.as_str(), "COMPLETE" | "TERMINATED")
        && (!control.active_coordinates.is_empty() || !control.authorized_queue.is_empty())
    {
        return data("terminal ProgramControl cannot dispatch work");
    }
    if control.state == "COMPLETE"
        && control
            .hard_gates
            .iter()
            .any(|gate| gate.state != "SATISFIED")
    {
        return data("complete ProgramControl cannot have an unsatisfied hard gate");
    }
    if control.state == "ACTIVE"
        && (control.reconciliation_receipt.is_empty() || control.hard_gates.is_empty())
    {
        return data("active ProgramControl needs a reconciliation receipt and hard gates");
    }
    if control.state == "TERMINATED" {
        let reason = control
            .terminal_disposition
            .as_ref()
            .and_then(|value| value.get("reason"))
            .and_then(Value::as_str);
        if !matches!(
            reason,
            Some("OWNER_CANCELLED" | "ABANDONED" | "SUPERSEDED" | "SAFETY")
        ) {
            return data("terminated ProgramControl needs a valid disposition");
        }
    } else if control.terminal_disposition.is_some() {
        return data("terminal_disposition is only valid for TERMINATED");
    }
    Ok(control)
}

pub fn validate_evidence_receipt(value: &Value) -> Result<EvidenceReceipt> {
    let receipt: EvidenceReceipt = decode(value, "EvidenceReceipt")?;
    if receipt.schema_version != 1 {
        return data("EvidenceReceipt.schema_version: must be 1");
    }
    for (label, value) in [
        ("claim", &receipt.claim),
        ("observation", &receipt.observation),
        ("artifact_identity", &receipt.artifact_identity),
        ("environment_identity", &receipt.environment_identity),
        ("method", &receipt.method),
        ("result", &receipt.result),
        ("citation", &receipt.citation),
        ("captured_at", &receipt.captured_at),
        ("superseded_by", &receipt.superseded_by),
    ] {
        nonempty(value, &format!("EvidenceReceipt.{label}"))?;
    }
    strings(&receipt.limitations, "EvidenceReceipt.limitations", false)?;
    Ok(receipt)
}

pub fn context_protocols(task: Option<&TaskRequest>, model_flags: &ProtocolFlags) -> Vec<String> {
    let task_flags = task.map_or_else(ProtocolFlags::default, |task| ProtocolFlags {
        program: task.signals.persistent_program,
        experiment: task.signals.controlled_comparison,
        secrets: task.signals.secret_risk != "none",
    });
    PROTOCOLS
        .iter()
        .filter(|protocol| match **protocol {
            "program" => task_flags.program || model_flags.program,
            "experiment" => task_flags.experiment || model_flags.experiment,
            "secrets" => task_flags.secrets || model_flags.secrets,
            _ => false,
        })
        .map(|protocol| (*protocol).to_owned())
        .collect()
}

pub fn resolve_permissions(
    policy_value: &Value,
    authorities_value: &Value,
    task_value: &Value,
    model_flags: Option<ProtocolFlags>,
) -> Result<ResolvedPermissions> {
    let verified = verify_project_policy(policy_value, authorities_value)?;
    let task = validate_task_request(task_value)?;
    let flags = model_flags.unwrap_or_default();
    let task_protocols = context_protocols(Some(&task), &flags);
    let protocols = PROTOCOLS
        .iter()
        .filter(|protocol| {
            let policy_enabled = match **protocol {
                "program" => verified.policy.protocols.program,
                "experiment" => verified.policy.protocols.experiment,
                "secrets" => verified.policy.protocols.secrets,
                _ => false,
            };
            policy_enabled || task_protocols.iter().any(|value| value == **protocol)
        })
        .map(|value| (*value).to_owned())
        .collect::<Vec<_>>();

    if protocols.iter().any(|value| value == "program")
        && !task
            .resource_refs
            .iter()
            .any(|value| value.starts_with("program-control:"))
    {
        return data("Program protocol requires a program-control: logical reference");
    }

    let allowed = verified
        .policy
        .actions
        .allowed
        .iter()
        .collect::<HashSet<_>>();
    let unknown = task
        .requested_actions
        .iter()
        .filter(|value| !allowed.contains(value))
        .cloned()
        .collect::<BTreeSet<_>>();
    if !unknown.is_empty() {
        return data(format!(
            "task requests actions not allowed by the ProjectPolicy: {}",
            unknown.into_iter().collect::<Vec<_>>().join(", ")
        ));
    }

    let mut forbidden = Vec::new();
    for value in verified
        .policy
        .actions
        .forbidden
        .iter()
        .chain(task.forbidden_actions.iter())
    {
        if !forbidden.contains(value) {
            forbidden.push(value.clone());
        }
    }
    let forbidden_set = forbidden.iter().collect::<HashSet<_>>();
    let conflicts = task
        .requested_actions
        .iter()
        .filter(|value| forbidden_set.contains(value))
        .cloned()
        .collect::<BTreeSet<_>>();
    if !conflicts.is_empty() {
        return data(format!(
            "task requests forbidden actions: {}",
            conflicts.into_iter().collect::<Vec<_>>().join(", ")
        ));
    }

    let gate_by_id = verified
        .policy
        .gates
        .iter()
        .map(|gate| (gate.id.as_str(), gate))
        .collect::<HashMap<_, _>>();
    let unknown_gates = task
        .required_gates
        .iter()
        .filter(|gate| !gate_by_id.contains_key(gate.as_str()))
        .cloned()
        .collect::<BTreeSet<_>>();
    if !unknown_gates.is_empty() {
        return data(format!(
            "task requests unknown gates: {}",
            unknown_gates.into_iter().collect::<Vec<_>>().join(", ")
        ));
    }
    let mut gate_ids = Vec::new();
    for gate in &verified.policy.gates {
        if gate.default {
            gate_ids.push(gate.id.clone());
        }
    }
    for gate in &task.required_gates {
        if !gate_ids.contains(gate) {
            gate_ids.push(gate.clone());
        }
    }
    let required_gates = gate_ids
        .iter()
        .map(|id| (*gate_by_id[id.as_str()]).clone())
        .collect::<Vec<_>>();

    let controls = ResolvedControls {
        reporting: verified.policy.reporting.clone(),
        program_repair_authority: protocols
            .iter()
            .any(|value| value == "program")
            .then(|| verified.policy.program.repair_authority.clone()),
        secrets: protocols
            .iter()
            .any(|value| value == "secrets")
            .then(|| verified.policy.secrets.clone()),
    };
    let task_json = serde_json::to_value(&task)?;

    Ok(ResolvedPermissions {
        schema_version: 1,
        method_version: verified.method_version,
        authority_mode: "resolved".to_owned(),
        task_id: task.task_id,
        task_sha256: sha256_hex(&canonical_json(&task_json)?),
        policy_verified: true,
        policy_ref: PolicyReference {
            id: verified.policy_id,
            policy_sha256: verified.policy_sha256,
            acceptance_receipt: verified.acceptance_receipt,
        },
        canonical_sources: {
            let mut values = verified.policy.canonical_sources;
            values.sort_by_key(|value| value.precedence);
            values
        },
        allowed_actions: task.requested_actions,
        forbidden_actions: forbidden,
        protocols,
        required_gates,
        controls,
    })
}

fn validate_policy_body(policy: &PolicyBody) -> Result<()> {
    strings(&policy.scope, "ProjectPolicy.policy.scope", false)?;
    validate_sources(&policy.canonical_sources)?;
    strings(
        &policy.actions.allowed,
        "ProjectPolicy.policy.actions.allowed",
        true,
    )?;
    strings(
        &policy.actions.forbidden,
        "ProjectPolicy.policy.actions.forbidden",
        true,
    )?;
    let allowed = policy.actions.allowed.iter().collect::<HashSet<_>>();
    let overlap = policy
        .actions
        .forbidden
        .iter()
        .filter(|value| allowed.contains(value))
        .cloned()
        .collect::<BTreeSet<_>>();
    if !overlap.is_empty() {
        return data(format!(
            "ProjectPolicy.policy.actions: allowed and forbidden overlap: {}",
            overlap.into_iter().collect::<Vec<_>>().join(", ")
        ));
    }
    validate_gates(&policy.gates, false)?;
    validate_secret_controls(&policy.secrets)?;
    nonempty(
        &policy.program.trigger,
        "ProjectPolicy.policy.program.trigger",
    )?;
    nonempty(
        &policy.program.repair_authority,
        "ProjectPolicy.policy.program.repair_authority",
    )?;
    nonempty(&policy.reporting, "ProjectPolicy.policy.reporting")
}

fn validate_sources(sources: &[CanonicalSource]) -> Result<()> {
    if sources.is_empty() {
        return data("canonical_sources: must not be empty");
    }
    let mut ids = HashSet::new();
    let mut precedences = Vec::new();
    for source in sources {
        identifier(&source.id, "canonical_sources.id", false)?;
        nonempty(&source.owns, "canonical_sources.owns")?;
        if !ids.insert(source.id.as_str()) {
            return data("canonical_sources: IDs must be unique");
        }
        precedences.push(source.precedence);
    }
    precedences.sort_unstable();
    let expected = (1..=sources.len() as u64).collect::<Vec<_>>();
    if precedences != expected {
        return data("canonical_sources: precedence must be contiguous");
    }
    Ok(())
}

fn validate_gates(gates: &[GateDefinition], allow_empty: bool) -> Result<()> {
    if gates.is_empty() && !allow_empty {
        return data("gates: must not be empty");
    }
    let mut ids = HashSet::new();
    for gate in gates {
        identifier(&gate.id, "gates.id", false)?;
        nonempty(&gate.before, "gates.before")?;
        nonempty(&gate.required_evidence, "gates.required_evidence")?;
        if !ids.insert(gate.id.as_str()) {
            return data("gates: IDs must be unique");
        }
    }
    Ok(())
}

fn validate_secret_controls(secrets: &SecretControls) -> Result<()> {
    strings(
        &secrets.approved_references,
        "secrets.approved_references",
        false,
    )?;
    for (label, value) in [
        ("routine_access", &secrets.routine_access),
        ("delivery", &secrets.delivery),
        ("artifact_scan", &secrets.artifact_scan),
        ("exposure_response", &secrets.exposure_response),
        ("forensic_quarantine", &secrets.forensic_quarantine),
        ("clean_context", &secrets.clean_context),
        ("encrypted_envelopes", &secrets.encrypted_envelopes),
    ] {
        nonempty(value, &format!("secrets.{label}"))?;
    }
    Ok(())
}

fn protocol_list(values: &[String]) -> Result<()> {
    strings(values, "ResolvedPermissions.protocols", true)?;
    for value in values {
        if !PROTOCOLS.contains(&value.as_str()) {
            return data(format!("unknown protocol: {value}"));
        }
    }
    Ok(())
}

fn validate_method_version(value: &str, label: &str) -> Result<()> {
    let Some((supported_major, supported_minor)) = version_minor(METHOD_VERSION) else {
        return data(format!(
            "installed Method version is unsupported: {METHOD_VERSION}"
        ));
    };
    let expected = format!("{supported_major}.{supported_minor}.x");
    let Some((major, minor)) = version_minor(value) else {
        return data(format!("{label}: expected a {expected} release"));
    };
    if (major, minor) != (supported_major, supported_minor) {
        return data(format!("{label}: expected a {expected} release"));
    }
    Ok(())
}

fn version_minor(value: &str) -> Option<(&str, &str)> {
    let mut parts = value.split('.');
    let major = parts.next()?;
    let minor = parts.next()?;
    let patch = parts.next()?;
    if parts.next().is_some()
        || [major, minor, patch].iter().any(|part| {
            part.is_empty() || !part.chars().all(|character| character.is_ascii_digit())
        })
    {
        return None;
    }
    Some((major, minor))
}

fn identifier(value: &str, label: &str, policy: bool) -> Result<()> {
    nonempty(value, label)?;
    let mut characters = value.chars();
    let Some(first) = characters.next() else {
        return data(format!("{label}: invalid identifier"));
    };
    let first_valid = if policy {
        first.is_ascii_lowercase() || first.is_ascii_digit()
    } else {
        first.is_ascii_alphanumeric()
    };
    let rest_valid = characters.all(|character| {
        if policy {
            character.is_ascii_lowercase()
                || character.is_ascii_digit()
                || matches!(character, '.' | '_' | '-')
        } else {
            character.is_ascii_alphanumeric() || matches!(character, '.' | '_' | ':' | '/' | '-')
        }
    });
    if !first_valid || !rest_valid {
        return data(format!("{label}: invalid identifier"));
    }
    Ok(())
}

fn strings(values: &[String], label: &str, allow_empty: bool) -> Result<()> {
    if values.is_empty() && !allow_empty {
        return data(format!("{label}: must not be empty"));
    }
    let mut seen = HashSet::new();
    for value in values {
        nonempty(value, label)?;
        if !seen.insert(value.as_str()) {
            return data(format!("{label}: entries must be unique"));
        }
    }
    Ok(())
}

fn nonempty(value: &str, label: &str) -> Result<()> {
    if value.trim().is_empty() {
        return data(format!("{label}: must be non-empty text"));
    }
    Ok(())
}

fn lowercase_sha256(value: &str, label: &str) -> Result<()> {
    if value.len() != 64
        || !value
            .chars()
            .all(|character| character.is_ascii_digit() || ('a'..='f').contains(&character))
    {
        return data(format!("{label}: expected lowercase SHA-256"));
    }
    Ok(())
}

fn decode<T: DeserializeOwned>(value: &Value, label: &str) -> Result<T> {
    serde_json::from_value(value.clone())
        .map_err(|error| MethodError::Data(format!("{label}: {error}")))
}

fn data<T>(message: impl Into<String>) -> Result<T> {
    Err(MethodError::Data(message.into()))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parse_json_strict;

    #[test]
    fn direct_context_routes_monotonically() {
        let task_value = parse_json_strict(
            br#"{
              "schema_version":1,
              "task_id":"task-1",
              "outcome":"test",
              "scope":{"include":["x"],"exclude":[]},
              "resource_refs":[],
              "requested_actions":[],
              "forbidden_actions":[],
              "signals":{
                "persistent_program":false,
                "controlled_comparison":true,
                "secret_risk":"none"
              },
              "required_gates":[],
              "baseline_identity":"base",
              "stop_conditions":["unclear"],
              "expires_on":["task-end"]
            }"#,
        )
        .unwrap();
        let task = validate_task_request(&task_value).unwrap();
        let flags = ProtocolFlags {
            secrets: true,
            ..ProtocolFlags::default()
        };
        assert_eq!(
            context_protocols(Some(&task), &flags),
            ["experiment", "secrets"]
        );
    }

    #[test]
    fn method_version_accepts_only_the_installed_minor_line() {
        assert!(validate_method_version(METHOD_VERSION, "test").is_ok());
        assert!(validate_method_version("0.6.99", "test").is_ok());
        let error = validate_method_version("0.5.99", "test").unwrap_err();
        assert!(error.to_string().contains("expected a 0.6.x release"));
        assert!(validate_method_version("0.6", "test").is_err());
        assert!(validate_method_version("0.6.0-alpha", "test").is_err());
    }
}
