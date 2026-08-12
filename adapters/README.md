# Consumption Adapters

Use the smallest integration the task needs. Authority always comes from the
current request and canonical project instructions, not from an adapter.

## Prompt-only local pack

Copy the complete `dist/pack/` directory and point repository instructions at
`pack/INDEX.md`. Direct mode loads only `KERNEL.md` plus protocols selected by
task shape. This is the recommended starting point.

When the `method` binary is available, the consumer can load the embedded,
verified equivalent without a repository-specific adapter:

```sh
method pack verify
method context --program
```

Use `--format json` when a host needs module paths, digests, and content as a
stable machine-readable value. For a vendored pack, pass its pinned release
digest with `method pack verify PATH --expect-manifest-sha256 "$DIGEST"`;
self-consistent file hashes alone are not an authority anchor.

When Program is selected, keep one canonical human-readable tracker body. A
host may validate its shape with `method program validate`, but remains
responsible for selecting the canonical tracker and enforcing project policy.
Use `method receipt validate` only for a decision-bearing fragile-evidence
handoff, not for routine task state.

## Single-file fallback

Copy `dist/MONOLITH.md` only when the prompt system cannot load linked modules.
It contains the Kernel and all protocols, so it costs more context and still
does not grant project authority.

## Tagged remote reference

Use only a published, verified tag:

```text
https://raw.githubusercontent.com/noeljackson/method/<tag>/dist/pack/INDEX.md
```

Confirm the tag before configuring a consumer:

```sh
NOEL_METHOD_TAG='vX.Y.Z'
git ls-remote --exit-code --refs https://github.com/noeljackson/method.git \
  "refs/tags/$NOEL_METHOD_TAG"
```

Do not substitute mutable `main`. If a linked module is unavailable, use an
approved local copy or report incomplete context.

## Vendored forms

Subtree:

```sh
NOEL_METHOD_TAG='vX.Y.Z'
git subtree add --prefix=vendor/noel-method \
  https://github.com/noeljackson/method.git "$NOEL_METHOD_TAG" --squash
```

Submodule:

```sh
NOEL_METHOD_TAG='vX.Y.Z'
git submodule add https://github.com/noeljackson/method.git vendor/noel-method
git -C vendor/noel-method checkout "$NOEL_METHOD_TAG"
git add .gitmodules vendor/noel-method
```

Record the tag, commit, and pack manifest digest in the consuming repository.

## Instruction snippets

- [Local pack](agents-local.md)
- [Remote reference](agents-remote.md)
- [Generic prompt](generic-prompt.md)
