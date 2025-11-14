#!/bin/bash

# publish-playbook.sh - Publish Blueprint GTM Playbook to GitHub Pages
# Usage: ./publish-playbook.sh blueprint-gtm-playbook-company-name.html

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if filename provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: No filename provided${NC}"
    echo "Usage: ./publish-playbook.sh blueprint-gtm-playbook-company-name.html"
    exit 1
fi

FILENAME=$1

# Check if file exists
if [ ! -f "$FILENAME" ]; then
    echo -e "${RED}Error: File '$FILENAME' not found${NC}"
    exit 1
fi

echo -e "${BLUE}📤 Publishing playbook to GitHub Pages...${NC}"
echo ""

# Get GitHub username from publish remote (for GitHub Pages)
GH_REPO=$(git config --get remote.publish.url 2>/dev/null || echo "")

if [ -z "$GH_REPO" ]; then
    echo -e "${RED}Error: No 'publish' remote configured${NC}"
    echo "Please configure the publish remote for GitHub Pages"
    exit 1
fi

# Extract username from GitHub URL
if [[ $GH_REPO == *"github.com"* ]]; then
    GH_USERNAME=$(echo $GH_REPO | sed -E 's|.*github\.com[:/]([^/]+)/.*|\1|')
    GH_REPONAME=$(echo $GH_REPO | sed -E 's|.*github\.com[:/][^/]+/([^/]+)(\.git)?|\1|')
else
    echo -e "${RED}Error: Could not parse GitHub URL${NC}"
    exit 1
fi

# Ensure .nojekyll exists (disables Jekyll processing for faster deployment)
if [ ! -f ".nojekyll" ]; then
    echo -e "${BLUE}→ Creating .nojekyll file (first-time setup)...${NC}"
    touch .nojekyll
    git add .nojekyll
fi

# Add file to git
echo -e "${BLUE}→ Adding $FILENAME to git...${NC}"
git add "$FILENAME"

# Commit with timestamp
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
COMPANY_NAME=$(echo "$FILENAME" | sed -E 's/blueprint-gtm-playbook-(.*)\.html/\1/')
git commit -m "Publish playbook: $COMPANY_NAME ($TIMESTAMP)"

# Push to GitHub Pages (publish remote)
echo -e "${BLUE}→ Pushing to GitHub Pages...${NC}"
git push publish main 2>/dev/null || git push publish master 2>/dev/null || {
    echo -e "${RED}Error: Could not push to GitHub Pages${NC}"
    echo "Make sure the publish remote is configured and Pages are enabled"
    exit 1
}

# Generate GitHub Pages URL
PAGES_URL="https://${GH_USERNAME}.github.io/${GH_REPONAME}/${FILENAME}"

# Wait for GitHub Pages deployment (typically 10-15 seconds without Jekyll)
echo -e "${BLUE}→ Waiting for GitHub Pages deployment (10-15 seconds)...${NC}"
sleep 15

echo ""
echo -e "${GREEN}✅ Published successfully!${NC}"
echo ""
echo -e "${GREEN}📎 Shareable URL:${NC}"
echo -e "${BLUE}   $PAGES_URL${NC}"
echo ""
echo -e "${BLUE}Note: GitHub Pages deployment usually completes within 10-15 seconds${NC}"
echo -e "${BLUE}(.nojekyll file bypasses Jekyll for faster deployment).${NC}"
echo -e "${BLUE}If the URL doesn't load, wait another 10 seconds and refresh.${NC}"
echo ""
