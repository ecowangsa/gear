---
name: sdlc
description: Use when starting any feature slice or significant code change that benefits from phased SDLC discipline - PM brainstorming, design + threat model, TDD build, QA pyramid (whitebox + E2E), SAST + DAST, docs + human commit gate. Drive this whenever the user says "feature slice", "new slice", "tambah feature", "implement X end-to-end", "build Y", or anything indicating a fresh development cycle on a project, even if they do not mention "sdlc" by name. Especially valuable when the change crosses multiple files, touches both backend and UI, has any security surface, or needs visible artifacts (phase log, defect register, traceability) for honest reporting. Orchestrates the gear role skills (pm, sa, dev, qa, sec, tw) with phase gates and loop-backs; each role skill also runs standalone.
---

# sdlc - phased SDLC orchestrator

Drives a feature slice from idea to release across six phases (Discovery, Design,
Build, QA, Security, Docs/Release) with iterative loop-backs and hard human commit gates.

One model voices each business role in turn. That is the honest framing: a single
model wearing all the hats, not a team of independent experts. The value is the
checklist and the gates, not headcount.

## What sdlc is

sdlc is a phased SDLC skill that drives a feature slice from idea to release
through six phases (Discovery -> Design -> Build -> QA -> Security ->
Docs/Release) with iterative loop-backs and hard human commit gates. It is the
executor counterpart to council (advisory). One model voices each business
role in turn, the honest framing being that one model moving all the work is
one model wearing all the hats.

The history of how sdlc was promoted from a recipe to a skill (including the
original five-criterion gate, the council deliberation that introduced and
revised criterion (e), and the load-bearing Contrarian dissent) is preserved in
`references/promotion-history.md` for future readers who want to understand
why the skill exists and what disciplines its design encodes.

**How a new lesson enters this skill (two tracks - so this file does not over-fit
one run).** *Default:* an observation folds into SKILL.md only after **>=2 confirmations
across runs**; until then it lives on the **Watch list** (end of file), not as settled
discipline. *Exception:* a **load-bearing catch** - a single run where the missing rule
would have let a real **P0/P1 slip** - may fold from one run via override (the mechanism
that elevated the concurrency probe after run #2). Mark single-run folds with their
provenance so the next reader can calibrate; a self-graded RED->GREEN is *necessary, not
sufficient* - real validation is an independent second run.

## Relationship to council (the boundary that keeps both clean)

When a council verdict needs a remediation plan before building, gear:triage turns it into a prioritized backlog that this skill then executes.

sdlc and council are **separate citizens** that respect each other's lane:

| | council | sdlc |
| --- | --- | --- |
| Nature | advisory - returns a verdict, never executes | executor - produces real code/tests/docs |
| Units | **lenses** (ways of reasoning), never job titles | **business roles** (job titles) |
| Shape | small parallel panel + gate, cap 5 | iterative role pipeline with loop-backs |

Hard rules so neither drifts:
- sdlc lives in **its own folder**. It never edits council's files (its
  `skills/council/SKILL.md` / `roles.md`), and it never reintroduces job-title names
  into council's lens catalog.
