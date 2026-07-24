# Program Protocol

Use this protocol only for persistent dependent workstreams with a
ProgramControl. It adds coordination procedure to the Runtime Kernel and grants
no authority.

The TaskRequest must name the live ProgramControl with a non-authorizing
logical reference. The harness validates and supplies that control separately;
the model does not select a convenient historical control. Missing, ambiguous,
or mismatched control identity permits read-only diagnosis only.

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
unless the RuntimeEnvelope explicitly identifies the concurrency boundary.

Each work item produces one reviewable outcome and its evidence. Split source
implementation from real-world evidence when their prerequisites differ.

## Dispatch

Only an `ACTIVE` ProgramControl may dispatch normal work. Before dispatch,
publication, merge, release, or external mutation, reconcile:

- goal, execution plan, and live control;
- active coordinate and accepted workstream frontier;
- tracker and canonical artifact;
- applicable evidence and exact revision;
- affected external state;
- RuntimeEnvelope authority, gates, and expiry.

A passing test, healthy local state, or previous-head receipt is evidence, not
authority.

Work begins only when every named hard gate is `SATISFIED`. Later dependent work
does not begin while an earlier gate is `UNSATISFIED`. Same-wave preparation
must be named in the authorized queue with its prerequisites.

## Stop and repair

Set state to `STOPPED_FOR_REPLAN` when a finding changes scope, dependencies,
gates, authority, repositories, contracts, external controls, or acceptance.
While stopped:

- read-only diagnosis and issue capture may continue;
- normal dispatch and unrelated work remain forbidden;
- mechanical freeze and non-mutating evidence capture may follow the old
  control; and
- plan or control mutation requires a RuntimeEnvelope whose repair authority is
  independent of every invalidated field and control.

An invalidated actor or control cannot authorize its own repair, acceptance, or
resumption. Resume only after the repaired control is independently accepted
and a newly resolved RuntimeEnvelope names the resume authority and satisfied
condition.

Emergency containment does not reactivate the program. It follows the Secrets
protocol when applicable and requires its own pre-existing authority, scope,
receipt, and stop condition.

## Terminal states

Set `COMPLETE` only when every goal condition and required receipt is satisfied.
Set `TERMINATED` when work ends with unmet goals, recording exactly one reason:
`OWNER_CANCELLED`, `ABANDONED`, `SUPERSEDED`, or `SAFETY`.

`COMPLETE` and `TERMINATED` controls have no active coordinates or dispatchable
queue. A terminated control cannot resume. Later work needs a new independently
accepted control and RuntimeEnvelope.
