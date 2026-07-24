# Changelog

All notable changes to the Noel Method are recorded here.

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
