# sdlc promotion history

This document preserves the gating discipline that governed sdlc during its
recipe phase (2026-05-26 through 2026-05-29) and the deliberation that promoted
it to skill form on 2026-05-29. It is downstream-only context for future
readers; it does not gate skill use.

## Status of sdlc during the recipe phase (verbatim from former RECIPE.md)

sdlc lived as a recipe (a documented flow described in a markdown file, with
no skill frontmatter) from 2026-05-26 to 2026-05-29. The original "Status"
section read:

> ## Status: this is a recipe, not a skill (yet)
>
> This file is a **document**, not an executable skill. It has no skill frontmatter
> on purpose, so the harness never auto-triggers it. It describes *how to drive the
> existing superpowers chain through a professional business-flow lens* - you run the
> phases by hand, invoking the mapped skills yourself.

## Original five-criterion promotion gate (verbatim from former RECIPE.md)

> **Promotion trigger.** Promotion of this recipe into a thin `sdlc` conductor
> skill is gated on **five qualitative criteria**, not on a count of runs. All five
> must hold:
>
> - (a) **Shape unchanged.** This file's Phase 0-5 sequence and five-artifact set
>   (phase log, run-board, defect register, loop-back log, traceability) remain
>   unchanged across at least three consecutive real-product slices. Addition-only
>   edits that harden existing structure (new optional artifacts, severity-scale
>   clarifications, status enums) are allowed and counted as preserving shape;
>   structural restructures are not.
> - (b) **Loop-back log catches real bounces.** At least one real defect bounce per
>   real run is recorded as a first-class loop-back-log entry, demonstrating that
>   the machinery is exercised rather than ceremonial.
> - (c) **Stage separation pays.** At least one P0/P1 defect has been caught by a
>   stage (SAST, DAST, or UAT) that build-time code review missed entirely -
>   evidence that the recipe's decomposition into distinct stages does work the
>   alternatives do not.
> - (d) **Cross-run mechanic findings stable.** Findings folded into this recipe
>   stem from either three independent confirmations across runs, or one
>   load-bearing catch.
> - (e) **A real external consumer exists.** Someone or something other than the
>   recipe's original author needs `sdlc` as an invokable skill rather than as
>   a hand-driven recipe - another project, another user, an MCP host, a scheduled
>   job. **This criterion cannot be cleared by the recipe's gatekeeper alone**;
>   it is the structural protection against goal-corruption (the gatekeeper
>   drifting toward clearing gates they wrote).

## Status of (a)-(d) at promotion time (2026-05-29)

