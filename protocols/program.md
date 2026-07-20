# Program Protocol

Use this protocol when work spans dependent waves, multiple workstreams, shared
state, or several independently reviewable changes.

## Separate target from execution

Maintain three distinct artifacts:

1. **Goal state:** durable end conditions and invariants. It says what must
   become true and stay true, not how to get there.
2. **Execution plan:** waves, workstreams, work items, dependencies, and
   acceptance criteria.
3. **Live program control:** current state, coordinate, authorized queue,
   gates, forbidden work, and reconciliation receipt.

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

Resume only after the repaired control is accepted and its resume condition is
met.

## Complete

Set state to `COMPLETE` only when every goal-state condition is true and every
required receipt is attached. Near-completion is still `ACTIVE` with remaining
gates `UNSATISFIED`.
