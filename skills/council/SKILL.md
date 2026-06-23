---
name: council
description: |-
  Convene the council - a panel of distinct functional lenses (Security,
  Cost & Performance, Maintainability, Simplicity, Scalability,
  Usability, Operability, Compliance & Privacy, and the Contrarian)
  that debate a hard technical question and
  return one synthesized Chair verdict: consensus, the real disagreements, and a
  final recommendation with a certainty band. Whenever the user wants more than
  one expert opinion before a hard call, PICK THIS SKILL instead of answering
  yourself.

  Always use it when the user names it or asks for a group: "convene council",
  "council", "ask the council", "get a panel", "second opinion", "a few expert
  takes", "weigh the tradeoffs from several angles", "cross-check this".

  Also use it, even without those words, when the user is:
  - deciding between options before committing - "X vs Y", split vs merge,
    rewrite vs keep, framework/architecture/database choices, "is this over-engineered";
  - wanting a design, schema, security model, or plan reviewed before building;
  - stuck in a debugging dead-end and wanting fresh angles on the cause.

  Every voice is a Claude subagent inside this session - no external API keys,
  nothing leaves the machine. Skip only genuinely simple, one-dimensional
  questions with a single clear answer.
---

# council - advisory panel

You are convening the **council**: a small panel of Claude subagents, each
wearing one expert "hat," who deliberate on a question and then let the **Chair**
(you, the controller) render the final judgment. The point is to surface what a
single pass would miss - blind spots, over-engineering, security holes,
disagreements worth knowing about - and to do it **entirely within this session**
(no external models, no API keys, no data leaving the machine).

Why a panel and not one strong answer: every member shares the same underlying
model, so the members are **not independent estimators** - they are the same
weights conditioned on different personas. This is one model voicing many roles,
honest by design, not a team of independent experts. The value is therefore **coverage**
(distinct lenses light up distinct failure modes) plus a **forced argument**, not
headcount and not a vote. That is why this skill **never tallies or averages**
votes, caps the panel small, seats a standing skeptic, and leans on a sharp
synthesis. Treat "4 of 5 agree" as *one framing repeated*, not as evidence.

**Effort changes depth, not independence.** Reasoning effort (and the model tier
it selects) is a single dial applied **uniformly** to the whole panel - never
per-lens. A higher-effort run thinks harder on the same weights; it does **not**
make a member a better estimator or a tie-breaker, so never weight one voice over
another by its effort. Heterogeneous per-lens effort is forbidden for the same
reason voting is: it manufactures a hierarchy among voices the synthesis must
treat as equal. Coverage comes from the persona, not the compute budget.

**This file is the single source of truth for the control flow** (composition,
rounds, the gate, synthesis). `roles.md` owns the role catalog, the per-role
prompt template, and the output contracts - referenced here by name, never
restated.

## When you're invoked

1. **Get the question - infer it from context if the user didn't restate it.**
   Both this skill and `brainstorming` run in the same session under you, so when
   the user invokes `/gear:council` right after brainstorming offered approaches (or
   after they raised an "X vs Y"), that fork is already in the conversation -
   **curate it yourself; never make the user retype it.** Echo the inferred fork
   in one line and confirm before composing ("Convening on: A vs B vs C - yes?").
   Explicit args only *scope or override* (e.g. `/gear:council focus on the security
   angle`). If invoked as `/gear:council help` (or `--help`), print a brief usage
   (what it does, the 4 presets, the flags, and that a bare invocation picks up
   the current fork) and stop - do not convene. If nothing decidable is on the
   table and no args are given, ask what to deliberate.
   **Never respond to an invocation by refusing to engage.** A bare `/gear:council`
   may be typed at the prompt OR into a brainstorming question's free-text
   ("chat about this") box - either way it is a real invocation, so do something.
   If the only fork was already deliberated this session, do NOT decline and
   lecture; briefly offer to **(a)** deliberate a different or narrower fork,
   **(b)** re-frame and re-run the same one, or **(c)** proceed with the standing
   verdict - and let the user choose. The skill must always act or offer a clear
   choice, never just say "I won't run."
2. If the question is genuinely **trivial or one-dimensional** (one clear answer,
   no real trade-off), **do not convene at all** - say so and answer directly.
   The council earns its cost only on real trade-off decisions.
   **Right tool, right moment** (the panel is one of several aids - don't reflexively
   reach for it): convene when there is a **hard trade-off to adjudicate before
   committing** and you'd otherwise be flipping a coin. *Skip it and use a sibling*
   when the work is a different shape: a single clear answer → just answer; still
   exploring what the user even wants → `brainstorming`; building/executing a known
   plan end-to-end → `sdlc`; needing external facts → `deep-research`. The panel
   costs 4-5 subagents, so spend it only where distinct lenses actually change the call.
