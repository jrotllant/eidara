# EIDARA - AI-Guided Installation
> **Created by Javier Rotllant Miras** | Open-source persistent memory for AI
> **Version 2.0** (2026-05-17) — adds Librarian self-trigger, missing-summary auto-push, W3(b) integrity check, FUSE caveat. See `PROJECT/UPDATE_v1_to_v2.md` if upgrading.

> **You are an AI assistant.** The user has given you this file so you can help them install EIDARA (a persistent memory system for AI). Follow these steps carefully, one at a time. Be friendly, explain what you are doing, and never skip a step.
>
> **IMPORTANT:** You need filesystem access to complete this installation. If you cannot read and write files, tell the user now and guide them through each step manually — tell them what commands to type and what output to expect.
>
> **If something goes wrong at any step,** check the **Troubleshooting** section at the end of this file, or read `SYSTEM/RECOVERY.md` for detailed recovery procedures.
>
> **Accessibility note:** This document uses `## STEP N` markdown headings for navigation. Status indicators are written as `[WARNING]`, `[NOTE]`, `[NEW]` (not as emoji). Code blocks are clearly marked with triple backticks. Tested with screen readers.

---

## BEFORE YOU START

> **[WARNING — Single-user system]** EIDARA is designed for **one person per installation**. Each person on the team installs their own copy of EIDARA. If you are setting this up for a team, stop and read the **Important Notes** section before continuing. (A multi-user mode is planned for a future release.)

### What is a terminal?

A terminal is a window where you type text commands to control your computer. It looks like a simple text window — black on Windows, white on macOS. You only need to type what the AI tells you.

**How to open a terminal:**

**Windows:**
1. Press the **Windows key** on your keyboard
2. Type `cmd` and press **Enter**
3. A black window opens — this is the terminal (also called Command Prompt)
4. Leave it open. You will type commands here.

**macOS:**
1. Press **Cmd + Space** to open Spotlight Search
2. Type `terminal` and press **Enter**
3. A white window opens — this is the terminal
4. Leave it open. You will type commands here.
5. If macOS says a file is "not from an identified developer," go to **System Settings > Privacy & Security** and click **Allow Anyway**.

**Linux:**
1. Press **Ctrl + Alt + T** (on most systems)
2. A terminal window opens
3. Leave it open. You will type commands here.

**Chromebook:**
1. Go to **Settings > Advanced > Developers > Linux development environment**
2. Click **Turn on** and follow the setup (takes a few minutes)
3. A Linux terminal opens. Python and Git are usually pre-installed.
4. If Linux is blocked by your school or organization, ask your admin to enable it — EIDARA cannot run without a terminal and Python.


> **Downloaded a ZIP?** You must **extract it first** before continuing. After extracting, check that `DARA.md` is in the root folder, not nested inside another folder. Right-click the ZIP and select "Extract All" (Windows), double-click it (macOS), or run `unzip filename.zip` (Linux/terminal). Do not try to run files from inside the ZIP — you will get "Access denied" errors.

> **Want to learn more about EIDARA first?** Read `PROJECT/README.md` for a full overview.

---

## UPGRADING FROM A PREVIOUS VERSION

If you already have EIDARA v5.x or older:

1. **Your memories are safe.** All your VAULT/ neurons are compatible with v1.0 — no data is lost.
2. Back up your current `SYSTEM/` folder (copy it somewhere safe).
3. Replace `SYSTEM/` and `DARA.md` with the new versions from this download.
4. Run `python3 SYSTEM/compile.py` (Windows: `python SYSTEM\compile.py`).
5. Your BRAIN.md will be rebuilt with all your existing memories.

**What changed:** DARA.md has updated rules, compile.py has new features (checksum protection, better error messages). Your neurons in VAULT/ do not change.

If you are installing EIDARA for the first time, skip this section and continue below.

---

## HOW THIS WORKS

Walk the user through 11 steps. At each step:
1. Explain what you are about to do and why (one sentence)
2. Do it (or ask the user to do it if you cannot)
3. **Check that it worked** before moving on

