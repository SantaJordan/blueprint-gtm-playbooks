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

# Get GitHub username (will prompt for repo creation if needed)
GH_REPO=$(git config --get remote.origin.url 2>/dev/null || echo "")

if [ -z "$GH_REPO" ]; then
    echo -e "${RED}Error: No GitHub remote configured${NC}"
    echo "Please run: gh repo create blueprint-gtm-playbooks --public --source=. --remote=origin"
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

# Add file to git
echo -e "${BLUE}→ Adding $FILENAME to git...${NC}"
git add "$FILENAME"

# Commit with timestamp
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
COMPANY_NAME=$(echo "$FILENAME" | sed -E 's/blueprint-gtm-playbook-(.*)\.html/\1/')
git commit -m "Publish playbook: $COMPANY_NAME ($TIMESTAMP)"

# Push to GitHub
echo -e "${BLUE}→ Pushing to GitHub...${NC}"
git push origin main 2>/dev/null || git push origin master 2>/dev/null || {
    echo -e "${RED}Error: Could not push to GitHub${NC}"
    echo "Make sure you've created the GitHub repository and enabled Pages"
    exit 1
}

# Generate GitHub Pages URL
PAGES_URL="https://${GH_USERNAME}.github.io/${GH_REPONAME}/${FILENAME}"

echo ""
echo -e "${GREEN}✅ Published successfully!${NC}"
echo ""
echo -e "${GREEN}📎 Shareable URL:${NC}"
echo -e "${BLUE}   $PAGES_URL${NC}"
echo ""
echo -e "${BLUE}Note: GitHub Pages may take 1-2 minutes to build and deploy.${NC}"
echo -e "${BLUE}If the URL doesn't work immediately, wait a moment and try again.${NC}"
echo ""
