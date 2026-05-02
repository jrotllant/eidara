"""
Tests for compile.py — compiler functions (non-validator).
Covers: log, ensure_dirs, backup, prune, read_vault_files, extract_header,
build_index, auto_feedback, compute_checksum, lock, strip_noise, render_enabler,
purge_archived, compile_brain integration.
"""
import json
import re
import sys
import shutil
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# ══════════════════════════════════════════════════════════════
# compute_checksum
# ══════════════════════════════════════════════════════════════

class TestComputeChecksum:
    def test_deterministic(self):
        from compile import compute_checksum
        assert compute_checksum("hello") == compute_checksum("hello")

    def test_different_content(self):
        from compile import compute_checksum
        assert compute_checksum("a") != compute_checksum("b")

    def test_length_16(self):
        from compile import compute_checksum
        assert len(compute_checksum("test")) == 16


# ══════════════════════════════════════════════════════════════
# strip_noise
# ══════════════════════════════════════════════════════════════

class TestStripNoise:
    def test_strips_iban(self):
        from compile import strip_noise
        result = strip_noise("Account: ES12 3456 7890 1234 5678 9012")
        assert "IBAN on file" in result
        assert "ES12" not in result

    def test_strips_nif(self):
        from compile import strip_noise
        result = strip_noise("NIF: 12345678A")
        assert "NIF on file" in result

    def test_strips_uuid(self):
        from compile import strip_noise
        result = strip_noise("ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890")
        assert "UUID on file" in result

    def test_strips_api_tokens(self):
        from compile import strip_noise
        result = strip_noise("Token: sk-abcdefghijklmnopqrstuvwxyz1234567890abcd")
        assert "token on file" in result

    def test_preserves_backtick_code(self):
        from compile import strip_noise
        result = strip_noise("Use `sk-abcdefghijklmnopqrstuvwxyz1234567890abcd` in code")
        assert "sk-" in result  # inside backticks = preserved

    def test_strips_windows_paths(self):
        from compile import strip_noise
        result = strip_noise(r"File at C:\Users\user\Documents\test.txt")
        assert "path on file" in result

    def test_normal_text_unchanged(self):
        from compile import strip_noise
        text = "Normal business text about quarterly results"
        assert strip_noise(text) == text


# ══════════════════════════════════════════════════════════════
# render_enabler_oneliner
# ══════════════════════════════════════════════════════════════

class TestRenderEnablerOneliner:
    def test_with_summary(self):
        from compile import render_enabler_oneliner
        entry = {
            "filename": "agent-test",
            "content": "summary: A test agent for demonstrations\n## Instructions\nDo things.",
            "category": "ENABLERS",
            "chars": 100,
        }
        result = render_enabler_oneliner(entry)
        assert "### agent-test" in result
        assert "A test agent" in result
        assert "summary only" in result

    def test_without_summary_uses_fallback(self):
        from compile import render_enabler_oneliner
        entry = {
            "filename": "agent-fallback",
            "content": "# AGENT Fallback Agent\nRole: Does fallback things\n## Instructions\nFallback.",
            "category": "ENABLERS",
            "chars": 80,
        }
        result = render_enabler_oneliner(entry)
        assert "### agent-fallback" in result

    def test_long_desc_truncated(self):
        from compile import render_enabler_oneliner
        long_desc = "summary: " + "word " * 50
        entry = {
            "filename": "agent-long",
            "content": long_desc + "\nBody",
            "category": "ENABLERS",
            "chars": 300,
        }
        result = render_enabler_oneliner(entry)
        # Should not exceed reasonable length
        first_line = result.split("\n")[0]
        assert len(first_line) < 300


# ══════════════════════════════════════════════════════════════
# read_vault_files
# ══════════════════════════════════════════════════════════════

