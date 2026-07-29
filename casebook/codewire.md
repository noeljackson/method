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

### Control activity must not replace outcome flow

Observation ID: `C-018`

After the bounded-repair correction, Connect Wave 5 still produced 54
canonical commits between formal entry and the adoption of version 0.6 with
WI-8B ready to begin. Twenty-four were explicitly governance or documentation
control commits before counting selector repairs. Mutation, review,
verification, evidence assembly, and successor readiness were often treated as
one serial activity. The checked-in master and handoff also continued to
present an old coordinate after canonical tracker receipts had advanced the
live state.

The safety decisions remained useful: exact artifacts, recovery boundaries,
and live-state evidence caught real defects. The remaining failure was that
control activity could become work in its own right, while safe non-mutating
support waited behind the mutation claimant and stale projections competed
with the canonical tracker.

Version 0.7 generalizes the correction narrowly. A coordinate has one mutation
claim while non-mutating review, verification, monitoring, and evidence may
run concurrently. Named successor preparation is provisional until refreshed
against its accepted predecessor. Copies of live control identify their source
and revision, and additional ceremony without a named failure, authority
purpose, or downstream evidence consumer is omitted.

## Experiment loop

An agent-harness project inside the same repository added a complementary
lesson: establish an unchanged baseline, make one general improvement, score
it in a fresh environment, keep only improvement or equal-result simplicity,
and retain discarded trials as evidence. This became the experiment protocol.
