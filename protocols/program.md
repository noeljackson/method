# Program Protocol

Use this protocol only for persistent dependent workstreams with a
ProgramControl. It adds coordination procedure to the Runtime Kernel and grants
no authority.

The current request and canonical plan must identify the live ProgramControl.
In resolved mode, the TaskRequest also names it with a non-authorizing logical
reference. The actor does not select a convenient historical control. Missing,
ambiguous, or mismatched control identity permits read-only diagnosis only.

## Separate three artifacts

Maintain:

1. **Goal state** — durable end conditions and invariants.
2. **Execution plan** — workstreams, reviewable work items, dependencies, and
   acceptance criteria.
3. **ProgramControl** — the single live state, queue, gates, forbidden work, and
   reconciliation receipt.

Historical and superseded controls are evidence, not live authority.

## Coordinate mutations

Every program mutation names a stable coordinate:

```text
Program / Wave / Workstream / Work Item
```

Several coordinates may be active only when their dependency and shared-state
receipts establish independence. Shared or external mutations remain serialized
unless the applicable authority and live ProgramControl identify the
concurrency boundary.

Before fixing a work-item boundary, perform the smallest readiness pass capable
of checking the actual operating surface, state ownership, authority and
sensitive-data paths, delivery and verification mechanisms, and recovery
boundary. Record only findings that materially determine the work.

Each work item produces one cohesive reviewable outcome and its evidence. Its
default boundary is the smallest change that can be reviewed, accepted, and
recovered or withdrawn together. Do not create separate status, evidence,
repair, or bookkeeping work items when they have the same prerequisites and
recovery boundary. Split implementation from real-world evidence when their
prerequisites genuinely differ.

## Dispatch

Only an `ACTIVE` ProgramControl may dispatch normal work. Before dispatch,
publication, merge, release, or external mutation, reconcile:

- goal, execution plan, and live control;
- active coordinate and accepted workstream frontier;
- tracker and canonical artifact;
- applicable evidence and exact revision;
- affected external state;
- applicable direct authority or ResolvedPermissions, gates, and expiry.

A passing test, healthy local state, or previous-head receipt is evidence, not
authority.

Each hard gate names the mutation or downstream coordinate that it blocks.
Before an action, only that action's prerequisite gates must be `SATISFIED`.
An `UNSATISFIED` gate does not block an explicitly authorized coordinate whose
dependency and shared-state receipts establish independence. Distinguish a gate
that accepts the current artifact from one that permits downstream work.
Same-wave preparation must be named in the authorized queue with its
prerequisites.

## Stop and repair

Keep the ProgramControl `ACTIVE` when a defect or failed hypothesis remains
inside the affected coordinate's accepted outcome, authority, dependencies,
external-state boundary, acceptance criteria, and recovery boundary. Mark that
coordinate's applicable gates `UNSATISFIED`, repair it under the same
coordinate, and leave explicitly independent authorized coordinates
dispatchable.

Set state to `STOPPED_FOR_REPLAN` only when a finding materially invalidates the
live ProgramControl by changing scope, dependencies, gates, authority,
controlled artifacts or systems, contracts, external controls, acceptance
criteria, or recovery boundaries. While stopped:

- read-only diagnosis and issue capture may continue;
- normal dispatch and unrelated work remain forbidden;
- mechanical freeze and non-mutating evidence capture may follow the old
  control; and
- plan or control mutation requires explicit repair authority independent of
  every invalidated field and control. That may be a direct owner decision or
  new ResolvedPermissions when resolved mode is selected.

An invalidated actor or control cannot authorize its own repair, acceptance, or
resumption. Resume only after the repaired control is independently accepted
and the applicable direct authority or new ResolvedPermissions names the
resume authority and satisfied condition.

Emergency containment does not reactivate the program. It follows the Secrets
protocol when applicable and requires its own pre-existing authority, scope,
receipt, and stop condition.

## Terminal states

Set `COMPLETE` only when every goal condition and required receipt is satisfied.
Set `TERMINATED` when work ends with unmet goals, recording exactly one reason:
`OWNER_CANCELLED`, `ABANDONED`, `SUPERSEDED`, or `SAFETY`.

`COMPLETE` and `TERMINATED` controls have no active coordinates or dispatchable
queue. A terminated control cannot resume. Later work needs a new independently
accepted control and applicable authority.