class TestReadVaultFiles:
    def test_reads_md_files(self, tmp_dara):
        from compile import read_vault_files
        neurons = tmp_dara / "VAULT" / "NEURONS"
        (neurons / "test-one.md").write_text("## test-one [A/H]\nContent here\nMore content\nEven more\n→tags: #test\n| 2026-04-01\n", encoding="utf-8")
        entries = read_vault_files(neurons, "NEURONS")
        assert len(entries) == 1
        assert entries[0]["filename"] == "test-one"
        assert entries[0]["category"] == "NEURONS"

    def test_skips_changelog(self, tmp_dara):
        from compile import read_vault_files
        neurons = tmp_dara / "VAULT" / "NEURONS"
        (neurons / "changelog.md").write_text("# Log\n", encoding="utf-8")
        (neurons / "real-neuron.md").write_text("## real-neuron [A/H]\nContent\nMore\nLines\n", encoding="utf-8")
        entries = read_vault_files(neurons, "NEURONS")
        assert len(entries) == 1
        assert entries[0]["filename"] == "real-neuron"

    def test_strips_null_bytes(self, tmp_dara):
        from compile import read_vault_files
        neurons = tmp_dara / "VAULT" / "NEURONS"
        (neurons / "nulls.md").write_text("## nulls [A/H]\nContent\x00with\x00nulls\nMore lines\nEven more\n", encoding="utf-8")
        entries = read_vault_files(neurons, "NEURONS")
        assert "\x00" not in entries[0]["content"]

    def test_empty_dir(self, tmp_dara):
        from compile import read_vault_files
        neurons = tmp_dara / "VAULT" / "NEURONS"
        entries = read_vault_files(neurons, "NEURONS")
        assert len(entries) == 0

    def test_nonexistent_dir(self, tmp_dara):
        from compile import read_vault_files
        fake = tmp_dara / "VAULT" / "FAKE"
        entries = read_vault_files(fake, "FAKE")
        assert len(entries) == 0


# ══════════════════════════════════════════════════════════════
# get_all_filenames / get_cred_names
# ══════════════════════════════════════════════════════════════

class TestHelpers:
    def test_get_all_filenames(self):
        from compile import get_all_filenames
        neurons = [{"filename": "a"}, {"filename": "b"}]
        enablers = [{"filename": "c"}]
        result = get_all_filenames(neurons, enablers)
        assert result == {"a", "b", "c"}

    def test_get_cred_names(self):
        from compile import get_cred_names
        enablers = [
            {"filename": "credentials", "content": "[CRED:notion-token] and [CRED:slack-key]"},
            {"filename": "other", "content": "no creds here"},
        ]
        result = get_cred_names(enablers)
        assert "notion-token" in result
        assert "slack-key" in result
        assert len(result) == 2

    def test_get_cred_names_no_credentials_file(self):
        from compile import get_cred_names
        enablers = [{"filename": "other", "content": "[CRED:fake]"}]
        result = get_cred_names(enablers)
        assert len(result) == 0


# ══════════════════════════════════════════════════════════════
# build_index
# ══════════════════════════════════════════════════════════════

class TestBuildIndex:
    def test_index_structure(self):
        from compile import build_index
        entries = [
            {"filename": "test-one", "category": "NEURONS"},
            {"filename": "agent-lib", "category": "ENABLERS"},
        ]
        result = build_index(entries)
        assert "## INDEX" in result
        assert "ENABLERS:" in result
        assert "agent-lib" in result

    def test_empty_entries(self):
        from compile import build_index
        result = build_index([])
        assert "## INDEX" in result


# ══════════════════════════════════════════════════════════════
# auto_feedback
# ══════════════════════════════════════════════════════════════

class TestAutoFeedback:
    def test_creates_feedback_file(self, tmp_dara, monkeypatch):
        import compile
        monkeypatch.setattr(compile, "INBOX_DIR", tmp_dara / "VAULT" / "INBOX")
        monkeypatch.setattr(compile, "COMPILER_VERSION", "3.1")
        compile.auto_feedback(["warning1"], ["stale1"])
        inbox = list((tmp_dara / "VAULT" / "INBOX").glob("feedback-*.md"))
        assert len(inbox) == 1
        text = inbox[0].read_text(encoding="utf-8")
        assert "warning1" in text
        assert "stale1" in text

    def test_no_feedback_when_clean(self, tmp_dara, monkeypatch):
        import compile
        monkeypatch.setattr(compile, "INBOX_DIR", tmp_dara / "VAULT" / "INBOX")
        compile.auto_feedback([], [])
        inbox = list((tmp_dara / "VAULT" / "INBOX").glob("feedback-*.md"))
        assert len(inbox) == 0

    def test_does_not_overwrite_existing(self, tmp_dara, monkeypatch):
        import compile
        monkeypatch.setattr(compile, "INBOX_DIR", tmp_dara / "VAULT" / "INBOX")
        monkeypatch.setattr(compile, "COMPILER_VERSION", "3.1")
        compile.auto_feedback(["first"], [])
        compile.auto_feedback(["second"], [])  # same day, should skip
        inbox = list((tmp_dara / "VAULT" / "INBOX").glob("feedback-*.md"))
        assert len(inbox) == 1
        text = inbox[0].read_text(encoding="utf-8")
        assert "first" in text
        assert "second" not in text


# ══════════════════════════════════════════════════════════════
# acquire/release compile lock
# ══════════════════════════════════════════════════════════════

