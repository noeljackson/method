# Example Profile: Software Repository

This example shows one possible specialization. Copy the project-profile
template rather than treating these choices as universal.

Method version: `0.1.0`

## Sources of truth

1. Current code and reproducible runtime behavior own shipped behavior.
2. Stable architecture and operational documentation own accepted intent.
3. Active plan and control documents own authorized future work.
4. The issue tracker owns work status, not implementation truth.

Conflicts are reconciled before mutation. Proposal documents do not override
current behavior merely because they are newer prose.

## Roles

One person or agent may research and execute a bounded change. Security,
destructive cleanup, release, and architecture decisions require an explicit
evaluator checkpoint. The repository owner is direction-setter for scope or
external-state changes.

## Work scales

- Direct: reversible single-surface edit with focused proof.
- Work item: one reviewable source change and its tests.
- Program: dependent migrations, multiple repositories, releases, or shared
  production state.

## Problem taxonomy

- design or invariant gap;
- implementation defect;
- ownership or authority defect;
- contract or schema drift;
- ordering, concurrency, or residue;
- harness or environment failure;
- dependency or supply-chain failure; and
- observability or evidence gap.

## Gates

Select checks from changed behavior and failure class. Prefer focused local
proof, then bounded integration, then end-to-end verification only when the
blast surface earns it. Unknown paths select the broad active gate set.

One work item maps to one pull request. Evidence from a previous head revision
does not satisfy a rebased or amended head.

## Authority

Routine source changes, tests, branches, and review artifacts are authorized
inside the work contract. Force pushes to shared history, releases,
credentials, production changes, and destructive data operations require
explicit authority.
