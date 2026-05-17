# EIDARA — Persistent AI Memory System

EIDARA is a file-based persistent memory system that gives any AI a durable, structured long-term memory. No cloud, no servers, no database — just markdown files and a Python compiler.

## How it works

1. **VAULT/** stores source-of-truth memories as markdown files (neurons = data, enablers = agents/configs)
2. **compile.py** reads VAULT, compresses, deduplicates, and generates a read-optimized **BRAIN.md**
3. Any AI reads BRAIN.md at session start and instantly has full context

The system is designed so that multiple AIs (Claude, DeepSeek, GPT, etc.) can read and write to the same memory, with built-in conflict resolution, tamper detection, and self-healing.

## Key features

- **Three-layer compression:** W-rules for encoding, strip_noise() for PII removal, brain summaries for density. A typical BRAIN.md is ~3.7K tokens — small enough for any context window.
- **Self-healing:** Built-in Librarian agent runs health checks, fixes broken references, compresses bloated entries, and maintains system hygiene automatically.
- **Platform-agnostic:** Works with any AI that can read files. Light Mode for platforms with unreliable tool calls. Standard Mode for full access.
- **Git-native:** Auto-commits on compile, tamper detection via checksums, full version history.
- **Constitution (DARA.md):** 15 rules (W1-W15) that govern how any AI interacts with the memory. No AI can modify the rules without going through the Architect protocol.

## Quick start

Open `INSTALL - Give this file to Claude or any AI.md` (in the root folder) and hand it to any AI assistant — it will guide you through the 11 setup steps. If you prefer the manual route, see the **Quick Start** section at the top of that file (works for users comfortable with Python, Git, and the terminal).

## Structure

```
EIDARA/
  DARA.md              # Constitution — the rules (W1–W15)
  INSTALL - Give this file to Claude or any AI.md
  LIBRARY/
    BRAIN.md           # Compiled output (auto-generated, do not edit — tamper-checked)
  VAULT/
    NEURONS/           # Data memories (projects, profiles, configs)
    ENABLERS/          # Agent definitions and system configs
    BACKUP/            # Auto-backups of BRAIN.md + protected SYSTEM/ files
    INBOX/             # Feedback from AIs for review
    TRASH/             # Soft-deleted archived entries (auto-purged after 120 days)
    changelog.md       # Append-only change log (W7 format)
  SYSTEM/
    compile.py         # The compiler (v3.1)
    validators.py      # Validation, fixing, and check functions
    watcher.py         # Auto-compiler — monitors VAULT/ and recompiles on save
    config.json        # Externalized constants (backups, staleness, thresholds)
    health.json        # Last-compile metrics and alerts (auto-written)
    RECOVERY.md        # Emergency procedures
    credentials-template.md  # Copy to VAULT/ENABLERS/credentials.md and fill in your keys
    tests/             # pytest suite (compile + validators)
```

## Personal vs. public version

This is a DARA starter instance. VAULT/NEURONS/ contains example neurons to help you get started. Replace them with your own knowledge.

## License

MIT — see [LICENSE](LICENSE).



---

**Created by [Javier Rotllant Miras](https://www.eidara.dev)** | Licensed under MIT | [www.eidara.dev](https://www.eidara.dev)
