"""
Shared fixtures for DARA test suite.
Creates isolated VAULT structures in tmp directories.
"""
import json
import pytest
import shutil
from pathlib import Path

@pytest.fixture
def tmp_dara(tmp_path):
    """Create a minimal DARA directory structure for testing."""
    root = tmp_path / "DARA"
    vault = root / "VAULT"
    neurons = vault / "NEURONS"
    enablers = vault / "ENABLERS"
    inbox = vault / "INBOX"
    trash = vault / "TRASH"
    backup = vault / "BACKUP"
    library = root / "LIBRARY"
    system = root / "SYSTEM"

    for d in [neurons, enablers, inbox, trash, backup, library, system]:
        d.mkdir(parents=True)

    # Create DARA.md
    dara_md = root / "DARA.md"
    dara_md.write_text(
        "# DARA\n\n## DESIGN PRINCIPLES\n- W1: One topic per neuron\n"
        "- W2: Encoding rules\n---\n\n## STRUCTURE\nVAULT/\n",
        encoding="utf-8"
    )

    # Create config.json
    config = system / "config.json"
    config.write_text(json.dumps({
        "maxBackups": 10,
        "stalenessDays": 180,
        "archivePurgeDays": 60,
        "brainThreshold": 1500,
    }), encoding="utf-8")

    return root


@pytest.fixture
def sample_neuron():
    """Return a well-formed neuron content string."""
    return (
        "## test-neuron [A/H] Test Neuron\n"
        "This is a test neuron with valid content.\n"
        "It has multiple lines of meaningful text.\n"
        "Status is active and high relevance.\n"
        "→refs: other-neuron\n"
        "→tags: #test, #fixture\n"
        "| 2026-04-15\n"
    )


@pytest.fixture
def sample_enabler():
    """Return a well-formed enabler content string."""
    return (
        "# AGENT Test Agent\n"
        "summary: A test enabler for unit testing\n"
        "**Trigger:** When tests are needed\n"
        "## Instructions\nDo the testing.\n"
    )


@pytest.fixture
def neuron_entry(sample_neuron, tmp_dara):
    """Return a neuron entry dict (as compile.py uses internally)."""
    fp = tmp_dara / "VAULT" / "NEURONS" / "test-neuron.md"
    fp.write_text(sample_neuron, encoding="utf-8")
    return {
        "filename": "test-neuron",
        "filepath": fp,
        "content": sample_neuron,
        "category": "NEURONS",
        "chars": len(sample_neuron),
    }


@pytest.fixture
def enabler_entry(sample_enabler, tmp_dara):
    """Return an enabler entry dict."""
    fp = tmp_dara / "VAULT" / "ENABLERS" / "agent-test.md"
    fp.write_text(sample_enabler, encoding="utf-8")
    return {
        "filename": "agent-test",
        "filepath": fp,
        "content": sample_enabler,
        "category": "ENABLERS",
        "chars": len(sample_enabler),
    }
