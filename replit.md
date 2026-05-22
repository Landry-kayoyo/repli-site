# Landry Net — Site Web Personnel

## Architecture
- **Backend** : Django 5.2 + DRF (port 8000) — `cd backend && python3 manage.py runserver localhost:8000 --settings=config.settings`
- **Frontend** : Next.js 14 + Tailwind CSS (port 5000) — `cd frontend && npm run dev`

## Accès
- **Site public** : http://localhost:5000
- **API REST** : http://localhost:8000/api/
- **Admin Django** : http://localhost:8000/admin/
  - Username : `admin`
  - Password : `Admin@LandryNet2024!`

## Configuration Email Gmail (Admin Django)
1. Ouvrir l'admin Django → Paramètres du site
2. Remplir : email_host_user = votre@gmail.com
3. email_host_password = mot de passe d'application Google (pas votre mot de passe Gmail)
4. contact_email = l'email qui reçoit les messages de contact
5. Générer un mot de passe d'application : https://myaccount.google.com/apppasswords

## Variables d'environnement (backend/.env)
```
EMAIL_HOST_USER=votre@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
DEFAULT_FROM_EMAIL=votre@gmail.com
```

## Pages disponibles
- `/` — Accueil avec sections dynamiques
- `/articles` — Blog avec filtres et recherche
- `/projets` — Projets + tutoriels
- `/astuces` — Astuces et conseils
- `/portfolio` — Réalisations
- `/a-propos` — Profil, compétences, expériences, formations
- `/contact` — Formulaire de contact avec envoi Gmail
- `/sitemap.xml` — Sitemap SEO
- `/rss/articles/` — Flux RSS articles

## Fonctionnalités
- ✅ Dashboard admin Django complet
- ✅ Articles, Projets, Astuces, Portfolio avec couverture, titre, sous-titre, description, contenu riche
- ✅ Commentaires avec modération
- ✅ Réactions (👍 ❤️ 😮 👏 🔥 🔖)
- ✅ Newsletter avec abonnement/désabonnement
- ✅ Recherche avancée
- ✅ Mode sombre/clair
- ✅ SEO (meta-tags, OG, Twitter Cards, Schema.org, Sitemap, RSS)
- ✅ PWA (manifest.json)
- ✅ Contact par Gmail
- ✅ Logo configurable depuis l'admin
- ✅ Responsive (mobile, tablette, ordinateur)

## User Preferences
- Langue : Français
- Architecture : Django backend + Next.js frontend découplé
- Toutes les configurations se font depuis l'admin Django
