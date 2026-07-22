# Secrets Protocol

Use this protocol when work authenticates with, creates, reads, changes,
rotates, revokes, deletes, or could expose a secret. It specializes `C8`; it
does not authorize secret access by itself.

## Preflight

Before access or mutation, establish without retrieving the value:

- the approved secret reference, owner, target environment, and intended use;
- the approved provider, tool path, and delivery boundary from the project
  profile;
- the exact authority to read, inject, create, rotate, revoke, or delete;
- the minimum scope and lifetime required by the receiving process;
- all reasonably foreseeable logs, traces, transcripts, artifacts, and
  external services that could see input or output, plus explicit treatment of
  material unknown egress; and
- the exposure-response owner and stop condition.

Unknown provider, target, authority, or materially exposure-relevant egress
fails closed. Immaterial platform unknowns remain explicit limitations. A
convenient ambient credential is not authority to use it.

Confirm that a reference is non-secret, non-authorizing, and safe for its
audience. Treat a bearer link, recovery link, presigned share, or any identifier
that grants access as a secret value.

## Deliver without revealing

- Prefer provider-managed direct injection into the intended process or
  service. Keep the value opaque to the coordinating actor and model.
- Generate new values inside the approved provider or destination, not in a
  prompt, transcript, patch, or coordinating tool call.
- Do not use output-producing reads, shell tracing, environment dumps,
  observable command arguments, diagnostic echoes, or verbose modes that can
  render the value. A `silent` flag is not a sufficient control by itself.
- Treat tool-call inputs and outputs as model-visible context even when the
  underlying command runs locally.
- Separate non-secret configuration and identifiers from secret values. Treat
  names, paths, and infrastructure details as sensitive when the profile says
  so.
- Avoid temporary files. When a receiving tool requires one, use the
  profile-approved protected location and permissions, bound its lifetime,
  and remove it through an authorized cleanup path.
- Do not widen a token, role, workflow permission, network path, or audience
  to make delivery easier.
- A profile-approved destination-encrypted envelope may be durable only when
  plaintext is
  created and decrypted outside the coordinating actor and model, only the
  intended destination holds the decryption capability, and the profile names
  its key, audience, retention, and delivery boundaries.

## Verify safely

Use the narrowest non-revealing proof that supports the claim:

- approved provider status, version, age, or policy metadata;
- presence of an expected reference or data-key shape without contents;
- successful intended behavior with sensitive response fields suppressed; or
- for rotation, acceptance of the new credential and rejection of the old one
  without rendering either value.

Run the project-defined secret scan over changed durable artifacts before
publication or commit. A clean scan is a backstop, not evidence that deliberate
disclosure is safe or that every secret shape was detected.

Evidence records contain approved secret references, artifact and environment
identity, redacted observations, and limitations. A redaction marker is not
proof that the original capture was safe.

When a leak has no safe label, an authorized isolated provider-side comparison
may match candidate secrets. It emits only the approved reference, match
status, and audit receipt; it MUST NOT emit values, bearer material, hashes, or
fingerprints to the coordinator.

## Respond to exposure

When a secret may have reached an uncontrolled surface:

1. Stop the command, publication, or propagation path when safe to do so.
2. Do not repeat the value while diagnosing or reporting the event.
3. Identify the affected secret, audience, surfaces, and time window using
   non-secret metadata.
4. Mark affected gates `UNSATISFIED` and notify the profile's response owner.
5. Revoke, rotate, expire, delete, or accept non-compromise only with the
   required authority; absence of that authority is an escalation, not
   permission to continue.
6. Close or disable the command, logger, transcript, or publication path that
   disclosed the value. Before introducing any replacement, prove the repair
   with a non-secret canary or dry run.
7. If a model context, transcript, captured tool output, or inherited process
   state received the value, abandon it and continue only in a clean context.
8. Within current authority, sanitize durable uncontrolled copies while
   preserving non-secret incident evidence. An original required for forensics
   or legal hold moves to an authorized quarantine with named audience,
   access, retention, and audit controls and is never exposed to a model.
9. Resume only after the owner accepts containment, the secret disposition,
   leak-path closure, clean-context evidence, and remaining limitations.

Redaction, deletion, or history rewriting does not reverse disclosure. It
reduces future propagation but does not replace revocation or rotation when
the response owner requires them.
