# sdlc field notes - load-bearing evidence behind the SKILL.md rules

The run-specific war-stories that justify several terse rules in `SKILL.md`.
Kept here so the skill stays scannable while the evidence that makes each rule
load-bearing is one click away. Cited inline as "(field-notes: <tag>)".

## E2E platform-tooling

Playwright MCP drives any browser, but Tauri-wrapped or Electron-wrapped apps
need a WebDriver-style native-shell driver (`tauri-driver`,
`electron-chromedriver`). On platforms where the driver is unsupported (e.g.
`tauri-driver` on macOS as of late 2026) the E2E role cannot run as prescribed.
Write the specs with a conditional preflight skip so they activate the moment
the platform gains support, document the gap explicitly in the Phase 3 report
("built, not exercised this platform"), and do not silently fake-green the role.
**Run #6 surfaced this when tauri-driver turned out to be macOS-blocked mid-DAST.**

## Bundled-sidecar staleness

When the slice ships a separate process as a bundled resource (Tauri sidecar,
Electron subprocess, serverless layer), the dev runner may not auto-rebuild the
bundle on source-tree change. DAST against a stale bundle produces
*false-positive* P0/P1 conclusions (the runtime code is older than the diff
under review). Before drawing any DAST conclusion about the slice's runtime
behavior, verify the bundle's source matches the source tree: grep for a recent
identifier in the bundled artifact, compare modification timestamps, or simply
rebuild explicitly. **Run #6 surfaced this when Phase 2 A1' middleware appeared
not to fire — the bundle was weeks-old, not buggy.**

## Local-repo fallback for SAST

The `security-review` skill hard-diffs against `origin/HEAD` and breaks on a
fresh local repo without a remote (or with an unborn `main`). When this happens,
dispatch a SAST subagent over the branch diff (`git diff main..feature-branch`)
— same checklist, manual driver. **Confirmed across three real runs**; the skill
itself is the right idea but the diff target needs to be the local base branch
when no remote exists.

## Provenance — why several SKILL.md rules earned their place (comic-web SEO + landing runs)

These back the terse rules in SKILL.md; the rule stays inline, the story lives here.

- **Loop-back fix is a fork / Code review is a STAGE / Verify findings:** a backend SEO slice's
  7-dimension code review surfaced 14 findings including **two P1 seam defects a green suite
  missed** — a model↔snapshot data-loss (adding `$hidden` made a snapshot/rollback wipe
  credentials) and a probe↔orchestrator credential leak (an api_key reached logs/DB/UI/export
  via an unhandled exception URL). Both fixes reached into **shared infra the focused slice
  never planned to touch** and carried design forks → each went to a council gate before any
  code changed. The Phase-4 pass also raised **four "injection/SSRF" findings on operator-set
  CLI values that were correctly refuted** (no privilege boundary crossed) — hence adversarial
  verify-before-gate.
- **Red-first + delta-SAST (loop-back fix discipline):** a regression guard test **passed for
  the wrong reason** (asserted on a state never set up) until strengthened; a **delta-SAST over
  the fix diff caught a P2 test-honesty defect** a full green suite did not.
- **Sponsor gate + UAT-vs-intent:** the Sponsor gate was **skipped on the backend slice**; on a
  UI slice the produced goal/metrics/guardrails artifact **anchored the plan-sign-off**, and the
  UAT-vs-intent check **caught a system-adaptive default, an absent empty-state, and a dark-mode
  contrast issue** that a green suite did not.
