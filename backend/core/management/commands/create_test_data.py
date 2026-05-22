from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Crée des données de test pour le site Landry Net'

    def handle(self, *args, **kwargs):
        self.stdout.write('Création des données de test...')

        # Get or create admin user
        user, _ = User.objects.get_or_create(
            username='admin',
            defaults={'first_name': 'Landry', 'last_name': 'K.', 'email': 'admin@landrynet.com', 'is_staff': True, 'is_superuser': True}
        )
        if not user.first_name:
            user.first_name = 'Landry'
            user.last_name = 'K.'
            user.save()

        # ---- SiteSettings ----
        from core.models import SiteSettings, Skill, Experience, Education
        settings, _ = SiteSettings.objects.get_or_create(pk=1)
        settings.site_name = 'Landry Net'
        settings.tagline = 'Partager, Apprendre, Innover'
        settings.description = 'Site personnel de Landry — développeur passionné par la technologie et le partage de connaissances.'
        settings.author_name = 'Landry'
        settings.author_bio = "Développeur full-stack passionné par les nouvelles technologies. J'aime partager mes connaissances à travers des articles, tutoriels et projets open-source."
        settings.author_location = 'Paris, France'
        settings.author_job_title = 'Développeur Full-Stack & Créateur de contenu'
        settings.about_title = 'À propos de moi'
        settings.about_content = "<p>Bonjour ! Je suis <strong>Landry</strong>, développeur full-stack avec une passion pour la technologie et l'enseignement.</p><p>Je crée du contenu technique pour aider la communauté francophone à apprendre la programmation moderne.</p><p>Sur ce site vous trouverez des articles, tutoriels, astuces et projets pratiques.</p>"
        settings.github_url = 'https://github.com/Landry-kayoyo'
        settings.newsletter_send_on_publish = False
        settings.newsletter_intro_text = 'Bonjour ! Voici une nouvelle publication sur Landry Net.'
        settings.newsletter_from_name = 'Landry Net'
        settings.save()
        self.stdout.write(self.style.SUCCESS('✅ SiteSettings mis à jour'))

        # ---- Skills ----
        skills_data = [
            ('Python', 90, '🐍', 'Backend'),
            ('Django', 88, '🎸', 'Backend'),
            ('JavaScript', 85, '⚡', 'Frontend'),
            ('React / Next.js', 82, '⚛️', 'Frontend'),
            ('TypeScript', 75, '📘', 'Frontend'),
            ('Node.js', 70, '🟢', 'Backend'),
            ('PostgreSQL', 78, '🐘', 'Base de données'),
            ('Docker', 65, '🐳', 'DevOps'),
            ('Git / GitHub', 90, '🔀', 'DevOps'),
            ('Tailwind CSS', 88, '🎨', 'Frontend'),
            ('REST API', 85, '🔌', 'Backend'),
            ('Linux', 72, '🐧', 'DevOps'),
        ]
        for i, (name, level, icon, category) in enumerate(skills_data):
            Skill.objects.get_or_create(name=name, defaults={'level': level, 'icon': icon, 'category': category, 'order': i})
        self.stdout.write(self.style.SUCCESS(f'✅ {len(skills_data)} compétences créées'))

        # ---- Experiences ----
        from datetime import date
        experiences_data = [
            ('Développeur Full-Stack', 'Freelance', 'Paris, France', date(2022, 1, 1), None, True, 'Développement d\'applications web sur mesure pour des clients en France et à l\'international. Stack principale : Django, React, PostgreSQL, Docker.'),
            ('Développeur Backend Python', 'Tech Startup', 'Lyon, France', date(2020, 3, 1), date(2021, 12, 31), False, 'Développement et maintenance d\'APIs REST avec Django et DRF. Mise en place de pipelines CI/CD avec GitHub Actions.'),
            ('Développeur Web Junior', 'Agence Digitale', 'Paris, France', date(2018, 6, 1), date(2020, 2, 28), False, 'Développement de sites web et applications web. HTML, CSS, JavaScript, PHP, WordPress.'),
        ]
        for i, (title, company, location, start, end, current, desc) in enumerate(experiences_data):
            Experience.objects.get_or_create(
                title=title, company=company,
                defaults={'location': location, 'start_date': start, 'end_date': end, 'is_current': current, 'description': desc, 'order': i}
            )
        self.stdout.write(self.style.SUCCESS(f'✅ {len(experiences_data)} expériences créées'))

        # ---- Education ----
        educations_data = [
            ('Master Informatique', 'Université Paris Saclay', 'Paris, France', date(2016, 9, 1), date(2018, 6, 30), False, 'Spécialisation en Génie Logiciel et Systèmes Distribués.'),
            ('Licence Informatique', 'Université Paris 6', 'Paris, France', date(2013, 9, 1), date(2016, 6, 30), False, 'Fondamentaux de l\'informatique, algorithmique, bases de données.'),
        ]
        for i, (degree, institution, location, start, end, current, desc) in enumerate(educations_data):
            Education.objects.get_or_create(
                degree=degree, institution=institution,
                defaults={'location': location, 'start_date': start, 'end_date': end, 'is_current': current, 'description': desc, 'order': i}
            )
        self.stdout.write(self.style.SUCCESS(f'✅ {len(educations_data)} formations créées'))

        # ---- Article Categories ----
        from articles.models import Category, Article
        categories_data = [
            ('Python', 'python', '🐍', '#3B82F6'),
            ('Django', 'django', '🎸', '#4F46E5'),
            ('JavaScript', 'javascript', '⚡', '#F59E0B'),
            ('React', 'react', '⚛️', '#06B6D4'),
            ('DevOps', 'devops', '🚀', '#10B981'),
            ('Tutoriels', 'tutoriels', '📚', '#8B5CF6'),
        ]
        cats = {}
        for name, slug, icon, color in categories_data:
            cat, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name, 'icon': icon, 'color': color})
            cats[slug] = cat
        self.stdout.write(self.style.SUCCESS(f'✅ {len(categories_data)} catégories articles créées'))

        # ---- Articles ----
        articles_data = [
            (
                'Créer une API REST avec Django REST Framework',
                'Guide complet pour débutants',
                'django',
                'Dans ce tutoriel, nous allons créer une API REST complète avec Django REST Framework. Vous apprendrez à créer des endpoints, gérer l\'authentification JWT, la pagination et bien plus encore.',
                '''<h2>Introduction</h2>
<p>Django REST Framework (DRF) est l\'une des bibliothèques les plus populaires pour créer des API REST en Python. Dans ce tutoriel, nous allons créer une API complète étape par étape.</p>

<h2>Installation</h2>
<pre><code>pip install djangorestframework
pip install djangorestframework-simplejwt</code></pre>

<h2>Configuration de base</h2>
<p>Ajoutez DRF dans vos INSTALLED_APPS :</p>
<pre><code>INSTALLED_APPS = [
    ...
    \'rest_framework\',
    \'rest_framework_simplejwt\',
]</code></pre>

<h2>Créer votre premier serializer</h2>
<pre><code>from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = \'__all__\'</code></pre>

<h2>Créer les vues</h2>
<pre><code>from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Article
from .serializers import ArticleSerializer

class ArticleListView(generics.ListAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [AllowAny]</code></pre>

<h2>Conclusion</h2>
<p>Vous avez maintenant une API REST fonctionnelle avec Django. Dans le prochain tutoriel, nous verrons comment ajouter l\'authentification JWT.</p>''',
                True,
                8
            ),
            (
                'Next.js 14 : Les nouveautés à connaître',
                'App Router, Server Components, et plus encore',
                'react',
                'Next.js 14 apporte de nombreuses améliorations majeures. Découvrez les nouvelles fonctionnalités qui vont changer votre façon de développer des applications React.',
                '''<h2>Next.js 14 — Ce qui change</h2>
<p>Next.js 14 est une mise à jour majeure qui apporte des améliorations significatives en termes de performance et de développement.</p>

<h2>App Router stable</h2>
<p>L\'App Router est maintenant stable en production. Il offre :</p>
<ul>
<li>Server Components par défaut</li>
<li>Meilleure gestion du cache</li>
<li>Layouts imbriqués</li>
<li>Loading states automatiques</li>
</ul>

<h2>Server Actions</h2>
<p>Les Server Actions permettent d\'exécuter du code serveur directement depuis vos composants :</p>
<pre><code>async function createPost(formData) {
  \'use server\'
  const title = formData.get(\'title\')
  await db.insert({ title })
}

export default function Form() {
  return (
    &lt;form action={createPost}&gt;
      &lt;input name="title" /&gt;
      &lt;button type="submit"&gt;Créer&lt;/button&gt;
    &lt;/form&gt;
  )
}</code></pre>

<h2>Partial Prerendering</h2>
<p>Une nouvelle stratégie de rendu qui combine le statique et le dynamique pour de meilleures performances.</p>''',
                True,
                6
            ),
            (
                'Docker pour développeurs Python : Guide pratique',
                'Containerisez vos applications Django',
                'devops',
                'Apprenez à containeriser vos applications Django avec Docker. De la création du Dockerfile à l\'orchestration avec Docker Compose, ce guide couvre tout ce dont vous avez besoin.',
                '''<h2>Pourquoi Docker ?</h2>
<p>Docker permet d\'isoler votre application et ses dépendances dans un conteneur portable. Fini les problèmes de "ça marche sur ma machine" !</p>

<h2>Dockerfile pour Django</h2>
<pre><code>FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]</code></pre>

<h2>Docker Compose</h2>
<pre><code>version: \'3.8\'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgres://user:pass@db:5432/mydb
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:</code></pre>

<h2>Déploiement</h2>
<p>Avec Docker Compose, déployer est simple :</p>
<pre><code>docker-compose up -d --build</code></pre>''',
                False,
                10
            ),
            (
                'Python 3.12 : Les nouvelles fonctionnalités',
                'Pattern matching, f-strings améliorés et plus',
                'python',
                'Python 3.12 est sorti avec son lot de nouvelles fonctionnalités passionnantes. Découvrez ce qui change et comment en tirer parti dans vos projets.',
                '''<h2>Nouveautés de Python 3.12</h2>
<p>Python 3.12 apporte plusieurs améliorations importantes pour les développeurs.</p>

<h2>F-strings améliorées</h2>
<p>Les f-strings supportent maintenant plus de syntaxe complexe :</p>
<pre><code># Python 3.12 - Maintenant possible
result = f"{'Bonjour':>20}"
data = f"{{"key": "value"}}"  # Accolades littérales</code></pre>

<h2>Typage amélioré</h2>
<pre><code>from typing import TypeVar, Generic

T = TypeVar(\'T\')

class Stack[T]:  # Nouvelle syntaxe !
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()</code></pre>

<h2>Performances</h2>
<p>Python 3.12 est jusqu\'à 5% plus rapide que Python 3.11, grâce à des optimisations du compilateur.</p>''',
                True,
                5
            ),
            (
                'Authentification JWT avec Django et React',
                'Sécurisez vos APIs en 30 minutes',
                'django',
                'L\'authentification JWT est un standard pour sécuriser les APIs REST. Dans ce tutoriel, nous implémentons un système d\'auth complet avec Django côté serveur et React côté client.',
                '''<h2>Introduction au JWT</h2>
<p>JSON Web Tokens (JWT) est un standard ouvert pour créer des tokens d\'accès sécurisés.</p>

<h2>Installation Django</h2>
<pre><code>pip install djangorestframework-simplejwt</code></pre>

<h2>Configuration</h2>
<pre><code>from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}</code></pre>

<h2>Côté React</h2>
<pre><code>const login = async (username, password) => {
  const response = await fetch(\'/api/token/\', {
    method: \'POST\',
    headers: { \'Content-Type\': \'application/json\' },
    body: JSON.stringify({ username, password }),
  })
  const data = await response.json()
  localStorage.setItem(\'access_token\', data.access)
  localStorage.setItem(\'refresh_token\', data.refresh)
}</code></pre>''',
                False,
                7
            ),
        ]

        created_articles = 0
        for title, subtitle, cat_slug, excerpt, content, featured, read_time in articles_data:
            slug = slugify(title)
            if not Article.objects.filter(slug=slug).exists():
                Article.objects.create(
                    title=title, subtitle=subtitle, slug=slug,
                    author=user, category=cats.get(cat_slug),
                    excerpt=excerpt, content=content,
                    status='published', is_featured=featured,
                    read_time=read_time, views_count=0,
                    published_at=timezone.now(),
                )
                created_articles += 1
        self.stdout.write(self.style.SUCCESS(f'✅ {created_articles} articles créés'))

        # ---- Project Categories ----
        from projects.models import ProjectCategory, Project
        proj_cats_data = [
            ('Web App', 'web-app', '🌐', '#4F46E5'),
            ('API / Backend', 'api-backend', '⚙️', '#10B981'),
            ('Mobile', 'mobile', '📱', '#F59E0B'),
            ('Open Source', 'open-source', '🔓', '#EF4444'),
        ]
        proj_cats = {}
        for name, slug, icon, color in proj_cats_data:
            cat, _ = ProjectCategory.objects.get_or_create(slug=slug, defaults={'name': name, 'icon': icon, 'color': color})
            proj_cats[slug] = cat

        projects_data = [
            (
                'Landry Net — Site Web Personnel',
                'Django + Next.js avec admin complet',
                'web-app',
                'Site personnel full-stack avec Django backend, Next.js frontend, gestion de contenu via admin, newsletter, commentaires et réactions.',
                '''<h2>Présentation du projet</h2>
<p>Landry Net est mon site personnel construit avec une architecture moderne découplée.</p>
<h2>Stack technique</h2>
<ul>
<li><strong>Backend</strong> : Django 5.2 + Django REST Framework</li>
<li><strong>Frontend</strong> : Next.js 14 + Tailwind CSS + Framer Motion</li>
<li><strong>Base de données</strong> : SQLite (dev) / PostgreSQL (prod)</li>
</ul>
<h2>Fonctionnalités</h2>
<ul>
<li>Articles, projets, astuces, portfolio</li>
<li>Newsletter automatique</li>
<li>Commentaires et réactions</li>
<li>Mode sombre/clair</li>
<li>PWA support</li>
</ul>''',
                'Django, Next.js, Tailwind CSS, DRF, Python',
                'https://github.com/Landry-kayoyo/repli-site',
                True,
            ),
            (
                'API de gestion de tâches avec Django',
                'Todo API REST avec authentification JWT',
                'api-backend',
                'Une API REST complète pour gérer des tâches avec authentification JWT, filtres avancés, pagination et documentation Swagger.',
                '''<h2>Architecture de l\'API</h2>
<p>Cette API suit les principes REST et propose une documentation Swagger automatique.</p>
<h2>Endpoints</h2>
<pre><code>GET    /api/tasks/       # Liste des tâches
POST   /api/tasks/       # Créer une tâche
GET    /api/tasks/{id}/  # Détail d\'une tâche
PUT    /api/tasks/{id}/  # Mettre à jour
DELETE /api/tasks/{id}/  # Supprimer</code></pre>
<h2>Authentification</h2>
<p>L\'API utilise JWT pour sécuriser les endpoints. Obtenez votre token avec :</p>
<pre><code>POST /api/token/ { "username": "...", "password": "..." }</code></pre>''',
                'Django, DRF, JWT, PostgreSQL, Swagger',
                'https://github.com/Landry-kayoyo',
                True,
            ),
            (
                'Dashboard Analytics avec React et Chart.js',
                'Visualisation de données en temps réel',
                'web-app',
                'Un dashboard de visualisation de données construit avec React, utilisant Chart.js pour les graphiques et un backend Express.js pour les données.',
                '''<h2>Présentation</h2>
<p>Ce dashboard propose des visualisations interactives pour analyser vos données.</p>
<h2>Technologies</h2>
<ul>
<li>React 18 avec hooks</li>
<li>Chart.js 4 pour les graphiques</li>
<li>TailwindCSS pour le style</li>
<li>Express.js backend</li>
</ul>
<h2>Types de graphiques</h2>
<p>Line charts, Bar charts, Pie charts, Area charts, et tableaux de données.</p>''',
                'React, Chart.js, Tailwind CSS, Node.js, Express',
                'https://github.com/Landry-kayoyo',
                False,
            ),
        ]

        created_projects = 0
        for title, subtitle, cat_slug, description, content, technologies, github_url, featured in projects_data:
            slug = slugify(title)
            if not Project.objects.filter(slug=slug).exists():
                Project.objects.create(
                    title=title, subtitle=subtitle, slug=slug,
                    author=user, category=proj_cats.get(cat_slug),
                    description=description, content=content,
                    technologies=technologies, github_url=github_url,
                    status='published', is_featured=featured,
                    views_count=0, published_at=timezone.now(),
                )
                created_projects += 1
        self.stdout.write(self.style.SUCCESS(f'✅ {created_projects} projets créés'))

        # ---- Tips Categories ----
        from tips.models import TipCategory, Tip
        tip_cats_data = [
            ('Python', 'python-tips', '🐍', '#3B82F6'),
            ('Git', 'git', '🔀', '#EF4444'),
            ('Terminal', 'terminal', '💻', '#6B7280'),
            ('VS Code', 'vscode', '🔵', '#06B6D4'),
            ('Django', 'django-tips', '🎸', '#4F46E5'),
        ]
        tip_cats = {}
        for name, slug, icon, color in tip_cats_data:
            cat, _ = TipCategory.objects.get_or_create(slug=slug, defaults={'name': name, 'icon': icon, 'color': color})
            tip_cats[slug] = cat

        tips_data = [
            (
                '10 raccourcis VS Code indispensables',
                'Boostez votre productivité',
                'vscode',
                'Maîtrisez ces raccourcis VS Code et doublez votre productivité en quelques jours.',
                '''<h2>Les raccourcis essentiels</h2>
<ul>
<li><code>Ctrl+P</code> — Ouvrir un fichier rapidement</li>
<li><code>Ctrl+Shift+P</code> — Palette de commandes</li>
<li><code>Ctrl+`</code> — Ouvrir/fermer le terminal</li>
<li><code>Alt+↑/↓</code> — Déplacer une ligne</li>
<li><code>Ctrl+D</code> — Sélectionner la prochaine occurrence</li>
<li><code>Ctrl+Shift+K</code> — Supprimer une ligne</li>
<li><code>Ctrl+/</code> — Commenter/décommenter</li>
<li><code>F12</code> — Aller à la définition</li>
<li><code>Ctrl+B</code> — Afficher/masquer la barre latérale</li>
<li><code>Ctrl+Shift+L</code> — Sélectionner toutes les occurrences</li>
</ul>''',
                'beginner', True,
            ),
            (
                'Git : Les commandes que vous devez connaître',
                'De débutant à confirmé',
                'git',
                'Un récapitulatif des commandes Git les plus utiles pour gérer vos dépôts efficacement au quotidien.',
                '''<h2>Commandes de base</h2>
<pre><code>git init                    # Initialiser un dépôt
git clone &lt;url&gt;             # Cloner un dépôt
git status                  # État du dépôt
git add .                   # Ajouter tous les fichiers
git commit -m "message"     # Commit</code></pre>

<h2>Branches</h2>
<pre><code>git branch feature          # Créer une branche
git checkout feature        # Changer de branche
git merge feature           # Fusionner
git branch -d feature       # Supprimer</code></pre>

<h2>Avancé</h2>
<pre><code>git stash                   # Mettre de côté les changements
git rebase main             # Rebaser
git cherry-pick &lt;hash&gt;      # Prendre un commit spécifique
git log --oneline --graph   # Historique graphique</code></pre>''',
                'intermediate', True,
            ),
            (
                'Python : 7 astuces pour écrire du code propre',
                'Pythonic code : les bonnes pratiques',
                'python-tips',
                'Écrivez du code Python plus élégant et plus lisible grâce à ces 7 astuces issues des meilleures pratiques de la communauté.',
                '''<h2>1. List comprehensions</h2>
<pre><code># Moins lisible
squares = []
for i in range(10):
    squares.append(i**2)

# Pythonic
squares = [i**2 for i in range(10)]</code></pre>

<h2>2. Décomposition de tuples</h2>
<pre><code>a, b, *rest = [1, 2, 3, 4, 5]
# a=1, b=2, rest=[3,4,5]</code></pre>

<h2>3. Dictionnaires</h2>
<pre><code>user = {"name": "Landry", "age": 30}
name = user.get("name", "Inconnu")  # Valeur par défaut</code></pre>

<h2>4. F-strings</h2>
<pre><code>name = "Landry"
score = 95.6789
print(f"Bonjour {name}, votre score : {score:.2f}")</code></pre>

<h2>5. Context managers</h2>
<pre><code>with open("fichier.txt", "r") as f:
    content = f.read()
# Fichier fermé automatiquement</code></pre>''',
                'beginner', True,
            ),
            (
                'Django : Optimiser les requêtes avec select_related',
                'Éviter le problème N+1',
                'django-tips',
                'Le problème N+1 est une des causes principales de lenteur dans les apps Django. Apprenez à l\'identifier et le corriger avec select_related et prefetch_related.',
                '''<h2>Le problème N+1</h2>
<pre><code># Problème : 1 requête pour les articles + N pour les auteurs
articles = Article.objects.all()
for article in articles:
    print(article.author.name)  # 1 requête par itération !</code></pre>

<h2>Solution : select_related</h2>
<pre><code># select_related pour ForeignKey et OneToOne
articles = Article.objects.select_related(\'author\', \'category\').all()
for article in articles:
    print(article.author.name)  # Pas de requête supplémentaire !</code></pre>

<h2>prefetch_related pour ManyToMany</h2>
<pre><code># prefetch_related pour ManyToMany
articles = Article.objects.prefetch_related(\'tags\').all()
for article in articles:
    print(article.tags.all())  # Pas de requête supplémentaire !</code></pre>

<h2>Debug avec django-debug-toolbar</h2>
<pre><code>pip install django-debug-toolbar
# Voir le nombre de requêtes SQL par page</code></pre>''',
                'intermediate', False,
            ),
        ]

        created_tips = 0
        for title, subtitle, cat_slug, excerpt, content, difficulty, featured in tips_data:
            slug = slugify(title)
            if not Tip.objects.filter(slug=slug).exists():
                Tip.objects.create(
                    title=title, subtitle=subtitle, slug=slug,
                    author=user, category=tip_cats.get(cat_slug),
                    excerpt=excerpt, content=content,
                    difficulty=difficulty,
                    status='published', is_featured=featured,
                    views_count=0, published_at=timezone.now(),
                )
                created_tips += 1
        self.stdout.write(self.style.SUCCESS(f'✅ {created_tips} astuces créées'))

        # ---- Portfolio ----
        from portfolio.models import PortfolioCategory, PortfolioItem
        port_cats_data = [
            ('Site Web', 'site-web'),
            ('Application Mobile', 'app-mobile'),
            ('Dashboard', 'dashboard'),
        ]
        port_cats = {}
        for name, slug in port_cats_data:
            cat, _ = PortfolioCategory.objects.get_or_create(slug=slug, defaults={'name': name})
            port_cats[slug] = cat

        portfolios_data = [
            ('Landry Net — Site Personnel', 'Portfolio personnel Django + Next.js', 'site-web', 'Site web personnel full-stack avec gestion de contenu.', True),
            ('E-commerce Django', 'Boutique en ligne complète', 'site-web', 'Application e-commerce avec panier, paiements Stripe et gestion des commandes.', True),
            ('Dashboard Analytics', 'Visualisation de données React', 'dashboard', 'Dashboard de visualisation avec graphiques interactifs et export PDF.', True),
        ]
        created_portfolio = 0
        for i, (title, subtitle, cat_slug, description, featured) in enumerate(portfolios_data):
            slug = slugify(title)
            if not PortfolioItem.objects.filter(slug=slug).exists():
                try:
                    PortfolioItem.objects.create(
                        title=title, subtitle=subtitle, slug=slug,
                        category=port_cats.get(cat_slug),
                        cover_image='',
                        description=description,
                        is_featured=featured, order=i,
                    )
                    created_portfolio += 1
                except Exception as e:
                    self.stdout.write(f'  Portfolio skipped: {e}')
        self.stdout.write(self.style.SUCCESS(f'✅ {created_portfolio} items portfolio créés'))

        # ---- Newsletter test subscribers ----
        from newsletter.models import Subscriber
        test_subs = [
            ('test1@example.com', 'Test Utilisateur 1'),
            ('test2@example.com', 'Test Utilisateur 2'),
        ]
        created_subs = 0
        for email, name in test_subs:
            _, created = Subscriber.objects.get_or_create(email=email, defaults={'name': name, 'status': 'active', 'confirmed': True})
            if created:
                created_subs += 1
        self.stdout.write(self.style.SUCCESS(f'✅ {created_subs} abonnés test créés'))

        self.stdout.write('\n' + self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('Données de test créées avec succès !'))
        self.stdout.write(self.style.SUCCESS('Admin : http://localhost:8000/admin/'))
        self.stdout.write(self.style.SUCCESS('Site  : http://localhost:5000/'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