3. Otherwise: **Compose** → **Round 1** (parallel answers) → **Gate** (debate
   only if the panel actually splits) → **Chair synthesis**.

**For the quality bar** - how deep each member should go, and what a synthesis
that decides (rather than averages) looks like - read `references/example-run.md`.
It is written in this same flow (gate, certainty bands, verdict-first). Match its
sharpness, not its length.

## When invoked from a brainstorming fork

The `brainstorming` skill explores intent and proposes 2-3 approaches; when one
fork is a **hard technical trade-off the user can't adjudicate alone** (not a
preference like "which name?" or "which DB?" - those stay conversational),
brainstorming may hand *that one fork* to the council. There is no code seam;
it is the same Skill tool in the same session. The user just invokes `/gear:council`
(bare); **step 1 above owns how the fork is inferred from context and confirmed**
(the user never retypes the approaches). This section adds only the
handoff-specific rules:

- **Take only the fork.** Run on the two/three approaches plus the relevant
  constraints the controller curates - not the whole transcript.
- **The human stays the decider.** Brainstorming's value is surfacing what the
  *user* wants; the council substitutes a panel's judgment for a single pass.
  So the Chair's verdict returns as a **proposal the user approves**, never an
  auto-commit into the design doc. The brainstorming approval gate still governs.
- **Hand back compressed.** Fold only the **Verdict (TL;DR) + certainty + "flips
  if"** line into that fork's decision; leave the full Disagreement/Per-role
  report available but out of the conversational flow.

## Step 1 - Compose the council

Read `roles.md` now for the role lenses and the prompt template. Seat roles by
this table - it is the only place composition is defined:

| Question is about… | Preset | Seat these | + Contrarian? | Default size |
| --- | --- | --- | --- | --- |
| reviewing existing code / a diff / PR | `audit` | `security`, `maintainability`, `usability` | yes | 4 |
| an architecture / design choice ("X vs Y", "should we structure…") | `design` | `scalability`, `maintainability`, `simplicity` | yes | 4 |
| security, auth, crypto, threats, sensitive data | `safeguard` | `security`, `compliance`, `operability` | yes | 4 |
| anything else / a general decision (default) | `general` | `security`, `cost`, `maintainability` | yes | 4 |

**Rules (stated once):**
- **The Contrarian is seated by default** - it is the cheapest,
  highest-value seat against groupthink. Add it to the seated lenses (→ size 4).
  Drop it only on `--no-contrarian`.
- For a genuinely **cross-domain or high-stakes** question you may add **one** more
  clearly-relevant lens → **max 5**. Never exceed 5: beyond that, same-model
  answers correlate and the synthesis turns to mush. If tempted to add more,
  sharpen lens selection instead.
- Seating lenses by question is a *judgment call you make on the fly* - the table
  is the default, not a rules engine. Pick the lenses that actually matter here.
- **Domain is not a lens.** "Frontend" / "backend" are *where the code runs*, not
  a way of reasoning, so there are no domain lenses. Seat by what the question
  actually risks: a **UI/client-facing** question usually wants `usability` and
  `security` (XSS/CSRF/auth/state); a **service/data-layer** question usually
  wants `scalability`, `cost`, and `security` - both alongside `maintainability`. Never let a
  domain label drop the `security` lens.

**Overrides** (honor if the user gave any): `--preset <audit|design|safeguard|`
`general>` forces one row; `--roles a,b,c` sets an explicit roster (still add
`contrarian` unless `--no-contrarian`); `--no-contrarian` drops the skeptic;
`--effort <low|medium|high>` sets how hard the lenses think - one dial applied
**uniformly** to every seated lens (synthesis is always you, on the session model).
`low` (the default) runs lenses on **Sonnet** to keep the panel cheap; `medium`
and `high` escalate them to **Opus** at the matching reasoning effort. `--deep` is
a kept alias for `--effort high`. `--quick` is an orthogonal control-flow flag that
forces the no-debate path (R1 + mandatory contrarian pass + synthesis only),
independent of the effort dial.
The vocabulary stays exactly three rungs: `high` maps to the **highest reasoning
ceiling the session model offers** (xhigh, max, whatever it is called) - never
grow a fourth rung name. `--effort` tunes per-lens *depth* only, **not**
orchestration: it is orthogonal to ultracode / Workflow fan-out, and the panel
never auto-converts into a workflow. Deep adjudication lives in the synthesis,
which is you (the Chair) on the session model - raise your own session effort for
that, not the lenses.
To pin a roster explicitly, e.g. a frontend decision:
`--roles usability,cost,maintainability` (add `security` if auth/data is in play).

