# Program Protocol

Use Program for persistent dependent work across sessions, repositories, or
operational gates. Several steps alone do not select it. It adds coordination,
never authority.

## One human control

Use one canonical tracker body for the Program control. Its fenced TOML header
contains `schema_version`, positive `control_revision`, `state`, and one
unambiguous `coordinator`; add `termination_reason` only for `TERMINATED`.
Follow it with `Goal`, `Done when`, `Current`, `Next`, `Needs from human`,
`Boundaries`, and `Evidence`, in that order.

Only the named coordinator revises the body. Increment its revision once per
material change to state, coordinator, frontier, claims, gates, next action,
or human need. Routine actions and evidence-only additions need no revision.
Replace superseded state and link evidence. Local copies, comments, host goals,
and timers supply context but cannot change live control or block work.

## Dispatch cohesive outcomes

While `ACTIVE`, pursue authorized deliverables with observable acceptance.
`Current` names relevant claims, dependencies, and gates; `Next` names the
immediate action, awaited transition, or decision. Keep future work at dependency
level until its decisions affect the next action.

Bind collision-prone mutations once to stable coordinates. Routine repair,
verification, and delivery inherit unchanged claims. Split work only for different
owners, dependencies, acceptance, external effects, or recovery boundaries.
Keep status, evidence, and bookkeeping with their deliverable.

Inspect only unresolved facts that can change the next action's design,
ownership, verification, acceptance, or recovery. Reconcile control at admission,
material change, merge, or an external result affecting the frontier, gates, or
recovery. Reuse unchanged decisions between those transitions.

Apply each gate only to the actions it blocks. A future permission or downstream
gate does not block current work. Continue authorized work whose dependencies
and shared-state boundaries establish independence, including while a passive
gate runs.

## Repair without ceremony

Keep `ACTIVE` when a defect, failed approach, or missing observation remains
within accepted scope, dependencies, contracts, external effects, acceptance,
recovery, and authority. Mark the affected acceptance claim unsatisfied and
update its gate if one exists. Localize, repair, and verify under the existing
claim; an issue or failed attempt does not finish the objective.

Set `STOPPED_FOR_REPLAN` for a material change to those boundaries. Hold that
Program's mutations; read-only diagnosis and independently authorized control
repair may continue. Resume under accepted control and applicable authority.
Separately authorized work outside the stopped Program continues.

Put a question under `Needs from human` when the immediate next useful action
needs a material decision or missing authority. Answer status questions and
criticism while continuing, unless the human directs a pause or scope change.

## Evidence and completion

Use ordinary results and links as evidence. Use one EvidenceReceipt only when
the result can disappear, must be reduced before destruction, or cannot reach
a successor through ordinary durable evidence. Crossing sessions alone is
insufficient. Predeclare claims without another artifact; preserve the terminal
receipt atomically before discarding raw output.

Set `COMPLETE` only when `Done when` and required checks are satisfied. When
ending with unmet goals, use `TERMINATED` with reason `OWNER_CANCELLED`,
`SUPERSEDED`, or `SAFETY`.
Supersession transfers ownership without invalidating accepted work or evidence.
Terminal controls have `Next: None` and cannot resume. Migrate formats at a
natural transition without pausing delivery solely for migration.
