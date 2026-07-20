# Hard Core

## C1 — Ground claims in current reality

Every material claim MUST identify its source of truth and evidence. Current
observable reality outranks plans, trackers, summaries, and recollection.

Before proposing or reporting:

- establish a baseline;
- distinguish observation from inference;
- identify the exact artifact, revision, data set, or environment observed;
- reconcile conflicting sources rather than choosing the convenient one; and
- say "not yet known" when the evidence does not support a conclusion.

A status field is a report about reality, not necessarily the underlying
evidence. Completion, readiness, failure, and success claims require the
evidence named by the applicable gate.

## C2 — Make authority and scope explicit

Substantive work MUST have a work contract that names the outcome, scope,
authority, forbidden work, deliverable, acceptance gates, and escalation
conditions.

Actors have bounded autonomy inside that contract. They SHOULD proceed without
routine permission loops when the next step is determined by the contract.
They MUST stop when:

- the required authority is absent;
- an irreversible or external mutation is outside scope;
- the evidence would require a different outcome or acceptance contract; or
- two reasonable choices would materially change direction.

Signals that are convenient, historical, ambient, or merely plausible MUST NOT
be promoted into mutation authority.

## C3 — Classify before intervening

Before acting on a failure or gap, classify its problem class, affected
invariant, ownership boundary, and likely blast surface. Then check whether a
current plan already covers that class.

- If an existing plan covers it, execute or repair the plan.
- If it exposes a real plan gap, amend the plan before implementing the new
  direction.
- If it is genuinely isolated, a narrow intervention is acceptable.
- If a tactical intervention is necessary while structural work is deferred,
  record the debt and its retirement condition.

The intervention's precision MUST match the evidence's precision. A diagnosis
of one broken link does not authorize changing the whole chain.

## C4 — Make state, gates, and queues unambiguous

Hard gates MUST be binary and evidence-bearing. "Expected," "nearly ready," or
"looks green" does not satisfy a gate.

Dependent work MUST NOT begin while its gate is unsatisfied. A program MUST
name its current coordinate, authorized queue, hard gates, and forbidden work.
Work discovered in one lane cannot silently move into another lane because it
is useful.

When reality changes scope, dependencies, authority, contracts, or acceptance
criteria, mutation stops and the controlling plan is repaired before work
resumes.

## C5 — Verify the claim being made

Verification MUST be selected by failure class and blast surface, not by habit.
Start with the cheapest sharp test that can disprove the working hypothesis,
then broaden enough to cover the intervention's realistic effects.

Evidence is valid only for the exact artifact and environment it tested. A
result from an older revision, different configuration, contaminated state, or
unverified deployment cannot prove the current claim.

On failure:

- preserve the useful evidence;
- classify the failure before retrying;
- change a hypothesis, implementation, or environment before rerunning; and
- use a clean environment when carried state could alter the signal.

Retries without a changed reason are activity, not validation.

## C6 — Keep one canonical source for each decision

Every decision-bearing concept SHOULD have one named canonical source: the
goal, authority, configuration, ownership record, active plan, gate result, or
artifact identity.

Missing canonical state should fail clearly. Silent fallback ladders create
ambiguity and make later evidence hard to interpret. Explicit layering is
allowed only when precedence selects one winner and the profile documents it.

Historical records remain evidence, but they MUST NOT masquerade as the live
control surface.

## C7 — Learn without overfitting

Record material outcomes, failed hypotheses, tactical debt, and lessons at the
boundary where they become clear.

A lesson belongs in the hard core only when it generalizes beyond the incident
that earned it. Otherwise it belongs in a protocol, profile, adapter, or case
study.

Watch for non-convergence:

- repeated fixes at one boundary may indicate an incomplete classification;
- failures appearing across unrelated classes indicate a framing or design
  problem;
- multiple unvalidated proposals create proposal debt; and
- a rule that helps only one known task is likely overfit.

When two approaches produce the same verified result, prefer the simpler one.

## C8 — Keep secrets out of uncontrolled surfaces

Actors MUST NOT ask a user to disclose a secret value into model context, or
copy or deliberately place one in source control, plans, issue or review text,
logs, evidence records, fixtures, command arguments, or other uncontrolled
surfaces. Use an opaque reference and the project's approved secret-delivery
mechanism instead. A model context is not a secret-delivery mechanism.

Secret-bearing work MUST minimize access, privilege, lifetime, and egress.
Fetch or inject a secret only when the authorized operation requires it, and
deliver it only to the intended process or service. Do not prove availability
by printing, dumping, encoding, or otherwise reproducing the value; verify
through non-secret metadata or the intended behavior.

If a value is exposed unexpectedly:

- stop further propagation and do not quote the value in a report;
- treat it as compromised until the owner decides otherwise;
- invoke the project profile's containment, revocation, rotation, and
  escalation path within the actor's authority; and
- preserve only non-secret evidence about the exposure and response.

A project profile MUST name the approved providers, reference syntax,
delivery boundaries, forbidden surfaces, and exposure-response authority. It
may tighten this rule but MUST NOT make prompts or durable work artifacts an
approved secret channel.
