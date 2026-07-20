# Repository Instruction Snippet: Remote Reference

Use only when the worker is expected to have network access:

```markdown
## Noel Method

This repository follows Noel Method `v0.2.0` at:
`https://github.com/noeljackson/method/blob/v0.2.0/dist/pack/INDEX.md`.

Start with that exact tagged index. Always load its linked core and the local
`<path>/PROJECT-PROFILE.md`, then fetch only modules selected by the index's
trigger table. Resolve relative links under the same `v0.2.0/dist/pack/` base.
Do not substitute `main` or a remembered version. If a required module cannot
be loaded, report the missing execution context and use an approved local
copy.
```