class TestCompileLock:
    def test_creates_and_releases_lock(self, tmp_dara, monkeypatch):
        import compile
        lock_file = tmp_dara / "SYSTEM" / ".compile.lock"
        monkeypatch.setattr(compile, "COMPILE_LOCK_FILE", lock_file)
        monkeypatch.setattr(compile, "DRY_RUN", False)
        compile.acquire_compile_lock()
        assert lock_file.exists()
        data = json.loads(lock_file.read_text(encoding="utf-8"))
        assert "pid" in data
        assert "started" in data
        compile.release_compile_lock()
        assert not lock_file.exists()

    def test_dry_run_no_lock(self, tmp_dara, monkeypatch):
        import compile
        lock_file = tmp_dara / "SYSTEM" / ".compile.lock"
        monkeypatch.setattr(compile, "COMPILE_LOCK_FILE", lock_file)
        monkeypatch.setattr(compile, "DRY_RUN", True)
        compile.acquire_compile_lock()
        assert not lock_file.exists()


# ══════════════════════════════════════════════════════════════
# backup + prune
# ══════════════════════════════════════════════════════════════

class TestBackup:
    def test_backup_creates_file(self, tmp_dara, monkeypatch):
        import compile
        brain = tmp_dara / "LIBRARY" / "BRAIN.md"
        backup = tmp_dara / "VAULT" / "BACKUP"
        brain.write_text("# Test Brain\n", encoding="utf-8")
        monkeypatch.setattr(compile, "BRAIN_FILE", brain)
        monkeypatch.setattr(compile, "BACKUP_DIR", backup)
        result = compile.backup_previous_brain()
        assert result is True
        backups = list(backup.glob("brain_*.md"))
        assert len(backups) == 1

    def test_skip_identical_backup(self, tmp_dara, monkeypatch):
        import compile
        brain = tmp_dara / "LIBRARY" / "BRAIN.md"
        backup = tmp_dara / "VAULT" / "BACKUP"
        brain.write_text("# Same Content\n", encoding="utf-8")
        monkeypatch.setattr(compile, "BRAIN_FILE", brain)
        monkeypatch.setattr(compile, "BACKUP_DIR", backup)
        compile.backup_previous_brain()
        compile.backup_previous_brain()
        backups = list(backup.glob("brain_*.md"))
        assert len(backups) == 1  # should skip duplicate


# ══════════════════════════════════════════════════════════════
# purge_archived
# ══════════════════════════════════════════════════════════════

class TestPurgeArchived:
    def test_purges_old_archived(self, tmp_dara, monkeypatch):
        import compile
        monkeypatch.setattr(compile, "ARCHIVE_PURGE_DAYS", 60)
        monkeypatch.setattr(compile, "DRY_RUN", False)
        monkeypatch.setattr(compile, "TRASH_DIR", tmp_dara / "VAULT" / "TRASH")
        old_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        fp = tmp_dara / "VAULT" / "NEURONS" / "old-entry.md"
        fp.write_text("## old-entry [C/L] Old Entry\nArchived content\n| " + old_date + "\n", encoding="utf-8")
        neurons = [{"filename": "old-entry", "filepath": fp, "content": fp.read_text(encoding="utf-8"), "category": "NEURONS", "chars": 50}]
        kept_n, kept_e, purged = compile.purge_archived(neurons, [])
        assert len(purged) == 1
        assert len(kept_n) == 0

    def test_keeps_recent_archived(self, tmp_dara, monkeypatch):
        import compile
        monkeypatch.setattr(compile, "ARCHIVE_PURGE_DAYS", 60)
        monkeypatch.setattr(compile, "DRY_RUN", False)
        recent = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        fp = tmp_dara / "VAULT" / "NEURONS" / "recent.md"
        fp.write_text("## recent [C/L] Recent\nContent\n| " + recent + "\n", encoding="utf-8")
        neurons = [{"filename": "recent", "filepath": fp, "content": fp.read_text(encoding="utf-8"), "category": "NEURONS", "chars": 40}]
        kept_n, kept_e, purged = compile.purge_archived(neurons, [])
        assert len(purged) == 0
        assert len(kept_n) == 1

    def test_keeps_active_entries(self, tmp_dara, monkeypatch):
        import compile
        monkeypatch.setattr(compile, "ARCHIVE_PURGE_DAYS", 60)
        fp = tmp_dara / "VAULT" / "NEURONS" / "active.md"
        fp.write_text("## active [A/H] Active\nContent\n| 2025-01-01\n", encoding="utf-8")
        neurons = [{"filename": "active", "filepath": fp, "content": fp.read_text(encoding="utf-8"), "category": "NEURONS", "chars": 40}]
        kept_n, kept_e, purged = compile.purge_archived(neurons, [])
        assert len(purged) == 0
        assert len(kept_n) == 1
