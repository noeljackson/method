# Vocabulary and Roles

Roles are responsibilities. A profile maps them to actors and decides when
separation is required.

- **Direction-setter:** chooses outcomes and supplies authority.
- **Evaluator:** frames work, checks evidence, maintains contracts, and reads
  gates.
- **Researcher:** gathers evidence without target mutation unless authorized.
- **Executor:** produces the deliverable and verification evidence.

One actor MAY hold several roles for lower-risk work, but should mark role
changes at evaluation boundaries.

A **direct task** is bounded, reversible, and locally provable. A **work item**
has one reviewable outcome. A **program** has persistent dependent workstreams
and explicit execution control.

A disposition is exactly `PROCEED`, `HOLD`, `CONTAIN`, or `TERMINATE`.

Program state is exactly `ACTIVE`, `STOPPED_FOR_REPLAN`, `COMPLETE`, or
`TERMINATED`. A terminated program records `OWNER_CANCELLED`, `ABANDONED`,
`SUPERSEDED`, or `SAFETY` and cannot resume. Gate state is exactly `SATISFIED`
or `UNSATISFIED`.

An **observation** was directly seen; an **inference** is derived; a **claim**
is what others are asked to trust; a **gate** is a condition with required
evidence; a **receipt** binds a result to an exact artifact and environment.

An **approved secret reference** is non-secret, non-authorizing, and safe for
its audience. A **clean context** never received an exposed value and inherits
none of its transcript, tool output, process state, or unsafe logging path.
