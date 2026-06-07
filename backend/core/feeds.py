from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed, Rss201rev2Feed
from django.conf import settings
from articles.models import Article
from projects.models import Project
from tips.models import Tip

SITE_URL = getattr(settings, 'SITE_URL', 'https://landryit.pythonanywhere.com')


def _abs(path):
    return f"{SITE_URL.rstrip('/')}{path}"


def _image_html(item):
    if item.cover_image:
        url = _abs(item.cover_image.url)
        return f'<p><img src="{url}" alt="{item.title}" style="max-width:100%;border-radius:8px;"></p>'
    return ''


def _tags_str(item):
    try:
        tags = item.tags.all()
        return ', '.join(t.name for t in tags) if tags else ''
    except Exception:
        return ''


def _category_str(item):
    try:
        return item.category.name if item.category else ''
    except Exception:
        return ''


def _author_str(item):
    try:
        u = item.author
        return u.get_full_name() or u.username
    except Exception:
        return 'Landry'


def _build_description(item, body_field='excerpt'):
    body = getattr(item, body_field, '') or ''
    img = _image_html(item)
    cat = _category_str(item)
    tags = _tags_str(item)
    author = _author_str(item)
    meta = []
    if cat:
        meta.append(f'<strong>Catégorie :</strong> {cat}')
    if tags:
        meta.append(f'<strong>Tags :</strong> {tags}')
    meta.append(f'<strong>Auteur :</strong> {author}')
    meta_html = ' &nbsp;|&nbsp; '.join(meta)
    return f'{img}<p style="color:#6b7280;font-size:0.875rem;">{meta_html}</p><p>{body}</p>'


