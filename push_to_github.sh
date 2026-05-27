#!/bin/bash
# Script de push vers GitHub — utilise GITHUB_PERSONAL_ACCESS_TOKEN

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
  git commit -m "chore: synchronisation automatique vers GitHub"
fi

# Récupérer les éventuels commits distants avant de pousser
if ! git pull --rebase "$REPO_URL" main 2>&1; then
  echo "⚠️  Échec du pull --rebase. Annulation du rebase."
  git rebase --abort 2>/dev/null || true
  exit 1
fi

if git push "$REPO_URL" HEAD:main 2>&1; then
  echo "✅ Push GitHub réussi !"
else
  echo "⚠️  Échec du push vers GitHub."
  exit 1
fi
