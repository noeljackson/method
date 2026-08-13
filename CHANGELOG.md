# Changelog

All notable changes to the Noel Method are recorded here.

## 0.9.2 - 2026-08-13

- Preserve bounded structural observations while allowing only
  claim-relevant facts to decide acceptance, and finish diagnostics once those
  facts are complete and quiescent instead of always consuming the full
  horizon.
- Classify diagnostic evidence by content and producer contract rather than
  treating a log channel as automatically secret or safe; retain protected raw
  material only for its current consumer.
- Record these failures as casebook observations `M-006` and `M-007` with two
  focused decision scenarios. This patch adds no protocol, artifact, schema,
  CLI, fixed stabilization interval, or service-specific contract.

## 0.9.1 - 2026-08-13

- Reset a working model before another mutation when authoritative evidence
  contradicts it: separate decision-bearing observations from interpretations,
  use the cheapest discriminator, and resume on a predictive model or a safe
  action common to all remaining models.
- Record the wrapper-model failure as casebook observation `M-005` and add one
  focused decision scenario. This clarification adds no protocol, artifact,
  schema, CLI, retry threshold, or mandatory decision table.

## 0.9.0 - 2026-08-12

- Rewrite the Kernel around five questions a trusted senior teammate answers,
  including bounded tentative assent, objective continuity across questions
  and failed approaches, and just-in-time human involvement.
- Make direct mode the only authority mode and remove ProjectPolicy,
  PolicyAuthorityRegistry, TaskRequest, ResolvedPermissions, their schemas and
  templates, and the resolver, policy, and generic validation commands.
- Replace the optional ProgramControl JSON with one canonical human-readable
  tracker body: a strict TOML metadata header and seven short Markdown
  sections, validated by `method program validate` and optional transition
  comparison.
- Advance EvidenceReceipt to version 2, reserve it for fragile operation
  results, and classify predeclared claims individually as `SUPPORTED`,
  `REJECTED`, or `INCONCLUSIVE`.
- Require diagnostic evidence to serve a pending decision, distinguish missing
  observation from product failure, isolate unrelated failure planes, and
  apply a known safe invariant without waiting for irrelevant perfect
  causation.
- Prefer local, deterministic discrimination before expensive qualification;
  preflight cheap prerequisites before consuming an operation attempt and
  preserve its claim-scoped reduction before raw evidence disappears.
- Simplify the CLI to version, context, Program validation, receipt validation,
  pack verification, and distribution commands. Machine-readable context is
  schema version 4.
- Bind pack verification to the v0.9 runtime inventory; older consumers retain
  their matching immutable CLI and pack until migration.
- Record the v0.9 failures and insufficiencies as casebook observations
  `M-001` through `M-004`, with focused deterministic decision scenarios and a
  public API migration snapshot.

## 0.8.5 - 2026-08-11

- Keep incidental prerequisites subordinate to the owning outcome: perform the
  minimum unblock, return, and promote follow-up only for current acceptance, a
  concrete safety guard, or changed scope.
- Treat expensive clean-room, end-to-end, and destructive gates as candidate
  qualification rather than ordinary debugging loops.
- Record the scope-return and qualification-loop failures as casebook
  observations `C-025` and `INF-002`, with four focused decision scenarios.
- Keep Program, schemas, authority modes, and CLI shape unchanged.

## 0.8.4 - 2026-08-08

- Make a designated ProgramControl authoritative over unrelated host goals,
  timers, and session state.
- Require an authorized, in-boundary source repair to continue under its
  existing claim rather than end at an issue, rejected attempt, or receipt.
- Limit extra Program artifacts and receipts to named failure, authority,
  transition, terminal-handoff, or later-decision use.
- Require an unambiguous named coordinator when live control uses one, and one
  bounded discriminator for an unknown result.
- Turn credible recurring failures with a concrete future consumer into the
  smallest in-scope guard at the closest existing enforcement boundary.
- Record the host-control and repair-continuity failure as casebook observation
  `C-024` and add focused decision scenarios.
- Record the Infra guard-ownership failure as casebook observation `INF-001`
  and add two bounded decision scenarios.
- Keep schemas, authority modes, and CLI shape unchanged.

## 0.8.3 - 2026-08-08

- Return requested durable-goal text as its plain-text payload only, without
  Markdown framing or surrounding commentary unless formatting is requested.
- Record the direct-reuse failure as casebook observation `C-023` and add a
  focused evaluation scenario.
- Keep protocols, schemas, authority modes, and CLI shape unchanged.

## 0.8.2 - 2026-08-07

- Classify manual retries by their effects instead of their initiation
  mechanism.
- Let unchanged verification-only work inherit its authorized action when
  canonical policy classifies the failure as transient.
- Keep retries capable of publication, deployment, release, recovery, live
  mutation, or direct credential handling separately authorized.
- Record the Codewire Infra retry observation as casebook entry `C-022` and
  add deterministic safe-retry and side-effecting-retry scenarios.
- Keep protocols, schemas, authority modes, and CLI shape unchanged.

## 0.8.1 - 2026-08-07

- Apply transition-driven passive-gate observation in direct mode as well as
  Program work, while preserving useful early failure and terminal feedback.
- Permit transition-aware observers without making unchanged state a recurring
  work iteration, and reserve detailed diagnostics for failure, inconsistency,
  empty output, or credible stall.
- Record the Codewire direct-mode observation as casebook entry `C-020` and add
  a deterministic direct-mode scenario.
- Require failure-layer localization before another side effect, with retries
  justified by a discriminating change or a canonical transient policy.
- Keep unknown results scoped to the affected mutation while read-only
  diagnosis and independent authorized work continue.
- Record the Codewire failure-convergence observation as casebook entry `C-021`
  and add three deterministic scenarios.
- Keep protocols, schemas, authority modes, and CLI shape unchanged.

## 0.8.0 - 2026-08-05

- Observe passive external gates after notifications, expected transition
  horizons, credible stalls, or when they become decision-relevant, instead of
  treating unchanged healthy state as a recurring work iteration.
- Preserve persistent objectives across passive waits while continuing any
  actionable authorized work.
- Bound detailed diagnostics to failures, inconsistencies, and credible stalls.
- Reconcile Program state on admission and material transitions, bind claims
  once, and let routine repair and verification inherit an unchanged admission.
- Treat goal, plan, and control as logical concerns that may share one artifact,
  and load archived controls only when relevant to a current claim.
- Bound inherited authority to pre-existing, unchanged automatic consequences
  declared by canonical policy and triggered solely by the authorized action.
- Report transitions and outcomes without repeating unchanged state.
- Record the Codewire observations as `C-018` and `C-019` and add deterministic
  Program and authority scenarios.
- Keep the ProgramControl schema and authority modes unchanged. Merging this
  source change does not publish a release or update downstream consumers.

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
- Record the generalized control-activity and stale-projection failure as
  casebook observation `P-001` and add deterministic Program scenarios.

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
