# Noel Method

The Noel Method is a prompt-native methodology for reliable delegated work.
It is designed to be read by humans and agents, and it treats roles as
responsibilities rather than identities.

The method is intentionally layered:

- A compact Base defines the non-waivable core, workflow, and common contracts.
- Optional protocols cover programs, experiments, and secret-bearing work.
- A project profile supplies local vocabulary, authority, gates, and tools.
- Adapters show several ways to copy, vendor, or reference a release.
- Case studies preserve the failures that earned the rules without turning
  the core into an incident journal.

## Quick install

From the root of the repository that will use the Method, run:

```sh
git subtree add --prefix=vendor/noel-method https://github.com/noeljackson/method.git v0.2.0 --squash
```

That installs the pinned release as local files. Then create the local profile
without overwriting an existing one:

```sh
test ! -e PROJECT-PROFILE.md && cp vendor/noel-method/templates/project-profile.md PROJECT-PROFILE.md
```

The Method is not active until an independent owner accepts that profile. For
the short setup walkthrough, including profile acceptance and everyday use,
read [Getting started](GETTING-STARTED.md). Other installation modes are in
the [adapter guide](adapters/README.md).

## The loop

```text
Orient and frame -> Gather and classify -> Check plan coverage
                 -> Contract -> Act -> Verify -> Report and learn
```

The core question is not merely, "Can this work be done?" It is:

> What evidence, authority, and acceptance contract make this the right work
> to do now?

## Once installed

1. Open the modular pack's [index](dist/pack/INDEX.md) from your pinned local
   copy or tagged remote reference.
2. Always load its Base and an independently accepted local project profile.
3. OR the caller, profile, and model ContextFlags and load enabled protocols.
4. Use the [full prompt pack](dist/NOEL-METHOD.md) only when the consumer
   cannot follow linked local files.
5. Use a [work contract](templates/work-contract.md) for substantive work.
6. For multi-wave work, also create a
   [program control](templates/program-control.md).

The modular pack is optimized for repeated agent use: `INDEX.md`, `BASE.md`,
and the local profile form the normal context. The three non-authoritative
flags—`program`, `experiment`, and `secrets`—only add context. They never grant
authority, and no source may use `false` to clear another source's `true`.

## Everyday use

Most routine work should stay light. For a bounded, reversible direct task,
the prompt can be its contract:

```text
Outcome: <what should be true next>
Constraints: <boundaries and non-goals>
Evidence: <current source of truth or check>
Next action: <one bounded step>
```

Use a formal [work contract](templates/work-contract.md) only when work is
substantive: it changes external or irreversible state, handles sensitive
material, crosses a meaningful handoff or authority boundary, or has material
uncertainty about success. An accepted ProjectProfile is workspace setup for
its scope and revision; it is not recreated for every task.

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
- `audits/` — dated release-readiness and security-tool reports
- `MIGRATION.md` — source-to-method traceability
- `evals/` — bounded adversarial context and decision evaluation

## Versioning

The current version is recorded in [`VERSION`](VERSION). Releases use semantic
versioning:

- Patch: clarification without a decision change.
- Minor: new optional protocol, template, or compatible field.
- Major: a hard-core rule or public contract changes meaning.

Before `1.0.0`, a minor release MAY make a breaking hard-core, public-contract,
or context-loading change when the changelog names it and `MIGRATION.md`
supplies an explicit path. A pre-1 patch remains wording-only. From `1.0.0`
onward, the major-change rule above applies without this exception. The core
becomes `1.0.0` after it has been consumed by multiple independently accepted
profiles.

## License

[MIT](LICENSE). Copy it, adapt it, and retain the attribution.
