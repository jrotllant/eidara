#!/usr/bin/env python3
"""
DARA Compiler v3.1
Reads VAULT/ -> validates -> AUTO-FIXES -> compresses -> generates LIBRARY/BRAIN.md

v2.0: auto-dedup, ghost ref cleanup, broken ref fix, CRED validation,
filename-header fix, staleness detection, INBOX check.
v2.1: READ routing line, ENCODING KEY section in BRAIN.md header.
v2.2: FEEDBACK REMINDER footer in BRAIN.md, auto-feedback file on warnings.
v2.3: dual-output logging (stdout+stderr), fixed truncation bugs.
v2.4: delta reporting (compare vs previous), [C/L] entries to ARCHIVE section.
v2.5: git integration (auto-init, auto-commit, warning if not installed).
v2.6: BRAIN.md protection (read-only lock + SHA256 checksum tamper detection).
v2.7: Warning header replaces lock. Checksum tamper fix. Git auto-commit.
v2.8: W8 kebab-case check, orphan file detection, W7 changelog format check, monetary format info.
v3.0: --dry-run mode, --stats quick health check, auto-purge archived entries.
v3.1: BRAIN efficiency — enabler one-liners, noise stripping, →brain: compression, Light Mode notice, INDEX active-only filter.
v3.2 (v2.0 release): F1.B (W3(b) integrity), G.B (Cowork git skip), Librarian self-trigger (A+B+C), anti-tampering check, C1 (auto-INBOX for missing →brain:), C2 (header surface), W11(b) bloat warning.

Usage:
  python compile.py                Full compilation
  python compile.py --dry-run      Validate without writing (safe preview)
  python compile.py --stats        Quick health check (no compilation)
  python compile.py --validate-only  Validate VAULT structure only (no compile)
  python compile.py --no-git       Compile but skip git auto-commit
"""

import re
import sys
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import hashlib
import json

from validators import (
    get_entry_date, fix_refs, fix_header, fix_ascii_arrows,
    check_creds, check_stale, dedup, content_similarity_check,
    check_kebab_case, check_orphan_files, check_changelog_format,
    check_monetary_format, check_misplaced_agents, check_size_regression,
    check_protected_files, check_brain_tamper
)

DARA_ROOT = Path(__file__).resolve().parent.parent
VAULT_DIR = DARA_ROOT / "VAULT"
NEURONS_DIR = VAULT_DIR / "NEURONS"
ENABLERS_DIR = VAULT_DIR / "ENABLERS"
INBOX_DIR = VAULT_DIR / "INBOX"
TRASH_DIR = VAULT_DIR / "TRASH"
BACKUP_DIR = VAULT_DIR / "BACKUP"
LIBRARY_DIR = DARA_ROOT / "LIBRARY"
BRAIN_FILE = LIBRARY_DIR / "BRAIN.md"
DARA_MD = DARA_ROOT / "DARA.md"
HEALTH_FILE = DARA_ROOT / "SYSTEM" / "health.json"
MAX_BACKUPS = 60
MAX_BACKUP_AGE_DAYS = 180
STALENESS_DAYS = 180
ARCHIVE_PURGE_DAYS = 60
BRAIN_THRESHOLD = 1500
COMPILER_VERSION = "3.2"
ARROW = "→"
WARNING = "⚠"
PROTECTED_FILES = ["DARA.md", "SYSTEM/compile.py", "SYSTEM/validators.py", "SYSTEM/watcher.py", "VAULT/ENABLERS/agent-architect.md"]
PROTECTED_CHECKSUMS_FILE = DARA_ROOT / "SYSTEM" / ".protected_checksums.json"
COMPILE_LOCK_FILE = DARA_ROOT / "SYSTEM" / ".compile.lock"
LOCK_STALE_SECONDS = 300  # locks older than 5 minutes are considered stale

# Load config (overrides defaults)
CONFIG_FILE = DARA_ROOT / "SYSTEM" / "config.json"
if CONFIG_FILE.exists():
    try:
        _cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        MAX_BACKUPS = _cfg.get("maxBackups", MAX_BACKUPS)
        MAX_BACKUP_AGE_DAYS = _cfg.get("maxBackupAgeDays", MAX_BACKUP_AGE_DAYS)
        STALENESS_DAYS = _cfg.get("stalenessDays", STALENESS_DAYS)
        ARCHIVE_PURGE_DAYS = _cfg.get("archivePurgeDays", ARCHIVE_PURGE_DAYS)
        BRAIN_THRESHOLD = _cfg.get("brainThreshold", 1500)
        COMPILER_VERSION = _cfg.get("version", "3.1")
    except (json.JSONDecodeError, OSError) as e:
        print(f"  WARNING: config.json is invalid or unreadable ({e}). Using defaults.", flush=True)

# CLI flags
DRY_RUN = "--dry-run" in sys.argv
STATS_ONLY = "--stats" in sys.argv
NO_GIT = "--no-git" in sys.argv
VALIDATE_ONLY = "--validate-only" in sys.argv

