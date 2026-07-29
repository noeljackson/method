# Case Study: Persistent Program Flow

This case records a generalized failure from a long-running, multi-workstream
change. Repository, organization, and infrastructure details are intentionally
omitted because they do not determine the lesson.

## Control activity must not replace outcome flow

Observation ID: `P-001`

A program retained useful exact-artifact, recovery-boundary, and live-state
controls, but treated mutation, review, verification, evidence assembly, and
successor readiness as one serial activity. Control updates accumulated while
goal completion advanced more slowly, and copied handoff state lagged the
canonical tracker.

The failure was not the presence of safety controls. Exact evidence caught real
defects. The failure was allowing control activity to become work in its own
right while safe non-mutating support waited behind the mutation claimant and
stale projections competed with live authority.

The generalized correction is narrow: a coordinate has one mutation claim
while non-mutating review, verification, monitoring, and evidence may proceed
concurrently. Named successor preparation is provisional until refreshed
against its accepted predecessor. Copies of live control identify their source
and revision. Additional ceremony without a named failure, authority purpose,
or downstream evidence consumer is omitted.
