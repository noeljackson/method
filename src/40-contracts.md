# Public Contracts

The contracts below are stable interfaces. Projects may add fields but should
preserve these meanings so prompts and reports remain portable.

## WorkContract

Required fields:

- `objective` — the concrete outcome.
- `why` — the decision or need this work serves.
- `deliverable` — the artifact or state that will exist.
- `in_scope` and `out_of_scope` — the allowed boundary.
- `authority` — mutations and decisions the executor may make.
- `forbidden_work` — actions that remain disallowed even if convenient.
- `sources_of_truth` — ordered references used to resolve facts.
- `known_evidence` and `unknowns` — observations, inferences, and open links.
- `acceptance_gates` — binary conditions and required evidence.
- `reporting` — required outcome and evidence format.
- `escalation` — conditions that stop or reframe work.

## EvidenceRecord

Required fields:

- `claim`
- `observation`
- `artifact_identity`
- `environment_identity`
- `method`
- `result`
- `citation`
- `captured_at`
- `freshness_or_supersession`

An evidence record MAY state that a field is not applicable, but it MUST NOT
silently omit identity needed to reproduce or interpret the claim.

## ProjectProfile

Required fields:

- method version and profile scope;
- source-of-truth hierarchy;
- role-to-actor mapping and separation policy;
- work-scale thresholds;
- domain problem taxonomy;
- mutation authority and prohibited actions;
- work-item and review boundary;
- gate catalog and evidence format;
- verification selection by blast surface;
- tool, environment, secret, and external-state rules;
- reporting and learning destinations; and
- explicit owner decisions that specialize optional behavior.

## ProgramControl

Required fields:

- `program`
- `program_state`
- `current_coordinate`
- `accepted_boundary`
- `authorized_queue`
- `hard_gates`
- `forbidden_work`
- `canonical_sources`
- `active_owner_decisions`
- `reconciliation_receipt`
- `stop_condition`
- `resume_condition`

Only one live program control may authorize mutation. Superseded controls move
to history and remain non-authoritative evidence.
