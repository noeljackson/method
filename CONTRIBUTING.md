# Contributing

The Noel Method grows from observed failures, not aspirational rules.

## Change classes

- **Kernel change:** changes a mandatory decision rule. It needs a casebook
  entry, an explanation of why the existing kernel is insufficient, migration
  notes, focused regression coverage, and a version change.
- **Protocol change:** changes an optional operating mode. It needs a concrete
  use case, compatibility notes, and scenario coverage where behavior changes.
- **Profile or adapter change:** specializes existing rules for a domain or
  consumption mechanism. It must not create a hidden hard requirement.
- **Editorial change:** improves clarity without changing a decision. It may
  use a patch release.

## Design checks

Before proposing a new rule, ask:

1. Which observed failure does it prevent?
2. Why do the existing rules not already cover that failure?
3. Is the rule universal, or does it belong in a protocol or policy?
4. Can a human and an agent both apply it without product-specific context?
5. What deterministic check or smallest decision scenario proves the wording
   is operational?
6. Does it make the direct supervised path heavier? If so, is the added trust
   worth that cost?

Prefer deterministic contract and routing tests over model calls. The sparse
eval fixtures remain regression evidence; they do not provide a runnable model
call path in this repository.

Run the release checks before opening a pull request:

```sh
cargo run --locked -- dist check
cargo fmt --all --check
cargo clippy --all-targets -- -D warnings
cargo test --all-targets
cargo package --locked
```
