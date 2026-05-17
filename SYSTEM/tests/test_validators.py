"""
Tests for validators.py — all 16 extracted validator/fix/check functions.
"""
import json
import re
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent dir so we can import validators
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from validators import (
    get_entry_date, fix_refs, fix_header, fix_ascii_arrows,
    check_creds, check_stale, dedup, content_similarity_check,
    check_kebab_case, check_orphan_files, check_changelog_format,
    check_monetary_format, check_misplaced_agents, check_size_regression,
    check_protected_files, check_brain_tamper,
)


# ══════════════════════════════════════════════════════════════
# get_entry_date
# ══════════════════════════════════════════════════════════════

class TestGetEntryDate:
    def test_standard_pipe_format(self):
        content = "## test [A/H]\nSome text\n| 2026-03-15\n"
        d = get_entry_date(content)
        assert d is not None
        assert d.year == 2026 and d.month == 3 and d.day == 15

    def test_fallback_date_in_last_lines(self):
        content = "## test [A/H]\nSome text\nUpdated 2025-12-01\n"
        d = get_entry_date(content)
        assert d is not None
        assert d.year == 2025

    def test_no_date(self):
        content = "## test [A/H]\nNo dates here\n"
        assert get_entry_date(content) is None

    def test_invalid_date(self):
        content = "## test [A/H]\n| 2026-13-99\n"
        assert get_entry_date(content) is None


# ══════════════════════════════════════════════════════════════
# fix_refs
# ══════════════════════════════════════════════════════════════

class TestFixRefs:
    def test_removes_broken_refs(self):
        content = "## test\n→refs: valid-one, broken-one\n"
        valid = {"valid-one", "other"}
        result, fixes = fix_refs(content, valid, "test")
        assert "broken-one" not in result
        assert "valid-one" in result
        assert len(fixes) == 1

    def test_keeps_all_valid(self):
        content = "## test\n→refs: a, b\n"
        valid = {"a", "b"}
        result, fixes = fix_refs(content, valid, "test")
        assert len(fixes) == 0
        assert "a" in result and "b" in result

    def test_all_broken_becomes_none(self):
        content = "→refs: ghost\n"
        result, fixes = fix_refs(content, set(), "test")
        assert "(none)" in result


# ══════════════════════════════════════════════════════════════
# fix_header
# ══════════════════════════════════════════════════════════════

class TestFixHeader:
    def test_auto_fixes_kebab_slug(self, tmp_path):
        fp = tmp_path / "correct-name.md"
        content = "## old-name Some Title\nBody\n"
        fp.write_text(content, encoding="utf-8")
        result, fixes = fix_header(content, "correct-name", fp, dry_run=True)
        assert "correct-name" in result
        assert len(fixes) == 1
        assert "auto-fixed" in fixes[0]

    def test_warns_non_kebab_header(self, tmp_path):
        fp = tmp_path / "my-file.md"
        content = "## My Fancy Title\nBody\n"
        fp.write_text(content, encoding="utf-8")
        result, fixes = fix_header(content, "my-file", fp, dry_run=True)
        assert "review manually" in fixes[0]

    def test_detects_single_hash(self, tmp_path):
        fp = tmp_path / "test.md"
        content = "# Bad Title\nBody\n"
        fp.write_text(content, encoding="utf-8")
        result, fixes = fix_header(content, "test", fp, dry_run=True)
        assert "single-hash" in fixes[0]

    def test_matching_header_no_fix(self, tmp_path):
        fp = tmp_path / "my-file.md"
        content = "## my-file Some Title\nBody\n"
        fp.write_text(content, encoding="utf-8")
        result, fixes = fix_header(content, "my-file", fp, dry_run=True)
        assert len(fixes) == 0


# ══════════════════════════════════════════════════════════════
# fix_ascii_arrows
# ══════════════════════════════════════════════════════════════

class TestFixAsciiArrows:
    def test_fixes_arrow_refs(self, tmp_path):
        fp = tmp_path / "test.md"
        content = "->refs: some-file\n->tags: #test\n"
        fp.write_text(content, encoding="utf-8")
        result, fixes = fix_ascii_arrows(content, "test", fp, dry_run=True)
        assert "→refs:" in result
        assert "→tags:" in result
        assert len(fixes) == 2

    def test_no_change_on_unicode(self, tmp_path):
        fp = tmp_path / "test.md"
        content = "→refs: valid\n"
        fp.write_text(content, encoding="utf-8")
        result, fixes = fix_ascii_arrows(content, "test", fp, dry_run=True)
        assert len(fixes) == 0


