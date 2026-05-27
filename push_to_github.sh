#!/bin/bash
# Script de push vers GitHub — utilise GITHUB_PERSONAL_ACCESS_TOKEN

set -e

if [ -z "$GITHUB_PERSONAL_ACCESS_TOKEN" ]; then
  echo "❌ GITHUB_PERSONAL_ACCESS_TOKEN non défini."
  exit 1
fi

REPO_URL="https://${GITHUB_PERSONAL_ACCESS_TOKEN}@github.com/Landry-kayoyo/repli-site.git"

export GIT_AUTHOR_NAME="Landry Net"
export GIT_AUTHOR_EMAIL="landry@landrynet.dev"
export GIT_COMMITTER_NAME="Landry Net"
export GIT_COMMITTER_EMAIL="landry@landrynet.dev"

git add -A

if git diff --cached --quiet; then
  echo "✅ Rien à committer — tout est déjà à jour."
else
  git commit -m "fix: icônes admin, emails sans IP, beau titre, logo site, URLs production"
fi

git push origin main

echo "✅ Push GitHub réussi !"