def log(msg=""):
    """Print to both stdout and stderr for sandbox compatibility."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"))
    try:
        print(msg, file=sys.stderr)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"), file=sys.stderr)

def ensure_dirs():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    LIBRARY_DIR.mkdir(parents=True, exist_ok=True)
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    TRASH_DIR.mkdir(parents=True, exist_ok=True)

def backup_previous_brain():
    """Backup BRAIN.md only if content changed since last backup."""
    if BRAIN_FILE.exists():
        current = BRAIN_FILE.read_text(encoding="utf-8")
        current_hash = hashlib.sha256(current.encode()).hexdigest()[:16]
        # Check if last backup has same content
        existing = sorted(BACKUP_DIR.glob("brain_*.md"), key=lambda f: f.stat().st_mtime)
        if existing:
            last = existing[-1].read_text(encoding="utf-8")
            last_hash = hashlib.sha256(last.encode()).hexdigest()[:16]
            if current_hash == last_hash:
                log("  Skipped backup (no changes since " + existing[-1].name + ")")
                return True
        ts = datetime.now().strftime("%Y-%m-%d_%H%M")
        dst = BACKUP_DIR / ("brain_" + ts + ".md")
        try:
            shutil.copy2(BRAIN_FILE, dst)
            log("  Backed up -> " + dst.name)
        except (PermissionError, OSError) as e:
            log("  WARNING: Backup failed (" + str(e) + ") - continuing without backup")
        return True
    return False

def prune_backups():
    bk = sorted(BACKUP_DIR.glob("brain_*.md"), key=lambda f: f.stat().st_mtime)
    cutoff = datetime.now() - timedelta(days=MAX_BACKUP_AGE_DAYS)
    pruned = 0
    # Phase 1: remove backups older than max age
    for b in bk:
        try:
            if datetime.fromtimestamp(b.stat().st_mtime) < cutoff:
                b.unlink()
                pruned += 1
        except OSError:
            pass
    # Phase 2: batch prune when approaching limit (at 90%, trim to 50%)
    bk = sorted(BACKUP_DIR.glob("brain_*.md"), key=lambda f: f.stat().st_mtime)
    threshold = int(MAX_BACKUPS * 0.90)
    target = int(MAX_BACKUPS * 0.50)
    if len(bk) >= threshold:
        to_remove = len(bk) - target
        for b in bk[:to_remove]:
            try:
                b.unlink()
                pruned += 1
            except OSError:
                pass
    if pruned:
        log("  Pruned " + str(pruned) + " old backup(s)")

def read_vault_files(directory, label):
    entries = []
    if not directory.exists():
        return entries
    # Check for non-.md files (#8 fix — invisible files warning)
    for f in sorted(directory.iterdir()):
        if f.is_file() and f.suffix != ".md" and not f.name.startswith("."):
            log("  WARNING: " + label + "/" + f.name + " is not a .md file — invisible to compiler and watcher")
    for f in sorted(directory.glob("*.md")):
        if f.name == "changelog.md":
            continue
        raw = f.read_text(encoding="utf-8", errors="replace")
        null_count = raw.count("\x00")
        if null_count:
            log("  ⚠ WARNING: " + f.name + " contains " + str(null_count) + " null bytes — stripped automatically. Investigate source!")
            raw = raw.replace("\x00", "")
            # Also clean the file on disk so the corruption doesn't persist
            try:
                f.write_text(raw, encoding="utf-8")
            except OSError:
                pass
        content = raw.strip()
        # Check for suspiciously short files (#7 fix — truncation detection)
        content_lines = [l for l in content.split("\n") if l.strip() and not l.strip().startswith("##")]
        if content_lines and len(content_lines) < 3:
            log("  WARNING: " + f.stem + " has only " + str(len(content_lines)) + " content line(s) — possible truncation")
        entries.append({
            "filename": f.stem,
            "filepath": f,
            "content": content,
            "category": label,
            "chars": len(content),
        })
    return entries

def get_all_filenames(neurons, enablers):
    return {e["filename"] for e in neurons + enablers}

def get_cred_names(enablers):
    creds = set()
    for e in enablers:
        if e["filename"] == "credentials":
            for m in re.finditer(r'\[CRED:([^\]]+)\]', e["content"]):
                creds.add(m.group(1))
    return creds

def extract_header():
    if not DARA_MD.exists():
        return "# DARA BRAIN - Compiled Memory\n\n> DARA.md not found.\n"
    text = DARA_MD.read_text(encoding="utf-8")
    lines = text.split("\n")
    h = []
    h.append("# DARA BRAIN - Compiled Memory")
    h.append("**Compiled:** " + datetime.now().strftime("%Y-%m-%d %H:%M") + " | **Source:** VAULT/")
    # A: Librarian status surfaced in header (visibility for all readers)
    librarian_file_hdr = VAULT_DIR / ".librarian-last-run"
    lib_hdr = "**Librarian:** never run — run agent-librarian to initialize"
    if librarian_file_hdr.exists():
        try:
            lr_date_hdr = librarian_file_hdr.read_text(encoding="utf-8").strip()
            lr_dt_hdr = datetime.strptime(lr_date_hdr, "%Y-%m-%d")
            days_ago_hdr = (datetime.now() - lr_dt_hdr).days
            if days_ago_hdr > 3:
                lib_hdr = "**Librarian:** " + lr_date_hdr + " (" + str(days_ago_hdr) + " days ago) — OVERDUE (cadence: 3d) — ask the user to run it"
            else:
                lib_hdr = "**Librarian:** " + lr_date_hdr + " (" + str(days_ago_hdr) + " days ago) — OK (cadence: 3d)"
        except (ValueError, OSError):
            lib_hdr = "**Librarian:** unknown"
    h.append(lib_hdr)
    # C2: Surface missing-brain count in header (visibility for every AI reading BRAIN)
    try:
        _missing_count = 0
        _missing_names = []
        for _d in [NEURONS_DIR]:
            if _d.exists():
                for _f in _d.glob("*.md"):
                    if _f.stat().st_size > BRAIN_THRESHOLD:
                        _txt = _f.read_text(encoding="utf-8", errors="replace")
                        _first5 = "\n".join(_txt.split("\n")[:5])
                        if "→brain:" not in _first5:
                            _missing_count += 1
                            _missing_names.append(_f.stem)
        if _missing_count > 0:
            _names_short = ", ".join(_missing_names[:3]) + (", ..." if _missing_count > 3 else "")
            h.append("**To-do:** " + str(_missing_count) + " neuron(s) need →brain: summary (" + _names_short + ") — run Librarian to generate")
    except (OSError, UnicodeDecodeError):
        pass
    h.append("")
    h.append("<!-- ⚠️ THIS FILE IS AUTO-GENERATED BY compile.py. DO NOT EDIT DIRECTLY. -->")
    h.append("<!-- Changes will be overwritten on next compilation. -->")
    h.append("<!-- To add/update information: write to VAULT/ and run compile.py. -->")
    h.append("")
    h.append("> **⚠️ DO NOT EDIT THIS FILE.** Auto-generated by compile.py.")
    h.append("> To update: modify files in VAULT/, then run compile.py.")
    h.append("")
    h.append("> **Reading mode:** If you're on a platform with unreliable tool calls (DeepSeek, etc.),")
    h.append("> read ONLY this file. The INDEX below tells you everything. Don't open VAULT files.")
    h.append("")
    in_laws = False
    for line in lines:
        if "## DESIGN PRINCIPLES" in line:
            in_laws = True
            h.append("## DESIGN PRINCIPLES")
            continue
        if in_laws:
            if line.startswith("---"):
                in_laws = False
                h.append("")
                continue
            h.append(line)
    h.append("## QUICK ROUTING")
    h.append("- READ -> LIBRARY/BRAIN.md (you are here). Compiled, read-optimized.")
    h.append("- WRITE -> VAULT/. Follow Writing Protocol in DARA.md.")
    h.append("- DETAIL -> Open specific VAULT/ file referenced below.")
    h.append("- LIBRARIAN -> VAULT/ENABLERS/agent-librarian.md")
    h.append("- ARCHITECT -> Only if the user activates. VAULT/ENABLERS/agent-architect.md")
    h.append("")
    h.append("## ENCODING KEY")
    enc1 = "Status: `[A]` active, `[C]` completed, `[P]` paused. "
    enc1 += "Relevance: `[H]` high, `[M]` medium, `[L]` low. "
    enc1 += "Combined: `[A/H]` = active + high relevance."
    h.append(enc1)
    enc2 = "Money: `€NNK` = thousands. People: `First.Last(role)`. "
    enc2 += "Refs: `→refs:` = linked files. Creds: `[CRED:name]` = see credentials entry. "
    enc2 += "Tags: `#tag`. Word count: `~NNNw`. Date: `YYYY-MM-DD`."
    h.append(enc2)
    h.append("")
    return "\n".join(h)

def build_index(entries):
    idx = ["## INDEX", ""]
    neurons = [e for e in entries if e["category"] == "NEURONS"]
    enablers = [e for e in entries if e["category"] == "ENABLERS"]
    if neurons:
        domains = {}
        for e in neurons:
            parts = e["filename"].split("-")
            prefix = parts[0]
            domains.setdefault(prefix, []).append(e["filename"])
        # Domain label mapping for the INDEX section.
        # Add your own filename prefixes here as you create neurons.
        # Example: if you have hot-website.md and hot-marketing.md,
        # add `"hot": "HOT Project"` so the INDEX groups them under one label.
        labels = {
            "profile": "Profile",
            "example": "Example",
            # Add your domains below. Format: "prefix": "Display Label"
        }
        seen = set()
        for prefix, fnames in sorted(domains.items()):
            lbl = labels.get(prefix, prefix.upper())
            if lbl in seen:
                continue
            seen.add(lbl)
            all_f = []
            for p, fn in domains.items():
                if labels.get(p, p.upper()) == lbl:
                    all_f.extend(fn)
            idx.append("**" + lbl + ":** " + ", ".join(sorted(set(all_f))))
    if enablers:
        idx.append("**ENABLERS:** " + ", ".join(e["filename"] for e in enablers))
    idx.append("")
    idx.append("---")
    idx.append("")
    return "\n".join(idx)

def auto_feedback(warns, stales):
    if not warns and not stales:
        return
    now = datetime.now().strftime("%Y-%m-%d")
    fname = "feedback-" + now + "-compiler-flags.md"
    fpath = INBOX_DIR / fname
    if fpath.exists():
        return
    fb = []
    fb.append("## FEEDBACK: Compiler detected issues")
    fb.append("**From:** compile.py v" + COMPILER_VERSION + " (automated)")
    fb.append("**Date:** " + now)
    fb.append("**Type:** INCONSISTENCY")
    sev = "CRITICAL" if any("missing [STATUS" in w for w in warns) else "IMPORTANT"
    fb.append("**Severity:** " + sev)
    fb.append("")
    fb.append("### What happened")
    fb.append("The compiler flagged " + str(len(warns)) + " warning(s) and " + str(len(stales)) + " stale flag(s) during compilation.")
    fb.append("")
    if warns:
        fb.append("### Warnings")
        for w in warns:
            fb.append("- " + w)
        fb.append("")
    if stales:
        fb.append("### Stale entries")
        for s in stales:
            fb.append("- " + s)
        fb.append("")
    fb.append("### Suggested fix")
    fb.append("Review each flagged entry in VAULT/ and update or mark as [C/L] if no longer active.")
    fpath.write_text("\n".join(fb), encoding="utf-8")
    log("  AUTO-FEEDBACK: Created " + fname)

_PREV_SIZES_FILE = DARA_ROOT / "SYSTEM" / ".prev_source_sizes.json"

def get_previous_sizes():
    """Read previous VAULT source sizes from .prev_source_sizes.json for accurate delta."""
    if not _PREV_SIZES_FILE.exists():
        return {}, 0
    try:
        data = json.loads(_PREV_SIZES_FILE.read_text(encoding="utf-8"))
        return data.get("sizes", {}), data.get("total", 0)
    except (json.JSONDecodeError, KeyError, OSError):
        return {}, 0

def save_current_sizes(entries):
    """Save current VAULT source sizes for next compilation's delta report."""
    sizes = {e["filename"]: e["chars"] for e in entries}
    total = sum(sizes.values())
    try:
        _PREV_SIZES_FILE.write_text(
            json.dumps({"sizes": sizes, "total": total}, indent=2),
            encoding="utf-8"
        )
    except OSError:
        log("  WARNING: Could not save source sizes for delta tracking")