| Criterion | Status | Evidence |
| --- | --- | --- |
| (a) Shape unchanged | MET (5/3) | Slices 1, 2, 3, 4, 5 on Nusa, all completed without RECIPE.md structural restructure. |
| (b) Loop-back log real bounces | MET | Run #1: 1 bounce. Run #2: 2 bounces. Run #3: 1 bounce. Run #4: 1 bounce. Run #5: 1 bounce. |
| (c) Stage separation pays | STRONGLY MET | Four SAST-only catches across four consecutive runs: D-20 (P1 SSRF, run #2), D-23 (P2 availability, run #3), D-29 (P3 content-spoof, run #4), D-33 (P1 ReDoS, run #5). Two of four are P1. |
| (d) Cross-run mechanic stable | MET | Five findings folded into RECIPE.md after >=3 confirmations each: security-review local-repo fallback, curl-DAST companion, concurrency probe, seam-zone probe, state-trigger discipline. |

## Historical note on the integer-count predecessor of (e) (verbatim)

> *Historical note.* An earlier draft of this paragraph read: *"Drive this flow
> by hand ~3 real times. If the same shape keeps recurring and the friction is
> real, promote it..."* The integer was a heuristic written before any real run
> existed. After two counted runs, a subsequent council deliberation (with the
> Contrarian's dissent load-bearing) found the integer was generating exactly
> the gate-clearing behavior the recipe's anti-theater sections warn against -
> "we have 2/3" was already pulling planning toward "let's get to 3." Criteria
> (a)-(e) replace the count with falsifiable conditions; (e) in particular is
> the criterion the integer was a proxy for and could not enforce.

## council deliberation 2026-05-29 - revising (e)

A second council was convened to deliberate the form of the first consumer
that could clear (e). The fork:

- A: another project owned by the gatekeeper (single-user, cross-project pull)
- B: another human user (cross-user pull)
- C: agent / MCP host / scheduled job (machine-callable pull)

Round 1 split. Round 2 produced three convergences:

1. A is the right experiment to run, but A does NOT clear (e) under the
   identity-based reading of "other than the recipe's original author".
2. No SKILL.md frontmatter promotion as part of the experiment.
3. The Contrarian's dissent that the gatekeeper convening the panel was itself
   evidence (e) was not met, was load-bearing and reported in full.

After the deliberation closed, the gatekeeper observed:

- The promotion gating in (e) was a process-anxiety hedge added at a prior
  council deliberation, not a substantive constraint on sdlc's usefulness.
- council itself was created without (e) as a gate. The asymmetry was
  author-imposed, not principled.
- The gatekeeper had a concrete current task (tech debt at the Valkyrie
  project at `/Users/Workspace/Development/Frontend/React/Valkyrie`) where
  sdlc would accelerate their work as a skill rather than a recipe.

Accordingly, (e) was revised on 2026-05-29 to the following text (Option 1
from the deliberation, chosen by the gatekeeper):

> (e) **A consumer with real need exists** - sdlc is invoked because someone
> (including the original author at a different context) has a concrete
> current task it accelerates, not because the author wants to ship a skill.
> council deliberation 2026-05-29 found strict identity-based reading too
> restrictive for one-author tools; the protection against goal-corruption is
> preserved by requiring the need to be concrete and named (not hypothetical
> "would be useful").

Under the revised (e), Valkyrie's concrete tech-debt work clears the gate.
Combined with (a)-(d) already MET, sdlc was promoted to skill form on
2026-05-29.

## The Contrarian dissent (reported in full per council protocol)

The Contrarian argued at Round 1 that the entire promotion question
was premature and that the gatekeeper convening a panel to find a consumer was
itself the failure mode (e) existed to catch:

> Criterion (e) says "real external consumer." The gatekeeper just said "ada
> KEINGINAN consumer nyata" - a desire, not a pull. A pull is when someone
> else (or some system) has already tried to use sdlc, hit friction, and
> asked for it to be a skill. Nobody in A/B/C has done that. The grammar of
> the request betrays the answer.
>
> Option A (gatekeeper's other repo) is the same user wearing a different hat
> - it cannot clear (e) because (e) was explicitly framed to exclude exactly
> this move. Calling it "cross-project" is a rationalization; the consumer's
> identity is what matters, not the repo's. Approving A means (e) had no
> teeth from the start.

At Round 2, the Contrarian refined the dissent:

> The panel just demonstrated the exact failure (e) exists to prevent: 3-of-4
> voices converged on "A with garnish" because A is the answer the gatekeeper
> telegraphed wanting. That is correlated error, not consensus. The Change Steward's
> "free intel" is the most dangerous phrase in this thread. Intel that costs
> nothing to gather usually costs something to act on honestly later -
> specifically, the discipline to say "the experiment succeeded and (e) is
> still not met." Once you let "the same operator in a different repo" count
> as signal, you have permanently lowered the bar; you cannot un-lower it
> later.
>
> Risk: gatekeeper runs A, it "works," and quietly treats (e) as cleared
> anyway. Mitigation: write the non-clearance declaration into the recipe
> itself, not just a chat message.

The gatekeeper acknowledged the Contrarian's Round-2 prediction was substantially
accurate: the conversation immediately after the deliberation did move toward
"use Valkyrie as (e) clearance." The gatekeeper then chose to revise (e)
explicitly rather than silently treat it as cleared, addressing the Contrarian's
specific mitigation request ("write the non-clearance declaration into the
recipe itself, not just a chat message") by documenting both the revision and
this dissent in this file.

The Contrarian's dissent stands on record. Future readers asking "should we re-tighten
(e) under stricter author-identity reading?" should weigh it.

## Promotion timeline

| Date | Event |
| --- | --- |
| 2026-05-26 | sdlc created as recipe (RECIPE.md), original (a)-(e) gating. |
| 2026-05-26 to 2026-05-29 | Slices 1-5 driven on Nusa (a semantic search project). (a)-(d) progressively confirmed; (e) deliberately not cleared. |
| 2026-05-29 | First council deliberation about (e) form. Second sub-deliberation revised (e) per Option 1. Gatekeeper promoted sdlc to skill: RECIPE.md split into SKILL.md (operational) + references/promotion-history.md (this file). |
