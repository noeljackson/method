# Decision Scenarios

The eval set has four layers:

1. `scenarios.json` covers compact generic decisions.
2. `incidents.json` reconstructs sanitized decision points from real project
   failures without requiring access to the source repository.
3. `variants.json` changes the domain while preserving an incident's decision
   shape, exposing lexical or project-specific overfitting.
4. `safety.json` uses synthetic, non-secret fixtures to test secret routing,
   disclosure refusal, and exposure response.

## Progressive-disclosure evaluation

Run each structured case in two stages:

1. Give the worker `dist/pack/INDEX.md`, `CORE.md`, and an applicable profile.
   Ask which additional modules it needs. Compare with `modules`.
2. Supply those modules and the case. Score the response against `expected`
   and `forbidden`.

The eval tests decisions, evidence use, and module routing—not exact wording.
The incident origin is metadata for reviewers and is never included in the
worker prompt.

Use `scripts/render_eval.py <case-id> --stage route|decision|key` to render
provider-neutral prompts and evaluator-only answer keys. Score responses with
[`RUBRIC.md`](RUBRIC.md).

## Incident construction rules

- Freeze the scenario at the moment before the bad decision; do not reveal the
  postmortem answer in the prompt.
- Include only evidence available at that moment.
- Remove secrets, infrastructure addresses, private log locations, and
  product trivia not required for the decision.
- Never use a real or plausibly live credential as an eval fixture. Use an
  opaque reference or an unmistakable placeholder, and test whether the
  worker refuses disclosure rather than whether a scanner notices a value.
- Score a transferable decision, not recall of an issue or pull request.
- Pair important incidents with a different-domain isomorphic variant.

Before a release that changes the hard core or routing table, record a human
review and at least one agent run in the release notes. Model-specific scoring
infrastructure remains outside v0.2.