If something fails, help the user fix it. Never skip ahead. If you cannot fix it, point the user to `SYSTEM/RECOVERY.md`.

---

## QUICK START (experienced users)

If you already know Python, Git, and the terminal, here are the commands. Run them from the EIDARA root folder. **If your path contains spaces**, wrap it in quotes (e.g. `cd "C:\Users\Jose Garcia\Desktop\EIDARA"`).

**macOS / Linux:**
```bash
cd /path/to/your/EIDARA/folder
python3 --version                         # Check Python 3.10+
git init && git add -A && git commit -m "EIDARA v2.0 initial"
# Personalize: open DARA.md and replace [Your Name] with your name (Step 7)
python3 SYSTEM/compile.py                 # First compile
python3 SYSTEM/watcher.py                 # Auto-watcher — keep running
```

**Windows:**
```bash
cd C:\path\to\your\EIDARA\folder
python --version                          # Check Python 3.10+
git init && git add -A && git commit -m "EIDARA v2.0 initial"
REM Personalize: open DARA.md and replace [Your Name] with your name (Step 7)
python SYSTEM\compile.py                  # First compile
python SYSTEM\watcher.py                  # Auto-watcher — keep running
```

After running these, jump to **Step 10** to verify. Everything still missing or unclear? Start from **Step 1** below.

---

## STEP 1 — Welcome

Introduce EIDARA:

*"Welcome! You are about to install EIDARA — a persistent memory system for AI, created by Javier Rotllant Miras. It allows any AI to remember information between conversations. I will guide you through the setup step by step. Let's get started!"*

---

## RESUMING AN INSTALLATION

Already started installing and coming back? Here is what to do:

1. Go to **Step 10 (Verification)** — it checks what is already done and tells you what is missing
2. Run `python3 SYSTEM/compile.py` (Windows: `python SYSTEM\compile.py`) to test the compiler
3. If Step 10 finds something missing, it tells you which step to go back to

Step 10 works even if you have not finished all steps — it checks each item and reports what still needs to be done.

---

## STEP 2 — Detect the environment

Check the operating system:
- **Windows:** `echo %OS%`
- **macOS/Linux:** `uname -s`

Also check the current folder:
- **Windows:** `cd`
- **macOS/Linux:** `pwd`

Tell the user: *"I am checking your system so I know which commands to use."*

Remember the result — you need it for platform-specific commands in every step.

---

## STEP 3 — Python

### What is Python and why do you need it?

Python is a programming language. EIDARA's compiler is written in Python — it reads your memory files and creates a single file (`BRAIN.md`) that the AI can load. EIDARA needs Python 3.10 or higher because the compiler uses features only available in that version. Older versions will fail with syntax errors.

### Check if Python is installed

Run the version check:
- **Windows:** `python --version` (if that fails, try `py -3 --version`)
- **macOS/Linux:** `python3 --version`

**If Python is installed and shows 3.10 or higher:** Tell the user and move on.

**If Python is not installed** (if python.org is blocked by your network, see Troubleshooting > "Corporate network blocks downloads"):
- **Windows:** *"Download Python from https://www.python.org/downloads/ — click the big yellow button. Run the installer. On the FIRST screen, CHECK the box 'Add Python to PATH'. This is important — **if you do NOT check this box, Python will not work and you must reinstall.**"* Alternative: `winget install Python.Python.3.12` or `choco install python` if available.
- **macOS:** *"Run `brew install python` if you have Homebrew. No Homebrew? Install it first: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` then run `brew install python`."*
- **Linux:** *"Run `sudo apt install python3` (Ubuntu/Debian) or `sudo dnf install python3` (Fedora)."*
- **Chromebook:** Python is usually pre-installed in the Linux environment. Run `python3 --version` to check.

**If Python is installed but the version is too old (below 3.10):** (also see Troubleshooting > "Compiler shows 'SyntaxError' or 'AttributeError'" — these errors usually mean an old Python version is being picked up by default)
- **Windows:** Download the latest installer from python.org and run it. A newer version installs alongside the old one safely. After installing, try `py -3 --version` — the `py` launcher selects the newest version automatically.
- **macOS:** `brew upgrade python`. Note: macOS Monterey/Ventura ships with Python 3.9 pre-installed — that is NOT enough; install a newer version via Homebrew.
- **Linux:** Use your package manager to install the latest version.

