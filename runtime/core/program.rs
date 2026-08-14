use crate::{MethodError, Result};
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

pub const PROGRAM_SECTIONS: [&str; 7] = [
    "Goal",
    "Done when",
    "Current",
    "Next",
    "Needs from human",
    "Boundaries",
    "Evidence",
];

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ProgramMetadata {
    pub schema_version: u64,
    pub control_revision: u64,
    pub state: ProgramState,
    pub coordinator: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub termination_reason: Option<TerminationReason>,
}

#[derive(Clone, Copy, Debug, Deserialize, PartialEq, Eq, Serialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum ProgramState {
    Active,
    StoppedForReplan,
    Complete,
    Terminated,
}

impl ProgramState {
    pub const fn as_str(self) -> &'static str {
        match self {
            Self::Active => "ACTIVE",
            Self::StoppedForReplan => "STOPPED_FOR_REPLAN",
            Self::Complete => "COMPLETE",
            Self::Terminated => "TERMINATED",
        }
    }
}

#[derive(Clone, Copy, Debug, Deserialize, PartialEq, Eq, Serialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum TerminationReason {
    OwnerCancelled,
    Superseded,
    Safety,
}

#[derive(Clone, Debug, Serialize)]
pub struct ProgramDocument {
    pub metadata: ProgramMetadata,
    pub sections: BTreeMap<String, String>,
    pub word_count: usize,
    pub warnings: Vec<String>,
}

pub fn validate_program_document(input: &str) -> Result<ProgramDocument> {
    let normalized = input.replace("\r\n", "\n");
    let remainder = normalized.strip_prefix("```toml\n").ok_or_else(|| {
        MethodError::Data("Program control must begin with a fenced TOML block".to_owned())
    })?;
    let (header, markdown) = remainder
        .split_once("\n```\n")
        .ok_or_else(|| MethodError::Data("Program control TOML block is not closed".to_owned()))?;
    let metadata: ProgramMetadata = toml::from_str(header)
        .map_err(|error| MethodError::Data(format!("Program control TOML: {error}")))?;
    validate_metadata(&metadata)?;
    let sections = parse_sections(markdown)?;
    validate_state_sections(&metadata, &sections)?;

    let word_count = normalized.split_whitespace().count();
    let warnings = if word_count > 700 {
        vec![format!(
            "Program control is {word_count} words; keep live control near 700 words"
        )]
    } else {
        Vec::new()
    };

    Ok(ProgramDocument {
        metadata,
        sections,
        word_count,
        warnings,
    })
}

pub fn validate_program_transition(current: &str, previous: &str) -> Result<ProgramDocument> {
    let current = validate_program_document(current)?;
    let previous = validate_program_document(previous)?;
    if matches!(
        previous.metadata.state,
        ProgramState::Complete | ProgramState::Terminated
    ) {
        return Err(MethodError::Data(
            "A terminal Program control cannot be revised; start a new Program".to_owned(),
        ));
    }
    let expected = previous
        .metadata
        .control_revision
        .checked_add(1)
        .ok_or_else(|| MethodError::Data("Program control revision overflow".to_owned()))?;
    if current.metadata.control_revision != expected {
        return Err(MethodError::Data(format!(
            "Program control revision must be {expected} after revision {}",
            previous.metadata.control_revision
        )));
    }
    Ok(current)
}

fn validate_metadata(metadata: &ProgramMetadata) -> Result<()> {
    if metadata.schema_version != 1 {
        return Err(MethodError::Data(
            "Program control schema_version must be 1".to_owned(),
        ));
    }
    if metadata.control_revision == 0 {
        return Err(MethodError::Data(
            "Program control revision must be positive".to_owned(),
        ));
    }
    if metadata.coordinator.trim().is_empty() {
        return Err(MethodError::Data(
            "Program control coordinator must be non-empty".to_owned(),
        ));
    }
    match metadata.state {
        ProgramState::Terminated if metadata.termination_reason.is_none() => Err(
            MethodError::Data("TERMINATED requires termination_reason".to_owned()),
        ),
        ProgramState::Terminated => Ok(()),
        _ if metadata.termination_reason.is_some() => Err(MethodError::Data(
            "termination_reason is valid only for TERMINATED".to_owned(),
        )),
        _ => Ok(()),
    }
}

