import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "retro.py"

class RetroBase(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp()
        self.env = {**os.environ, "GEAR_HOME": self.home}

    def retro(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True, text=True, env=self.env,
        )

class TestInit(RetroBase):
    def test_init_creates_store_idempotently(self):
        r = self.retro("init")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((Path(self.home) / "pending").is_dir())
        self.assertTrue((Path(self.home) / "candidates").is_dir())
        self.assertTrue((Path(self.home) / "harvested.log").exists())
        # idempotent: second run also succeeds
        self.assertEqual(self.retro("init").returncode, 0)

class TestCandidate(RetroBase):
    def test_candidate_writes_templated_frontmatter(self):
        r = self.retro(
            "candidate",
            "--name", "Retry With Backoff",
            "--confidence", "0.7",
            "--problem", "flaky network calls fail intermittently",
            "--solution", "wrap in exponential backoff with jitter",
            "--example", "see api/client.py:42",
            "--triggers", "network", "retry",
            "--session", "abc123",
            "--created", "2026-06-20",
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        path = Path(self.home) / "candidates" / "retry-with-backoff.md"
        self.assertTrue(path.exists())
        text = path.read_text()
        self.assertIn("name: retry-with-backoff", text)
        self.assertIn("class: reusable-technique", text)
        self.assertIn("confidence: 0.7", text)
        self.assertIn("status: confirmed", text)
        self.assertIn("ttl_days: 30", text)
        self.assertIn("source_session: abc123", text)
        self.assertIn('triggers: ["network", "retry"]', text)
        self.assertIn("flaky network calls", text)
        self.assertIn("exponential backoff", text)
        self.assertIn("api/client.py:42", text)
        self.assertEqual(r.stdout.strip(), str(path))

class TestList(RetroBase):
    def test_list_returns_candidate_filenames(self):
        self.retro("candidate", "--name", "Foo Bar", "--confidence", "0.5",
                    "--problem", "p", "--solution", "s")
        r = self.retro("list")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("foo-bar.md", r.stdout)

    def test_list_empty_store_is_ok(self):
        self.retro("init")
        r = self.retro("list")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), "")

class TestListLong(RetroBase):
    def test_list_long_shows_slug_triggers_problem(self):
        self.retro("candidate", "--name", "Retry With Backoff", "--confidence", "0.7",
                    "--problem", "flaky network calls fail intermittently",
                    "--solution", "exponential backoff", "--triggers", "network", "retry")
        r = self.retro("list", "--long")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("retry-with-backoff", r.stdout)
        self.assertIn("triggers: network, retry", r.stdout)
        self.assertIn("problem: flaky network calls", r.stdout)

    def test_list_plain_unchanged(self):
        self.retro("candidate", "--name", "Foo", "--confidence", "0.5",
                    "--problem", "p", "--solution", "s")
        r = self.retro("list")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("foo.md", r.stdout)
        self.assertNotIn("triggers:", r.stdout)

class TestPendingHarvested(RetroBase):
    def test_pending_lists_ids(self):
        self.retro("init")
        (Path(self.home) / "pending" / "sx.json").write_text("{}")
        r = self.retro("pending")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("sx", r.stdout)

    def test_harvested_appends_id(self):
        self.retro("init")
        r = self.retro("harvested", "sx")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("sx", (Path(self.home) / "harvested.log").read_text())

    def test_harvested_idempotent(self):
        self.retro("init")
        self.retro("harvested", "sx")
        self.retro("harvested", "sx")
        ids = [l for l in (Path(self.home) / "harvested.log").read_text().splitlines() if l.strip() == "sx"]
        self.assertEqual(len(ids), 1)


class TestNudge(RetroBase):
    def nudge(self):
        return subprocess.run([sys.executable, str(SCRIPT), "nudge"],
                              capture_output=True, text=True, env=self.env)

    def test_nudge_emits_one_line_when_pending(self):
        self.retro("init")
        (Path(self.home) / "pending" / "s1.json").write_text("{}")
        (Path(self.home) / "pending" / "s2.json").write_text("{}")
        r = self.nudge()
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout)
        ctx = out["hookSpecificOutput"]["additionalContext"]
        self.assertIn("2", ctx)
        self.assertIn("/gear:retro", ctx)
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "SessionStart")

    def test_nudge_silent_when_empty(self):
        self.retro("init")
        r = self.nudge()
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")


class DetectBase(RetroBase):
    def setUp(self):
        super().setUp()
        self.projects = tempfile.mkdtemp()
        self.env["GEAR_PROJECTS_DIR"] = self.projects

    def write_transcript(self, cwd, session_id, body):
        import re as _re
        slug = _re.sub(r"[^A-Za-z0-9]", "-", cwd)
        d = Path(self.projects) / slug
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{session_id}.jsonl").write_text(body)

    def detect(self, payload):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "detect"],
            input=json.dumps(payload), capture_output=True, text=True, env=self.env,
        )

