# Changelog

All notable changes to the Noel Method are recorded here.

## 0.7.0 - 2026-07-29

- Simplify the Program protocol around one live control, cohesive recovery
  boundaries, named mutation claims, action-scoped gates, local repair, and
  terminal evidence.
- Allow non-mutating review, verification, monitoring, and evidence assembly
  to proceed concurrently with one coordinate's mutation claim.
- Allow explicitly queued successor-readiness preparation while making it
  provisional until refreshed against the accepted predecessor.
- Require copied or rendered live controls to identify their canonical source
  and revision; stale projections are evidence rather than authority.
- Require each work item to advance a named goal condition through a cohesive
  recoverable outcome, and omit additional control artifacts, gates, or
  receipts that prevent no named failure, carry no authority, and provide no
  evidence consumed by a later decision.
- Clarify that the Method is the normative Markdown; the stateless CLI,
  generated pack, schemas, templates, and structured controls are optional
  aids rather than adoption requirements.
- Record Codewire control activity and stale projection drift as casebook
  observation `C-018` and add deterministic Program scenarios.

## 0.6.0 - 2026-07-29

- Distinguish bounded coordinate repair from a finding that materially
  invalidates the live ProgramControl.
- Keep independent authorized coordinates dispatchable while another
  coordinate's scoped gate is unsatisfied.
- Add explicit blocked-action or blocked-coordinate targets to ProgramControl
  hard gates and bump that optional JSON serialization to schema version 2.
- Right-size work items around one cohesive change and recovery boundary,
  avoiding status, evidence, repair, and bookkeeping fragmentation.
- Add a bounded readiness pass before fixing a work-item boundary.
- Record the Codewire full-stop and fragmented-work failure as casebook
  observation `C-017` and add focused decision scenarios.

## 0.5.0 - 2026-07-24

- Add the installable Rust `method` CLI and `noel-method` Cargo package with an
  embedded, manifest-verified runtime pack.
- Add stateless commands for context assembly, pack verification, strict
  contract validation, policy digest and acceptance verification, and
  deterministic resolved-mode permission calculation.
- Let `method context` consume a TaskRequest, ResolvedPermissions, or monotonic
  model-selected protocol flags and return ready-to-inject Markdown or stable
  JSON. The CLI does not create authority, broker tools, or retain task state.
- Add a strict JSON Schema and native validator for EvidenceReceipt.
- Require ResolvedPermissions Program and Secrets controls to match their
  selected protocols exactly.
- Make Rust the sole executable implementation. The generated pack contains
  data and schemas only; it no longer ships a Python resolver or fallback.
- Move generated-pack build and drift checking into `method dist build` and
  `method dist check`, and retire the Python evaluator scripts and tests.
- Add native Linux, macOS, and Windows release packaging, checksums, Cargo
  publication support, and Rust checks to continuous integration.
- Preserve the v0.4 Kernel and authority-mode decisions unchanged.

## 0.4.0 - 2026-07-24

- Make direct authority mode the default for conversational work. The current
  request and canonical project instructions may authorize external,
  persistent, and bounded review-lifecycle actions without Method-specific
  artifacts.
- Make resolved mode explicit opt-in by the project, current request, or
  consuming host. Missing resolved-mode controls fail closed only after that
  mode has been selected.
- Rename `ProjectProfile` to `ProjectPolicy` and `RuntimeEnvelope` to
  `ResolvedPermissions` across contracts, schemas, resolver output, adapters,
  and generated distribution.
- Clarify that the deterministic resolver checks policy/request consistency;
  it does not authenticate the caller, prove conversational fidelity, or
  enforce tool permissions.
- Route Program, Experiment, and Secrets by task shape in either authority
  mode. Allow ProgramControl to use an existing canonical plan or host record
  instead of requiring a second JSON artifact.
- Record the Codewire v0.3 adoption deadlock as casebook observation `C-016`.
- Keep model evaluations opt-in with no merge-time calls and an eight-call
  ceiling; deterministic tests own authority-mode, routing, contract, and
  distribution correctness.

## 0.3.0 - 2026-07-23

- Replace the eight-rule Base and routine Session/Verification protocols with
  a 600-word runtime Kernel: Observe, Bound, Act, Verify, Report, plus the
  permanent secret boundary.
- Make direct supervised work artifact-free; the current request is sufficient
  for bounded, reversible, locally provable tasks.
- Reserve ProjectProfile, TaskRequest, and RuntimeEnvelope for guarded work
  that crosses the direct supervised boundary.
- Add a strict standard-library resolver with duplicate-field rejection,
  digest-bound external profile acceptance, monotonic protocol selection,
  action/gate validation, and compact conditional controls.
- Retain only Program, Experiment, and Secrets as universal optional protocols.
- Replace the generated distribution with a progressively loaded runtime pack
  and an exactly equivalent `dist/MONOLITH.md`.
- Replace the 76-call default eval with an opt-in eight-call smoke gate.
  Deterministic tests own routing and contract correctness; broader ablations
  are diagnostic only.
- Add strict JSON Schemas and JSON templates for all guarded-runner controls.

## 0.2.1 - 2026-07-22

- Put the pinned local-pack installation command, ProjectProfile explanation,
  and everyday-use path directly in the README; remove the redundant
  getting-started page.

## 0.2.0 - 2026-07-20

- Add a linked modular distribution with one always-loaded Base and three
  monotonic ContextFlags for Program, Experiment, and Secrets.
- Anchor ProjectProfile acceptance to an external authority source and exact
  profile digest; make C1–C8 non-waivable for conforming use.
- Represent concurrent program frontiers, incomplete termination, and
  separately authorized emergency containment.
- Keep the full prompt pack as a compatibility fallback.
- Add a generated manifest with per-file SHA-256 digests.
- Add a bounded ten-case adversarial eval with neutral, Base,
  explicit-protocol, and same-session automatic-context arms.
- Make Python a deterministic documentation loader: validate three booleans,
  merge them by OR, and map enabled flags to protocol files.
- Add hard-core rule C8 from observed secret-output disclosures, an opt-in
  secrets protocol, clean-context recovery, and secret disclosure evals.
- Require a reconciled canonical baseline and explicit execution-context and
  shared-resource boundaries before substantive or parallel mutation.
- Validate modular links, distribution drift, context derivation, word budgets,
  eval call caps, profile acceptance, and rule provenance in CI.

## 0.1.0 - 2026-07-20

- Distill the actor-neutral hard core as C1, C2, C3, C4, C5, C6, and C7.
- Add session, program, verification, and experiment protocols.
- Add copyable work, evidence, profile, and program-control contracts.
- Add software, research, and operations profiles.
- Add copy, vendor, reference, subtree, and submodule consumption paths.
- Preserve source lessons in case studies and a complete migration map.
- Add generated prompt-pack, documentation, boundary, and scenario checks.
