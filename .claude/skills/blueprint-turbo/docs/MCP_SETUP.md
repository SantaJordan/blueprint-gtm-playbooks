# MCP Server Setup for Blueprint Turbo

Blueprint Turbo requires two Model Context Protocol (MCP) servers to achieve its 12-15 minute execution time. This guide walks you through installation and verification.

---

## Overview

**Required MCP Servers:**

1. **Browser MCP** - Enables parallel web research (15-20 concurrent calls)
   - Repository: https://github.com/modelcontextprotocol/servers/tree/main/src/browser
   - Purpose: Wave 1 (intelligence) and Wave 2 (data discovery)
   - Fallback: Sequential WebFetch (slower but functional)

2. **Sequential Thinking MCP** - Enables stepwise reasoning for segment generation
   - Repository: https://github.com/sequentialthinking/mcp-server
   - Purpose: Synthesis phase (connecting data to pain segments)
   - Fallback: None - **REQUIRED** for Blueprint Turbo to run

---

## Prerequisites

- **Node.js 18+** (for Browser MCP)
- **npm or npx** (for package management)
- **Claude Desktop or Claude Code CLI** (for MCP server integration)

Check your Node.js version:
```bash
node --version
```

If you don't have Node.js, install from: https://nodejs.org/

---

## Installation: Browser MCP

### Step 1: Install Browser MCP Server

The Browser MCP server is part of the official MCP servers repository.

**Option A: Install via npx (Recommended)**

```bash
npx @modelcontextprotocol/server-browser
```

This will download and run the server. To verify it's working, you should see output about the server starting.

**Option B: Clone and Install from Source**

```bash
# Clone the repository
git clone https://github.com/modelcontextprotocol/servers.git
cd servers/src/browser

# Install dependencies
npm install

# Build the server
npm run build
```

### Step 2: Configure Browser MCP in Claude

Add the Browser MCP server to your Claude configuration file.

**For Claude Desktop:**

Edit your `claude_desktop_config.json` (location varies by OS):
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

Add this entry to the `mcpServers` section:

```json
{
  "mcpServers": {
    "browser": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-browser"
      ]
    }
  }
}
```

**For Claude Code CLI:**

Edit your `.claude/mcp.json` file in your working directory:

```json
{
  "mcpServers": {
    "browser": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-browser"
      ]
    }
  }
}
```

### Step 3: Restart Claude

- **Claude Desktop**: Quit and reopen the application
- **Claude Code CLI**: Exit and restart your terminal session

### Step 4: Verify Browser MCP

Test that the Browser MCP server is loaded:

**In Claude Desktop or Claude Code:**
```
Can you list the available MCP tools?
```

You should see tools like:
- `mcp__browser__navigate`
- `mcp__browser__screenshot`
- `mcp__browser__get_content`

If you see these, Browser MCP is working correctly.

---

## Installation: Sequential Thinking MCP

### Step 1: Install Sequential Thinking MCP Server

**Via npm (Recommended):**

```bash
npm install -g @sequentialthinking/mcp-server
```

**Or via npx (no installation):**

```bash
npx @sequentialthinking/mcp-server
```

### Step 2: Configure Sequential Thinking MCP in Claude

Add the Sequential Thinking MCP server to your Claude configuration file.

**For Claude Desktop:**

