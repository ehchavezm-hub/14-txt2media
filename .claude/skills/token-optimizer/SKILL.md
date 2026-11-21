---
name: token-optimizer
description: Audits a Claude Code or Codex setup for context-window waste, fixes it with the user's approval, and measures the saving. Use when context feels tight, sessions degrade, or costs climb.
effort: high
---

# Token Optimizer

Measures where a setup spends its context window, proposes fixes, applies the ones the user approves, and re-measures. The deliverable is a before-and-after the user can verify, with every change backed up. Typical recovery is 5-15% of the window from config cleanup, more when compaction and caching settings are wrong for the way the user works.

Token Optimizer's own skills (`token-optimizer`, `token-coach`, `token-dashboard`, `fleet-auditor`, `resume-checkpoint`) are the measurement layer, so leave them out of every unused-skill, archive or consolidation suggestion, however rarely they run.

## Step 0: pick the right workflow for this runtime

The audit below reads and edits `~/.claude`, which is the wrong target anywhere but Claude Code, so settle the runtime before touching any path. Run exactly this, in this order.

**a. Environment check** (touches no file; an explicit `TOKEN_OPTIMIZER_RUNTIME` wins, and Claude plugin variables are checked before stray `OPENCODE_*` exports, the same order `detect_runtime()` uses):

```bash
if [ "${TOKEN_OPTIMIZER_RUNTIME:-}" = "claude" ] || [ "${TOKEN_OPTIMIZER_RUNTIME:-}" = "codex" ]; then :
elif [ "${TOKEN_OPTIMIZER_RUNTIME:-}" = "opencode" ]; then echo "Token Optimizer — OpenCode runtime detected."
elif [ "${TOKEN_OPTIMIZER_RUNTIME:-}" = "copilot" ]; then echo "Token Optimizer — GitHub Copilot runtime detected."
elif [ "${TOKEN_OPTIMIZER_RUNTIME:-}" = "cursor" ]; then echo "Token Optimizer — Cursor runtime detected."
elif [ "${TOKEN_OPTIMIZER_RUNTIME:-}" = "antigravity" ]; then echo "Token Optimizer — Google Antigravity runtime detected."
elif [ -n "${CLAUDE_PLUGIN_ROOT:-}${CLAUDE_PLUGIN_DATA:-}" ]; then :
elif [ -n "${OPENCODE_BIN:-}${OPENCODE_CONFIG_DIR:-}${OPENCODE_DATA_DIR:-}${OPENCODE_CONFIG:-}${OPENCODE_CLIENT:-}" ]; then echo "Token Optimizer — OpenCode runtime detected."
elif [ -n "${COPILOT_HOME:-}${TOKEN_OPTIMIZER_COPILOT_HOME:-}" ]; then echo "Token Optimizer — GitHub Copilot runtime detected."
elif [ -n "${TOKEN_OPTIMIZER_CURSOR_HOME:-}" ]; then echo "Token Optimizer — Cursor runtime detected."
elif [ -n "${CURSOR_PROJECT_DIR:-}" ] && [ -n "${CURSOR_VERSION:-}" ]; then echo "Token Optimizer — Cursor runtime detected."
elif [ -n "${TOKEN_OPTIMIZER_ANTIGRAVITY_HOME:-}" ]; then echo "Token Optimizer — Google Antigravity runtime detected."
fi
```

| It prints | Do this |
|-----------|---------|
| "OpenCode runtime detected." | Stop. Follow `references/opencode-workflow.md` |
| "Cursor runtime detected." | Stop. Follow `references/cursor-workflow.md` |
| "GitHub Copilot runtime detected." | Stop. Follow the Copilot guidance in `docs/copilot.md`. |
| "Google Antigravity runtime detected." | Stop. Follow `docs/antigravity.md`. |
| nothing | Continue to b. |

**b. Resolve `$MEASURE_PY` and `$PY`.** Each Bash call is a fresh shell, so env vars do not persist between calls: the block ends by echoing both values, and every later command must use the echoed values verbatim.

**c. The authoritative gate.** `"$PY" "$MEASURE_PY" report 2>&1 | head -1`

Any "... runtime detected." line means stop and follow that runtime's file from the table above.

## The audit (Claude Code)

Work through these in order and tick each off; a skipped phase stays in the list as `skip: <reason>`.

```
- [ ] 0. Setup            references/phase0-setup.md
- [ ] 1. Parallel audit   references/agent-prompts.md
- [ ] 2. Synthesis        references/agent-prompts.md (Synthesis Agent)
- [ ] 3. Present, then wait for the user's decision   references/presentation-workflow.md
- [ ] 4. Implement the approved changes               references/implementation-playbook.md
- [ ] 5. Verify and report before/after               references/agent-prompts.md (Verification Agent)
```

**1. Parallel audit.** Dispatch six agents in one message:

| Agent | Writes | Looks at |
|-------|--------|----------|
| CLAUDE.md | `audit/claudemd.md` | Size, duplication, tiering, cache structure |
| MEMORY.md | `audit/memorymd.md` | Size, overlap with CLAUDE.md |
| Skills | `audit/skills.md` | Count, frontmatter overhead, duplicates |
| MCP | `audit/mcp.md` | Deferred tools, broken or unused servers |
| Commands | `audit/commands.md` | Count, menu overhead |
| Settings and advanced | `audit/advanced.md` | Hooks, rules, settings, @imports, cache lifetime, compaction window |

**4. Implement.** Only what the user approved, one change at a time, following the playbook (actions 4A-4P). Also offer:
- `"$PY" "$MEASURE_PY" recommendations`: daily-measured usage recommendations
- `"$PY" "$MEASURE_PY" subagent-cache status` / `compact-advice`

**5. Verify.** The verification agent re-measures and computes the saving. Show before and after, then the habits that keep it. If a verification number is worse than the baseline, find which change caused it, restore that file from the backup, and return to step 4.

## Rules for changing a user's setup

- Back up before every change, and show the diff before applying it.
- Archive, never delete, and archive outside the skills directory so the archive does not load.
- Check what depends on a skill, MCP server or deny rule before archiving it, and name the side effect first.
- Prefer a project-level deny rule to a global one.
- Leave the user's own settings values alone unless they approve the specific change.
- Quote measured numbers (tokens and percent of the window). Frame savings as context budget.

Written for and checked on Claude Opus 5.5 and Sonnet 5.5, and GPT-5.6 on Codex.
