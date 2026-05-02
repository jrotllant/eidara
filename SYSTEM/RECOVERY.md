# DARA RECOVERY — Emergency Procedures
**Last updated:** 2026-04-30
**When to use:** When DARA files are corrupted, missing, or the system behaves unexpectedly.

---

## RECOVERY PRIORITY ORDER

Always try these in order:
1. **Git** (fastest): `git checkout -- <file>` restores any file to its last committed version. `git log --oneline` shows history. `git diff` shows what changed.
2. **System backups**: `VAULT/BACKUP/SYSTEM/` — Librarian-maintained copies of the 4 W3(b) protected files (compile.py, DARA.md, agent-architect.md, watcher.py). Up to 3 recent copies of each, rotated automatically.
3. **Compiler backups**: `VAULT/BACKUP/brain_*.md` — for BRAIN.md only (up to 60 snapshots, auto-pruned).
4. **Manual reconstruction**: Architect rebuilds from VAULT sources + system knowledge.

If git is not available, skip to step 2.

---

## SCENARIO 1: BRAIN.md is missing or corrupted

**Fix:**
1. Run `python SYSTEM/compile.py` — it regenerates BRAIN.md from VAULT sources. This is the fastest fix.
2. If compile.py fails, restore from backup: `cp VAULT/BACKUP/brain_YYYY-MM-DD_HHMM.md LIBRARY/BRAIN.md`
3. If both fail: ask any AI to read all VAULT files and concatenate them into BRAIN.md.

---

## SCENARIO 2: compile.py is broken or corrupted

**Fix:**
1. **Git:** `git checkout -- SYSTEM/compile.py` — instant restore to last committed version.
2. **System backup:** Copy the most recent `VAULT/BACKUP/SYSTEM/compile_*.py` to `SYSTEM/compile.py`.
3. If neither available: Architect rewrites from Constitution + VAULT structure knowledge.

**Note:** compile.py is W3(b) protected. Only the Architect can modify it.

---

## SCENARIO 3: DARA.md (Constitution) is corrupted or truncated

**This is the most critical file. Handle with extreme care.**

**Detection:** If `wc -l DARA.md` shows significantly fewer lines than expected (~226 as of v1.0), it's truncated. Check last lines with `tail -3 DARA.md` — should end with the AUTO-MEMORY COEXISTENCE section.

**Fix:**
1. **Git:** `git checkout -- DARA.md` — instant restore to last committed version.
2. **Git history:** `git log --oneline -- DARA.md` to see all versions. `git show <commit>:DARA.md` to inspect before restoring.
3. **System backup:** Copy the most recent `VAULT/BACKUP/SYSTEM/DARA_*.md` to `DARA.md`.
4. If none available: Architect reconstructs from knowledge of the Constitution structure.

**Prevention (W12):** After any edit to DARA.md, always verify with `tail -3 DARA.md` and `wc -l DARA.md`. Never use the Edit tool on this file — always use bash for writes.

**Note:** DARA.md is W3(b) protected. Only the Architect can modify it.

---

## SCENARIO 4: VAULT files are corrupted, truncated, or missing

**Detection:**
- Run `compile.py` — reports warnings for missing status, broken refs, missing tags.
- Any `.md` file with 0 bytes or <50 bytes is likely corrupted.
- Check with `wc -c VAULT/NEURONS/*.md` for suspiciously small files.

**Fix:**
1. **Git:** `git checkout -- VAULT/NEURONS/<file>.md` — restores specific file.
2. **Git bulk restore:** `git checkout -- VAULT/` — restores all VAULT files to last commit.
3. After restoring, run `compile.py` to verify and regenerate BRAIN.md.

**Prevention (W12):** After editing any VAULT file, verify with `tail` and `wc -l`. For files with special characters or >300 lines, use bash for writes.

---

## SCENARIO 5: changelog.md is overwritten or lost

**Fix:**
1. **Git:** `git checkout -- VAULT/changelog.md`
2. If no git: entries will be lost. Start a fresh changelog and note the gap.

**Note:** changelog.md is append-only (W7). Overwriting = protocol violation.

---

## SCENARIO 6: System integrity check

Run these steps to verify DARA is healthy:

1. **Git status:** `git status` — should show clean or only expected changes.
2. **Compile:** `python SYSTEM/compile.py` — should complete with 0 errors, 0 warnings.
3. **BRAIN.md:** should exist with compiled content. Size scales with your VAULT — typically ~3-5K chars (~900 tokens) for a fresh install, growing to 15K+ chars (~4K tokens) with heavier use.
4. **DARA.md:** `tail -3 DARA.md` should end with the Auto-Memory section. Line count ~226 as of v1.0.
5. **File counts:** check health.json for current totals (starts with 2 starter neurons + 4 enablers; grows as you populate it).
6. **INBOX:** check for pending feedback files.
7. **System backups:** `VAULT/BACKUP/SYSTEM/` should have recent copies (maintained by Librarian).
8. **BRAIN backups:** `VAULT/BACKUP/brain_*.md` should have recent snapshots.

---

## EMERGENCY CONTACTS

- **Architect mode:** the user says "activate architect mode" or "open the golden door"
- **Git history:** `git log --oneline` (in DARA root folder)
- **System backups:** `VAULT/BACKUP/SYSTEM/` (Librarian-maintained, up to 3 copies per file)
- **Watcher:** `SYSTEM/watcher.py` (runs via Startup shortcut to `SYSTEM/watcher_silent.vbs`). Re-run `SYSTEM/SETUP_AUTOSTART.bat` if moved.

---

## F5 — Cowork Sandbox Limitation

When running from Claude Desktop Cowork, the Linux sandbox FUSE mount cannot list VAULT/ directories (os.listdir returns []). compile.py must be run via Windows PowerShell, not from the bash sandbox.

**Workaround:** Use PowerShell MCP to run compile.py:
```
python "<YOUR_DARA_ROOT>\SYSTEM\compile.py"
```
