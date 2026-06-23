#!/usr/bin/env python3
"""retro - state-store helper for the gear `retro` reflection/memory skill.

Why it exists: the per-project memory route reuses the model's native memory
writing, but the "candidate" store (reusable-technique lessons awaiting
graduation) needs one consistent, testable on-disk format. This owns that store
using only the Python standard library (no third-party deps), matching gear's
zero-install convention.

Store lives at $GEAR_HOME (default ~/.claude/gear), deliberately OUTSIDE
~/.claude/skills/ so it never auto-loads as a plugin shadow.
"""
import argparse, datetime, json, os, re, sys
from pathlib import Path


def state_home():
    return Path(os.environ.get("GEAR_HOME", Path.home() / ".claude" / "gear"))


def cmd_init(args):
    home = state_home()
    (home / "pending").mkdir(parents=True, exist_ok=True)
    (home / "candidates").mkdir(parents=True, exist_ok=True)
    (home / "harvested.log").touch(exist_ok=True)
    print(home)


def slugify(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    return s or "lesson"


def cmd_candidate(args):
    home = state_home()
    (home / "candidates").mkdir(parents=True, exist_ok=True)
    slug = slugify(args.name)
    created = args.created or datetime.date.today().isoformat()
    triggers = json.dumps(list(args.triggers or []))
    path = home / "candidates" / f"{slug}.md"
    path.write_text(
        "---\n"
        f"name: {slug}\n"
        "class: reusable-technique\n"
        f"confidence: {args.confidence}\n"
        f"source_session: {args.session or 'unknown'}\n"
        f"created: {created}\n"
        f"ttl_days: {args.ttl}\n"
        "status: confirmed\n"
        "target: candidate\n"
        f"triggers: {triggers}\n"
        "---\n"
        f"**Problem:** {args.problem}\n\n"
        f"**Solution:** {args.solution}\n\n"
        f"**Example:** {args.example}\n"
    )
    print(path)


def _candidate_summary(path):
    slug = path.stem
    triggers, problem = "", ""
    for line in path.read_text().splitlines():
        if line.startswith("triggers:"):
            raw = line[len("triggers:"):].strip()
            try:
                triggers = ", ".join(json.loads(raw))
            except Exception:
                triggers = raw
        elif line.startswith("**Problem:**"):
            problem = line[len("**Problem:**"):].strip()
            break  # body follows the frontmatter; the first Problem line is the one
    if len(problem) > 80:
        problem = problem[:79] + "…"
    return slug, triggers, problem


def cmd_list(args):
    d = state_home() / "candidates"
    if not d.exists():
        return
    for p in sorted(d.glob("*.md")):
        if args.long:
            slug, triggers, problem = _candidate_summary(p)
            print(f"{slug} | triggers: {triggers} | problem: {problem}")
        else:
            print(p.name)


PROJECTS_DIR_ENV = "GEAR_PROJECTS_DIR"
MAX_BYTES_ENV = "GEAR_MAX_BYTES"   # skip huge transcripts at SessionEnd (cheap guard)
DEFAULT_MAX_BYTES = 25 * 1024 * 1024  # 25 MB; --since can still reach larger ones on demand
SIGNALS = [
    ("tool-error", r'"is_error"\s*:\s*true'),
    ("root-cause", r'root cause'),
    ("the-issue-was", r'the issue was'),
    ("ternyata", r'\bternyata\b'),
    ("turns-out", r'turns out'),
    ("defect-register", r'\bD-\d+\b'),
    ("council-verdict", r'Council verdict'),
]


def _projects_dir():
    return Path(os.environ.get(PROJECTS_DIR_ENV, Path.home() / ".claude" / "projects"))


def _harvested_ids():
    log = state_home() / "harvested.log"
    if not log.exists():
        return set()
    return {ln.strip() for ln in log.read_text().splitlines() if ln.strip()}


def cmd_pending(args):
    d = state_home() / "pending"
    if not d.exists():
        return
    for p in sorted(d.glob("*.json")):
        print(p.stem)


def cmd_harvested(args):
    home = state_home()
    home.mkdir(parents=True, exist_ok=True)
    log = home / "harvested.log"
    existing = _harvested_ids()
    if args.session_id not in existing:
        with log.open("a") as f:
            f.write(args.session_id + "\n")


def cmd_nudge(args):
    d = state_home() / "pending"
    n = len(list(d.glob("*.json"))) if d.exists() else 0
    if n == 0:
        return
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": f"retro: {n} sesi punya pelajaran belum dipanen - jalankan /gear:retro untuk meninjau.",
    }}))


def cmd_detect(args):
    # Never break session shutdown: any failure -> silent exit 0.
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    sid = str(payload.get("session_id") or "").strip()
    cwd = str(payload.get("cwd") or "")
    if not sid:
        return
    slug = re.sub(r"[^A-Za-z0-9]", "-", cwd)
    tpath = _projects_dir() / slug / f"{sid}.jsonl"
    if not tpath.exists():
        return
    try:
        max_bytes = int(os.environ.get(MAX_BYTES_ENV, DEFAULT_MAX_BYTES))
        if tpath.stat().st_size > max_bytes:   # too big to scan cheaply at shutdown; leave for --since
            return
        text = tpath.read_text(errors="ignore")
    except Exception:
        return
    if "gear:" not in text:          # self-gate: only gear sessions
        return
    if sid in _harvested_ids():
        return
    markers = [name for name, pat in SIGNALS if re.search(pat, text, re.I)]
    if not markers:
        return
    home = state_home()
    (home / "pending").mkdir(parents=True, exist_ok=True)
    (home / "pending" / f"{sid}.json").write_text(json.dumps({
        "session_id": sid,
        "transcript_path": str(tpath),
        "cwd": cwd,
        "markers": markers,
        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
    }))


