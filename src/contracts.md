# Runtime Contracts

Direct work requires no Method-specific document. The Method publishes only
two optional control contracts: one human-readable Program body and one JSON
receipt for fragile evidence. Neither contract grants authority.

## Program control

A Program has one canonical tracker body. Its first content is a fenced TOML
block with exactly:

- `schema_version = 1`;
- a positive `control_revision`;
- `state` as `ACTIVE`, `STOPPED_FOR_REPLAN`, `COMPLETE`, or `TERMINATED`;
- one unambiguous primary `coordinator`; and
- `termination_reason` only when terminated, as `OWNER_CANCELLED`,
  `SUPERSEDED`, or `SAFETY`.

The body then has these Markdown headings exactly once and in order: `Goal`,
`Done when`, `Current`, `Next`, `Needs from human`, `Boundaries`, and
`Evidence`. Outside fenced code, the control dialect allows only those ATX H2
headings and optional H3-or-deeper subsections. H1, Setext headings, raw HTML
H1/H2, and ambiguous backtick fences are invalid. This hybrid is the human and
machine interface. Do not maintain a second live JSON control.

Only the named coordinator revises the body. Increment `control_revision` once
when live state, coordinator, frontier, claims, gates, `Next`, or human need
materially changes, not for a routine action or evidence-only addition. An
optional validator may compare revisions. It checks structure, exact revision
increment, and terminal lock. It does not compare prose, prove that a
tracker is canonical, authenticate a coordinator transfer, establish evidence,
or authorize an action.

Comments, commits, pull requests, host goals, and local copies may supply
evidence or scheduling, but cannot change Program state. Migrate an active
older control at its next natural transition instead of pausing delivery just
to change formats.

## EvidenceReceipt

Use an EvidenceReceipt only when an expensive, destructive, sensitive, or
multi-plane result can disappear, must be reduced before raw material is
destroyed, or cannot survive for a successor in ordinary durable evidence.
Crossing sessions alone is insufficient. Ordinary test output, commits, and
links remain ordinary evidence.

Version 2 records:

- why durability is needed: `ephemeral`, `destructive_output`,
  `secret_reduced`, or `successor_gap` when ordinary durable evidence cannot
  preserve the result for a successor;
- the exact subject and environment identities;
- the bounded procedure;
- one or more predeclared claims;
- the durable non-secret evidence reference and capture event;
- material limitations and any superseded receipt; and
- whether raw source was non-sensitive, retained protected, or reduced and
  destroyed.

Each claim has a stable identifier, direct non-secret observation, and exactly
one outcome: `SUPPORTED`, `REJECTED`, or `INCONCLUSIVE`. Predeclaring claims
alone creates no artifact; the receipt is terminal operation output, not
admission or attempt narration. A broad label cannot erase which claim failed,
and duplicate attestations do not strengthen one boundary.

The JSON Schema and native validator check shape and internal consistency.
They do not prove the observation, authenticate the author, or authorize a
follow-up action. JSON Schema checks each item; the native validator also
enforces unique claim identifiers and non-whitespace text.
