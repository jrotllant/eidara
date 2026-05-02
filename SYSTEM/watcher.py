#!/usr/bin/env python3
"""
DARA Watcher v1.1
Monitors VAULT/ for file changes and auto-runs compile.py.

Usage:
    python watcher.py              # Poll every 5 seconds (default)
    python watcher.py --interval 10  # Poll every 10 seconds
    python watcher.py --once         # Check once and exit (for cron/scheduler)

No external dependencies — stdlib only.
"""

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────
SYSTEM_DIR = Path(__file__).resolve().parent
DARA_ROOT = SYSTEM_DIR.parent
VAULT_DIR = DARA_ROOT / "VAULT"
COMPILE_PY = SYSTEM_DIR / "compile.py"
NEURONS_DIR = DARA_ROOT / "VAULT" / "NEURONS"
ENABLERS_DIR = DARA_ROOT / "VAULT" / "ENABLERS"
CHANGELOG = DARA_ROOT / "VAULT" / "changelog.md"
LIBRARY_DIR = DARA_ROOT / "LIBRARY"
BRAIN_FILE = LIBRARY_DIR / "BRAIN.md"
COMPILE_ERROR_FILE = SYSTEM_DIR / ".compile-error"

# ── Configuration ──────────────────────────────────────────────
DEBOUNCE_SECONDS = 3       # Wait this long after last change before compiling
WATCH_EXTENSIONS = {".md"}  # Only watch these file types
IGNORE_FILES = {"changelog.md", ".librarian-last-run"}  # Don't trigger on these


def get_vault_snapshot():
    """Get dict of {filepath: mtime} for all watched files in VAULT/ + monitored system files."""
    snapshot = {}
    for folder in [NEURONS_DIR, ENABLERS_DIR]:
        if not folder.exists():
            continue
        for f in folder.iterdir():
            if f.suffix in WATCH_EXTENSIONS and f.name not in IGNORE_FILES:
                try:
                    snapshot[str(f)] = f.stat().st_mtime
                except OSError:
                    pass
    # Monitor LIBRARY/BRAIN.md and SYSTEM/ protected files for external tampering
    for monitored in [BRAIN_FILE, COMPILE_PY, SYSTEM_DIR / "watcher.py"]:
        if monitored.exists():
            try:
                snapshot["__monitor__" + str(monitored)] = monitored.stat().st_mtime
            except OSError:
                pass
    return snapshot


def diff_snapshots(old, new):
    """Compare two snapshots. Return list of changes."""
    changes = []
    for path, mtime in new.items():
        if path not in old:
            changes.append(("ADDED", Path(path).name))
        elif old[path] != mtime:
            changes.append(("MODIFIED", Path(path).name))
    for path in old:
        if path not in new:
            changes.append(("DELETED", Path(path).name))
    return changes


def run_compile():
    """Run compile.py and return success status."""
    try:
        result = subprocess.run(
            [sys.executable, str(COMPILE_PY)],
            cwd=str(DARA_ROOT),
            capture_output=True,
            text=True,
            timeout=60
        )
        # Extract key stats from output
        for line in result.stdout.split("\n"):
            if any(k in line for k in ["Entries:", "Size:", "Warnings:", "GIT:"]):
                log("  " + line.strip())
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        log("  ERROR: compile.py timed out after 60s")
        return False
    except Exception as e:
        log("  ERROR: " + str(e))
        return False