Edit your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "browser": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-browser"
      ]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": [
        "@sequentialthinking/mcp-server"
      ]
    }
  }
}
```

**For Claude Code CLI:**

Edit your `.claude/mcp.json`:

```json
{
  "mcpServers": {
    "browser": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-browser"
      ]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": [
        "@sequentialthinking/mcp-server"
      ]
    }
  }
}
```

### Step 3: Restart Claude

- **Claude Desktop**: Quit and reopen the application
- **Claude Code CLI**: Exit and restart your terminal session

### Step 4: Verify Sequential Thinking MCP

Test that the Sequential Thinking MCP server is loaded:

**In Claude Desktop or Claude Code:**
```
Can you list the available MCP tools?
```

You should see:
- `mcp__sequential-thinking__sequentialthinking`

If you see this, Sequential Thinking MCP is working correctly.

---

## Verification: Full System Check

Run this test to confirm both MCP servers are working:

```
Can you use Sequential Thinking to analyze whether Browser MCP is installed?
```

Claude should:
1. Use the `mcp__sequential-thinking__sequentialthinking` tool to reason through the check
2. List available MCP tools to confirm Browser MCP is present
3. Report success or failure

**Expected Output:**
```
✅ Sequential Thinking MCP: Available
✅ Browser MCP: Available
✅ Blueprint Turbo: Ready to run
```

---

## Troubleshooting

### Error: "Sequential Thinking MCP not found"

**Symptom:** Blueprint Turbo fails immediately with:
```
ERROR: Sequential Thinking MCP server is required but not found.
Blueprint Turbo cannot proceed without this dependency.
```

**Fix:**
1. Verify installation: `npm list -g @sequentialthinking/mcp-server`
2. Check configuration file for typos in `"sequential-thinking"` entry
3. Restart Claude after making configuration changes
4. If using npx, ensure you have internet connectivity (npx downloads on first run)

### Error: "Browser MCP not found"

**Symptom:** Blueprint Turbo runs but falls back to sequential WebFetch, adding 5-10 minutes to execution time.

**Impact:** Non-critical - Blueprint Turbo will still complete, just slower.

**Fix:**
1. Verify installation: `npx @modelcontextprotocol/server-browser --version`
2. Check configuration file for typos in `"browser"` entry
3. Ensure Node.js 18+ is installed: `node --version`
4. Restart Claude after making configuration changes

### Error: "Command not found: npx"

**Symptom:** Claude configuration fails to load MCP servers with error about `npx` not being found.

**Fix:**
1. Install Node.js from https://nodejs.org/ (includes npx)
2. Verify installation: `npx --version`
3. Restart your terminal/Claude after installing Node.js

### Error: "MCP server crashed" or timeout errors

**Symptom:** MCP tools appear in the list but fail when called.

**Fix:**
1. Check for conflicting Node.js versions: `node --version`
2. Clear npm cache: `npm cache clean --force`
3. Reinstall MCP servers:
   ```bash
   npm uninstall -g @sequentialthinking/mcp-server
   npm install -g @sequentialthinking/mcp-server
   ```
4. Check Claude logs for specific error messages:
   - **macOS**: `~/Library/Logs/Claude/`
   - **Windows**: `%APPDATA%\Claude\logs\`
   - **Linux**: `~/.config/Claude/logs/`

### Configuration File Not Found

**Symptom:** Cannot locate `claude_desktop_config.json` or `.claude/mcp.json`.

**Fix for Claude Desktop:**
1. Create the directory if it doesn't exist:
   - **macOS**: `mkdir -p ~/Library/Application\ Support/Claude`
   - **Windows**: `mkdir %APPDATA%\Claude`
   - **Linux**: `mkdir -p ~/.config/Claude`
2. Create the file: `claude_desktop_config.json`
3. Add the minimal configuration:
   ```json
   {
     "mcpServers": {}
   }
   ```
4. Add server entries as shown above

**Fix for Claude Code CLI:**
1. Navigate to your working directory
2. Create `.claude/mcp.json`:
   ```bash
   mkdir -p .claude
   touch .claude/mcp.json
   ```
3. Add the configuration shown above

---

## Testing Blueprint Turbo

Once both MCP servers are installed and verified, test Blueprint Turbo with a quick run:

```bash
/blueprint-turbo https://example.com
```

**Expected Behavior:**
- Wave 1 completes in 0-4 minutes (15-20 parallel intelligence calls via Browser MCP)
- Wave 2 completes in 4-9 minutes (15-20 parallel data discovery calls)
- Synthesis completes in 9-11 minutes (Sequential Thinking generates segments)
- Wave 3 completes in 11-14 minutes (message generation + critique)
- Wave 4 completes in 14-15 minutes (HTML assembly)

**Total Time:** 12-15 minutes

If execution takes 20-25 minutes, Browser MCP is likely not working (falling back to sequential WebFetch).

If execution fails at Synthesis phase, Sequential Thinking MCP is not working.

---

## Alternative: Running Without MCP Servers

### Without Browser MCP

Blueprint Turbo will automatically fall back to sequential WebFetch calls.

**Impact:**
- Execution time increases from 12-15 minutes to 20-25 minutes
- Quality remains the same
- No action required - fallback is automatic

### Without Sequential Thinking MCP

Blueprint Turbo **cannot run** without Sequential Thinking MCP.

**Alternative:**
Use the original Blueprint skills with manual stage execution:
1. `/blueprint-company-research <url>`
2. `/blueprint-data-research` (uses company research output)
3. `/blueprint-message-generation` (uses data research output)
4. `/blueprint-explainer-builder` (uses message output)

**Execution time:** 30-45 minutes (same quality as Blueprint Turbo)

---

## Advanced Configuration

### Custom Node.js Path

If you have multiple Node.js versions, specify the exact path:

```json
{
  "mcpServers": {
    "browser": {
      "command": "/usr/local/bin/node",
      "args": [
        "/path/to/node_modules/@modelcontextprotocol/server-browser/dist/index.js"
      ]
    }
  }
}
```

### Debugging Mode

Enable verbose logging for MCP servers:

```json
{
  "mcpServers": {
    "browser": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-browser",
        "--debug"
      ],
      "env": {
        "DEBUG": "*"
      }
    }
  }
}
```

Logs will appear in Claude's log directory (see "Error: MCP server crashed" section above).

---

## Updating MCP Servers

### Update Browser MCP

```bash
npm update -g @modelcontextprotocol/server-browser
```

Or if using npx, it will automatically use the latest version on next run.

### Update Sequential Thinking MCP

```bash
npm update -g @sequentialthinking/mcp-server
```

### Check for Updates

```bash
npm outdated -g
```

---

## Support

**Browser MCP Issues:**
- GitHub: https://github.com/modelcontextprotocol/servers/issues
- Documentation: https://github.com/modelcontextprotocol/servers/tree/main/src/browser

**Sequential Thinking MCP Issues:**
- GitHub: https://github.com/sequentialthinking/mcp-server/issues
- Documentation: https://github.com/sequentialthinking/mcp-server

**Blueprint Turbo Issues:**
- See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for Blueprint-specific debugging
- File issues at your Blueprint Turbo repository

---

## Quick Reference

| Task | Command |
|------|---------|
| Install Browser MCP | `npx @modelcontextprotocol/server-browser` |
| Install Sequential Thinking MCP | `npm install -g @sequentialthinking/mcp-server` |
| Verify Node.js | `node --version` |
| List MCP tools | Ask Claude: "List available MCP tools" |
| Test Blueprint Turbo | `/blueprint-turbo https://example.com` |
| Check npm packages | `npm list -g` |
| Update MCP servers | `npm update -g` |

---

## Next Steps

Once both MCP servers are installed and verified:

1. Read [README.md](./README.md) for Blueprint Turbo overview
2. Review [SKILL.md](./SKILL.md) for full methodology documentation
3. Run your first Blueprint Turbo execution: `/blueprint-turbo <company-url>`
4. Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) if you encounter issues

---

**Version:** 1.0.0 (November 2025)
