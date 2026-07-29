# Program Protocol

Use this protocol only for persistent dependent workstreams. It adds
coordination procedure to the Runtime Kernel and grants no authority. A
program needs a live control, but that control may be a canonical plan block,
tracker record, host state, or optional structured document.

## Keep one live control

Keep three concerns separate:

1. **Goal state** — durable end conditions and invariants.
2. **Execution plan** — workstreams, recovery boundaries, dependencies, and
   acceptance criteria.
3. **ProgramControl** — current state, mutation claims, authorized queue,
   gates, forbidden work, and reconciliation receipt.

The request and canonical plan identify the live ProgramControl. A copied or
rendered control must identify its canonical source and revision. Superseded or
stale controls are evidence, not live authority. Missing, ambiguous, or
mismatched control identity permits read-only diagnosis only.

## Shape and coordinate work

Every program mutation names a stable coordinate:

```text
Program / Wave / Workstream / Work Item
```

Define a work item as the smallest cohesive outcome that can be reviewed,
accepted, and recovered or withdrawn together. Do not split status, evidence,
repair, language, or bookkeeping work from implementation when prerequisites
and recovery are the same. Split source work from publication, production,
live evidence, irreversible deletion, or another external effect when their
prerequisites or recovery differ.

Before fixing that boundary, perform the smallest readiness pass capable of
checking the actual operating surface, state ownership, authority and
sensitive-data paths, delivery and verification, and recovery. Record only
findings that change the work.

A coordinate has one mutation claim. Other actors may concurrently inspect,
review, verify, monitor, or assemble evidence when those activities neither
mutate the claimed surface nor contend for shared state. Several mutation
claims may be active only when the live control proves their dependencies and
shared state independent. Shared or external mutations remain serialized
unless their authority and control identify a narrower boundary.

Every work item advances a named goal condition through a cohesive recoverable
outcome. Every additional control artifact, gate, or receipt must prevent a
named failure, carry authority, or provide evidence consumed by a later
decision. Otherwise omit it.

## Dispatch only what is ready

Only an `ACTIVE` control dispatches normal mutation. Before dispatch,
acceptance, publication, release, or external mutation, reconcile the goal,
plan, live control, tracker, canonical artifact and revision, affected
external state, applicable authority, and required evidence.

Each hard gate names exactly which mutation or downstream coordinate it
blocks. Only that action's prerequisite gates must be `SATISFIED`; an
`UNSATISFIED` gate does not freeze an explicitly authorized independent
coordinate. Distinguish artifact acceptance from permission to start
downstream work.

The authorized queue may name read-only preparation for a successor while its
predecessor is active. That preparation is provisional: it grants no successor
mutation and must be refreshed against the accepted canonical predecessor
before successor dispatch.

A passing test, healthy local state, draft receipt, or previous-head result is
evidence, not authority.

## Repair locally or replan

Keep the control `ACTIVE` when a defect remains inside the affected
coordinate's accepted outcome, authority, dependencies, external-state
boundary, acceptance criteria, and recovery boundary. Mark only its applicable
gates `UNSATISFIED`, repair under the same coordinate, and leave independent
authorized work dispatchable.

Set `STOPPED_FOR_REPLAN` only when a finding materially changes scope,
dependencies, gates, authority, controlled artifacts or systems, contracts,
external controls, acceptance criteria, or recovery. While stopped, only
read-only diagnosis, issue capture, mechanical freeze, non-mutating evidence,
and independently authorized control repair may continue. An invalidated
actor or control cannot accept its own repair or resumption.

Emergency containment does not reactivate a program. It requires separate
pre-existing authority and follows the Secrets protocol when applicable.

## Finish once

Set `COMPLETE` only when every goal condition and required receipt is
satisfied. Set `TERMINATED` when work ends with unmet goals, recording exactly
one reason: `OWNER_CANCELLED`, `ABANDONED`, `SUPERSEDED`, or `SAFETY`.

Terminal controls have no active mutation claims or dispatchable queue. A
terminated control cannot resume; later work needs a new accepted control and
applicable authority.
