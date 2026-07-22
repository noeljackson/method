# Supply-chain scan: 2026-07-21

Release conclusion: **the strict scan is green for this worktree.** No
supply-chain indicator, dependency advisory, workflow issue, or secret finding
was reported.

## Coordinates

- Target Method base HEAD: `c74fee849b481770ff6da696cf7527cab63c9acf`
- Scanner base HEAD: `ac3e803b984e7c95ac8145a78548a0610f8b8b8b`
- Target: the current dirty Method worktree containing the v0.2 remediation
- Scanner: the current dirty supplychain worktree containing the tested
  docs-only OSV classification change

## Scanner change

The scanner now distinguishes three OSV states: `completed`, `unavailable`,
and `not_applicable`. OSV Scanner's explicit `No package sources found` result
maps to `not_applicable`; a missing tool or other execution failure still fails
closed under strict policy. Human and JSON reports expose the distinction.

The scanner's full Go test suite passed after the change.

## Strict result

Command:

```sh
go run . ci /home/noel/src/codewire/method --no-update
```

Result: exit status 0.

- Repository and IOC scan: clean.
- OSV: available; `not_applicable` because the Method repository has no
  supported package sources.
- Workflow audit: Zizmor completed without a reported finding.
- Secret scan: completed without a reported finding.
- Bun verification: not applicable because the target has no `bun.lock`.

The corresponding JSON source scan reported `has_hits: false`,
`has_supply_chain_hits: false`, and `has_advisory_hits: false`.

## Final compact-method rerun

After replacing the routed draft with the compact Base plus ContextFlags
design, the strict scan was rerun against the completed worktree:

```sh
/home/noel/src/noeljackson/supplychain/supplychain ci --policy=strict .
```

The first invocation used a stale local executable built before the scanner's
docs-only OSV fix and exited 1 on OSV's `No package sources found` result. The
current dirty scanner source already contained that tested fix; rebuilding the
local executable and repeating the exact command exited 0.

- Repository and redacted secret scan: clean.
- OSV: available and `not_applicable`; no supported package source exists.
- Workflow audit: Zizmor completed without a finding.

No target-repository exception or weakened strict policy was introduced.
