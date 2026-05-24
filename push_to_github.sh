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
  git commit -m "✨ Refonte Landry Net — Hero centré, Tech Stack DB, Admin mobile, Fix emails — $TIMESTAMP

Changements principaux :
- Hero homepage : centré sans photo (clean mobile), pills de stats
- Stats section (grille 3/6 cartes) : supprimée de la homepage
- Nouveau modèle Technology (tech stack piloté depuis admin Django)
  - Migration : core/0005_add_technology.py
  - Widget recherche Bootstrap Icons en live dans l'admin
- Fix emails contact + newsletter : get_connection() thread-safe
- Admin Django : navbar mobile améliorée, meilleurs touch targets,
  header compact, inputs 44px, tables scrollables, submit-row vertical
- Footer mobile : Navigation + Autres côte à côte
- README (replit.md) : mise à jour avec commandes de migration prod"
fi

git push origin main

echo "✅ Push GitHub réussi !"
