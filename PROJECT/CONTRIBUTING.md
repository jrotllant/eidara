# Contributing to DARA

Thanks for your interest in contributing to DARA. Here's how to get involved.

## How to contribute

1. **Fork the repo** and create a feature branch.
2. **Make your changes** — follow the conventions below.
3. **Test:** Run `python SYSTEM/compile.py` and verify 0 warnings, 0 errors.
4. **Submit a PR** with a clear description of what you changed and why.

## Conventions

- **Neuron format:** `## filename [STATUS/RELEVANCE]` as the first content line. Status: A (active), P (paused), C (completed). Relevance: H (high), M (medium), L (low).
- **Encoding:** Use W-rule compression (e.g., `€NNK` for monetary values, `First.Last(role)` for people, `[A/H]` for status).
- **Footer:** Every VAULT file ends with `→refs:`, `→tags:`, and `~NNNw | YYYY-MM-DD`.
- **Changelog:** Append to `VAULT/changelog.md` in W7 format: `- AI Model (Platform) | file | what changed | ops:N | retry:Y/N | ~NNKt`.
- **Protected files (W3(b)):** Do not modify `DARA.md`, `compile.py`, `agent-architect.md`, or `watcher.py` without Architect protocol approval.

## What to contribute

- **Bug fixes** in compile.py (always welcome)
- **New agent templates** (enablers) for common use cases
- **Documentation** improvements
- **Test cases** for the compiler pipeline
- **Platform adapters** (making DARA work better on specific AI platforms)

## What not to contribute

- Personal data or credentials (even as examples)
- Changes to DARA.md (the Constitution) without discussion
- Dependencies on external services — DARA is designed to be self-contained

## Questions?

Open an issue or start a discussion. We're happy to help.
