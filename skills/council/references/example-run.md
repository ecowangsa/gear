# council - worked example (the quality bar)

This is one complete, real council run, written in the **current** flow
(divergence gate, `CERTAINTY` bands, verdict-first synthesis). Read it to
calibrate the *depth* expected: members take sharp, one-sided positions; the
debate **actually moves** stances (it is not a rubber stamp); and the Chair's
synthesis surfaces the *real shape* of the disagreement plus concrete, actionable
conditions - not a grey average. Aim for this quality; don't pad to reach this
length.

---

**Question:** When opening an *encrypted* iOS backup, should we stage the
decrypted `ChatStorage.sqlite` as a plaintext file in the working dir (reuse the
existing read path + blake3 + chain-of-custody log), or decrypt on-the-fly into
memory only?

**Compose:** sensitive-data / security question → seat `security`, `compliance`,
`contrarian` (a focused subset of `safeguard` - no ops/deploy surface here, so
`operability` is left out → **3 lenses**, Sonnet).
*"Convening council (safeguard, focused): security, compliance, contrarian."*

**Round 1 (the split):**
- `security` → **B (memory-only)**. Plaintext on disk persists across
  crashes, swap, SSD wear-leveling/remanence; the investigator's own tool would
  create the very artifacts examiners hunt for. *(CERTAINTY: firm - flips if
  custody provably requires a durable on-disk artifact.)*
- `compliance` → **A (plaintext + controls)**. Chain-of-custody needs
  a *verifiable hashed artifact*; memory-only leaves an "evidence gap"; a two-tier
  log (some files logged, some silent) undermines trust. *(CERTAINTY: lean -
  flips if an in-memory hash closes the custody gap as well as a file does.)*
- `contrarian` → **challenges the premise**: a password-taking decryptor
  is no longer a "passive viewer" but an "evidence transformer"; maybe decrypt
  with a validated *external* tool and feed plaintext in. *(CERTAINTY: shaky -
  flips if the in-house decrypt can be made provably non-mutating.)*

**Gate:** R1 split (security:B / compliance:A / contrarian:reframe), **no plurality →
debate all three.**

**Round 2 (debate moved positions):** the security member's rebuttal - *hash the
decrypted bytes in memory before opening SQLite, log that hash + the ciphertext
hash; custody is anchored to hash equality, not file presence* - flipped both
others. Compliance **CHANGED A→B** (conceding the hash closes the logical gap)
but **HOLDS** that the hash must be **API-enforced**. The Contrarian **CHANGED**
to concede the feature can exist but **HOLDS** that "memory-only" is a *spec, not
a guarantee* (SQLite may spill to WAL/temp files) and that a **consent gate** is
mandatory.

**The Chair's synthesis (abridged):**

> **Verdict (TL;DR):** Adopt **B (memory-only)** as the default; custody is
> satisfied by in-memory hashing of {ciphertext, plaintext, algo, timestamp,
> session}. **Certainty: firm.** Flips if: a real adversarial-litigation need
> demands a durable on-disk artifact.
>
> **Consensus:** B by default; the in-memory hash, not file presence, anchors
> chain-of-custody.
>
> **Disagreement:** (1) contrarian - must *prove* SQLite never spills plaintext to
> disk; (2) compliance - the hash must be enforced at the API/type level, not by
> convention; (3) compliance residual - a durable artifact (A) may be more
> defensible in high-stakes adversarial litigation.
>
> **Reasoning & conditions:** B may only *claim* memory-only once (a) SQLite disk
> I/O is forced off (`temp_store=MEMORY`, no WAL, no temp fallback - verified),
> (b) the decrypt API returns `(bytes, hash)` so custody is unskippable, (c) the
> key/plaintext are zeroized and core dumps suppressed, with residual swap risk
> documented. Add a logged consent gate. Defer an optional Option-A mode unless a
> real adversarial-litigation need appears.

**Why this is a good run:** the seating fit the question; the three lenses gave
genuinely different first answers; the **gate detected a real split** and sent
all three to debate; that debate produced *movement and a crux* (the in-memory-
hash rebuttal), not three monologues; and the Chair led with the decision, then gave
the exact engineering conditions that make it safe - the kind of thing a single
pass would have missed (the SQLite-temp-spill trap, the type-enforced hash).
