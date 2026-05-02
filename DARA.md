# DARA — [Your Name]'s Artificial Brain
**Version:** 1.0 | **Updated:** 2026-05-02 | **Owner:** [Your Name] ([your-email])

---

## WHAT IS DARA

DARA is a persistent AI memory system. You — the AI reading this — gain memory across conversations by following this protocol. No human navigates these files. You manage it; the user owns it.

## DESIGN PRINCIPLES

1. **Rules control, not roles.** Any AI reads/writes if it follows this protocol. Claude, GPT, DeepSeek, n8n — same rules for all.
2. **Errors self-heal.** ~10% imprecision OK. Next AI that spots an error fixes it. Don't freeze — act and log.
3. **Scales infinitely.** 25 memories or 2,000 — structure doesn't change.

---

## STRUCTURE

```
DARA/
├── DARA.md              ← YOU ARE HERE. Read fully before anything.
├── VAULT/               ← GATE 1: Source of truth (write here)
│   ├── NEURONS/         ← Project & context knowledge
│   ├── ENABLERS/        ← Agents, tools, credentials, workflows
│   ├── INBOX/           ← Feedback channel for the Architect
│   └── BACKUP/          ← BRAIN.md snapshots + SYSTEM/ (W3(b) file copies)
│       └── SYSTEM/      ← Librarian-maintained backups of protected files
├── LIBRARY/             ← GATE 2: Compiled brain (read here)
│   └── BRAIN.md         ← Compressed, read-optimized, single file
└── SYSTEM/               Compiler and internal tooling
    ├── compile.py        Compiler v3.1: VAULT → validate → auto-fix → compress → BRAIN.md
    └── watcher.py        Auto-compiler: monitors VAULT/ every 5s, debounces 3s, runs compile.py
```

---

## ROUTING: WHERE DO YOU GO?

**You need to READ the user's context?**
→ Go to `LIBRARY/BRAIN.md`. It contains everything compressed and optimized.

**You need to WRITE new information?**
→ Go to `VAULT/`. Follow the Writing Protocol below. After writing, run `compile.py`.

**You spotted something wrong or have a suggestion?**
→ Drop a feedback file in `VAULT/INBOX/`. See INBOX protocol below.

**the user says "run the librarian"?**
→ Read `VAULT/ENABLERS/agent-librarian.md` and execute it.

**the user says "activate architect mode" or "open the golden door"?**
→ Read `VAULT/ENABLERS/agent-architect.md` and execute it. Only if the user explicitly activates it.

---

## ENCODING LANGUAGE

All files in VAULT/ use compressed notation. Learn these conventions:

### Format rules
- **Dates:** YYYY-MM-DD (2026-04-24)
- **Money:** €NNK (thousands), €NNM (millions), €NN (exact)
- **Status:** `[A]` active, `[C]` completed, `[P]` paused
- **Relevance:** `[H]` high, `[M]` medium, `[L]` low
- **People:** First.Last(role) → `Alice.M(Marketing)`, `Bob.S(Engineering)`
- **Connections:** `→refs:` followed by filenames → `→refs: project-alpha, profile-technical`
- **Consensus flags:** `→flag: "reason" | N/3 | AI1(date), AI2(date)` — content removal vote (see W11)
- **Credentials:** `[CRED:name]` placeholder, full value in ENABLERS/credentials.md
- **Tags:** `#tag1 #tag2` at end of section header
- **Word count:** `~NNNw` at end of entry
- **Lists:** comma-separated inline, no bullets unless multi-line data
- **URLs:** domain only unless path matters → `example.com` not `https://www.example.com/`
- **Booleans:** ✓/✗

### Section structure in VAULT files
```
## filename [STATUS/RELEVANCE]
Compressed content using encoding rules above.
→refs: connected-file-1, connected-file-2
→tags: #tag1 #tag2
~NNNw | YYYY-MM-DD
```

---

## READING MODES

**Standard Mode** (Claude Desktop, Claude Cowork, and models with reliable tool calls):
1. Read full `LIBRARY/BRAIN.md` at session start
2. Open specific VAULT files via `→detail:` pointers as needed
3. Chain tool calls freely

**Light Mode** (DeepSeek, TypingMind, models without MCP or with unreliable tool calls):
1. Read `LIBRARY/BRAIN.md` — the full file, which is compact (typically ~900 tokens for a fresh install, scaling up to ~4K+ with heavier use)
2. Do NOT attempt to open VAULT files — all essential context is in the →brain: summaries
3. For writes: one file per operation, compile only at session end (or skip if risky)
4. If a tool call fails, do NOT retry more than once — log and continue

**Which mode to use:** The AI should self-select based on its platform. The compiler adds a `READING MODE` indicator at the top of BRAIN.md. See W15 for the formal rule.

---

## GATE 1: WRITING PROTOCOL

When you need to add or update information in DARA:

**W1 — Check first.** Open LIBRARY/BRAIN.md and scan the **INDEX** section (top of file). It lists every neuron grouped by domain. If the topic already exists there, update that VAULT file. If no match in the INDEX, create a new neuron. Only read the full BRAIN.md content if you need more detail about an existing entry.


