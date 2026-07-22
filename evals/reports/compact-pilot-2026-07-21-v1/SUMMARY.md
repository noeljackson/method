# compact-pilot-2026-07-21-v1 eval report

Status: **PILOT GATE PASSED**

- Source digest: `36ac0cd520a3ac651a653ca2fd0b400ac9de91b94ae26f7920648e3b0455757c`
- Git HEAD: `c74fee849b481770ff6da696cf7527cab63c9acf`
- Started: `2026-07-21T10:33:14.439251+00:00`
- Completed: `2026-07-21T10:44:46.112108+00:00`
- Model: `gpt-5.6-sol` at `xhigh`
- Cases: 8; samples per cell: 1
- Total recorded model tokens: 1424167

## Decision results

| Arm | Responses | Mean / 9 | Pass rate | Hard failures | Mean words |
| --- | ---: | ---: | ---: | ---: | ---: |
| accepted | 8 | 8.812 | 1.000 | 0 | 5036.1 |
| core-profile | 8 | 8.675 | 1.000 | 0 | 2665.1 |
| drafted | 8 | 8.400 | 0.938 | 0 | 4983.4 |
| monolith | 8 | 8.562 | 1.000 | 0 | 6199.1 |
| no-method | 8 | 6.521 | 0.688 | 0 | 247.4 |
| wrong | 8 | 8.300 | 1.000 | 0 | 4548.0 |

## Drafted routing

- Exact descriptor rate: 0.375
- Module precision/recall: 1.0 / 0.846154
- Decisive-module recall: 0.857
- Critical Secrets-module recall: 1.000

## Pilot gates

- PASS — `accepted_routes_exact`
- PASS — `drafted_secret_module_recalled`
- PASS — `wrong_routes_omit_decisive_module`
- PASS — `drafted_and_accepted_safety_no_hard_failure`

## Judge reliability

```json
{
  "decision_and_required_nominal": {
    "agreement": 0.973958,
    "items": 192,
    "kappa": 0.886952
  },
  "evidence_predicates_nominal": {
    "agreement": 0.993056,
    "items": 144,
    "kappa": 0.0
  },
  "forbidden_nominal": {
    "agreement": 0.990741,
    "items": 108,
    "kappa": 0.962539
  }
}
```

## Limitations

- This pilot diagnoses runner, routing, schema, and scoring failures; it is not release evidence.
- One model family and one sample per cell cannot establish stable methodology lift.
- Both blinded judges use separate calls to the same model family rather than independent humans.

Raw prompts, model responses, judge rationales, console logs, and session
records remain local under the ignored run directory. `run-manifest.json`
publishes the frozen inputs and call hashes without those contents.
