# Case Study: Codewire

Codewire extended the session-oriented method into a long-running,
multi-workstream program with dependency waves, production evidence, multiple
repositories, and exact release boundaries.

## Lessons retained

### Goal state is not an execution plan

A durable "gold" document defined end conditions and invariants, while
workstream documents described the steps. This let workers test each proposed
change against convergence without treating old steps as current behavior.

Generalized into the program protocol's goal, plan, and live-control split.

### Authorization needs a coordinate

Useful work was unsafe when it could be pulled forward from a later wave or
side lane. Naming every action as Program / Wave / Workstream / Work Item made
the authorized queue reviewable.

Generalized into `C4`, program coordinates, and `ProgramControl`.

### Gates need exact evidence

Observation ID: `C-006`

A green run on an old head, a healthy feature branch, or an accepted source
without matching deployment evidence did not authorize the next irreversible
step. The program reconciled plan, tracker, canonical source, exact-head
verification, exact-main receipts, and live state.

Generalized into `C1`, `C4`, `C5`, and the program dispatch gate.

### Reality changes require docs-first replan

New findings sometimes changed scope, contracts, dependencies, or acceptance
criteria. Continuing "productive" work under the old plan compounded the
mistake. The safe response was to stop mutations, repair the plan, record the
owner decision, and resume at an explicit boundary.

Generalized into `STOPPED_FOR_REPLAN` and the program replan protocol.

### Verification follows blast surface

Running the broadest suite for every edit wasted time and sometimes hid the
actual failure class. A single changed-path classification feeding both local
and remote gates made verification cheaper without creating competing policy.

Generalized into the verification selector and `C6`.

### Live control must not become its own archive

Observation ID: `C-014`

A large master plan accumulated many superseding execution-control blocks.
Although the newest block declared precedence, the live authorization surface
became expensive to read and easy to misapply.

The universal protocol corrects this by allowing one live `ProgramControl` and
moving superseded controls into an append-only decision ledger.

### Secret delivery must stay outside coordination context

Operational workflows needed credentials without making their values part of
the agent transcript or retained evidence. Output-producing secret reads,
shell tracing, environment dumps, observable command arguments, and reliance
on a tool's `silent` flag could all cross that boundary. The safer workflows
used an approved provider to inject values directly into the intended process
and verified only permitted metadata or authenticated behavior.

Generalized into `C8`, the secrets protocol, secret-aware work contracts, and
non-revealing verification. Provider commands, secret paths, and response
owners remain ProjectPolicy content in resolved mode or project-local controls
in direct mode.

### Optional control infrastructure must not become an adoption prerequisite

Observation ID: `C-016`

Codewire pinned Noel Method v0.3.0 in Gitea issue `#1326` and PR `#1327`.
The adopted instruction required a verified RuntimeEnvelope for external or
persistent work, while the same instruction declared that Codewire had no
ProjectProfile or resolver and must remain read-only when one was required.
A later owner-directed program session therefore refused ordinary Gitea
publication even though the repository's canonical program control already
defined the coordinate, gates, and prohibitions.

The failure was not missing care; it was an impossible bootstrap. A universal
method had made optional host infrastructure mandatory based on task shape.
Version 0.4 generalizes the correction by making direct conversational
authority the default, routing protocols by risk, and requiring
ResolvedPermissions only when a consumer explicitly selects and implements
resolved mode.

### Bounded defects must not stop an entire program

Observation ID: `C-017`

During a long Connect migration, the program repeatedly treated defects inside
an already accepted work-item boundary as discoveries that invalidated the
whole plan. It created additional status, correction, and evidence work items,
serialized independent work behind unrelated verification, and required
docs-first resume cycles even when outcome, authority, dependencies, contracts,
external state, acceptance, and recovery boundaries had not changed.

Codewire recorded the corrective program-control decision as WI-M131 and
accepted it through Gitea PR `#1477`.

Some discoveries did change those boundaries, and the full stop correctly
prevented silent scope expansion. The failure was that the Program protocol did
not state the difference. Its broad stop list encouraged conservative actors to
equate a failed implementation hypothesis with an invalid ProgramControl, while
its "one reviewable outcome" language did not tie work-item size to a cohesive
change and recovery boundary.

Version 0.6 generalizes the correction by adding a bounded readiness pass,
right-sizing work items around one recovery boundary, scoping gates to the
actions they block, and keeping the program active for repairs that remain
inside an accepted coordinate.

### Unchanged external state must not become recurring work

Observation ID: `C-018`

During Codewire's Rust web cutover in issue `#1555` and pull request `#1569`,
local product, integration, image, and supply-chain verification had already
produced the evidence needed for development. Remote CI still proved useful:
its Docker-container Buildx driver exposed that a successfully built image had
not been loaded for the verification step. The correction was real and kept
exact-head CI valuable as final attestation.

After that finding, however, healthy 30-to-40-minute jobs were polled roughly
once a minute. Repeated full run state, healthy log tails, and unchanged status
narration added no evidence. The retrospective estimated that only 15-to-25
percent of those observation interactions were needed; six-to-ten meaningful
checks would have captured the binding, failures, retry, corrected head, and
terminal conclusions.

The existing Program rule allowed monitoring to proceed concurrently, but did
not distinguish active evidence work from repeatedly observing a passive
external gate. That omission let persistence be interpreted as continuous
polling and narration.

