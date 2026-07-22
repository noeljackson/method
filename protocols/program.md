# Program Protocol

Use this protocol when work spans dependent waves, multiple workstreams, shared
state, or several independently reviewable changes.

## Separate target from execution

Maintain three distinct artifacts:

1. **Goal state:** durable end conditions and invariants. It says what must
   become true and stay true, not how to get there.
2. **Execution plan:** waves, workstreams, work items, dependencies, and
   acceptance criteria.
3. **Live program control:** current state, active coordinates, accepted
   frontiers, authorized queue, gates, forbidden work, and reconciliation
   receipt.

Do not append new live controls above old live controls indefinitely. There is
one authoritative control artifact; superseded controls move to a dated,
append-only decision ledger.

## Coordinate every action

Every program mutation is reported as:

```text
Program / Wave / Workstream / Work Item
```

One work item produces one reviewable change set and its evidence. If source
implementation and real-world evidence have different prerequisites, split
them into separate work items.

Several coordinates may be active when their dependency and shared-state
receipts prove independence. Maintain a set of maximal accepted coordinates
for each workstream instead of forcing concurrent work into a false total
order.

Each workstream names its execution context, canonical baseline, and any
shared mutable resources. Reconcile a reused context before dispatch. A local
context is evidence about state, not authority to mutate, publish, or merge;
unaccepted residue from another lane cannot seed a new coordinate.

## Dispatch gate

Before dispatching, publishing, merging, releasing, or performing an external
mutation, reconcile:

- goal and invariants;
- execution plan and live program control;
- workstream status and tracker;
- canonical artifact or branch;
- applicable evidence and its exact revision;
- external state affected by the action; and
- the project profile's authority rules.

Record this as the reconciliation receipt. Healthy local state or a passing
test is not authorization by itself.

## Gates and queues

- A work item may start only when its named gates are `SATISFIED`.
- Later-wave work is forbidden while an earlier hard gate is `UNSATISFIED`.
- Same-wave preparation is allowed only when the live control names it and its
  prerequisites.
- Mutations to shared or external state are serialized unless the contract
  proves concurrency safe.
- Cleanup, retention, and handoff for temporary execution contexts are named
  in the work item or shared-resource receipt when they affect evidence,
  safety, or later work.
- A useful discovery stays in its lane until the plan assigns it a coordinate.

## Replan

Set program state to `STOPPED_FOR_REPLAN` when a new finding changes scope,
dependencies, gates, authority, repositories, contracts, external controls, or
acceptance criteria.

While stopped:

- read-only diagnosis and issue capture may continue;
- only the plan repair explicitly authorized by the live control may mutate
  program artifacts; and
- unrelated productive work does not become authorized merely because the
  original lane is stopped.

An emergency does not reactivate the stopped lane. Least-harm containment may
proceed only under separate pre-existing authority and an incident work
contract that records its own authority receipt, scope, evidence, and stop
condition. The program remains `STOPPED_FOR_REPLAN` until its repaired control
is accepted.

Resume only after the repaired control is accepted and its resume condition is
met.

## Complete

Set state to `COMPLETE` only when every goal-state condition is true and every
required receipt is attached. Near-completion is still `ACTIVE` with remaining
gates `UNSATISFIED`.

## Terminate

Set state to `TERMINATED` when the program ends without satisfying every goal.
Record exactly one disposition: `OWNER_CANCELLED`, `ABANDONED`, `SUPERSEDED`,
or `SAFETY`. The terminal receipt names the authority source, decision actor
and time, reason, unmet goals, preserved evidence, external-state disposition,
and successor control when superseded.

A terminated control cannot resume. Later work needs a new accepted live
control and cannot inherit authority from the terminal one.
