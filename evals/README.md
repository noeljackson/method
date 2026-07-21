# Compact Evaluation

The active suite asks one practical question: does compact methodology context
improve difficult decisions enough to justify its token cost?

`cases.json` freezes ten adversarial cases:

- four Base cases: profile authority, evidence identity, destructive recovery,
  and descriptive versus normative truth;
- two Secrets cases: bearer references and exposure recovery;
- two Program cases: concurrent accepted frontiers and owner cancellation; and
- two Experiment cases: protected regression and contaminated state.

The older incident, variant, safety, control, pair, and batch files are retained
as prototype evidence. They are not loaded, validated, or claimed as the active
release evaluation.

## Context arms

Core cases use neutral and Base arms. Protocol cases use neutral, Base,
explicit-protocol, and automatic-context arms. The automatic arm first asks for
the exact three ContextFlags, then appends selected protocols in the same model
session before requesting the decision.

With two samples, the frozen design makes exactly 76 model calls and yields 64
decisions:

- Core: `4 cases × 2 samples × 2 decisions = 16 calls`.
- Protocol: `6 cases × 2 samples × (3 direct decisions + selection + automatic decision) = 60 calls`.

## Use

Render and inspect the call plan without making model calls:

```sh
python3 scripts/run_eval_batch.py
```

Optionally materialize the rendered prompts:

```sh
python3 scripts/run_eval_batch.py --render-dir /tmp/noel-method-prompts
```

Execution is deliberately noisy and bounded:

```sh
python3 scripts/run_eval_batch.py \
  --execute --call-budget 76 --output-dir evals/runs/<run-id>
```

The runner refuses a different budget or any plan above 80 calls. It creates a
64-response blinded bundle and mapping for human review. It does not run model
judges. Apply `RUBRIC.md`, double-score a stratified sample, and report
inter-rater reliability before publishing aggregate claims.

Record judgments in an ignored `human-scores.json`:

```json
{
  "schema_version": 1,
  "reviewers": ["reviewer-a", "reviewer-b"],
  "scores": {
    "response-...": [
      {
        "decision_match": true,
        "evidence_integrity": {
          "observation_inference": true,
          "identity_binding": true,
          "material_limitations": true
        },
        "required": {"required-1": true},
        "forbidden": {"forbidden-1": "rejected"}
      }
    ]
  }
}
```

Every response needs one judgment. Supply two for at least one response in
each family/context-arm stratum. Publication requires quadratic weighted κ of
at least 0.8 and writes only aggregate evidence:

```sh
python3 scripts/publish_eval.py evals/runs/<run-id> \
  evals/runs/<run-id>/human-scores.json
```

The compact pilot under `reports/compact-pilot-2026-07-21-v1/` was development
evidence for the retired TaskDescriptor design and is superseded by this suite.
Raw and incomplete runs under `evals/runs/` remain ignored and unpublished.
