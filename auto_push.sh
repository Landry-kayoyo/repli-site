#!/bin/bash
# Synchronisation automatique vers GitHub toutes les 5 minutes
# Délègue la logique git à push_to_github.sh

INTERVAL=300  # secondes entre chaque vérification
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🔄 Démarrage de la synchronisation automatique GitHub (intervalle: ${INTERVAL}s)"

if [ -z "$GITHUB_PERSONAL_ACCESS_TOKEN" ]; then
  echo "❌ GITHUB_PERSONAL_ACCESS_TOKEN non défini — synchronisation impossible."
  exit 1
fi

while true; do
  TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

  if bash "$SCRIPT_DIR/push_to_github.sh" 2>&1; then
    echo "[$TIMESTAMP] 🚀 Synchronisation GitHub terminée."
  else
    EXIT_CODE=$?
    echo "[$TIMESTAMP] ⚠️  Synchronisation GitHub échouée (code: $EXIT_CODE)."
  fi

  sleep "$INTERVAL"
done