### I have multiple Python versions (pyenv, conda, multiple installers)

Pick the command that matches your setup. Run them BEFORE running `compile.py`:

| Setup | Command | What it does |
|---|---|---|
| **Windows py launcher** | `py -3.10 --version` then `py -3.10 SYSTEM\compile.py` | Selects Python 3.10 explicitly |
| **conda** | `conda create -n dara python=3.12 && conda activate dara` | Creates and activates a dedicated environment |
| **pyenv** | `pyenv local 3.10.12` (run inside EIDARA folder) | Pins this folder to Python 3.10.12 |
| **Direct path** | `python3.10 SYSTEM/compile.py` | Bypasses `python3` ambiguity |
| **Verify which is active** | `python3 --version && which python3` (Linux/Mac) or `where python` (Windows) | Shows which Python the OS will pick |

If you don't know which setup you have, run `python3 --version`. If it says 3.10 or higher, you're fine — proceed.

**After installing, verify:**
- Run the version command again. You should see `Python 3.10.x` or higher.
- If you see "command not found" or the old version, close the terminal, open a new one, and try again. On Windows, if it still fails, reinstall and check "Add to PATH".

**Wait for confirmation before continuing.**

---

## STEP 4 — Git

Run: `git --version`

**If installed:** Tell the user and move on.

**If not installed:**
- **Windows:** *"Download from https://git-scm.com/download/win — use all default options."* Alternative: `winget install Git.Git`
- **macOS:** *"Run `xcode-select --install` — a dialog will appear. Click Install and wait about 5-10 minutes."*
- **Linux:** *"Run `sudo apt install git` (Ubuntu/Debian) or `sudo dnf install git` (Fedora)."*

**Why Git?** Git saves versions of your files so you can undo any change. Without Git you lose:
- **Version history** — you cannot undo changes or go back to a previous state
- **File protection** — you cannot detect if a file was changed by mistake
- **Auto-save points** — no automatic snapshots after each compile

DARA works without Git, but these protections are valuable. If the user declines, warn them and continue. Suggest: *"If you skip Git, consider manually copying your VAULT/ folder to a safe place from time to time as a backup."*

**Wait for confirmation before continuing.**

---

## STEP 5 — Locate the folder

Find the folder that contains this file. It should have these contents:

The root folder (which may be called "EIDARA" or another name) contains: the file `DARA.md` (the constitution and system rules), this INSTALL file, and four subfolders — `LIBRARY/` (where the compiled BRAIN.md goes), `PROJECT/` (README, LICENSE, CONTRIBUTING), `SYSTEM/` (the compiler, watcher, tests, and recovery guide), and `VAULT/` (your memory files, organized into ENABLERS, NEURONS, INBOX, BACKUP, and TRASH).

This folder can have any name, and paths with spaces or special characters are fine. If your path has spaces, use quotes: `cd "C:\Users\Jose Garcia\Desktop\EIDARA"` (Windows) or `cd "/Users/Jose Garcia/EIDARA"` (macOS/Linux).

The root folder should contain — in plain words: two files at the top (`DARA.md`, this INSTALL), and four subfolders (`LIBRARY/`, `PROJECT/`, `SYSTEM/`, `VAULT/`).

Detailed list:
- `DARA.md` — constitution and system rules
- `INSTALL - Give this file to Claude or any AI.md` — this file
- `LIBRARY/` — compiled output (BRAIN.md goes here)
- `PROJECT/` — project documentation (README, LICENSE, CONTRIBUTING)
- `SYSTEM/` — compiler (compile.py, validators.py), watcher (watcher.py), tests, and recovery guide (RECOVERY.md)
- `VAULT/` — your memory files, with subfolders: ENABLERS (AI agents), NEURONS (your notes), INBOX (quick-capture), BACKUP (automatic backups), and TRASH (soft-delete, auto-purged after 120 days)

