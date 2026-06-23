# Changelog

All notable changes to the Gear plugin are documented here. Format loosely
follows [Keep a Changelog](https://keepachangelog.com/); versions use semver.

## 0.13.0 - 2026-06-23

### Added
- Frontend lane. For UI/frontend slices, gear:pm now offers brainstorming's visual companion
  (mockup + local preview URL) during Discovery and marks the slice UI-touching, and gear:dev
  builds UI work units with the frontend-design skill (degrading to a plain build, with a noted
  gap, if frontend-design is not installed). gear:sdlc preflight lists frontend-design as a soft
  dependency.

## 0.12.0 - 2026-06-23

### Added
- New skill gear:triage, the JUDGES-to-ACTS bridge. It turns a council verdict, code/security
  review, or findings list into a prioritized remediation backlog (P0..P3, sequenced, mapped to
  an sdlc owner, with done-criteria) conforming to the existing task-contract schema, then offers
  gated handoffs to gear:retro (save the plan) and gear:sdlc (execute it). gear:council now offers
  a triage handoff after rendering a verdict.

## 0.11.0 - 2026-06-23

### Changed
- Renamed the 9 council lenses to plain domain labels for clarity: Security, Cost & Performance,
  Maintainability, Simplicity, Scalability, Usability, Operability, Compliance & Privacy, and
  Contrarian (Chair unchanged). Unified the lens ids into one scheme across roles.md, SKILL.md,
  and the showcase. Lens descriptions are unchanged; only names and ids changed.

## 0.10.0 - 2026-06-22

### Added
- Multi-agent execution. gear:pm now emits a schema-bound backlog of work units (the task
  contract: skills/sdlc/references/task-contract.schema.json + a worked example). gear:sdlc
  consumes it and fans independent units out across agents: inline subagents by default,
  escalating to a Workflow harness for large fan-out, with git-worktree isolation for parallel
  edits and adversarial verification of each unit before accept. Zero-dep contract test added.

## 0.9.0 - 2026-06-22

### Changed
- Split `gear:sdlc` into a thin orchestrator plus six standalone role skills: `gear:pm` (Phase 0),
  `gear:sa` (1), `gear:dev` (2), `gear:qa` (3), `gear:sec` (4), `gear:tw` (5). The orchestrator keeps
  the spine (preflight, iterative flow, cross-phase artifacts, the human GATEs, the Watch list) and
  delegates each phase's STAGE work to its role skill; every role skill also runs standalone.
- Moved the zero-dep `md2docx.py` helper to `gear:tw` (Phase 5 docs).

## 0.8.0 - 2026-06-22

### Changed
- **Rebrand wayang -> gear.** The plugin, its skills, scripts, hooks, manifest, and
  tests are renamed and fully de-themed to plain SDLC vocabulary.
  - **Skills renamed:** `dalang -> sdlc`, `punakawan -> council`, `batara -> retro`
    (directories, frontmatter `name`, and all `/wayang:*` invocations now `/gear:*`).
  - **Full de-theme:** the council panel now uses functional lens names (Threat Modeler,
    Cost Realist, Change Steward, Restraint Keeper, Scale Forecaster, Consumer Advocate,
    Operability Watch, Obligation Officer, Contrarian) and a plain **Chair** synthesizer
    in place of the wayang-character names.
  - **Retro store moved** from `~/.claude/batara` to `~/.claude/gear`, with the env vars
    renamed to the `GEAR_*` namespace (`GEAR_HOME`, `GEAR_PROJECTS_DIR`, `GEAR_MAX_BYTES`,
    `GEAR_SKILLS_DIR`).
  - **Hooks repointed** to `skills/retro/scripts/retro.py` (`detect` at SessionEnd,
    `nudge` at SessionStart).
  - All tests green after the rename.

## 0.7.0 - 2026-06-22

### Added
- **Triangle integration (segitiga): dalang/punakawan -> batara.** Closes the two edges into
  batara, completing the cycle (dalang ACTS, punakawan JUDGES, batara REMEMBERS).
  - **dalang Phase 5:** an opt-in end-of-arc "harvest via batara" offer that hands batara an arc
    summary (decisions, P0/P1 defects, loop-back lessons, MUST-ID closure). Declining writes nothing.
  - **punakawan:** an opt-in post-verdict "save via batara" offer that hands batara the verdict.
  - **batara handoff mode:** a handed-off summary is treated as the primary candidate material,
    still classified, deduped, GATED, and routed as usual. Reflecting on the transcript is the fallback.
  - Structural tests for all three points (`tests/test_integration_segitiga.py`). Doc and
    orchestration only: no `batara.py` or hook changes.

### Fixed
- Dropped a redundant `hooks` declaration from the plugin manifest; added a manifest test
  (`tests/test_plugin_manifest.py`) to guard against regressions.

## 0.6.0 — 2026-06-20

### Added
- **batara graduate + skill-lesson diff (B4).**
  - **skill-lesson route is now live:** when batara harvests a lesson about how a wayang skill should
    behave, it emits an applyable **unified diff** to that skill's `LESSONS-FROM-RUNS.md` (creating the
    file if absent). batara never touches the repo - you apply + commit it in your wayang clone.
  - **`/wayang:batara evolve`:** graduate mature reusable-technique candidates into a standalone
    personal skill under `~/.claude/skills/<name>/` (auto-loads next session). Gated: drafts a
    SKILL.md, confirms with you, then `install-skill` (slug-validated, refuses clobber without
    `--force`) and marks source candidates `promoted` (exempt from prune).
  - Helper subcommands: `batara.py lesson-block | promote | install-skill`.
  This completes the batara loop (B1 reflect/route -> B2 auto-harvest -> B3 TTL/prune -> B4 graduate).