**W1(b) — External-session writes.** When writing to VAULT from an external session (Cowork, API, plugin, automation, or any context where you have not yet read DARA.md): (1) read DARA.md fully before the first VAULT write — no exceptions for "quick updates"; (2) verify the target file follows the encoding key (## header, →refs, →tags, ~NNNw | YYYY-MM-DD); (3) if you cannot read DARA.md (no filesystem access, sandboxed), draft the content as a feedback file in VAULT/INBOX/ for the Librarian to merge — do NOT write to NEURONS/ or ENABLERS/ blindly. "Go fast" is not a valid reason to skip protocol.
**W2 — Fix errors.** If you spot incorrect data while reading, fix it in VAULT/ and log it. Self-healing.

**W3 - File protection.**
a) Never delete files without explicit instruction from the user.
b) PROTECTED FILES (Architect-only): `DARA.md`, `compile.py`, `agent-architect.md`, `watcher.py`. Standard agents cannot modify these.
c) For all other VAULT files: any AI can fix errors (W2), but structural changes (merge, split, delete) require permission.
**W4 — Update existing** when: new info on same topic, data changed, error detected, the user provides new info. (Applies to NEURONS and non-protected ENABLERS only.)

**W5 — Create new** ONLY when: topic doesn't fit anywhere existing, the user says "save/remember this", genuinely new project/area. Creating new `agent-*.md` files requires the user's explicit instruction.

**W6 — After any write:** regenerate BRAIN.md. If `watcher.py` is running (default on the user's machine), compilation happens automatically within ~8 seconds of your last write — no action needed. If watcher is not running, run `compile.py` manually. If you can't run Python (e.g., DeepSeek/TypingMind), note in the changelog that compilation is pending — the watcher will handle it next time it starts. After compiling, always confirm to the user with a short status:
- DARA updated
- [N] entries | ~[N] tokens | [N] fixes | [N] warnings
- Status: all systems operational — or list issues and ask: "Want me to activate Architect mode to review this?"

**W7 — Log everything** in `VAULT/changelog.md`. **Append only — never overwrite existing entries.** Format per entry:
`- AI Model (Platform) | file | what changed | ops:N | retry:Y/N | ~NNKt`
Where: `AI Model (Platform)` identifies who wrote (e.g., `Claude Opus (Cowork)`, `DeepSeek V3 (TypingMind)`), `ops` = number of tool calls used for this DARA update (read+write+compile+sync), `retry` = Y if something failed and had to be redone, `~NNKt` = estimated tokens consumed for the DARA operation (rough: count your tool calls × 4K average, or use platform metrics if available). Example:
`- Claude Opus (Cowork) | project-alpha.md | UPDATED — added quick hits | ops:4 | retry:N | ~16Kt`

**W8 — File naming:** kebab-case.
- NEURONS: `[business]-[topic].md` → `tffc-extras-ps26.md`
- ENABLERS: `agent-[name].md`, `credentials.md`, `tools-[platform].md`

**W9 — Session closing trigger.** Before ending a conversation where significant work was done on a project, check: "Is there anything from this session that DARA should remember?" If yes, create or update the relevant neuron in VAULT, compile, and log. This applies to ALL AI sessions, not just memory-focused ones. A 4-hour coding session is just as worthy of a VAULT update as a memory review session.

**W10 — Live memory detection (Standard Mode only).** During a conversation, if you detect information that **significantly** changes what DARA knows — new project, price change, business decision, new contact, strategic shift — flag it immediately: "This isn't in DARA / this contradicts DARA. Should I update it?" Do NOT interrupt for minor details, formatting, or trivial data. Only flag changes that would affect how other AIs understand the user's context. If the user confirms, write to VAULT immediately (don't wait for session end). This rule does NOT apply in Light Mode — unreliable tool calls make mid-conversation writes risky.

**W11 — Write lean, review everything.** When updating a neuron (W4), you are not just adding — you are **editing the whole entry**. Before saving:
1. **Review all existing content** in that neuron. Is anything now redundant, obsolete, or superseded by what you're adding? Remove it directly — no permission needed for clear cases.
2. **Follow encoding strictly.** Use compressed notation (€NNK, First.Last(role), comma-separated inline, no bullets unless multi-line data). No prose where data suffices.
3. **If you're unsure whether content still adds value**, don't delete it and don't escalate to INBOX. Instead, add a **consensus flag** directly below the questionable content:
`→flag: "reason this may not add value" | 1/3 | YourName.Platform(YYYY-MM-DD)`
When another AI reads the neuron and **independently agrees** with the flag, it adds its vote:
`→flag: "reason" | 2/3 | AI1.Platform(date), AI2.Platform(date)`
At **3/3 votes**, the next AI that sees it removes the flagged content AND the flag line, and logs the removal in changelog. No Architect needed.
Rules: each AI votes only once per flag. Don't vote on your own flags. If you **disagree** with a flag, remove the flag line (reset it) and log why. Flags older than 30 days with <3 votes should be removed (the consensus didn't form — the content stays).
4. **After compiling, check the delta report.** If the compiler reports significant growth (+20% or more on any entry), review whether compression was possible. The goal: every write leaves the neuron leaner or equal, never bloated.
5. **Only use INBOX for structural/architectural issues** — things that affect DARA's design, protocol, or cross-neuron consistency. Content-level cleanup should resolve itself through flags (step 3). The Architect handles the 1%, not the 99%.