def _candidate_meta(path):
    meta = {"created": "", "ttl_days": 30, "status": "confirmed"}
    for line in path.read_text().splitlines():
        if line.startswith("created:"):
            meta["created"] = line[len("created:"):].strip()
        elif line.startswith("ttl_days:"):
            try:
                meta["ttl_days"] = int(line[len("ttl_days:"):].strip())
            except ValueError:
                pass
        elif line.startswith("status:"):
            meta["status"] = line[len("status:"):].strip()
        elif line.startswith("---") and meta["created"]:
            break  # end of frontmatter once we've seen fields
    return meta


def _is_expired(meta, today):
    if meta["status"] == "promoted":
        return False
    try:
        created = datetime.date.fromisoformat(meta["created"])
    except (ValueError, TypeError):
        return False  # unparseable created -> never expire (conservative)
    return created + datetime.timedelta(days=meta["ttl_days"]) < today


def cmd_expired(args):
    today = datetime.date.fromisoformat(args.today) if args.today else datetime.date.today()
    d = state_home() / "candidates"
    if not d.exists():
        return
    for p in sorted(d.glob("*.md")):
        if _is_expired(_candidate_meta(p), today):
            print(p.stem)


def cmd_remove(args):
    base = (state_home() / "candidates").resolve()
    target = (base / f"{args.slug}.md").resolve()
    # validasi: target harus di dalam base dan berakhiran .md
    if target.parent != base or target.suffix != ".md":
        return  # tolak path traversal / di luar candidates/ tanpa menghapus
    if target.exists():
        target.unlink()


SKILLS_DIR_ENV = "GEAR_SKILLS_DIR"


def _skills_dir():
    return Path(os.environ.get(SKILLS_DIR_ENV, Path.home() / ".claude" / "skills"))


def cmd_install_skill(args):
    name = args.name
    # clean kebab slug, start+end alphanumeric (no trailing dash), bounded length
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name) or name.endswith("-") or len(name) > 64:
        sys.stderr.write(f"invalid skill name: {name}\n")
        raise SystemExit(2)
    dest_dir = _skills_dir() / args.name
    dest = dest_dir / "SKILL.md"
    if dest.exists() and not args.force:
        sys.stderr.write(f"skill already exists: {dest} (use --force)\n")
        raise SystemExit(2)
    src = Path(args.src)
    if not src.exists():
        sys.stderr.write(f"source not found: {src}\n")
        raise SystemExit(2)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest.write_text(src.read_text())
    print(dest)


def cmd_promote(args):
    p = state_home() / "candidates" / f"{args.slug}.md"
    if not p.exists():
        return
    txt = p.read_text()
    if "status: confirmed" in txt:
        p.write_text(txt.replace("status: confirmed", "status: promoted", 1))


def cmd_lesson_block(args):
    lines = [f"### {args.title} ({args.date})", ""]
    lines.append(f"**Problem:** {args.problem}")
    lines.append("")
    lines.append(f"**Solution:** {args.solution}")
    if args.example:
        lines.append("")
        lines.append(f"**Example:** {args.example}")
    print("\n".join(lines))


def build_parser():
    ap = argparse.ArgumentParser(prog="retro")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init", help="create the retro state store").set_defaults(func=cmd_init)
    c = sub.add_parser("candidate", help="write a reusable-technique candidate")
    c.set_defaults(func=cmd_candidate)
    c.add_argument("--name", required=True)
    c.add_argument("--confidence", type=float, required=True)
    c.add_argument("--problem", required=True)
    c.add_argument("--solution", required=True)
    c.add_argument("--example", default="")
    c.add_argument("--triggers", nargs="*", default=[])
    c.add_argument("--session", default="")
    c.add_argument("--created", default="")
    c.add_argument("--ttl", type=int, default=30)
    lst = sub.add_parser("list", help="list candidate lessons")
    lst.set_defaults(func=cmd_list)
    lst.add_argument("--long", action="store_true", help="show slug + triggers + problem for dedup")
    sub.add_parser("detect", help="SessionEnd: stage a pending pointer for a gear session with signal").set_defaults(func=cmd_detect)
    sub.add_parser("nudge", help="SessionStart: one-line passive nudge if pending lessons exist").set_defaults(func=cmd_nudge)
    sub.add_parser("pending", help="list staged pending session ids").set_defaults(func=cmd_pending)
    h = sub.add_parser("harvested", help="mark a session id as harvested")
    h.set_defaults(func=cmd_harvested)
    h.add_argument("session_id")
    e = sub.add_parser("expired", help="list candidate slugs past their TTL (excludes promoted)")
    e.set_defaults(func=cmd_expired)
    e.add_argument("--today", default="", help="override today's date (YYYY-MM-DD) for testing")
    rm = sub.add_parser("remove", help="delete one candidate by slug (validated to candidates/)")
    rm.set_defaults(func=cmd_remove)
    rm.add_argument("slug")
    pr = sub.add_parser("promote", help="mark a candidate as promoted (exempt from prune)")
    pr.set_defaults(func=cmd_promote)
    pr.add_argument("slug")
    lb = sub.add_parser("lesson-block", help="format one LESSONS-FROM-RUNS.md entry")
    lb.set_defaults(func=cmd_lesson_block)
    lb.add_argument("--title", required=True)
    lb.add_argument("--date", required=True)
    lb.add_argument("--problem", required=True)
    lb.add_argument("--solution", required=True)
    lb.add_argument("--example", default="")
    ins = sub.add_parser("install-skill", help="write a graduated skill to the skills dir (validated)")
    ins.set_defaults(func=cmd_install_skill)
    ins.add_argument("--name", required=True)
    ins.add_argument("--from", dest="src", required=True)
    ins.add_argument("--force", action="store_true")
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
