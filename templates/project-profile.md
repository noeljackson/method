# Project Profile: <name>

Method version: `<version>`

## Scope

<What work and repositories, systems, teams, or artifacts this profile governs.>

## Sources of truth

List in precedence order and state what each source owns:

1. `<source>` — `<owned facts or decisions>`
2. `<source>` — `<owned facts or decisions>`

On conflict: `<fail, reconcile, or escalation behavior>`

## Roles and actors

| Role | Default actor | Must be separate when |
| --- | --- | --- |
| Direction-setter | `<actor>` | `<condition>` |
| Evaluator | `<actor>` | `<condition>` |
| Researcher | `<actor>` | `<condition>` |
| Executor | `<actor>` | `<condition>` |

## Work scales

- Direct task: `<local threshold>`
- Work item: `<local review/change boundary>`
- Program: `<conditions that activate program control>`

## Problem taxonomy

| Class | Diagnostic owner | Typical evidence | Structural response |
| --- | --- | --- | --- |
| `<class>` | `<role>` | `<evidence>` | `<response>` |

## Authority and forbidden actions

Actors may: `<authorized mutations>`

Actors may not: `<forbidden mutations>`

Additional approval is required for: `<conditions>`

## Work-item boundary

One work item maps to: `<PR, document, transaction, run, decision, or other reviewable unit>`

Parallel work rules: `<independence, contention, and shared-state rules>`

## Gates and evidence

| Gate | Applies when | Required evidence | Authority to accept |
| --- | --- | --- | --- |
| `<gate>` | `<selector>` | `<receipt>` | `<role>` |

Unknown or unclassified work selects: `<fail-closed behavior>`

## Environments, tools, and secrets

- Canonical environment: `<source>`
- Tool rules: `<rules>`
- Approved secret providers and opaque reference syntax: `<providers and references>`
- Approved delivery boundaries: `<how values reach only their intended process or service>`
- Forbidden secret operations and disclosure surfaces: `<rules>`
- Safe verification, redaction, and secret-scanning rules: `<rules>`
- Exposure response and rotation authority: `<owner, stop condition, and path>`
- External-state rules: `<rules>`

## Reporting and learning

- Status format: `<format>`
- Evidence destination: `<location>`
- Decisions and debt: `<location>`
- Lessons and case studies: `<location>`

## Active owner decisions

Record only decisions that specialize optional behavior. A decision that
changes the hard core must state the conflict and remain explicit.

- `<date>` — `<decision, reason, and affected contract>`