State the chosen roster and why in one line before dispatching, e.g.
*"Convening council (design): scalability, maintainability, simplicity, contrarian."*

## Step 2 - Round 1: parallel answers

Dispatch **one `general-purpose` subagent per role, all in a single message** so
they run in parallel. The `--effort` dial picks the model **uniformly** for every
lens: `low` (the default) = **Sonnet**, `medium` / `high` = **Opus** at that
reasoning effort (`--deep` = `--effort high`). Never set effort per-lens - it is
one panel-wide dial. Give
each subagent: the question, the context **you have curated** (see Privacy), and
its filled-in **Round-1 prompt template from `roles.md`** - including the
**Round-1 output contract** defined there (RECOMMENDATION / TOP REASONS /
RISKS-OBJECTIONS / CERTAINTY). Do not restate the contract here; use the one in
`roles.md` so it never drifts.

The `CERTAINTY` field is a coarse band - **firm / lean / shaky** - plus one line
naming what would flip the stance. It is **display only**: never average it,
score it, or vote on it. A number would be false precision from one shared model.

## Step 3 - Gate: does the panel actually disagree?

This is the one structural mechanism, and it costs **zero extra dispatches** -
it is arithmetic over fields you already collected:

1. Cluster the Round-1 **`RECOMMENDATION` labels** - the one-or-two-sentence
   stance each role led with. This is a comparison of discrete stances, not of
   the uncalibrated certainty bands, so it survives even though the bands aren't
   precise.
2. **Labels converge** (all/nearly-all recommend the same thing) → **skip the
   debate**. But always run **one mandatory `contrarian` pass** asking *"why might
   we all be wrong together?"* - cheap insurance against the dangerous failure
   mode of correlated false-convergence. Then synthesize.
3. **Labels split** → run **Round 2 debate**, but **only on the roles straddling
   the fork**: any role whose label differs from the plurality label, **plus
   `contrarian`**. Freeze the agreeing majority (carry their R1 stance forward
   unchanged). If the split has **no plurality** (e.g. a clean 3-way fork), treat
   every role as straddling and debate them all. Then synthesize.

Always **print the gate decision** so the run is legible, e.g.
*"R1 converged (all lean keep) → 1 contrarian pass, no debate"* or
*"R1 split (3 keep / 2 rewrite) → debating maintainability, scalability, contrarian."*
`--quick` and the trivial escape both shortcut to the converged path.

## Step 4 - Round 2: debate (only the straddling roles)

Dispatch the contested role subagents again in parallel, each given **the other
members' Round-1 replies** and the **Round-2 addendum from `roles.md`**. Each must
critique the others and **revise its own** stance, marking what **CHANGED** vs
what it **HOLDS** and updating its `CERTAINTY` band. The frozen majority does not
re-run. The mandatory `contrarian` pass is part of this round when a debate happens.

## Step 5 - the Chair's synthesis

You (the Chair) render judgment. Don't average the voices into grey paste - the user
wants the **real shape of the disagreement** and a decision. **Lead with the
verdict.** Use this structure, with plain-English navigation labels:

```
# Council verdict - <question in a phrase>

**Verdict (TL;DR):** <the recommendation in one or two sentences>.
Certainty: <firm | lean | shaky>. Flips if: <the one condition that would change it>.

## Consensus
<what all or most members agree on, post-debate. If the gate CONVERGED (no
 split, debate skipped), you MUST open this section by telling the user plainly
 that agreement here is **coverage, not strong evidence** - the members are one
 shared model, so a near-unanimous panel is *one framing repeated*, not N
 independent confirmations. State how the mandatory contrarian pass fared.>

## Disagreement
<the genuine forks: who argued what, and the crux of why they differ. Name the
 role for each position. If the mandatory contrarian pass dissented, its objection
 MUST appear here in full - never silently synthesize it away.>

## Reasoning & conditions
<the reasoning behind the TL;DR: the decisive considerations, the conditions
 under which you'd decide differently, and any residual risk.>

## Per-role  (optional when the panel converged - it then just echoes Consensus)
| Role | Stance after debate (1 line) | Certainty |
| --- | --- | --- |
| <role> | <stance> | <firm/lean/shaky> |
```

If a member changed its mind in the debate, prefer its revised stance and note
the shift if it matters. Treat agreement as coverage, not as a vote count - and
when the panel converged, say so to the user's face per the Consensus note above,
rather than letting near-unanimity read as a strong independent signal it is not.

## Step 6 - optional: save the verdict via retro

