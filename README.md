# Noel Method

The Noel Method is a prompt-native methodology for reliable delegated work.
It is designed to be read by humans and agents, and it treats roles as
responsibilities rather than identities.

The method is intentionally layered:

- A small hard core defines the minimum discipline.
- Protocols cover sessions, multi-wave programs, verification, and
  experiments.
- A project profile supplies local vocabulary, authority, gates, and tools.
- Adapters show several ways to copy, vendor, or reference a release.
- Case studies preserve the failures that earned the rules without turning
  the core into an incident journal.

## The loop

```text
Orient -> Frame -> Evidence -> Classify -> Plan coverage
       -> Contract -> Execute -> Verify -> Report -> Learn
```

The core question is not merely, "Can this work be done?" It is:

> What evidence, authority, and acceptance contract make this the right work
> to do now?

## Start here

1. Read the generated [prompt pack](dist/NOEL-METHOD.md).
2. Choose or complete a [project profile](templates/project-profile.md).
3. Choose a consumption mode from [the adapters guide](adapters/README.md).
4. Use a [work contract](templates/work-contract.md) for substantive work.
5. For multi-wave work, also create a
   [program control](templates/program-control.md).

## Consumption options

| Mode | Best for | Trade-off |
| --- | --- | --- |
| Tagged reference | Readers and networked agents | Smallest footprint; unavailable offline |
| Single-file copy | Prompt context and small repositories | Easy to drift unless its version is recorded |
| Vendored release | Reproducible local use | Updates are explicit repository changes |
| Git subtree | Projects that want local files and upstream history | Update commands require care |
| Git submodule | Projects that want an exact upstream checkout | Adds submodule workflow overhead |

Always pin a release. A reference to mutable `main` is useful for browsing but
is not reproducible execution context.

## Repository map

- `src/` — hard core, vocabulary, workflow, and public contracts
- `protocols/` — optional operating protocols
- `templates/` — copyable project and work artifacts
- `profiles/` — software, research, and operations examples
- `adapters/` — integration and consumption snippets
- `casebook/` — evidence behind the method
- `MIGRATION.md` — source-to-method traceability
- `evals/` — decision scenarios for prompt evaluation

## Versioning

The current version is recorded in [`VERSION`](VERSION). Releases use semantic
versioning:

- Patch: clarification without a decision change.
- Minor: new optional protocol, template, or compatible field.
- Major: a hard-core rule or public contract changes meaning.

The initial `0.x` releases are for field testing. The core becomes `1.0.0`
after it has been consumed by multiple independent project profiles.

## License

[MIT](LICENSE). Copy it, adapt it, and retain the attribution.