**Check for problems:**
- If anything is missing, tell the user exactly what and stop.
- If the structure is `eidara-main/eidara-main/DARA.md` (double-nested), the ZIP was extracted wrong. Move the contents of the inner folder up one level and delete the empty inner folder.
- If the folder is inside Downloads or a temporary location: *"I recommend moving this folder to your Desktop. It makes loading BRAIN.md into conversations faster, and avoids accidental deletion."*

**Note:** `compile.py` resolves paths relative to its own location, so it works no matter what folder you run it from. However, Git commands must be run from the root folder.

Store the full path — you need it for the remaining steps.

---

## STEP 6 — Git setup

Navigate to the root folder and run:

```bash
cd /path/to/your/EIDARA/folder
git init
git add -A
git commit -m "EIDARA v2.0 - initial install"
```

Tell the user: *"Done. Your first save point is created. Starting now, every change is recorded."*

**If Git is not installed** (skipped Step 4), skip this step and warn: *"Without Git, if a file gets corrupted or the AI changes something by mistake, you cannot restore it. Consider installing Git later."*

---

## STEP 7 — Personalize

Open `DARA.md` in the root folder. Find these lines near the top:

```
# DARA — [Your Name]'s Artificial Brain
**Version:** 1.0 | **Updated:** [date] | **Owner:** [Your Name] ([your-email])
```

Ask: *"What is your name? And optionally, your email?"*

Replace `[Your Name]` with their name, `[your-email]` with their email (or remove the email part if they prefer). Update the date to today.

