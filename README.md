<div align="center">

<img src="assets/eidara-mark.svg" width="64" height="64" alt="EIDARA logo">
<br>
<h1>EIDARA</h1>

**Your AI remembers everything between conversations.**

You use Claude, ChatGPT, Gemini, DeepSeek. Every session starts from zero.
<br>
DARA is a file they all share — write once, read everywhere.
<br>
Open source. Local. No cloud required.

<p>
  <a href="https://github.com/jrotllant/eidara/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+"></a>
  <a href="https://github.com/jrotllant/eidara/releases"><img src="https://img.shields.io/badge/release-v1.0-brightgreen" alt="Release v1.0"></a>
</p>

</div>

---

## What is this

DARA is a **compiled persistent memory system for AI**. Any AI writes structured markdown files. A compiler produces a single optimized file (`BRAIN.md`) that any AI reads cold — instant full context, every session.

**No database. No Docker. No API keys. No cloud.** Markdown + Python stdlib.

## How it works

```
┌──────────┐         ┌──────────┐         ┌──────────┐
│  WRITE   │         │ COMPILE  │         │   READ   │
│          │────────▶│          │────────▶│          │
│  VAULT/  │         │compile.py│         │ BRAIN.md │
└──────────┘         └──────────┘         └──────────┘
Any AI writes.       10-step pipeline.    Any AI reads.
Any platform.        Validates. Dedupes.  One file. Current.
                     Auto-fixes. Locks.   SHA256 verified.
```

1. AIs write memories as markdown files in `VAULT/` following 15 rules (the "constitution")
2. `compile.py` validates, deduplicates, compresses, checksums, and auto-commits to git
3. Any AI reads `BRAIN.md` at session start — one file, always current, SHA256-verified

**Write anywhere. Compile once. Read everywhere.**

### Two actions

**→ Consult DARA.** Open any AI with file access and say:
   *"Check DARA for full context on project X."*
   Seconds later, the AI has full context.

**→ Write to DARA.** When something new happens, say:
   *"Update your context in DARA."*
   The AI writes it, the watcher compiles it, next session it's there.

*That's it. Day-to-day, you never touch files, folders, or terminals.*

## Quick start

```bash
git clone https://github.com/jrotllant/eidara.git
```

Give the `INSTALL - Give this file to Claude or any AI.md` file to any AI (Claude, TypingMind, or any LLM with filesystem access). It handles everything: prerequisites, personalization, first compile, auto-watcher.

**That's it.** Your AI does the setup.

