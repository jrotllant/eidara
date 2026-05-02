#!/usr/bin/env python3
"""
DARA Validators v1.0
Validation, fixing, and checking functions for the DARA compiler.
Split from compile.py for modularity and testability.

All functions receive explicit parameters — no global state dependency.
"""

import re
import hashlib
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path


ARROW = "\u2192"  # →


def get_entry_date(content):
    """Extract the most recent date from a VAULT entry."""
    m = re.search(r'\|\s*(\d{4}-\d{2}-\d{2})\s*$', content, re.MULTILINE)
    if m:
        try:
            return datetime.strptime(m.group(1), "%Y-%m-%d")
        except ValueError:
            pass
    lines = content.strip().split("\n")
    for line in reversed(lines[-5:]):
        m2 = re.search(r'(\d{4}-\d{2}-\d{2})', line)
        if m2:
            try:
                return datetime.strptime(m2.group(1), "%Y-%m-%d")
            except ValueError:
                pass
    return None


def fix_refs(content, valid, name):
    """Fix broken →refs: by removing references to non-existent files."""
    fixes = []
    lines = content.split("\n")
    out = []
    for line in lines:
        if line.startswith(ARROW + "refs:"):
            ref_part = line.split(":", 1)[1].strip()
            refs = [r.strip() for r in ref_part.split(",") if r.strip() and r.strip() != "(none)"]
            good = [r for r in refs if r in valid]
            bad = [r for r in refs if r not in valid]
            if bad:
                fixes.append(name + ": removed broken refs: " + ", ".join(bad))
            if good:
                out.append(ARROW + "refs: " + ", ".join(good))
            else:
                out.append(ARROW + "refs: (none)")
        else:
            out.append(line)
    return "\n".join(out), fixes


def fix_header(content, filename, filepath, dry_run=False):
    """Fix or warn about mismatched ## headers. Conservative: only auto-fix kebab-case slugs."""
    fixes = []
    lines = content.split("\n")
    if lines and lines[0].startswith("## "):
        m = re.match(r'## (\S+)\s*(.*)', lines[0])
        if m and m.group(1) != filename:
            old = m.group(1)
            if re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', old):
                lines[0] = "## " + filename + " " + m.group(2)
                fixes.append(filename + ": header '" + old + "' auto-fixed to '" + filename + "'")
                if not dry_run:
                    try:
                        filepath.write_text("\n".join(lines), encoding="utf-8")
                    except Exception:
                        pass
                return "\n".join(lines), fixes
            else:
                fixes.append(filename + ": header '" + old + "' differs from filename — review manually (not auto-fixed)")
    elif lines and re.match(r'^# [^#]', lines[0]):
        fixes.append(filename + ": uses single-hash header (# instead of ##) — may not parse correctly")
    return content, fixes


def fix_ascii_arrows(content, filename, filepath, dry_run=False):
    """Auto-fix ASCII ->refs: and ->tags: to Unicode arrows."""
    fixes = []
    original = content
    if "->refs:" in content:
        content = content.replace("->refs:", ARROW + "refs:")
        fixes.append(filename + ": auto-fixed ->refs: to " + ARROW + "refs:")
    if "->tags:" in content:
        content = content.replace("->tags:", ARROW + "tags:")
        fixes.append(filename + ": auto-fixed ->tags: to " + ARROW + "tags:")
    if "->flag:" in content:
        content = content.replace("->flag:", ARROW + "flag:")
        fixes.append(filename + ": auto-fixed ->flag: to " + ARROW + "flag:")
    if fixes and content != original and not dry_run:
        try:
            filepath.write_text(content, encoding="utf-8")
        except Exception:
            pass
    return content, fixes


def check_creds(content, valid_creds, name):
    """Check for [CRED:x] references pointing to non-existent credentials."""
    warns = []
    for m in re.finditer(r'\[CRED:([^\]]+)\]', content):
        if m.group(1) not in valid_creds:
            warns.append(name + ": [CRED:" + m.group(1) + "] not in credentials.md")
    return warns


