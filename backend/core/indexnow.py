"""
IndexNow — soumet les URLs fraîchement publiées à Bing (et Google via IndexNow).
Protocole officiel : https://www.indexnow.org/
"""
import uuid
import urllib.request
import urllib.error
import json
import logging

logger = logging.getLogger(__name__)


def get_or_create_indexnow_key():
    """Retourne la clé IndexNow depuis la BDD, en crée une si absente."""
    try:
        from core.models import SiteSettings
        s, _ = SiteSettings.objects.get_or_create(pk=1)
        if not s.indexnow_key:
            s.indexnow_key = uuid.uuid4().hex
            s.save(update_fields=['indexnow_key'])
        return s.indexnow_key
    except Exception as e:
        logger.debug(f"IndexNow key fetch failed: {e}")
        return None


def submit_url_indexnow(url, site_url=None):
    """
    Soumet une URL via le protocole IndexNow à Bing.
    Bing redistribue automatiquement aux autres moteurs partenaires (Yandex, etc.).
    Google teste IndexNow mais n'est pas encore partenaire officiel.

    Args:
        url: URL complète de la page publiée (ex: https://monsite.com/articles/mon-article/)
        site_url: URL de base du site (ex: https://monsite.com)
    Returns:
        dict avec 'success', 'status', 'engine', 'message'
    """
    try:
        from django.conf import settings as dj_settings
        if not site_url:
            site_url = getattr(dj_settings, 'SITE_URL', '').rstrip('/')

        if not site_url:
            return {'success': False, 'message': 'SITE_URL non configuré'}

        key = get_or_create_indexnow_key()
        if not key:
            return {'success': False, 'message': 'Clé IndexNow non disponible'}

        key_location = f"{site_url}/{key}.txt"

        payload = json.dumps({
            'host': site_url.replace('https://', '').replace('http://', ''),
            'key': key,
            'keyLocation': key_location,
            'urlList': [url],
        }).encode('utf-8')

        # Bing IndexNow endpoint (redistribue à Yandex, Seznam, etc.)
        req = urllib.request.Request(
            'https://api.indexnow.org/indexnow',
            data=payload,
            headers={
                'Content-Type': 'application/json; charset=utf-8',
                'User-Agent': 'LandryNet-IndexNow/1.0',
            },
            method='POST',
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            status = resp.status
            # 200 = OK, 202 = Accepted (en attente de vérification de la clé)
            ok = status in (200, 202)
            return {
                'success': ok,
                'status': status,
                'engine': 'IndexNow (Bing)',
                'message': f'HTTP {status} — {"Soumis avec succès" if ok else "Vérification en cours"}',
            }
    except urllib.error.HTTPError as e:
        if e.code == 422:
            msg = 'URL invalide ou host incorrect'
        elif e.code == 429:
            msg = 'Trop de requêtes — réessayez plus tard'
        elif e.code == 403:
            msg = 'Clé invalide ou key file inaccessible'
        else:
            msg = f'HTTP {e.code}'
        return {'success': False, 'status': e.code, 'engine': 'IndexNow', 'message': msg}
    except Exception as e:
        return {'success': False, 'engine': 'IndexNow', 'message': str(e)}


def submit_sitemap_indexnow(site_url=None):
    """
    Soumet le sitemap complet via IndexNow (utile après une mise à jour du sitemap).
    Bing aussi accepte une soumission de sitemap directe.
    """
    try:
        from django.conf import settings as dj_settings
        if not site_url:
            site_url = getattr(dj_settings, 'SITE_URL', '').rstrip('/')
        if not site_url:
            return {'success': False, 'message': 'SITE_URL non configuré'}

        sitemap_url = f"{site_url}/sitemap.xml"

        # Bing accepte encore le ping sitemap
        req = urllib.request.Request(
            f'https://www.bing.com/ping?sitemap={sitemap_url}',
            headers={'User-Agent': 'LandryNet-SitemapPing/1.0'},
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            status = resp.status
            ok = status in (200, 204)
            return {
                'success': ok,
                'status': status,
                'engine': 'Bing',
                'sitemap_url': sitemap_url,
                'message': f'Bing sitemap ping HTTP {status}',
            }
    except urllib.error.HTTPError as e:
        return {
            'success': False,
            'status': e.code,
            'engine': 'Bing',
            'message': f'HTTP {e.code}',
        }
    except Exception as e:
        return {'success': False, 'engine': 'Bing', 'message': str(e)}
