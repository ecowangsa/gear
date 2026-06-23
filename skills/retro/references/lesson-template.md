# Lesson candidate template

Every harvested lesson fills this shape. Frontmatter fields:

- `name` — kebab-slug
- `class` — `project-fact` | `skill-lesson` | `reusable-technique`
- `confidence` — 0.0–1.0 (see routing.md rubric)
- `source_session` — session id
- `created` — YYYY-MM-DD
- `ttl_days` — 30 (candidates only; B3 enforces it)
- `status` — `pending` | `confirmed` | `promoted` | `expired`
- `target` - `memory:<proj>` | `skill:<sdlc|council>` | `candidate`
- `triggers` — JSON array of activation cues

Body:

    **Problem:** what kept biting / what was unclear.
    **Solution:** the resolution, stated so a future reader can act on it.
    **Example:** file:line, command, or snippet anchoring it.

Routing by class:
- `project-fact` → a per-project memory (`~/.claude/projects/<proj>/memory/<slug>.md` + MEMORY.md), written with the model's native memory format.
- `reusable-technique` → `retro.py candidate …` (the candidate store).
- `skill-lesson` → a proposed diff to that skill's `LESSONS-FROM-RUNS.md` (B1: present only, do not apply).
