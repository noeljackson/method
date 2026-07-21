# Eval Profile: Research

Method version: `0.2.0`

## Acceptance

- Profile status: `ACCEPTED`
- Authority source: `eval-authority:research`
- Profile digest: `45c326de794977f0b51e458f2c5c4c7ba1bce60793781fa6bf01f2f934e5903c`
- Accepted by: `fixture-direction-setter`
- Accepted at: `2026-07-20T00:00:00Z`
- Acceptance receipt: `approval:research-profile-v1`

## Scope

Synthetic research decision evals only; no participant contact or publication.

## Sources of truth

1. Supplied observations and primary measurements own current facts.
2. The case contract owns the research question and gates.

Conflicts remain visible until their reconciliation method is recorded.

## Roles and actors

The fixture direction-setter owns the question; the evaluator decides gates;
the worker analyzes evidence without contacting participants or publishing.

## Work scales and taxonomy

Direct, work-item, and program thresholds follow Core. Classes include missing
evidence, measurement, analysis, inference, scope, and authority failures.

## Context flags

No protocol is forced for every fixture. Caller, profile, and model flags
combine by boolean OR. Flags select context and do not authorize mutation.

## Authority, boundaries, and gates

Workers may inspect supplied facts and propose analysis. They may not alter
real data or publish. Gates require cited observations, explicit inference,
and reproducible identity. Unknown work fails closed. One work item is one
reviewable research answer.

## Environments, tools, and secrets

Only synthetic material is in scope. `secret-ref:<name>` is the approved
non-authorizing syntax; no secret delivery is expected. Emergency authority
may stop fixture propagation only. Leak recovery requires closure, canary
evidence, and clean context. Forensic originals stay outside the fixture.
Destination-encrypted envelopes require destination-only decryption.

## Reporting and learning

Return the requested JSON. Evidence, decisions, and lessons stay in evaluator
records; no owner deviations are active.
