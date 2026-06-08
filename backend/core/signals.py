"""
Signals: IndexNow + Bing Sitemap ping, Facebook auto-post, optimisation images.
Note: Google a déprécié son /ping endpoint en janvier 2023.
On utilise maintenant IndexNow (supporté par Bing, Yandex, Seznam…).
"""
import threading
import urllib.request
import urllib.error
import urllib.parse
import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)

# Mémorise le statut AVANT sauvegarde pour détecter le 1er passage à 'published'
_pre_save_status = {}


# ──────────────────────────────────────────────
# IndexNow + Bing Sitemap Ping
# ──────────────────────────────────────────────

def _submit_via_indexnow(page_url, site_url):
    """Soumet l'URL publiée via IndexNow à Bing (et partenaires)."""
    try:
        from core.indexnow import submit_url_indexnow
        result = submit_url_indexnow(page_url, site_url)
        if result['success']:
            logger.info(f"IndexNow OK: {page_url} → HTTP {result.get('status')}")
        else:
            logger.warning(f"IndexNow failed (non-critical): {result.get('message')}")
    except Exception as e:
        logger.warning(f"IndexNow error (non-critical): {e}")


def _ping_bing_sitemap(sitemap_url):
    """Ping Bing avec l'URL du sitemap (encore supporté par Bing)."""
    try:
        req = urllib.request.Request(
            f'https://www.bing.com/ping?sitemap={sitemap_url}',
            headers={'User-Agent': 'LandryNet-SitemapPing/1.0'}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            logger.info(f"Bing sitemap ping: HTTP {resp.status}")
    except urllib.error.HTTPError as e:
        logger.warning(f"Bing sitemap ping failed (non-critical): HTTP {e.code}")
    except Exception as e:
        logger.warning(f"Bing sitemap ping failed (non-critical): {e}")


def _schedule_ping(instance=None, content_type=None):
    """Lance IndexNow + Bing sitemap ping en arrière-plan."""
    try:
        from django.conf import settings
        site_url = getattr(settings, 'SITE_URL', '').rstrip('/')
        if not site_url:
            return

        sitemap_url = f"{site_url}/sitemap.xml"

        # Construire l'URL de la page publiée pour IndexNow
        page_url = None
        if instance and content_type:
            slug = getattr(instance, 'slug', None)
            if slug:
                path_map = {
                    'article': f'/articles/{slug}/',
                    'project': f'/projets/{slug}/',
                    'tip': f'/astuces/{slug}/',
                }
                path = path_map.get(content_type)
                if path:
                    page_url = f"{site_url}{path}"

        def _run():
            # 1. IndexNow pour l'URL spécifique (si disponible)
            if page_url:
                _submit_via_indexnow(page_url, site_url)
            # 2. Bing sitemap ping (encore actif)
            _ping_bing_sitemap(sitemap_url)

        threading.Thread(target=_run, daemon=True).start()
    except Exception as e:
        logger.debug(f"Ping schedule failed: {e}")


# ──────────────────────────────────────────────
# Facebook auto-post
# ──────────────────────────────────────────────

def _get_fb_settings():
    """Retourne (page_id, page_token) ou (None, None) si non configuré."""
    try:
        from core.models import SiteSettings
        s = SiteSettings.objects.first()
        if s and s.facebook_auto_post and s.facebook_page_id and s.facebook_page_token:
            return s.facebook_page_id, s.facebook_page_token
    except Exception:
        pass
    return None, None


def _post_to_facebook(message, link):
    """Appelle l'API Graph Facebook pour publier sur la Page."""
    page_id, token = _get_fb_settings()
    if not page_id:
        return

    try:
        from django.conf import settings
        site_url = getattr(settings, 'SITE_URL', '').rstrip('/')
        full_link = f"{site_url}{link}" if link.startswith('/') else link

        data = urllib.parse.urlencode({
            'message': message,
            'link': full_link,
            'access_token': token,
        }).encode('utf-8')

        req = urllib.request.Request(
            f'https://graph.facebook.com/v19.0/{page_id}/feed',
            data=data,
            method='POST',
            headers={'User-Agent': 'LandryNet-FacebookBot/1.0'},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = resp.read().decode('utf-8')
            logger.info(f"Facebook post OK: {result}")
    except Exception as e:
        logger.warning(f"Facebook post failed (non-critical): {e}")


def _schedule_facebook_post(instance, content_type):
    """Prépare le message et lance le post Facebook en arrière-plan."""
    try:
        from django.conf import settings
        site_url = getattr(settings, 'SITE_URL', '').rstrip('/')

        if content_type == 'article':
            excerpt = getattr(instance, 'excerpt', '') or ''
            link = f"/articles/{instance.slug}/"
            message = (
                f"📝 Nouvel article : {instance.title}\n\n"
                f"{excerpt[:200]}{'…' if len(excerpt) > 200 else ''}\n\n"
                f"🔗 Lire la suite : {site_url}{link}"
            )
        elif content_type == 'projet':
            desc = getattr(instance, 'description', '') or ''
            link = f"/projets/{instance.slug}/"
            message = (
                f"🚀 Nouveau projet : {instance.title}\n\n"
                f"{desc[:200]}{'…' if len(desc) > 200 else ''}\n\n"
                f"🔗 Voir le projet : {site_url}{link}"
            )
        elif content_type == 'astuce':
            excerpt = getattr(instance, 'excerpt', '') or ''
            link = f"/astuces/{instance.slug}/"
            message = (
                f"💡 Nouvelle astuce : {instance.title}\n\n"
                f"{excerpt[:200]}{'…' if len(excerpt) > 200 else ''}\n\n"
                f"🔗 Lire l'astuce : {site_url}{link}"
            )
        else:
            return

        threading.Thread(
            target=_post_to_facebook,
            args=(message, site_url + link),
            daemon=True
        ).start()
    except Exception as e:
        logger.debug(f"Facebook schedule failed: {e}")


def _was_just_published(instance):
    """Retourne True si l'objet vient de passer à 'published' pour la 1ère fois."""
    key = f"{type(instance).__name__}_{instance.pk}"
    old_status = _pre_save_status.pop(key, None)
    return old_status is not None and old_status != 'published' and instance.status == 'published'


# ──────────────────────────────────────────────
# Image optimization helper
# ──────────────────────────────────────────────

def _optimize_model_images(instance):
    """Compresse toutes les ImageFields d'une instance (non bloquant)."""
    try:
        from django.db.models import ImageField
        from core.image_utils import optimize_image_field
        for field in instance._meta.get_fields():
            if isinstance(field, ImageField):
                optimize_image_field(instance, field.name)
        image_fields = [
            f.name for f in instance._meta.get_fields()
            if isinstance(f, ImageField)
        ]
        if image_fields:
            type(instance).objects.filter(pk=instance.pk).update(
                **{f: getattr(instance, f) for f in image_fields}
            )
    except Exception as e:
        logger.debug(f"Image optimization failed (non-critical): {e}")


# ──────────────────────────────────────────────
# Signal registration
# ──────────────────────────────────────────────

def register_content_signals():
    """Enregistre les signaux pour les modèles publiables et l'optimisation d'images."""
    try:
        from articles.models import Article
        from projects.models import Project
        from tips.models import Tip
        from core.models import SiteSettings

        # ── pre_save : mémorise l'ancien statut ──

        @receiver(pre_save, sender=Article, weak=False)
        def article_pre_save(sender, instance, **kwargs):
            if instance.pk:
                try:
                    old = Article.objects.get(pk=instance.pk)
                    _pre_save_status[f"Article_{instance.pk}"] = old.status
                except Article.DoesNotExist:
                    pass

        @receiver(pre_save, sender=Project, weak=False)
        def project_pre_save(sender, instance, **kwargs):
            if instance.pk:
                try:
                    old = Project.objects.get(pk=instance.pk)
                    _pre_save_status[f"Project_{instance.pk}"] = old.status
                except Project.DoesNotExist:
                    pass

        @receiver(pre_save, sender=Tip, weak=False)
        def tip_pre_save(sender, instance, **kwargs):
            if instance.pk:
                try:
                    old = Tip.objects.get(pk=instance.pk)
                    _pre_save_status[f"Tip_{instance.pk}"] = old.status
                except Tip.DoesNotExist:
                    pass

        # ── post_save : actions après publication ──

        @receiver(post_save, sender=Article, weak=False)
        def article_saved(sender, instance, created, **kwargs):
            if instance.status == 'published':
                _schedule_ping(instance=instance, content_type='article')
            if _was_just_published(instance):
                _schedule_facebook_post(instance, 'article')
            if created:
                threading.Thread(
                    target=_optimize_model_images, args=(instance,), daemon=True
                ).start()

        @receiver(post_save, sender=Project, weak=False)
        def project_saved(sender, instance, created, **kwargs):
            if instance.status == 'published':
                _schedule_ping(instance=instance, content_type='project')
            if _was_just_published(instance):
                _schedule_facebook_post(instance, 'projet')
            if created:
                threading.Thread(
                    target=_optimize_model_images, args=(instance,), daemon=True
                ).start()

        @receiver(post_save, sender=Tip, weak=False)
        def tip_saved(sender, instance, created, **kwargs):
            if instance.status == 'published':
                _schedule_ping(instance=instance, content_type='tip')
            if _was_just_published(instance):
                _schedule_facebook_post(instance, 'astuce')
            if created:
                threading.Thread(
                    target=_optimize_model_images, args=(instance,), daemon=True
                ).start()

        @receiver(post_save, sender=SiteSettings, weak=False)
        def settings_saved(sender, instance, created, **kwargs):
            if created:
                threading.Thread(
                    target=_optimize_model_images, args=(instance,), daemon=True
                ).start()

    except Exception as e:
        logger.debug(f"Signal registration skipped: {e}")
