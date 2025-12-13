/**
 * Core Worker using Claude Agent SDK
 * Executes Blueprint Turbo via the Agent SDK query() function
 */

import { execSync } from "child_process";
import { existsSync, readFileSync } from "fs";
import path from "path";
import { createClient } from "@supabase/supabase-js";
import { getConfig } from "./config.js";
// Note: getBlueprintTurboPrompt is kept as a fallback, but primary path is /blueprint-turbo slash command
import {
  BlueprintJob,
  markJobProcessing,
  markJobCompleted,
  markJobFailed,
} from "./supabase.js";

// Note: The actual Agent SDK import will be:
// import { query, ClaudeAgentOptions } from "@anthropic-ai/claude-agent-sdk";
// For now, we'll implement with the expected interface

interface AgentMessage {
  type: "assistant" | "user" | "result" | "system";
  subtype?: "success" | "error_during_execution" | "error_tool_execution";
  message?: {
    content: Array<{ type: "text"; text: string } | { type: "tool_use"; name: string }>;
  };
  error?: string;
}

interface QueryOptions {
  prompt: string;
  options: {
    cwd: string;  // SDK uses 'cwd' not 'workingDirectory'
    settingSources: ("user" | "project")[];
    permissionMode: "acceptEdits" | "bypassPermissions";
    systemPrompt?: {
      type: "preset";
      preset: "claude_code";
    };
    mcpServers?: Record<string, {
      type: "stdio";
      command: string;
      args: string[];
      env?: Record<string, string>;
    }>;
    allowedTools?: string[];
    maxTurns?: number;
    maxBudgetUsd?: number;
  };
}

/**
 * Ensure the skills repository is available
 * In Modal, skills are pre-populated in the image at /app/blueprint-skills
 * For local dev, clone the repo if not present
 */
export async function ensureSkillsRepo(): Promise<string> {
  const config = getConfig();
  const repoPath = config.skillsRepoPath;
  const claudeDir = `${repoPath}/.claude`;

  console.log(`[Worker] Ensuring skills repo at ${repoPath}`);

  // Check if .claude directory already exists (pre-populated in Modal image)
  if (existsSync(claudeDir)) {
    console.log(`[Worker] Skills directory found at ${claudeDir} - using pre-populated skills`);
    return repoPath;
  }

  // Clone repo if not present (for local development)
  if (!existsSync(repoPath)) {
    console.log(`[Worker] Cloning skills repo...`);
    execSync(`git clone ${config.skillsRepoUrl} ${repoPath}`, {
      stdio: "inherit",
      env: {
        ...process.env,
        GIT_TERMINAL_PROMPT: "0",
      },
    });
  } else {
    console.log(`[Worker] Updating skills repo...`);
    try {
      execSync("git pull --ff-only", {
        cwd: repoPath,
        stdio: "inherit",
        env: {
          ...process.env,
          GIT_TERMINAL_PROMPT: "0",
        },
      });
    } catch (error) {
      console.warn(`[Worker] Git pull failed, continuing with existing repo`);
    }
  }

  return repoPath;
}

/**
 * Extract playbook URL from agent output
 */
