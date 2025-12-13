# Agent SDK Worker Testing Report

**Date:** 2025-12-10 01:30 UTC
**Test Duration:** ~50 minutes of monitoring
**Test Job:** `e6f3e55e-4e90-43ab-a4d2-b7fa9586c468` (medtrainer.com)

---

## Executive Summary

The Agent SDK worker with the **full embedded prompt** (~1750 lines) timed out after 45+ minutes without producing a playbook. This is an improvement over previous attempts with the condensed prompt (90+ min failures), but still far from the target of 12-20 minutes that local `/blueprint-turbo` achieves.

---

## Test Configuration

### What Was Deployed
- **Full embedded prompt**: Complete `.claude/commands/blueprint-turbo.md` content (~1750 lines)
- **Agent SDK version**: `@anthropic-ai/claude-agent-sdk` v0.1.62
- **maxTurns**: 150
- **maxBudgetUsd**: $25.00
- **Worker timeout**: 40 minutes (2400 seconds)
- **Modal function timeout**: 45 minutes (2700 seconds)

### MCP Servers Configured
- `sequential-thinking`: Enabled
- `browser-mcp`: **Commented out** (requires Chrome/Chromium not available in Modal)

### Allowed Tools
```
WebFetch, WebSearch, Read, Write, Edit, Bash, Glob, Grep, Task, Skill, SlashCommand, TodoWrite, mcp__sequential-thinking__sequentialthinking
```

---

## Test Timeline

| Time (min) | Status | Notes |
|------------|--------|-------|
| 0 | pending | Job created in Supabase |
| 0.5 | processing | Picked up by cron worker `poll_pending_jobs` |
| 5 | processing | Still running |
| 10 | processing | Still running |
| 15 | processing | Past target time (12-15 min) |
| 20 | processing | Matches local ~20 min runtime |
| 25 | processing | Still going |
| 30 | processing | Approaching timeout |
| 35 | processing | Exceeds target significantly |
| 40 | processing | Past worker subprocess timeout |
| 45 | processing | Past Modal function timeout |
| 45+ | **FAILED** | Manually marked as failed - orphaned job |

---

## Key Findings

### 1. Job Was Orphaned on Timeout
When Modal function times out, the job stays in "processing" state forever. The error handling doesn't update Supabase on timeout.

**Fix needed:** Add try/finally or signal handler to mark jobs failed on timeout.

### 2. Full Prompt Didn't Reduce Execution Time
Despite having the complete instructions, execution took 45+ minutes vs. expected 12-20 minutes.

**Hypothesis:** The Agent SDK execution is fundamentally slower than local Claude Code due to:
- No browser-mcp for parallel web fetching
- Sequential tool execution vs. parallel
- Additional overhead (Modal container, npm install, git operations)

### 3. Browser-MCP is Critical
Local `/blueprint-turbo` uses browser-mcp for parallel web scraping. Without it, WebFetch must be used sequentially, adding significant time.

**Fix needed:** Install headless Chrome/Chromium in Modal container and enable browser-mcp.

### 4. Job Claimed by Cron Worker
The test job was picked up by `poll_pending_jobs` cron (runs every 5 min) instead of the webhook endpoint. This is expected behavior but worth noting.

---

## Comparison: Local vs. Agent SDK

| Aspect | Local Claude Code | Agent SDK Worker |
|--------|------------------|------------------|
| Execution time | 12-20 min | 45+ min (timeout) |
| browser-mcp | Enabled | Disabled |
| Skill discovery | Auto (project-level) | User-level copy workaround |
| Parallel tool calls | Yes | Unclear |
| MCP servers | All available | Only sequential-thinking |
| Interactive | Yes | No |

---

## Recommended Next Steps

### Option 1: Add Headless Chrome to Modal (Recommended)
Update `modal/wrapper.py` to install Chromium and enable browser-mcp:

```python
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("curl", "git", "chromium", "chromium-driver")
    # ... rest of config
)
```

Then uncomment browser-mcp in `src/worker.ts`.

### Option 2: Optimize/Reduce Prompt
Trim non-essential sections of the embedded prompt to reduce "analysis paralysis".

### Option 3: Add Time Constraints to Prompt
Add explicit timing instructions:
```
IMPORTANT: Complete this analysis within 15 minutes. Prioritize speed over exhaustive research.
```

### Option 4: Increase Timeouts (Less Ideal)
Increase Modal timeout to 60+ minutes. This doesn't solve the root cause but may allow completion.

### Option 5: Hybrid Approach
Use Python worker for speed, then post-process output with Claude for quality improvements.

---

## Files Modified in This Session

1. **`src/prompt.ts`** - Replaced condensed prompt with full ~1750 line embedded prompt
2. **`src/worker.ts`** - Updated maxTurns (100→150), maxBudgetUsd ($10→$25)
3. **`modal/wrapper.py`** - Already had browser-mcp npm install (but not Chrome)

---

## Code Locations

- Worker entry: `agent-sdk-worker/src/index.ts`
- Core logic: `agent-sdk-worker/src/worker.ts` (lines 129-302)
- Prompt: `agent-sdk-worker/src/prompt.ts`
- Modal wrapper: `agent-sdk-worker/modal/wrapper.py`
- Original command: `.claude/commands/blueprint-turbo.md`

---

## Database State

Test job marked as failed:
```sql
UPDATE blueprint_jobs
SET status = 'failed',
    error_message = 'Modal function timeout after 45+ minutes - Agent SDK execution took too long',
    completed_at = NOW()
WHERE id = 'e6f3e55e-4e90-43ab-a4d2-b7fa9586c468';
```

---

## Questions for Next Session

1. What was the agent actually doing for 45 minutes? (Check Modal logs)
2. Would browser-mcp alone cut execution time to target?
3. Is there a way to enable parallel tool execution in Agent SDK?
4. Should we consider a different architecture (e.g., breaking into smaller sub-tasks)?

---

## Appendix: Plan File Location

Full implementation plan at:
`/Users/jordancrawford/.claude/plans/atomic-munching-barto.md`

Contains:
- Root cause analysis
- Option A (Full Prompt Embedding) - what we tested
- Option B (Skill Invocation Pattern) - alternative approach
- Linux skill discovery workaround (GitHub Issue #268)
