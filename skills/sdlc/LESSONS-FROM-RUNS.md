# Lessons from real sdlc runs (synthesis after counted run #2)

> **Purpose.** Distill what two real counted runs on Nusa actually demonstrated
> about the recipe - as evidence for or against the eventual promotion-to-skill
> decision. Written at the council panel's recommendation that "two unsynthesized
> runs don't get more useful by adding a third; they get useful by being read."
> Not a polished essay - just the honest read.

## Runs covered

- **Slice 0 (uncounted, 2026-05-28):** Nusa semantic search over a fixed seed corpus. Practice run while Nusa was still a test scaffold. Mechanic-validation only; not counted as promotion evidence.
- **Slice 1 - counted run #1 (2026-05-28):** Nusa single-URL ingest (`POST /ingest` + CLI). The foundation slice toward the cross-site `.id` crawler epic. Nusa elevated to a real maintained project before this run started.
- **Slice 2 - counted run #2 (2026-05-28):** Nusa shallow same-domain crawl (`POST /crawl` + CLI). Frontier + dedup + per-host politeness + robots cache, built on slice 1's foundation.

Slice 3 (cross-site `.id` with persistence) has **not** been executed and is **not** being scheduled to chase the counter.

## What stayed the same across both runs (shape evidence)

| Element | Slice 1 | Slice 2 | Comment |
| --- | --- | --- | --- |
| Phase 0-5 sequence | unchanged | unchanged | Both runs followed Discovery -> Design -> Build -> QA -> Security -> Docs/Release without deviation. |
| Five artifacts | all filled | all filled | phase log + run-board + defect register + loop-back log + traceability - all natural to fill on both runs. |
| Role -> skill mapping | held | held | brainstorming -> writing-plans -> subagent-driven-development -> Playwright MCP -> security-review subagent -> finishing-a-development-branch - no exceptions either run. |
| `awaiting-gate` status | used | used | Healthy terminal state at human commit gate, both runs. |
| Per-task commits on sandbox branch + hard gate on merge to `main` | yes | yes | `main` never touched until human approval, both runs. |

**No structural edits to RECIPE.md were needed during either run.** Edits I did make (loop-back log, `awaiting-gate`, single P-scale, Phase 4 fallback notes) were *additions* that hardened existing structure, not restructures. That is one data point for "shape stable."

## What the recipe machinery actually caught (machinery earned-keep evidence)

| Run | Defect | Severity | Caught by | What it cost / saved |
| --- | --- | --- | --- | --- |
| Run #1 | D-03: R-03 422-leak (malformed body returned leaky 422 instead of clean 400) | P2 | Static review (Phase 3) | Real bug; would have leaked pydantic schema detail. Fixed via loop-back (1 commit + 3 tests). |
| Run #2 | D-15/D-16/D-19: ceiling-constants unenforced inside `crawl()`, unbounded `_crawl_delay_for`, mid-file imports | P3 / P3 / cosmetic | Static review (Phase 3) | Defense-in-depth + cosmetic. Bundled fix (1 commit + 1 test). |
| Run #2 | **D-20: SSRF leak - robots.txt fetched BEFORE policy check** | **P1** | **SAST (Phase 4)** | **Real P1 caught only by SAST. Build-time code review missed it entirely.** Would have shipped a port-scan oracle on private hosts even with strict SSRF policy. Bug emerged from the *interaction* between slice 2's robots-cache layer and slice 1's per-page-policy guarantee - exactly the seam issue build-time review cannot see. |
| Run #2 | D-21: `VectorIndex.add` race under concurrent `/crawl` (sync route -> threadpool, shared state) | P2 | SAST | Real race; reproducible shape mismatch crashing subsequent `/search`. Build-review missed entirely. |
| Run #2 | D-22: unbounded `summary.skipped` (~160 MB response possible from adversarial input) | P2 | SAST | DoS knob; build-review missed entirely. |
| Run #2 | D-23, D-25 | P3 | SAST | Small defense-in-depth fixes (NaN guard, `trust_env=False`). |

**Loop-back log entries across both runs:**

1. Run #1: Phase 3 static review -> Phase 2 build (D-03).
2. Run #2: Phase 3 static review -> Phase 2 build (D-15/16/19).
3. Run #2: **Phase 4 SAST -> Phase 2 build (D-20 P1 + 4 others).**

