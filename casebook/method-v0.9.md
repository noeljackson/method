# Case Study: Human Method v0.9

These observations came from repeated Codewire and infrastructure delivery
sessions and from auditing the Method surface they loaded. Project details are
evidence here; the rules they earned remain repository- and vendor-neutral.

## One control should serve both people and tools

Observation ID: `M-001`

The v0.8 public surface supported direct work but also carried an optional
five-document resolved-authority model, a resolver, six validation targets,
and parallel JSON control. Codewire used direct authority and a canonical
tracker instead. No observed delivery depended on the resolver stack, while
agents repeatedly spent context explaining whether it was required.

The live tracker then accumulated hundreds of lines of receipts and
superseded frontier text. A replacement session had to read the same body in
several slices before finding its current `Next`, even though a handful of
present-tense fields decided dispatch. Human Markdown and machine JSON had
become competing representations of one decision.

Direct-by-default in v0.8 was insufficient because the unused alternative was
still a supported interface that every adapter, schema, migration, test, and
reader had to understand. The one-live-control rule was insufficient because
it did not provide a small format that both a person and a validator could
consume without duplication.

Version 0.9 removes Method-level authority resolution and uses one Program
tracker body with a strict TOML metadata header and short human sections. It
migrates active controls at a natural transition so interface cleanup cannot
itself stop delivery. Project authentication and enforcement remain project or
host responsibilities.

## Conversation is steering, not an implicit stop signal

Observation ID: `M-002`

In several active sessions, the owner said “continue,” “do that,” or “great,”
then asked a status or design question. The worker treated the question as a
new terminal interaction and returned even though the accepted objective still
had safe work. In another loop, an optimization failed its tests and was
reverted cleanly. The worker correctly rejected the patch, but then stopped
twice after explaining why it should have continued.

Existing v0.8 rules already kept a Program active across host-goal changes and
bounded repairs. They did not generalize the human interaction: ordinary
tentative assent was sometimes treated as too weak to start, while any later
question was treated as strong enough to stop. Nor did they state plainly that
a failed approach invalidates the approach, not the objective.

Version 0.9 treats reasonable tentative assent as authority for the bounded
objective already in context. Questions, criticism, status requests, clean
worktrees, reverted attempts, and the absence of a valid patch do not pause
that objective while a safe in-scope action remains. An explicit stop, pause,
checkpoint, or scope change still controls immediately.

## Diagnostic evidence must choose an action

Observation ID: `M-003`

A runtime investigation repeatedly paid for broad integration runs while
adding counters and reducers after each failure. Some counters combined a
successful setup message with an unrelated failed request; another integration
failure belonged to a different subsystem but was allowed to contaminate the
target conclusion. At one point the relevant safety repair—disable registry
fallback and prove the requested artifact existed locally—was already the same
under every plausible root cause, yet more instrumentation preceded it.

Other runs treated absence of a service-state line as evidence that the
service or extension was absent. The direct observation was only that the
current harness had not observed it. Rebuilding the product could not repair
that observation boundary.

The v0.8 “one changed factor” and “cheapest sharp check” rules were
insufficient because an agent could add a new counter without naming the
decision it selected, or call an unobserved claim a defect. Version 0.9 first
states the unresolved question, plausible answers, and action selected by each
answer. If every answer selects the same safe invariant repair, make it. It
also separates failure planes and distinguishes missing observation from a
rejected product claim.

## Preserve the claims an operation was meant to prove

Observation ID: `M-004`

A sensitive live verifier disposed of raw output after a terminal session lost
the summarized result. A later reducer retained only a broad runtime label, so
the next session could not tell which of several probes failed. Another
guarded attempt exited before the workflow because a cheap local prerequisite
was missing; the Program then spent another control cycle determining whether
the expensive operation had actually begun.

EvidenceReceipt v1 could record one summary, but did not require claims to be
declared separately or classified independently. General receipt guidance also
did not require cheap prerequisites to be checked before consuming a costly or
destructive attempt.

Version 0.9 reserves EvidenceReceipt v2 for fragile operation boundaries. It
predeclares claim identifiers, records each as `SUPPORTED`, `REJECTED`, or
`INCONCLUSIVE`, and preserves the reduced result atomically before raw evidence
is destroyed. Cheap local prerequisites run first. Ordinary tests and status
remain ordinary evidence so this durability rule does not recreate receipt
ceremony.

## Authoritative contradictions reset the working model

Observation ID: `M-005`

A staged operating-system recovery wrapper repeatedly rejected a healthy node.
It treated a firmware-reported boot entry as case-sensitive proof of what had
run, then encoded the same interpretation in its mocks. Protected observations
showed the boot identity had not changed, while upstream source treated the two
entry spellings as the same identity. The artifact was staged correctly; the
wrapper's state model was wrong.

The existing decision-focused diagnostic rule could still permit another
counter or patch after each reading. The one-factor retry rule limited each
attempt but did not say when contrary authoritative evidence invalidated the
model behind the attempts. The live system became the integration fixture for
assumptions that source and a few decision-bearing facts could have rejected.

Version 0.9.1 freezes further mutation at a boundary when authoritative
evidence contradicts its working model. It separates direct observations from
interpretations and uses the cheapest discriminator. Work resumes when one
model predicts the next result or every remaining model selects the same safe
action. This is not an arbitrary retry count, demand for exhaustive certainty,
or mandatory decision-table artifact.

## Observe broadly enough to decide narrowly

Observation ID: `M-006`

A staged runtime diagnostic proved its artifact, cache, boot, and named runtime
services, then rejected the candidate because one additional service was not
healthy. The reducer listed only services it already knew, so it hid the
decision-bearing service name. Its acceptance predicate also treated every
unrelated service as part of the target claim and waited the full horizon after
the observed state had stopped changing.

The v0.9 claim and instrumentation rules were insufficient because a reducer
could preserve every predeclared claim while discarding bounded structural
facts needed to interpret a new state. A narrow claim could also be rejected by
context that had no named dependency on it.

Version 0.9.2 preserves bounded observations while allowing only
claim-relevant facts to decide acceptance. Missing or malformed evidence stays
`INCONCLUSIVE`. A diagnostic may finish when relevant evidence is complete and
quiescent; the full horizon remains for state that is still progressing.
Service names, formats, and stabilization intervals remain project policy.

## Evidence sensitivity belongs to content, not channel

Observation ID: `M-007`

A runtime investigation protected credentials, rendered configuration, and
state correctly, but generalized that protection to ordinary structural logs.
The resulting reducer hid the process and service diagnostics needed to explain
why a synthetic fixture passed while the real runtime did not. More guarded
attempts then produced less useful evidence than a bounded local capture would
have provided.

The existing secret boundary prohibited secret values in logs and evidence,
but did not reject the inverse assumption that every log was secret. That
channel-level classification made safe structural messages unavailable without
proving they contained sensitive fields.

Version 0.9.2 classifies evidence by content and its producer's contract. Logs
are neither secret nor safe by default. Known structural diagnostics remain
available; named sensitive fields are suppressed. Uncertain raw material stays
under restricted local access only while its current consumer needs it, then is
disposed of according to project policy. Ordinary durable logs do not require
a Method receipt merely because they cross a session.