class ArticlesFeed(Feed):
    title = "Landry Net — Articles"
    description = "Derniers articles publiés sur Landry Net"

    @property
    def link(self):
        return _abs('/articles/')

    def feed_url(self):
        return _abs('/rss/articles/')

    def items(self):
        return Article.objects.filter(status='published').order_by('-published_at').select_related('author', 'category')[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return _build_description(item, 'excerpt')

    def item_link(self, item):
        return _abs(f'/articles/{item.slug}/')

    def item_pubdate(self, item):
        return item.published_at

    def item_author_name(self, item):
        return _author_str(item)

    def item_categories(self, item):
        cats = []
        if _category_str(item):
            cats.append(_category_str(item))
        try:
            cats += [t.name for t in item.tags.all()]
        except Exception:
            pass
        return cats

    def item_enclosure_url(self, item):
        if item.cover_image:
            return _abs(item.cover_image.url)
        return None

    def item_enclosure_length(self, item):
        return 0

    def item_enclosure_mime_type(self, item):
        return 'image/jpeg'


class ArticlesAtomFeed(ArticlesFeed):
    feed_type = Atom1Feed
    subtitle = ArticlesFeed.description

    def feed_url(self):
        return _abs('/rss/articles/atom/')


class ProjectsFeed(Feed):
    title = "Landry Net — Projets"
    description = "Derniers projets publiés sur Landry Net"

    @property
    def link(self):
        return _abs('/projets/')

    def feed_url(self):
        return _abs('/rss/projets/')

    def items(self):
        return Project.objects.filter(status='published').order_by('-published_at').select_related('author', 'category')[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        desc = item.description or ''
        tech = getattr(item, 'technologies', '') or ''
        img = _image_html(item)
        cat = _category_str(item)
        tags = _tags_str(item)
        author = _author_str(item)
        meta = []
        if cat:
            meta.append(f'<strong>Catégorie :</strong> {cat}')
        if tech:
            meta.append(f'<strong>Technologies :</strong> {tech}')
        if tags:
            meta.append(f'<strong>Tags :</strong> {tags}')
        meta.append(f'<strong>Auteur :</strong> {author}')
        meta_html = ' &nbsp;|&nbsp; '.join(meta)
        links_html = ''
        if getattr(item, 'github_url', ''):
            links_html += f' <a href="{item.github_url}">GitHub</a>'
        if getattr(item, 'demo_url', ''):
            links_html += f' <a href="{item.demo_url}">Démo</a>'
        if links_html:
            links_html = f'<p>{links_html.strip()}</p>'
        return f'{img}<p style="color:#6b7280;font-size:0.875rem;">{meta_html}</p><p>{desc}</p>{links_html}'

    def item_link(self, item):
        return _abs(f'/projets/{item.slug}/')

    def item_pubdate(self, item):
        return item.published_at

    def item_author_name(self, item):
        return _author_str(item)

    def item_categories(self, item):
        cats = []
        if _category_str(item):
            cats.append(_category_str(item))
        try:
            cats += [t.name for t in item.tags.all()]
        except Exception:
            pass
        return cats

    def item_enclosure_url(self, item):
        if item.cover_image:
            return _abs(item.cover_image.url)
        return None

    def item_enclosure_length(self, item):
        return 0

    def item_enclosure_mime_type(self, item):
        return 'image/jpeg'


class ProjectsAtomFeed(ProjectsFeed):
    feed_type = Atom1Feed
    subtitle = ProjectsFeed.description

    def feed_url(self):
        return _abs('/rss/projets/atom/')


class TipsFeed(Feed):
    title = "Landry Net — Astuces"
    description = "Dernières astuces publiées sur Landry Net"

    DIFFICULTY_LABELS = {
        'beginner': 'Débutant',
        'intermediate': 'Intermédiaire',
        'advanced': 'Avancé',
    }

    @property
    def link(self):
        return _abs('/astuces/')

    def feed_url(self):
        return _abs('/rss/astuces/')

    def items(self):
        return Tip.objects.filter(status='published').order_by('-published_at').select_related('author', 'category')[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        body = item.excerpt or ''
        img = _image_html(item)
        cat = _category_str(item)
        tags = _tags_str(item)
        author = _author_str(item)
        difficulty = self.DIFFICULTY_LABELS.get(getattr(item, 'difficulty', ''), '')
        meta = []
        if cat:
            meta.append(f'<strong>Catégorie :</strong> {cat}')
        if difficulty:
            meta.append(f'<strong>Niveau :</strong> {difficulty}')
        if tags:
            meta.append(f'<strong>Tags :</strong> {tags}')
        meta.append(f'<strong>Auteur :</strong> {author}')
        meta_html = ' &nbsp;|&nbsp; '.join(meta)
        return f'{img}<p style="color:#6b7280;font-size:0.875rem;">{meta_html}</p><p>{body}</p>'

    def item_link(self, item):
        return _abs(f'/astuces/{item.slug}/')

    def item_pubdate(self, item):
        return item.published_at

    def item_author_name(self, item):
        return _author_str(item)

    def item_categories(self, item):
        cats = []
        if _category_str(item):
            cats.append(_category_str(item))
        diff = getattr(item, 'difficulty', '')
        if diff:
            cats.append(self.DIFFICULTY_LABELS.get(diff, diff))
        try:
            cats += [t.name for t in item.tags.all()]
        except Exception:
            pass
        return cats

    def item_enclosure_url(self, item):
        if item.cover_image:
            return _abs(item.cover_image.url)
        return None

    def item_enclosure_length(self, item):
        return 0

    def item_enclosure_mime_type(self, item):
        return 'image/jpeg'


class TipsAtomFeed(TipsFeed):
    feed_type = Atom1Feed
    subtitle = TipsFeed.description

    def feed_url(self):
        return _abs('/rss/astuces/atom/')


class GlobalFeed(Feed):
    title = "Landry Net — Tout le contenu"
    description = "Articles, projets et astuces de Landry Net"

    @property
    def link(self):
        return _abs('/')

    def feed_url(self):
        return _abs('/rss/')

    def items(self):
        articles = list(
            Article.objects.filter(status='published')
            .select_related('author', 'category')
            .only('title', 'slug', 'excerpt', 'cover_image', 'published_at', 'author', 'category')[:30]
        )
        projects = list(
            Project.objects.filter(status='published')
            .select_related('author', 'category')
            .only('title', 'slug', 'description', 'cover_image', 'published_at', 'author', 'category')[:30]
        )
        tips = list(
            Tip.objects.filter(status='published')
            .select_related('author', 'category')
            .only('title', 'slug', 'excerpt', 'cover_image', 'published_at', 'author', 'category')[:30]
        )

        for a in articles:
            a._type = 'article'
        for p in projects:
            p._type = 'projet'
        for t in tips:
            t._type = 'astuce'

        combined = articles + projects + tips
        combined.sort(key=lambda x: x.published_at or __import__('django.utils.timezone', fromlist=['timezone']).timezone.now(), reverse=True)
        return combined[:30]

    def item_title(self, item):
        type_label = {'article': '📝', 'projet': '🚀', 'astuce': '💡'}.get(item._type, '')
        return f"{type_label} {item.title}"

    def item_description(self, item):
        if item._type == 'article':
            return _build_description(item, 'excerpt')
        elif item._type == 'projet':
            desc = item.description or ''
            img = _image_html(item)
            cat = _category_str(item)
            tech = getattr(item, 'technologies', '') or ''
            author = _author_str(item)
            meta = []
            if cat:
                meta.append(f'<strong>Catégorie :</strong> {cat}')
            if tech:
                meta.append(f'<strong>Technologies :</strong> {tech}')
            meta.append(f'<strong>Auteur :</strong> {author}')
            meta_html = ' &nbsp;|&nbsp; '.join(meta)
            return f'{img}<p style="color:#6b7280;font-size:0.875rem;">{meta_html}</p><p>{desc}</p>'
        else:
            return _build_description(item, 'excerpt')

    def item_link(self, item):
        routes = {'article': 'articles', 'projet': 'projets', 'astuce': 'astuces'}
        return _abs(f'/{routes[item._type]}/{item.slug}/')

    def item_pubdate(self, item):
        return item.published_at

    def item_author_name(self, item):
        return _author_str(item)

    def item_categories(self, item):
        type_labels = {'article': 'Article', 'projet': 'Projet', 'astuce': 'Astuce'}
        cats = [type_labels.get(item._type, '')]
        if _category_str(item):
            cats.append(_category_str(item))
        try:
            cats += [t.name for t in item.tags.all()]
        except Exception:
            pass
        return [c for c in cats if c]

    def item_enclosure_url(self, item):
        if item.cover_image:
            return _abs(item.cover_image.url)
        return None

    def item_enclosure_length(self, item):
        return 0

    def item_enclosure_mime_type(self, item):
        return 'image/jpeg'


class GlobalAtomFeed(GlobalFeed):
    feed_type = Atom1Feed
    subtitle = GlobalFeed.description

    def feed_url(self):
        return _abs('/rss/atom/')
