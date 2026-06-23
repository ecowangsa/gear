# sdlc artifacts - table formats

The five live-table artifacts an sdlc run produces (named + ruled in SKILL.md
→ "Outputs the runner gets"). These are just the column shapes; keep each small.

## Phase log (the run record)
Per-phase record of which role mapped to which skill/tool, in order, and what came
out — often the most reproducible artifact (a reader can replay the run from it).

| # | Phase / role | Skill or tool | Output |
| --- | --- | --- | --- |
| 0 | PM / BA | `brainstorming` | requirements + acceptance criteria |
| 1 | SA / Architect | `code-architect` + `writing-plans` | design + plan |
| ... | ... | ... | ... |

## Run-board (phase status)
Status vocabulary: done / active / pending / blocked / looped-back / awaiting-gate.

| Phase | Status | Note |
| --- | --- | --- |
| 0 Discovery | ... | ... |
| 1 Design | ... | ... |

## Defect / findings register
| ID | Source | Severity | Title | Status |
| --- | --- | --- | --- | --- |
| D-01 | QA-e2e / Sec-SAST / Sec-DAST / review | P0 / P1 / P2 / P3 (`-` = clean check) | ... | open / fixed / accepted / closed - no finding |

## Loop-back log
| From -> To | Trigger | Resolution |
| --- | --- | --- |
| Phase 4 Security -> Phase 2 Build | D-01 (P1) | fixed, re-verified green |

## Traceability
| Requirement | Test(s) | Result |
| --- | --- | --- |
| R-01 (from PM acceptance criteria) | unit X / contract Y / e2e Z | pass / fail (-> D-id) |
