#!/usr/bin/env bash
set -e
cd ~/code/abhinavgupta707

# Make sure we're up to date with any bot pushes
git pull --rebase 2>&1 | tail -3 || true

# Remove old metrics workflow and the giant SVG outputs
git rm -f .github/workflows/metrics.yml metrics.svg metrics.plugin.achievements.svg 2>/dev/null || true

git add -A
git commit -m "feat: expand hero, condense shape-of-work to languages+radar cards, rewrite intro"
git push 2>&1 | tail -3

echo ""
echo "=== Dispatch profile summary cards workflow ==="
gh workflow run "Profile summary cards"
sleep 5
gh run list --limit 4

# Clean up self
rm -f ~/code/abhinavgupta707/.ship.sh
