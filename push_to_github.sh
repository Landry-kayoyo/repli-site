#!/bin/bash
# Script de push vers GitHub — utilise GITHUB_PERSONAL_ACCESS_TOKEN

set -e

if [ -z "$GITHUB_PERSONAL_ACCESS_TOKEN" ]; then
  echo "❌ GITHUB_PERSONAL_ACCESS_TOKEN non défini."
  exit 1
fi

REPO_URL="https://${GITHUB_PERSONAL_ACCESS_TOKEN}@github.com/Landry-kayoyo/repli-site.git"

git config user.email "landry@landrynet.dev" 2>/dev/null || true
git config user.name "Landry Net" 2>/dev/null || true

git remote set-url origin "$REPO_URL" 2>/dev/null || git remote add origin "$REPO_URL"

git add -A

TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
if git diff --cached --quiet; then
  echo "✅ Rien à committer — tout est déjà à jour."
else
  git commit -m "🚀 Refonte complète Landry Net — Design, Email, IA boostée, Optimisations — $TIMESTAMP"
fi

git push origin main

echo "✅ Push GitHub réussi !"
