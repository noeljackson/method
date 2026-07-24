# Noel Method

The Noel Method is a small runtime discipline for delegated work: observe the
real state, bound authority, take the smallest useful action, verify the exact
claim, and report what others may rely on.

## When to use it

Use the [Kernel](src/KERNEL.md) for any delegated task where a wrong answer or
action would cost more than a quick correction. That includes most repository
changes, operational diagnosis, and evidence-backed research.

Do **not** create method artifacts for a question, inspection, or small
reversible change under direct human supervision. A concise request is enough:

```text
Outcome: fix the parser defect.
Scope: parser source and focused tests.
Forbidden: publish, deploy, access credentials.
Evidence: the focused test must pass on the changed revision.
```

Use a verified RuntimeEnvelope only when work crosses that direct boundary:
external or irreversible mutation, sensitive-material risk, an authority
crossing, persistent coordinated work, or delegated mutation through material
uncertainty. Multiple local steps alone are not a trigger. The envelope is
produced by a trusted resolver; the model does not author it.

A human-readable excerpt may look like:

```json
{
  "profile_verified": true,
  "authority": ["edit repository files", "run local checks"],
  "forbidden": ["publish", "deploy", "access credentials"],
  "protocols": [],
  "required_gates": ["focused-tests"]
}
```

For that example, no Noel protocol is needed: it is a standard bounded change.
If a repository calls its own workflow `standard-change`, that is a local
adapter, not a universal Noel protocol. The full machine envelope also binds
the task, accepted policy receipt, gate definitions, and relevant controls.

## Two adoption levels

### 1. Prompt-only

Copy or reference `dist/pack/KERNEL.md` in the agent instructions. Keep normal
task prompts short. Load Program, Experiment, or Secrets only when the task
actually has that risk. This is the minimum useful adoption path.

### 2. Guarded runner

For consequential work outside the direct boundary, accept a
[ProjectProfile](templates/project-profile.json) once per policy revision,
create a [TaskRequest](templates/task-request.json), and resolve the compact
runtime guardrail:

```sh
python3 dist/pack/tools/noel_method.py resolve \
  --profile PROJECT-PROFILE.json \
  --authorities PROFILE-AUTHORITIES.json \
  --task TASK-REQUEST.json
```

Profile acceptance is an owner operation, not a model task:

1. Copy and edit `templates/project-profile.json` while its status is `draft`.
2. Compute its policy digest with `noel_method.py profile-digest`.
3. An independent owner records that digest and acceptance metadata using
   `templates/profile-authorities.json`, then puts the same receipt ID and
   metadata in the profile and changes its status to `accepted`.
4. Run `noel_method.py verify-profile` before resolving tasks.

Changing policy invalidates the digest. Changing acceptance metadata without
an exact matching external receipt also fails. Keep the authority registry
outside model write authority.

The resolver rejects draft or altered profiles, unknown actions and gates, and
attempts to weaken protocol selection. The model receives the TaskRequest,
RuntimeEnvelope, Kernel, and only the selected protocol modules.

When Program is selected, the harness must also supply the current
ProgramControl named by a non-authorizing TaskRequest reference. Structural
validation does not prove that a control is live or authoritative; reconcile
that identity against canonical project state.

## Distribution

- `dist/pack/` — recommended progressively loaded pack
- `dist/MONOLITH.md` — all normative runtime text for one-file systems
- `src/` and `protocols/` — normative source
- `schemas/` and `templates/` — guarded-runner contracts
- `profiles/` — draft examples, not accepted authority
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
