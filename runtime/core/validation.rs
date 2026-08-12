use crate::contracts::{EvidenceReceipt, ProtocolFlags};
use crate::{MethodError, Result};
use serde_json::Value;
use std::collections::HashSet;

const PROTOCOLS: [&str; 3] = ["program", "experiment", "secrets"];

pub fn context_protocols(flags: &ProtocolFlags) -> Vec<String> {
    PROTOCOLS
        .iter()
        .filter(|protocol| match **protocol {
            "program" => flags.program,
            "experiment" => flags.experiment,
            "secrets" => flags.secrets,
            _ => false,
        })
        .map(|value| (*value).to_owned())
        .collect()
}

pub fn validate_evidence_receipt(value: &Value) -> Result<EvidenceReceipt> {
    let receipt: EvidenceReceipt = serde_json::from_value(value.clone())
        .map_err(|error| MethodError::Data(format!("EvidenceReceipt: {error}")))?;
    if receipt.schema_version != 2 {
        return data("EvidenceReceipt.schema_version must be 2");
    }
    for (label, value) in [
        ("subject_identity", &receipt.subject_identity),
        ("environment_identity", &receipt.environment_identity),
        ("procedure", &receipt.procedure),
        ("evidence_ref", &receipt.evidence_ref),
        ("captured_at", &receipt.captured_at),
    ] {
        nonempty(value, &format!("EvidenceReceipt.{label}"))?;
    }
    if receipt.claims.is_empty() {
        return data("EvidenceReceipt.claims must not be empty");
    }
    let mut claim_ids = HashSet::new();
    for claim in &receipt.claims {
        identifier(&claim.id, "EvidenceReceipt.claims.id")?;
        if !claim_ids.insert(claim.id.as_str()) {
            return data("EvidenceReceipt.claim IDs must be unique");
        }
        nonempty(
            &claim.observation,
            &format!("EvidenceReceipt.claims.{}.observation", claim.id),
        )?;
    }
    unique_strings(&receipt.limitations, "EvidenceReceipt.limitations")?;
    if let Some(supersedes) = &receipt.supersedes {
        nonempty(supersedes, "EvidenceReceipt.supersedes")?;
    }
    Ok(receipt)
}

fn nonempty(value: &str, label: &str) -> Result<()> {
    if value.trim().is_empty() {
        data(format!("{label} must be non-empty"))
    } else {
        Ok(())
    }
}

fn identifier(value: &str, label: &str) -> Result<()> {
    nonempty(value, label)?;
    let mut chars = value.chars();
    let first = chars.next().expect("non-empty identifier");
    if !first.is_ascii_alphanumeric()
        || !chars.all(|character| {
            character.is_ascii_alphanumeric() || matches!(character, '.' | '_' | ':' | '/' | '-')
        })
    {
        return data(format!("{label} is not a portable identifier"));
    }
    Ok(())
}

fn unique_strings(values: &[String], label: &str) -> Result<()> {
    let mut seen = HashSet::new();
    for value in values {
        nonempty(value, label)?;
        if !seen.insert(value.as_str()) {
            return data(format!("{label} entries must be unique"));
        }
    }
    Ok(())
}

fn data<T>(message: impl Into<String>) -> Result<T> {
    Err(MethodError::Data(message.into()))
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn receipt_requires_unique_claims() {
        let value = json!({
            "schema_version": 2,
            "durability_reason": "ephemeral",
            "subject_identity": "tree:abc",
            "environment_identity": "qemu:test",
            "procedure": "run fixture",
            "claims": [
                {"id": "boot", "outcome": "SUPPORTED", "observation": "exact"},
                {"id": "boot", "outcome": "INCONCLUSIVE", "observation": "missing"}
            ],
            "evidence_ref": "fixture:1",
            "captured_at": "2026-08-12T00:00:00Z",
            "limitations": [],
            "source_disposition": "not_sensitive",
            "supersedes": null
        });
        assert!(validate_evidence_receipt(&value).is_err());
    }
}