**Want to see DARA fully populated before personalizing?**
Download the **Sample Vault** from [Releases](https://github.com/jrotllant/eidara/releases) (`eidara-sample-vault-v1.0.zip`). It contains a fictional indie maker's full DARA (17 neurons, 6 enablers, populated changelog, INBOX feedback) — drop it on your Desktop, run `python compile.py`, and explore the system in action in 2 minutes. Wipe it when you're ready to start your own.

## Why DARA?

### It has a constitution
15 writing rules (W1–W15) in `DARA.md`. Any AI that reads the file knows how to interact. No training, no fine-tuning — the rules ARE the onboarding.

### It compiles, not concatenates
A 10-step pipeline: validates, deduplicates, auto-fixes, compresses, checksums, git-commits. Nobody else compiles their AI memory.

### Model-agnostic by design
Claude, DeepSeek, or any LLM with filesystem access — anyone writes if they follow the protocol. **Tested across 4 models with 52 autonomous tests. Average score: 92.6%.**

### Self-healing
If certain → fix it. If uncertain → flag it. Every AI leaves the system slightly better than it found it. Consensus flags (3/3 vote) protect against unilateral content changes.

### Zero infrastructure
Python 3.10+ and Git. That's it. Runs on any machine. Your files never leave your computer. No telemetry, no accounts, no cloud.

### Two reading modes
**Standard** (full VAULT access) for Claude/GPT with tools. **Light** (BRAIN.md only) for DeepSeek, ChatGPT web, or models without filesystem access.

## Test results

52 autonomous tests across 7 evaluation blocks. 4 different AI models each ran the full battery independently.

| Model | Platform | Score | % |
|-------|----------|-------|---|
| Opus 4.6 | Claude Cowork | 670/700 | **95.7%** |
| Sonnet 4.6 | Claude Cowork | 652/700 | **93.1%** |
| DeepSeek V4 | TypingMind (no shell) | 650/700 | **92.9%** |
| Opus 4.7 | Claude Cowork | 613/700 | **87.6%** |

**Average: 92.6% · Zero system failures · Zero data corruption**

We publish cross-model test results because it has to work with your AI — not just ours.

## Repository structure

```
eidara/
├── DARA.md                 # Constitution (15 rules — start here)
├── INSTALL - Give this file to Claude or any AI.md  # AI-guided installation
├── CONTRIBUTING.md         # How to contribute
├── LICENSE                  # MIT
├── .gitignore
├── SYSTEM/
│   ├── compile.py          # The compiler (v3.1, ~1170 lines, stdlib only)
│   ├── validators.py       # 16 validation functions (322 lines)
│   ├── watcher.py          # Auto-compile on file changes
│   ├── config.json         # Externalized settings
│   ├── RECOVERY.md         # 6 emergency procedures
│   └── tests/              # 103 pytest tests (100% pass)
├── VAULT/
│   ├── NEURONS/            # Your knowledge (one topic per file)
│   ├── ENABLERS/           # Agents, tools, credentials
│   ├── INBOX/              # AI feedback queue
│   └── BACKUP/             # Timestamped snapshots
└── LIBRARY/
    └── BRAIN.md            # Compiled output (auto-generated, do not edit)
```

## Who is this for

- You use more than one AI platform (Claude, DeepSeek, GPT...)
- You're tired of pasting context manually every session
- You manage multiple projects and your AIs should know them all
- You care about privacy (no cloud, no telemetry)
- You can run a Python script (or know someone who can)

**If 2 or more describe you, EIDARA will save you time starting today.**

## Roadmap

| When | What | Why it matters |
|------|------|----------------|
| **v1.0** | GitHub release + eidara.dev | The launch |
| **Jul 2026** | Semantic search (`--with-index`, SQLite) | Find info without remembering exact words |
| **Sep 2026** | MCP Server | Connect DARA to Cursor, Cline, Claude Desktop |
| **Q4 2026** | Web dashboard + consensus audit trail | Who wrote what, when. Full traceability. |
| **2027** | Agent marketplace + optional cloud sync | Community agents. Cloud never required. |

Stay updated at [eidara.dev](https://eidara.dev) — each release ships as an `UPDATE.md` file. Give it to your AI, it applies the changes automatically.

## FAQ

**Do I need to know Python?**
No. You need Python installed (the INSTALL guide helps). You never write Python code — the compiler is a black box.

**Does it work with my AI model?**
If it can read a markdown file and follow written instructions, it works. We've tested Claude (Opus 4.6, Sonnet 4.6) and DeepSeek V4. The protocol is model-agnostic by design.

**How much context does BRAIN.md use?**
Starts at ~900 tokens with the starter vault (2 neurons, 4 enablers). Scales efficiently — a typical setup with 20+ entries fits in ~3,500 tokens. Budget warnings at 50K/100K/150K. Designed to fit any modern context window.

**What if I break something?**
Git tracks every change. RECOVERY.md has 6 emergency scenarios. The compiler creates timestamped backups automatically.

**Is my data private?**
100%. Your files never leave your machine. No telemetry. No cloud sync. No analytics.

## License

MIT — see [LICENSE](LICENSE).

## Author

**Javier Rotllant Miras** — Former Bain & Company. Built EIDARA because he needed it.

- Web: [eidara.dev](https://eidara.dev)
- GitHub: [github.com/jrotllant](https://github.com/jrotllant)
- Email: javier@eidara.dev

---

<div align="center">
  <sub>Built with markdown, Python, and stubbornness.</sub>
</div>
