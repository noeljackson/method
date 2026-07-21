# Program Control: <program>

This is the only live execution-control artifact for the program. Move
superseded controls to the decision ledger; do not stack them here.

- Program state: `<ACTIVE | STOPPED_FOR_REPLAN | COMPLETE | TERMINATED>`

## Active coordinates

- `<Program / Wave / Workstream / Work Item; independence receipt>`

## Accepted frontiers

| Workstream | Maximal accepted coordinates | Evidence |
| --- | --- | --- |
| `<Program / Wave / Workstream>` | `<coordinate set>` | `<receipts>` |

## Authorized queue

1. `<coordinate and prerequisite>`

## Hard gates

| Gate | State | Required receipt | Dependent work |
| --- | --- | --- | --- |
| `<name>` | `<SATISFIED | UNSATISFIED>` | `<evidence>` | `<coordinates>` |

## Forbidden work

- <work forbidden at the current boundary>

## Canonical sources

1. <goal state>
2. <execution plan>
3. <tracker or state source>
4. <artifact source>

## Active owner decisions

- `<date>` — `<decision and affected coordinates>`

## Reconciliation receipt

- Goal and plan: `<result>`
- Workstream and tracker: `<result>`
- Canonical artifact: `<identity>`
- Evidence freshness: `<result>`
- External state: `<result>`
- Reconciled at: `<timestamp or event>`

## Stop condition

<Finding or event that requires STOPPED_FOR_REPLAN.>

## Resume condition

<Exact accepted artifact, decision, or gate needed to resume.>

## Terminal disposition

Complete only when program state is `TERMINATED`:

- Disposition: `<OWNER_CANCELLED | ABANDONED | SUPERSEDED | SAFETY>`
- Authority source, decided by, and decided at: `<provenance>`
- Decision receipt and reason: `<evidence>`
- Preserved evidence and unmet goals: `<citations>`
- External-state disposition: `<reconciled state>`
- Successor control, if superseded: `<new control or n/a>`

A terminated control cannot resume.
