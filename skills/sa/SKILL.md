---
name: sa
description: Phase 1 of the gear SDLC - Design and Architecture. Produce a design plus implementation plan (feature-dev code-architect + writing-plans) and a threat model with numbered MUSTs via gear:council --preset safeguard. Use to design and threat-model before building. Triggers on "design this", "architecture", "threat model", "plan the implementation".
---

# sa - Design and Architecture (gear SDLC Phase 1)

Produce a design and implementation plan, then run a shift-left threat model to surface
numbered MUSTs that Phase 4 security must later close. This is Phase 1 of the gear:sdlc
pipeline; it also runs standalone. One model voicing the SA/Architect role, honest by
design, not a separate expert.

## Role table

| Role | Type | Maps to | Output |
| --- | --- | --- | --- |
| SA / Architect | STAGE | `feature-dev:code-architect` *(subagent, not a skill)* + `writing-plans` (skill) | design + implementation plan |
| Security (shift-left) | GATE | `/gear:council --preset safeguard` (threat / obligation / operability) | threat model + **numbered MUSTs (T1, T2...)** folded into the plan |
| Plan sign-off | GATE | human approves the plan | go / no-go |

For a UI design decision you may surface mockups via brainstorming's visual companion (offered in gear:pm); the UI itself is built with frontend-design in gear:dev.

## Threat model and traceability

The security shift-left gate runs `/gear:council --preset safeguard` and produces
numbered MUSTs (T1, T2...) that are folded directly into the implementation plan. Plan
sign-off is a human gate: the orchestrator (gear:sdlc) parks at `awaiting-gate` until
the human approves. When running standalone, present the plan + threat model and wait
for explicit go/no-go before handing off.

The T-numbered MUSTs are not advisory: Phase 4 SAST must close every MUST-ID, each
surfacing as a defect-register row (verified-clean or a finding), so a design-time
security requirement cannot silently go unverified. A threat model that re-scopes the
slice entirely (finding the core approach unsafe, not merely adding MUSTs) is the gate
working correctly - record it as a Phase-1->Architecture loop-back and split rather than
bolt mitigations onto an unsafe original. (field-notes: a safeguard panel found a planned
"isolation" was not containment at all and re-scoped a slice to read-only plan-mode MVP,
deferring the dangerous write capability to a follow-up slice that re-runs the panel first.)