class TestDetect(DetectBase):
    def test_gear_session_with_signal_stages_pending(self):
        self.write_transcript("/proj/a", "sid1",
            'used /gear:sdlc here\n{"root cause": "off-by-one"}\n')
        r = self.detect({"session_id": "sid1", "cwd": "/proj/a"})
        self.assertEqual(r.returncode, 0, r.stderr)
        pf = Path(self.home) / "pending" / "sid1.json"
        self.assertTrue(pf.exists())
        data = json.loads(pf.read_text())
        self.assertEqual(data["session_id"], "sid1")
        self.assertTrue(data["markers"])  # non-empty

    def test_non_gear_session_skipped(self):
        self.write_transcript("/proj/b", "sid2", 'plain coding\nroot cause: x\n')
        r = self.detect({"session_id": "sid2", "cwd": "/proj/b"})
        self.assertEqual(r.returncode, 0)
        self.assertFalse((Path(self.home) / "pending" / "sid2.json").exists())

    def test_gear_session_no_signal_skipped(self):
        self.write_transcript("/proj/c", "sid3", 'used /gear:council, nothing notable\n')
        r = self.detect({"session_id": "sid3", "cwd": "/proj/c"})
        self.assertEqual(r.returncode, 0)
        self.assertFalse((Path(self.home) / "pending" / "sid3.json").exists())

    def test_already_harvested_skipped(self):
        self.retro("init")
        (Path(self.home) / "harvested.log").write_text("sid4\n")
        self.write_transcript("/proj/d", "sid4", '/gear:retro\nroot cause: y\n')
        r = self.detect({"session_id": "sid4", "cwd": "/proj/d"})
        self.assertFalse((Path(self.home) / "pending" / "sid4.json").exists())

    def test_missing_transcript_silent(self):
        r = self.detect({"session_id": "nope", "cwd": "/proj/none"})
        self.assertEqual(r.returncode, 0)
        self.assertFalse((Path(self.home) / "pending" / "nope.json").exists())

    def test_malformed_stdin_never_crashes(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "detect"],
                           input="not json", capture_output=True, text=True, env=self.env)
        self.assertEqual(r.returncode, 0)

    def test_oversize_transcript_skipped(self):
        self.write_transcript("/proj/big", "sidBig", 'used /gear:sdlc\nroot cause: huge\n')
        env = {**self.env, "GEAR_MAX_BYTES": "10"}  # tiny cap forces the size guard
        r = subprocess.run([sys.executable, str(SCRIPT), "detect"],
                           input=json.dumps({"session_id": "sidBig", "cwd": "/proj/big"}),
                           capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0)
        self.assertFalse((Path(self.home) / "pending" / "sidBig.json").exists())


class TestExpired(RetroBase):
    def make(self, name, created, ttl="30", status=None):
        # tulis kandidat via cmd candidate (status default 'confirmed'), lalu set status bila perlu
        self.retro("candidate", "--name", name, "--confidence", "0.6",
                    "--problem", "p", "--solution", "s", "--created", created, "--ttl", ttl)
        if status:
            from pathlib import Path as _P
            slug = name.strip().lower().replace(" ", "-")
            p = _P(self.home) / "candidates" / f"{slug}.md"
            txt = p.read_text().replace("status: confirmed", f"status: {status}")
            p.write_text(txt)

    def test_old_candidate_is_expired(self):
        self.make("Old One", "2026-01-01", ttl="30")   # jauh di masa lalu
        r = self.retro("expired", "--today", "2026-06-20")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("old-one", r.stdout)

    def test_fresh_candidate_not_expired(self):
        self.make("Fresh One", "2026-06-19", ttl="30")
        r = self.retro("expired", "--today", "2026-06-20")
        self.assertNotIn("fresh-one", r.stdout)

    def test_promoted_candidate_exempt(self):
        self.make("Promoted One", "2026-01-01", ttl="30", status="promoted")
        r = self.retro("expired", "--today", "2026-06-20")
        self.assertNotIn("promoted-one", r.stdout)

    def test_broken_created_not_expired(self):
        self.make("Broken One", "2026-01-01", ttl="30")
        from pathlib import Path as _P
        p = _P(self.home) / "candidates" / "broken-one.md"
        p.write_text(p.read_text().replace("created: 2026-01-01", "created: not-a-date"))
        r = self.retro("expired", "--today", "2026-06-20")
        self.assertNotIn("broken-one", r.stdout)


