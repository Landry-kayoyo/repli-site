# Landry Net — Site Web Personnel

Site personnel full-stack construit avec **Django** (backend API REST) et **Next.js** (frontend SSR).

## Tech Stack
- **Backend** : Django 5.2 + Django REST Framework + SQLite
- **Frontend** : Next.js 14 + Tailwind CSS + Framer Motion
- **Admin** : Django Admin complet avec gestion de contenu

## Fonctionnalités
- Articles, Projets, Astuces, Portfolio
- Commentaires et Réactions (👍 ❤️ 😮 👏 🔥 🔖)
- Newsletter avec envoi automatique à la publication
- Statistiques de vues (PageView tracker)
- Recherche avancée, Mode sombre/clair
- SEO complet (Sitemap, RSS, OG tags, Schema.org)
- PWA support

## Démarrage rapide

### Backend Django
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate --settings=config.settings
python manage.py create_test_data --settings=config.settings
python manage.py runserver 0.0.0.0:8000 --settings=config.settings
```

### Frontend Next.js
```bash
cd frontend
npm install
npm run dev
```

## Accès
| URL | Description |
|-----|-------------|
| http://localhost:5000 | Site public |
| http://localhost:8000/api/ | API REST |
| http://localhost:8000/admin/ | Admin Django |

**Identifiants admin :** `admin` / `Admin@LandryNet2024!`

## Configuration Newsletter Gmail
Dans l'admin Django → Paramètres du site → Configuration Email Gmail :
1. `email_host_user` = votre@gmail.com
2. `email_host_password` = mot de passe d'application Google
3. `newsletter_send_on_publish` = Oui

## Structure
```
repli-site/
├── backend/          # Django API
│   ├── articles/     # Articles & Blog
│   ├── projects/     # Projets & Tutoriels
│   ├── tips/         # Astuces
│   ├── portfolio/    # Portfolio
│   ├── newsletter/   # Newsletter
│   ├── comments/     # Commentaires
│   ├── reactions/    # Réactions
│   ├── contact/      # Formulaire contact
│   └── core/         # Paramètres, Compétences, Stats
└── frontend/         # Next.js
    ├── pages/        # Pages
    ├── components/   # Composants
    └── lib/          # API helpers
```

## Auteur
**Landry** — [GitHub](https://github.com/Landry-kayoyo)
