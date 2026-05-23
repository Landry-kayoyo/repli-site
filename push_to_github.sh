#!/bin/bash
# Script de push vers GitHub — utilise GITHUB_PERSONAL_ACCESS_TOKEN

set -e

if [ -z "$GITHUB_PERSONAL_ACCESS_TOKEN" ]; then
  echo "❌ GITHUB_PERSONAL_ACCESS_TOKEN non défini."
  exit 1
fi

REPO_URL="https://${GITHUB_PERSONAL_ACCESS_TOKEN}@github.com/Landry-kayoyo/repli-site.git"

git remote set-url origin "$REPO_URL"

git add -A

git config user.email "landry@landrynet.dev" 2>/dev/null || true
git config user.name "Landry Net" 2>/dev/null || true

TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
git commit -m "🚀 Mise à jour Landry Net — $TIMESTAMP" 2>/dev/null || echo "Rien à committer."

git push origin main

echo "✅ Push GitHub réussi !"
