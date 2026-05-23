"""
Signals: ping Google Sitemap + optimisation automatique des images.
"""
import threading
import urllib.request
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Google Sitemap Ping
# ──────────────────────────────────────────────

def _ping_google(sitemap_url):
    try:
        req = urllib.request.Request(
            f"https://www.google.com/ping?sitemap={sitemap_url}",
            headers={'User-Agent': 'LandryNet-SitemapPing/1.0'}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            logger.info(f"Google sitemap ping: {resp.status} for {sitemap_url}")
    except Exception as e:
        logger.warning(f"Google sitemap ping failed (non-critical): {e}")


def ping_google_sitemap(sitemap_url):
    threading.Thread(target=_ping_google, args=(sitemap_url,), daemon=True).start()


def _schedule_ping():
    try:
        from django.conf import settings
        site_url = getattr(settings, 'SITE_URL', None)
        if not site_url:
            return
        ping_google_sitemap(f"{site_url.rstrip('/')}/sitemap.xml")
    except Exception as e:
        logger.debug(f"Ping schedule failed: {e}")


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
        # Re-save only the image fields without triggering signals again
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
        from portfolio.models import PortfolioItem
        from core.models import SiteSettings

        @receiver(post_save, sender=Article, weak=False)
        def article_saved(sender, instance, created, **kwargs):
            if instance.status == 'published':
                _schedule_ping()
            if created:
                threading.Thread(
                    target=_optimize_model_images, args=(instance,), daemon=True
                ).start()

        @receiver(post_save, sender=Project, weak=False)
        def project_saved(sender, instance, created, **kwargs):
            if instance.status == 'published':
                _schedule_ping()
            if created:
                threading.Thread(
                    target=_optimize_model_images, args=(instance,), daemon=True
                ).start()

        @receiver(post_save, sender=Tip, weak=False)
        def tip_saved(sender, instance, created, **kwargs):
            if instance.status == 'published':
                _schedule_ping()
            if created:
                threading.Thread(
                    target=_optimize_model_images, args=(instance,), daemon=True
                ).start()

        @receiver(post_save, sender=PortfolioItem, weak=False)
        def portfolio_saved(sender, instance, created, **kwargs):
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
