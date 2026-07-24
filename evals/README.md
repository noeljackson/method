# Sparse Evaluation

The active release smoke test asks one narrow question: does the routed v0.3
context avoid important decision failures without requiring a large model
budget?

Deterministic unit tests own profile verification, routing, monotonic
escalation, protocol order, path containment, terminal program states, prompt
leakage, generated drift, and context budgets. Model calls do not test those
properties.

`cases.json` contains eight adversarial fixtures for deterministic coverage.
The frozen release manifest samples four high-signal cases—Core, Program,
Experiment, and combined Program/Secrets—using one neutral and one routed
decision each. That is exactly eight optional calls.

## Default: no model calls

Inspect the plan:

```sh
python3 scripts/run_eval_batch.py
```

Render all eight prompts:

```sh
python3 scripts/run_eval_batch.py --render-dir /tmp/noel-method-prompts
```

Execute only when release evidence is worth the cost:

```sh
python3 scripts/run_eval_batch.py \
  --execute --call-budget 8 --output-dir evals/runs/<run-id>
```

The runner requires a clean, commit-bound worktree and checks that inputs do
not change during execution. Each call is ephemeral and read-only. It creates
a blind map for human scoring and runs no model judge.

Two distinct reviewers score every response using [RUBRIC.md](RUBRIC.md).
Human score entries bind each judgment to its reviewer:

```json
{
  "schema_version": 2,
  "scores": {
    "response-01": [
      {"reviewer_id": "reviewer-a", "judgment": {}},
      {"reviewer_id": "reviewer-b", "judgment": {}}
    ]
  }
}
```

Publish only aggregate results:

```sh
python3 scripts/publish_eval.py evals/runs/<run-id> \
  evals/runs/<run-id>/human-scores.json
```

Use `kernel`, `wrong`, and `monolith` render modes individually to diagnose a
failure. They are not multiplied across the release matrix. Historical v0.2
eval files and reports are retained as prototype evidence, not active results.
