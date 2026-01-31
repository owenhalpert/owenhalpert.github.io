#!/bin/bash
# Deploy blog from Obsidian
# This script generates the blog locally, commits changes, and pushes to GitHub

cd /Users/owenhalpert/Documents/owenhalpert.github.io

# Generate blog locally for preview
echo "Generating blog..."
python3 generate_blog.py

# Add changes
echo "Adding changes to git..."
git add posts/ generate_blog.py index.html CLAUDE.md .github/

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "No changes to commit"
    exit 0
fi

# Commit with a timestamp
COMMIT_MSG="Update blog - $(date '+%Y-%m-%d %H:%M')"
echo "Committing: $COMMIT_MSG"
git commit -m "$COMMIT_MSG"

# Push to GitHub
echo "Pushing to GitHub..."
git push origin main

echo "✓ Blog deployed! GitHub Actions will build and publish it."
