# Runtime Contracts

These contracts define the small public interface between people, hosts,
tools, and delegated actors. Direct mode requires no Method-specific document.
The JSON forms under `schemas/` are optional automation serializations. The
packaged resolver owns semantic checks that schemas cannot express, such as
source precedence and action-set relations.

## ProjectPolicy

A ProjectPolicy is standing policy for resolved mode, accepted once per policy
revision. It defines canonical sources, action boundaries, protocol defaults,
gates, secret controls, program repair authority, and reporting.

The canonical JSON has exactly five top-level fields: `schema_version`,
`method_version`, `policy_id`, `policy`, and `acceptance`. The policy digest
covers the canonical JSON representation of every field except `acceptance`.
Unknown or duplicate fields fail closed. Acceptance metadata is evidence only
when an independently authoritative receipt matches the exact policy digest.
The PolicyAuthorityRegistry shape is published under `schemas/`; it must live
outside the delegated model's write authority.

The coordinating model does not validate or load the ProjectPolicy. The
consuming host validates it and supplies the accepted input to the resolver.

## TaskRequest

A TaskRequest is a host-authenticated snapshot of the caller's request for one
resolved-mode task. A model draft is not authoritative merely because it
matches the schema. It states:

- task identity and outcome;
- included and excluded scope;
- non-authorizing logical references to relevant resources or live controls;
- requested and forbidden actions;
- program, experiment, and secret-risk signals;
- additional required gates;
- baseline identity, stop conditions, and expiry conditions.

Requested actions must be a subset of policy-allowed actions and must not
intersect any forbidden action.

## ResolvedPermissions

ResolvedPermissions is generated, task-scoped capability context. It contains:

- the explicit `resolved` authority mode and exact TaskRequest digest;
- exact policy identity, digest, and acceptance receipt;
- canonical sources and their precedence;
- allowed and forbidden actions;
- selected protocols;
- required gates and their evidence definitions; and
- only the project controls needed by the selected protocols, plus reporting.

The TaskRequest carries outcome, scope, logical references, baseline, stop, and
expiry data; ResolvedPermissions does not repeat them. References must never
be bearer or authorizing material. Secret and program controls are omitted
unless their protocols are selected.

Only the consuming host may treat `policy_verified: true` as meaningful. The
resolver proves structural consistency and a matching acceptance receipt; it
does not authenticate the caller, prove that a TaskRequest preserves the
conversation, or enforce a permission. The host must protect the ProjectPolicy
and authority registry, bind the accepted TaskRequest, and map action and gate
identifiers to enforceable tools where available.

## ControlledAction

Before a consequential mutation, restate only:

- outcome;
- allowed and forbidden action;
- gate that permits the action;
- recovery or accepted irreversibility; and
- stop condition.

Do not create a separate controlled-action artifact when the applicable direct
boundary or ResolvedPermissions already states these fields clearly.

## EvidenceReceipt

An EvidenceReceipt binds a claim to its observation, exact artifact,
environment, method, terminal result, citation, capture event, limitations, and
supersession condition. It contains no secret value. A newer artifact or
material environment change invalidates the old receipt for the changed claim.

## ProgramControl

ProgramControl exists only for persistent dependent workstreams. It records one
live program state, active coordinates, accepted frontiers, authorized queue,
hard gates with the actions or coordinates they block, forbidden work,
reconciliation receipt, and stop/resume conditions. It may be a canonical plan
block, tracker record, host state, or the optional JSON serialization. The
Method does not require JSON or the `method` binary. A copied or rendered
control identifies its canonical source and revision; if that identity is stale
or ambiguous, the copy is evidence rather than live authority.

Only `ACTIVE` controls dispatch normal work. A defect that remains inside the
accepted coordinate boundaries keeps the control active, makes the affected
coordinate's applicable gates unsatisfied, and does not block explicitly
independent authorized coordinates. A finding that materially invalidates the
live control sets `STOPPED_FOR_REPLAN`, which permits read-only diagnosis and
independently authorized plan repair. `COMPLETE` and `TERMINATED` controls have
no active coordinates or dispatchable queue. Authority invalidated by a finding
cannot authorize its own repair or acceptance.

Protocol routing does not infer live program state. The actor or host must
reconcile the ProgramControl identified by the current request and canonical
plan, or by the TaskRequest in resolved mode. A missing or mismatched control
keeps program work read-only.
