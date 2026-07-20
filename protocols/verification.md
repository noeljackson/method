# Verification Protocol

Verification earns confidence in a specific claim. A collection of familiar
checks is not automatically a verification strategy.

## Define the claim and baseline

Before changing anything:

- state the behavior or invariant being tested;
- capture the current baseline;
- write the expected observation that would support or reject the hypothesis;
  and
- identify the artifact and environment.

This prevents interpreting results only after seeing them.

## Select by failure class and blast surface

Choose the cheapest check that can catch the relevant failure:

1. Static or structural checks for format, schema, or policy failures.
2. Focused unit or component checks for local behavior.
3. Bounded integration checks for contract or dependency behavior.
4. End-to-end or real-environment checks for cross-boundary behavior.
5. Broad rehearsal only when the blast surface spans the broader system.

Project profiles define the concrete selector. Local and remote verification
SHOULD consume the same classification rather than maintain competing maps.
Unknown surfaces fail toward broader active verification, not toward silence.

## Bind evidence to identity

A verification receipt identifies:

- exact input revision or artifact digest;
- generated or dependent artifact identities;
- relevant configuration and environment;
- the command, observation, or review method;
- terminal result and non-empty evidence location; and
- what newer event would supersede it.

Evidence from an earlier artifact cannot authorize a changed one. After
rebasing, regenerating, rebuilding, or redeploying, rerun the affected gate.

## Handle failure

Read the failing component's evidence first. Confirm it is non-empty before
proposing a mechanism.

Preserve failed state when it contains unique diagnostic evidence. Use a clean
environment for the next changed attempt when residue, cache, ordering, or
ambient state could contaminate comparison.

Do not rerun unchanged work solely to seek a lucky result. A retry needs an
explicit reason, such as repaired infrastructure, a changed hypothesis, or a
known nondeterministic input whose handling is itself under test.

## Report gates

Report each gate independently:

| Gate | State | Artifact | Evidence | Superseded by |
| --- | --- | --- | --- | --- |
| `<name>` | `SATISFIED` or `UNSATISFIED` | `<identity>` | `<citation>` | `<condition>` |

If a required cell is missing, the gate is `UNSATISFIED`.
