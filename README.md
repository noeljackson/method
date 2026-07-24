# Noel Method

The Noel Method is a small runtime discipline for delegated work: observe the
real state, bound authority, take the smallest useful action, verify the exact
claim, and report what others may rely on.

## When to use it

Use the [Kernel](src/KERNEL.md) for any delegated task where a wrong answer or
action would cost more than a quick correction. That includes most repository
changes, operational diagnosis, and evidence-backed research.

Direct authority mode is the default. The current request and canonical
project instructions are the boundary; normal chat creates no Method-specific
artifact. A concise request may be enough:

```text
Outcome: fix the parser defect.
Scope: parser source and focused tests.
Forbidden: publish, deploy, access credentials.
Evidence: the focused test must pass on the changed revision.
```

External or persistent work does not automatically change the authority mode.
A project may declare a bounded edit, check, commit, push, review, and merge
lifecycle direct. Release, deploy, production mutation, and credential access
remain separately controlled by the request and project.

Load optional protocols by task shape:

- [Program](protocols/program.md) for persistent dependent work;
- [Experiment](protocols/experiment.md) for a controlled comparison; and
- [Secrets](protocols/secrets.md) for a secret-capable path.

Protocols add procedure, never permission.

## Two adoption levels

### 1. Direct mode

Copy or reference `dist/pack/KERNEL.md` in the agent instructions. Keep normal
task prompts short. Load Program, Experiment, or Secrets only when the task
actually has that risk. This is the minimum useful adoption path.

The optional `method` CLI embeds the verified pack and makes this easy for a
human, an agent, or a host:

```sh
# Kernel only
method context

# Kernel plus task-shaped procedure
method context --program --secrets

# Stable machine-readable module content and identities
method context --experiment --format json
```

The Markdown output is ready to inject into an LLM's instruction context.
An agent may run the command itself when it can load local instructions. The
CLI remains stateless: it assembles context and checks data, but it does not
create an authorization session, broker tools, or turn a model request into
permission.

### 2. Optional resolved mode

Use resolved mode only when the project, current request, or consuming host
explicitly selects it. The host authenticates the caller, protects an accepted
[ProjectPolicy](templates/project-policy.json), binds a
[TaskRequest](templates/task-request.json) to the approved conversation, and
computes [ResolvedPermissions](schemas/resolved-permissions.schema.json):

```sh
method resolve \
  --policy PROJECT-POLICY.json \
  --authorities POLICY-AUTHORITIES.json \
  --task TASK-REQUEST.json > RESOLVED-PERMISSIONS.json

method context \
  --task TASK-REQUEST.json \
  --permissions RESOLVED-PERMISSIONS.json
```

Policy acceptance is an owner or host operation, not a model task:

1. Copy and edit `templates/project-policy.json` while its status is `draft`.
2. Compute its digest with `method policy digest PROJECT-POLICY.json`.
3. An independent owner records that digest and acceptance metadata using
   `templates/policy-authorities.json`, then puts the same receipt ID and
   metadata in the policy and changes its status to `accepted`.
4. Run `method policy verify PROJECT-POLICY.json --authorities
   POLICY-AUTHORITIES.json` before resolving tasks.

Changing policy invalidates the digest. Changing acceptance metadata without
an exact matching external receipt also fails. Keep the authority registry
outside model write authority.

The resolver rejects draft or altered policies, unknown actions and gates, and
attempts to weaken protocol selection. It proves consistency, not caller
identity or enforcement. The host remains responsible for authenticating the
request, protecting inputs, supplying TaskRequest and ResolvedPermissions to
the model, and restricting tools when enforcement is required.

The LLM can use `method validate`, `method context`, and additional monotonic
protocol flags. It must not author its own accepted policy, authority receipt,
or trusted TaskRequest. Resolved mode is useful at an actual host boundary—
for example, a service translating authenticated user intent into constrained
tools—not as extra paperwork inside an ordinary chat.

When Program is selected, the harness must also supply the current
ProgramControl named by a non-authorizing TaskRequest reference. Structural
validation does not prove that a control is live or authoritative; reconcile
that identity against canonical project state.

## Install the CLI

Install the published crate:

```sh
cargo install noel-method --locked --version 0.5.0
method version --json
method pack verify
```

Release archives provide native `method` binaries for Linux, macOS, and
Windows with a `SHA256SUMS` file. To build the current checkout instead:

```sh
cargo install --path . --locked
```

For a separately downloaded or vendored pack, bind verification to the
manifest digest recorded by the consuming project or release:

```sh
method pack verify vendor/noel-method/dist/pack \
  --expect-manifest-sha256 "$EXPECTED_SHA256"
```

All JSON-reading commands accept `-` for standard input. Validation supports
`project-policy`, `policy-authorities`, `task-request`,
`resolved-permissions`, `program-control`, and `evidence-receipt`:

```sh
method validate task-request TASK-REQUEST.json --json
method validate evidence-receipt - --json < EVIDENCE-RECEIPT.json
```

Invalid data exits with status 2; file and stream errors exit with status 1.
The runtime pack contains no executable fallback: use the matching `method`
release for resolved-mode validation and resolution.

## Development

The repository has no Python runtime or test dependency. Regenerate or verify
the checked-in distribution with Rust:

```sh
method dist build
method dist check
cargo test --all-targets
```

## Distribution

- `dist/pack/` — recommended progressively loaded pack
- `dist/MONOLITH.md` — all normative runtime text for one-file systems
- `method` / the `noel-method` crate — optional stateless runtime tooling
- `src/` and `protocols/` — normative source
- `schemas/` and `templates/` — optional resolved-mode contracts
- `policies/` — draft examples, not accepted authority
- `casebook/` and `MIGRATION.md` — rationale and source traceability
- `evals/` — sparse, opt-in decision smoke test

For subtree, submodule, remote, and single-file consumption, see the
[adapter guide](adapters/README.md). Use an existing release tag; never treat
the `VERSION` in an unreleased checkout as a published tag.

## Versioning

The current version is in [`VERSION`](VERSION). Before `1.0.0`, a minor release
may make a breaking decision or contract change when the changelog and
migration guide name it. Patch releases clarify wording without changing
decisions.

## License

[MIT](LICENSE).
