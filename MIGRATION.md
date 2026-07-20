# Source Migration Map

This map proves that the universal method distilled rather than silently
dropped the source material. Destinations are intentionally narrower than the
original documents.

Destination labels:

- **Core:** one of `C1`–`C7` or the main workflow.
- **Protocol:** optional session, program, verification, or experiment rules.
- **Contract:** stable template/interface.
- **Profile:** project or domain specialization.
- **Adapter:** tool or repository integration.
- **Casebook:** rationale and incident history.
- **Retired:** a local mechanism that should not become universal.

## isol8 methodology

| ID | Source concept | Destination | Disposition |
| --- | --- | --- | --- |
| I-001 | Core decision flow | Core workflow | Retained with actor- and domain-neutral terms |
| I-002 | Architectural answer | C3, C7 | Structural proportionality retained without making every small fix architectural |
| I-003 | Names encode intent | Profile, casebook | Valuable design guidance, not universal execution control |
| I-004 | Evidence before architecture | C1, C3 | Hard-core evidence requirement |
| I-005 | Long-term versus short-term | C3, C7 | Tactical debt and retirement condition retained |
| I-006 | Race-class taxonomy | ProjectProfile | Taxonomy is required; concrete classes stay local |
| I-007 | Plan-coverage check | C3, workflow | Retained as a mandatory pre-intervention decision |
| I-008 | Single source of truth | C6 | Generalized to every decision-bearing concept |
| I-009 | Working trust and autonomy | C2, session protocol | Roles become responsibilities; autonomy stays contract-bounded |
| I-010 | Process discipline | Session protocol, software profile | Review and repository mechanics stay profile-specific |
| I-011 | Orchestrator pattern recognition | C7, session protocol | Evaluator owns non-convergence detection |
| I-012 | Monitoring cadence | Session protocol | Cadence remains project-defined, not a universal number |
| I-013 | Direction reassessment | Session protocol | Strategic review separated from tactical status |
| I-014 | Brief as contract | C2, WorkContract | Promoted to a public contract |
| I-015 | Constrained subworkers | C2, ProjectProfile | Canonical authority and forbidden evidence retained |
| I-016 | Worker harness correctness | C1, C2, adapters | Environment identity retained; local launcher mechanics retired |
| I-017 | Failure as ledger state | Software profile, casebook | Domain architecture pattern, not universal method |
| I-018 | Hash-verified deployment | C5, EvidenceRecord | Generalized to exact artifact and environment identity |
| I-019 | Write down what worked | C7, contributing rules | Retained as earned learning |
| I-020 | Anti-pattern table | Casebook, scenarios | Converted into rationale and executable decisions |
| I-021 | Method non-applicability | Work scales | Direct scale prevents bureaucracy for trivial work |
| I-022 | Code self-heals working state | Software profile, casebook | Domain ownership rule, not hard core |
| I-023 | Empirical convergence | C5, verification protocol | Preserve evidence, classify failure, retry cleanly |
| I-024 | Evidence integrity | C1, C5 | Exact artifact and environment become mandatory |
| I-025 | Deliberate pause | C2, session protocol | Stop only at real authority, evidence, or direction boundaries |
| I-026 | Evidence with citation | C1, EvidenceRecord | Citation and observation/inference split retained |
| I-027 | Multi-gate readiness | C4, C5 | Gate tables generalized; local gate list stays profile-specific |
| I-028 | Avoid routine permission loops | C2, session protocol | Bounded autonomy retained |
| I-029 | Engineer the path to truth | Session and verification protocols | Signal and coordination questions generalized |
| I-030 | Verify deployment | C5, EvidenceRecord | Exact artifact/environment receipt replaces local mechanism |
| I-031 | Parallel versus solo rubric | Session protocol | Parallelize independent evidence, not sequential uncertainty |
| I-032 | Fresh validation before push | Verification protocol, software profile | Freshness retained where state can contaminate evidence |
| I-033 | Match fix precision | C3 | Promoted to hard-core intervention proportionality |
| I-034 | Targeted probes | C5, verification protocol | Promoted to sharpest-test-first rule |
| I-035 | Orient before proposing | C1, workflow | Current plans and state must be read first |
| I-036 | Evidence-gated fix shape | C1, C3 | Missing broken-link evidence yields investigation only |
| I-037 | Chain evidence | EvidenceRecord, WorkContract | Captured as observed, inferred, and unknown links |
| I-038 | Proposal hygiene | C7 | Generalized to proposal debt and validation |
| I-039 | Not knowing is valid | C1 | Hard-core distinction between observation and inference |
| I-040 | Limit proposals | C7, experiment protocol | Renamed from budget to proposal debt; no time/token policy |
| I-041 | Cross-layer ledger | ProjectProfile | Profiles define domain layers and evidence |
| I-042 | Minimum invariant first | C5, verification protocol | Sharpest product invariant precedes broad rehearsal |
| I-043 | Artifact coherence | EvidenceRecord | Generalized artifact manifest fields |
| I-044 | Dependency fetchability | Software profile | Supply-chain preflight remains domain-specific |
| I-045 | One canonical moving plan | C6, program protocol | One live control plus separate history |
| I-046 | Earned updates | C7, contributing rules | New core rules require observed failure evidence |

## Codewire methodology

| ID | Source concept | Destination | Disposition |
| --- | --- | --- | --- |
| C-001 | Goal budget policy | Profile | Repository-local policy; explicitly not universalized |
| C-002 | Program coordinate | Vocabulary, program protocol | Retained verbatim as the program address |
| C-003 | Exact states | Vocabulary, program protocol | Retained as stable public vocabulary |
| C-004 | Pre-mutation reconciliation | ProgramControl, program protocol | Promoted to the dispatch gate |
| C-005 | One work item per pull request | Work-item contract, software profile | Generalized to one reviewable change set |
| C-006 | Hard-gate ordering | C4, program protocol | Promoted to hard core |
| C-007 | Docs-first replan | C4, program protocol | Promoted to `STOPPED_FOR_REPLAN` behavior |
| C-008 | Lane ownership | C4, program protocol | Discovered work needs an authorized coordinate |
| C-009 | Forge commands | Adapter, local profile | Retired from universal content |
| C-010 | Risk-selected verification | C5, verification protocol | Promoted to blast-surface selection |
| C-011 | Identifier and packaging sweeps | Software profile | Valuable repository-specific preflight |
| C-012 | Gold goal state | Program protocol | Separated from execution and live control |
| C-013 | Exact revision evidence | C1, C5, EvidenceRecord | Generalized to exact artifact receipts |
| C-014 | Control-block accumulation | Program protocol, casebook | Corrected with one live control and a decision ledger |
| C-015 | Shared verification selector | C6, verification protocol | One classification drives local and remote gates |

## AutoAgent experiment loop

| ID | Source concept | Destination | Disposition |
| --- | --- | --- | --- |
| A-001 | Baseline first | Experiment protocol | Retained as first mandatory experiment step |
| A-002 | One general change | Experiment protocol | Makes results interpretable |
| A-003 | Keep or discard | Experiment protocol | Metric-based acceptance retained |
| A-004 | Fresh environment | C5, experiment protocol | Prevents carried state from moving the score |
| A-005 | Protected invariants | WorkContract, experiment protocol | Improvements cannot regress protected behavior |
| A-006 | Overfitting test | C7, experiment protocol | Promoted as generalization check |
| A-007 | Simplicity tie-breaker | C7, experiment protocol | Equal verified results prefer simpler systems |
