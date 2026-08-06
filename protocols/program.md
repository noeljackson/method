# Program Protocol

Use this protocol only for persistent dependent workstreams. It adds
coordination procedure to the Runtime Kernel and grants no authority. A program
needs one live control, which may be a canonical tracker, plan block, host
state, or optional structured document.

## Keep one live control

Keep three logical concerns explicit; they may share one control or artifact:

1. **Goal state** — durable end conditions and invariants.
2. **Execution plan** — workstreams, recovery boundaries, dependencies, and
   acceptance criteria.
3. **ProgramControl** — current state, mutation claims, authorized queue,
   gates, forbidden work, and reconciliation state.

The request and canonical plan identify the live ProgramControl. A copy must
name its canonical source and revision. Superseded or stale controls are
evidence, not authority; load them only when relevant to a current claim.
Missing, ambiguous, or mismatched control identity permits read-only diagnosis
only.

## Shape and coordinate work

Bind each mutation claim once to a stable coordinate:

```text
Program / Wave / Workstream / Work Item
```

Routine actions inherit that coordinate until a material transition. Define a
work item as the smallest cohesive outcome that can be reviewed, accepted, and
recovered or withdrawn together. Do not split status, evidence, repair,
language, or bookkeeping from implementation when prerequisites and recovery
are the same. Split source from publication, production, live evidence,
irreversible deletion, or another external effect when their prerequisites or
recovery differ.

Before the first claim, perform the smallest readiness pass capable of checking
the operating surface, ownership, authority and sensitive-data paths, delivery,
verification, and recovery. Record only findings that change the work.

A coordinate has one mutation claim. Other actors may inspect, review, verify,
monitor, or assemble evidence concurrently when they neither mutate the claim
nor contend for shared state. Several claims may be active only when the live
control proves their dependencies and shared state independent. Shared or
external mutations remain serialized unless authority and control prove a
narrower boundary.

Every work item advances a named goal condition through a cohesive recoverable
outcome. Every additional control artifact, gate, or receipt must prevent a
named failure, carry authority, or provide evidence consumed by a later
decision. Otherwise omit it.

## Dispatch only what is ready

Only an `ACTIVE` control dispatches normal mutation. Reconcile at admission;
when the goal, scope, dependency, gate, authority, canonical revision, or
affected external state materially changes; and immediately before acceptance,
merge, publication, release, or external mutation. Routine actions against the
same claim and unchanged admission inherit that reconciliation.

Each hard gate names the mutation or downstream coordinate it blocks. Only
that action's gates must be `SATISFIED`; an `UNSATISFIED` gate does not freeze
an explicitly authorized independent coordinate. Distinguish artifact
acceptance from permission to start downstream work.

The queue may name read-only preparation for a successor while its predecessor
is active. That preparation is provisional: it grants no successor mutation
and must be refreshed against the accepted predecessor before dispatch.

A passing test, healthy local state, draft receipt, or previous-head result is
evidence, not authority.

## Observe passive gates by transition

Apply the Kernel's passive-gate rule to each bound Program gate. Continue
actionable authorized work while a gate is pending. When none remains,
end the current observation iteration without terminating the durable
objective. The host may resume after a transition trigger. An observer is an
aid, not authority or evidence by itself.

## Repair locally or replan

Keep the control `ACTIVE` when a defect remains inside the coordinate's
accepted outcome, authority, dependencies, external-state boundary, acceptance
criteria, and recovery. Mark only its gates `UNSATISFIED`, then repair, rebase,
retry, and verify under the same claim and admission. Leave independent
authorized work dispatchable.

Set `STOPPED_FOR_REPLAN` only when a finding materially changes scope,
dependencies, gates, authority, controlled artifacts or systems, contracts,
external controls, acceptance, or recovery. While stopped, only read-only
diagnosis, issue capture, mechanical freeze, non-mutating evidence, and
independently authorized control repair may continue. An invalidated actor or
control cannot accept its own repair or resumption.

Emergency containment does not reactivate a program. It requires separate
pre-existing authority and follows Secrets when applicable.

## Finish once

Set `COMPLETE` only when every goal condition and required receipt is satisfied.
Set `TERMINATED` when work ends with unmet goals, recording exactly one reason:
`OWNER_CANCELLED`, `ABANDONED`, `SUPERSEDED`, or `SAFETY`.

Terminal controls have no active mutation claims or dispatchable queue. A
terminated control cannot resume; later work needs a new accepted control and
applicable authority.
