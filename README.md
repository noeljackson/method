# Noel Method

The Noel Method helps people and agents do delegated work with clear authority,
small evidence-based steps, and explicit acceptance.

## Quick install

From the root of the repository that will use the Method, run:

```sh
git subtree add --prefix=vendor/noel-method https://github.com/noeljackson/method.git v0.2.0 --squash
```

That installs the pinned release as local files. Then create the project’s
local profile without overwriting an existing one:

```sh
test ! -e PROJECT-PROFILE.md && cp vendor/noel-method/templates/project-profile.md PROJECT-PROFILE.md
```

## Set up the ProjectProfile

A ProjectProfile is a small local policy file for this repository. It names
the sources of truth, who may decide or act, the important boundaries and
gates, and where results are reported. It is the project-specific companion to
the general Method.

Fill in [the copied template](templates/project-profile.md). While it is
`DRAFT`, it grants no mutation authority. An independent owner accepts its
exact contents once it is correct. Usually you set it up once for a repository,
then reaccept it only when its authority or scope changes.

## Everyday use

For each task, tell the agent to start with the installed pack’s
`vendor/noel-method/dist/pack/INDEX.md` and this repository’s accepted
`PROJECT-PROFILE.md`.

Most routine work needs only a short request:

```text
Outcome: <what should be true next>
Constraints: <boundaries and non-goals>
Evidence: <current source of truth or check>
Next action: <one bounded step>
```

Use a [WorkContract](templates/work-contract.md) when work changes external or
irreversible state, handles sensitive material, crosses an authority boundary,
or has material uncertainty. The index adds the Program, Experiment, or
Secrets protocol only when that kind of work applies.

## Need another installation mode?

The local subtree above is the recommended default. For a remote reference,
single-file prompt, submodule, or update procedure, use the
[adapter guide](adapters/README.md). Always pin a release rather than using
mutable `main`.

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
