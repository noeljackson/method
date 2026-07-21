# Supply-chain scan: 2026-07-20

Release conclusion: **the strict scan is not green.** The findings inspected
in this repository are tool-policy mismatches rather than identified malicious
dependencies or exposed credentials, but they still prevent claiming that the
strict policy passed.

## Scanner identity

- Scanner repository:
  `/home/noel/src/noeljackson/supplychain`
- Scanner commit: `ac3e803b984e7c95ac8145a78548a0610f8b8b8b`
- Installed version: `supplychain v0.1.3-24-gac3e803`
- Target Method HEAD: `c74fee849b481770ff6da696cf7527cab63c9acf`

The target worktree was dirty. This report covers the completed local tree,
including the frozen confirmatory eval artifacts.

## Strict result

Command:

```sh
supplychain ci --policy=strict .
```

Result: exit status 1.

- OSV advisory check: failed because the docs-only repository contains no
  supported package or lockfile source. A direct OSV scan reports `No package
  sources found`; no `package.json`, Python package manifest, Go module, Cargo
  manifest, or equivalent dependency source exists.
- Workflow audit: clean. Zizmor completed against
  `.github/workflows/ci.yml` without a reported finding.
- Secret policy: failed with four Gitleaks `generic-api-key` matches.

## Gitleaks triage

All four matches were scanned with redaction and inspected structurally. Each
is the JSON key `protocols/secrets.md` adjacent to its generated 64-hex SHA-256
digest:

| File | Line in this scan | Classification |
| --- | ---: | --- |
| `dist/pack/MANIFEST.json` | 11 | Generated file digest; false positive |
| `evals/runs/smoke-v2-2026-07-20/run.json` | 204 | Frozen input digest; false positive |
| `evals/runs/pilot-2026-07-20/run.json` | 404 | Frozen input digest; false positive |
| `evals/runs/confirmatory-2026-07-20-v1/run.json` | 4723 | Frozen input digest; false positive |

No matched value was printed or copied into this report. Each value was
validated only as a full lowercase SHA-256-shaped string. A broad path or rule
exemption was deliberately not added: those JSON files could contain a real
secret in a different field.

## Degraded non-OSV scan

Running `supplychain scan --no-update --json .` with OSV intentionally
unavailable produced:

- `has_hits: false`
- `has_supply_chain_hits: false`
- no manifest, lockfile, payload, persistence, script, freshness, typosquat,
  signature, maintainer-change, or drift findings

This is useful negative evidence for the scanner's built-in IOC checks. It is
not a substitute for the failed strict command and does not perform advisory
or secret scanning.

## Required remediation

1. Teach `supplychain ci` to record dependency scanning as explicit `N/A` for
   a repository with no supported dependency source, rather than converting
   OSV's no-source result into a strict failure.
2. Add a narrow, tested Gitleaks exception that requires both the exact
   `protocols/secrets.md` JSON key and a complete SHA-256 digest value. Do not
   exempt whole run directories, manifest files, or the generic API-key rule.
3. Add scanner regression fixtures for docs-only repositories and
   path-plus-digest JSON records.
4. Rerun the strict command after those scanner-policy changes and preserve its
   version, exit status, and redacted findings in the release evidence.

Until that rerun exits successfully without suppressing unrelated findings,
the supply-chain release check remains unresolved.
