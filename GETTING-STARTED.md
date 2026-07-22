# Getting started with Noel Method

Noel Method is workspace setup plus a small working loop. You install one
pinned pack, accept one local ProjectProfile for the workspace, and then use
only the context needed by the work in front of you.

## 1. Start from a published tag

Use a Git tag that exists remotely. `VERSION` describes the source checkout;
it is not by itself a released, reproducible install target. Never point a
worker at mutable `main`.

```sh
NOEL_METHOD_TAG='vX.Y.Z' # replace with a published release tag
git ls-remote --exit-code --refs https://github.com/noeljackson/method.git \
  "refs/tags/$NOEL_METHOD_TAG"
```

If the tag is absent, wait for the release or inspect the source read-only.
Do not present an untagged checkout as an installed Method release.

## 2. Choose one installation mode

### Local, reproducible pack

Use this for a repository that expects repeated agent work or offline access.
It keeps the Method alongside the project and makes updates ordinary reviewed
repository changes.

```sh
NOEL_METHOD_TAG='vX.Y.Z' # replace with a published release tag
git subtree add --prefix=vendor/noel-method \
  https://github.com/noeljackson/method.git "$NOEL_METHOD_TAG" --squash
test ! -e PROJECT-PROFILE.md
cp vendor/noel-method/templates/project-profile.md PROJECT-PROFILE.md
```

Point your repository instructions at
`vendor/noel-method/dist/pack/INDEX.md`. Keep the pack's `MANIFEST.json` and
relative layout intact. For a submodule or a one-file prompt system, use the
[adapter guide](adapters/README.md).

### Tagged remote reference

Use this only when the worker has network access and can verify the tag and
its manifest. Put the exact URL, not `main`, in the repository instructions:

```text
https://raw.githubusercontent.com/noeljackson/method/<published-tag>/dist/pack/INDEX.md
```

The [remote instruction snippet](adapters/agents-remote.md) is ready to copy.
Keep `PROJECT-PROFILE.md` in the consuming repository; remote Method text does
not supply local authority.

## 3. Create and accept the project profile

Fill the copied [ProjectProfile template](templates/project-profile.md) with
the workspace's canonical sources, actors, authority boundaries, gates,
secret handling, and reporting destination.

While it is `DRAFT`, it grants no mutation authority. An independent owner
must accept the exact body digest and record the authority source, actor, time,
and receipt in the Acceptance section. A profile must be reaccepted whenever
its scope, authority source, or body changes. The profile is setup for the
workspace, not a form to recreate for each task.

For a local checkout or vendored subtree, print the required digest with:

```sh
python3 vendor/noel-method/scripts/profile_digest.py PROJECT-PROFILE.md
```

The command excludes the Acceptance section exactly as the profile contract
requires. Record its output in `Profile digest` before the independent owner
accepts the profile.

## 4. Use the normal path

For every task, load the pinned pack's `INDEX.md`, `BASE.md`, and the exact
accepted `PROJECT-PROFILE.md`.

For most bounded, reversible work, use this small prompt shape:

```text
Outcome: <what should be true next>
Constraints: <boundaries and non-goals>
Evidence: <current source of truth or check>
Next action: <one bounded step>
```

Use a [WorkContract](templates/work-contract.md) only when the work is
substantive: it changes external or irreversible state, handles sensitive
material, crosses a meaningful handoff or authority boundary, or has material
uncertainty about success.

Enable an optional protocol only when it applies:

| Work | Context flag | Additional context |
| --- | --- | --- |
| Persistent multi-workstream program | `program` | Program protocol and ProgramControl |
| Controlled comparison against a fixed baseline | `experiment` | Experiment protocol |
| Credential, secret delivery, or possible exposure | `secrets` | Secrets protocol |

Caller, profile, and model flags merge by boolean OR. A flag adds context; it
does not grant authority.

## 5. Know the limits

The Method does not choose the project's goal, make a draft profile active, or
turn a passing test into permission for an unrelated mutation. It gives people
and agents a compact way to make those boundaries explicit, preserve evidence,
and stop when reality changes the approved work.

For copy-ready instruction text, see the [local-pack adapter](adapters/agents-local.md),
[remote-reference adapter](adapters/agents-remote.md), and
[generic prompt wrapper](adapters/generic-prompt.md).
