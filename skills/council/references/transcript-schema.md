# Transcript schema - the bridge contract for `index.html` (the simulation page)

This is the single source of truth for the JSON the simulation page reads.
The **producer** (the council controller, when the user asks to see a run)
writes `sidang.json` next to the HTML; the **consumer** (`index.html`)
fetches and renders it. Neither side owns the shape - this file does. Keep it
flat and dumb: it describes *what was said*, never the gate logic.

## File

`sidang.json`, placed in the skill folder (served by the same local HTTP
server). The page tries to fetch it; if absent, it shows a bundled sample and
auto-polls every ~6s until a real `sidang.json` appears, then loads it.

## Shape

```json
{
  "schemaVersion": 1,
  "status": "running | done",
  "title": "string - the header shown next to the live dot",
  "topik": "string - the question under debate (pinned context card)",
  "beats": [ Beat, ... ]
}
```

`status` drives the two viewing modes (see "Live vs replay" below). Omit it or
set `"done"` for a finished transcript; set `"running"` while a sidang is still
being written incrementally.

### Beat

| field     | type            | required | meaning |
| --------- | --------------- | -------- | ------- |
| `phase`   | int 1-5         | yes      | 1 Open, 2 Opinions (Round 1), 3 Gate, 4 Debate (Round 2), 5 Verdict. Drives the phase ribbon + pacing. |
| `role`    | string or null  | yes      | one of the role ids below, the synthesizer id `"chair"` (the Chair, kept as the literal id `index.html` expects), or `null` for a system/narrator line. Unknown ids render as a generic speaker (never crash). |
| `badge`   | string          | yes      | short stage label shown on the backdrop (e.g. "Opinions", "Verdict"). |
| `text`    | string          | yes      | the line. Supports tiny markup: `**bold**` and `*italic*` only. |
| `tag`     | string          | no       | a short chip (e.g. "yakin 78%", "mantap", "berubah", "teguh"). |
| `changed` | bool            | no       | if true, the tag is highlighted (a member that revised its stance). |
| `gong`    | string          | no       | for system beats: a small heading above the line (e.g. "Chair filtering"). |
| `list`    | array of string | no       | for the verdict beat: a numbered list under the text. |
| `pending` | bool            | no       | live mode only: this member is being dispatched / thinking. Renders as a "sedang berpikir" typing bubble (text may be empty). When the reply lands, rewrite the beat with `text` filled and `pending` dropped. |

## Live vs replay

The page picks a mode from `status`:

- **`done`** (or absent) - REPLAY. The page auto-plays the chat at reading
  speed (no Play button needed), showing a brief "thinking" indicator before
  each member speaks. This is how a finished transcript or the bundled sample
  behaves.
- **`running`** - LIVE. The page shows every beat that exists right now (no
  timer), renders any `pending` beats as "sedang berpikir" bubbles, and re-polls
  `sidang.json` every ~2s. As the producer fills beats and appends new ones, the
  page follows along. When `status` flips to `done`, it freezes on the full
  transcript (no rewind).

### Live write protocol (only when the user is watching in the browser)

The producer writes `sidang.json` more than once during the run:

1. Before dispatching Round 1: `status:"running"`, and one `pending:true` beat
   per seated role (parallel - they all think at once).
2. After Round 1 returns: rewrite those beats with real `text`, `pending` gone.
3. Append the gate beat; before Round 2, append `pending` beats for the
   contested roles; fill them when they return.
4. Append the Chair verdict beat(s); set `status:"done"`.

Each write is a full-file overwrite of the same `sidang.json` (still one file,
still no streaming server). If the user is NOT watching live, skip all this and
just write once at the end with `status:"done"`.

Role ids (must match the page's `ROLES` table): `security`, `cost`,
`maintainability`, `simplicity`, `scalability`, `usability`,
`operability`, `compliance`, `contrarian`, plus `chair` for the
synthesizer and `null` for system lines. (Only roles actually seated in the run
appear.)

## Rules (so it does not rot)

- **Flat, not structural.** A beat records a line spoken; it never encodes the
  gate's branching. If you find yourself adding fields that mirror control flow,
  stop - that is overbuild.
- **Bump `schemaVersion`** if a field's meaning changes. The page tolerates
  unknown roles and missing optional fields, but not a changed contract.
- **One write, at the end.** The producer emits the whole file once after the
  Chair synthesis (the live-write protocol above is the only exception).
- **Presentation is downstream of the verdict, never upstream.** Writing the
  transcript must not influence any deliberation decision.
- **`sidang.json` is generated, not source** - it is gitignored. The page's
  fallback sample is baked into the HTML, so a fresh clone still works. To keep a
  good run, copy it into `samples/<name>.json` and commit *that* as source
  (a curated keepsake, reloadable). Do not archive runs automatically and do not
  add a run-picker - that is the scenario dropdown that was deliberately removed.
