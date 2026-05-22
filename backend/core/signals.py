"""
Signals pour le ping Google Sitemap lors de la publication de contenu.
"""
import threading
import urllib.request
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)

SITEMAP_URL = None  # Sera défini depuis settings


def _ping_google(sitemap_url):
    """Ping Google Indexing en arrière-plan (non bloquant)."""
    try:
        google_ping = f"https://www.google.com/ping?sitemap={sitemap_url}"
        req = urllib.request.Request(google_ping, headers={'User-Agent': 'LandryNet-SitemapPing/1.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            logger.info(f"Google sitemap ping: {resp.status} for {sitemap_url}")
    except Exception as e:
        logger.warning(f"Google sitemap ping failed (non-critical): {e}")


def ping_google_sitemap(sitemap_url):
    """Lance le ping Google dans un thread séparé pour ne pas bloquer la sauvegarde."""
    thread = threading.Thread(target=_ping_google, args=(sitemap_url,), daemon=True)
    thread.start()


def register_content_signals():
    """Enregistre les signaux pour les modèles de contenu publiables."""
    try:
        from articles.models import Article
        from projects.models import Project
        from tips.models import Tip

        @receiver(post_save, sender=Article, weak=False)
        def article_published(sender, instance, created, **kwargs):
            if instance.status == 'published':
                _schedule_ping()

        @receiver(post_save, sender=Project, weak=False)
        def project_published(sender, instance, created, **kwargs):
            if instance.status == 'published':
                _schedule_ping()

        @receiver(post_save, sender=Tip, weak=False)
        def tip_published(sender, instance, created, **kwargs):
            if instance.status == 'published':
                _schedule_ping()

    except Exception as e:
        logger.debug(f"Signal registration skipped: {e}")


def _schedule_ping():
    """Récupère l'URL du site depuis les settings et lance le ping."""
    try:
        from django.conf import settings
        site_url = getattr(settings, 'SITE_URL', None)
        if not site_url:
            return
        sitemap_url = f"{site_url.rstrip('/')}/sitemap.xml"
        ping_google_sitemap(sitemap_url)
    except Exception as e:
        logger.debug(f"Ping schedule failed: {e}")
