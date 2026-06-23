---
name: dev
description: Phase 2 of the gear SDLC - Build. Implement a planned slice with subagent-driven-development and test-driven-development (whitebox unit tests first). Also the home of loop-back fix discipline (red-first regression test, delta-SAST the fix). Use to build TDD-first. Triggers on "build it", "implement the plan", "write the code".
---

# dev - Build (gear SDLC Phase 2)

Implement a planned slice test-first. This is Phase 2 of the gear:sdlc pipeline; it also
runs standalone. One model voicing the DEV role, honest by design, not a separate expert.

### Phase 2 - Build
| Role | Type | Maps to | Output |
| --- | --- | --- | --- |
| DEV | STAGE | `subagent-driven-development` + `test-driven-development` | code + unit tests (whitebox) |

### Loop-back fix discipline (Phase-2 work)
When gear:sdlc bounces a finding back to Build, the fix is Phase-2 work held to Phase-2
discipline. (The loop-back log itself is an orchestrator-owned artifact; its table format
lives in gear:sdlc's `references/artifacts.md`.)

**When you loop back to fix a finding** (it is Phase-2 work, held to Phase-2 discipline):
- **Red-first + test-honesty.** Write the regression test first and *watch it fail*; confirm it
  goes red when the defect is present (a test that passes pre-fix proves nothing).
- **Delta-SAST the fix, not just the suite.** A fix is new code on (often shared) surface; before
  re-clearing the gate re-run SAST over the **fix diff** (`git diff` of the loop-back commits),
  not just the full re-run. A green suite is necessary, not sufficient. (field-notes: a guard test
  passed for the wrong reason; delta-SAST caught a P2 test-honesty defect.)

## UI / frontend build units

When a work unit is a UI/frontend change (the slice was marked UI-touching by gear:pm), build
it with the **frontend-design** skill (distinctive, production-grade interfaces that avoid
generic AI aesthetics) alongside test-driven-development, not hand-rolled generic components. If
the frontend-design skill is not installed, degrade to a plain TDD build and **note the gap** in
the phase report - do not silently ship a lower-fidelity UI as if it were designed.
