---
name: retro
description: |-
  Use AFTER meaningful work to harvest reusable lessons from the session - when something was hard-won (a bug root-caused, a workaround found, a convention or decision settled, a defect caught) and worth remembering. retro reflects on the session, classifies each lesson (project-fact / skill-lesson / reusable-technique), scores its confidence, and ONLY ON YOUR CONFIRMATION routes it to its home: project facts to the per-project memory store, reusable techniques to the retro candidate store, skill lessons as a proposed diff. The reflection/memory leg of the toolkit - sdlc ACTS, council JUDGES, retro REMEMBERS. Trigger on "harvest lessons", "what did we learn", "remember this", "/gear:retro", or at the end of a substantial slice.
---

# retro - reflect, then route what was learned

The toolkit's memory: it watches a finished slice, distills the durable lessons,
and files each where it will be found again. sdlc ACTS, council JUDGES, **retro REMEMBERS**.
These three are one model voicing different roles, honest by design, not a team of
independent experts.

## What this skill does (complete loop)
Reflects on the **current session**, on **staged sessions** the SessionEnd detector flagged, and on
past transcripts via **`--since <date>`**. A passive one-line nudge at session start announces pending
lessons. The detector is cheap and no-LLM; all classification, dedup, scoring, and writes happen here
behind the confirmation gate. Candidates carry a TTL and can be pruned (`/gear:retro prune`); the
skill-lesson route emits an applyable diff to a skill's `LESSONS-FROM-RUNS.md`; and mature candidates
can graduate into a standalone skill (`/gear:retro evolve`). Nothing reaches a real store without
your confirmation.

## The loop