# ══════════════════════════════════════════════════════════════
# check_creds
# ══════════════════════════════════════════════════════════════

class TestCheckCreds:
    def test_valid_cred(self):
        content = "Uses [CRED:notion-token] for access"
        warns = check_creds(content, {"notion-token"}, "test")
        assert len(warns) == 0

    def test_invalid_cred(self):
        content = "Uses [CRED:ghost-cred] for access"
        warns = check_creds(content, {"notion-token"}, "test")
        assert len(warns) == 1
        assert "ghost-cred" in warns[0]


# ══════════════════════════════════════════════════════════════
# check_stale
# ══════════════════════════════════════════════════════════════

class TestCheckStale:
    def test_stale_active_entry(self):
        old_date = (datetime.now() - timedelta(days=200)).strftime("%Y-%m-%d")
        content = "## old [A/H]\nOld content\n| " + old_date + "\n"
        flags = check_stale(content, "old", staleness_days=180)
        assert len(flags) == 1

    def test_recent_entry_not_stale(self):
        recent = datetime.now().strftime("%Y-%m-%d")
        content = "## new [A/H]\nNew content\n| " + recent + "\n"
        flags = check_stale(content, "new", staleness_days=180)
        assert len(flags) == 0

    def test_archived_not_flagged(self):
        old_date = (datetime.now() - timedelta(days=200)).strftime("%Y-%m-%d")
        content = "## old [C/L]\nOld content\n| " + old_date + "\n"
        flags = check_stale(content, "old", staleness_days=180)
        assert len(flags) == 0


# ══════════════════════════════════════════════════════════════
# dedup
# ══════════════════════════════════════════════════════════════

class TestDedup:
    def test_removes_duplicate_from_enablers(self):
        neurons = [{"filename": "shared"}]
        enablers = [{"filename": "shared"}, {"filename": "unique"}]
        n, e, fixes = dedup(neurons, enablers)
        assert len(e) == 1
        assert e[0]["filename"] == "unique"
        assert len(fixes) == 1

    def test_no_duplicates(self):
        neurons = [{"filename": "a"}]
        enablers = [{"filename": "b"}]
        n, e, fixes = dedup(neurons, enablers)
        assert len(fixes) == 0


# ══════════════════════════════════════════════════════════════
# content_similarity_check
# ══════════════════════════════════════════════════════════════

class TestContentSimilarity:
    def test_identical_content_flagged(self):
        text = "## header\nThis is a long body of text with many words about finance investment portfolio strategy risk management returns allocation diversification bonds equities market analysis quarterly performance review\n"
        neurons = [
            {"filename": "a", "content": text},
            {"filename": "b", "content": text},
        ]
        warns = content_similarity_check(neurons)
        assert len(warns) == 1
        assert "similarity" in warns[0]

    def test_different_content_ok(self):
        neurons = [
            {"filename": "a", "content": "## a\nThis talks about cats dogs animals pets veterinary care grooming feeding walking training behavior socialization\n"},
            {"filename": "b", "content": "## b\nThis covers finance investment portfolio strategy risk management returns allocation diversification bonds equities\n"},
        ]
        warns = content_similarity_check(neurons)
        assert len(warns) == 0

    def test_single_neuron_no_check(self):
        warns = content_similarity_check([{"filename": "a", "content": "text"}])
        assert len(warns) == 0


# ══════════════════════════════════════════════════════════════
# check_kebab_case
# ══════════════════════════════════════════════════════════════

class TestKebabCase:
    def test_valid_kebab(self):
        entries = [{"filename": "my-cool-file"}, {"filename": "simple"}]
        assert len(check_kebab_case(entries)) == 0

    def test_invalid_names(self):
        entries = [
            {"filename": "My_File"},
            {"filename": "HAS SPACES"},
            {"filename": "camelCase"},
        ]
        warns = check_kebab_case(entries)
        assert len(warns) == 3


# ══════════════════════════════════════════════════════════════
# check_orphan_files
# ══════════════════════════════════════════════════════════════

class TestOrphanFiles:
    def test_no_orphans(self, tmp_dara):
        vault = tmp_dara / "VAULT"
        (vault / "changelog.md").write_text("# Log\n", encoding="utf-8")
        warns = check_orphan_files(vault)
        assert len(warns) == 0

    def test_detects_orphan(self, tmp_dara):
        vault = tmp_dara / "VAULT"
        (vault / "stray-file.md").write_text("orphan\n", encoding="utf-8")
        warns = check_orphan_files(vault)
        assert len(warns) == 1
        assert "orphan" in warns[0]


# ══════════════════════════════════════════════════════════════
# check_changelog_format
# ══════════════════════════════════════════════════════════════

