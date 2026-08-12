# Migration from 0.8.5 to 0.9.0

Version 0.9.0 is a breaking pre-1 simplification. It keeps direct authority and
the Program, Experiment, and Secrets protocols. It removes unused
authority-resolution machinery, replaces parallel Program JSON with one
human-readable control, and narrows durable receipts to evidence that can
actually be lost.

Immutable 0.8 tags retain the old interfaces for historical consumers. The
exact 0.9 surface is recorded in
[`migration/public-api-0.9.0.json`](migration/public-api-0.9.0.json).

## Authority and context

Direct mode is now the only Method authority mode. Authority continues to come
from the current request and canonical project instructions; a Method document
or validator never grants it.

Retire active `ProjectPolicy`, `PolicyAuthorityRegistry`, `TaskRequest`, and
`ResolvedPermissions` documents. Do not translate them into a new Method
envelope. Move any still-needed standing rule into canonical project policy,
and keep request-specific authority in the current request.

Remove calls to:

```text
method resolve
method policy digest
method policy verify
method validate
```

Select context only with `method context` and the optional `--program`,
`--experiment`, and `--secrets` flags. Machine-readable context advances to
schema version 4 and contains selected modules and identities, not an authority
mode or permission set.

## Program controls

Replace ProgramControl JSON with one canonical tracker body based on
[`templates/program-control.md`](templates/program-control.md). Put only this
machine metadata in the opening TOML fence:

```toml
schema_version = 1
control_revision = 1
state = "ACTIVE"
coordinator = "one unambiguous primary coordinating session"
```

Add `termination_reason` only for `TERMINATED`. Preserve the previous control's
durable goal, acceptance, current frontier, dependencies, claims, gates,
boundaries, and evidence links under the required Markdown headings. Replace
superseded current state instead of copying action history. Comments and old
receipts remain linked evidence, not another live control.

Migrate an active Program at its next natural transition. Do not pause delivery
solely to change formats. Validate a body or transition with:

```sh
method program validate CONTROL.md
method program validate CONTROL.md --previous PREVIOUS.md
```

The validator checks structure, exact revision increment, and terminal lock.
It does not compare prose or authenticate coordinator
changes. The project still decides which tracker is canonical and whether its
evidence and actions are valid.

## Evidence receipts

EvidenceReceipt advances from schema version 1 to 2. Use it only when an
operation result is `ephemeral`, `destructive_output`, `secret_reduced`, or has
a `successor_gap` because ordinary durable evidence cannot preserve it.
Crossing sessions alone is insufficient. Routine status, commits, links, and
ordinary test output do not need receipts.

Replace the singular claim/result with a `claims` array. Each claim has:

- a stable `id`;
- one outcome: `SUPPORTED`, `REJECTED`, or `INCONCLUSIVE`; and
- a direct non-secret `observation`.

Record exact subject and environment identities, the procedure, durable
evidence reference, capture event, limitations, and source disposition.
Predeclare claims before an expensive, destructive, sensitive, or multi-plane
operation; that declaration alone creates no artifact. Preserve the terminal
reduced result atomically before destroying raw evidence.

Validate with:

```sh
method receipt validate RECEIPT.json
```

## CLI mapping

| 0.8 command | 0.9 replacement |
| --- | --- |
| `method context [protocol flags]` | unchanged; JSON output is schema v4 |
| `method validate program-control FILE` | `method program validate FILE` |
| `method validate evidence-receipt FILE` | `method receipt validate FILE` |
| `method validate` for other contracts | removed |
| `method policy ...` | removed; use canonical project policy |
| `method resolve ...` | removed; use direct authority |
| `method pack verify` | command retained; v0.9 enforces the v0.9 inventory, so use a matching CLI and pack |
| `method dist build` / `check` | unchanged |

Invalid contract data still exits 2; file and stream errors exit 1.

## Consumer checklist

1. Pin the published v0.9 tag, commit, and pack-manifest digest.
2. Remove active resolver commands and retired authority-contract inputs.
3. Update context JSON consumers to schema version 4.
4. Convert a Program control only at its next natural transition and keep one
   canonical tracker body.
5. Convert only still-needed fragile receipts to EvidenceReceipt v2; delete
   status-only receipt generation.
6. Verify the vendored or embedded pack and run the consumer's focused Method
   integration tests.

The v0.9 verifier intentionally rejects older pack inventories even when their
own historical manifest is internally consistent. Keep a v0.8.5 CLI with a
v0.8.5 consumer until it migrates, then pin the v0.9 CLI and pack together.
