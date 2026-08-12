# Experiment Protocol

Use only for a controlled comparison against a fixed baseline. It grants no
authority over the evaluated system or promotion.

Record the baseline's inputs, environment, metric, protected invariants, exact
artifact, and result. Preserve the best accepted artifact separately.

For each trial:

1. State one general hypothesis and expected observation.
2. Make one coherent change.
3. Run the same evaluation in a fresh or equivalent environment.
4. Record the full result, regressions, and limits.
5. Keep, discard, or invalidate it by the predeclared rule.

Promote only when the metric improves without violating an invariant. Keep an
equal result only when it makes the system demonstrably simpler. Otherwise keep
the baseline. If removing one exact fixture erases the benefit, suspect
overfitting; prefer changes that remove a failure class.