**Where to reflect from (B2).** By default, reflect on the **current session**, and also pick up
any **staged sessions**: run
`python3 "${CLAUDE_PLUGIN_ROOT}/skills/retro/scripts/retro.py" pending` to list session ids the
SessionEnd detector flagged (their pointers live in `~/.claude/gear/pending/<id>.json`, each with
a `transcript_path`). If the user passes **`--since <date>`**, also sweep this project's transcripts
(`~/.claude/projects/<slug>/*.jsonl`) modified on/after that date whose id is not already in
`harvested.log`. The auto-detector only stages **gear** sessions; `--since` is unrestricted (it is
the user's explicit intent), so it may reach non-gear sessions too.

**Handoff mode.** When a sibling skill invokes you with a handoff summary - `sdlc`'s
end-of-arc harvest, a `council` verdict, or a `triage` remediation plan - treat that summary as the
**primary candidate material**: still classify, dedup, GATE, and route it exactly
as below. Reflecting on the transcript is the fallback when no summary is handed off.
`sdlc`, `council`, and `triage` are the sibling skills that hand off summaries to retro.

1. **Ensure the store exists.** Run once:
   `python3 "${CLAUDE_PLUGIN_ROOT}/skills/retro/scripts/retro.py" init`
2. **Reflect.** Re-read this session. Surface candidate lessons - each a thing that was
   *hard-won or non-obvious*: a bug's root cause, a workaround, a project convention, a
   decision + rationale, a defect a phase caught, a panel verdict. Skip the trivial and the
   one-off (see `references/routing.md`).
3. **Classify + score.** For each candidate assign a class and a confidence per
   `references/routing.md`, and fill the shape in `references/lesson-template.md`.
4. **Dedup against what is already saved.** Before the gate, confirm each candidate is not
   already recorded - so you surface signal, not repeats:
   - List existing candidates:
     `python3 "${CLAUDE_PLUGIN_ROOT}/skills/retro/scripts/retro.py" list --long`
     (shows slug, triggers, and a short problem line for each).
   - Scan the current project's memory store (`~/.claude/projects/<proj>/memory/` - the
     `MEMORY.md` index plus each file's `name` / `description`) for the same lesson.
   - Match by **meaning**, not exact string: a different wording of the same lesson is still a
     duplicate.
   - Mark each candidate **NEW** or **DUPLICATE** (and note where it already lives:
     `candidate <slug>` or `memory <slug>`).
5. **GATE - present, do not write.** Show the user every candidate (class, confidence,
   problem/solution/example, proposed destination). Let them confirm / edit / reject each.
   **Never write anything before explicit confirmation** (user rule: confirm before
   irreversible).
   Group candidates as **NEW** vs **DUPLICATE**. Default: **skip DUPLICATEs**, naming where each
   already lives; write one only if the user explicitly overrides. Present NEW candidates for
   confirm / edit / reject as usual. (Rejecting still writes nothing.)
6. **Route the confirmed ones:**
   - **project-fact** -> save as a per-project memory using your native memory-writing
     (a `~/.claude/projects/<proj>/memory/<slug>.md` file with the standard
     `name`/`description`/`metadata.type` frontmatter, plus a one-line pointer in
     `MEMORY.md`). This reuses the existing, auto-recalled memory store.
   - **reusable-technique** -> run:
     `python3 "${CLAUDE_PLUGIN_ROOT}/skills/retro/scripts/retro.py" candidate --name "<title>" --confidence <0-1> --problem "<...>" --solution "<...>" --example "<...>" --triggers <cue> <cue> --session "<session-id>"`
   - **skill-lesson** -> produce an applyable diff to that skill's `LESSONS-FROM-RUNS.md`:
     1. Format the entry:
        `python3 "${CLAUDE_PLUGIN_ROOT}/skills/retro/scripts/retro.py" lesson-block --title "<short title>" --date <YYYY-MM-DD> --problem "<...>" --solution "<...>" --example "<...>"`
     2. Read the target skill's current lessons file at
        `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/LESSONS-FROM-RUNS.md` (if it does not exist, treat the
        current content as empty - the diff will create the file).
     3. Show the user a **unified diff** that appends the new block to that file (you may compute it
        with `python3 -c "import difflib,sys; ..."` or present it inline). retro does **not** touch
        the gear repo - tell the user to apply it to their gear clone and commit
        (e.g. `git apply` in their checkout). Nothing is written automatically.
7. **Confirm what landed.** List what was written
   (`python3 "${CLAUDE_PLUGIN_ROOT}/skills/retro/scripts/retro.py" list` for candidates)
   and where, so the user sees the result.
   Then mark each fully-processed session as harvested so it is not re-proposed:
   `python3 "${CLAUDE_PLUGIN_ROOT}/skills/retro/scripts/retro.py" harvested <session-id>`, and the
   staged pointer in `~/.claude/gear/pending/<id>.json` may be removed. (A staged session the user
   chose to skip entirely should also be marked harvested so the nudge clears.)

## Pruning stale candidates (B3)

When the user runs `/gear:retro prune` (or asks to clean up stale candidates), expire
reusable-technique candidates that aged past their TTL without graduating - keeping the store
signal, not clutter. This is **manual and gated**: never auto-delete.

1. **Dry-run.** List what would expire:
   `python3 "${CLAUDE_PLUGIN_ROOT}/skills/retro/scripts/retro.py" expired`
   (lists candidate slugs whose `created + ttl_days` is in the past; `status: promoted` is exempt;
   candidates with an unreadable `created` are conservatively kept).
2. **Show context, then GATE.** For each expired slug, show the user its **age in days** (today minus
   `created`) and its **confidence** (from the frontmatter), so they can judge. **Present the list and
   ask for confirmation - delete nothing before the user approves.** (Deletion is permanent.)
3. **Delete the confirmed ones.** For each slug the user approves:
   `python3 "${CLAUDE_PLUGIN_ROOT}/skills/retro/scripts/retro.py" remove <slug>`
4. **Report.** State what was removed and what was kept. Rejecting the prune removes nothing.

## Graduating candidates into a skill (evolve, B4)

When the user runs `/gear:retro evolve`, turn mature reusable-technique candidates into a
standalone personal skill under `~/.claude/skills/`. This is **gated**: never write a skill without
confirmation.

1. **List candidates.** `python3 "${CLAUDE_PLUGIN_ROOT}/skills/retro/scripts/retro.py" list --long`
   and read each candidate's `confidence` from its frontmatter.
2. **Select the mature ones and cluster.** Pick candidates with high confidence (guideline: >= 0.7)
   that are not expired or already `promoted`, and group related ones by theme. Each coherent cluster
   becomes one proposed skill.
3. **Draft the SKILL.md.** For each cluster, author a `SKILL.md` (frontmatter `name:` = a clean
   kebab slug, `description:` = a clear when-to-use line; body = the synthesized problem/solution and
   activation triggers from the cluster's candidates) to a temporary file.
4. **GATE.** Show the user each proposed skill (name, description, which candidates feed it) and
   confirm. Write nothing before approval.
5. **Install + promote.** For each approved skill:
   `python3 "${CLAUDE_PLUGIN_ROOT}/skills/retro/scripts/retro.py" install-skill --name <slug> --from <draft.md>`
   (refuses a dirty slug or an existing skill without `--force`), then mark each source candidate:
   `python3 "${CLAUDE_PLUGIN_ROOT}/skills/retro/scripts/retro.py" promote <candidate-slug>`.
6. **Report.** Tell the user the new skill lives at `~/.claude/skills/<slug>/SKILL.md` and auto-loads
   next session as `<slug>@skills-dir`; the source candidates are now `promoted` (exempt from prune).

## Principles
- **Signal over volume.** A handful of real lessons beats a wall of obvious ones.
- **Nothing leaves without the gate.** Rejecting a candidate writes nothing, anywhere.
- **Reuse, don't duplicate.** Project facts go to the memory store you already have; only
  genuinely reusable techniques get a retro candidate.