## 0.5.0 — 2026-06-20

### Added
- **batara candidate TTL + prune (B3).** Reusable-technique candidates that age past their
  `ttl_days` without graduating can now be pruned. `/wayang:batara prune` runs a **gated** flow:
  dry-run (`batara.py expired` lists slugs past TTL; `status: promoted` exempt; unreadable `created`
  kept conservatively) → shows each candidate's age + confidence → on your confirmation deletes the
  approved ones (`batara.py remove <slug>`, path-traversal guarded). Permanent delete; never
  automatic. Confidence is unchanged (informational, for B4 graduation).

## 0.4.0 — 2026-06-20

### Added
- **batara auto-harvest (B2, K2-minimal).** wayang's first hooks:
  - `SessionEnd` detector (zero-LLM) self-gated to **wayang** sessions: when a session shows a reusable
    signal, it stages a silent pointer to `~/.claude/batara/pending/` — it never writes the real stores.
  - `SessionStart` passive nudge: one line announcing pending lessons (no per-turn nagging).
  - `/wayang:batara --since <date>` sweeps past project transcripts on demand.
  - Helper subcommands: `batara.py detect | nudge | pending | harvested`.
  The confirmation gate is unchanged — nothing reaches memory/candidate stores without your OK.
  (Design adjudicated by a Punakawan panel: SessionEnd over per-turn Stop, self-gated over global,
  silent-stage over chatty nudge.)

## 0.3.1 — 2026-06-20

### Changed
- **`/wayang:batara` dedup awareness.** Sebelum menampilkan kandidat di gate, batara kini
  memeriksa candidate store dan memori proyek; lesson yang sudah tersimpan ditandai DUPLICATE
  dan default di-skip (disebut lokasinya), bukan diusulkan ulang. Helper dapat subcommand
  `batara.py list --long`. ("Perkuat/merge" kandidat duplikat menyusul di rilis berikutnya.)

## 0.3.0 — 2026-06-20

### Added
- New skill **`/wayang:batara`** — wayang's reflection/memory leg (dalang ACTS, punakawan
  JUDGES, batara REMEMBERS). On demand, it reflects on the current session, classifies each
  reusable lesson (project-fact / skill-lesson / reusable-technique), scores confidence, and
  — only on your confirmation — routes project-facts to the per-project memory store and
  reusable-techniques to a new `~/.claude/batara/` candidate store. Skill-lessons are
  presented as a proposed diff. Stdlib-only helper `scripts/batara.py`; no third-party deps.
  (Session-end auto-detect hook, past-session sweep, TTL/prune, and graduate-to-skill land in
  later releases.)

## 0.2.0 — 2026-06-20

### Breaking
- Consolidated into a single `wayang` plugin: the SDLC executor and the advisory panel
  now ship as the co-located sibling skills `/wayang:dalang` and `/wayang:punakawan`.
- Install: `/plugin marketplace add ecowangsa/wayang` then `/plugin install wayang@wayang`.

### Changed
- `skills/sdlc/` -> `skills/dalang/`; `skills/panel/` -> `skills/punakawan/` (directory + frontmatter `name`).
- Punakawan showcase assets (`preview.sh`, `sidang.json`, `index.html`, `samples/`, `assets/`)
  moved under `skills/punakawan/`; `${CLAUDE_PLUGIN_ROOT}` references repathed accordingly.
- Removed the `dalang -> punakawan` plugin dependency (now co-located sibling skills).
