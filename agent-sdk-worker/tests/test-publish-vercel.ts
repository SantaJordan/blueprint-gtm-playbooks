/**
 * Test script for Vercel playbook publishing
 *
 * Usage:
 *   VERCEL_TOKEN=xxx npx tsx tests/test-publish-vercel.ts --playbook spear-education
 *
 * This tests the publishing flow in isolation without running the full worker.
 */

import { readFileSync, existsSync } from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Command line argument parsing
const args = process.argv.slice(2);
const playbookIndex = args.indexOf("--playbook");
const playbookSlug = playbookIndex !== -1 ? args[playbookIndex + 1] : "spear-education";

/**
 * Upload playbook HTML to Vercel (copied from worker.ts for isolated testing)
 */
async function uploadPlaybookToVercel(
  htmlContent: string,
  companySlug: string,
  vercelToken: string,
  projectName: string = "blueprint-playbooks"
): Promise<{ success: boolean; url?: string; error?: string }> {
  const filename = `${companySlug}.html`;

  console.log(`[Vercel] Uploading playbook: ${filename}`);

  const vercelConfig = JSON.stringify({
    rewrites: [
      { source: "/:slug", destination: "/:slug.html" }
    ]
  });

  try {
    const response = await fetch("https://api.vercel.com/v13/deployments", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${vercelToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        name: projectName,
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
          framework: null,
        }
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`[Vercel] Upload failed: ${response.status} - ${errorText}`);
      return { success: false, error: `Vercel API error: ${response.status} - ${errorText}` };
    }

    const data = await response.json();
    const deployedUrl = `https://playbooks.blueprintgtm.com/${companySlug}`;

    console.log(`[Vercel] Playbook deployed: ${deployedUrl}`);
    console.log(`[Vercel] Deployment ID: ${data.id}`);

    return { success: true, url: deployedUrl };
  } catch (e) {
    console.error(`[Vercel] Upload exception: ${e}`);
    return { success: false, error: String(e) };
  }
}

/**
 * Verify URL is accessible
 */
async function verifyUrl(url: string, maxRetries: number = 3): Promise<boolean> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      console.log(`[Test] Verifying URL (attempt ${i + 1}/${maxRetries}): ${url}`);

      // Wait before checking (Vercel deployment takes a moment)
      if (i > 0) {
        console.log(`[Test] Waiting 5 seconds...`);
        await new Promise(resolve => setTimeout(resolve, 5000));
      }

      const response = await fetch(url, { method: "HEAD" });
      if (response.ok) {
        console.log(`[Test] ✓ URL is accessible (status: ${response.status})`);
        return true;
      }
      console.log(`[Test] URL returned status: ${response.status}`);
    } catch (e) {
      console.log(`[Test] URL check failed: ${e}`);
    }
  }
  return false;
}

async function main() {
  console.log("=".repeat(60));
  console.log("Vercel Publishing Test");
  console.log("=".repeat(60));

  // Check for VERCEL_TOKEN
  const vercelToken = process.env.VERCEL_TOKEN;
  if (!vercelToken) {
    console.error("\n❌ ERROR: VERCEL_TOKEN environment variable not set");
    console.error("Usage: VERCEL_TOKEN=xxx npx tsx tests/test-publish-vercel.ts --playbook <slug>");
    process.exit(1);
  }
  console.log("✓ VERCEL_TOKEN found");

  // Find playbook file
  const playbookFilename = `blueprint-gtm-playbook-${playbookSlug}.html`;
  const possiblePaths = [
    path.join(__dirname, "../../playbooks", playbookFilename),
    path.join(__dirname, "../playbooks", playbookFilename),
    path.join(process.cwd(), "playbooks", playbookFilename),
    path.join(process.cwd(), "..", "playbooks", playbookFilename),
  ];

  let playbookPath: string | null = null;
  for (const p of possiblePaths) {
    if (existsSync(p)) {
      playbookPath = p;
      break;
    }
  }

  if (!playbookPath) {
    console.error(`\n❌ ERROR: Playbook file not found: ${playbookFilename}`);
    console.error("Searched paths:");
    possiblePaths.forEach(p => console.error(`  - ${p}`));
    process.exit(1);
  }
  console.log(`✓ Found playbook: ${playbookPath}`);

  // Read playbook content
  const htmlContent = readFileSync(playbookPath, "utf-8");
  console.log(`✓ Read ${htmlContent.length} bytes`);

  // Upload to Vercel
  console.log("\nUploading to Vercel...");
  const result = await uploadPlaybookToVercel(htmlContent, playbookSlug, vercelToken);

  if (!result.success) {
    console.error(`\n❌ UPLOAD FAILED: ${result.error}`);
    process.exit(1);
  }

  console.log(`\n✓ Upload successful!`);
  console.log(`URL: ${result.url}`);

  // Verify URL is accessible
  console.log("\nVerifying URL is accessible...");
  const isAccessible = await verifyUrl(result.url!);

  if (!isAccessible) {
    console.error("\n⚠️  WARNING: URL not immediately accessible");
    console.error("This may be due to Vercel propagation delay. Try again in a few minutes.");
    process.exit(1);
  }

  console.log("\n" + "=".repeat(60));
  console.log("✅ TEST PASSED");
  console.log("=".repeat(60));
  console.log(`Playbook published to: ${result.url}`);
}

main().catch(e => {
  console.error("Test failed with exception:", e);
  process.exit(1);
});