def git_is_available():
    """Check if git is installed on this system."""
    try:
        r = subprocess.run(["git", "--version"], capture_output=True, timeout=5)
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def git_auto_init():
    """Initialize git repo if .git doesn't exist. Returns True if repo exists/created."""
    git_dir = DARA_ROOT / ".git"
    if git_dir.exists():
        return True
    try:
        r = subprocess.run(
            ["git", "init", "-b", "main"],
            cwd=str(DARA_ROOT), capture_output=True, text=True, timeout=10
        )
        if r.returncode == 0:
            # Set default identity for DARA commits
            subprocess.run(
                ["git", "config", "user.email", "dara@system.local"],
                cwd=str(DARA_ROOT), capture_output=True, timeout=5
            )
            subprocess.run(
                ["git", "config", "user.name", "DARA Compiler"],
                cwd=str(DARA_ROOT), capture_output=True, timeout=5
            )
            log("  GIT: Auto-initialized repository")
            return True
    except (subprocess.TimeoutExpired, OSError):
        pass
    return False

def git_auto_commit(active, archived, tokens):
    """Auto-commit after successful compilation."""
    # G.B: skip git in Cowork sandbox (FUSE lock semantics break HEAD lockfile)
    if _is_cowork_env():
        log("  GIT: Skipped (Cowork environment — local watcher will commit)")
        return
    if not git_is_available():
        log("  GIT: Not installed. Recommended: install Git for automatic version history.")
        return
    if not git_auto_init():
        log("  GIT: Could not initialize repository.")
        return
    # Clean stale index.lock if present (crash recovery)
    lock_file = DARA_ROOT / ".git" / "index.lock"
    if lock_file.exists():
        try:
            import time
            lock_age = time.time() - lock_file.stat().st_mtime
            if lock_age > 60:
                lock_file.unlink()
                log("  GIT: Removed stale index.lock (age: " + str(int(lock_age)) + "s)")
            else:
                log("  GIT: index.lock exists (age: " + str(int(lock_age)) + "s) — another git process may be running. Skipping commit.")
                return
        except OSError:
            log("  GIT: Could not remove index.lock — skipping commit.")
            return
    try:
        # Stage all changes
        subprocess.run(
            ["git", "add", "-A"],
            cwd=str(DARA_ROOT), capture_output=True, timeout=15
        )
        # Check if there are changes to commit
        r = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=str(DARA_ROOT), capture_output=True, timeout=10
        )
        if r.returncode == 0:
            log("  GIT: No changes to commit.")
            return
        # Commit with descriptive message
        msg = "DARA compile: " + str(active) + " active, " + str(archived) + " archived, ~" + "{:,}".format(tokens) + " tokens"
        r = subprocess.run(
            ["git", "commit", "-m", msg],
            cwd=str(DARA_ROOT), capture_output=True, text=True, timeout=15
        )
        if r.returncode == 0:
            # Extract short hash
            rh = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=str(DARA_ROOT), capture_output=True, text=True, timeout=5
            )
            sha = rh.stdout.strip() if rh.returncode == 0 else "?"
            log("  GIT: Committed [" + sha + "] " + msg)
        else:
            log("  GIT: Commit failed — " + r.stderr.strip()[:80])
    except (subprocess.TimeoutExpired, OSError) as e:
        log("  GIT: Error — " + str(e)[:80])