fn parse_sections(markdown: &str) -> Result<BTreeMap<String, String>> {
    let mut found = Vec::<(String, String)>::new();
    let mut current: Option<(String, Vec<&str>)> = None;
    let mut fence: Option<(char, usize)> = None;

    for line in markdown.lines() {
        if let Some((marker, length)) = fence {
            if let Some((candidate, candidate_length, trailing)) = fence_marker(line)
                && candidate == marker
                && candidate_length >= length
                && trailing.trim().is_empty()
            {
                fence = None;
            }
            if let Some((_, lines)) = current.as_mut() {
                lines.push(line);
            } else if !line.trim().is_empty() {
                return Err(MethodError::Data(
                    "Only whitespace may appear between the TOML header and Goal".to_owned(),
                ));
            }
            continue;
        }

        if let Some((marker, length, trailing)) = fence_marker(line) {
            if marker == '`' && trailing.contains('`') {
                return Err(MethodError::Data(
                    "Program control contains an ambiguous backtick fence".to_owned(),
                ));
            }
            if let Some((_, lines)) = current.as_mut() {
                lines.push(line);
                fence = Some((marker, length));
            } else {
                return Err(MethodError::Data(
                    "Only whitespace may appear between the TOML header and Goal".to_owned(),
                ));
            }
            continue;
        }

        reject_ambiguous_control_markdown(line)?;

        if let Some(heading) = h2_heading(line) {
            if !PROGRAM_SECTIONS.contains(&heading) {
                return Err(MethodError::Data(format!(
                    "Unknown Program control section: {heading}"
                )));
            }
            if let Some((name, lines)) = current.take() {
                found.push((name, lines.join("\n").trim().to_owned()));
            }
            current = Some((heading.to_owned(), Vec::new()));
        } else if let Some((_, lines)) = current.as_mut() {
            lines.push(line);
        } else if !line.trim().is_empty() {
            return Err(MethodError::Data(
                "Only whitespace may appear between the TOML header and Goal".to_owned(),
            ));
        }
    }
    if fence.is_some() {
        return Err(MethodError::Data(
            "Program control contains an unclosed fenced code block".to_owned(),
        ));
    }
    if let Some((name, lines)) = current {
        found.push((name, lines.join("\n").trim().to_owned()));
    }

    let names = found
        .iter()
        .map(|(name, _)| name.as_str())
        .collect::<Vec<_>>();
    if names != PROGRAM_SECTIONS {
        return Err(MethodError::Data(format!(
            "Program control sections must appear once in this order: {}",
            PROGRAM_SECTIONS.join(", ")
        )));
    }

    let mut sections = BTreeMap::new();
    for (name, content) in found {
        if content.is_empty() {
            return Err(MethodError::Data(format!(
                "Program control section {name} must be non-empty"
            )));
        }
        sections.insert(name, content);
    }
    Ok(sections)
}

fn reject_ambiguous_control_markdown(line: &str) -> Result<()> {
    let indentation = line.bytes().take_while(|byte| *byte == b' ').count();
    if indentation > 3 {
        return Ok(());
    }
    let candidate = line[indentation..].trim_end();
    if candidate == "="
        || candidate == "-"
        || (candidate.len() >= 2 && candidate.chars().all(|value| value == '='))
        || (candidate.len() >= 2 && candidate.chars().all(|value| value == '-'))
    {
        return Err(MethodError::Data(
            "Program control does not allow Setext headings or thematic breaks".to_owned(),
        ));
    }
    if candidate.strip_prefix('#').is_some_and(|rest| {
        !rest.starts_with('#') && (rest.is_empty() || rest.starts_with([' ', '\t']))
    }) {
        return Err(MethodError::Data(
            "Program control does not allow H1 headings".to_owned(),
        ));
    }
    let lowercase = candidate.to_ascii_lowercase();
    if contains_heading_tag(&lowercase) {
        return Err(MethodError::Data(
            "Program control does not allow raw HTML H1 or H2 headings".to_owned(),
        ));
    }
    Ok(())
}

