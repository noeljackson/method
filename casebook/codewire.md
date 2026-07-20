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
owners remain project-profile policy.

## Experiment loop

An agent-harness project inside the same repository added a complementary
lesson: establish an unchanged baseline, make one general improvement, score
it in a fresh environment, keep only improvement or equal-result simplicity,
and retain discarded trials as evidence. This became the experiment protocol.
