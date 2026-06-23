# Classification + confidence rubric

## Classify each candidate into exactly one class
- **project-fact** — true for THIS repo/project: a convention, gotcha, config quirk,
  or a decision and its rationale. Home: the per-project memory store.
- **skill-lesson** - a lesson about how a gear skill (`sdlc` or `council`) ITSELF
  should behave; applying it would improve that skill. Home: that skill's
  `LESSONS-FROM-RUNS.md` (as a proposed diff).
- **reusable-technique** — a cross-project debugging method, library/API workaround, or
  pattern that would help on unrelated projects. Home: the candidate store (may later
  `evolve` into a standalone skill).

When unsure between project-fact and reusable-technique, ask: "would this help me on a
totally different project?" Yes → reusable-technique; no → project-fact.

## Confidence (crude, deliberately simple)
Start at 0.5, then:
- +0.2 if hard-won (multiple failed attempts before it resolved)
- +0.2 if it recurred or was independently reinforced this session
- −0.3 if one-off, trivial, or obvious in hindsight
Clamp to [0.0, 1.0]. Candidates below 0.4 are shown but default to "skip".
