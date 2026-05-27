# Landry Net — Site Web Personnel (Django Full Stack)

## Architecture
- **Backend + Frontend** : Django 5.2 + Templates HTML/CSS/JS (port 5000)
- **API REST** : DRF disponible sur `/api/` pour usage AJAX
- **Base de données** : SQLite (dev) / PostgreSQL (prod)

## Démarrage
```bash
cd backend && python manage.py runserver 0.0.0.0:5000 --settings=config.settings
```

## Accès
- **Site public** : http://localhost:5000
- **API REST** : http://localhost:5000/api/
- **Admin Django** : http://localhost:5000/admin/
  - Username : `admin`
  - Password : `Admin@LandryNet2024!`

## Pages disponibles
- `/` — Accueil : hero centré, features, tech stack, articles, projets, astuces, portfolio
- `/articles/` — Blog avec filtres catégorie, recherche, pagination
- `/articles/<slug>/` — Détail article avec commentaires, réactions, partage
- `/projets/` — Projets + tutoriels avec filtres
- `/projets/<slug>/` — Détail projet avec liens GitHub/démo, technologies
- `/astuces/` — Astuces avec filtre difficulté (débutant/intermédiaire/avancé)
- `/astuces/<slug>/` — Détail astuce avec commentaires et réactions
- `/portfolio/` — Réalisations avec galerie photos
- `/portfolio/<slug>/` — Détail portfolio avec galerie
- `/a-propos/` — Profil, compétences, expériences, formations
- `/contact/` — Formulaire de contact AJAX (thread-safe)
- `/sitemap.xml` — Sitemap SEO
- `/rss/articles/` — Flux RSS articles
- `/admin/` — Administration Django (custom UI indigo/violet)
- `/admin-ai/newsletter/` — Gestion newsletter (composer, envoyer, historique)

## Fonctionnalités
- ✅ Navbar responsive : logo LN, mode sombre/clair, recherche (Ctrl+K), RSS
- ✅ Hero centré sans photo (propre sur mobile), pills de stats, réseaux sociaux
- ✅ Section Features (4 cartes) : articles, projets, astuces, portfolio
- ✅ **Section Tech Stack piloté depuis l'admin** — modèle `Technology` (nom, icône Bootstrap Icons, couleur, lien)
- ✅ Articles, Projets, Astuces, Portfolio avec couverture, titre, sous-titre, contenu riche (CKEditor)
- ✅ Commentaires avec modération et réponses imbriquées
- ✅ Réactions (👍 ❤️ 😮 👏 🔥 🔖) via AJAX
- ✅ Newsletter avec abonnement AJAX (envoi thread-safe avec `get_connection()`)
- ✅ **Gestion Newsletter** : composer, envoyer, historique des campagnes depuis l'admin IA
- ✅ Contact par formulaire AJAX (envoi SMTP thread-safe)
- ✅ **SMTP auto-détection** : si l'hôte contient un `@`, le bon serveur SMTP est détecté automatiquement (Gmail, Yahoo, Outlook, iCloud…)
- ✅ Recherche avancée modale (Ctrl+K)
- ✅ Mode sombre/clair avec persistance localStorage (site + admin)
- ✅ SEO complet (meta-tags, OG, Twitter Cards, Schema.org, Sitemap, RSS)
- ✅ **OG image intelligente** : homepage et pages contenu → logo du site ; page à-propos → logo du site ou photo de profil
- ✅ PWA (manifest.json)
- ✅ Logo configurable depuis l'admin Django (affiché aussi dans l'en-tête admin)
- ✅ Floating action buttons (retour en haut + contact)
- ✅ Filtres par catégorie et difficulté
- ✅ Pagination propre
- ✅ Barre de compétences animée (à propos)
- ✅ Timeline expériences et formations
- ✅ Responsive mobile-first — images chargées sans animation de scroll
- ✅ Admin Django custom : couleurs indigo/violet, mode sombre complet, IA intégrée, notifications, search Bootstrap Icons
- ✅ **Assistant IA** : génération de contenu professionnel complet (article/projet/astuce), SEO, analyse, newsletter
- ✅ **Bouton IA** disparaît à l'ouverture du panneau (pas de superposition sur mobile)
- ✅ **Sélecteur d'auteur** dans la barre de publication IA
- ✅ HTML rendu dans les réponses IA (titres, listes, code formatés)

## Captures d'écran — État actuel

### Page d'accueil (`/`)
Hero centré "Bonjour, je suis Landry" avec pills de stats (articles, projets, astuces, abonnés),
boutons "Explorer le blog" et "À propos", navbar indigo avec recherche et mode sombre.

