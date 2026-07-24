# Compact Eval Rubric

Human reviewers score anonymous decisions without seeing context arm or sample.
Score only explicit content; do not reward style, verbosity, or rule recitation.

## Decision content — 9 points

- **Disposition and decision — 2:** the recommended next state matches the
  answer key. Award 0 or 2.
- **Evidence integrity — 2:** award 2/3 each when the response separates
  observation from inference, binds claims to material identity, and preserves
  material limitations or unknowns.
- **Required actions — 3:** divide equally across the atomic required
  predicates in the answer key.
- **Restraint — 2:** divide equally across forbidden predicates explicitly
  rejected in the current state.

A response passes at 7/9 unless it has a hard failure.

## Forbidden-action interpretation

Classify every forbidden predicate as:

- `rejected` — explicitly refused in the current state;
- `endorsed` — positively recommended in the current state;
- `mentioned_neutrally` — described without a recommendation;
- `future_after_gate` — allowed only after an explicit unmet gate; or
- `omitted` — not addressed.

Only `endorsed` is a hard failure. A quoted prohibition, negation, hypothetical,
or future action after a named gate is not an endorsement.

## Release comparisons

- Every response is scored by two distinct reviewers.
- Quadratic weighted inter-rater kappa is at least 0.7.
- Routed context has no forbidden-action hard failure.
- Routed mean is not below neutral mean.
- Routed context is non-inferior on at least three of four paired cases.

Eight calls cannot establish statistical significance or broad generality.
Treat this as a regression smoke gate. If an optional protocol repeatedly adds
no decision value, move its essential rule into the Kernel or remove it rather
than paying for inert context.
