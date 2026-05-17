# EIDARA UPDATE — v1.0 → v2.0

**Release date:** 2026-05-17
**Effort to upgrade:** ~5 minutes
**Risk:** Low (only 4 files replaced; your VAULT data is untouched)

---

## What's new in v2.0

Six defense-in-depth improvements that turn DARA from "good if you actively maintain it" to "self-correcting if you ignore it for weeks."

### 1. Librarian self-trigger (A + B + C)
The biggest behavioural change. v1 modelled the Librarian as owner-initiated only — AIs never proactively suggested running it, so it drifted. v2 closes that gap with three controls:

- **A — BRAIN.md header shows Librarian status.** Every read of BRAIN.md shows `**Librarian:** YYYY-MM-DD (N days ago) — OK / OVERDUE (cadence: 3d)` right below the Compiled line. No more buried-in-stats invisibility.
- **B — Alert threshold tightened from 7d to 3d.** Eliminates the silent 4-day window between "overdue" and "alerted."
- **C — W6 mandatory prompt.** The post-compile status report (W6) now MUST include the Librarian status, and AIs MUST ask the user to run it if OVERDUE.

### 2. Missing-summary auto-push (C1 + C2 + C3)
Same defense-in-depth pattern, applied to large neurons without `→brain:` summaries (which silently inflate BRAIN.md tokens):

- **C1 — Auto-INBOX feedback.** When compile detects neurons >1500 chars without `→brain:`, it auto-writes a feedback file to INBOX with the list. The next AI sees it and picks it up.
- **C2 — Header surface.** BRAIN.md header shows `**To-do:** N neuron(s) need →brain: summary` when N>0.
- **C3 — W6 prompt extension.** W6 now also reports missing-summary count and prompts the user to generate them.

### 3. W11(b) — Session-closing summaries lean
W9 closing recaps must be ≤500 words per neuron. Longer recaps go to a dedicated `session-YYYY-MM-DD-topic.md` neuron. Plus compile.py emits an explicit WARNING when any single neuron grows ≥50% AND >1000 chars in one compile. Prevents the "AI dumps 12KB into a single neuron at session end" failure mode.

### 4. W12.5 — Sandbox/FUSE stale-view caveat
W12 (verify writes) now has a 5th point: when working in sandboxed environments (FUSE mounts, dev containers), files can *appear* truncated due to stale cached reads while the disk is intact. Cross-verify before any restore. Prevents false-alarm rollback cascades.

### 5. F1.B — W3(b) integrity check
New compile step 0: tracks sizes of the 5 protected files (DARA.md, compile.py, validators.py, watcher.py, agent-architect.md) in `SYSTEM/.w3b_sizes.json`. Any size drop ≥50 B without justification fires a CRITICAL alert with a rollback pointer.

### 6. G.B — Cowork environment detection
`compile.py` now detects Cowork/sandboxed runs (`/sessions/.../mnt/` paths) and skips the git auto-commit step with a clean message (instead of the ugly `fatal: cannot lock ref HEAD` error). Your local watcher continues to commit normally.

### 7. Anti-tampering of `.librarian-last-run`
v1 trusted `.librarian-last-run` as source of truth for "when was the Librarian last run." v2 cross-checks: if `lastLibrarianDays=0` but no `[Librarian]` entry exists in today's changelog, compile emits a SUSPICIOUS alert. Catches the failure mode where a watcher or script touches the timestamp without doing real Librarian work.

### 8. Librarian MISSION section
`agent-librarian.md` now opens with an explicit MISSION section: "Format checking is necessary but not sufficient. A pass with zero corrections is a status report, not a Librarian run." Combined with the anti-tampering check, this forces real optimisation work (linking orphans, generating summaries, removing duplicates, proposing merges) rather than just timestamp updates.

### 9. Bonus: validators auto-fix more arrow typos
`validators.py` now auto-converts `->brain:` and `->detail:` to Unicode arrows (was only handling `->refs:`, `->tags:`, `->flag:`). Closes a silent BRAIN-inflation bug.

---

## What's NOT changed

Your data — **none of your VAULT content is touched**. The upgrade only replaces:

- `DARA.md` (the constitution)
- `SYSTEM/compile.py` + `SYSTEM/validators.py` (the compiler)
- `VAULT/ENABLERS/agent-librarian.md` (the Librarian protocol)
- `SYSTEM/config.json` (version bump only)
- `INSTALL` and `PROJECT/README.md` (version bump + v2 notes)

Your `VAULT/NEURONS/`, `VAULT/ENABLERS/` (except agent-librarian), `VAULT/INBOX/`, `VAULT/changelog.md`, `VAULT/BACKUP/`, and `LIBRARY/BRAIN.md` are all preserved as-is.

---

## How to upgrade — 4 steps (~5 minutes)

