# Runtime Contracts

These contracts define the small public interface between people, resolvers,
tools, and delegated actors. JSON Schemas under `schemas/` are authoritative
for document shape; the packaged resolver owns semantic acceptance checks that
schemas cannot express, such as source precedence and action-set relations.

## ProjectProfile

A ProjectProfile is standing project policy, accepted once per policy revision.
It defines canonical sources, default action boundaries, protocol defaults,
gates, secret controls, program repair authority, and reporting.

The canonical JSON has exactly five top-level fields: `schema_version`,
`method_version`, `profile_id`, `policy`, and `acceptance`. The policy digest
covers the canonical JSON representation of every field except `acceptance`.
Unknown or duplicate fields fail closed. Acceptance metadata is evidence only
when an independently authoritative receipt matches the exact policy digest.
The ProfileAuthorityRegistry shape is published under `schemas/`; it must live
outside the delegated model's write authority.

The coordinating model does not validate or load the ProjectProfile. A trusted
resolver validates it and emits the applicable policy as a RuntimeEnvelope.

## TaskRequest

A TaskRequest is trusted caller input for one controlled task. It states:

- task identity and outcome;
- included and excluded scope;
- non-authorizing logical references to relevant resources or live controls;
- requested and forbidden actions;
- program, experiment, and secret-risk signals;
- additional required gates;
- baseline identity, stop conditions, and expiry conditions.

Requested actions must be a subset of profile-allowed actions and must not
intersect any forbidden action.

## RuntimeEnvelope

A RuntimeEnvelope is generated, task-scoped capability context. It contains:

- exact profile identity, policy digest, and acceptance receipt;
- canonical sources and their precedence;
- allowed and forbidden actions;
- selected protocols;
- required gates and their evidence definitions; and
- only the project controls needed by the selected protocols, plus reporting.

The TaskRequest carries outcome, scope, logical references, baseline, stop, and
expiry data; the envelope does not repeat them. References must never be bearer
or authorizing material. Secret and program controls are omitted unless their
protocols are selected.

Only a trusted resolver may set `profile_verified` to `true`. The envelope does
not itself enforce a permission; the consuming harness should map action and
gate identifiers to enforceable tools where available.

## ControlledAction

Before a consequential mutation, restate only:

- outcome;
- allowed and forbidden action;
- gate that permits the action;
- recovery or accepted irreversibility; and
- stop condition.

Do not create a separate controlled-action artifact when the RuntimeEnvelope
already states these fields clearly.

## EvidenceReceipt

An EvidenceReceipt binds a claim to its observation, exact artifact,
environment, method, terminal result, citation, capture event, limitations, and
supersession condition. It contains no secret value. A newer artifact or
material environment change invalidates the old receipt for the changed claim.

## ProgramControl

ProgramControl exists only for persistent dependent workstreams. It records one
live program state, active coordinates, accepted frontiers, authorized queue,
hard gates, forbidden work, reconciliation receipt, and stop/resume conditions.

Only `ACTIVE` controls dispatch normal work. `STOPPED_FOR_REPLAN` permits
read-only diagnosis and independently authorized plan repair. `COMPLETE` and
`TERMINATED` controls have no active coordinates or dispatchable queue.
Authority invalidated by a finding cannot authorize its own repair or
acceptance.

The resolver selects Program but does not infer live program state. The harness
must separately validate and supply the ProgramControl named by the
TaskRequest. A missing or mismatched control keeps program work read-only.
