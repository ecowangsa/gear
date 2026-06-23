---
name: sec
description: Phase 4 of the gear SDLC - Security verification. SAST via /security-review (with local-repo diff fallback), concurrency and seam-zone probes, and DAST via Playwright plus curl, closing every Phase-1 threat-model MUST. Use to security-verify a slice. Triggers on "security review", "SAST", "DAST", "pentest", "close the MUSTs".
---

# sec - Security verification (gear SDLC Phase 4)

Security-verify a slice with SAST and DAST, closing every Phase-1 threat-model MUST-ID.
This is Phase 4 of the gear:sdlc pipeline; it also runs standalone. One model voicing the
Security role, honest by design, not a separate expert.

Each MUST-ID closure surfaces as a defect-register row (verified-clean or a finding); that
register is tracked by the gear:sdlc orchestrator, not by this skill. When running standalone,
maintain a local defect register in the same format so results are portable back to the
orchestrator.

### Phase 4 - Security verification (the role that was missing)
| Activity | Type | Maps to | Output |
| --- | --- | --- | --- |
| SAST / secure code review | STAGE | `/security-review` (CLI built-in, not a plugin skill) on the diff (see local-repo fallback below) | injection / authz / secret / crypto findings |
| Concurrency probe | STAGE | included in SAST when the slice adds any **multi-write code path** (a new endpoint or call site that mutates shared state, esp. through a sync route hitting FastAPI's threadpool) | races, lost updates, inconsistent reads |
| Seam-zone probe | STAGE | included in SAST whenever the slice (a) **deviates from the spec's implementation choice** (e.g. regex instead of the spec'd parser library), or (b) introduces a new boundary between layers (cache + policy, parser + orchestration, etc.). Build-time review cannot see these seams because they are *inter-stage* by construction. | misuse-of-deviation findings, content-spoofing, parser-ambiguity edge cases |
| DAST / pentest | STAGE* | **Playwright MCP** for browser-level probes (XSS, IDOR, authz bypass) **+ `curl` / raw HTTP for protocol-level probes** + OWASP checklist | dynamic findings |

`*` **Honest limit.** Deep pentest (Burp / ZAP, fuzzing) is manual / tooling outside
Claude. The recipe *points* to it; it does not pretend to automate it. What is
automatable here: `security-review` (static) plus light Playwright probing (dynamic).

**Local-repo fallback for SAST.** When `security-review` breaks on a fresh local repo
without a remote (it hard-diffs against `origin/HEAD`), dispatch a SAST subagent over the
branch diff (`git diff main..feature-branch`) - same checklist, manual driver. (field-notes:
local-repo fallback.)

**Why `curl` alongside Playwright for DAST.** Chromium blocks HTTP/1.1 request
streaming and rejects some header manipulation; SSRF probes via chunked uploads,
explicit `Content-Length` bypass attempts, or `Transfer-Encoding: chunked` need a
non-browser client. Pair Playwright (DOM/UI surface) with `curl` (protocol surface).

**DAST when there is no browser / HTTP surface** - *provisional (n=1); full guidance + why
it is provisional are in the **Watch list** of the gear:sdlc orchestrator skill.* Gist: when a slice
exposes no web surface (backend probes, CLI, a library, an encrypted column), retarget DAST
to the runtime that exists and **prove the security claim with a real command, not by
reasoning**. The honest-limit note above still applies.

**Bundled-sidecar staleness pre-check for DAST.** If the slice ships a bundled separate
process (Tauri sidecar, Electron subprocess, serverless layer), the dev runner may not
rebuild it on source change - DAST against a stale bundle gives *false-positive* P0/P1.
Before any DAST conclusion, verify the bundle matches the source tree (grep a recent
identifier, compare mtimes, or rebuild). (field-notes: bundled-sidecar staleness.)

## Verify findings before they gate

A finding from SAST / DAST is a **claim, not yet a fact**. Before its severity drives
a loop-back, **adversarially verify each finding**: an *independent skeptic, refute-by-default*,
reads the actual code and rules it **confirmed / refuted / severity-adjusted**, grounded in
file:line. This kills false positives and stops a confident-but-wrong severity from blocking
the run; record each verdict + reasoning in the defect register. (field-notes: a Phase-4 pass
correctly refuted four "injection" findings on operator-set CLI values - no boundary crossed.)

## Discipline / honesty rules

- **GATE != subagent.** Security verification is a STAGE, not a headcount exercise. Do not
  spawn a subagent per job title / persona; run the mapped tools and one skeptical verifier pass.
- **Many hats, one head.** One model voices the Security role, honest by design.
- **Security is shift-left, shift-right, and *traced*.** Phase 4 must close every MUST-ID from
  the Phase-1 threat model; each surfaces as a defect-register row. A design-time security
  requirement cannot silently go unverified.
- **Scale to the change.** Use the lite lane for small fixes; run the full SAST + DAST for
  changes that touch auth, crypto, shared state, or any externally reachable surface.