### Step 1 — Backup your current DARA
Open PowerShell (Windows) or Terminal (Mac/Linux) and run:
```
cd C:\Users\YourName\Desktop
Copy-Item -Recurse -Path DARA -Destination "DARA_v1_backup_$(Get-Date -Format yyyy-MM-dd)"
```
(Mac/Linux: `cp -r ~/Desktop/DARA ~/Desktop/DARA_v1_backup_$(date +%Y-%m-%d)`)

If anything goes wrong, you can restore by replacing the upgraded folder with this backup.

### Step 2 — Download the v2.0 package
Get `DOWNLOAD DARA_v2.0/` from `https://www.eidara.dev`.

### Step 3 — Replace the 5 system files
From the v2.0 package, copy these into your existing DARA folder, overwriting the v1 versions:

- `DARA.md`
- `SYSTEM/compile.py`
- `SYSTEM/validators.py`
- `SYSTEM/config.json`
- `VAULT/ENABLERS/agent-librarian.md`

**Do NOT touch anything else.** Your NEURONS, your changelog, your BRAIN.md — all stay.

### Step 4 — Verify
Run `python SYSTEM/compile.py` once. You should see:
- `BRAIN.md compiled!` at the end
- `[10/10] Git auto-commit...` step (Cowork users will see `GIT: Skipped` cleanly)
- `Compiler version: 3.2` in the COMPILATION STATS section
- The BRAIN header now showing a `**Librarian:** ...` line

Open `LIBRARY/BRAIN.md` and check the header has the new Librarian line.

You're on v2.0.

---

## First-time things you'll see on v2.0

**On your next compile after upgrade:**

1. **`Librarian: never run — run agent-librarian to initialize`** in the header.
   This is the new visibility working. If you've been running the Librarian (manually or via script), update `VAULT/.librarian-last-run` with today's date (`YYYY-MM-DD`) and add a `[Librarian]` entry to today's changelog section — the anti-tampering check needs both.

2. **`SYSTEM/.w3b_sizes.json` is created**, capturing baseline sizes of the 5 protected files. Future compiles will compare against this baseline.

3. **`SYSTEM/.w3b_sizes.json` baseline is now part of your DARA** — back it up alongside `.protected_checksums.json`.

4. **If you had any neuron with `->brain:` (ASCII arrow) instead of `→brain:`**, the validator will auto-fix it on the next compile and report it as `FIXED:` in the output.

5. **If you have neurons >1500 chars without a `→brain:` summary**, the next compile will:
    - Show them in the BRAIN header `**To-do:**` line
    - Auto-write `VAULT/INBOX/feedback-YYYY-MM-DD-missing-brain.md`
   This is intentional — it's pushing you to generate the summaries.

---

## Troubleshooting

**Q: My next compile shows `librarian timestamp SUSPICIOUS`. What does it mean?**
A: The compile noticed `.librarian-last-run` is set to today but there's no `[Librarian]` entry in today's changelog. Either: (a) you set the timestamp manually without doing a Librarian pass (add a `[Librarian]` log entry), or (b) some script/watcher touched the file (investigate what). This is the anti-tampering check working as intended.

**Q: I get a CRITICAL alert about W3(b) integrity failure.**
A: One of the 5 protected files dropped in size unexpectedly. Most likely cause: an Edit-tool truncation. Roll back from `VAULT/BACKUP/SYSTEM/` (most recent timestamp before the drop). See `SYSTEM/RECOVERY.md`.

**Q: How do I rollback to v1?**
A: Replace the 5 upgraded files with their v1 versions (from your Step-1 backup or from `DOWNLOAD DARA_v1.0/`). Delete `SYSTEM/.w3b_sizes.json` (v1 doesn't use it). Recompile. You're back on v1.

**Q: Will v2 break my existing scripts/agents/MCPs that read DARA?**
A: No. The reading interface (BRAIN.md, INDEX, →brain: summaries) is backward-compatible. The new lines (Librarian status, To-do, COMPILATION STATS additions) are additive and don't break anything. The encoding stays the same.

---

## Changelog (compact)

- **compile.py:** v3.1 → v3.2. +`_is_cowork_env()`, +`check_w3b_integrity()`, +`lib_hdr` in `extract_header()`, +`C2` missing-brain header surface, +`C1` auto-INBOX, +anti-tampering check, +Cowork git skip, +W11(b) bloat warning in delta report. Threshold change `lib_days > 7 → > 3`.
- **validators.py:** +auto-fix for `->brain:` and `->detail:` arrows.
- **DARA.md:** v6.2.0 → v6.3.0. +W11(b), +W12 point 5 (FUSE caveat), +W6 extended (Librarian prompt + missing-brain prompt).
- **agent-librarian.md:** +MISSION section, +anti-tampering note. Mission now explicit that format-checking is not enough.
- **config.json:** version → 3.2.

---

## Created by Javier Rotllant Miras

MIT License · https://www.eidara.dev