class TestChangelogFormat:
    def test_valid_format(self, tmp_dara):
        vault = tmp_dara / "VAULT"
        cl = vault / "changelog.md"
        cl.write_text(
            "# Changelog\n\n## 2026-04-30\n"
            "- Claude Opus (Cowork) | test-file | updated content | ops:3 | retry:N | ~2Kt\n",
            encoding="utf-8"
        )
        warns = check_changelog_format(vault)
        assert len(warns) == 0

    def test_bad_format(self, tmp_dara):
        vault = tmp_dara / "VAULT"
        cl = vault / "changelog.md"
        cl.write_text(
            "# Changelog\n\n## 2026-04-30\n"
            "- Just updated some stuff\n",
            encoding="utf-8"
        )
        warns = check_changelog_format(vault)
        assert len(warns) == 1


# ══════════════════════════════════════════════════════════════
# check_monetary_format
# ══════════════════════════════════════════════════════════════

class TestMonetaryFormat:
    def test_verbose_money_flagged(self):
        entries = [{"filename": "test", "content": "Cost is 1.500 euros per month"}]
        infos = check_monetary_format(entries)
        assert len(infos) == 1

    def test_encoded_money_ok(self):
        entries = [{"filename": "test", "content": "Budget: €15K allocated"}]
        infos = check_monetary_format(entries)
        assert len(infos) == 0

    def test_credentials_skipped(self):
        entries = [{"filename": "credentials", "content": "1.500 euros in account"}]
        infos = check_monetary_format(entries)
        assert len(infos) == 0


# ══════════════════════════════════════════════════════════════
# check_misplaced_agents
# ══════════════════════════════════════════════════════════════

class TestMisplacedAgents:
    def test_agent_prefix_in_neurons(self):
        neurons = [{"filename": "agent-test", "content": "## agent-test\nBody\n"}]
        warns = check_misplaced_agents(neurons)
        assert len(warns) == 1

    def test_agent_header_in_neurons(self):
        neurons = [{"filename": "my-agent", "content": "# AGENT My Agent\nBody\n"}]
        warns = check_misplaced_agents(neurons)
        assert len(warns) == 1

    def test_normal_neuron_ok(self):
        neurons = [{"filename": "my-topic", "content": "## my-topic [A/H]\nBody\n"}]
        warns = check_misplaced_agents(neurons)
        assert len(warns) == 0


# ══════════════════════════════════════════════════════════════
# check_protected_files
# ══════════════════════════════════════════════════════════════

class TestProtectedFiles:
    def test_first_run_no_warnings(self, tmp_dara):
        # Create a protected file
        dara_md = tmp_dara / "DARA.md"
        checksums_file = tmp_dara / "SYSTEM" / ".protected_checksums.json"
        warns = check_protected_files(["DARA.md"], tmp_dara, checksums_file, dry_run=False)
        assert len(warns) == 0
        assert checksums_file.exists()

    def test_detects_modification(self, tmp_dara):
        dara_md = tmp_dara / "DARA.md"
        checksums_file = tmp_dara / "SYSTEM" / ".protected_checksums.json"
        # First run: baseline
        check_protected_files(["DARA.md"], tmp_dara, checksums_file, dry_run=False)
        # Modify the file
        dara_md.write_text("MODIFIED CONTENT", encoding="utf-8")
        # Second run: should detect change
        warns = check_protected_files(["DARA.md"], tmp_dara, checksums_file, dry_run=False)
        assert len(warns) == 1
        assert "W3(b)" in warns[0]

    def test_dry_run_no_write(self, tmp_dara):
        checksums_file = tmp_dara / "SYSTEM" / ".protected_checksums.json"
        check_protected_files(["DARA.md"], tmp_dara, checksums_file, dry_run=True)
        assert not checksums_file.exists()


# ══════════════════════════════════════════════════════════════
# check_brain_tamper
# ══════════════════════════════════════════════════════════════