Version 0.8 generalizes the correction by binding a passive gate once,
observing it on transitions or decision-relevant triggers, and treating an
unchanged healthy result as no new work. Actionable authorized work continues;
when none remains, ending the current observation iteration preserves the
durable objective rather than abandoning it.

### Coordination procedure must inherit unchanged decisions

Observation ID: `C-019`

During a later Codewire methodology audit, canonical issue state, current
comments, and a checked-in master named different frontiers. Agents repeatedly
restated coordinates and authority, reloaded historical controls, reconciled
unchanged state before routine actions, and turned bounded repairs and CI waits
into new receipt cycles. Separately, an authorized merge triggered existing
repository CI that published support artifacts with configured credentials;
the session paused as though it had initiated a new credential operation.

Version 0.7 already required one live control, omitted ceremony without a
consumer, and kept bounded defects local. It did not state clearly enough that
goal, plan, and control were logical concerns rather than separate artifacts;
that a claim and admission persist across routine actions; that archived state
is opt-in context; or that a declared unchanged automatic consequence belongs
to its authorized triggering action. Conservative actors therefore rebuilt
procedure without controlling another failure.

Version 0.8 generalizes the correction by loading only relevant archived
evidence, binding claims once, reconciling material transitions, inheriting an
unchanged admission across repair and verification, reporting outcomes rather
than unchanged state, and bounding automatic-consequence authority. Repository
workflow names, environments, credential mechanisms, and risk tiers remain
project-local policy.

### Passive-gate discipline also belongs to direct work

Observation ID: `C-020`

Codewire pull request `#1688` changed only repository agent policy. Its focused
local policy gate passed, while required exact-head CI continued remotely. A
transition-aware `tea actions runs watch` invocation was useful because it
could surface failure or completion promptly without repeated model polling.
The session nevertheless narrated an unchanged partial job state and fetched
the full run again before a transition made that inspection relevant.

The existing Program protocol already prohibited recurring unchanged-state
work, but direct-mode documentation and small source tasks do not load Program.
The Kernel's general instruction to omit unchanged reports also did not say
clearly that a transition-aware observer is permitted or when detailed
diagnostics become useful. A conservative correction could therefore ban
watching entirely and delay useful failure feedback.

Version 0.8.1 generalizes the distinction in Kernel verification: bind a
passive gate once, allow transition-aware observation when early failure or a
terminal result matters, create no work from unchanged state, and inspect
diagnostics after failure, inconsistency, empty output, or credible stall.
Codewire's workflow selector independently scheduled broad product checks for
this policy edit; that proportionality problem remains repository-local and is
not evidence against transition-aware observation.

### Unknown failure must drive diagnosis, not ceremony

Observation ID: `C-021`

During Codewire's confidential-storage live acceptance, an unclassified Talos
apply result triggered six diagnostic issue and pull-request cycles (`#1697`,
`#1698`, `#1700`, `#1702`, `#1703`, and `#1706`) and nine guarded saved-plan
apply attempts. The changes expanded redacted error taxonomy and tracing while
preserving the nodes and avoiding partial mutation, but they did not first
prove which execution layer failed. Only a later local trace established that
the saved-plan path had never called the provider lifecycle operation being
diagnosed.

The live control also treated unknown classification as a reason to stop the
Program and seek new authority for read-only provider diagnosis. That confused
a scoped retry gate with the authority boundary already granted for diagnosis
and recovery. The safety controls prevented an uncontrolled live mutation, but
the sequence multiplied source changes, plans, CI turns, and live attempts
without producing a discriminating observation early.

The prior Kernel rule required a changed hypothesis before retry, but a new
label or speculative instrument could satisfy that wording without localizing
the failure. Version 0.8.1 generalizes the correction: preserve the evidence,
localize the failing layer, and permit another side effect only when a changed
input predicts a discriminating result or canonical policy identifies a
transient failure. An unknown result freezes that mutation; it does not freeze
read-only diagnosis, independent authorized work, or the whole Program.

### Verification retry authority follows effects

Observation ID: `C-022`

On Codewire's Infra pull request `#313`, focused source and security checks
passed for the exact head. The required infrastructure check later failed in
an unrelated `pentest-scanner` remote read, using the repository's fixed
`remote read failure` class. The agent correctly avoided attributing the
failure to the proposed source, but stopped and requested separate authority
to rerun the unchanged verification-only workflow.

The Kernel grouped every manual retry with recovery and reconfiguration when
describing automatic-consequence authority. That safely excluded a retry of a
publishing or state-mutating workflow, but also made the user-interface action
of rerunning a read-only check more important than its effect. The Verify rule
already allowed canonical transient retries, so the two rules together said
when a retry was justified while leaving routine delivery blocked on duplicate
approval.

Version 0.8.2 classifies the retry by effect. Retrying unchanged
verification-only work under a canonical transient policy inherits the
authorized action. A manual action capable of publication, deployment,
release, recovery, live mutation, or direct credential handling remains
separate. Repository policy still defines what counts as verification-only and
which failures are transient.

## Experiment loop

An agent-harness project inside the same repository added a complementary
lesson: establish an unchanged baseline, make one general improvement, score
it in a fresh environment, keep only improvement or equal-result simplicity,
and retain discarded trials as evidence. This became the experiment protocol.
