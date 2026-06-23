---
name: pm
description: Phase 0 of the gear SDLC - Discovery and Intent. Turn a raw idea into requirements, user stories, and acceptance criteria via brainstorming, and produce the 3-line sponsor artifact (goal / success metrics / scope guardrails). Use standalone to scope or clarify a slice, or as the first phase gear:sdlc runs. Triggers on "scope this", "what are the requirements", "discovery", "intake a feature".
---

# pm - Discovery and Intent (gear SDLC Phase 0)

Turn a raw idea into requirements, user stories, and acceptance criteria, and produce
the sponsor artifact. This is Phase 0 of the gear:sdlc pipeline; it also runs standalone.
One model voicing the PM/BA role, honest by design, not a separate expert.

## Role table

| Role | Type | Maps to | Output |
| --- | --- | --- | --- |
| Sponsor / CEO | GATE | human; `/gear:council` if direction is contested | goal, success metrics, scope guardrails |
| PM / BA | STAGE | `brainstorming` | requirements, user stories, acceptance criteria |

## State-trigger discipline

When a requirement defines a UI/UX state (empty, no-results, error, loading), the
acceptance criterion must answer **when does this state actually trigger** given the
backend's real semantics, not just **is this state implemented**. A state that is
defined but unreachable in practice is theater; a state whose trigger depends on a
backend change must either include that change in the slice or be explicitly deferred.
This rule emerged from a real catch at E2E in a run where a "no-results" message was
shipped but never reached because the search endpoint always returned top-k.

## Sponsor/CEO gate artifact

The Sponsor/CEO gate is cheap but NOT a rubber-stamp - produce a 3-line artifact (or
it gets skipped): **(1) Goal** - one sentence; **(2) Success metrics** - >=1 *measurable*
check, before->after where it applies; **(3) Scope guardrails** - what's in, and explicitly
what's *out / untouched*. Contested direction -> `/gear:council`. (field-notes: skipped on a
backend slice; on a UI slice the artifact anchored sign-off.)

## Task backlog (the contract gear:sdlc executes)

Beyond requirements, pm emits a **backlog**: an ordered list of **work units** that
gear:sdlc schedules and fans out. Each work unit conforms to the schema in gear:sdlc's
`references/task-contract.schema.json` (worked example: `references/task-contract.example.json`).
A unit carries: `id`, `goal` (one sentence), `inputs` (files/context), `output_schema` (the
shape of its result), `acceptance` (checkable criteria), `deps` (unit ids that must finish
first), `isolation` (`none`, or `worktree` if it edits files in parallel), and `verify` (how
the result is checked before accept). A precise, schema-bound backlog is what makes results
predictable: gear:sdlc runs each unit against its task-contract instead of guessing.

## UI / frontend slices

When the slice touches a client-facing UI (web components, pages, styling, or UI/UX states),
offer brainstorming's visual companion once, on its own line: *"Want me to mock this up in a
local preview URL (mockups, layout comparisons) while we scope it?"* Offer first, do not
auto-open; declining keeps Discovery in the terminal. Mark the slice as **UI-touching** in the
requirements and in the task backlog, so gear:sa and gear:dev bring the frontend lane (gear:dev
builds UI units with frontend-design). The visual companion lives in the brainstorming skill;
pm only makes sure it is offered for UI work instead of leaving it implicit.