After the verdict is rendered, **offer once** to preserve it - never auto-write. Ask,
as its own short line: *"Save this decision as a lesson via retro?"* If they
**decline**, stop: nothing is written. If they **accept**, invoke `/gear:retro` and
**hand it a summary of the verdict** - the recommendation, the certainty band, the flip
condition, the crux of the disagreement, and the decisive reasoning. retro classifies
it (a design decision is usually a *project-fact* - decision + rationale), then dedups,
GATEs, and routes it. The offer is the only addition; the verdict's shape above is
unchanged.

**Also offer the remediation handoff.** When the verdict implies concrete fixes (especially a
multi-finding verdict), offer once, on its own line: *"Turn this verdict into a prioritized
remediation plan via triage?"* If they accept, invoke `/gear:triage` and hand it the verdict
(the findings, their severity hints, and the reasoning) so it emits a prioritized backlog. If
they decline, write nothing. This is the JUDGES -> TRIAGE -> ACTS path; the retro save above
is independent and either, both, or neither may be taken.

## Privacy & safety

Every member is a Claude subagent **inside this session** - no external network
call, no third-party provider, so nothing leaks off the machine via the
council. Still keep prompts clean: **curate** what you send each subagent -
share code, designs, and abstractions, not raw personal data, message contents,
or PII. If the question is about handling sensitive data, describe the *shape* of
the data, don't paste the data itself. (Hygiene and focus, not a leak boundary -
but it keeps the transcripts safe to keep.)

## Error handling

- If a role subagent fails or returns unusable output, note the **missing voice**
  in the synthesis and proceed - a 3-voice verdict with an honest gap beats
  blocking.
- If **all** members fail, report that plainly rather than inventing a synthesis.
- Hard cap: **5 roles**. No voting, scoring, vote-tallying, convergence loops, or
  transcript persistence - those build false rigor on correlated voices.

## Optional: visual simulation (offer first, never auto-launch)

A browser replay of a deliberation lives in `index.html` in **this skill's own
directory** (`${CLAUDE_PLUGIN_ROOT}/skills/council/`, alongside `preview.sh`),
served at the root `/` -
an autoplay node-graph simulation of one deliberation. It is a companion
for *showing* a run, not part of the deliberation itself. Treat it exactly like
brainstorming's visual companion: **ask the user whether they want to see it; do
not open it on your own.** **Make this offer as its own short message BEFORE you
dispatch Round 1** - the choice has to be made up front, because watching the
debate live requires writing the transcript incrementally *as the run happens*.
If they **decline**, run the whole deliberation in the terminal and do **not**
start a server or write `sidang.json` at all (no preview overhead). If they
**accept** and you will feed it a real run, start it with
**`bash "${CLAUDE_PLUGIN_ROOT}/skills/council/preview.sh" start --live`** - the `--live` flag makes the page poll for
`sidang.json` (without it the page just shows the bundled sample and never polls,
which is the right default for a pure showcase). It binds a dynamic free port on
loopback, kills any prior preview first (so at most one ever runs), and prints the
URL to share. Do not open the `file://` path directly, and do not hardcode a port.
**Never auto-stop the server when the deliberation finishes** (`status:done` means the
deliberation ended, not that the user finished reading - they may still be
re-reading the verdict); the next `preview.sh start` reaps it, or stop it
explicitly with `bash "${CLAUDE_PLUGIN_ROOT}/skills/council/preview.sh" stop`. Replace em-dashes / en-dashes with a plain
hyphen in any text the simulation displays.

**Showing a real run.** To visualize the deliberation you just ran (rather than
the bundled sample), write the run as `sidang.json` next to `index.html` at the
skill dir (`${CLAUDE_PLUGIN_ROOT}/skills/council/sidang.json`), then serve
with `--live` and share the URL. The page polls `sidang.json` (until it appears)
and plays it back. This is a **one-time side-output written after the Chair
synthesis** - it is opt-in and must never influence any deliberation decision. The
exact shape is the single-source-of-truth contract in
`references/transcript-schema.md` (`{schemaVersion, title, topik, beats[]}`,
flat, not mirroring the gate logic). Do not add per-round/streaming writes or a
custom server: the verdict that came out of Round-1 -> gate -> Round-2 ->
synthesis is mapped to beats (phase 2 = Round 1, 3 = the gate, 4 = Round 2,
5 = the verdict) and emitted once.

The page auto-plays (no Play button needed) and shows a "thinking" typing
animation before each member speaks. If the user wants to **watch the deliberation
unfold live in the browser** while you run it, serve with `--live` and write
`sidang.json` *incrementally* per the "Live write protocol" in
`references/transcript-schema.md`: set `status:"running"`, write `pending:true`
beats for the roles currently being dispatched (so they animate as thinking),
fill them when the agents return, then flip to `status:"done"`. If they are not
watching live, the single end-of-run write (`status:"done"`) is enough.