**W12 — Verify writes.** After any file edit (especially files >100 lines or containing special characters like →, €, ñ), verify the write succeeded:
1. Check the file's last lines (`tail`) and line count (`wc -l`) via shell — do NOT rely on the Read tool cache, which may show stale content.
2. If truncation is detected (file shorter than expected, content cut mid-line), restore immediately: use `git checkout -- filename` if git is available, or rewrite the file via bash.
3. For files >300 lines with special characters, prefer writing via bash (`cat > file << 'EOF'`) over the Edit tool, which has a known truncation bug on long files.
4. After restoring, recompile and log the incident in changelog.

**W13 — Structure for BRAIN efficiency.** The compiler compresses VAULT into BRAIN.md. Help it produce a leaner output:
1. **Neurons: summary first.** Start every neuron entry with a one-line summary (what/status/key-fact). Details, history, and specifics below. Example first line: `project-alpha | Website redesign — launched 2026-03, monitoring performance` then details on subsequent lines.
2. **Enablers = one-liners in BRAIN.** The compiler renders each enabler as a single summary line in BRAIN.md with a `→detail:` pointer to the full VAULT file. Write enablers normally in VAULT — the AI reads the full file only when it needs to execute that agent/tool.
3. **Data, not prose.** Prefer `Revenue: €340K (+12% YoY)` over "The revenue reached three hundred and forty thousand euros, representing a twelve percent increase." Every word in BRAIN costs tokens.
4. **Preserve →brain: lines.** If a neuron starts with `→brain:`, it is a compiler summary. When editing neurons: keep this line, update it if your changes affect the summary, or delete it (the compiler will fall back to full content).

**W14 — Enabler summaries.** Every enabler file MUST start with a `summary:` line (first line of content). This line is used by the compiler to generate the one-liner in BRAIN.md. Format: `summary: What this agent/tool does in one sentence`. If missing, the compiler uses auto-detection (less accurate) and emits a WARNING.

**W15 — Platform-aware mode selection.** When reading BRAIN.md:
- **Standard Mode** (Claude Desktop, Claude Cowork): Full BRAIN.md + follow detail: pointers as needed.
- **Light Mode** (DeepSeek, TypingMind, models without MCP): Read BRAIN.md only. Do NOT attempt to open VAULT files. All essential context is in the brain: summaries.
The compiler adds a `READING MODE` indicator at the top of BRAIN.md. The AI should auto-detect its platform and select the appropriate mode.

---

## SIGNAL SYSTEM

When an AI reads a VAULT entry and something doesn't feel right — data seems outdated, contradicts another source, or doesn't match reality — it must act:

**Don't ask the user. Fix or flag.**

1. **If you're certain it's wrong:** Fix it directly (W2). Log the fix.
2. **If you're unsure:** Leave a feedback file in VAULT/INBOX/ explaining what seems off, with evidence.
3. **If the entry has a feedback file already pending:** Treat that entry with caution — the data may be unreliable.

The Architect processes INBOX items periodically. The compiler reports pending INBOX items at every compilation so nothing gets forgotten.

---

## INBOX PROTOCOL

`VAULT/INBOX/` is the feedback channel. Any AI can write here. Only the Architect processes it.

**When to use INBOX:**
- You spotted an inconsistency but aren't sure how to fix it
- You have a suggestion for improving DARA's structure or protocol
- A reader reported issues with BRAIN.md accuracy
- You detected a pattern across neurons that needs attention

**File format:** `feedback-YYYY-MM-DD-topic.md`
```
## FEEDBACK: [short title]
**From:** [AI name/session]
**Date:** YYYY-MM-DD
**Type:** BUG | SUGGESTION | INCONSISTENCY | STALE
**Severity:** CRITICAL | IMPORTANT | MINOR

### What happened
[Description]

### Evidence
[Files, data, specifics]

### Suggested fix
[If known]
```

**What the Architect does:**
1. Reads all pending items
2. Fixes in VAULT, updates Constitution, or dismisses with reason
3. Deletes the feedback file after processing
4. Logs action in changelog.md

---

## AUTO-MEMORY COEXISTENCE

Some AI platforms (like Claude Cowork) maintain their own session memory (e.g., `/mnt/.auto-memory/`). This creates two sources of truth. The policy is:

- **Auto-memory = session notes.** Ephemeral, platform-specific, useful during the session.
- **DARA = consolidated truth.** Permanent, cross-platform, the single source of truth.

When closing a session, apply W9: anything important from session notes should be written to DARA VAULT before the session ends. Don't duplicate — consolidate.
