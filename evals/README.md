# Sparse Evaluation

The active release smoke test asks one narrow question: does the routed v0.5
context avoid important decision failures without requiring a large model
budget?

Deterministic unit tests own policy verification, routing, monotonic
escalation, protocol order, path containment, terminal program states, prompt
leakage, generated drift, and context budgets. Model calls do not test those
properties.

`cases.json` contains eight adversarial fixtures for deterministic coverage.
The frozen release manifest samples four high-signal cases—Core, Program,
Experiment, and combined Program/Secrets—using one neutral and one routed
decision each. That is exactly eight optional calls.

## Execution status

The fixtures, rubric, and historical reports remain as evidence and regression
inputs. The former Python evaluator has been retired with the executable
fallback: release correctness is now covered by the Rust contract, routing,
pack, and distribution tests. Do not treat the historical reports as a live
release gate or invoke model calls from this repository by default.
