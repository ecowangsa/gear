# Gear - an SDLC toolkit of Claude Code skills

**Gear** is a single [Claude Code](https://claude.com/claude-code) plugin that
packages ten skills: **sdlc** (the orchestrator), six **role skills** (pm, sa, dev,
qa, sec, tw) that execute each SDLC phase, **council** (the advisor), **retro**
(the memory), and **triage** (the remediation planner). One model, many roles, honest by design.

> [!IMPORTANT]
> **One model, many roles, not a team of independent experts.** Every skill voices
> multiple roles or lenses using one model. The value is the **structure, the gates,
> and the honest artifacts**, never the illusion of independent voices. The skills
> say so out loud, on purpose.

> [!WARNING]
> **Status: experimental (v0.14.0).** These skills have been run across a handful of
> sessions by their author. **Zero confirmed external users.** Treat them as sharp
> checklists that are still earning their evidence, not battle-tested discipline.

---

## Install

```text
/plugin marketplace add ecowangsa/gear
/plugin install gear@gear
```

All ten skills (`/gear:sdlc`, `/gear:pm`, `/gear:sa`, `/gear:dev`, `/gear:qa`,
`/gear:sec`, `/gear:tw`, `/gear:council`, `/gear:retro`, `/gear:triage`) are available
immediately in a new session. The session hooks (see "Live hooks" below) register automatically.

---

## The ten skills, one cycle

The skills divide a development cycle into four advisory jobs and never edit each other's files:

| Skill | Role | Nature | Invoke |
| --- | --- | --- | --- |
| **sdlc** | ACTS | orchestrator: drives a slice through all six phases via the role skills | `/gear:sdlc <slice>` |
| **council** | JUDGES | advisory: returns a verdict, never executes | `/gear:council <trade-off>` |
| **triage** | TRIAGES | remediation planner: turns a verdict or findings list into a prioritized backlog for sdlc | `/gear:triage` |
| **retro** | REMEMBERS | memory: harvests durable lessons, gated | `/gear:retro` |

sdlc orchestrates. At a hard fork it calls council for a verdict. council can hand off to triage,
which turns the verdict into a sequenced remediation backlog that sdlc executes. At the end of a
slice sdlc offers the lessons to retro, which files each where it will be found again.

The six role skills are the phases gear:sdlc orchestrates; each is also invokable on
its own (e.g. `/gear:dev` to build a planned slice without running the full pipeline).

| Skill | Phase | Does |
| --- | --- | --- |
| **gear:pm** | 0 Discovery and Intent | requirements + sponsor artifact |
| **gear:sa** | 1 Design and Architecture | design + plan + threat-model MUSTs |
| **gear:dev** | 2 Build | TDD build |
| **gear:qa** | 3 QA | test pyramid + code review |
| **gear:sec** | 4 Security | SAST + DAST, close MUSTs |
| **gear:tw** | 5 Docs | release/stakeholder docs (opt-in) |

---

### Multi-agent execution

gear:pm emits a schema-bound backlog of work units called the task contract
(schema at `skills/sdlc/references/task-contract.schema.json`, with a worked
example alongside it). gear:sdlc consumes that backlog and fans independent
units out across agents: inline subagents by default, escalating to a Workflow
harness for large fan-out. Each unit runs in its own git worktree so parallel
file edits do not collide. Before a unit is accepted, gear:sdlc adversarially
verifies it against the acceptance criteria in the contract.

Honesty note: parallel for speed is distinct from parallel for judgment. The
agents share one underlying model, so this is structured throughput, not a team
of independent experts.

---

### `/gear:sdlc` - phased SDLC orchestrator

sdlc drives a feature slice from **idea to release** through six phases: Discovery,
Design, Build, QA, Security, Docs/Release, with iterative loop-backs and **hard human
commit gates**. It delegates each phase's stage work to the corresponding role skill
(gear:pm through gear:tw), while keeping the spine: preflight, cross-phase artifacts,
human GATEs, the Watch list, and loop-back logic. The value is the checklist, the
phase gates, and the honest artifacts, not the illusion of independent experts.

Invoke it explicitly or let it engage on intent:

```text
/gear:sdlc <describe the feature slice>
```

Triggers on: *"build X end-to-end"*, *"new slice"*, *"tambah feature"*, *"implement Y"*.

It runs a preflight check before Phase 0, walks each phase, parks at human gates for
your go/no-go, and loops back when QA or Security finds a defect or UAT rejects the
result. Nothing is committed, pushed, or deployed without an explicit human gate.

**The six phases (each handled by its role skill):**

| Phase | Role skill | What happens |
| --- | --- | --- |
| **0 - Discovery and Intent** | `/gear:pm` | Sponsor artifact (goal / success / scope) + requirements via `brainstorming` |
| **1 - Design and Architecture** | `/gear:sa` | `code-architect` + `writing-plans`; `/gear:council --preset safeguard` threat model with numbered MUSTs; human sign-off |
| **2 - Build** | `/gear:dev` | `subagent-driven-development` + `test-driven-development` |
| **3 - QA** | `/gear:qa` | Unit/integration + contract + Playwright E2E + multi-dimensional code review |
| **4 - Security** | `/gear:sec` | `/security-review` (all Phase-1 MUSTs closed) + dynamic probes |
| **5 - Docs and Release** | `/gear:tw` | Verification; UAT; **hard human commit gate**; offers a retro harvest |

Maturity note: run across a handful of slices by the author on their own projects.
Zero confirmed external users. Several rules are provisional (n=1) and live on the
SKILL.md Watch list until an independent second run confirms them.

---

### Role skills (`/gear:pm`, `/gear:sa`, `/gear:dev`, `/gear:qa`, `/gear:sec`, `/gear:tw`)

The six role skills implement each SDLC phase. gear:sdlc calls them in sequence as an
orchestrator; each also runs **standalone** so you can jump directly into a single
phase without running the full pipeline.

Examples:

```text
/gear:pm   # Phase 0: draft requirements and a sponsor artifact for a slice
/gear:sa   # Phase 1: produce a design, a plan, and a threat-model MUST list
/gear:dev  # Phase 2: build a planned slice with TDD
/gear:qa   # Phase 3: run the test pyramid and multi-dimensional code review
/gear:sec  # Phase 4: SAST + DAST probes; confirms all Phase-1 MUSTs are closed
/gear:tw   # Phase 5: release notes, stakeholder docs, changelog update (opt-in)
```

Running a role skill standalone respects the same honest-single-model disclaimer as
gear:sdlc: one model, multiple lenses, no illusion of independent experts.

**Frontend lane.** For UI/frontend slices, gear:pm offers a visual mockup with a local
preview URL (brainstorming's visual companion) during Discovery and marks the slice as
UI-touching. gear:dev then builds the UI with the `frontend-design` skill; if
`frontend-design` is not installed, gear:dev falls back to a plain build and notes the
gap. gear:sdlc preflight lists `frontend-design` as a soft dependency.

---

### `/gear:council` - advisory panel

When you face a real trade-off (*"split this service or not?"*, *"is this
over-engineered?"*, *"event-sourced vs CRUD?"*), council convenes a few Claude
sub-agents, each arguing one functional lens, runs a short structured debate, and
returns a single decision with a certainty band and the *real* shape of the
disagreement.

```text
/gear:council <describe the trade-off>
/gear:council              # bare: reads the fork from the conversation
/gear:council help         # prints usage without convening
```

Nine lenses: Security, Cost & Performance, Maintainability, Simplicity, Scalability,
Usability, Operability, Compliance & Privacy, and the Contrarian (seated by default).
Four presets: `general`, `audit`, `design`,
`safeguard`. Flags: `--preset`, `--roles a,b,c`, `--no-contrarian`,
`--effort <low|medium|high>`.

The flow: **Round 1** (parallel answers), then a **Gate** (debate only if the panel
splits), then **Chair synthesis** (verdict-first: decision, certainty band, "flips if").
After the verdict it offers to save the decision as a lesson via retro; declining
writes nothing.

Every voice is a Claude sub-agent inside your session, no external API keys, nothing
leaves your machine.

---

### `/gear:retro` - reflect, then route what was learned

After meaningful work, retro reflects on the session, surfaces the hard-won lessons
(a bug's root cause, a workaround, a settled convention, a defect a phase caught, a
panel verdict), classifies and scores each, and **only on your confirmation** routes
it to its home:

| Class | Destination |
| --- | --- |
| **project-fact** | per-project memory store (`~/.claude/projects/<proj>/memory/`) |
| **reusable-technique** | retro candidate store (`~/.claude/gear`) |
| **skill-lesson** | an applyable unified diff to that skill's `LESSONS-FROM-RUNS.md` |

```text
/gear:retro                 # harvest the current + staged sessions
/gear:retro --since <date>  # also sweep this project's past transcripts
/gear:retro prune           # expire stale candidates past their TTL (gated)
/gear:retro evolve          # graduate mature candidates into a standalone skill (gated)
```

Triggers on: *"harvest lessons"*, *"what did we learn"*, *"remember this"*.

The candidate store lives under `~/.claude/gear` (override with `GEAR_HOME`; related
`GEAR_*` env vars tune the scan). **Nothing reaches a real store without the gate.**
Rejecting a candidate writes nothing, anywhere. retro never touches the gear repo: the
skill-lesson route hands you a diff to apply in your own clone.

---

### `/gear:triage` - remediation planner

After council returns a verdict, or after a code/security review surfaces findings, triage
turns the raw output into a **prioritized remediation backlog** (P0..P3, sequenced, with an
sdlc owner and done-criteria for each item) conforming to the existing task-contract schema.
It then offers gated handoffs so nothing moves forward without your approval:

```text
/gear:triage              # reads the latest verdict or findings from the conversation
/gear:triage <summary>    # explicit input: paste or describe the findings
```

The flow: triage reads the council verdict or review findings, assigns a priority band
(P0 = critical/blocker, P1 = high, P2 = medium, P3 = low/nice-to-have), sequences items
so dependencies are respected, maps each to an sdlc phase owner, and writes done-criteria.
Then it offers two gated handoffs: **save the plan via retro** (so the decision is captured
as a lesson) and **hand the backlog to gear:sdlc** (so execution starts). Declining either
handoff writes nothing.

Triage is the JUDGES-to-ACTS bridge. It sits between council and sdlc in the cycle:
council JUDGES, triage TRIAGES, sdlc ACTS, retro REMEMBERS.

---

## Live hooks (passive automation)

Gear registers two lightweight, no-LLM session hooks (`hooks/hooks.json`). They only
**detect and remind**; all classification and writing stays behind retro's gate.

| Hook | Command | What it does |
| --- | --- | --- |
| **SessionEnd** | `retro.py detect` | For a session that shows a reusable signal, stages a silent pointer under `~/.claude/gear` (pending). Never writes the real stores. |
| **SessionStart** | `retro.py nudge` | One passive line announcing pending lessons. No per-turn nagging. |

So a slice you finish today is detected at session end; tomorrow's session greets you
with a one-line reminder to harvest it.

---

## The cycle

The four advisory skills form a cycle: **council JUDGES, triage TRIAGES, sdlc ACTS, retro REMEMBERS.**
retro is the memory hub; the others hand off summaries to it and never write memory themselves.

```text
         council (JUDGES)
        returns a verdict
         /              \
   called at a           offers triage
   hard fork             handoff
        |                     |
        v                     v
   sdlc (ACTS) <-------- triage (TRIAGES)
   executes the          turns verdict/findings
   backlog               into P0..P3 backlog
        \                     /
   offers harvest        offers to save
   at Phase 5            plan via retro
              \          /
               v        v
            retro (REMEMBERS)
            files each lesson
            behind your gate
```

- **council** after the Chair verdict offers a triage handoff (turns the verdict into a remediation backlog) and a retro save (writes nothing if declined).
- **triage** after building the backlog offers to hand it to gear:sdlc for execution and to save the plan via retro.
- **sdlc** at Phase 5 offers "Harvest the lessons from this slice via retro" (opt-in).
- **retro** accepts a handoff summary as primary material, then classifies, dedups, GATES, and routes it.

The skills never edit each other's files. Only retro writes to memory, always after your confirmation.

---

## Prerequisites (sdlc)

sdlc runs an inline preflight before Phase 0 and surfaces what is missing with the
exact install command. Set these up first:

| Dependency | Kind | If absent |
| --- | --- | --- |
| `git` | CLI | the sandbox/branch/commit-gate safety spine breaks: **stop** |
| **superpowers** | plugin | Phase 0/2/5 skills vanish: **stop** |
| **gear** (council) | co-located | Phase-0 gate + Phase-1 threat model cannot run: **stop** on security-touching slices |
| **feature-dev** | plugin | Phase-1 `code-architect` absent |
| Node.js / `npx` | runtime | Phase-3 E2E, Phase-4 browser-DAST, Phase-5 context7 silently no-op |
| Playwright MCP | MCP | no browser E2E / DAST |
| `/security-review` | CLI built-in | Phase-4 SAST driver |

```text
/plugin marketplace add anthropics/claude-plugins-official
/plugin install superpowers@claude-plugins-official
/plugin install feature-dev@claude-plugins-official
/plugin install playwright@claude-plugins-official
/plugin install context7@claude-plugins-official   # optional
```

---

## License

MIT, see [LICENSE](LICENSE). (c) 2026 Ecowangsa.
