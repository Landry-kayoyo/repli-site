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
  git commit -m "✨ Suggestions IA en temps réel — articles, projets, astuces — $TIMESTAMP

Nouveau système de suggestions IA inline dans les formulaires admin :

- Nouveau endpoint /admin-ai/inline-suggest/ (core/ai_views.py)
  Retourne JSON structuré : subtitle, excerpt/description, tags, meta_title, meta_description
  Adapté par type : article (excerpt), projet (description), astuce (excerpt + difficulty)

- Panel visuel inline dans base_site.html
  Apparaît automatiquement 1,5s après frappe dans le champ titre
  Bouton Appliquer par champ + bouton Tout appliquer en un clic
  Bouton Régénérer pour relancer les suggestions
  Détection automatique du type selon l'URL admin
  Support mode sombre complet

- URL enregistrée dans config/urls.py
- Fonctionne sur : /admin/articles/article/, /admin/projects/project/, /admin/tips/tip/
- Portfolio exclu intentionnellement"
fi

git push origin main

echo "✅ Push GitHub réussi !"