def log(msg):
    """Print timestamped log message."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def watch_loop(interval):
    """Main watch loop — polls VAULT/ for changes."""
    log("DARA Watcher v1.1 started")
    log(f"  Watching: VAULT/NEURONS/ + VAULT/ENABLERS/")
    log(f"  Interval: {interval}s | Debounce: {DEBOUNCE_SECONDS}s")
    log(f"  Press Ctrl+C to stop")
    log("")

    snapshot = get_vault_snapshot()
    vault_files = len([k for k in snapshot if not k.startswith("__monitor__")])
    monitored_files = len([k for k in snapshot if k.startswith("__monitor__")])
    log(f"Initial snapshot: {vault_files} vault files, {monitored_files} monitored system files")
    last_change_time = None
    consecutive_failures = 0

    # Check for previous compile errors
    if COMPILE_ERROR_FILE.exists():
        log("  WARNING: Previous compile errors detected. Delete SYSTEM/.compile-error to resume auto-compile.")

    try:
        while True:
            time.sleep(interval)
            new_snapshot = get_vault_snapshot()
            changes = diff_snapshots(snapshot, new_snapshot)

            if changes:
                for action, name in changes:
                    log(f"  {action}: {name}")
                last_change_time = time.time()
                snapshot = new_snapshot

            # Check for monitored file tampering (BRAIN.md, compile.py, watcher.py)
            if changes:
                for action, name in changes:
                    if name.startswith("__monitor__"):
                        real_name = Path(name.replace("__monitor__", "")).name
                        log("  *** ALERT: " + real_name + " was modified externally — possible tampering ***")

            # Debounce: compile only after DEBOUNCE_SECONDS of quiet
            if last_change_time and (time.time() - last_change_time) >= DEBOUNCE_SECONDS:
                # Filter out monitor changes (don't recompile for BRAIN.md/SYSTEM edits)
                vault_changes = [c for c in changes if not c[1].startswith("__monitor__")] if changes else []
                if not last_change_time:
                    pass  # already handled
                # Skip if compile halted due to repeated failures
                if COMPILE_ERROR_FILE.exists():
                    log("Compile skipped — .compile-error exists. Delete it to resume.")
                    last_change_time = None
                    snapshot = get_vault_snapshot()
                    continue
                log("Compiling...")
                success = run_compile()
                if success:
                    log("Compile OK")
                    consecutive_failures = 0
                    # Clear error file on success
                    if COMPILE_ERROR_FILE.exists():
                        try:
                            COMPILE_ERROR_FILE.unlink()
                        except OSError:
                            pass
                else:
                    consecutive_failures += 1
                    log("Compile FAILED (" + str(consecutive_failures) + "/3)")
                    if consecutive_failures >= 3:
                        error_msg = datetime.now().isoformat() + " | compile.py failed 3 consecutive times. Watcher pausing compilation until .compile-error is deleted."
                        try:
                            COMPILE_ERROR_FILE.write_text(error_msg)
                        except OSError:
                            pass
                        log("  *** COMPILE HALTED: 3 consecutive failures. Delete SYSTEM/.compile-error to resume. ***")
                log("")
                last_change_time = None
                # Refresh snapshot after compile (compile may modify files)
                snapshot = get_vault_snapshot()

    except KeyboardInterrupt:
        log("\nWatcher stopped.")


def check_once():
    """Single check — useful for cron/scheduler."""
    log("DARA Watcher — single check")
    # Compare current state with last known compile time
    if not COMPILE_PY.exists():
        log("ERROR: compile.py not found")
        return

    brain = DARA_ROOT / "LIBRARY" / "BRAIN.md"
    if not brain.exists():
        log("No BRAIN.md — compiling...")
        run_compile()
        return

    brain_mtime = brain.stat().st_mtime
    snapshot = get_vault_snapshot()
    newer = [Path(p).name for p, mt in snapshot.items() if mt > brain_mtime]

    if newer:
        log(f"Files newer than BRAIN.md: {', '.join(newer)}")
        log("Compiling...")
        success = run_compile()
        log("Done" if success else "FAILED")
    else:
        log("All up to date — no compile needed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DARA Watcher — auto-compile on VAULT changes")
    parser.add_argument("--interval", type=int, default=5, help="Poll interval in seconds (default: 5)")
    parser.add_argument("--once", action="store_true", help="Check once and exit")
    args = parser.parse_args()

    if args.once:
        check_once()
    else:
        watch_loop(args.interval)
