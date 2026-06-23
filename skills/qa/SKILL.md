---
name: qa
description: Phase 3 of the gear SDLC - QA and the test pyramid. Whitebox (unit+integration), blackbox/contract, E2E (Playwright MCP), and multi-dimensional code review, with off-web retarget guidance. Use to verify a build before security. Triggers on "test this", "QA", "code review", "e2e".
---

# qa - QA and the test pyramid (gear SDLC Phase 3)

Verify a build before security. This is Phase 3 of the gear:sdlc pipeline; it also
runs standalone. One model voicing the QA role, honest by design, not a separate expert.

### Phase 3 - QA / Test (the test pyramid)
| Layer | Type | Maps to | Output |
| --- | --- | --- | --- |
| Whitebox (unit + integration) | STAGE | `test-driven-development` + coverage | green internal tests |
| Blackbox (functional + API / contract) | STAGE | functional / contract tests against the interface (no internals) | green behavior tests |
| E2E / UI | STAGE | **Playwright MCP** (`browser_navigate` / `browser_click` / `browser_snapshot`) | smoke + user-flow regression |
| Static review | **STAGE** | `requesting-code-review` (skill) or the `/code-review` built-in (multi-dimensional for multi-file / security slices) | review findings addressed |

**Code review is a STAGE, not a cheap gate, for any multi-file or security-touching slice.**
A single inline glance under-reads a 15+-file or credential-touching change. Run it as a
*multi-dimensional* review - a reviewer per dimension (DI / seams, correctness, security
surface, tests + spec-conformance) - then **verify the findings** (below). The `GATE != subagent`
rule below bans inflating headcount by *persona / job-title*, **not** the review *dimensions* a
STAGE legitimately fans out. (Lite lane: one cheap single-pass review. field-notes: a 7-dimension
review caught two P1 seam defects a green suite missed.)

**Platform-tooling pre-check for E2E.** Browser-wrapping shells (Tauri, Electron) need a
native-shell WebDriver driver (`tauri-driver`, `electron-chromedriver`); where it is
platform-unsupported, write specs with a conditional preflight skip, document the gap in
the Phase 3 report, and *do not fake-green the role*. (field-notes: E2E platform-tooling.)

**When the slice has no UI / no HTTP surface (off-web), E2E and Blackbox retarget - they
don't vanish.** *(Provisional, n=1 - comic-web Slice B; confirm on a 2nd off-web slice.
Mirrors the non-web-DAST note in Phase 4.)* For a CLI / job / library / internal-service
slice: **E2E** = drive the real entrypoint end-to-end against real (test) infra and assert
the *observable outcome* - exit code, DB / queue state, emitted events, logs - not a browser
flow; **Blackbox** = test the *contract* of that interface (CLI args / flags / exit-codes /
stdout, or the public API/method signature + return), internals kept black-box. Whitebox,
static-review, and SAST are unchanged.
