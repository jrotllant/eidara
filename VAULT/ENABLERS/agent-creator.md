summary: Creates new agents following DARA methodology. 10 design principles, 5-step build process.
## agent-creator [A/H]
Agent creation methodology for DARA. Invoked when the owner says "create an agent that does X" or "build me an agent for Y".
Follow these steps and principles in order. Output: a new `agent-*.md` in ENABLERS/ (requires the owner's explicit permission per W5/W3(b)) or a neuron in NEURONS/ if the agent is a one-time workflow.

### 10 DESIGN PRINCIPLES

**P1 — Start small, scale gradually.** Build a single-purpose agent first (observe→reason→act loop). Find one repetitive task and solve only that. Do NOT orchestrate multi-agent flows at start. Scale only after validating results.

**P2 — Modular architecture.** Separate: instructions (in `agent-*.md`), tools/scripts (separate files or MCPs), context/knowledge (NEURONS/), and output (workspace or external system). Each agent file must include `→refs:` linking to its tools, context, and credentials.

**P3 — Evaluate everything.** Before deploying, define a golden set of test inputs/outputs. Version prompts, models, and data. Monitor: cost, tokens, latency, errors. Use simulations before production.

**P4 — AgentOps lifecycle.** Treat the agent as a complex engineering system. Apply CI/CD: deploy fast, update, security patch. Log all changes in VAULT/changelog.md. Version the agent file itself.

**P5 — Human-in-the-loop.** No "set and forget". Agent needs supervision, quality review, and course correction. Think of it as a smart intern: clear instructions, output review, correction when needed. Include human review steps in the agent flow.

**P6 — Design for outcomes, not outputs.** Anchor every build in measurable business results. A successful POC is not one that works technically, but one that delivers value. Define success metrics before coding.

**P7 — Security & governance from day 1.** Every agent needs protections similar to a human. Implement guardrails (ethical & operational limits), decision traceability, audit trail. Data pipeline failures = #1 cause of broken agents.

**P8 — Right-sized stack.** Choose tools proportional to the problem. Options by layer: LLM (Claude, GPT-4, Gemini, or multi-provider routing), orchestration (LangChain, Vercel AI SDK, or direct API — prefer simplest), knowledge/RAG (Pinecone, vector DB, or flat files), tools (scripts, MCPs, APIs), frontend (minimal or none). Default: simplest that works.

**P9 — Invest in people.** AI literacy is the real bottleneck. Tools get cheaper; human competence to supervise and direct agents is the differentiator. Design agents that augment, not replace, human judgment.

**P10 — Micro-Agent Architecture (DARA native).** Structure:
```
agent-[name].md   # Instructions (system prompt, versionable)
tools/            # Scripts (Python, Bash, Node) — or MCPs
context/          # Docs, guides, NEURONS references
workspace/        # Outputs (research, drafts, data)
```
No heavy frameworks unless justified. The AI reads the agent file and executes. This == DARA's own architecture.

### CREATION WORKFLOW

**Step 1 — Clarify the ask.** What problem? Who uses it? What systems does it touch? What defines success? Output: 3-line brief.

**Step 2 — Design.** Apply P1-P10. Define: instructions, tools needed, inputs/outputs, human touchpoints, error handling, evaluation criteria.

**Step 3 — Write.** Create `agent-[name].md` in ENABLERS/ following DARA encoding format (status/relevance, →refs, →tags, ~NNNw | YYYY-MM-DD). Include the full system prompt as the agent's instructions. Include a clear activation trigger phrase.

**Step 4 — Validate.** Run through golden set. Check: does it follow W3(b) (no protected files touched)? Does it respect existing DARA rules? Is it self-contained?

**Step 5 — Register.** Log in changelog.md. Run compile.py. Confirm to the owner with: agent name, purpose, tools used, pending items.

### RESTRICTIONS
- NEVER modify `DARA.md`, `compile.py`, `agent-architect.md`, or `watcher.py` (W3(b) protected)
- Creating new `agent-*.md` requires the owner's explicit permission (W5)
- If the owner asks to update an existing agent, check W3(b) first — if protected, leave INBOX feedback
- If unsure about design, leave INBOX feedback for the Architect

→refs: agent-architect
→tags: #agent #creator #methodology #design-principles #DARA #agents #architecture
~609w | 2026-04-26