function extractPlaybookUrl(text: string): string | null {
  // Pattern 1: GitHub Pages URL (primary target)
  const githubPagesMatch = text.match(
    /https:\/\/santajordan\.github\.io\/blueprint-gtm-playbooks\/[^\s"'<>]+\.html/i
  );
  if (githubPagesMatch) {
    return githubPagesMatch[0];
  }

  // Pattern 2: Any GitHub Pages URL format
  const genericGithubMatch = text.match(
    /https:\/\/[a-z0-9-]+\.github\.io\/[^\s"'<>]+\.html/i
  );
  if (genericGithubMatch) {
    return genericGithubMatch[0];
  }

  // Pattern 3: Local playbook file path (for constructing URL)
  // Matches patterns like: playbooks/blueprint-gtm-playbook-owner.html
  const localPathMatch = text.match(
    /playbooks\/blueprint-gtm-playbook-[a-z0-9-]+\.html/i
  );
  if (localPathMatch) {
    // Convert to GitHub Pages URL
    const filename = localPathMatch[0].replace("playbooks/", "");
    return `https://santajordan.github.io/blueprint-gtm-playbooks/${filename}`;
  }

  // Pattern 4: Just the filename (e.g., "blueprint-gtm-playbook-owner.html")
  const filenameMatch = text.match(
    /blueprint-gtm-playbook-[a-z0-9-]+\.html/i
  );
  if (filenameMatch) {
    return `https://santajordan.github.io/blueprint-gtm-playbooks/${filenameMatch[0]}`;
  }

  return null;
}

/**
 * Extract company name from agent output
 */
function extractCompanyName(text: string): string | null {
  // Look for patterns like "Company: X" or "playbook for X"
  const companyMatch = text.match(/(?:Company|playbook for|analyzing)\s*[:\-]?\s*([A-Z][^\n.!?]{1,50})/i);
  if (companyMatch) {
    return companyMatch[1].trim();
  }
  return null;
}

/**
 * Extract playbook file path from agent output
 * Agent outputs: PLAYBOOK_PATH: playbooks/blueprint-gtm-playbook-owner.html
 */
function extractPlaybookPath(text: string): string | null {
  // Pattern 1: Explicit marker (most reliable)
  const markerMatch = text.match(/PLAYBOOK_PATH:\s*([^\s\n]+\.html)/i);
  if (markerMatch) {
    return markerMatch[1];
  }

  // Pattern 2: Write/saved file path
  const writeMatch = text.match(/(?:wrote|saved|created|generated).*?(playbooks\/[^\s"']+\.html)/i);
  if (writeMatch) {
    return writeMatch[1];
  }

  // Pattern 3: File path in output
  const pathMatch = text.match(/(playbooks\/blueprint-gtm-playbook-[a-z0-9-]+\.html)/i);
  if (pathMatch) {
    return pathMatch[1];
  }

  return null;
}

// ============================================================================
// PUBLISHING FLOW (agent-sdk-worker / cloud):
// 1. Agent generates playbook HTML at /app/blueprint-skills/playbooks/
// 2. Worker finds the file and reads content
// 3. Worker uploads to Vercel via REST API
// 4. Final URL: https://playbooks.blueprintgtm.com/{company-slug}
//
// NOTE: Local CLI uses GitHub Pages via .claude/skills/blueprint-github-publish
// ============================================================================

/**
 * Upload playbook HTML to Vercel for proper Content-Type serving.
 * Uses Vercel REST API v13 - see https://vercel.com/docs/rest-api/endpoints/deployments
 */
async function uploadPlaybookToVercel(
  htmlContent: string,
  companySlug: string,
  vercelToken: string,
  projectName: string = "blueprint-playbooks"
): Promise<{ success: boolean; url?: string; error?: string }> {
  // Use simplified filename for pretty URLs (e.g., "owner-com.html")
  const filename = `${companySlug}.html`;

  console.log(`[Vercel] Uploading playbook: ${filename}`);

  // Vercel.json configuration for clean URLs (/:slug -> /:slug.html)
  const vercelConfig = JSON.stringify({
    rewrites: [
      { source: "/:slug", destination: "/:slug.html" }
    ]
  });

  try {
    // Vercel REST API v13 - files array format per official docs
    const response = await fetch("https://api.vercel.com/v13/deployments", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${vercelToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        name: projectName,
        // Files array format: { file: "path", data: "content", encoding: "utf-8" }
        files: [
          {
            file: filename,
            data: htmlContent,
            encoding: "utf-8"
          },
          {
            file: "vercel.json",
            data: vercelConfig,
            encoding: "utf-8"
          }
        ],
        target: "production",
        projectSettings: {
          framework: null,  // Static file, no framework
        }
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`[Vercel] Upload failed: ${response.status} - ${errorText}`);
      return { success: false, error: `Vercel API error: ${response.status}` };
    }

    const data = await response.json();
    // Return pretty URL with custom domain (e.g., playbooks.blueprintgtm.com/owner-com)
    const deployedUrl = `https://playbooks.blueprintgtm.com/${companySlug}`;

    console.log(`[Vercel] Playbook deployed: ${deployedUrl}`);

    return { success: true, url: deployedUrl };
  } catch (e) {
    console.error(`[Vercel] Upload exception: ${e}`);
    return { success: false, error: String(e) };
  }
}

/**
 * Extract company slug from URL for pretty Vercel URLs.
 * Includes TLD with dashes.
 * e.g., "https://owner.com" -> "owner-com"
 * e.g., "https://www.canvas-medical.com" -> "canvas-medical-com"
 * e.g., "https://www.example.co.uk" -> "example-co-uk"
 */
function extractCompanySlug(companyUrl: string): string {
  try {
    const url = new URL(companyUrl);
    // Remove www. prefix
    let hostname = url.hostname.replace(/^www\./, "");
    // Replace dots with dashes (includes TLD)
    return hostname.toLowerCase().replace(/\./g, "-").replace(/[^a-z0-9-]/g, "");
  } catch {
    // Fallback: extract from URL string
    return companyUrl
      .replace(/^https?:\/\/(www\.)?/i, "")
      .split('/')[0]
      .toLowerCase()
      .replace(/\./g, "-")
      .replace(/[^a-z0-9-]/g, "");
  }
}

/**
 * Extract OLD-format company slug for finding files created by the agent.
 * Agent still uses the old format (without TLD).
 * e.g., "https://owner.com" -> "owner"
 * e.g., "https://www.canvas-medical.com" -> "canvas-medical"
 */
function extractOldCompanySlug(companyUrl: string): string {
  try {
    const url = new URL(companyUrl);
    // Remove www. prefix and get hostname without TLD
    let hostname = url.hostname.replace(/^www\./, "");
    // Remove common TLDs
    hostname = hostname.replace(/\.(com|net|org|io|co|ai|health|edu)$/i, "");
    // Convert to slug format
    return hostname.toLowerCase().replace(/[^a-z0-9-]/g, "-");
  } catch {
    // Fallback: extract from URL string
    return companyUrl
      .replace(/^https?:\/\/(www\.)?/i, "")
      .replace(/\.(com|net|org|io|co|ai|health|edu).*/i, "")
      .toLowerCase()
      .replace(/[^a-z0-9-]/g, "-");
  }
}

/**
 * Find playbook file anywhere under /app using find command.
 * Handles cwd mismatch between Agent SDK and worker subprocess.
 *
 * Agent SDK runs with cwd: /app/blueprint-skills
 * Worker subprocess runs from /app/agent-sdk-worker
 */
function findPlaybookFile(filename: string): string | null {
  try {
    // Find files modified in last 30 minutes (fresh from this run)
    const findResult = execSync(
      `find /app -name "${filename}" -type f -mmin -30 2>/dev/null | head -1`,
      { encoding: 'utf-8', timeout: 10000 }
    ).trim();

    if (findResult && existsSync(findResult)) {
      console.log(`[File] Found playbook via find: ${findResult}`);
      return findResult;
    }
  } catch (e) {
    console.log(`[File] find command failed: ${e}`);
  }

  return null;
}

/**
 * Run Blueprint Turbo via Agent SDK
 * This is the core function that invokes the /blueprint-turbo command
 */
export async function runBlueprintTurbo(
  companyUrl: string,
  workingDirectory: string
): Promise<{ playbookUrl: string; companyName?: string }> {
  const config = getConfig();
  const startTime = Date.now();
  const maxExecutionMs = 30 * 60 * 1000; // 30 minutes hard limit

  console.log(`[Worker] Starting Blueprint Turbo for ${companyUrl}`);
  console.log(`[Worker] Working directory: ${workingDirectory}`);
  console.log(`[Worker] Max execution time: ${maxExecutionMs / 60000} minutes`);

  // Log directory contents for debugging
  try {
    const { readdirSync, existsSync } = await import("fs");
    console.log(`[Worker] Working dir exists: ${existsSync(workingDirectory)}`);
    if (existsSync(workingDirectory)) {
      console.log(`[Worker] Working dir contents: ${readdirSync(workingDirectory).join(", ")}`);
    }
    const claudeDir = `${workingDirectory}/.claude`;
    console.log(`[Worker] .claude dir exists: ${existsSync(claudeDir)}`);
    if (existsSync(claudeDir)) {
      console.log(`[Worker] .claude contents: ${readdirSync(claudeDir).join(", ")}`);
      const commandsDir = `${claudeDir}/commands`;
      if (existsSync(commandsDir)) {
        console.log(`[Worker] commands contents: ${readdirSync(commandsDir).join(", ")}`);
      }
    }
  } catch (e) {
    console.log(`[Worker] Dir listing error: ${e}`);
  }

  // Import the Agent SDK dynamically to handle cases where it's not installed yet
  let query: (options: QueryOptions) => AsyncIterable<AgentMessage>;

  try {
    const sdk = await import("@anthropic-ai/claude-agent-sdk");
    query = sdk.query;
  } catch (error) {
    throw new Error(
      `Claude Agent SDK not installed. Run: npm install @anthropic-ai/claude-agent-sdk\nError: ${error}`
    );
  }

  let playbookUrl: string | null = null;
  let playbookPath: string | null = null;
  let companyName: string | null = null;
  let lastOutput = "";
  let errorOutput = "";

  // Use slash command with claude_code preset (matches local behavior)
  // The systemPrompt preset enables command discovery via progressive disclosure
  const prompt = `/blueprint-turbo ${companyUrl}`;
  console.log(`[Worker] Using slash command: ${prompt}`);

  const queryOptions: QueryOptions = {
    prompt,
    options: {
      cwd: workingDirectory,
      // Include user-level skills for Linux discovery workaround (Modal copies to /root/.claude).
      settingSources: ["project", "user"],
      permissionMode: "acceptEdits",  // SDK option - use acceptEdits for now

      // CRITICAL: Use claude_code preset for same harness as local Claude Code
      systemPrompt: {
        type: "preset",
        preset: "claude_code",
      },

      mcpServers: {
        "sequential-thinking": {
          type: "stdio",
          command: "npx",
          args: ["@modelcontextprotocol/server-sequential-thinking"],
        },
        "browser-mcp": {
          type: "stdio",
          command: "npx",
          args: ["browser-mcp"],
          env: {
            CHROME_PATH: process.env.CHROME_PATH || "/usr/bin/chromium",
            PUPPETEER_HEADLESS: "true",
          },
        },
      },

      // No allowedTools restriction - bypassPermissions allows all tools

      maxTurns: 150,
      maxBudgetUsd: 25.0,
    },
  };

  console.log(`[Worker] Invoking Agent SDK with claude_code preset`);
  console.log(`[Worker] ANTHROPIC_API_KEY present: ${!!process.env.ANTHROPIC_API_KEY}`);

  let messageCount = 0;
  try {
    console.log(`[Worker] Starting query iteration...`);
    for await (const message of query(queryOptions)) {
      messageCount++;

      // Wall-clock timeout check
      const elapsed = Date.now() - startTime;
      if (elapsed > maxExecutionMs) {
        console.error(`[Worker] Wall-clock timeout after ${elapsed / 60000} minutes`);
        throw new Error(`Wall-clock timeout: execution exceeded ${maxExecutionMs / 60000} minutes`);
      }

      console.log(`[Worker] Message #${messageCount}, type: ${message.type}, elapsed: ${Math.round(elapsed / 1000)}s`);
      // Log full message for debugging
      console.log(`[Worker] Full message: ${JSON.stringify(message).substring(0, 1000)}`);
      if (message.type === "result") {
        const resultMsg = message as any;
        console.log(`[Worker] Result subtype: ${resultMsg.subtype}`);
        console.log(`[Worker] Result errors: ${JSON.stringify(resultMsg.errors)}`);
        console.log(`[Worker] Result cost: $${resultMsg.total_cost_usd}`);
        if (resultMsg.result) {
          console.log(`[Worker] Result text: ${resultMsg.result.substring(0, 500)}`);
        }
      }
      // Process different message types
      if (message.type === "assistant" && message.message?.content) {
        for (const block of message.message.content) {
          if (block.type === "text") {
            lastOutput = block.text;

            // Log progress indicators
            if (block.text.includes("Wave")) {
              console.log(`[Worker] Progress: ${block.text.substring(0, 100)}...`);
            }

            // Try to extract URL
            const url = extractPlaybookUrl(block.text);
            if (url) {
              playbookUrl = url;
              console.log(`[Worker] Found playbook URL: ${playbookUrl}`);
            }

            // Try to extract local file path (for Vercel upload)
            const foundPath = extractPlaybookPath(block.text);
            if (foundPath && !playbookPath) {
              playbookPath = foundPath;
              console.log(`[Worker] Found playbook path: ${playbookPath}`);
            }

            // Try to extract company name
            const name = extractCompanyName(block.text);
            if (name && !companyName) {
              companyName = name;
              console.log(`[Worker] Found company name: ${companyName}`);
            }
          }
        }
      }

      if (message.type === "result") {
        if (message.subtype === "success") {
          console.log(`[Worker] Agent SDK completed successfully`);
        } else if (message.subtype === "error_during_execution") {
          errorOutput = message.error || lastOutput;
          console.error(`[Worker] Agent SDK error: ${errorOutput}`);
        }
      }
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    console.error(`[Worker] Exception during Agent SDK execution:`, errorMessage);
    console.error(`[Worker] Total messages received before error: ${messageCount}`);
    throw new Error(`Agent SDK execution failed: ${errorMessage}`);
  }

  console.log(`[Worker] Query finished. Total messages: ${messageCount}, elapsed: ${Math.round((Date.now() - startTime) / 1000)}s`);

  // UPLOAD STRATEGY:
  // 1. Check explicit paths first (Agent SDK writes to /app/blueprint-skills/playbooks/)
  // 2. Fall back to findPlaybookFile() with `find` command
  // 3. Upload to GitHub Pages (serves HTML correctly with proper Content-Type)
  const companySlug = extractCompanySlug(companyUrl);  // Format with TLD (e.g., owner-com)
  const oldCompanySlug = extractOldCompanySlug(companyUrl);  // Old format for file lookup (e.g., owner)
  const expectedFilenameOld = `blueprint-gtm-playbook-${oldCompanySlug}.html`;  // Agent creates files with OLD format
  const expectedFilenameNew = `blueprint-gtm-playbook-${companySlug}.html`;    // Fallback if agent includes TLD

  // Debug logging for upload strategy
  console.log(`[Worker] ========== UPLOAD CONFIG ==========`);
  console.log(`[Worker] Publishing to: GitHub Pages (SantaJordan/blueprint-gtm-playbooks)`);
  console.log(`[Worker] companySlug: ${companySlug}`);
  console.log(`[Worker] oldCompanySlug (file lookup): ${oldCompanySlug}`);
  console.log(`[Worker] expectedFilenameOld: ${expectedFilenameOld}`);
  console.log(`[Worker] expectedFilenameNew: ${expectedFilenameNew}`);
  console.log(`[Worker] workingDirectory: ${workingDirectory}`);
  console.log(`[Worker] =====================================`);

  // Step 1: Find the playbook file
  // Priority order matches where Agent SDK actually writes files:
  // - Agent SDK cwd is /app/blueprint-skills
  // - Agent writes to playbooks/xxx.html (relative to cwd)
  // - So file lands at /app/blueprint-skills/playbooks/xxx.html
  let foundPath: string | null = null;

  // PRIMARY: Check explicit paths where Agent SDK writes files
  const expectedFilenames = [expectedFilenameOld, expectedFilenameNew];
  const explicitPaths: string[] = [];
  for (const expectedFilename of expectedFilenames) {
    explicitPaths.push(
      `/app/blueprint-skills/playbooks/${expectedFilename}`,
      path.join(workingDirectory, `playbooks/${expectedFilename}`),
      `/app/agent-sdk-worker/playbooks/${expectedFilename}`,
    );
  }

  // Add paths from extracted playbookPath if available
  if (playbookPath) {
    const extractedPaths = [
      path.join(workingDirectory, playbookPath),
      path.join("/app/blueprint-skills", playbookPath),
      path.join("/app/agent-sdk-worker", playbookPath),
      playbookPath,
      path.resolve(playbookPath),
    ];
    if (path.isAbsolute(playbookPath)) {
      extractedPaths.unshift(playbookPath);
    }
    explicitPaths.push(...extractedPaths);
  }

  // Deduplicate paths
  const uniquePaths = [...new Set(explicitPaths)];

  console.log(`[Worker] Searching for playbook file...`);
  console.log(`[Worker] Checking ${uniquePaths.length} explicit paths:`);

  for (const loc of uniquePaths) {
    const exists = existsSync(loc);
    console.log(`[Worker]   ${exists ? "✓ FOUND" : "✗ not found"}: ${loc}`);
    if (exists && !foundPath) {
      foundPath = loc;
      // Continue logging to show all checked paths for debugging
    }
  }

  // If not found via explicit paths, use find command as last resort
  if (!foundPath) {
    console.log(`[Worker] Explicit paths failed, using find command...`);
    for (const expectedFilename of expectedFilenames) {
      foundPath = findPlaybookFile(expectedFilename);
      if (foundPath) break;
    }
  }

  // Step 2: Upload to Vercel if file found
  if (foundPath) {
    const htmlContent = readFileSync(foundPath, "utf-8");
    console.log(`[Worker] Found playbook at ${foundPath}, size: ${htmlContent.length} bytes`);

    // Upload to Vercel for proper HTML serving
    // Final URL: https://playbooks.blueprintgtm.com/{company-slug}
    const vercelToken = process.env.VERCEL_TOKEN;
    if (vercelToken) {
      console.log(`[Worker] Publishing to Vercel: ${companySlug}`);
      try {
        const result = await uploadPlaybookToVercel(htmlContent, companySlug, vercelToken);
        if (result.success && result.url) {
          playbookUrl = result.url;
          console.log(`[Worker] Vercel publish successful: ${playbookUrl}`);
        } else {
          console.error(`[Worker] Vercel publish failed: ${result.error}`);
        }
      } catch (vercelError) {
        console.error(`[Worker] Vercel publish exception: ${vercelError}`);
      }
    } else {
      console.error(`[Worker] VERCEL_TOKEN not set - cannot publish playbook`);
    }
  } else {
    console.warn(`[Worker] Playbook file not found. Checked:`);
    console.warn(`[Worker]   - Direct paths from playbookPath: ${playbookPath || "(not extracted)"}`);
    console.warn(`[Worker]   - find /app -name "${expectedFilenameOld}"`);
    console.warn(`[Worker]   - find /app -name "${expectedFilenameNew}"`);
    console.log(`[Worker] Using extracted URL as fallback: ${playbookUrl}`);
  }

  if (!playbookUrl) {
    // If no URL was extracted, check if there was an error
    if (errorOutput) {
      throw new Error(`Blueprint Turbo failed: ${errorOutput}`);
    }
    if (messageCount === 0) {
      throw new Error(`Agent SDK returned no messages. Check ANTHROPIC_API_KEY and SDK configuration.`);
    }
    throw new Error(
      `Blueprint Turbo completed but no playbook URL was found in output. Messages: ${messageCount}, Last output: ${lastOutput.substring(0, 500)}`
    );
  }

  return {
    playbookUrl,
    companyName: companyName || undefined,
  };
}

/**
 * Process a single Blueprint job
 */
export async function processJob(job: BlueprintJob): Promise<{
  success: boolean;
  playbookUrl?: string;
  error?: string;
}> {
  console.log(`[Worker] Processing job ${job.id} for ${job.company_url}`);

  try {
    // Mark job as processing
    await markJobProcessing(job.id);

    // Ensure skills repo is available
    const workingDirectory = await ensureSkillsRepo();

    // Run Blueprint Turbo
    const result = await runBlueprintTurbo(job.company_url, workingDirectory);

    // Mark job as completed
    await markJobCompleted(job.id, result.playbookUrl, result.companyName);

    // If this job was created via Stripe (manual capture), trigger capture after delivery.
    const paymentIntentId = job.stripe_payment_intent_id;
    if (paymentIntentId) {
      const vercelApiUrl = process.env.VERCEL_API_URL;
      const modalWebhookSecret = process.env.MODAL_WEBHOOK_SECRET;
      if (vercelApiUrl && modalWebhookSecret) {
        try {
          console.log(`[Worker] Capturing payment for job ${job.id}...`);
          const resp = await fetch(`${vercelApiUrl}/api/capture-payment`, {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${modalWebhookSecret}`,
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              job_id: job.id,
              playbook_url: result.playbookUrl,
            }),
          });
          if (!resp.ok) {
            const text = await resp.text();
            console.warn(`[Worker] Payment capture failed: ${resp.status} ${text}`);
          } else {
            console.log(`[Worker] Payment capture request succeeded`);
          }
        } catch (e) {
          console.warn(`[Worker] Payment capture request errored: ${e}`);
        }
      } else {
        console.log(`[Worker] Payment capture skipped - missing VERCEL_API_URL or MODAL_WEBHOOK_SECRET`);
      }
    }

    console.log(`[Worker] Job ${job.id} completed successfully`);
    return {
      success: true,
      playbookUrl: result.playbookUrl,
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    console.error(`[Worker] Job ${job.id} failed:`, errorMessage);

    // Mark job as failed
    await markJobFailed(job.id, errorMessage);

    return {
      success: false,
      error: errorMessage,
    };
  }
}

// Expose internal helpers for test suite (no runtime behavior change).
export const __test__ = {
  extractPlaybookUrl,
  extractPlaybookPath,
  extractCompanySlug,
  extractOldCompanySlug,
};