- sdlc **calls** `/gear:council` as an *advisory gate* at a hard fork the controller
  cannot adjudicate solo - a design or security choice, a **loop-back fix that crosses
  the slice boundary**, or a process/governance call. **But skip trivial / one-dimensional
  forks** (council's own rule): the panel earns its cost only on a real multi-tradeoff
  decision, and over-invoking it trains the gate to be ignored. Calling it does not change
  how council works.
- council stays lens-based and advisory; sdlc stays role-based and executive.

## The flow is iterative, not a one-way pipeline

Phases have a default order but **gates can bounce work back**. That is what makes it
professional rather than waterfall:

- QA or Security finds a **defect** -> back to **DEV** (do not proceed).
- **UAT / End User** rejects -> back to **PM / Design** (matching the spec is not the
  same as matching what was wanted).
- A **threat model** opens a new risk -> back to **Architecture**.

**A loop-back fix is itself a fork when it crosses the slice boundary.** The loop-back rule
(any open P0/P1 -> back to DEV) says *when* to bounce, not that you may silently expand the
blast radius. If clearing a finding means editing a file **outside the slice's planned set**
(shared / pre-existing infra) **or** making a real design choice, **STOP and escalate first** -
human re-scope and/or `/gear:council` - before writing the fix. This discipline lives here, not in
the user's CLAUDE.md. (field-notes: two Slice-B P1 fixes hit this.)

**Tailor to change size.** A one-line fix does not need the full pipeline. Two lanes:
- **lite** - PM (clarify) -> DEV (TDD) -> static review -> verification -> commit gate.
- **full** - every phase below, including security shift-left and the QA pyramid.

## Multi-agent execution (how the orchestrator fans out)

gear:sdlc consumes the backlog gear:pm emits (the `task-contract`: see
`references/task-contract.schema.json`). It schedules the work units, fanning independent
ones out across agents so a slice finishes fast with predictable results.

- **Hybrid, tiered engine.** Default: dispatch subagents inline (one per ready unit,
  honoring `deps`), which works in any session with no setup. Escalate to a **Workflow**
  harness (pipeline/parallel + schema-validated output + isolation + verification) when
  fan-out is large: more than 6 independent ready units, OR two-or-more units with
  `isolation: worktree`. One contract drives both paths.
- **Isolation.** Any unit with `isolation: worktree` runs in its own git worktree, so
  parallel file edits never collide; results merge only after they pass verify.
- **Adversarial verify before accept.** Each unit's result is checked against its
  `acceptance` by an independent skeptic (refute-by-default) reading the real code;
  `verify.votes > 1` runs that many skeptics and accepts on majority. This reuses the
  "Verify findings before they gate" discipline below.
- **No silent truncation.** If the orchestrator caps fan-out (top-N, sampling, no-retry),
  it logs what was dropped; silence reads as full coverage when it was not.
- **Honesty.** Parallel agents for speed (decomposed independent work) are distinct from
  parallel agents for judgment (council, verification). Both are one model. This is not a
  team of independent experts; the value is the contract, the gates, and honest artifacts.

## Preflight - confirm the toolchain before Phase 0 (run once, fail loud)

sdlc's phases map onto external skills, plugins, MCP servers, and CLIs. A missing one
mostly **degrades silently** - the worst failure for a skill whose whole value is *honest
reporting* (it would file artifacts claiming coverage a missing stage never gave). So
**before Phase 0, check the toolchain and surface what's absent with the exact install
command - never silently skip a stage.**

| Need | Kind | If absent |
| --- | --- | --- |
| `git` | CLI | the sandbox / branch / diff / commit-gate **safety spine** breaks - **stop** |
| `superpowers` | plugin | Phase 0 `brainstorming`, Phase 2 `subagent-driven-development` + `test-driven-development`, Phase 5 `verification-before-completion` + `finishing-a-development-branch` are all gone - **stop** |
| `council` | skill | Phase 0 contested-direction gate + **Phase 1 threat model** (the source of the T1/T2 MUSTs Phase 4 must close) cannot run - **stop** on any security-touching slice |
| `feature-dev` | plugin | Phase 1 `code-architect` (a subagent) absent - architecture is improvised |
| `frontend-design` | plugin | UI build units fall back to a plain dev build (lower fidelity) - degrade and note, not a stop |
| Node.js / `npx` | runtime | **both** MCP servers fail to spawn -> Phase 3 E2E, Phase 4 browser-DAST, Phase 5 `context7` silently become **no-ops** (web slices) |
| Playwright MCP | MCP | no browser E2E / DAST (off-web slices retarget - see Phase 3 / 4) |
| `/security-review` | CLI built-in | present without any plugin; it is the Phase 4 SAST driver |
| `python3`, `curl`, `gh`, `context7`, `pandoc` | misc | degrade gracefully (md2docx fallback, protocol-DAST, PR path, lib-docs) |

Print the missing set + its install commands at run start; only then enter Phase 0. (This
is an inline check, **not** a separate skill - a doctor-skill that is itself missing helps
no one.) Rows whose consequence says **stop** are hard-required (do not proceed without
them - the `council` stop is conditional on a security-touching slice); everything else
degrades gracefully. **Exact install commands live in the plugin README.**

## Role -> skill / tool mapping

Each phase is either a **STAGE** (real work, delegated to a role skill) or a **GATE**
(a cheap human / inline / advisory checkpoint, *not* a spawned subagent). Each role skill
also runs standalone; the orchestrator's job is the order, the gates, and the loop-backs.

### Phase 0 - Discovery and Intent
STAGE: run `gear:pm` (requirements + the 3-line sponsor artifact). GATE: Sponsor/CEO sign-off (human; `/gear:council` if the direction is contested).

### Phase 1 - Design and Architecture
STAGE: run `gear:sa` (design + implementation plan + threat-model MUSTs via `/gear:council --preset safeguard`). GATE: human plan sign-off (go / no-go).

### Phase 2 - Build
STAGE: run `gear:dev` (subagent-driven-development + test-driven-development).

### Phase 3 - QA / Test
STAGE: run `gear:qa` (whitebox + blackbox/contract + E2E + multi-dimensional code review).

### Phase 4 - Security verification
STAGE: run `gear:sec` (SAST + DAST). Every Phase-1 MUST-ID must close here as a defect-register row.

### Phase 5 - Docs and Release
STAGE: run `gear:tw` (docs, opt-in). GATEs (orchestrator-owned, below): Verification, UAT vs intent, the hard human commit gate, and the end-of-arc retro harvest offer.

The four release GATEs the orchestrator owns at Phase 5:
- **Verification** via `verification-before-completion` (must be green before the commit gate).
- **UAT vs intent** (below) - acceptance against what was *wanted*, not just the spec.
- **Hard human commit gate** via `finishing-a-development-branch` (worktree/branch sandbox; no commit/push/deploy without it).
- **Harvest offer** (below) - the opt-in end-of-arc retro hand-off.

**UAT vs intent - check what was *wanted*, not just the spec (concrete checklist).** This is
the only gate guarding *wanted != built*; green tests + spec-conformance are necessary, not
sufficient. Run it explicitly: **(a)** does the result match the **Phase-0 goal + the user's
own words** (not just the plan)? **(b)** are the **defined UI/UX states actually reachable**
(empty / error / loading - see the state-trigger discipline in `gear:pm`)? **(c)** for a UI change,
**observe the real artifact** - screenshot / E2E the rendered result against the design
intent and confirm no console errors (do not infer from tests alone); **(d)** an *intent*
mismatch loops back to **PM / Design** (distinct from a defect, which loops to DEV). (field-notes: a UI UAT caught a system-adaptive default, an absent empty-state, and a dark-mode contrast issue.)

**Harvest is opt-in and end-of-arc - offer it, don't auto-run it.** After the release
gate, ask once: *"Harvest the lessons from this slice via retro?"* (Matches sdlc's
offer-first discipline.) When accepted, invoke `/gear:retro` and **hand it a concise
arc summary** drawn from the run artifacts - key design decisions, notable
defect-register findings (P0/P1), loop-back lessons, and threat-model MUST-ID closure -
so retro reflects on that summary instead of re-deriving it from the transcript; it then
dedups, GATEs, and routes as usual. This complements the `SessionEnd` auto-stage (a
passive backstop for the next session); declining writes nothing.

## Outputs the runner gets (the honest professional artifacts)

sdlc executes in **one session** (minutes), so it produces engineering artifacts
and traceability - **not** a calendar, sprint cadence, or velocity (theater for an
in-session agent). Produce five small live tables - **phase log, run-board, defect
register, loop-back log, traceability** - treating the phase log as first-class (a
reader can replay the run from it). **Column formats: `references/artifacts.md`.**

**Where the artifacts live - offer it ONCE at run start (cross-repo safety).** First **detect any
existing convention** - if the repo already uses `docs/superpowers/runs/` or `docs/sdlc/`,
continue it (don't fragment). Then **offer the destination**: *"Run history in `docs/sdlc/<slice>/`
(default), this repo's existing `docs/...`, or another path - e.g. a separate / central docs repo
for cross-repo work?"* Confirm once with a sensible default (don't re-ask per artifact); record the
chosen path in the phase log so the run stays replayable.

Behavioral rules that ride on the artifacts:
- **Run-board:** `awaiting-gate` is the terminal state of a *healthy* run parked at a
  human gate - keep it distinct from `blocked` (stuck on an unresolved defect/dependency).
- **Defect register:** one **P0/P1/P2/P3** scale (not a parallel Crit/High/Med/Low) so the
  loop-back rule stays crisp. **Any open P0/P1 bounces back to DEV before the commit gate.**
  Record clean checks too (severity `-`, status `closed - no finding`) - negative results
  aren't lost.

### Verify findings before they gate

A finding from review / SAST / DAST is a **claim, not yet a fact**. Before its severity drives
a loop-back or blocks the commit gate, **adversarially verify each finding**: an *independent
skeptic, refute-by-default*, reads the actual code and rules it **confirmed / refuted /
severity-adjusted**, grounded in file:line. This kills false positives and stops a
confident-but-wrong severity from gating the run; record each verdict + reasoning in the
register. (Skip on the lite lane. field-notes: a Phase-4 pass correctly refuted four "injection"
findings on operator-set CLI values - no boundary crossed.)

### Loop-back log (what bounced, and why)
Loop-backs are what make this iterative rather than waterfall, but a status snapshot
hides them - record each bounce as a first-class event (format in `references/artifacts.md`).

The loop-back fix discipline (red-first regression test, delta-SAST the fix) lives in gear:dev.

### Traceability
Map each PM acceptance criterion to the test(s) that cover it and the result; a failing
row points to its defect ID. Format in `references/artifacts.md`.

## Discipline / honesty rules (carried from the council verdict)

- **GATE != subagent.** Gate rows are cheap human/inline/advisory checks. Do not
  spawn a subagent per *job title / persona* - collapse roles to the mapped skill calls.
  This bans **headcount theater**, not the multiple review *dimensions* a STAGE (code
  review, SAST) legitimately fans out, nor the *independent skeptic* that verifies a
  finding - those are real work, not personas.
- **Many hats, one head.** 8+ roles are one model conditioned on different personas,
  not independent reviewers. The value is the *checklist and the gates*, not headcount.
- **Security is shift-left, shift-right, and *traced*.** Once at design (threat model ->
  numbered MUSTs T1…), once at verification (SAST + DAST). **Phase-4 SAST must close every
  MUST-ID** - each surfaces as a defect-register row (verified-clean or a finding), so a
  design-time security requirement can't silently go unverified (the security analog of
  requirement->test traceability). Never only at the end.
- **Execution writes to a sandbox.** All work happens on a worktree/branch; a hard
  human gate precedes any commit, push, or deploy. A bad run is `git reset`-able.
- **Scale to the change.** Use the lite lane for small fixes; reserve the full
  pipeline (E2E + pentest) for changes that warrant it.

## Watch list (provisional - n=1, awaiting a 2nd confirmation)

Observations from a *single* run that did **not** meet the load-bearing-catch bar (no
P0/P1 would have slipped without them) - so per the "two tracks" rule near the top they
are recorded here, **not** folded as settled discipline, until a 2nd independent run
confirms them. Treat them as useful defaults, not law; promote to the body on confirmation.

- **DAST when there is no browser / HTTP surface** *(comic-web Slice B).* Many slices
  (backend probes, CLI commands, a library, a new encrypted column) expose no web surface,
  so Playwright/curl have nothing to drive. DAST does not vanish - it *retargets* to the
  runtime that exists: invoke the CLI / probe under real conditions (missing / malformed /
  valid input, unreachable upstream) and **prove the security claim with a real command,
  not by reasoning** - e.g. write a row through the app then read the *raw* DB column to
  confirm ciphertext-at-rest with plaintext absent; grep logs/stdout for leaked secrets;
  confirm the path fails closed. *Provisional because in its origin run the agent improvised
  this fine without the rule - a guidance gap, not a missed catch.*

- **Off-web E2E / Blackbox retarget** *(comic-web Slice B; n=1).* The Phase-3 off-web retarget
  note is **provisional** - the contrasting slice was on-web, so it did not confirm the off-web
  case. Promote once a 2nd off-web slice (CLI / job / library) confirms it.

*(Promoted to the body this run: Sponsor-gate output template, UAT-vs-intent checklist, TW
deliverable+format, code-review-as-STAGE - each on a 2nd contrasting confirmation. Threat-model
-> SAST traceability folded too, but as a **structural completion** of the existing
requirement->test traceability discipline, n=1 - watch for a real MUST-slip to confirm its weight.)*

- **Pre-Build foundation / health precheck** *(comic-web landing QA run; n=1).* Before Phase 3
  QA / E2E, verify the app is actually runnable + has the data the slice needs: app boots over
  *real HTTP* (not just the CLI kernel - stale opcache/config-cache 500'd every route incl
  `/up` until `optimize:clear` + container restart), the build toolchain is reachable (node was
  host-only, not in the app container), the web server is healthy (nginx was unhealthy -> use
  `php artisan serve`), and there's enough seed data to exercise content states (empty dev DB +
  SQLite test-DB missing content tables both blocked real verification). sdlc already has
  E2E platform-tooling + bundled-sidecar prechecks; this is the broader "does it even run, with
  data?" gate. Confirm on a 2nd run before folding.