def check_stale(content, name, staleness_days=180):
    """Flag active entries older than staleness_days."""
    flags = []
    d = get_entry_date(content)
    if d:
        age = (datetime.now() - d).days
        if age > staleness_days and ("[A/H]" in content or "[A/M]" in content):
            flags.append(name + ": " + str(age) + " days old, still active")
    return flags


def dedup(neurons, enablers):
    """Remove entries that exist in both NEURONS and ENABLERS (keep NEURONS)."""
    fixes = []
    n_names = {e["filename"] for e in neurons}
    clean = []
    for e in enablers:
        if e["filename"] in n_names:
            fixes.append(e["filename"] + ": duplicate in NEURONS+ENABLERS, keeping NEURONS")
        else:
            clean.append(e)
    return neurons, clean, fixes


def content_similarity_check(neurons):
    """Check for semantically similar neurons using Jaccard similarity on word sets."""
    warns = []
    if len(neurons) < 2:
        return warns
    word_sets = {}
    for e in neurons:
        text = e["content"].lower()
        text = re.sub(r'^##.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'\u2192\w+:.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'\d{4}-\d{2}-\d{2}', '', text)
        words = re.findall(r'[a-z]{3,}', text)
        stops = {"the","and","for","that","this","with","from","are","was","has","have","not","but","its","will","can","all","been","would","were","they","their","also","more","some","than","other","into","over","about","which","when","each","only","after","between","these","most","such","both","through","just","any","being"}
        meaningful = [w for w in words if w not in stops][:100]
        word_sets[e["filename"]] = set(meaningful)
    names = list(word_sets.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = word_sets[names[i]], word_sets[names[j]]
            if not a or not b:
                continue
            intersection = len(a & b)
            union = len(a | b)
            if union == 0:
                continue
            jaccard = intersection / union
            if jaccard > 0.60:
                warns.append(names[i] + " <-> " + names[j] + ": " + str(int(jaccard * 100)) + "% content similarity — possible duplicate, consider merging")
    return warns


def check_kebab_case(entries):
    """W8: All filenames must be kebab-case."""
    warns = []
    for e in entries:
        fn = e["filename"]
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', fn):
            warns.append(fn + ": filename is NOT kebab-case (W8 violation)")
    return warns


def check_orphan_files(vault_dir):
    """Check for .md files in VAULT/ root that shouldn't be there."""
    warns = []
    known_root = {"changelog.md"}
    if not vault_dir.exists():
        return warns
    for f in vault_dir.glob("*.md"):
        if f.name not in known_root:
            warns.append(f.name + ": orphan file in VAULT/ root (should be in NEURONS/ or ENABLERS/)")
    return warns


def check_changelog_format(vault_dir):
    """W7: Check changelog entries follow the standard format."""
    warns = []
    cl_path = vault_dir / "changelog.md"
    if not cl_path.exists():
        return warns
    text = cl_path.read_text(encoding="utf-8", errors="replace")
    sections = re.split(r'^##+ \d{4}-\d{2}-\d{2}', text, flags=re.MULTILINE)
    if len(sections) < 2:
        return warns
    last_section = sections[1]
    lines = [l.strip() for l in last_section.split("\n") if l.strip().startswith("- ")]
    w7_pattern = re.compile(r'^- .+\|.+\|.+\| ops:\d+', re.IGNORECASE)
    bad_count = 0
    for line in lines:
        if not w7_pattern.match(line):
            bad_count += 1
    if bad_count > 0:
        warns.append("changelog.md: " + str(bad_count) + " entry(ies) in latest section don\'t follow W7 format (AI Model (Platform) | file | what | ops:N | retry:Y/N | ~NNKt)")
    return warns


def check_monetary_format(entries):
    """INFO: Flag entries using verbose monetary formats instead of encoding."""
    infos = []
    verbose_money = re.compile(r'\b\d{1,3}(?:[.,]\d{3})+\s*(?:euros?|EUR|\u20ac)\b|\b(?:euros?|EUR)\s*\d{1,3}(?:[.,]\d{3})+\b', re.IGNORECASE)
    for e in entries:
        if e["filename"] == "credentials":
            continue
        matches = verbose_money.findall(e["content"])
        if matches:
            infos.append(e["filename"] + ": " + str(len(matches)) + " verbose monetary value(s) found — consider encoding")
    return infos


def check_misplaced_agents(neurons):
    """Detect agent files in NEURONS/ (should be in ENABLERS/)."""
    warns = []
    for e in neurons:
        if e["filename"].startswith("agent-"):
            warns.append(e["filename"] + ": agent file in NEURONS/ — should be in ENABLERS/ (W8)")
        elif e["content"].lstrip().startswith("# AGENT"):
            warns.append(e["filename"] + ": has AGENT header but is in NEURONS/ — should be in ENABLERS/ (W8)")
    return warns


def check_size_regression(neurons_dir, enablers_dir, root_dir):
    """Pre-compile: compare VAULT file sizes vs last git commit. Detect truncation."""
    warns = []
    try:
        r = subprocess.run(["git", "--version"], capture_output=True, timeout=5)
        if r.returncode != 0:
            return warns
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return warns
    git_dir = root_dir / ".git"
    if not git_dir.exists():
        return warns
    for d, label in [(neurons_dir, "NEURONS"), (enablers_dir, "ENABLERS")]:
        if not d.exists():
            continue
        for f in sorted(d.glob("*.md")):
            if f.name == "changelog.md":
                continue
            current_size = f.stat().st_size
            rel_path = "VAULT/" + label + "/" + f.name
            try:
                r = subprocess.run(
                    ["git", "show", "HEAD:" + rel_path],
                    cwd=str(root_dir), capture_output=True, timeout=5
                )
                if r.returncode == 0:
                    git_size = len(r.stdout)
                    if git_size > 200 and current_size < git_size * 0.8:
                        pct = int((1 - current_size / git_size) * 100)
                        warns.append(f.stem + ": file shrank " + str(pct) + "% vs last commit (" + str(git_size) + " -> " + str(current_size) + " bytes) — possible truncation")
            except (subprocess.TimeoutExpired, OSError):
                pass
    return warns


def check_protected_files(protected_files, root_dir, checksums_file, dry_run=False):
    """W3(b): Verify protected files haven\'t changed since last compile."""
    warns = []
    current = {}
    for rel in protected_files:
        fp = root_dir / rel
        if fp.exists():
            h = hashlib.sha256(fp.read_bytes()).hexdigest()[:16]
            current[rel] = h
    prev = {}
    if checksums_file.exists():
        try:
            prev = json.loads(checksums_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    if prev:
        for rel, cur_hash in current.items():
            if rel in prev and prev[rel] != cur_hash:
                warns.append("W3(b) ALERT: " + rel + " was modified since last compile (hash changed)")
    if not dry_run:
        try:
            checksums_file.write_text(
                json.dumps(current, indent=2), encoding="utf-8"
            )
        except OSError:
            pass
    return warns


def check_brain_tamper(brain_file, checksum_tag="DARA_CHECKSUM"):
    """Check if BRAIN.md was manually edited since last compile."""
    if not brain_file.exists():
        return False, None
    try:
        text = brain_file.read_text(encoding="utf-8")
    except (PermissionError, OSError):
        return False, None
    m = re.search(r'<!-- ' + checksum_tag + r':([a-f0-9]{16}) -->', text)
    if not m:
        return False, "no_checksum"
    stored = m.group(1)
    after_checksum = text[m.end():].strip()
    if after_checksum:
        return True, "appended"
    content_before = text[:m.start()].rstrip("\n")
    actual = hashlib.sha256(content_before.encode("utf-8")).hexdigest()[:16]
    if stored != actual:
        return True, "modified"
    return False, None
