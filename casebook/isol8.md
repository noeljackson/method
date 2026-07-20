# Case Study: isol8

The original Noel Method grew inside a systems project with difficult
lifecycle, virtualization, networking, storage, and test-environment failure
classes. Its methodology document became a high-resolution incident journal:
rules were added immediately after costly failures.

## Lessons retained

### Evidence before architecture

Elegant designs repeatedly looked plausible before the broken link had been
isolated. Requiring a call-chain evidence map separated investigation from
implementation and prevented design preference from impersonating proof.

Generalized into `C1`, `C3`, and the `EvidenceRecord` contract.

### Classify the failure and check the plan

Similar symptoms originated in different layers: target code, orchestration
harnesses, carried state, ordering, or infrastructure. The method learned to
classify first and to ask whether an accepted but incomplete architecture
already removed that class.

Generalized into `C3` and the decision workflow's classification and
plan-coverage steps. The concrete taxonomy remains profile-specific.

### The brief is the authority boundary

Broad prompts let workers infer cleanup or lifecycle authority from ambient
signals. Strong briefs named the canonical authority, forbidden evidence,
negative tests, and stop conditions.

Generalized into `C2`, `WorkContract`, and the session protocol.

### Failed environments are evidence

Reusing failed test environments mixed old residue with new behavior, while
destroying them too quickly erased the best diagnostic state. Preserving the
failed specimen and retrying changed work on a clean environment produced a
clearer comparison.

Generalized into `C5` and the verification protocol.

### Verify what actually ran

At least one architectural conclusion was drawn from a node running an older
artifact than the one under evaluation. Artifact hash, observed new-path
behavior, and process restart evidence changed the conclusion.

Generalized into exact artifact and environment identity in `C1`, `C5`, and
`EvidenceRecord`.

### Methodology must be distilled

The source document accumulated numbering discontinuities, duplicated
operating rules, dated infrastructure, and even a conflict marker. Those are
normal scars in a live incident journal but poor prompt context.

The universal method therefore keeps a generated coherent core, moves local
mechanics into profiles and adapters, and preserves incident detail here.
