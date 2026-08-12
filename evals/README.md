# Decision Scenarios

[`scenarios.json`](scenarios.json) is the active v0.9 decision corpus. Each
fixture names a situation, the proportionate safe behavior, and the behavior
the Method must not induce. It is a searchable regression library, not a
mandatory per-release study. Review only scenarios cited by changed provenance
plus the `tentative-assent-bounded`, `secret-requested-in-prompt`, and
`stale-revision-evidence` sentinels.

The scenarios are not a statistical model evaluation and are not an excuse to
add a second policy or control system. Functional behavior belongs in ordinary
code and contract tests. Historical batches and reports remain immutable
evidence of earlier Method development and are not v0.9 release gates.
Other pre-v0.9 evaluation JSON is historical source data; current tools route
only `scenarios.json`.
