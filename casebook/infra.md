# Infrastructure observations

### Recurring failures need an enforcing consumer

Observation ID: `INF-001`

During a private Forgejo migration, a value-blind inventory established that a
target contained no Actions records. That observation did not prove the
repository capability itself was disabled. Repository-local commits
`0dd167f`, `27c74e6`, and `826e9c9` progressively added the inventory, disabled
Actions before ref import, verified the disabled state, and retained only the
bounded outcome needed by later migration work.

The Kernel already said to record lessons at the narrowest generalizable
layer. It did not say when a recurring failure should become an enforcing
guard, so a worker could leave the lesson in prose or let an importer, static
checker, evidence object, and report each define it differently.

Version 0.8.4 generalizes the correction: when authorized work faces a
credible recurring failure and a concrete future consumer exists, place the
smallest guard at the closest existing enforcement boundary. Outcome checks
may confirm that guard but do not become another definition. A guard may
remove an invalid state, strengthen a type, reuse a validator, add a focused
assertion, or retain a regression fixture; it need not add a framework.

Generated contracts and tests share one reasoning lineage, so their agreement
is useful coverage rather than independent proof. Forgejo fields, token rules,
staging, counterexample storage, and production assertion policy remain local
engineering decisions.