class TestBrainTamper:
    def _make_brain(self, path, content, add_checksum=True):
        import hashlib
        if add_checksum:
            h = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
            full = content + "\n<!-- DARA_CHECKSUM:" + h + " -->\n"
        else:
            full = content
        path.write_text(full, encoding="utf-8")

    def test_no_tampering(self, tmp_dara):
        brain = tmp_dara / "LIBRARY" / "BRAIN.md"
        self._make_brain(brain, "# BRAIN\nClean content")
        tampered, reason = check_brain_tamper(brain, "DARA_CHECKSUM")
        assert tampered is False
        assert reason is None

    def test_modified_content(self, tmp_dara):
        brain = tmp_dara / "LIBRARY" / "BRAIN.md"
        self._make_brain(brain, "# BRAIN\nOriginal")
        # Now modify the content but keep old checksum
        text = brain.read_text(encoding="utf-8")
        text = text.replace("Original", "HACKED")
        brain.write_text(text, encoding="utf-8")
        tampered, reason = check_brain_tamper(brain, "DARA_CHECKSUM")
        assert tampered is True
        assert reason == "modified"

    def test_appended_content(self, tmp_dara):
        brain = tmp_dara / "LIBRARY" / "BRAIN.md"
        self._make_brain(brain, "# BRAIN\nContent")
        text = brain.read_text(encoding="utf-8")
        brain.write_text(text + "\nAppended stuff", encoding="utf-8")
        tampered, reason = check_brain_tamper(brain, "DARA_CHECKSUM")
        assert tampered is True
        assert reason == "appended"

    def test_no_checksum(self, tmp_dara):
        brain = tmp_dara / "LIBRARY" / "BRAIN.md"
        self._make_brain(brain, "# BRAIN\nNo checksum", add_checksum=False)
        tampered, reason = check_brain_tamper(brain, "DARA_CHECKSUM")
        assert tampered is False
        assert reason == "no_checksum"

    def test_missing_file(self, tmp_dara):
        brain = tmp_dara / "LIBRARY" / "BRAIN.md"
        tampered, reason = check_brain_tamper(brain, "DARA_CHECKSUM")
        assert tampered is False


# ══════════════════════════════════════════════════════════════
# check_size_regression (limited — needs git)
# ══════════════════════════════════════════════════════════════

class TestSizeRegression:
    def test_no_git_returns_empty(self, tmp_dara):
        neurons = tmp_dara / "VAULT" / "NEURONS"
        enablers = tmp_dara / "VAULT" / "ENABLERS"
        warns = check_size_regression(neurons, enablers, tmp_dara)
        assert warns == []


# ══════════════════════════════════════════════════════════════
# EDGE CASES — additional coverage to reach 80+ tests
# ══════════════════════════════════════════════════════════════

class TestGetEntryDateEdgeCases:
    def test_multiple_dates_returns_pipe_format(self):
        content = "## test\nMentioned 2020-01-01 somewhere\nAnother 2021-06-15\n| 2026-01-01\n"
        d = get_entry_date(content)
        assert d.year == 2026  # pipe format takes priority

    def test_date_in_tags_line(self):
        content = "## test [A/H]\nBody\n→tags: #updated\n2025-08-20\n"
        d = get_entry_date(content)
        assert d is not None
        assert d.year == 2025


class TestFixRefsEdgeCases:
    def test_multiple_ref_lines(self):
        content = "→refs: a, b\nMiddle line\n→refs: c\n"
        valid = {"a", "c"}
        result, fixes = fix_refs(content, valid, "test")
        assert "a" in result
        assert "b" not in result
        assert "c" in result

    def test_empty_refs(self):
        content = "→refs: \n"
        result, fixes = fix_refs(content, set(), "test")
        assert "(none)" in result

    def test_refs_with_extra_spaces(self):
        content = "→refs:   spaced  ,  another  \n"
        valid = {"spaced", "another"}
        result, fixes = fix_refs(content, valid, "test")
        assert len(fixes) == 0


class TestFixHeaderEdgeCases:
    def test_empty_content(self, tmp_path):
        fp = tmp_path / "empty.md"
        fp.write_text("", encoding="utf-8")
        result, fixes = fix_header("", "empty", fp, dry_run=True)
        assert len(fixes) == 0

    def test_no_header_at_all(self, tmp_path):
        fp = tmp_path / "nohead.md"
        content = "Just body text\nNo header\n"
        fp.write_text(content, encoding="utf-8")
        result, fixes = fix_header(content, "nohead", fp, dry_run=True)
        assert len(fixes) == 0

    def test_triple_hash_header(self, tmp_path):
        fp = tmp_path / "triple.md"
        content = "### triple Something\nBody\n"
        fp.write_text(content, encoding="utf-8")
        result, fixes = fix_header(content, "triple", fp, dry_run=True)
        assert len(fixes) == 0  # not ## or #, so no action


