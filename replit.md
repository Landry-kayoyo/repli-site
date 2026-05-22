# Landry Net — Site Web Personnel (Django Full Stack)

## Architecture
- **Backend + Frontend** : Django 5.2 + Templates HTML/CSS/JS (port 5000)
- **API REST** : DRF disponible sur `/api/` pour usage AJAX
- **Base de données** : SQLite (dev) / PostgreSQL (prod)

## Démarrage
```
cd backend && python manage.py runserver 0.0.0.0:5000 --settings=config.settings
```

## Accès
- **Site public** : http://localhost:5000
- **API REST** : http://localhost:5000/api/
- **Admin Django** : http://localhost:5000/admin/
  - Username : `admin`
  - Password : `Admin@LandryNet2024!`

## Pages disponibles
- `/` — Accueil avec hero, stats, articles, projets, astuces, portfolio
- `/articles/` — Blog avec filtres par catégorie, recherche, pagination
- `/articles/<slug>/` — Détail article avec commentaires, réactions, partage
- `/projets/` — Projets + tutoriels avec filtres
- `/projets/<slug>/` — Détail projet avec liens GitHub/démo, technologies
- `/astuces/` — Astuces avec filtre de difficulté (débutant/intermédiaire/avancé)
- `/astuces/<slug>/` — Détail astuce avec commentaires et réactions
- `/portfolio/` — Réalisations avec galerie photos
- `/portfolio/<slug>/` — Détail portfolio avec galerie
- `/a-propos/` — Profil, compétences avec barres de niveau, expériences, formations
- `/contact/` — Formulaire de contact AJAX
- `/sitemap.xml` — Sitemap SEO
- `/rss/articles/` — Flux RSS articles
- `/admin/` — Administration Django

## Fonctionnalités
- ✅ Navbar responsive avec logo LN, mode sombre/clair, recherche (Ctrl+K), RSS
- ✅ Hero avec photo de profil, boutons sociaux, stats animées
- ✅ Articles, Projets, Astuces, Portfolio avec couverture, titre, sous-titre, description, contenu riche
- ✅ Commentaires avec modération et réponses imbriquées
- ✅ Réactions (👍 ❤️ 😮 👏 🔥 🔖) via AJAX
- ✅ Newsletter avec abonnement AJAX
- ✅ Recherche avancée modale (Ctrl+K)
- ✅ Mode sombre/clair avec persistance localStorage
- ✅ SEO complet (meta-tags, OG, Twitter Cards, Schema.org, Sitemap, RSS)
- ✅ PWA (manifest.json)
- ✅ Contact par formulaire AJAX
- ✅ Logo configurable depuis l'admin Django
- ✅ Floating action buttons (retour en haut + contact)
- ✅ Filtres par catégorie et difficulté
- ✅ Pagination propre
- ✅ Barre de compétences animée (à propos)
- ✅ Timeline expériences et formations
- ✅ Responsive (mobile, tablette, ordinateur)

## Structure du projet
```
backend/
  config/         — Configuration Django
  web/            — App Django templates (views.py, urls.py)
  templates/      — Templates HTML (base.html, home.html, etc.)
  static/
    css/main.css  — Styles CSS complets avec dark mode
    js/main.js    — JavaScript : theme, search, reactions, comments, newsletter
    manifest.json — PWA manifest
  articles/       — App articles avec DRF
  projects/       — App projets avec DRF
  tips/           — App astuces avec DRF
  portfolio/      — App portfolio avec DRF
  core/           — Settings du site, compétences, expériences
  contact/        — Formulaire de contact
  newsletter/     — Abonnements newsletter
  comments/       — Commentaires
  reactions/      — Réactions emoji
```

## Configuration Email Gmail (Admin Django)
1. Ouvrir l'admin Django → Paramètres du site
2. Remplir : email_host_user = votre@gmail.com
3. email_host_password = mot de passe d'application Google
4. contact_email = email qui reçoit les messages
5. Générer un mot de passe d'application : https://myaccount.google.com/apppasswords

## Variables d'environnement (backend/.env)
```
EMAIL_HOST_USER=votre@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
DEFAULT_FROM_EMAIL=votre@gmail.com
SECRET_KEY=votre-cle-secrete
```

## GitHub
- Repo : https://github.com/Landry-kayoyo/repli-site.git

## User Preferences
- Langue : Français
- Architecture : Django full stack (templates + API DRF)
- Toutes les configurations se font depuis l'admin Django
- Design : Indigo/Violet, mode sombre/clair, Inter font
