#!/bin/bash
# Synchronisation automatique vers GitHub toutes les 5 minutes

INTERVAL=300  # secondes entre chaque vérification

echo "🔄 Démarrage de la synchronisation automatique GitHub (intervalle: ${INTERVAL}s)"

if [ -z "$GITHUB_PERSONAL_ACCESS_TOKEN" ]; then
  echo "❌ GITHUB_PERSONAL_ACCESS_TOKEN non défini — synchronisation impossible."
  exit 1
fi

REPO_URL="https://${GITHUB_PERSONAL_ACCESS_TOKEN}@github.com/Landry-kayoyo/repli-site.git"

export GIT_AUTHOR_NAME="Landry Net"
export GIT_AUTHOR_EMAIL="landry@landrynet.dev"
export GIT_COMMITTER_NAME="Landry Net"
export GIT_COMMITTER_EMAIL="landry@landrynet.dev"

while true; do
  TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

  git add -A

  if git diff --cached --quiet; then
    echo "[$TIMESTAMP] ✅ Aucun changement détecté."
  else
    CHANGED=$(git diff --cached --name-only | head -5 | tr '\n' ', ')
    git commit -m "chore: synchronisation automatique [$TIMESTAMP]"
    echo "[$TIMESTAMP] 📦 Commit créé — fichiers: $CHANGED"
  fi

  # Synchronisation avec le dépôt distant (pull rebase + push)
  if git pull --rebase "$REPO_URL" main 2>&1; then
    if git push "$REPO_URL" HEAD:main 2>&1; then
      echo "[$TIMESTAMP] 🚀 Push GitHub réussi."
    else
      echo "[$TIMESTAMP] ⚠️  Échec du push GitHub."
    fi
  else
    echo "[$TIMESTAMP] ⚠️  Conflit lors du pull — push annulé."
    git rebase --abort 2>/dev/null || true
  fi

  sleep "$INTERVAL"
done