All three bounces would have been invisible in a snapshot run-board. The loop-back log table captured all three cleanly. That refinement (added to RECIPE.md after slice 0) earned its keep.

## What stabilized across runs (cross-run mechanic findings)

After three confirmations across slices 0, 1, 2, these moved from notes-in-memory to RECIPE.md edits:

1. **`security-review` skill local-repo fallback** - the skill hard-diffs against `origin/HEAD` and fails on fresh local repos. SAST subagent over `git diff main..feature-branch` is the workaround. Confirmed every run. Folded into RECIPE.md Phase 4.
2. **`curl` as DAST companion to Playwright MCP** - Chromium blocks HTTP/1.1 request streaming + some header manipulation; SSRF and chunked-body probes need a non-browser client. Confirmed every run. Folded into RECIPE.md Phase 4.
3. **Concurrency probe in SAST for multi-write slices** - new from run #2. Folded into RECIPE.md Phase 4 even without 3-confirm because the catch (D-20, D-21) was load-bearing.

## What I genuinely don't know yet

- **Does the shape survive persistence?** All three slices so far are in-memory, sync, single-session. Slice 3 (cross-site + persistence) is the first that would break that assumption. Without running it, I cannot say whether the recipe absorbs that without re-shaping. This is the legitimate open question that the integer "~3" was a coarse proxy for.
- **Is there a real consumer for sdlc-as-skill?** Currently sdlc is invoked by one person on one project. The thin-conductor skill would package the discipline so others (or scheduled jobs, MCP hosts, downstream agents) can invoke it. Without any such consumer, the packaging has no recipient - and the Contrarian's strongest argument applies: sdlc-as-recipe is already producing value (the D-20 catch), and promotion to skill is adding wrapper, not capability.

## Promotion criteria the runs justify (replacement for "~3")

Phrased as falsifiable predicates rather than vibes:

- (a) **Shape unchanged.** RECIPE.md Phase 0-5 sequence + five-artifact set unchanged across >=3 consecutive real-product slices. *Currently 2/3 unchanged; addition-only edits are allowed and counted.*
- (b) **Loop-back log captures real bounces.** At least one real defect bounce per real run, recorded as a first-class loop-back-log entry. *Met: 1 + 2 = 3 real bounces.*
- (c) **Stage separation pays.** At least one P0/P1 defect caught by a stage (SAST, DAST, UAT) that build-time review missed - demonstrating the recipe's stage-decomposition does work the alternatives don't. *Met: D-20 P1 in run #2.*
- (d) **Cross-run mechanics stable.** Findings folded into the recipe stem from >=3 confirmations or one load-bearing catch. *Currently met for the three findings already folded; new findings would need to clear the bar.*
- (e) **A real consumer exists.** Someone or something other than the original author genuinely needs sdlc-as-skill rather than sdlc-as-recipe. *NOT met. This is the load-bearing missing condition.*

If all of (a)-(e) are met, promotion is justified. If (e) is never met, sdlc stays a recipe - and that is the honest end-state. **(e) cannot be cleared by the gatekeeper alone**; this is the structural protection against the goal-corruption the Contrarian warned about.

## Concrete next steps suggested by this synthesis

1. **Edit RECIPE.md** to demote the "~3 real times" sentence to a footnote and add criteria (a)-(e) as the actual promotion gate. (Reversible, ~10 minutes.)
2. **Wait** - for either Nusa to genuinely need cross-site `.id` crawl (slice 3 = product work, not theater), OR for a real consumer of sdlc-as-skill to appear. No time-box; idle is the honest state.
3. **If neither happens**, sdlc remains a recipe permanently, and that is fine. The recipe already produced value that justified the time spent on it (the D-20 catch alone).

## Honest meta-note

This synthesis was written *after* the council panel that produced it - the recommendation was Cost lens's: "Two unsynthesized runs don't get more useful by adding a third unsynthesized run; they get useful by being *read*." The document is the cheap-and-informative alternative to manufacturing slice 3. Whether it succeeds at being that depends on whether you (or a future reader) actually find it useful for the promotion decision when the time comes. If the trigger gets edited per (a)-(e) above, this file is the evidence that supports the new criteria.