def compute_checksum(content):
    """Compute SHA256 checksum of content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

def acquire_compile_lock():
    """Try to acquire compile lock. Warns if another session is compiling."""
    import os, platform
    lock_info = {
        "pid": os.getpid(),
        "host": platform.node(),
        "started": datetime.now().isoformat(),
        "model": "unknown"  # can be set by caller
    }
    if COMPILE_LOCK_FILE.exists():
        try:
            prev = json.loads(COMPILE_LOCK_FILE.read_text(encoding="utf-8"))
            lock_time = datetime.fromisoformat(prev.get("started", "2000-01-01"))
            age_seconds = (datetime.now() - lock_time).total_seconds()
            if age_seconds < LOCK_STALE_SECONDS:
                log("  WARNING: Another compile is in progress (PID " + str(prev.get("pid", "?")) + ", started " + prev.get("started", "?") + ")")
                log("  WARNING: Proceeding anyway — but concurrent writes may cause conflicts")
            else:
                log("  INFO: Cleared stale compile lock (age: " + str(int(age_seconds)) + "s)")
        except (json.JSONDecodeError, OSError, ValueError):
            pass
    if not DRY_RUN:
        try:
            COMPILE_LOCK_FILE.write_text(json.dumps(lock_info, indent=2), encoding="utf-8")
        except OSError:
            pass

def _is_cowork_env():
    """Detect sandboxed environment (Cowork, FUSE mount) where git lockfile semantics fail."""
    p = str(DARA_ROOT)
    return "/sessions/" in p and "/mnt/" in p

def check_w3b_integrity():
    """F1.B: Detect Edit-tool truncation on W3(b) protected files.

    Compares each W3(b) file's current size against the stored baseline in
    SYSTEM/.w3b_sizes.json. Any size DROP triggers a CRITICAL alert pointing
    to the most recent BACKUP/SYSTEM/ copy for rollback.
    """
    W3B_SIZES_FILE = DARA_ROOT / "SYSTEM" / ".w3b_sizes.json"
    w3b_paths = [
        DARA_ROOT / "DARA.md",
        DARA_ROOT / "SYSTEM" / "compile.py",
        DARA_ROOT / "SYSTEM" / "validators.py",
        DARA_ROOT / "SYSTEM" / "watcher.py",
        DARA_ROOT / "VAULT" / "ENABLERS" / "agent-architect.md",
    ]
    current = {}
    for fp in w3b_paths:
        if fp.exists():
            current[fp.name] = fp.stat().st_size

    alerts_w3b = []
    previous = {}
    if W3B_SIZES_FILE.exists():
        try:
            previous = json.loads(W3B_SIZES_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            previous = {}
        for name, sz in current.items():
            prev_sz = previous.get(name)
            if prev_sz is not None and sz < prev_sz:
                drop = prev_sz - sz
                pct = (drop * 100) // prev_sz if prev_sz else 0
                if drop >= 50:
                    alerts_w3b.append(name + ": " + str(prev_sz) + " B -> " + str(sz) + " B (-" + str(drop) + " B, -" + str(pct) + "%) — POSSIBLE F1 TRUNCATION")

    if alerts_w3b:
        log("")
        log("  " + WARNING + " CRITICAL: W3(b) integrity check FAILED:")
        for a in alerts_w3b:
            log("    " + a)
        log("  Action: roll back from VAULT/BACKUP/SYSTEM/ (most recent timestamp before drop). See DARA.md W12.")
        return alerts_w3b

    try:
        W3B_SIZES_FILE.parent.mkdir(parents=True, exist_ok=True)
        W3B_SIZES_FILE.write_text(json.dumps(current, indent=2, sort_keys=True), encoding="utf-8")
    except OSError:
        pass
    return []

def release_compile_lock():
    """Release compile lock."""
    if COMPILE_LOCK_FILE.exists() and not DRY_RUN:
        try:
            COMPILE_LOCK_FILE.unlink()
        except OSError:
            pass

def strip_noise(text):
    """Strip sensitive/noisy patterns from neuron content for BRAIN output.
    Preserves content inside backtick blocks (inline `code` and ```fenced```)."""
    # Split into code and non-code segments
    parts = re.split(r'(```[\s\S]*?```|`[^`]+`)', text)
    result = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            # Inside backticks — preserve as-is
            result.append(part)
        else:
            # Outside backticks — apply noise stripping
            part = re.sub(r'\b[A-Z]{2}\d{2}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{0,4}\b', '[IBAN on file]', part)
            part = re.sub(r'\b[0-9XYZ]\d{7}[A-Z]\b', '[NIF on file]', part)
            part = re.sub(r'\b[ABCDEFGHJNPQRSUVW]\d{7}[0-9A-J]\b', '[CIF on file]', part)
            part = re.sub(r'[A-Z]:\\(?:Users|Program)[^\s\n\)\]]*', '[path on file]', part)
            part = re.sub(r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b', '[UUID on file]', part, flags=re.IGNORECASE)
            part = re.sub(r'\b[0-9a-f]{40,}\b', '[ID on file]', part)
            part = re.sub(r'ntn_[A-Za-z0-9_-]{30,}', '[token on file]', part)
            part = re.sub(r'pat[A-Za-z0-9_]{20,}', '[token on file]', part)
            part = re.sub(r'tvly-[A-Za-z0-9_-]+', '[token on file]', part)
            part = re.sub(r'sk-[A-Za-z0-9]{40,}', '[token on file]', part)
            part = re.sub(r'xoxb-[0-9]+-[0-9]+-[A-Za-z0-9]+', '[token on file]', part)
            part = re.sub(r'xkeysib-[A-Za-z0-9]{40,}', '[token on file]', part)
            part = re.sub(r're_[A-Za-z0-9]{20,}', '[token on file]', part)
            part = re.sub(r'gh[pousr]_[A-Za-z0-9]{30,}', '[token on file]', part)
            part = re.sub(r'sk_live_[A-Za-z0-9]{20,}', '[token on file]', part)
            part = re.sub(r'pk_live_[A-Za-z0-9]{20,}', '[token on file]', part)
            part = re.sub(r'rk_live_[A-Za-z0-9]{20,}', '[token on file]', part)
            part = re.sub(r'AKIA[0-9A-Z]{16}', '[token on file]', part)
            part = re.sub(r'AC[a-f0-9]{32}', '[token on file]', part)
            part = re.sub(r'[a-f0-9]{32}-us\d{1,2}', '[token on file]', part)
            result.append(part)
    return ''.join(result)

def render_enabler_oneliner(entry):
    """Render an enabler as a compact one-liner for BRAIN.md."""
    fn = entry["filename"]
    raw = entry["content"]
    detail = WARNING + " summary only " + ARROW + " open file to activate agent\n" + ARROW + "detail: VAULT/" + entry["category"] + "/" + fn + ".md"

    # Priority 1: explicit summary: line (W14)
    first_line = raw.split("\n")[0].strip()
    if first_line.startswith("summary:"):
        desc = first_line[len("summary:"):].strip()
        return "### " + fn + " | " + desc + "\n" + detail

    # Priority 2: auto-detect from content (fallback — W14 warning)
    log("  WARNING: " + fn + " has no summary: line (W14) — using auto-detection (less accurate)")
    lines = raw.split("\n")
    desc = ""
    trigger = ""
    for l in lines[:15]:
        ll = l.lower().strip()
        if not desc:
            if l.startswith("# "):
                desc = l.lstrip("#").strip()
            elif "role" in ll or "purpose" in ll or "description" in ll:
                if ":" in l:
                    desc = l.split(":", 1)[-1].strip().strip("*").strip()[:120]
        if not trigger:
            if "trigger" in ll or "activaci" in ll.replace("\u00f3", "o"):
                if ":" in l:
                    tval = l.split(":", 1)[-1].strip().strip("*").strip()[:80]
                    trigger = " | Trigger: " + tval
    if not desc:
        desc = fn
    # Word-boundary truncation (#4 fix)
    if len(desc) > 120:
        desc = desc[:120].rsplit(' ', 1)[0] + "..."
    return "### " + fn + " | " + desc + trigger + "\n" + detail

def quick_stats():
    """--stats: Print system health without compiling."""
    log("DARA Quick Stats")
    log("=" * 50)
    neurons = list(NEURONS_DIR.glob("*.md")) if NEURONS_DIR.exists() else []
    neurons = [f for f in neurons if f.name != "changelog.md"]
    enablers = list(ENABLERS_DIR.glob("*.md")) if ENABLERS_DIR.exists() else []
    inbox = list(INBOX_DIR.glob("*.md")) if INBOX_DIR.exists() else []
    inbox = [f for f in inbox if f.name != "README.md"]

    # Count active vs archived
    active_n = 0
    archived_n = 0
    for f in neurons:
        text = f.read_text(encoding="utf-8")
        first_line = text.split("\n")[0] if text else ""
        if "[C/L]" in first_line:
            archived_n += 1
        else:
            active_n += 1
    active_e = 0
    archived_e = 0
    for f in enablers:
        text = f.read_text(encoding="utf-8")
        first_line = text.split("\n")[0] if text else ""
        if "[C/L]" in first_line:
            archived_e += 1
        else:
            active_e += 1

    total_active = active_n + active_e
    total_archived = archived_n + archived_e

    # Token estimate from BRAIN.md
    brain_tokens = 0
    brain_date = "never"
    if BRAIN_FILE.exists():
        brain_text = BRAIN_FILE.read_text(encoding="utf-8")
        brain_tokens = len(brain_text) // 4
        m = re.search(r'\*\*Compiled:\*\* (\d{4}-\d{2}-\d{2} \d{2}:\d{2})', brain_text)
        if m:
            brain_date = m.group(1)

    # Librarian last run
    librarian_file = VAULT_DIR / ".librarian-last-run"
    lib_status = "never"
    if librarian_file.exists():
        try:
            lr_date = librarian_file.read_text(encoding="utf-8").strip()
            lr_dt = datetime.strptime(lr_date, "%Y-%m-%d")
            days_ago = (datetime.now() - lr_dt).days
            lib_status = lr_date + " (" + str(days_ago) + " days ago)"
            if days_ago > 3:
                lib_status += " ** OVERDUE **"
        except (ValueError, OSError):
            lib_status = "unknown"

    log("")
    log("  NEURONS:    " + str(active_n) + " active, " + str(archived_n) + " archived")
    log("  ENABLERS:   " + str(active_e) + " active, " + str(archived_e) + " archived")
    log("  TOTAL:      " + str(total_active) + " active, " + str(total_archived) + " archived")
    log("  BRAIN.md:   ~" + "{:,}".format(brain_tokens) + " tokens")
    log("  Compiled:   " + brain_date)
    log("  Librarian:  " + lib_status)
    log("  INBOX:      " + str(len(inbox)) + " pending")
    if inbox:
        for i in inbox:
            log("    - " + i.name)

    # Archived entries approaching purge
    purge_candidates = []
    for f in neurons + enablers:
        text = f.read_text(encoding="utf-8")
        first_line = text.split("\n")[0] if text else ""
        if "[C/L]" not in first_line:
            continue
        d = get_entry_date(text)
        if d:
            age = (datetime.now() - d).days
            remaining = ARCHIVE_PURGE_DAYS - age
            if remaining <= 10:
                purge_candidates.append((f.stem, age, remaining))
    if purge_candidates:
        log("")
        log("  PURGE UPCOMING:")
        for name, age, remaining in sorted(purge_candidates, key=lambda x: x[2]):
            if remaining <= 0:
                log("    " + name + ": " + str(age) + " days old - WILL BE PURGED on next compile")
            else:
                log("    " + name + ": " + str(age) + " days old - purge in " + str(remaining) + " days")

    log("")
    log("=" * 50)

def purge_archived(neurons, enablers):
    """N8: Auto-delete [C/L] entries older than ARCHIVE_PURGE_DAYS."""
    purged = []
    kept_neurons = []
    kept_enablers = []

    for e in neurons:
        first_line_e = e["content"].split("\n")[0] if e["content"] else ""
        if "[C/L]" not in first_line_e:
            kept_neurons.append(e)
            continue
        d = get_entry_date(e["content"])
        if d:
            age = (datetime.now() - d).days
            if age > ARCHIVE_PURGE_DAYS:
                if not DRY_RUN:
                    try:
                        shutil.move(str(e["filepath"]), str(TRASH_DIR / e["filepath"].name))  # soft-delete to TRASH
                    except OSError:
                        kept_neurons.append(e)
                        continue
                purged.append((e["filename"], age))
                continue
        kept_neurons.append(e)

    for e in enablers:
        first_line_e = e["content"].split("\n")[0] if e["content"] else ""
        if "[C/L]" not in first_line_e:
            kept_enablers.append(e)
            continue
        d = get_entry_date(e["content"])
        if d:
            age = (datetime.now() - d).days
            if age > ARCHIVE_PURGE_DAYS:
                if not DRY_RUN:
                    try:
                        shutil.move(str(e["filepath"]), str(TRASH_DIR / e["filepath"].name))  # soft-delete to TRASH
                    except OSError:
                        kept_enablers.append(e)
                        continue
                purged.append((e["filename"], age))
                continue
        kept_enablers.append(e)

    return kept_neurons, kept_enablers, purged

def write_health_json(active_n, active_e, archived_count, brain_tokens, warns_count, inbox_count, backups_count, missing_brain_count, source_tokens=0):
    """Generate SYSTEM/health.json with compilation metrics."""
    librarian_file = VAULT_DIR / ".librarian-last-run"
    lib_days = -1
    if librarian_file.exists():
        try:
            lr_date = librarian_file.read_text(encoding="utf-8").strip()
            from datetime import datetime as dt2
            lr_dt = dt2.strptime(lr_date, "%Y-%m-%d")
            lib_days = (datetime.now() - lr_dt).days
        except (ValueError, OSError):
            pass

    # Read previous health for comparison
    prev_health = None
    if HEALTH_FILE.exists():
        try:
            prev_health = json.loads(HEALTH_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    health = {
        "lastCompile": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "activeNeurons": active_n,
        "activeEnablers": active_e,
        "archived": archived_count,
        "sourceTokens": source_tokens if source_tokens else active_n * 250 + active_e * 150,
        "brainTokens": brain_tokens,
        "warnings": warns_count,
        "inboxPending": inbox_count,
        "backupCount": backups_count,
        "missingBrainSummaries": missing_brain_count,
        "lastLibrarianDays": lib_days,
    }

    # Alerts based on thresholds
    alerts = []
    if prev_health:
        if warns_count > prev_health.get("warnings", 0):
            alerts.append("warnings increased: " + str(prev_health.get("warnings", 0)) + " " + ARROW + " " + str(warns_count))
        if backups_count > int(MAX_BACKUPS * 0.85):
            alerts.append("backup count high: " + str(backups_count))
    if inbox_count > 0:
        alerts.append(str(inbox_count) + " inbox item(s) pending")
    if lib_days > 3:
        alerts.append("librarian overdue: " + str(lib_days) + " days (cadence: 3d)")
    # Anti-tampering: if librarian-last-run says "today" (lib_days=0) but no [Librarian]
    # entry in changelog today, the timestamp may have been touched by a non-Librarian process.
    if lib_days == 0:
        changelog_path = VAULT_DIR / "changelog.md"
        today_str = datetime.now().strftime("%Y-%m-%d")
        if changelog_path.exists():
            try:
                cl = changelog_path.read_text(encoding="utf-8")
                lines_cl = cl.split("\n")
                librarian_today = False
                in_today_section = False
                for line in lines_cl:
                    if line.startswith("## " + today_str):
                        in_today_section = True
                    elif line.startswith("## 20") and not line.startswith("## " + today_str):
                        in_today_section = False
                    if in_today_section and "[Librarian]" in line:
                        librarian_today = True
                        break
                if not librarian_today and "[Librarian]" in cl:
                    tail = "\n".join(lines_cl[-50:])
                    if "[Librarian]" in tail and today_str in tail:
                        librarian_today = True
                if not librarian_today:
                    alerts.append("librarian timestamp SUSPICIOUS: .librarian-last-run says today but no [Librarian] entry in today's changelog — may have been touched by non-Librarian process")
            except (OSError, UnicodeDecodeError):
                pass
    if missing_brain_count > 0:
        alerts.append(str(missing_brain_count) + " large neurons without " + ARROW + "brain: summary")

    health["alerts"] = alerts

    HEALTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        HEALTH_FILE.write_text(json.dumps(health, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError:
        log("  WARNING: Could not write health.json")
    if alerts:
        log("  Health alerts: " + "; ".join(alerts))
    else:
        log("  Health: all clear")

def compile_brain():
    if STATS_ONLY:
        quick_stats()
        return

    mode = " [DRY RUN]" if DRY_RUN else ""
    log("DARA Compiler v" + COMPILER_VERSION + mode)
    log("=" * 50)
    ensure_dirs()

    # Acquire compile lock (concurrent session detection)
    acquire_compile_lock()

    # Pre-compile: detect truncated VAULT files (>20% shrink vs git)
    trunc_warns = check_size_regression(NEURONS_DIR, ENABLERS_DIR, DARA_ROOT)
    for tw in trunc_warns:
        log("  *** TRUNCATION WARNING: " + tw + " ***")

    # W3(b) protected files check
    w3b_warns = check_protected_files(PROTECTED_FILES, DARA_ROOT, PROTECTED_CHECKSUMS_FILE, DRY_RUN)
    for w in w3b_warns:
        log("  *** " + w + " ***")

    # Tamper detection
    tampered, tamper_reason = check_brain_tamper(BRAIN_FILE, "DARA_CHECKSUM")
    if tamper_reason == "no_checksum":
        log("  WARNING: BRAIN.md has no DARA_CHECKSUM — tamper detection disabled. Will auto-add on next compile.")
    if tampered:
        log("")
        log("  *** TAMPER DETECTED: BRAIN.md was manually edited! ***")
        log("  *** This file is auto-generated. Manual edits will be overwritten. ***")

    log("")
    # F1.B: W3(b) integrity check (detect Edit-tool truncation pre-flight)
    w3b_alerts = check_w3b_integrity()

    log("[1/10] Backing up...")
    if DRY_RUN or VALIDATE_ONLY:
        log("  [SKIPPED] " + ("DRY RUN" if DRY_RUN else "VALIDATE-ONLY") + " — no backup needed")
    elif not backup_previous_brain():
        log("  No previous BRAIN.md")

    log("[2/10] Pruning backups...")
    if DRY_RUN or VALIDATE_ONLY:
        log("  [SKIPPED] " + ("DRY RUN" if DRY_RUN else "VALIDATE-ONLY") + " — no prune needed")
    else:
        prune_backups()
    log("[3/10] Reading VAULT...")
    neurons = read_vault_files(NEURONS_DIR, "NEURONS")
    enablers = read_vault_files(ENABLERS_DIR, "ENABLERS")
    log("  " + str(len(neurons)) + " NEURONS, " + str(len(enablers)) + " ENABLERS")

    if not neurons and not enablers:
        log("  ERROR: No files in VAULT/. Aborting.")
        sys.exit(1)

    log("[4/10] Auto-purge archived entries...")
    neurons, enablers, purged = purge_archived(neurons, enablers)
    if purged:
        for name, age in purged:
            action = "WOULD PURGE" if DRY_RUN else "PURGED"
            log("  " + action + ": " + name + ".md (archived " + str(age) + " days ago)")
    else:
        log("  No entries to purge")

    log("[5/10] Dedup...")
    neurons, enablers, dd_fixes = dedup(neurons, enablers)
    for f in dd_fixes:
        log("  FIXED: " + f)
    if not dd_fixes:
        log("  No duplicates")
    # Content similarity check (Jaccard)
    sim_warns = content_similarity_check(neurons)
    for sw in sim_warns:
        log("  SIMILARITY: " + sw)

    all_entries = neurons + enablers
    valid = get_all_filenames(neurons, enablers)
    vcreds = get_cred_names(enablers)

    log("[6/10] Validate + auto-fix...")
    fixes = list(dd_fixes)
    warns = []
    stales = []

    for entry in all_entries:
        c = entry["content"]
        fn = entry["filename"]
        fp = entry["filepath"]
        is_exec = c.startswith("# AGENT")

        if not is_exec:
            c2, rf = fix_refs(c, valid, fn)
            if rf:
                entry["content"] = c2
                entry["chars"] = len(c2)
                fixes.extend(rf)

            c3, hf = fix_header(entry["content"], fn, fp, DRY_RUN)
            if hf:
                entry["content"] = c3
                entry["chars"] = len(c3)
                fixes.extend(hf)

            # Auto-fix ASCII arrows (->refs: etc)
            c4, af = fix_ascii_arrows(entry["content"], fn, fp, DRY_RUN)
            if af:
                entry["content"] = c4
                entry["chars"] = len(c4)
                fixes.extend(af)

            warns.extend(check_creds(entry["content"], vcreds, fn))
            stales.extend(check_stale(entry["content"], fn, STALENESS_DAYS))

            has_refs = (ARROW + "refs:") in entry["content"]
            has_tags = (ARROW + "tags:") in entry["content"]
            if not has_refs and not has_tags:
                warns.append(fn + ": missing refs/tags")

            if entry["category"] == "NEURONS":
                if "[A/" not in c and "[C/" not in c and "[P/" not in c:
                    warns.append(fn + ": missing [STATUS/RELEVANCE]")

    # NEW v2.8 validations
    # W8: kebab-case naming (WARNING)
    kebab_warns = check_kebab_case(all_entries)
    warns.extend(kebab_warns)

    # W8: agents misplaced in NEURONS (WARNING)
    misplaced_warns = check_misplaced_agents(neurons)
    warns.extend(misplaced_warns)

    # Orphan files in VAULT/ root (WARNING)
    orphan_warns = check_orphan_files(VAULT_DIR)
    warns.extend(orphan_warns)

    # W7: changelog format (WARNING)
    cl_warns = check_changelog_format(VAULT_DIR)
    warns.extend(cl_warns)

    # Monetary format (INFO — for agent review, not a hard warning)
    money_infos = check_monetary_format(all_entries)

    # Token budget check — raw VAULT chars (pre-compression estimate)
    # Note: actual BRAIN.md is much smaller due to →brain: compression
    # Thresholds are set high to account for compression ratio (~7:1 typical)
    budget_tc = sum(e["chars"] for e in all_entries if "[C/L]" not in (e["content"].split("\n")[0] if e["content"] else ""))
    budget_tokens = budget_tc // 4
    if budget_tokens >= 150000:
        warns.append("BRAIN.md TOKEN BUDGET CRITICAL: ~" + "{:,}".format(budget_tokens) + " raw tokens. Librarian should urgently archive/compress old entries.")
    elif budget_tokens >= 100000:
        warns.append("BRAIN.md TOKEN BUDGET WARNING: ~" + "{:,}".format(budget_tokens) + " raw tokens. Librarian should prioritize compression and archival.")
    elif budget_tokens >= 50000:
        money_infos.append("BRAIN.md approaching budget (~" + "{:,}".format(budget_tokens) + " raw tokens). Review compression opportunities.")

    for f in fixes[len(dd_fixes):]:
        log("  FIXED: " + f)
    for w in warns:
        log("  WARNING: " + w)
    for s in stales:
        log("  STALE: " + s)
    for info in money_infos:
        log("  INFO: " + info)
    if not fixes and not warns and not stales and not money_infos:
        log("  All clean.")

    log("[7/10] Checking INBOX...")
    inbox = list(INBOX_DIR.glob("*.md")) if INBOX_DIR.exists() else []
    inbox = [f for f in inbox if f.name != "README.md"]
    # Auto-cleanup: remove auto-generated feedback older than 30 days
    cleaned_fb = 0
    remaining_inbox = []
    for fb_file in inbox:
        if "compiler-flags" in fb_file.name:  # auto-generated files only
            m_date = re.match(r'feedback-(\d{4}-\d{2}-\d{2})', fb_file.name)
            if m_date:
                try:
                    fb_date = datetime.strptime(m_date.group(1), "%Y-%m-%d")
                    age = (datetime.now() - fb_date).days
                    if age > 30 and not DRY_RUN:
                        fb_file.unlink()
                        cleaned_fb += 1
                        continue
                except (ValueError, OSError):
                    pass
        remaining_inbox.append(fb_file)
    if cleaned_fb:
        log("  Cleaned " + str(cleaned_fb) + " stale auto-feedback file(s) (>30 days old)")
    inbox = remaining_inbox
    inbox_overdue_days = 0
    inbox_overdue_count = 0
    if inbox:
        log("  " + str(len(inbox)) + " feedback item(s) pending:")
        for i in inbox:
            log("    - " + i.name)
            # Check age from filename: feedback-YYYY-MM-DD-topic.md
            m_date = re.match(r'feedback-(\d{4}-\d{2}-\d{2})', i.name)
            if m_date:
                try:
                    fb_date = datetime.strptime(m_date.group(1), "%Y-%m-%d")
                    age = (datetime.now() - fb_date).days
                    if age > 10:
                        inbox_overdue_count += 1
                        inbox_overdue_days = max(inbox_overdue_days, age)
                except ValueError:
                    pass
        if inbox_overdue_count > 0:
            log("  ⚠️ INBOX OVERDUE: " + str(inbox_overdue_count) + " item(s) older than 10 days (oldest: " + str(inbox_overdue_days) + " days)")
    else:
        log("  INBOX empty")

    # Get previous sizes for delta reporting
    prev_sizes, prev_total = get_previous_sizes()

    # Separate active vs archived entries
    def is_archived(entry):
        first_line = entry["content"].split("\n")[0] if entry["content"] else ""
        return "[C/L]" in first_line

    active_neurons = [e for e in neurons if not is_archived(e)]
    archived_neurons = [e for e in neurons if is_archived(e)]
    active_enablers = [e for e in enablers if not is_archived(e)]
    archived_enablers = [e for e in enablers if is_archived(e)]
    archived_all = archived_neurons + archived_enablers

    if VALIDATE_ONLY:
        log("")
        log("Validation complete. No compilation performed.")
        return

    log("[8/10] Compiling BRAIN.md...")
    out = []
    out.append(extract_header())
    out.append(build_index(active_neurons + active_enablers))

    out.append("## NEURONS\n")
    for entry in active_neurons:
        c = entry["content"]
        # Layer 3 forward-compat: if Librarian added a →brain: summary, use it
        brain_line = None
        for bl in c.split("\n"):
            if bl.startswith("→brain:"):
                brain_line = bl[len("→brain:"):].strip()
                break
        if brain_line:
            # Extract [STATUS/RELEVANCE] from the ## header line
            status_match = re.search(r'\[([ACP]/[HML])\]', c)
            status = " " + status_match.group(0) if status_match else ""
            out.append("### " + entry["filename"] + status + " | " + strip_noise(brain_line))
            out.append("→detail: VAULT/" + entry["category"] + "/" + entry["filename"] + ".md")
        else:
            out.append(strip_noise(c))
        out.append("\n---\n")

    out.append("## ENABLERS\n")
    for entry in active_enablers:
        out.append(render_enabler_oneliner(entry))

    # Archived section — minimal, just names
    if archived_all:
        out.append("## ARCHIVE (closed/low relevance)\n")
        out.append("These entries exist in VAULT but are no longer active. Open the VAULT file if you need historical detail.\n")
        for entry in archived_all:
            first_line = entry["content"].split("\n")[0] if entry["content"] else ""
            out.append("- " + first_line.lstrip("# ").strip())
        out.append("\n---\n")

    tc = sum(e["chars"] for e in active_neurons + active_enablers)
    et = tc // 4
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    # Check for large neurons missing →brain: summaries
    missing_brain = []
    for entry in active_neurons:
        c = entry["content"]
        has_brain = any(bl.startswith("→brain:") for bl in c.split("\n"))
        if not has_brain and entry["chars"] > BRAIN_THRESHOLD:
            missing_brain.append(entry["filename"])
    
    out.append("## COMPILATION STATS")
    out.append("- **Compiled:** " + now)
    out.append("- **Compiler:** v" + COMPILER_VERSION)
    out.append("- **Active NEURONS:** " + str(len(active_neurons)))
    out.append("- **Active ENABLERS:** " + str(len(active_enablers)))
    out.append("- **Archived:** " + str(len(archived_all)))
    out.append("- **Total entries:** " + str(len(all_entries)))
    out.append("- **Source chars (active):** " + "{:,}".format(tc))
    out.append("- **Est. tokens (active):** ~" + "{:,}".format(et))
    out.append("- **Auto-fixes:** " + str(len(fixes)))
    out.append("- **Warnings:** " + str(len(warns)))
    out.append("- **Stale flags:** " + str(len(stales)))
    out.append("- **INBOX:** " + str(len(inbox)) + " pending")
    if inbox_overdue_count > 0:
        out.append("")
        out.append("> **📬 INBOX OVERDUE:** " + str(inbox_overdue_count) + " feedback item(s) unprocessed for " + str(inbox_overdue_days) + "+ days. The Librarian should triage first (resolve simple items). If structural issues remain, ask the user: \"There are unresolved INBOX items that need the Architect. Want me to activate it?\"")

    # Librarian self-trigger: read last run date
    librarian_file = VAULT_DIR / ".librarian-last-run"
    if librarian_file.exists():
        try:
            lr_date = librarian_file.read_text(encoding="utf-8").strip()
            from datetime import datetime as dt2
            lr_dt = dt2.strptime(lr_date, "%Y-%m-%d")
            days_ago = (datetime.now() - lr_dt).days
            out.append("- **Last Librarian:** " + lr_date + " (" + str(days_ago) + " days ago)")
            if days_ago > 3:
                out.append("")
                out.append("> **🔍 LIBRARIAN OVERDUE:** Last health check was " + str(days_ago) + " days ago (cadence: every 3 days). Ask the user: \"Your VAULT hasn't been reviewed in " + str(days_ago) + " days. Want me to run a health check?\"")
        except (ValueError, OSError):
            out.append("- **Last Librarian:** unknown")
    else:
        out.append("- **Last Librarian:** never")
        out.append("")
        out.append("> **🔍 LIBRARIAN NEEDED:** No health check has ever been run. Ask the user: \"Your VAULT has never been reviewed. Want me to run a health check?\"")

    out.append("")
    if missing_brain:
        out.append("- **→brain: MISSING:** " + str(len(missing_brain)) + " neurons >1500 chars without summary: " + ", ".join(missing_brain))
        out.append("  **Action: run the Librarian** to generate compressed summaries.")
        # C1: auto-write INBOX feedback (once per day max — don't spam)
        today_fb = INBOX_DIR / ("feedback-" + datetime.now().strftime("%Y-%m-%d") + "-missing-brain.md")
        if not today_fb.exists():
            try:
                fb_content = "## FEEDBACK: Missing →brain: summaries\n"
                fb_content += "**From:** compile.py v" + COMPILER_VERSION + " (automated)\n"
                fb_content += "**Date:** " + datetime.now().strftime("%Y-%m-%d") + "\n"
                fb_content += "**Type:** OPTIMIZATION OPPORTUNITY\n"
                fb_content += "**Severity:** IMPORTANT (inflates BRAIN.md tokens)\n\n"
                fb_content += "### What happened\n"
                fb_content += str(len(missing_brain)) + " active neurons >1500 chars lack a →brain: summary line. "
                fb_content += "Without it, the compiler embeds the full content in BRAIN.md instead of a one-line summary, wasting tokens.\n\n"
                fb_content += "### Affected neurons\n"
                for n in missing_brain:
                    fb_content += "- " + n + "\n"
                fb_content += "\n### Action for next AI / Librarian\n"
                fb_content += "1. Read each affected neuron.\n"
                fb_content += "2. Generate a →brain: one-liner capturing what/status/key-fact (≤150 chars). See agent-librarian.md Phase 4.\n"
                fb_content += "3. Insert as line 2 of the neuron (right after the `## name [STATUS]` header).\n"
                fb_content += "4. Compile to verify and delete this feedback file.\n"
                today_fb.write_text(fb_content, encoding="utf-8")
                log("  C1: auto-feedback written -> " + today_fb.name)
            except OSError:
                pass
    
    out.append("## FEEDBACK")
    out.append("If you noticed inconsistencies, stale data, or have suggestions while reading this file:")
    out.append("Drop a feedback file in VAULT/INBOX/ (format: feedback-YYYY-MM-DD-topic.md). The Architect reviews periodically.")

    brain = "\n".join(out)

    # Add checksum to brain content
    checksum = compute_checksum(brain)
    brain_protected = brain + "\n<!-- DARA_CHECKSUM:" + checksum + " -->\n"

    # Write BRAIN.md
    if DRY_RUN:
        log("  [DRY RUN] Would write BRAIN.md (" + "{:,}".format(len(brain_protected)) + " chars)")
    else:
        BRAIN_FILE.write_text(brain_protected, encoding="utf-8")
        auto_feedback(warns, stales)

    bt = len(brain) // 4
    # V12: Generate health.json
    if not DRY_RUN:
        bk_count = len(list(BACKUP_DIR.glob("brain_*.md")))
        write_health_json(
            len(active_neurons), len(active_enablers), len(archived_all),
            bt, len(warns), len(inbox), bk_count, len(missing_brain),
            source_tokens=et
        )

    log("")
    log("=" * 50)
    compiled_msg = "BRAIN.md compiled!" if not DRY_RUN else "BRAIN.md would be compiled (DRY RUN - no files written)"
    log(compiled_msg)
    log("  Entries: " + str(len(all_entries)) + " (" + str(len(active_neurons + active_enablers)) + " active, " + str(len(archived_all)) + " archived)")
    log("  Size: " + "{:,}".format(len(brain)) + " chars (~" + "{:,}".format(bt) + " tokens)")
    log("  Fixes: " + str(len(fixes)))
    log("  Warnings: " + str(len(warns)))
    log("  Stale: " + str(len(stales)))

    # Delta reporting
    log("")
    log("[9/10] Delta report...")
    if not prev_sizes:
        log("  No previous compilation to compare.")
    else:
        current_sizes = {}
        for e in all_entries:
            current_sizes[e["filename"]] = e["chars"]
        current_total = sum(current_sizes.values())
        delta_total = current_total - prev_total
        pct = (delta_total / prev_total * 100) if prev_total else 0
        sign = "+" if delta_total >= 0 else ""
        log("  Total: " + sign + "{:,}".format(delta_total) + " chars (" + sign + "{:.1f}".format(pct) + "% vs previous)")
        # Per-entry deltas — show significant growers and shrinkers
        growers = []
        shrinkers = []
        new_entries = []
        for name, cur in current_sizes.items():
            if name in prev_sizes:
                prev = prev_sizes[name]
                if prev > 0:
                    d = cur - prev
                    dp = d / prev * 100
                    if dp >= 20 and d > 200:
                        growers.append((name, d, dp))
                    elif dp <= -20 and abs(d) > 200:
                        shrinkers.append((name, d, dp))
            else:
                if cur > 100:
                    new_entries.append((name, cur))
        if growers:
            growers.sort(key=lambda x: -x[1])
            log("  Growers (>20%):")
            for name, d, dp in growers:
                log("    " + name + ": +" + "{:,}".format(d) + " chars (+" + "{:.0f}".format(dp) + "%)")
        if shrinkers:
            shrinkers.sort(key=lambda x: x[1])
            log("  Shrinkers (>20%):")
            for name, d, dp in shrinkers:
                log("    " + name + ": " + "{:,}".format(d) + " chars (" + "{:.0f}".format(dp) + "%)")
        if new_entries:
            log("  New entries:")
            for name, c in new_entries:
                log("    " + name + ": " + "{:,}".format(c) + " chars")
        if not growers and not shrinkers and not new_entries:
            log("  No significant changes.")

    # Save source sizes for next delta
    if not DRY_RUN:
        save_current_sizes(all_entries)

    # Git auto-commit
    log("")
    log("[10/10] Git auto-commit...")
    if DRY_RUN:
        log("  [DRY RUN] Skipping git commit")
    else:
        n_active = len(active_neurons + active_enablers)
        n_archived = len(archived_all)
        if not NO_GIT:
            git_auto_commit(n_active, n_archived, bt)
        else:
            log("  Skipped (--no-git)")

    # Release compile lock
    release_compile_lock()

    log("")
    log("Done.")

if __name__ == "__main__":
    compile_brain()
