# Render.com Deployment Guide - repli-site

## 🚀 Déployer sur Render en 5 minutes

### Étape 1 : Préparation du repo ✅ (Déjà fait!)

Les fichiers suivants ont été configurés :
- ✅ `render.yaml` - Configuration automatisée
- ✅ `backend/requirements.txt` - Dépendances Python
- ✅ `backend/config/settings.py` - Django configuré pour production

### Étape 2 : Déployer sur Render

1. **Va sur https://render.com** et crée un compte gratuit

2. **Clique "New +" → "Blueprint"**

3. **Connecte ton repo GitHub** : `Landry-kayoyo/repli-site`

4. **Sélectionne la branche** : `main`

5. **Clique "Create Resources"** 

Render va automatiquement :
- ✅ Créer le Web Service (Backend)
- ✅ Créer la Base de Données PostgreSQL
- ✅ Configurer toutes les variables d'environnement
- ✅ Installer les dépendances
- ✅ Faire les migrations
- ✅ Collecter les static files
- ✅ Démarrer le serveur

**⏱️ Attends 5-10 minutes...**

---

### Étape 3 : Récupérer l'URL du Backend

Une fois déployé :

1. Va dans la section "Services"
2. Clique sur "repli-site-backend"
3. Copie l'URL (ex: `https://repli-site-backend.render.com`)

---

### Étape 4 : Déployer le Frontend sur Vercel

1. Va sur **https://vercel.com**

2. Clique "New Project"

3. Importe ton repo GitHub

4. Configure :
   ```
   Framework: Next.js
   Root Directory: frontend
   ```

5. Ajoute la variable d'environnement :
   ```
   NEXT_PUBLIC_API_URL=https://repli-site-backend.render.com/api
   ```
   (Remplace par l'URL Render que tu as copiée)

6. Clique "Deploy"

---

### Étape 5 : Test Final

**Ton site est maintenant en ligne ! 🎉**

| Service | URL | Accès |
|---------|-----|-------|
| **Frontend** | https://repli-site.vercel.app | Public |
| **API** | https://repli-site-backend.render.com/api/ | Public |
| **Admin** | https://repli-site-backend.render.com/admin/ | Admin |

**Identifiants Admin** : `admin` / `Admin@LandryNet2024!`

---

## 🔍 Troubleshooting

### Problème : 502 Bad Gateway
**Solution** :
1. Va sur Render → "repli-site-backend"
2. Clique "Logs"
3. Cherche l'erreur
4. Si c'est une erreur de migration, redéploie manuellement

### Problème : Variables d'environnement manquantes
**Solution** :
1. Va dans Render → Service Settings
2. Scrolle jusqu'à "Environment"
3. Ajoute les variables manuellement :
   - `DEBUG=False`
   - `ALLOWED_HOSTS=.render.com,.vercel.app`
   - `SECRET_KEY=(généré automatiquement)`

### Problème : Static files ne chargent pas
**Solution** :
- C'est normal au première visite
- Attends que `collectstatic` finisse
- Force un redéploiement : Settings → "Manual Deploy"

### Problème : Frontend ne peut pas accéder l'API
**Solution** :
- Vérifie que `NEXT_PUBLIC_API_URL` pointe vers l'URL Render
- Redéploie Vercel

---

## 📝 Variables d'Environnement (configurées automatiquement)

```
DEBUG = False
ALLOWED_HOSTS = .render.com,.vercel.app,localhost,127.0.0.1
CORS_ALLOWED_ORIGINS = https://repli-site.vercel.app
DATABASE_URL = (auto-généré par Render PostgreSQL)
SECRET_KEY = (auto-généré)
FRONTEND_URL = https://repli-site.vercel.app
```

---

## 🎯 Fonctionnalités Render Utilisées

- **Web Service** : Hébergement du backend Django
- **PostgreSQL** : Base de données gratuite
- **Environment Variables** : Configuration sécurisée
- **Auto-Deploy** : Redéploiement automatique à chaque git push
- **SSL/HTTPS** : Certificat automatique

---

## 💡 Tips

1. **Logs Render** : Très utiles pour déboguer
   - Settings → Logs → voir en temps réel

2. **Auto-redeploy** : Chaque git push redéploie automatiquement

3. **Sleep mode** : Le service dormira après 15 min d'inactivité (free tier)
   - Accès à l'API le réveille automatiquement

4. **Base de données** : PostgreSQL gratuit limité mais suffisant pour commencer

---

## ✅ Checklist Avant Déploiement

- [x] `render.yaml` configuré
- [x] `requirements.txt` à jour
- [x] `settings.py` pour production
- [x] Variables d'environnement prêtes
- [ ] Compte Render créé
- [ ] Repo GitHub connecté
- [ ] Blueprint importé et déployé
- [ ] URL Backend copiée
- [ ] Frontend déployé sur Vercel
- [ ] Tests effectués

---

**Besoin d'aide ? Consulte les logs Render ou contacte le support ! 🚀**