fn contains_heading_tag(value: &str) -> bool {
    ["<h1", "</h1", "<h2", "</h2"].iter().any(|prefix| {
        value.match_indices(prefix).any(|(index, _)| {
            value[index + prefix.len()..]
                .chars()
                .next()
                .is_some_and(|character| character.is_ascii_whitespace() || character == '>')
        })
    })
}

/// Returns a CommonMark-style fence marker, its run length, and the remainder.
/// Up to three leading spaces are allowed; four spaces make the line code.
fn fence_marker(line: &str) -> Option<(char, usize, &str)> {
    let indentation = line.bytes().take_while(|byte| *byte == b' ').count();
    if indentation > 3 {
        return None;
    }
    let candidate = &line[indentation..];
    let marker = candidate.chars().next()?;
    if marker != '`' && marker != '~' {
        return None;
    }
    let length = candidate
        .chars()
        .take_while(|value| *value == marker)
        .count();
    if length < 3 {
        return None;
    }
    let offset = marker.len_utf8() * length;
    Some((marker, length, &candidate[offset..]))
}

/// Returns the normalized text of an H2 ATX heading. H3 and deeper headings are
/// section content. Optional closing hashes follow CommonMark's whitespace rule.
fn h2_heading(line: &str) -> Option<&str> {
    let indentation = line.bytes().take_while(|byte| *byte == b' ').count();
    if indentation > 3 {
        return None;
    }
    let candidate = &line[indentation..];
    let remainder = candidate.strip_prefix("##")?;
    if remainder.starts_with('#') {
        return None;
    }
    if !remainder.is_empty() && !remainder.starts_with([' ', '\t']) {
        return None;
    }

    let mut heading = remainder.trim();
    let without_hashes = heading.trim_end_matches('#');
    if without_hashes.len() != heading.len()
        && without_hashes
            .chars()
            .next_back()
            .is_some_and(char::is_whitespace)
    {
        heading = without_hashes.trim_end();
    }
    Some(heading)
}

