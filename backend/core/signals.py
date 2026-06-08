"""
Signals: ping Google + Bing Sitemap, Facebook auto-post, optimisation images.
"""
import threading
import urllib.request
import urllib.parse
import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)

# Mémorise le statut AVANT sauvegarde pour détecter le 1er passage à 'published'
_pre_save_status = {}


# ──────────────────────────────────────────────
# Sitemap Ping — Google + Bing
# ──────────────────────────────────────────────

def _ping_search_engines(sitemap_url):
    # Google a déprécié son /ping endpoint en janvier 2023 (retourne 410 Gone)
    # On tente quand même mais on ignore l'erreur 410
    engines = {
        'Google': f'https://www.google.com/ping?sitemap={sitemap_url}',
        'Bing':   f'https://www.bing.com/ping?sitemap={sitemap_url}',
    }
    for name, url in engines.items():
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'LandryNet-SitemapPing/1.0'}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                logger.info(f"{name} sitemap ping: {resp.status} for {sitemap_url}")
        except urllib.error.HTTPError as e:
            if e.code in (410, 404, 400) and name == 'Google':
                logger.info(f"Google sitemap ping endpoint deprecated (HTTP {e.code}) — normal depuis 2023")
            else:
                logger.warning(f"{name} sitemap ping failed (non-critical): HTTP {e.code}")
        except Exception as e:
            logger.warning(f"{name} sitemap ping failed (non-critical): {e}")


def _schedule_ping():
    try:
        from django.conf import settings
        site_url = getattr(settings, 'SITE_URL', None)
        if not site_url:
            return
        sitemap_url = f"{site_url.rstrip('/')}/sitemap.xml"
        threading.Thread(
            target=_ping_search_engines, args=(sitemap_url,), daemon=True
        ).start()
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
                _schedule_ping()
            if _was_just_published(instance):
                _schedule_facebook_post(instance, 'article')
            if created:
                threading.Thread(
                    target=_optimize_model_images, args=(instance,), daemon=True
                ).start()

        @receiver(post_save, sender=Project, weak=False)
        def project_saved(sender, instance, created, **kwargs):
            if instance.status == 'published':
                _schedule_ping()
            if _was_just_published(instance):
                _schedule_facebook_post(instance, 'projet')
            if created:
                threading.Thread(
                    target=_optimize_model_images, args=(instance,), daemon=True
                ).start()

        @receiver(post_save, sender=Tip, weak=False)
        def tip_saved(sender, instance, created, **kwargs):
            if instance.status == 'published':
                _schedule_ping()
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
