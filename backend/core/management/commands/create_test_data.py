from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Crée des données de test complètes pour Landry Net'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('🚀 Création des données de test...'))

        # ── Admin users ──────────────────────────────────────────────────────
        admin, created = User.objects.get_or_create(username='admin', defaults={
            'first_name': 'Landry', 'last_name': 'K.',
            'email': 'admin@landrynet.com',
            'is_staff': True, 'is_superuser': True,
        })
        admin.set_password('admin123')
        admin.first_name = admin.first_name or 'Landry'
        admin.last_name = admin.last_name or 'K.'
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()
        self.stdout.write(self.style.SUCCESS(f'✅ Admin : admin / admin123'))

        # ── SiteSettings ─────────────────────────────────────────────────────
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
        settings.newsletter_intro_text = 'Voici une nouvelle publication qui devrait vous intéresser !'
        settings.newsletter_from_name = 'Landry Net'
        settings.save()
        self.stdout.write(self.style.SUCCESS('✅ SiteSettings configurés'))

        # ── Skills ───────────────────────────────────────────────────────────
        skills_data = [
            ('Python', 90, 'bi-filetype-py', 'Backend'),
            ('Django', 88, 'bi-gear-fill', 'Backend'),
            ('JavaScript', 85, 'bi-lightning-fill', 'Frontend'),
            ('React / Next.js', 82, 'bi-layers-fill', 'Frontend'),
            ('TypeScript', 75, 'bi-file-code-fill', 'Frontend'),
            ('Node.js', 70, 'bi-server', 'Backend'),
            ('PostgreSQL', 78, 'bi-database-fill', 'Base de données'),
            ('Docker', 65, 'bi-box-seam-fill', 'DevOps'),
            ('Git / GitHub', 90, 'bi-git', 'DevOps'),
            ('Tailwind CSS', 88, 'bi-palette-fill', 'Frontend'),
            ('REST API', 85, 'bi-plug-fill', 'Backend'),
            ('Linux', 72, 'bi-terminal-fill', 'DevOps'),
        ]
        for i, (name, level, icon, category) in enumerate(skills_data):
            Skill.objects.get_or_create(name=name, defaults={'level': level, 'icon': icon, 'category': category, 'order': i})
        self.stdout.write(self.style.SUCCESS(f'✅ {len(skills_data)} compétences'))

        # ── Experiences ──────────────────────────────────────────────────────
        experiences_data = [
            ('Développeur Full-Stack', 'Freelance', 'Paris, France', date(2022, 1, 1), None, True,
             'Développement d\'applications web sur mesure pour des clients en France et à l\'international. Stack principale : Django, React, PostgreSQL, Docker.'),
            ('Développeur Backend Python', 'Tech Startup', 'Lyon, France', date(2020, 3, 1), date(2021, 12, 31), False,
             'Développement et maintenance d\'APIs REST avec Django et DRF. Mise en place de pipelines CI/CD avec GitHub Actions.'),
            ('Développeur Web Junior', 'Agence Digitale', 'Paris, France', date(2018, 6, 1), date(2020, 2, 28), False,
             'Développement de sites web et applications web. HTML, CSS, JavaScript, PHP, WordPress.'),
        ]
        for i, (title, company, location, start, end, current, desc) in enumerate(experiences_data):
            Experience.objects.get_or_create(
                title=title, company=company,
                defaults={'location': location, 'start_date': start, 'end_date': end, 'is_current': current, 'description': desc, 'order': i}
            )
        self.stdout.write(self.style.SUCCESS(f'✅ {len(experiences_data)} expériences'))

        # ── Education ────────────────────────────────────────────────────────
        educations_data = [
            ('Master Informatique', 'Université Paris Saclay', 'Paris, France', date(2016, 9, 1), date(2018, 6, 30), False,
             'Spécialisation en Génie Logiciel et Systèmes Distribués.'),
            ('Licence Informatique', 'Université Paris 6', 'Paris, France', date(2013, 9, 1), date(2016, 6, 30), False,
             'Fondamentaux de l\'informatique, algorithmique, bases de données.'),
        ]
        for i, (degree, institution, location, start, end, current, desc) in enumerate(educations_data):
            Education.objects.get_or_create(
                degree=degree, institution=institution,
                defaults={'location': location, 'start_date': start, 'end_date': end, 'is_current': current, 'description': desc, 'order': i}
            )
        self.stdout.write(self.style.SUCCESS(f'✅ {len(educations_data)} formations'))

        # ── Article Categories ────────────────────────────────────────────────
        from articles.models import Category, Article
        categories_data = [
            ('Python', 'python', 'bi-filetype-py', '#3B82F6'),
            ('Django', 'django', 'bi-gear-fill', '#4F46E5'),
            ('JavaScript', 'javascript', 'bi-lightning-fill', '#F59E0B'),
            ('React', 'react', 'bi-layers-fill', '#06B6D4'),
            ('DevOps', 'devops', 'bi-box-seam-fill', '#10B981'),
            ('Tutoriels', 'tutoriels', 'bi-book-fill', '#8B5CF6'),
        ]
        cats = {}
        for name, slug, icon, color in categories_data:
            cat, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name, 'icon': icon, 'color': color})
            cats[slug] = cat
        self.stdout.write(self.style.SUCCESS(f'✅ {len(categories_data)} catégories articles'))

        # ── Articles ─────────────────────────────────────────────────────────
        articles_data = [
            (
                'Créer une API REST avec Django REST Framework',
                'Guide complet pour débutants',
                'django',
                'Dans ce tutoriel, nous allons créer une API REST complète avec Django REST Framework. Vous apprendrez à créer des endpoints, gérer l\'authentification JWT, la pagination et bien plus encore.',
                '''<h2>Introduction</h2>
<p>Django REST Framework (DRF) est l\'une des bibliothèques les plus populaires pour créer des API REST en Python.</p>
<h2>Installation</h2>
<pre><code>pip install djangorestframework
pip install djangorestframework-simplejwt</code></pre>
<h2>Configuration</h2>
<pre><code>INSTALLED_APPS = [
    \'rest_framework\',
    \'rest_framework_simplejwt\',
]</code></pre>
<h2>Votre premier serializer</h2>
<pre><code>from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = \'__all__\'</code></pre>
<h2>Conclusion</h2>
<p>Vous avez maintenant une API REST fonctionnelle avec Django !</p>''',
                True, 8, 245
            ),
            (
                'Next.js 14 : Les nouveautés à connaître',
                'App Router, Server Components, et plus encore',
                'react',
                'Next.js 14 apporte de nombreuses améliorations majeures. Découvrez les nouvelles fonctionnalités qui vont changer votre façon de développer des applications React.',
                '''<h2>Next.js 14 — Ce qui change</h2>
<p>Next.js 14 est une mise à jour majeure avec des améliorations significatives en termes de performance.</p>
<h2>App Router stable</h2>
<ul><li>Server Components par défaut</li><li>Meilleure gestion du cache</li><li>Layouts imbriqués</li></ul>
<h2>Server Actions</h2>
<pre><code>async function createPost(formData) {
  \'use server\'
  const title = formData.get(\'title\')
  await db.insert({ title })
}</code></pre>''',
                True, 6, 189
            ),
            (
                'Docker pour développeurs Python : Guide pratique',
                'Containerisez vos applications Django',
                'devops',
                'Apprenez à containeriser vos applications Django avec Docker. De la création du Dockerfile à l\'orchestration avec Docker Compose.',
                '''<h2>Pourquoi Docker ?</h2>
<p>Docker permet d\'isoler votre application et ses dépendances dans un conteneur portable.</p>
<h2>Dockerfile pour Django</h2>
<pre><code>FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]</code></pre>''',
                False, 10, 134
            ),
            (
                'Python 3.12 : Les nouvelles fonctionnalités',
                'Pattern matching, f-strings améliorés et plus',
                'python',
                'Python 3.12 est sorti avec son lot de nouvelles fonctionnalités passionnantes. Découvrez ce qui change.',
                '''<h2>Nouveautés de Python 3.12</h2>
<p>Python 3.12 apporte plusieurs améliorations importantes pour les développeurs.</p>
<h2>F-strings améliorées</h2>
<pre><code>result = f"{{\'Bonjour\':>20}}"</code></pre>
<h2>Performances</h2>
<p>Python 3.12 est jusqu\'à 5% plus rapide que Python 3.11.</p>''',
                True, 5, 98
            ),
            (
                'Authentification JWT avec Django et React',
                'Sécurisez vos APIs en 30 minutes',
                'django',
                'L\'authentification JWT est un standard pour sécuriser les APIs REST. Dans ce tutoriel, nous implémentons un système d\'auth complet.',
                '''<h2>Introduction au JWT</h2>
<p>JSON Web Tokens (JWT) est un standard ouvert pour créer des tokens d\'accès sécurisés.</p>
<h2>Installation</h2>
<pre><code>pip install djangorestframework-simplejwt</code></pre>
<h2>Côté React</h2>
<pre><code>const login = async (username, password) => {
  const response = await fetch(\'/api/token/\', {
    method: \'POST\',
    body: JSON.stringify({ username, password }),
  })
  const data = await response.json()
  localStorage.setItem(\'access_token\', data.access)
}</code></pre>''',
                False, 7, 167
            ),
        ]

        created_articles_list = []
        ca = 0
        for title, subtitle, cat_slug, excerpt, content, featured, read_time, views in articles_data:
            slug = slugify(title)
            if not Article.objects.filter(slug=slug).exists():
                art = Article.objects.create(
                    title=title, subtitle=subtitle, slug=slug,
                    author=admin, category=cats.get(cat_slug),
                    excerpt=excerpt, content=content,
                    status='published', is_featured=featured,
                    read_time=read_time, views_count=views,
                    published_at=timezone.now() - timedelta(days=random.randint(1, 60)),
                )
                created_articles_list.append(art)
                ca += 1
            else:
                art = Article.objects.get(slug=slug)
                created_articles_list.append(art)
        self.stdout.write(self.style.SUCCESS(f'✅ {ca} articles créés (+ {len(articles_data) - ca} existants)'))

        # ── Project Categories ────────────────────────────────────────────────
        from projects.models import ProjectCategory, Project
        proj_cats_data = [
            ('Web App', 'web-app', 'bi-globe', '#4F46E5'),
            ('API / Backend', 'api-backend', 'bi-cpu-fill', '#10B981'),
            ('Mobile', 'mobile', 'bi-phone-fill', '#F59E0B'),
            ('Open Source', 'open-source', 'bi-github', '#EF4444'),
        ]
        proj_cats = {}
        for name, slug, icon, color in proj_cats_data:
            cat, _ = ProjectCategory.objects.get_or_create(slug=slug, defaults={'name': name, 'icon': icon, 'color': color})
            proj_cats[slug] = cat

        projects_data = [
            (
                'Landry Net — Site Web Personnel',
                'Django + Templates HTML avec admin complet',
                'web-app',
                'Site personnel full-stack avec Django backend, templates HTML/CSS/JS, gestion de contenu via admin, newsletter, commentaires et réactions.',
                '''<h2>Présentation</h2>
<p>Landry Net est mon site personnel construit avec Django 5.2 + Templates.</p>
<h2>Stack technique</h2>
<ul><li><strong>Backend</strong> : Django 5.2 + DRF</li><li><strong>Frontend</strong> : Templates HTML/CSS/JS</li><li><strong>DB</strong> : SQLite (dev) / PostgreSQL (prod)</li></ul>
<h2>Fonctionnalités</h2>
<ul><li>Articles, projets, astuces, portfolio</li><li>Newsletter automatique</li><li>Commentaires et réactions</li><li>Mode sombre/clair</li></ul>''',
                'Django, DRF, Python, SQLite, WhiteNoise',
                'https://github.com/Landry-kayoyo/repli-site',
                True, 312
            ),
            (
                'API de gestion de tâches avec Django',
                'Todo API REST avec authentification JWT',
                'api-backend',
                'Une API REST complète pour gérer des tâches avec authentification JWT, filtres avancés, pagination et documentation Swagger.',
                '''<h2>Architecture</h2>
<p>Cette API suit les principes REST avec documentation Swagger automatique.</p>
<pre><code>GET    /api/tasks/
POST   /api/tasks/
PUT    /api/tasks/{{id}}/
DELETE /api/tasks/{{id}}/</code></pre>''',
                'Django, DRF, JWT, PostgreSQL, Swagger',
                'https://github.com/Landry-kayoyo',
                True, 87
            ),
            (
                'Dashboard Analytics avec React et Chart.js',
                'Visualisation de données en temps réel',
                'web-app',
                'Un dashboard de visualisation de données construit avec React, utilisant Chart.js pour les graphiques et un backend Express.js.',
                '''<h2>Technologies</h2>
<ul><li>React 18 avec hooks</li><li>Chart.js 4 pour les graphiques</li><li>TailwindCSS</li><li>Express.js backend</li></ul>''',
                'React, Chart.js, Tailwind CSS, Node.js, Express',
                'https://github.com/Landry-kayoyo',
                False, 54
            ),
        ]

        cp = 0
        for title, subtitle, cat_slug, description, content, technologies, github_url, featured, views in projects_data:
            slug = slugify(title)
            if not Project.objects.filter(slug=slug).exists():
                Project.objects.create(
                    title=title, subtitle=subtitle, slug=slug,
                    author=admin, category=proj_cats.get(cat_slug),
                    description=description, content=content,
                    technologies=technologies, github_url=github_url,
                    status='published', is_featured=featured,
                    views_count=views, published_at=timezone.now() - timedelta(days=random.randint(1, 90)),
                )
                cp += 1
        self.stdout.write(self.style.SUCCESS(f'✅ {cp} projets créés'))

        # ── Tips ─────────────────────────────────────────────────────────────
        from tips.models import TipCategory, Tip
        tip_cats_data = [
            ('Python', 'python-tips', 'bi-filetype-py', '#3B82F6'),
            ('Git', 'git', 'bi-git', '#EF4444'),
            ('Terminal', 'terminal', 'bi-terminal-fill', '#6B7280'),
            ('VS Code', 'vscode', 'bi-code-square', '#06B6D4'),
            ('Django', 'django-tips', 'bi-gear-fill', '#4F46E5'),
        ]
        tip_cats = {}
        for name, slug, icon, color in tip_cats_data:
            cat, _ = TipCategory.objects.get_or_create(slug=slug, defaults={'name': name, 'icon': icon, 'color': color})
            tip_cats[slug] = cat

        tips_data = [
            ('10 raccourcis VS Code indispensables', 'Boostez votre productivité', 'vscode',
             'Maîtrisez ces raccourcis VS Code et doublez votre productivité en quelques jours.',
             '''<h2>Les raccourcis essentiels</h2>
<ul>
<li><code>Ctrl+P</code> — Ouvrir un fichier rapidement</li>
<li><code>Ctrl+Shift+P</code> — Palette de commandes</li>
<li><code>Ctrl+`</code> — Terminal intégré</li>
<li><code>Alt+↑/↓</code> — Déplacer une ligne</li>
<li><code>Ctrl+D</code> — Sélectionner l\'occurrence suivante</li>
<li><code>Ctrl+/</code> — Commenter/décommenter</li>
<li><code>F12</code> — Aller à la définition</li>
<li><code>Ctrl+Shift+L</code> — Toutes les occurrences</li>
</ul>''', 'beginner', True, 156),
            ('Git : Les commandes que vous devez connaître', 'De débutant à confirmé', 'git',
             'Un récapitulatif des commandes Git les plus utiles pour gérer vos dépôts au quotidien.',
             '''<h2>Commandes de base</h2>
<pre><code>git init && git clone &lt;url&gt; && git status
git add . && git commit -m "message" && git push</code></pre>
<h2>Branches</h2>
<pre><code>git branch feature && git checkout feature
git merge feature && git branch -d feature</code></pre>''', 'intermediate', True, 203),
            ('Python : 7 astuces pour écrire du code propre', 'Pythonic code', 'python-tips',
             'Écrivez du code Python plus élégant avec ces 7 astuces des meilleures pratiques.',
             '''<h2>1. List comprehensions</h2>
<pre><code>squares = [i**2 for i in range(10)]</code></pre>
<h2>2. F-strings</h2>
<pre><code>print(f"Score : {score:.2f}")</code></pre>
<h2>3. Context managers</h2>
<pre><code>with open("fichier.txt", "r") as f:
    content = f.read()</code></pre>''', 'beginner', True, 98),
            ('Django : Optimiser les requêtes avec select_related', 'Éviter le N+1', 'django-tips',
             'Identifiez et corrigez le problème N+1 dans Django avec select_related et prefetch_related.',
             '''<h2>Le problème N+1</h2>
<pre><code># Mauvais : 1 + N requêtes
for article in Article.objects.all():
    print(article.author.name)</code></pre>
<h2>La solution</h2>
<pre><code># Bon : 1 seule requête JOIN
articles = Article.objects.select_related(\'author\', \'category\').all()</code></pre>''', 'intermediate', False, 67),
        ]

        ct = 0
        for title, subtitle, cat_slug, excerpt, content, difficulty, featured, views in tips_data:
            slug = slugify(title)
            if not Tip.objects.filter(slug=slug).exists():
                Tip.objects.create(
                    title=title, subtitle=subtitle, slug=slug,
                    author=admin, category=tip_cats.get(cat_slug),
                    excerpt=excerpt, content=content,
                    difficulty=difficulty, status='published', is_featured=featured,
                    views_count=views, published_at=timezone.now() - timedelta(days=random.randint(1, 45)),
                )
                ct += 1
        self.stdout.write(self.style.SUCCESS(f'✅ {ct} astuces créées'))

        # ── Newsletter subscribers ────────────────────────────────────────────
        from newsletter.models import Subscriber
        subscribers_data = [
            ('alice.martin@example.com', 'Alice Martin'),
            ('bob.dupont@example.com', 'Bob Dupont'),
            ('claire.leroy@example.com', 'Claire Leroy'),
            ('david.moreau@example.com', 'David Moreau'),
            ('emma.bernard@example.com', 'Emma Bernard'),
            ('test@example.com', 'Testeur Newsletter'),
        ]
        cs = 0
        for email, name in subscribers_data:
            _, created_s = Subscriber.objects.get_or_create(
                email=email,
                defaults={'name': name, 'status': 'active', 'confirmed': True}
            )
            if created_s:
                cs += 1
        self.stdout.write(self.style.SUCCESS(f'✅ {cs} abonnés newsletter ajoutés ({len(subscribers_data)} total)'))

        # ── PageView test data ────────────────────────────────────────────────
        from core.models import PageView
        from django.db.models import F

        today = timezone.now().date()
        articles_qs = Article.objects.filter(status='published')[:5]
        projects_qs = Project.objects.filter(status='published')[:3]
        tips_qs = Tip.objects.filter(status='published')[:3]

        from django.db import transaction as db_transaction, connection as db_connection

        def upsert_pageview(content_type, obj_pk, obj_title, obj_slug, day, count):
            try:
                with db_transaction.atomic():
                    try:
                        pv = PageView.objects.get(content_type=content_type, object_id=obj_pk, date=day)
                        pv.count = count
                        pv.object_title = obj_title
                        pv.object_slug = obj_slug
                        pv.save(update_fields=['count', 'object_title', 'object_slug'])
                    except PageView.DoesNotExist:
                        PageView.objects.create(
                            content_type=content_type, object_id=obj_pk, date=day,
                            object_title=obj_title, object_slug=obj_slug, count=count
                        )
            except Exception:
                pass

        pv_count = 0
        for i in range(30):
            day = today - timedelta(days=i)
            base_views = max(1, 25 - i + random.randint(-5, 10))

            for art in articles_qs:
                v = max(1, base_views + random.randint(-8, 8))
                upsert_pageview('article', art.pk, art.title, art.slug, day, v)
                pv_count += 1

            for proj in projects_qs:
                v = max(1, base_views // 2 + random.randint(-3, 5))
                upsert_pageview('project', proj.pk, proj.title, proj.slug, day, v)
                pv_count += 1

            for tip in tips_qs:
                v = max(1, base_views // 3 + random.randint(-2, 4))
                upsert_pageview('tip', tip.pk, tip.title, tip.slug, day, v)
                pv_count += 1

        self.stdout.write(self.style.SUCCESS(f'✅ {pv_count} entrées de vues de pages (30 jours)'))

        # ── Contact messages ──────────────────────────────────────────────────
        from contact.models import ContactMessage
        contacts_data = [
            ('Marie Curie', 'marie@example.com', 'Collaboration sur un projet', 'Bonjour Landry, je suis développeuse et j\'aimerais collaborer avec vous sur un projet open-source. Pouvez-vous me contacter ?', 'new'),
            ('Jean Dubois', 'jean@example.com', 'Question sur votre article Django', 'Super article sur Django REST Framework ! J\'ai une question : comment gérer les permissions personnalisées ? Merci !', 'read'),
            ('Sophia Chen', 'sophia@example.com', 'Offre de mission freelance', 'Bonjour, je suis chef de projet dans une startup et nous cherchons un développeur Django pour une mission de 3 mois. Intéressé ?', 'new'),
        ]
        cc = 0
        for name, email, subject, message, status in contacts_data:
            if not ContactMessage.objects.filter(email=email, subject=subject).exists():
                ContactMessage.objects.create(
                    name=name, email=email, subject=subject,
                    message=message, status=status,
                    ip_address='127.0.0.1'
                )
                cc += 1
        self.stdout.write(self.style.SUCCESS(f'✅ {cc} messages de contact'))

        # ── Comments ─────────────────────────────────────────────────────────
        from comments.models import Comment
        from django.contrib.contenttypes.models import ContentType

        all_articles = list(Article.objects.filter(status='published')[:3])
        comments_data = [
            ('Thomas Martin', 'thomas@example.com', 'Excellent article, très bien expliqué !', True),
            ('Julien Petit', 'julien@example.com', 'Merci pour ce tutoriel, j\'ai enfin compris le concept.', True),
            ('Sophie Bernard', 'sophie@example.com', 'Peut-on avoir un exemple avec PostgreSQL ?', False),
        ]
        cco = 0
        if all_articles:
            art_ct = ContentType.objects.get_for_model(Article)
            art = all_articles[0]
            for author_name, author_email, content_text, approved in comments_data:
                if not Comment.objects.filter(author_email=author_email, content_type=art_ct, object_id=art.pk).exists():
                    Comment.objects.create(
                        content_type=art_ct, object_id=art.pk,
                        author_name=author_name, author_email=author_email,
                        content=content_text, is_approved=approved,
                    )
                    cco += 1
        self.stdout.write(self.style.SUCCESS(f'✅ {cco} commentaires'))

        # ── Summary ──────────────────────────────────────────────────────────
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('━' * 50))
        self.stdout.write(self.style.SUCCESS('🎉 Données de test créées avec succès !'))
        self.stdout.write(self.style.SUCCESS('━' * 50))
        self.stdout.write(self.style.WARNING('🔑 Identifiants admin :'))
        self.stdout.write(self.style.WARNING('   Username : admin'))
        self.stdout.write(self.style.WARNING('   Password : admin123'))
        self.stdout.write(self.style.WARNING(f'   URL admin : http://localhost:5000/admin/'))
        self.stdout.write(self.style.SUCCESS('━' * 50))