- **A Phase-1 threat model can RE-SCOPE the slice, not only add MUSTs** *(Enkari Plan C; n=1).*
  The safeguard panel may conclude the slice's **core approach** is unsafe and bounce all the way
  back to re-defining what the slice *is* - not just appending T-numbered requirements. In Plan C
  the panel found the planned containment (an agent with `acceptEdits` "isolated" on a git branch)
  was not containment at all (a branch isolates the commit graph, not Bash/filesystem/network), and
  the slice was re-scoped from "run the agent that edits" to a **read-only `plan`-mode MVP**, with
  the dangerous write capability deferred to a *follow-up slice that re-runs the safeguard panel
  first*. Treat such a re-scope as the threat-model gate **working**, record it as a Phase-1->
  Architecture loop-back (human re-scope), and split rather than push the dangerous capability
  through. *Already implied by "a threat model opens a new risk -> back to Architecture"; the new
  nuance is that the right resolution is often a smaller, safer slice + a deferred one, not a pile
  of mitigations bolted onto the original.* Promote on a 2nd run where a panel re-scopes a slice.

- **Spike the real external contract before TDD-ing the parser** *(Enkari Plan C; n=1).* When a
  slice integrates an external tool's stream/output (a CLI, an API), make the **first Build task a
  SPIKE** that captures the *real* schema from the live tool and then TDD against captured fixtures -
  never against an assumed shape. The Plan C spike of `claude --output-format stream-json` found
  load-bearing surprises an assumed schema would have gotten wrong: huge hook-noise lines (validating
  the parser's byte-cap), and the requested `--model` alias differing from the model actually billed
  in the events (so the UI must read the model from the events, not assume the alias). A self-graded
  parser built on guessed shapes is *necessary, not sufficient* - the captured fixture is the
  validation. Confirm on a 2nd external-integration slice before folding.