fn validate_state_sections(
    metadata: &ProgramMetadata,
    sections: &BTreeMap<String, String>,
) -> Result<()> {
    let next = sections
        .get("Next")
        .expect("required Program section was parsed")
        .trim();
    match metadata.state {
        ProgramState::Active | ProgramState::StoppedForReplan if next == "None" => {
            Err(MethodError::Data(
                "ACTIVE and STOPPED_FOR_REPLAN require a Next action, awaited transition, or decision"
                    .to_owned(),
            ))
        }
        ProgramState::Complete | ProgramState::Terminated if next != "None" => Err(
            MethodError::Data("COMPLETE and TERMINATED require Next to be exactly None".to_owned()),
        ),
        _ => Ok(()),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn active(revision: u64) -> String {
        format!(
            "```toml\nschema_version = 1\ncontrol_revision = {revision}\nstate = \"ACTIVE\"\ncoordinator = \"/root\"\n```\n\n## Goal\n\nShip it.\n\n## Done when\n\nIt works.\n\n## Current\n\nReady.\n\n## Next\n\nImplement.\n\n## Needs from human\n\nNone\n\n## Boundaries\n\nNo production.\n\n## Evidence\n\nPR.\n"
        )
    }

    #[test]
    fn validates_active_document_and_transition() {
        let document = validate_program_document(&active(4)).unwrap();
        assert_eq!(document.metadata.control_revision, 4);
        assert!(document.warnings.is_empty());
        assert!(validate_program_transition(&active(5), &active(4)).is_ok());
        assert!(validate_program_transition(&active(7), &active(4)).is_err());
    }

    #[test]
    fn rejects_terminal_document_with_work() {
        let value = active(1).replace("state = \"ACTIVE\"", "state = \"COMPLETE\"");
        assert!(validate_program_document(&value).is_err());
    }

    #[test]
    fn accepts_crlf_h3_and_ignores_h2_inside_fences() {
        let value = active(1).replace(
            "Ready.",
            "### Detail\n\n```text\n## Next\n## Not a control section\n```",
        );
        let value = value.replace('\n', "\r\n");
        let document = validate_program_document(&value).unwrap();
        assert!(document.sections["Current"].contains("## Next"));
        assert_eq!(document.sections["Next"], "Implement.");
    }

    #[test]
    fn requires_strict_toml_header_and_known_metadata() {
        assert!(validate_program_document(&format!("intro\n{}", active(1))).is_err());
        assert!(validate_program_document(&active(1).replacen("```toml", " ```toml", 1)).is_err());
        assert!(
            validate_program_document(
                &active(1).replace("schema_version = 1", "schema_version = 1\nowner = \"noel\"")
            )
            .is_err()
        );
    }

    #[test]
    fn requires_each_h2_once_and_in_order_and_rejects_preamble() {
        assert!(validate_program_document(&active(1).replace("## Current", "## Notes")).is_err());
        assert!(validate_program_document(&active(1).replace("## Current", "## Goal")).is_err());
        assert!(
            validate_program_document(&active(1).replace("\n## Goal", "\npreamble\n## Goal"))
                .is_err()
        );
    }

    #[test]
    fn rejects_markdown_that_can_render_hidden_control_headings() {
        for replacement in [
            "Ready.\n\nHidden\n---",
            "Ready.\n\n# Hidden",
            "Ready.\n\n<h2>Next</h2>",
            "Ready.\n\n<div><h2 class=\"live\">Next</h2></div>",
            "Ready.\n\n```bad`info\n## Next\n```",
        ] {
            assert!(
                validate_program_document(&active(1).replace("Ready.", replacement)).is_err(),
                "ambiguous Markdown was accepted: {replacement}"
            );
        }
    }

    #[test]
    fn enforces_state_next_and_termination_contracts() {
        assert!(validate_program_document(&active(1).replace("Implement.", "None")).is_err());
        assert!(
            validate_program_document(
                &active(1)
                    .replace("state = \"ACTIVE\"", "state = \"STOPPED_FOR_REPLAN\"")
                    .replace("Implement.", "None")
            )
            .is_err()
        );

        let complete = active(1)
            .replace("state = \"ACTIVE\"", "state = \"COMPLETE\"")
            .replace("Implement.", "None");
        assert!(validate_program_document(&complete).is_ok());

        let terminated = active(1)
            .replace(
                "state = \"ACTIVE\"",
                "state = \"TERMINATED\"\ntermination_reason = \"SUPERSEDED\"",
            )
            .replace("Implement.", "None");
        assert_eq!(
            validate_program_document(&terminated)
                .unwrap()
                .metadata
                .termination_reason,
            Some(TerminationReason::Superseded)
        );
        assert!(
            validate_program_document(
                &terminated.replace("\ntermination_reason = \"SUPERSEDED\"", "")
            )
            .is_err()
        );
        assert!(
            validate_program_document(&active(1).replace(
                "coordinator = \"/root\"",
                "coordinator = \"/root\"\ntermination_reason = \"SAFETY\""
            ))
            .is_err()
        );
    }

    #[test]
    fn transition_requires_next_revision_but_allows_coordinator_transfer() {
        let transferred =
            active(5).replace("coordinator = \"/root\"", "coordinator = \"/root/new\"");
        assert!(validate_program_transition(&transferred, &active(4)).is_ok());
        assert!(validate_program_transition(&active(6), &active(4)).is_err());

        let complete = active(4)
            .replace("state = \"ACTIVE\"", "state = \"COMPLETE\"")
            .replace("Implement.", "None");
        assert!(validate_program_transition(&active(5), &complete).is_err());

        let stopped = active(4).replace("state = \"ACTIVE\"", "state = \"STOPPED_FOR_REPLAN\"");
        let stopped_complete = active(5)
            .replace("state = \"ACTIVE\"", "state = \"COMPLETE\"")
            .replace("Implement.", "None");
        assert!(validate_program_transition(&stopped_complete, &stopped).is_ok());
        assert!(validate_program_transition(&active(5), &stopped).is_ok());
    }

    #[test]
    fn warns_when_live_markdown_exceeds_seven_hundred_words() {
        let value = active(1).replace("PR.", &vec!["evidence"; 701].join(" "));
        let document = validate_program_document(&value).unwrap();
        assert!(document.word_count > 700);
        assert_eq!(document.warnings.len(), 1);
    }
}