class TestRemove(RetroBase):
    def test_remove_deletes_candidate(self):
        self.retro("candidate", "--name", "Zap Me", "--confidence", "0.5",
                    "--problem", "p", "--solution", "s")
        p = Path(self.home) / "candidates" / "zap-me.md"
        self.assertTrue(p.exists())
        r = self.retro("remove", "zap-me")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(p.exists())

    def test_remove_missing_is_silent_noop(self):
        self.retro("init")
        r = self.retro("remove", "ghost")
        self.assertEqual(r.returncode, 0)

    def test_remove_rejects_path_traversal(self):
        self.retro("init")
        # buat file sensitif di luar candidates/
        outside = Path(self.home) / "secret.md"
        outside.write_text("keep me")
        r = self.retro("remove", "../secret")
        self.assertTrue(outside.exists(), "remove must not delete files outside candidates/")


class TestPromote(RetroBase):
    def test_promote_flips_status(self):
        self.retro("candidate", "--name", "Grad Me", "--confidence", "0.8",
                    "--problem", "p", "--solution", "s")
        r = self.retro("promote", "grad-me")
        self.assertEqual(r.returncode, 0, r.stderr)
        txt = (Path(self.home) / "candidates" / "grad-me.md").read_text()
        self.assertIn("status: promoted", txt)
        self.assertNotIn("status: confirmed", txt)

    def test_promote_idempotent_and_missing_safe(self):
        self.retro("candidate", "--name", "Grad Me", "--confidence", "0.8",
                    "--problem", "p", "--solution", "s")
        self.retro("promote", "grad-me")
        r = self.retro("promote", "grad-me")   # kedua kali
        self.assertEqual(r.returncode, 0)
        self.assertEqual(self.retro("promote", "ghost").returncode, 0)  # tak ada file


class TestInstallSkill(RetroBase):
    def setUp(self):
        super().setUp()
        self.skills = tempfile.mkdtemp()
        self.env["GEAR_SKILLS_DIR"] = self.skills

    def src(self, body="---\nname: x\ndescription: y\n---\nbody\n"):
        f = Path(self.home) / "draft.md"
        f.write_text(body)
        return str(f)

    def test_install_writes_skill(self):
        r = self.retro("install-skill", "--name", "my-skill", "--from", self.src())
        self.assertEqual(r.returncode, 0, r.stderr)
        dest = Path(self.skills) / "my-skill" / "SKILL.md"
        self.assertTrue(dest.exists())
        self.assertIn("name: x", dest.read_text())

    def test_install_rejects_dirty_slug(self):
        r = self.retro("install-skill", "--name", "../evil", "--from", self.src())
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse((Path(self.skills) / ".." / "evil").exists())

    def test_install_refuses_overwrite_without_force(self):
        self.retro("install-skill", "--name", "dup", "--from", self.src())
        r = self.retro("install-skill", "--name", "dup", "--from", self.src("changed"))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("name: x", (Path(self.skills) / "dup" / "SKILL.md").read_text())  # tak tertimpa

    def test_install_force_overwrites(self):
        self.retro("install-skill", "--name", "dup", "--from", self.src())
        r = self.retro("install-skill", "--name", "dup", "--from", self.src("changed"), "--force")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((Path(self.skills) / "dup" / "SKILL.md").read_text(), "changed")

    def test_install_rejects_trailing_dash_and_overlong(self):
        for bad in ["trailing-", "a" * 65]:
            r = self.retro("install-skill", "--name", bad, "--from", self.src())
            self.assertNotEqual(r.returncode, 0, f"expected reject for {bad!r}")
            self.assertFalse((Path(self.skills) / bad / "SKILL.md").exists())


class TestLessonBlock(RetroBase):
    def test_lesson_block_format(self):
        r = self.retro("lesson-block", "--title", "Stop hook fires per turn",
                        "--date", "2026-06-20", "--problem", "assumed once per session",
                        "--solution", "use SessionEnd for once-per-session",
                        "--example", "hooks/hooks.json")
        self.assertEqual(r.returncode, 0, r.stderr)
        out = r.stdout
        self.assertIn("### Stop hook fires per turn (2026-06-20)", out)
        self.assertIn("**Problem:** assumed once per session", out)
        self.assertIn("**Solution:** use SessionEnd for once-per-session", out)
        self.assertIn("**Example:** hooks/hooks.json", out)

    def test_lesson_block_omits_empty_example(self):
        r = self.retro("lesson-block", "--title", "T", "--date", "2026-06-20",
                        "--problem", "p", "--solution", "s")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("**Example:**", r.stdout)


if __name__ == "__main__":
    unittest.main()
