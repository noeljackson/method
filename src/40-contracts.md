# Public Contracts

Projects may add fields but should preserve these stable meanings.

## WorkContract

Required fields:

- `outcome` — concrete intended result;
- `disposition` — `PROCEED`, `HOLD`, `CONTAIN`, or `TERMINATE`;
- `scope` — included and excluded work;
- `authority` — permitted decisions and mutations, plus forbidden work;
- `evidence` — sources, observations, inferences, and unknowns;
- `gates` — binary acceptance conditions and receipts;
- `next_evidence` — what permits the next disposition change; and
- `reporting` — audience, destination, and format.

Add `recovery` for consequential or destructive mutation, including rollback,
forward repair, isolation, or accepted irreversibility and a negative
authority-boundary check. Add `secrets`, `program`, or `experiment` when the
corresponding context flag is true.

## ActionEnvelope

Every substantive recommendation or handoff keeps these fields stable:

- `disposition`
- `observations`
- `inferences_and_unknowns`
- `allowed_actions`
- `forbidden_actions`
- `gates`
- `recovery`
- `next_evidence`

## EvidenceRecord

Required fields are `claim`, `observation`, `artifact_identity`,
`environment_identity`, `method`, `result`, `citation`, `captured_at`, and
`freshness_or_supersession`. Do not omit identity needed to reproduce or
interpret the claim.

## ProjectProfile

Required fields:

- `profile_status` — `DRAFT` or `ACCEPTED`;
- `authority_source`, `profile_digest`, `accepted_by`, `accepted_at`, and
  `acceptance_receipt` binding acceptance to an independently authoritative
  source and the exact profile revision;
- method version and profile scope;
- canonical sources and their precedence;
- role, authority, mutation, and separation boundaries;
- work-scale thresholds, gates, and evidence policy;
- conditional secret policy and emergency containment authority; and
- reporting and learning destinations.

A draft or unverifiable profile grants no mutation authority. Acceptance
metadata inside the profile is not evidence by itself. A profile may set
context flags to true but cannot force an applicable flag false.

## ProgramControl

Required fields are `program`, `program_state`, `active_coordinates`,
`accepted_frontiers`, `authorized_queue`, `hard_gates`, `forbidden_work`,
`canonical_sources`, `active_owner_decisions`, `reconciliation_receipt`,
`stop_condition`, `resume_condition`, `terminal_disposition`, and
`terminal_receipt`.

Terminal fields are required only for `TERMINATED` and preserve authority,
reason, evidence, unmet goals, and external-state disposition. Only one live
ProgramControl may authorize mutation. Superseded controls remain historical
evidence.
