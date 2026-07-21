# Consumption Adapters

Every consumption mode uses the same release and project profile. Choose based
on reproducibility, network access, and repository policy.

## Tagged remote reference

Use when readers and agents can fetch network content. Put the exact release
URL and local profile path in the repository instructions.

```text
https://raw.githubusercontent.com/noeljackson/method/<tag>/dist/pack/INDEX.md
```

If the reference cannot be loaded, do not guess at the method. Use a local copy
or report that the execution context is incomplete.

## Modular copy

Copy the complete `dist/pack/` directory into the consuming repository. Point
the repository instructions at `pack/INDEX.md`, retain `MANIFEST.json`, and
keep relative paths unchanged. This is the recommended mode for repeated agent
use because Base stays small and only applicable optional protocols are added.

## Single-file copy

Copy `dist/NOEL-METHOD.md` into the consuming repository when the prompt
system can load only one document. Retain its generated version header and add
an independently accepted project profile beside it.

## Vendored release

Copy the release's `dist/pack/` into a versioned vendor directory. Record the
upstream tag, commit, and manifest digest in the local profile.

## Git subtree

```sh
git subtree add --prefix=vendor/noel-method \
  https://github.com/noeljackson/method.git v0.2.0 --squash
```

Use a reviewed subtree pull to update the pinned release.

## Git submodule

```sh
git submodule add https://github.com/noeljackson/method.git vendor/noel-method
git -C vendor/noel-method checkout v0.2.0
git add .gitmodules vendor/noel-method
```

Commit the submodule pointer and ensure worker environments initialize
submodules before relying on the method.

## Instruction snippets

- [Local pack](agents-local.md)
- [Remote reference](agents-remote.md)
- [Generic prompt](generic-prompt.md)
