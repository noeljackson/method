# Vocabulary and Roles

Stable vocabulary makes prompts, plans, and reports interoperable.

## Roles

Roles are responsibilities. A project profile maps them to people or agents and
decides when separate actors are required.

- **Direction-setter:** chooses the outcome, supplies authority, and decides
  trade-offs that change scope or commitments.
- **Evaluator:** frames work, checks evidence, maintains the contract, detects
  drift, interprets gates, and decides when the method determines a pivot.
- **Researcher:** gathers and analyzes evidence without performing the target
  mutation unless the contract explicitly grants it.
- **Executor:** produces the deliverable and verification evidence within the
  work contract.

One actor MAY hold multiple roles for lower-risk work. The role change should
be explicit at evaluation boundaries so self-evaluation is not mistaken for
independent evidence.

## Work scales

- **Direct task:** bounded, reversible, low-blast work with an obvious local
  proof. The prompt may serve as its contract.
- **Work item:** one reviewable outcome with its own contract, change set, and
  acceptance evidence.
- **Program:** multiple dependent work items organized into waves and
  workstreams with execution control.

## Program coordinate

A program coordinate is written:

```text
Program / Wave / Workstream / Work Item
```

Every mutating action in a program belongs to one authorized coordinate.

## Program and gate state

Program state is exactly one of:

- `ACTIVE` — work may execute only at authorized coordinates whose gates are
  satisfied.
- `STOPPED_FOR_REPLAN` — mutations are stopped while the controlling contract
  is repaired.
- `COMPLETE` — all end-state conditions and evidence are satisfied.

Gate state is exactly one of:

- `SATISFIED`
- `UNSATISFIED`

An external wait does not need another program state. The program remains
`ACTIVE` with the relevant gate `UNSATISFIED`, which forbids dependent work.

## Evidence terms

- **Observation:** what was directly seen or measured.
- **Inference:** a conclusion derived from observations.
- **Claim:** a statement the work asks others to trust.
- **Gate:** a named condition with required evidence.
- **Receipt:** evidence tying a gate result to an exact artifact and
  environment.
- **Accepted boundary:** the last coordinate whose output and evidence are
  authoritative.
- **Proposal debt:** unvalidated proposals that compete for attention without
  increasing confidence.
