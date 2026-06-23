---
name: tw
description: Phase 5 of the gear SDLC - technical writing / docs. Produce the release or stakeholder document in the project's format (zero-dep md2docx.py for .docx, or context7 for library docs), offered not auto-run. Use when documenting a finished slice. Triggers on "write the docs", "release notes", "stakeholder doc".
---

# tw - technical writing / docs (gear SDLC Phase 5)

Produce the release or stakeholder document for a finished slice, in the project's format.
This is the docs STAGE of the gear:sdlc pipeline; it also runs standalone. One model voicing
the TW role, honest by design, not a separate expert. The release GATEs (verification, UAT,
commit) are owned by gear:sdlc, not by this skill.

### Phase 5 - Docs (TW STAGE only)
| Role | Type | Maps to | Output |
| --- | --- | --- | --- |
| TW | STAGE *(optional, offered)* | **offer** "produce the release/stakeholder doc now?" - usually deferred until *all* modules' UAT is done; format asked per project; `context7` for library docs | documentation in the project's format (when accepted) |

**TW is opt-in and usually end-of-arc - offer it, don't auto-run it.** Documentation is
typically written **once, after *all* modules' UAT** (not per slice), so **ask** rather than
auto-produce: *"Produce the release/stakeholder doc now? It's usually done after the whole
feature's UAT."* (Matches sdlc's offer-first discipline.) When accepted,
the deliverable is the stakeholder/release doc (**distinct** from the markdown run-artifacts,
which stay markdown), in the **project's delivery format - ask which** (markdown / .docx / other).
For a **.docx (Word)** shop the bundled **`${CLAUDE_PLUGIN_ROOT}/skills/tw/scripts/md2docx.py`**
makes a *valid* `.docx` from a Markdown subset with **zero deps** (python stdlib; verified
`Microsoft Word 2007+` on py3.9) - or `pandoc` / `python-docx` if the project has them.
The format is a per-project choice, not a universal rule; this skill ships the zero-dep
.docx capability for when it's wanted.
