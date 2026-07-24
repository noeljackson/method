# Secrets Protocol

Use this protocol for planned credential use, bearer material, secret delivery,
possible exposure, or an unknown secret-capable path. It specializes the
Kernel's permanent secret boundary and grants no access or containment
authority.

## Preflight without retrieval

Before access or mutation, establish from the RuntimeEnvelope:

- approved non-authorizing reference, owner, target, and intended use;
- approved provider, delivery boundary, and receiving process;
- authority to read, inject, create, rotate, revoke, or delete;
- minimum privilege, audience, and lifetime;
- foreseeable logs, traces, transcripts, artifacts, and external egress;
- non-revealing artifact scan and exposure-response path.

Unknown provider, target, authority, secret-capable tool behavior, or material
egress results in `HOLD`. Ambient credentials are not authority. Bearer links,
recovery links, presigned shares, and identifiers that grant access are secret
values, not references.

## Deliver opaquely

Prefer provider-managed injection directly into the intended process. Generate
new values inside the approved provider or destination. Keep plaintext outside
the coordinating actor, model, prompts, tool-call context, command arguments,
shell history, source, patches, logs, fixtures, and evidence.

Do not use output-producing reads, shell tracing, environment dumps,
diagnostic echoes, or verbose modes that can render a value. A silent flag is
not a safety boundary. Avoid temporary files; if an approved receiver requires
one, constrain location, permissions, audience, lifetime, and cleanup.

A destination-encrypted envelope is allowed only when plaintext is created and
decrypted outside the coordinator and model, only the destination holds the
decryption capability, and the profile names its audience, key, retention, and
delivery boundary.

## Verify and scan without revealing

Use provider status, permitted metadata, expected reference shape, or intended
authenticated behavior with sensitive fields suppressed. For rotation, verify
new acceptance and old rejection without rendering either value.

Before durable publication, run the RuntimeEnvelope's secret-scan gate. The
scanner may emit only a safe location, category, approved reference, and
terminal result. It must not print matched bytes, lines, encodings,
fingerprints, or hashes derived from a candidate secret. Raw scanner captures,
when legally or operationally required, belong only in the profile's authorized
forensic quarantine and never in model context.

A clean scan is a detection backstop, not permission to disclose.

## Respond within authority

When exposure is possible:

1. Stop the actor's own output or foreground command when safe, without
   repeating the value.
2. Do not mutate an external process or service unless the RuntimeEnvelope
   names pre-existing containment authority.
3. If containment authority is absent, cease initiating propagation, mark
   affected gates `UNSATISFIED`, and immediately invoke the response path.
4. Identify plausible affected references, audience, surfaces, and time window
   using non-secret metadata.
5. Revoke, rotate, expire, delete, or determine non-compromise only under the
   named disposition authority.
6. Close the emitting command, logger, transcript, or publication path and
   prove the repair with a non-secret canary or dry run.
7. Abandon any model context, transcript, tool output, or inherited process
   state that received the value.
8. Preserve ordinary evidence without secrets. A required forensic original
   remains outside model context in the authorized quarantine with named
   access, retention, and audit.
9. Resume only after the response owner accepts containment, disposition,
   leak-path closure, clean-context evidence, and remaining limitations.

Redaction, deletion, or history rewriting reduces later propagation but does
not reverse disclosure or replace credential disposition.
