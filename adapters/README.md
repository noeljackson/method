# Consumption Adapters

Every consumption mode uses the same release and project profile. Choose based
on reproducibility, network access, and repository policy.

## Tagged remote reference

Use when readers and agents can fetch network content. Put the exact release
URL and local profile path in the repository instructions.

```text
https://raw.githubusercontent.com/noeljackson/method/v0.1.0/dist/NOEL-METHOD.md
```

If the reference cannot be loaded, do not guess at the method. Use a local copy
or report that the execution context is incomplete.

## Single-file copy

Copy `dist/NOEL-METHOD.md` into the consuming repository, retain its generated
version header, and add a completed project profile beside it. Updates are
ordinary reviewed file changes.

## Vendored release

Copy the release's `dist/`, `templates/`, and any selected protocols or
adapters into a versioned vendor directory. Record the upstream tag and commit
in the local profile.

## Git subtree

```sh
git subtree add --prefix=vendor/noel-method \
  https://github.com/noeljackson/method.git v0.1.0 --squash
```

Use a reviewed subtree pull to update the pinned release.

## Git submodule

```sh
git submodule add https://github.com/noeljackson/method.git vendor/noel-method
git -C vendor/noel-method checkout v0.1.0
git add .gitmodules vendor/noel-method
```

Commit the submodule pointer and ensure worker environments initialize
submodules before relying on the method.

## Instruction snippets

- [Local pack](agents-local.md)
- [Remote reference](agents-remote.md)
- [Generic prompt](generic-prompt.md)
