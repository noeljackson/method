# Decision Scenarios

`scenarios.json` contains small situations with expected and forbidden method
decisions. They serve two purposes:

1. Deterministic checks ensure the scenario interface remains complete.
2. A prompt evaluation can attach `dist/NOEL-METHOD.md`, present each
   situation, and compare the response with `expected` and `forbidden`.

The scenarios test decisions, not exact wording. Before a release that changes
the hard core, record a human review and at least one agent run in the release
notes. Model-specific scoring infrastructure is intentionally outside v0.1.