class TestCheckStaleEdgeCases:
    def test_paused_not_flagged(self):
        old_date = (datetime.now() - timedelta(days=200)).strftime("%Y-%m-%d")
        content = "## test [P/M]\nPaused content\n| " + old_date + "\n"
        flags = check_stale(content, "test", staleness_days=180)
        assert len(flags) == 0  # [P] = paused, not active

    def test_exactly_at_threshold(self):
        exact = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
        content = "## test [A/H]\nContent\n| " + exact + "\n"
        flags = check_stale(content, "test", staleness_days=180)
        assert len(flags) == 0  # exactly 180 = not stale (> not >=)

    def test_custom_staleness_days(self):
        recent = (datetime.now() - timedelta(days=35)).strftime("%Y-%m-%d")
        content = "## test [A/M]\nContent\n| " + recent + "\n"
        flags = check_stale(content, "test", staleness_days=30)
        assert len(flags) == 1


class TestContentSimilarityEdgeCases:
    def test_empty_neurons(self):
        warns = content_similarity_check([])
        assert len(warns) == 0

    def test_neurons_with_only_metadata(self):
        neurons = [
            {"filename": "a", "content": "## a [A/H]\n→refs: b\n→tags: #x\n| 2026-01-01\n"},
            {"filename": "b", "content": "## b [A/H]\n→refs: a\n→tags: #y\n| 2026-01-02\n"},
        ]
        warns = content_similarity_check(neurons)
        assert len(warns) == 0  # metadata stripped, no meaningful words

    def test_partial_overlap_below_threshold(self):
        base_words = "alpha bravo charlie delta echo foxtrot golf hotel india juliet"
        other_words = "kilo lima mike november oscar papa quebec romeo sierra tango"
        neurons = [
            {"filename": "a", "content": "## a\n" + base_words + " " + other_words[:20] + "\n"},
            {"filename": "b", "content": "## b\n" + other_words + " " + base_words[:20] + "\n"},
        ]
        warns = content_similarity_check(neurons)
        assert len(warns) == 0


class TestCheckKebabCaseEdgeCases:
    def test_numbers_allowed(self):
        entries = [{"filename": "project-2026"}, {"filename": "v3-release"}]
        assert len(check_kebab_case(entries)) == 0

    def test_underscore_not_allowed(self):
        entries = [{"filename": "my_file"}]
        assert len(check_kebab_case(entries)) == 1

    def test_uppercase_not_allowed(self):
        entries = [{"filename": "MyFile"}]
        assert len(check_kebab_case(entries)) == 1

    def test_single_word(self):
        entries = [{"filename": "simple"}]
        assert len(check_kebab_case(entries)) == 0

    def test_trailing_hyphen(self):
        entries = [{"filename": "bad-"}]
        assert len(check_kebab_case(entries)) == 1


class TestCheckProtectedFilesEdgeCases:
    def test_missing_file_no_crash(self, tmp_dara):
        checksums_file = tmp_dara / "SYSTEM" / ".protected_checksums.json"
        warns = check_protected_files(["nonexistent.md"], tmp_dara, checksums_file, dry_run=True)
        assert len(warns) == 0

    def test_corrupted_checksums_file(self, tmp_dara):
        checksums_file = tmp_dara / "SYSTEM" / ".protected_checksums.json"
        checksums_file.write_text("NOT JSON!", encoding="utf-8")
        warns = check_protected_files(["DARA.md"], tmp_dara, checksums_file, dry_run=True)
        assert len(warns) == 0  # should gracefully handle


class TestBrainTamperEdgeCases:
    def test_wrong_checksum_tag(self, tmp_dara):
        import hashlib
        brain = tmp_dara / "LIBRARY" / "BRAIN.md"
        content = "# BRAIN\nContent"
        h = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
        brain.write_text(content + "\n<!-- RAM_CHECKSUM:" + h + " -->\n", encoding="utf-8")
        # Looking for DARA_CHECKSUM but file has RAM_CHECKSUM
        tampered, reason = check_brain_tamper(brain, "DARA_CHECKSUM")
        assert reason == "no_checksum"


class TestCheckOrphanFilesEdgeCases:
    def test_nonexistent_vault(self):
        warns = check_orphan_files(Path("/fake/path"))
        assert len(warns) == 0

    def test_non_md_files_ignored(self, tmp_dara):
        vault = tmp_dara / "VAULT"
        (vault / "notes.txt").write_text("text file\n")
        warns = check_orphan_files(vault)
        assert len(warns) == 0  # only checks .md


class TestCheckMonetaryEdgeCases:
    def test_small_numbers_not_flagged(self):
        entries = [{"filename": "test", "content": "Only 50 euros"}]
        infos = check_monetary_format(entries)
        assert len(infos) == 0  # no thousand separator = not verbose

    def test_eur_format(self):
        entries = [{"filename": "test", "content": "Cost: 2.500 EUR total"}]
        infos = check_monetary_format(entries)
        assert len(infos) == 1