> **[WARNING — DARA.md is the system Constitution.** Only change name, email, and date. **Do not modify any other line.** Anything else triggers a `W3(b) ALERT` on every compile and may break the protocol.
>
> **If you accidentally modified more than name/email/date:** restore with `git checkout -- DARA.md` (works only if you completed Step 6 — Git setup).

The compiler checks DARA.md using a SHA-256 checksum (a digital fingerprint of the file). If you change anything other than your name, email, or the date, you will see a `W3(b) ALERT` warning on every compile.

---

## STEP 8 — First compile

Run the compiler:
- **Windows:** `python SYSTEM\compile.py`
- **macOS/Linux:** `python3 SYSTEM/compile.py`

**Expected output:**
- `BRAIN.md compiled!` at the end
- `Entries: X` (should be several entries)
- `Warnings: 0` (a few warnings on first run are normal)
- `Errors: 0`

**If you see errors:** Read the error message — it usually says what is wrong. Common fixes:
- `SyntaxError` or `AttributeError` — you are running a Python version below 3.10. Any error mentioning "invalid syntax" or "has no attribute" usually means your Python is too old. Check Step 3.
- `ModuleNotFoundError` — wrong Python version. Try `python3` instead of `python`.
- `FileNotFoundError: VAULT/` — you are in the wrong folder. Run `cd /path/to/EIDARA` first. (Note: compile.py usually handles this automatically, but Git commands need the correct folder.)
- `PermissionError` — a file is locked by another program, or you are running from inside a ZIP. Close editors and make sure you extracted the ZIP first.
- If Windows Defender blocks the script, see Troubleshooting > "Antivirus (Windows Defender) blocks Python scripts".

Tell the user: *"Your first compile is done! BRAIN.md is now in the LIBRARY folder — this is your AI's compiled memory."*

---

## STEP 9 — Auto-watcher

The watcher monitors VAULT/ and recompiles BRAIN.md automatically every time you save a file. Without it, you would have to run `compile.py` manually after every edit.

**Start it:**
- **Windows:** `python SYSTEM\watcher.py`
- **macOS/Linux:** `python3 SYSTEM/watcher.py`

You should see: `DARA Watcher v1.1 started` and `Initial snapshot: X vault files`. The watcher runs continuously — leave this terminal (or SSH session) open.

**Auto-start on boot:**

**Windows:**
1. Run `SYSTEM\SETUP_AUTOSTART.bat`
2. This creates a startup shortcut with the DARA icon — the watcher launches silently when your computer starts.

**macOS:**
Add `nohup python3 /full/path/to/SYSTEM/watcher.py >/dev/null 2>&1 &` to your shell profile (`~/.zshrc` or `~/.bash_profile`). The `nohup` keeps the watcher running after you close the terminal. Alternatively, use `launchctl` for a true background daemon (advanced).

**Linux (systemd — recommended for servers):**
Create a service file at `/etc/systemd/system/dara-watcher.service`:
```
[Unit]
Description=DARA Watcher — auto-compile BRAIN.md
After=network.target

[Service]
ExecStart=/usr/bin/python3 /full/path/to/SYSTEM/watcher.py
WorkingDirectory=/full/path/to/EIDARA/
Restart=on-failure
User=YOUR_USERNAME

[Install]
WantedBy=multi-user.target
```
Then run: `sudo systemctl enable dara-watcher && sudo systemctl start dara-watcher`

**Linux (quick alternative):** Use `nohup python3 SYSTEM/watcher.py &` to keep the watcher running after you close the terminal, or run it inside `tmux` or `screen`.

Tell the user: *"The auto-watcher is running. Every time you save a file in VAULT/, BRAIN.md updates automatically."*

**If the watcher stops detecting changes** or pauses after errors, see Troubleshooting > "Watcher does not detect changes" and "Watcher halted (`.compile-error`)".

---

## STEP 10 — Verification

Run through this checklist. For each item, run the actual command and report the result. **This step also works for resuming an interrupted installation** — it tells you what is done and what is still missing.

1. **DARA.md personalized:**
   Read the first 5 lines of DARA.md — should show the user's name, not `[Your Name]`.
   *Missing? Go to Step 7.*

2. **BRAIN.md exists and has content:**
   Check file size — should be at least 3,000 characters.
   *Missing? Go to Step 8.*

3. **Compiler works:**
   `python3 SYSTEM/compile.py --stats` (Windows: `python SYSTEM\compile.py --stats`) — should print stats without errors.
   *Errors? Check Step 3 (Python) and Step 8 (compile).*

4. **Neurons exist:**
   List `VAULT/NEURONS/` — should contain `.md` files (at least `example-project.md`).
   *Missing? The download may be incomplete. Re-download from the source.*

5. **Enablers exist:**
   List `VAULT/ENABLERS/` — should contain agent files (e.g., `agent-architect.md`).
   *Missing? Same as above.*

6. **Git initialized** (if applicable):
   Check if `.git/` folder exists in the root.
   *Missing? Go to Step 6, or skip if user chose not to use Git.*

7. **Watcher running:**
   The watcher terminal should show `DARA Watcher v1.1 started`. If not, start it (see Step 9).

**Report to user:**
- All pass: *"Everything is set up correctly. Your DARA system is ready!"*
- Something failed: explain what is wrong, point to the specific step, and help fix it.

---

## STEP 11 — What's next

*"Your DARA installation is complete! Here is how to use it:*

**Create memories:** Add `.md` files to `VAULT/NEURONS/`. Each file is a 'neuron' — one topic, project, person, or idea per file. See `VAULT/NEURONS/example-project.md` for the format.

**Compile:** Run `python3 SYSTEM/compile.py` (Windows: `python SYSTEM\compile.py`) to rebuild BRAIN.md. If the watcher is running, this happens automatically.

**Load your memory:** At the start of any AI conversation, give the AI your `LIBRARY/BRAIN.md`. It will know everything you have stored.

**Key rules:**
- Read `DARA.md` first in any new conversation — it teaches the AI how the memory system works
- Never delete or modify the 5 protected system files: `DARA.md`, `SYSTEM/compile.py`, `SYSTEM/validators.py`, `SYSTEM/watcher.py`, and `VAULT/ENABLERS/agent-architect.md`. Only the Architect (activated by you saying "open the golden door") may modify them
- Use `VAULT/INBOX/` for feedback to the Architect (e.g., `feedback-YYYY-MM-DD-topic.md`) — these are NOT auto-compiled into BRAIN.md; they wait for the Librarian or Architect to process them
- `VAULT/TRASH/` is a soft-delete — files are auto-purged after 120 days
- Read `SYSTEM/RECOVERY.md` if anything goes wrong"*

Then share this message from the creator:

*"A personal note from Javier Rotllant Miras, the creator of EIDARA:*

*I built this because I believe AI should remember the people it works with. I hope it works perfectly for you. If you have questions, ideas, or just want to say hi — reach me at [www.eidara.dev](https://www.eidara.dev) or on the GitHub repository. Welcome to EIDARA!"*

---

## TROUBLESHOOTING

**"python/python3 is not recognized" or "command not found"**
Python is not installed or not in PATH. Go back to Step 3. On Windows, reinstall Python and check "Add Python to PATH". On macOS, try `python3` instead of `python`. After installing, close and reopen the terminal.

**"git is not recognized"**
Git is not installed. Go back to Step 4, or continue without it (DARA works without Git).

**Compiler shows "SyntaxError" or "AttributeError"**
Your Python version is too old. Any error mentioning "invalid syntax" or "has no attribute" usually means you need Python 3.10 or higher. Check your version with `python3 --version` (Windows: `python --version` or `py -3 --version`) and upgrade if needed (see Step 3).

**Compiler shows "FileNotFoundError"**
You are running compile.py from the wrong folder, or the folder structure is incomplete. Navigate to the EIDARA root folder: `cd /path/to/your/EIDARA/folder`. Note: compile.py usually resolves paths automatically, so this error may mean files are missing — check that VAULT/ and its subfolders exist.

**Compiler shows "ModuleNotFoundError"**
Wrong Python version. Try `python3` instead of `python`. If that fails, check `python3 --version` — you need 3.10+.

**Compiler shows "PermissionError" or "Access denied"**
Two common causes: (1) A file is locked by another program — close any editors that have DARA files open and try again. (2) You are running from inside a ZIP file — extract the ZIP first (see "BEFORE YOU START").

**BRAIN.md is empty or missing**
Run `python3 SYSTEM/compile.py` manually. If it still fails, check that `VAULT/NEURONS/` contains at least one `.md` file.

**Watcher does not detect changes**
Make sure the watcher terminal is still running. If it stopped, restart it: `python3 SYSTEM/watcher.py`. Check that you are saving files inside `VAULT/NEURONS/` or `VAULT/ENABLERS/`.

**Double-nested folder after extracting ZIP**
If your structure looks like `eidara-main/eidara-main/DARA.md`, move everything from the inner folder up one level and delete the empty inner folder.

**Antivirus (Windows Defender) blocks Python scripts**
Windows Defender may flag `compile.py` or `watcher.py`. To fix: open **Windows Security > Virus & threat protection > Manage settings > Exclusions > Add exclusion > Folder** and select your EIDARA folder. This tells Defender to trust these files.

**Corporate network blocks downloads**
If your firewall blocks python.org or git-scm.com:
- **Windows:** Try `winget install Python.Python.3.12` or `choco install python` (if available).
- **Proxy:** Set proxy environment variables: `set HTTP_PROXY=http://your-proxy:port` and `set HTTPS_PROXY=http://your-proxy:port` (Windows) or `export HTTP_PROXY=...` (macOS/Linux).
- **Offline:** Download the Python and Git installers on a different computer and transfer them via USB drive.

**Compile shows "W3(b) ALERT" after editing DARA.md**
This means a protected file was modified since the last compile (DARA.md, compile.py, validators.py, watcher.py, or agent-architect.md). If you intentionally edited it (e.g., personalized DARA.md in Step 7), the alert is normal — the next compile refreshes the checksum and it goes away. If you did NOT edit it, restore the original from `VAULT/BACKUP/SYSTEM/` or `git checkout -- <file>`.

**Watcher halted (`.compile-error` exists)**
The watcher pauses compilation after 3 consecutive failures and creates `SYSTEM/.compile-error` as a halt marker. Open the file to see the failure timestamp and the error. Fix the underlying problem (usually a syntax error in a VAULT file or a missing dependency), then delete `SYSTEM/.compile-error` to resume auto-compile.

**Something else went wrong**
Read `SYSTEM/RECOVERY.md` — it has detailed instructions for recovering from most problems.

---

## IMPORTANT NOTES

**Single-user system — team setups.** EIDARA is designed for one person per installation. **For teams**, the recommended pattern is: each member runs their own instance, and shared knowledge is exchanged by copying neuron files between VAULT/NEURONS/ folders. There is no built-in collaboration layer (no shared write, no merge-aware compiler) — adding that contradicts the zero-infrastructure principle. A multi-user mode is on the roadmap but not yet released.

**Glossary reference:** If any term in this file is unclear, check the Glossary below.

---

## GLOSSARY

- **Terminal / Command line:** A window where you type text commands to control your computer. Example: typing `python --version` shows which version of Python you have.
- **Python:** A programming language. EIDARA uses it to compile (combine) your memory files into BRAIN.md. Example: `python3 SYSTEM/compile.py` runs the compiler.
- **Git:** A tool that saves versions of your files so you can undo changes. Example: `git init` creates a new version history.
- **Compile:** Read all your memory files and combine them into one file (BRAIN.md) that the AI can load. Example: after adding a new neuron, compiling updates BRAIN.md.
- **BRAIN.md:** The compiled output — all your memories in one file, ready for any AI to read.
- **Neuron:** A single memory file — one topic, project, or idea per file. Stored in VAULT/NEURONS/.
- **Token:** A unit of text (roughly 4 characters or 3/4 of a word). AI models have limits on how much they can read at once.
- **PATH:** A list of folders your computer searches when you type a command name. If Python is "not in PATH," your computer cannot find it.
- **Watcher:** A background process that watches for file changes and automatically recompiles BRAIN.md when you save a file.
- **Root folder:** The main EIDARA folder that contains DARA.md, SYSTEM/, VAULT/, etc. All commands run from here.
- **Checksum (SHA-256):** A digital fingerprint of a file. If the file changes, the fingerprint changes. EIDARA uses this to detect unauthorized modifications to protected files.
- **Proxy:** A middleman server between your computer and the internet. Common in corporate networks. If downloads fail, you may need to configure proxy settings.
- **VAULT:** The folder where your memory files live. Source of truth — write here. Two main subfolders: NEURONS (your data) and ENABLERS (AI agents).
- **LIBRARY:** The folder where the compiled output (BRAIN.md) lives. Read-only — the AI loads this; you do not edit it.
- **Enabler:** A reusable AI agent or tool definition (lives in `VAULT/ENABLERS/`, files named `agent-*.md`). Examples: `agent-architect.md`, `agent-librarian.md`.
- **Architect:** A special agent that designs the system rules (Constitution). Activated only when you say "open the golden door". Can modify protected files.
- **Librarian:** A maintenance agent that runs health checks on your VAULT every 3 days, fixes encoding errors, processes feedback, and keeps content lean. Activated when you say "run the librarian".
- **INBOX:** A feedback folder (`VAULT/INBOX/`). Any AI can drop a feedback file here when it spots an issue. The Librarian or Architect processes them — they are NOT compiled into BRAIN.md.
- **W-rules:** The Constitution rules (W1 through W15) defined in `DARA.md`. Govern how every AI must read, write, and update DARA. Example: W3(b) marks the 5 files only the Architect may modify.

---

## NOTES FOR THE AI

- This installer is part of the EIDARA open-source project (v1.0)
- The compiler (`compile.py` v3.1) has 103 automated tests
- Protected files have SHA-256 checksums verified on each compile
- Always use `python3` for macOS/Linux commands and `python` for Windows commands
- After each step, verify the result before continuing — do not assume success
- If the user seems confused, simplify your language and offer to explain any term from the Glossary
- If you are an AI without filesystem access (ChatGPT, DeepSeek, Gemini, or any other), tell the user immediately and guide them manually step by step — tell them exactly what to type and what output to expect
- For detailed system docs: `PROJECT/README.md`, `PROJECT/CONTRIBUTING.md`, `SYSTEM/RECOVERY.md`

---

EIDARA v2.0 — Created by **Javier Rotllant Miras** | MIT License | https://www.eidara.dev