### Admin Dashboard (`/admin/`)
Tableau de bord indigo/violet avec cartes KPI (articles, projets, astuces, abonnés),
graphique de vues 7 jours, actions rapides, bannière IA, mode sombre complet.

### Assistant IA (`/admin/` → bouton ✨)
Panneau flottant avec historique de conversation, actions rapides (SEO, Idées, Article, Lacunes),
champ de saisie avec bouton Envoyer — sans superposition sur mobile.

### Newsletter (`/admin-ai/newsletter/`)
Stats abonnés, formulaire composer sujet + contenu, bouton envoi immédiat ou brouillon,
historique des campagnes avec statut et bouton réutiliser.

### Diagnostic Email (`/admin/core/diagnostic/`)
Test SMTP étape par étape, détection automatique du serveur SMTP (si email tapé en hôte),
envoi d'email de test, configuration affichée clairement.

## Structure du projet
```
backend/
  config/         — Configuration Django
  web/            — App Django templates (views.py, urls.py)
  templates/      — Templates HTML (base.html, home.html, etc.)
    admin/        — Templates admin personnalisés
  static/
    css/main.css  — Styles CSS complets avec dark mode
    js/main.js    — JavaScript : theme, search, reactions, comments, newsletter
    manifest.json — PWA manifest
  articles/       — App articles avec DRF
  projects/       — App projets avec DRF
  tips/           — App astuces avec DRF
  portfolio/      — App portfolio avec DRF
  core/           — Settings du site, compétences, expériences, technologies, IA
  contact/        — Formulaire de contact
  newsletter/     — Abonnements newsletter + campagnes
  comments/       — Commentaires
  reactions/      — Réactions emoji
```

## Ajouter des technologies (Tech Stack section)
1. Aller sur `/admin/core/technology/`
2. Cliquer **Ajouter Technologie**
3. Remplir le nom (ex: Python), l'icône Bootstrap Icons (utiliser la recherche intégrée), la couleur hex, le lien docs
4. Sauvegarder → apparaît immédiatement sur la homepage

## Configuration Email Gmail (Admin Django)
1. Ouvrir l'admin Django → Paramètres du site
2. Remplir : `Compte Gmail` = votre@gmail.com
3. `Mot de passe app.` = mot de passe d'application Google (16 caractères)
4. `Email de contact` = email qui reçoit les messages
5. **Le champ "Hôte SMTP" peut rester vide** — il est auto-détecté depuis votre adresse email
6. Générer un mot de passe d'application : https://myaccount.google.com/apppasswords

> **Note SMTP** : Si vous avez accidentellement tapé votre adresse email dans le champ "Hôte",
> ce n'est pas grave — le système corrige automatiquement en utilisant `smtp.gmail.com`.

## Variables d'environnement (backend/.env)
```
EMAIL_HOST_USER=votre@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
DEFAULT_FROM_EMAIL=votre@gmail.com
SECRET_KEY=votre-cle-secrete
```

## Migrations — Mettre à jour la base de données en production

### Après chaque déploiement (nouvelles migrations)
```bash
cd backend
python manage.py migrate --settings=config.settings
```

### Si tu ajoutes un modèle ou un champ
```bash
cd backend
python manage.py makemigrations --settings=config.settings
python manage.py migrate --settings=config.settings
```

### Migrations ajoutées dans cette version
| Migration | App | Description |
|---|---|---|
| `core/0005_add_technology.py` | core | Nouveau modèle Technology (tech stack homepage) |

### Commandes complètes pour mettre à jour le serveur en production
```bash
# 1. Récupérer le code
git pull origin main

# 2. Installer les dépendances (si nouvelles)
pip install -r requirements.txt

# 3. Appliquer les migrations
cd backend && python manage.py migrate --settings=config.settings

# 4. Recollecte des fichiers statiques
python manage.py collectstatic --noinput --settings=config.settings

# 5. Redémarrer le serveur (gunicorn/supervisord selon hébergeur)
# systemctl restart gunicorn  (ou selon ton setup)
```

## Push vers GitHub
```bash
./push_to_github.sh
```
Nécessite `GITHUB_PERSONAL_ACCESS_TOKEN` dans les variables d'environnement Replit.

## GitHub
- Repo : https://github.com/Landry-kayoyo/repli-site.git

## User Preferences
- Langue : Français
- Architecture : Django full stack (templates + API DRF)
- Toutes les configurations se font depuis l'admin Django
- Design : Indigo/Violet, mode sombre/clair, Inter/Plus Jakarta Sans font
- Pas de section stats (grille de cartes) sur la homepage
- Pas d'animations de chargement lors du scroll — les images se chargent directement
