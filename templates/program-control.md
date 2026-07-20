# Program Control: <program>

This is the only live execution-control artifact for the program. Move
superseded controls to the decision ledger; do not stack them here.

- Program state: `<ACTIVE | STOPPED_FOR_REPLAN | COMPLETE>`
- Current coordinate: `<Program / Wave / Workstream / Work Item>`
- Accepted boundary: `<last accepted coordinate and evidence>`

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
