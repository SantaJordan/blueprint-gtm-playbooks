# Blueprint GitHub Publish Skill

Publishes Blueprint GTM playbooks to GitHub Pages and returns a live URL.

## Description

This skill handles the git operations needed to publish a playbook HTML file to GitHub Pages:
1. Copies the playbook from `playbooks/` to `docs/` (GitHub Pages serving folder)
2. Stages both files
3. Creates a commit
4. Pushes to the remote repository
5. Generates the GitHub Pages URL (at root path, no `/playbooks/` prefix)
6. Verifies the deployment is live

## Usage

This skill is invoked automatically by `/blueprint-turbo` after generating a playbook. It can also be invoked manually:

```
Skill(skill: "blueprint-github-publish")
```

**Input:** The skill expects the playbook path to be available from the preceding turbo execution (via `PLAYBOOK_PATH:` marker in context).

**Output:** GitHub Pages URL + verification status

---

## Execution Flow

### Step 1: Extract Playbook Path

Parse the playbook path from context. Look for the `PLAYBOOK_PATH:` marker from the preceding turbo execution.

If no marker found, look for the most recently modified HTML file in `playbooks/`:
```bash
ls -t playbooks/*.html | head -1
```

### Step 2: Verify Git Repository

```bash
git rev-parse --git-dir 2>/dev/null
```

If not in a git repository:
- Output error: "Not in a git repository. Playbook saved locally but not published."
- Exit gracefully (don't break the flow)

### Step 3: Get Remote Information

Use `origin` remote (the main repository where GitHub Pages is configured):

```bash
# Use origin remote
REMOTE_URL=$(git config --get remote.origin.url)
REMOTE_NAME="origin"
```

Extract GitHub username and repo name from the remote URL:
- SSH format: `git@github.com:username/repo.git`
- HTTPS format: `https://github.com/username/repo.git`

**Note:** Repo name in GitHub Pages URLs is lowercase (e.g., `blueprint-gtm-skills` not `Blueprint-GTM-Skills`).

### Step 4: Copy to docs/ Folder

GitHub Pages serves from the `docs/` folder at the root URL path. Copy the playbook there:

```bash
# Extract filename from path
FILENAME=$(basename [playbook-path])

# Copy to docs/ folder for GitHub Pages serving
cp [playbook-path] docs/$FILENAME
```

### Step 5: Ensure .nojekyll Exists

GitHub Pages uses Jekyll by default, which ignores files starting with underscore and processes certain files. The `.nojekyll` file in `docs/` disables this:

```bash
if [ ! -f "docs/.nojekyll" ]; then
    touch docs/.nojekyll
    git add docs/.nojekyll
fi
```

### Step 6: Stage and Commit

```bash
# Stage both locations (playbooks/ may be in .gitignore, so use -f)
git add -f [playbook-path]
git add docs/$FILENAME

# Create commit with descriptive message
git commit -m "Publish Blueprint GTM playbook: [company-name]"
```

Extract company name from filename:
- `blueprint-gtm-playbook-owner.html` → `Owner`
- `blueprint-gtm-playbook-canvas-medical.html` → `Canvas Medical`

### Step 7: Push to Remote

```bash
# Try main branch first, then master
git push $REMOTE_NAME main 2>/dev/null || git push $REMOTE_NAME master
```

If push fails:
- Output error with details
- Suggest checking remote access/permissions
- Exit gracefully

### Step 8: Generate GitHub Pages URL

Construct the URL using only the filename (GitHub Pages serves from docs/ at root):
```
https://[username].github.io/[repo-name-lowercase]/[filename-only]
```

Example:
```
https://santajordan.github.io/blueprint-gtm-skills/blueprint-gtm-playbook-owner.html
```

**Important:** The URL does NOT include `/playbooks/` or `/docs/` - files in `docs/` are served at the root path.

### Step 9: Verify Deployment (with Retries)

GitHub Pages can take 30-60 seconds to deploy. Poll the URL with retries:

```bash
MAX_ATTEMPTS=4
DELAYS=(5 10 15 20)  # Increasing delays between attempts

for i in $(seq 0 $((MAX_ATTEMPTS-1))); do
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$PAGES_URL")

    if [ "$HTTP_STATUS" = "200" ]; then
        echo "Verified live (HTTP 200)"
        break
    fi

    if [ $i -lt $((MAX_ATTEMPTS-1)) ]; then
        sleep ${DELAYS[$i]}
    fi
done
```

---

## Output Format

**Success:**
```
Publishing to GitHub Pages...
Copied to docs/ folder
Pushed to GitHub
URL: https://santajordan.github.io/blueprint-gtm-skills/blueprint-gtm-playbook-owner.html
Verified live (HTTP 200)
```

**Push succeeded but verification pending:**
```
Publishing to GitHub Pages...
Copied to docs/ folder
Pushed to GitHub
URL: https://santajordan.github.io/blueprint-gtm-skills/blueprint-gtm-playbook-owner.html
Deployment pending (may take 1-2 minutes to go live)
```

**Error (not in git repo):**
```
Not in a git repository. Playbook saved locally at:
playbooks/blueprint-gtm-playbook-owner.html
```

**Error (push failed):**
```
Failed to push to GitHub. Check remote access/permissions.
Playbook saved locally at: playbooks/blueprint-gtm-playbook-owner.html
```

---

## Error Handling

This skill should NEVER break the turbo flow. All errors are handled gracefully:

| Scenario | Behavior |
|----------|----------|
| Not in git repo | Output local path, skip publish |
| No remote configured | Output local path, skip publish |
| Push fails (auth/permissions) | Output error + local path |
| Verification times out | Output URL + "pending" status |
| File doesn't exist | Output error, suggest checking turbo output |

---

## Implementation Notes

1. **No interactive prompts:** All git operations must be non-interactive
2. **No force push:** Never use `--force` to avoid overwriting others' work
3. **No config changes:** Never modify git config (username, email, etc.)
4. **Graceful degradation:** Playbook is always available locally even if publish fails
