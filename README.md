# Noel Method

The Noel Method is a compact way for a person and a delegated agent to work
together like senior teammates. It keeps attention on five questions:

1. What outcome does the human want?
2. What is true now, and what is only inferred?
3. What is the smallest safe next action?
4. What evidence would change the next decision?
5. What genuinely needs the human?

The normative Method is the Markdown in [`src/`](src/) and
[`protocols/`](protocols/). The CLI, templates, schemas, and generated pack are
optional aids. They do not grant authority, schedule work, retain state, or
replace project instructions.

## Use it

Start with the [Kernel](src/KERNEL.md). Direct mode is the only authority mode:
the current request and canonical project instructions define what may happen.
Normal work needs no Method artifact.

Load an optional protocol only when its task signal is present:

- [Program](protocols/program.md) for persistent dependent work across
  sessions, repositories, or operational gates;
- [Experiment](protocols/experiment.md) for a controlled comparison; and
- [Secrets](protocols/secrets.md) when the actor or a local process can access
  secret material.

Protocols add procedure, never permission. Several steps, a remote service, or
a long conversation do not by themselves select Program.

The optional CLI returns the exact verified modules:

```sh
method context
method context --program --secrets
method context --experiment --format json
```

The Markdown output is ready to inject into an agent's instruction context.
The JSON form identifies each selected module and digest without inventing an
authorization envelope.

## Human and machine controls

Most tasks stay conversational. A persistent Program uses one human-readable
tracker body: a small TOML metadata header followed by `Goal`, `Done when`,
`Current`, `Next`, `Needs from human`, `Boundaries`, and `Evidence`. The body is
both the human control and the machine-checkable control; do not maintain a
second JSON copy.

```sh
method program validate CONTROL.md
method program validate CONTROL.md --previous PREVIOUS.md
```

Ordinary commits, links, and test output are ordinary evidence. Use the JSON
[EvidenceReceipt](templates/evidence-receipt.json) only when an operation result
can be lost, destroyed, reduced to protect secrets, or cannot be preserved for
a successor through ordinary durable evidence. Crossing sessions alone is not
a durability reason:

```sh
method receipt validate RECEIPT.json
```

Each declared claim is classified `SUPPORTED`, `REJECTED`, or `INCONCLUSIVE`.
Predeclaring claims creates no artifact. A receipt is terminal output that
preserves a decision-bearing result, not a status ritual or authority token.

## Install and verify

When the optional crate is published, install it with:

```sh
cargo install noel-method --locked --version 0.9.2
method version --json
method pack verify
```

Release archives provide native `method` binaries for Linux, macOS, and
Windows with a `SHA256SUMS` file and are the canonical binary distribution.
To build the current checkout:

```sh
cargo install --path . --locked
```

Bind a separately downloaded or vendored pack to the manifest digest recorded
by the consumer:

```sh
method pack verify vendor/noel-method/dist/pack \
  --expect-manifest-sha256 "$EXPECTED_SHA256"
```

JSON-reading commands accept `-` for standard input. Invalid contract data
exits with status 2; file and stream errors exit with status 1.

## Develop and distribute

The repository has no Python runtime or test dependency. Regenerate or verify
the checked-in distribution with Rust:

```sh
method dist build
method dist check
cargo test --all-targets
```

Published surfaces are:

- `dist/pack/` — progressively loaded runtime pack;
- `dist/MONOLITH.md` — one-file fallback with every protocol;
- `method` / `noel-method` — optional stateless tooling;
- `src/` and `protocols/` — normative source;
- `schemas/` and `templates/` — optional Program and evidence contracts;
- `casebook/` and [`MIGRATION.md`](MIGRATION.md) — rationale and traceability;
- `evals/` — deterministic decision fixtures and historical evaluation data.

For subtree, submodule, remote, and single-file consumption, see the
[adapter guide](adapters/README.md). Use a published tag, never mutable `main`.

Before `1.0.0`, a minor release may make a breaking interface or decision
change when the changelog and migration guide name it. Patch releases clarify
wording without changing decisions.

## License

[MIT](LICENSE).
