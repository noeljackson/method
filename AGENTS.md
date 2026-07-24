# Agent instructions

This repository publishes the Noel Method. Keep its normative core concise,
actor-neutral, and domain-neutral.

## Sources of truth

- Files under `src/` and `protocols/` are the normative source.
- `dist/MONOLITH.md` and `dist/pack/` are generated. Never edit them by hand.
- Templates, policies, adapters, case studies, and migration notes may explain
  or specialize the method, but they may not silently add hard-core rules.

## Change rules

- A new hard-core rule must cite an observed failure in the casebook, explain
  why an existing rule is insufficient, and include a changelog entry.
- Keep tool, vendor, repository, infrastructure, and personal operational
  details out of `src/` and the generated distribution.
- Preserve stable kernel sections and contract names. Behavioral changes
  require a version change; wording-only corrections use a patch release.
- Use pull requests after the initial repository bootstrap.

## Verification

Run before publishing:

```sh
python3 scripts/build_dist.py
python3 -m unittest discover -s tests
python3 scripts/check_docs.py
```
