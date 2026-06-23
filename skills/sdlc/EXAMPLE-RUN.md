# sdlc - worked example of a run's artifacts

> **NOT A REAL RUN. NOT COUNTED.** This file is a *dry-run-zero*: a synthetic,
> illustrative example of what sdlc's three artifact tables look like when
> filled in, built to shake out the mechanics and to serve as a concrete sample
> for the eventual conductor skill. It is **explicitly not one of the ~3 real
> hand-runs** that gate promotion (see RECIPE.md "Promotion trigger"). No code was
> written, no tests were run. The council panel that produced RECIPE.md was
> emphatic on this point: a dogfood/synthetic run must never be silently counted
> as evidence, because the promotion gate turns on *real* friction from *real*
> work. Treat the tables below as a template-with-data, nothing more.

## The example scenario (invented)

A small but security-relevant, public-facing change - the kind that warrants the
**full** lane:

> **Feature:** Add per-IP rate limiting to `POST /api/contact` (public,
> unauthenticated) to stop spam/abuse.

It is chosen because it exercises every phase, including security shift-left
(threat model at design) and shift-right (SAST + DAST), and it naturally produces
a **loop-back** (a P1 security finding bounces back to DEV before the commit gate)
so the iterative discipline is visible rather than a clean waterfall.

## Phase log - which role mapped to which skill, in order

This is the part that tests the role -> skill mapping in RECIPE.md as an actual
sequence, not just a table.

| # | Phase / role | Skill or tool invoked | What came out |
| --- | --- | --- | --- |
| 0 | PM / BA | `brainstorming` | 4 requirements (R-01..R-04) + acceptance criteria |
| 1 | SA / Architect | `feature-dev:code-architect` + `writing-plans` | limiter-middleware design + impl plan |
| 1 | Security (shift-left) | `/gear:council --preset safeguard` | threat model: spoofable client IP, counter-map DoS -> folded into plan |
| 1 | Plan sign-off | human GATE | go |
| 2 | DEV | `subagent-driven-development` + `test-driven-development` | limiter middleware + unit tests |
| 3 | Whitebox QA | `test-driven-development` + coverage | unit/window tests green |
| 3 | Blackbox QA | contract test against the interface | 6th request -> 429 (green) |
| 3 | E2E / UI | Playwright MCP | spam-the-form flow -> raised **D-02** |
| 3 | Static review | `code-review` | raised **D-03** |
| 4 | SAST | `security-review` on the diff | raised **D-01 (P1)** -> loop-back to DEV |
| 4 | DAST | Playwright MCP probe + OWASP checklist | **D-04** closed, no finding |
| 5 | TW | docs/changelog (`context7` for lib docs) | 429 behavior + limit documented |
| 5 | Verification | `verification-before-completion` | all green after D-01 fix |
| 5 | UAT / End User | human GATE | accepts: spam stopped, legit users unaffected |
| 5 | Commit / Release | **hard human GATE** + worktree sandbox | *stops here - sdlc never auto-commits* |

## Run-board (phase status)

| Phase | Status | Note |
| --- | --- | --- |
| 0 Discovery | done | PM clarified: 5 req/min/IP; 429 + Retry-After on exceed |
| 1 Design | done | threat model added 2 risks (IP spoofing, counter-map DoS); folded into plan |
| 2 Build | done | limiter middleware + unit tests via TDD |
| 3 QA | done | unit/contract green; e2e raised D-02; static review raised D-03 |
| 4 Security | looped-back -> done | SAST raised D-01 (P1) -> back to DEV; re-verified green; DAST clean |
| 5 Docs/Release | blocked | parked at the hard human commit gate (awaiting human go) |

## Defect / findings register

| ID | Source | Severity | Title | Status |
| --- | --- | --- | --- | --- |
| D-01 | Sec-SAST | P1 | Rate limit keyed on client-controlled `X-Forwarded-For` -> trivially bypassable | fixed (looped back to DEV) |
| D-02 | QA-e2e | P2 | 429 response missing `Retry-After` header | fixed |
| D-03 | review | P3 | Magic numbers for window/limit (no named constant) | fixed |
| D-04 | Sec-DAST | - | Header-spoof bypass probe + endpoint XSS/IDOR scan | closed - no finding |

The open **P1 (D-01)** is what bounced the run back to DEV before it could reach
the commit gate - exactly the "any open P0/P1 loops back" rule in RECIPE.md.

## Traceability

| Requirement | Test(s) | Result |
| --- | --- | --- |
| R-01: limit to 5 req/min per client IP | unit `limiter_window` + contract `contact_429` | pass |
| R-02: on exceed, return 429 + `Retry-After` | contract `contact_429` + e2e `contact_spam_ui` | pass (failed first -> D-02 -> fixed) |
| R-03: not bypassable via client-controlled headers | SAST review + e2e/DAST spoof probe | pass (failed first -> D-01 -> fixed) |
| R-04: legitimate users under the limit unaffected | unit `limiter_underlimit` + e2e `contact_happy` | pass |

## Mechanics notes (the actual point of this dry-run)

Honest friction observed while filling the tables in - this is the feedback that
should inform the eventual promotion decision, captured so it isn't lost:

1. **Run-board "Status" vocabulary needs a terminal value for the human gate.** A
   phase can be `done`, but the *run* ends in a deliberately non-terminal
   "awaiting human" state at commit. "blocked" (used above) overloads the same
   word used for being stuck on a defect. Consider a distinct `awaiting-gate`
   status so a parked-at-gate run reads differently from a stuck run.
2. **Loop-backs are invisible in a snapshot table.** The run-board shows the
   *current* status; the fact that Phase 4 bounced to Phase 2 and back only
   survives in the "Note" column as prose ("looped-back -> done"). If loop-backs
   are the thing that makes this "professional not waterfall," the artifact should
   record them as first-class events, not a note. A tiny ordered "loop-back log"
   (from-phase, to-phase, trigger defect-id) may be worth a fourth table.
3. **Severity scale is double-defined.** RECIPE.md lists both `P0/P1/P2/P3` and
   `Crit/High/Med/Low`. The example had to pick one (P-scale). The skill should
   commit to a single scale to keep the loop-back rule ("any open P0/P1") crisp.
4. **DAST/"no finding" rows have no severity.** A clean security probe is a real,
   valuable result but doesn't fit the severity column (left as "-"). Findings
   register may want a `result` notion distinct from `severity`, or a separate
   "checks run / clean" line so negative results are still recorded.
5. **The role -> skill phase log (above) is arguably more useful than the
   run-board** for a reader trying to reproduce a run, yet RECIPE.md doesn't list
   it as an output. If the conductor skill is built, consider promoting the phase
   log to a first-class artifact.

None of these are blockers; they are the kind of small, real shape-friction the
~3 real runs exist to confirm or refute. This dry-run can't tell whether they
recur under genuine work - only real runs can.
