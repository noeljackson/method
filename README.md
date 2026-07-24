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

### 1. Prompt-only

Copy or reference `dist/pack/KERNEL.md` in the agent instructions. Keep normal
task prompts short. Load Program, Experiment, or Secrets only when the task
actually has that risk. This is the minimum useful adoption path.

### 2. Optional resolved mode

Use resolved mode only when the project, current request, or consuming host
explicitly selects it. The host authenticates the caller, protects an accepted
[ProjectPolicy](templates/project-policy.json), binds a
[TaskRequest](templates/task-request.json) to the approved conversation, and
computes [ResolvedPermissions](schemas/resolved-permissions.schema.json):

```sh
python3 dist/pack/tools/noel_method.py resolve \
  --policy PROJECT-POLICY.json \
  --authorities POLICY-AUTHORITIES.json \
  --task TASK-REQUEST.json
```

Policy acceptance is an owner or host operation, not a model task:

1. Copy and edit `templates/project-policy.json` while its status is `draft`.
2. Compute its digest with `noel_method.py policy-digest`.
3. An independent owner records that digest and acceptance metadata using
   `templates/policy-authorities.json`, then puts the same receipt ID and
   metadata in the policy and changes its status to `accepted`.
4. Run `noel_method.py verify-policy` before resolving tasks.

Changing policy invalidates the digest. Changing acceptance metadata without
an exact matching external receipt also fails. Keep the authority registry
outside model write authority.

The resolver rejects draft or altered policies, unknown actions and gates, and
attempts to weaken protocol selection. It proves consistency, not caller
identity or enforcement. The host remains responsible for authenticating the
request, protecting inputs, supplying TaskRequest and ResolvedPermissions to
the model, and restricting tools when enforcement is required.

When Program is selected, the harness must also supply the current
ProgramControl named by a non-authorizing TaskRequest reference. Structural
validation does not prove that a control is live or authoritative; reconcile
that identity against canonical project state.

## Distribution

- `dist/pack/` — recommended progressively loaded pack
- `dist/MONOLITH.md` — all normative runtime text for one-file systems
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
