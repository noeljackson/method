# Example Profile: Operational Change

This is an unaccepted example, not a live ProjectProfile. Copy the template and
obtain independent acceptance before relying on local authority.

Method version: `0.2.0`

## Sources of truth

1. Current live-state observations and immutable audit records.
2. Approved desired state and change control.
3. Current runbooks and ownership records.
4. Historical incident and status summaries.

A dashboard summary without underlying live evidence cannot authorize a risky
mutation.

## Roles

The evaluator owns preflight and gate interpretation. The executor performs
the approved change. High-impact, irreversible, or customer-visible changes
require separate direction-setter authority.

## Work scales

- Direct: reversible, isolated operation with immediate verification.
- Work item: one bounded change, rollback, and evidence record.
- Program: coordinated rollout across environments, teams, or release waves.

## Context flags

Program is enabled for persistent coordinated rollouts, Experiment for an
explicit controlled comparison, and Secrets for credential operations or
possible exposure. Caller, profile, and model flags combine monotonically.
Flags select context; the approved change, incident record, or separately
preauthorized containment lane supplies authority.

## Problem taxonomy

- desired-state drift;
- stale or ambiguous authority;
- dependency readiness;
- partial rollout;
- configuration or artifact mismatch;
- monitoring or evidence failure;
- capacity or performance boundary; and
- cleanup or residue.

## Gates

Preflight ties the approved change to exact target and artifact identities.
Execution has a stop condition and rollback or forward-repair path.
Post-change verification checks the user-visible invariant, not only command
success. Shared mutations are serialized unless proven safe.

## Authority

Read-only inspection is allowed by default. Deployment, data mutation,
credential changes, external communication, and destructive cleanup require a
work contract that names exact targets, recovery evidence, and a negative
authority-boundary check.

## Secrets

Secret access uses the environment's approved provider and least-privilege
delivery path. Operational evidence records only references, safe metadata,
and redacted behavioral results. Shell tracing, environment dumps,
output-producing secret reads, and secret-bearing command arguments are
forbidden. Suspected exposure makes the affected gate `UNSATISFIED` until the
owner accepts containment, credential disposition, leak-path closure, and
clean-context evidence.
