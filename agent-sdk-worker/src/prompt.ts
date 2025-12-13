/**
 * Blueprint Turbo Prompt Helper
 *
 * With systemPrompt preset: "claude_code", the agent uses /blueprint-turbo directly.
 * This module only provides a fallback if command discovery fails.
 *
 * PRIMARY PATH: Agent SDK uses `/blueprint-turbo ${companyUrl}` command
 * FALLBACK: Read command file from disk and substitute $ARGUMENTS
 */

import { readFileSync, existsSync } from "fs";
import { join } from "path";

/**
 * Get the blueprint-turbo prompt with the URL substituted
 *
 * This is a FALLBACK function - the primary execution path is the
 * /blueprint-turbo slash command invoked directly by the Agent SDK.
 *
 * Only used if command discovery fails in the cloud environment.
 */
export function getBlueprintTurboPrompt(companyUrl: string): string {
  // Try to read from file system (for cases where command discovery fails)
  const possiblePaths = [
    "/app/blueprint-skills/.claude/commands/blueprint-turbo.md",
    "/root/.claude/commands/blueprint-turbo.md",
    join(process.cwd(), ".claude/commands/blueprint-turbo.md"),
  ];

  for (const path of possiblePaths) {
    if (existsSync(path)) {
      console.log(`[Prompt] Loading blueprint-turbo from ${path}`);
      try {
        const content = readFileSync(path, "utf-8");
        // Remove YAML frontmatter if present
        const withoutFrontmatter = content.replace(/^---[\s\S]*?---\s*/, "");
        // Replace $ARGUMENTS with the company URL
        return withoutFrontmatter.replace(/\$ARGUMENTS/g, companyUrl);
      } catch (e) {
        console.warn(`[Prompt] Failed to read ${path}: ${e}`);
      }
    }
  }

  // Minimal fallback - rely on the slash command being available
  console.warn(`[Prompt] Command file not found, using minimal fallback`);
  return `Execute /blueprint-turbo ${companyUrl}

This command should generate a Blueprint GTM playbook for the company.
If the /blueprint-turbo command is not available, check that:
1. Skills are properly installed in ~/.claude/skills/ or .claude/skills/
2. Commands are properly installed in ~/.claude/commands/ or .claude/commands/
3. The systemPrompt preset is set to "claude_code"`;
}
