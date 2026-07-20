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

1. Open the modular pack's [index](dist/pack/INDEX.md).
2. Always load its core and a completed local project profile.
3. Follow the index only to modules whose trigger applies.
4. Use the [full prompt pack](dist/NOEL-METHOD.md) only when the consumer
   cannot follow linked local files.
5. Choose or complete a [project profile](templates/project-profile.md).
6. Choose a consumption mode from [the adapters guide](adapters/README.md).
7. Use a [work contract](templates/work-contract.md) for substantive work.
8. For multi-wave work, also create a
   [program control](templates/program-control.md).

The modular pack is optimized for repeated agent use: `INDEX.md`, `CORE.md`,
and the local profile form the minimum context. Workflow, protocol, and
contract modules are loaded by trigger rather than on every turn.

## Consumption options

| Mode | Best for | Trade-off |
| --- | --- | --- |
| Tagged reference | Readers and networked agents | Smallest footprint; unavailable offline |
| Modular copy | Repeated agent use | Best context efficiency; preserve relative links |
| Single-file copy | One-document prompt systems | Broadest context on every use |
| Vendored release | Reproducible local use | Updates are explicit repository changes |
| Git subtree | Projects that want local files and upstream history | Update commands require care |
| Git submodule | Projects that want an exact upstream checkout | Adds submodule workflow overhead |

Always pin a release. A reference to mutable `main` is useful for browsing but
is not reproducible execution context.

## Repository map

- `dist/pack/` — recommended linked, progressively loaded distribution
- `dist/NOEL-METHOD.md` — single-file compatibility distribution
- `src/` — hard core, vocabulary, workflow, and public contracts
- `protocols/` — optional operating protocols
- `templates/` — copyable project and work artifacts
- `profiles/` — software, research, and operations examples
- `adapters/` — integration and consumption snippets
- `casebook/` — evidence behind the method
- `MIGRATION.md` — source-to-method traceability
- `evals/` — generic, incident-derived, and synthetic decision scenarios

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
