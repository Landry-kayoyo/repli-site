"""
Email & Newsletter diagnostic views — admin only.
"""
import json
import smtplib
import ssl
import logging
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone


def _staff_json_required(view_func):
    """Retourne JSON 403 pour les endpoints AJAX si non authentifié staff."""
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return JsonResponse(
                {"error": "Session expirée. Veuillez vous reconnecter à l'admin (/admin/)."},
                status=403
            )
        return view_func(request, *args, **kwargs)
    return wrapper


logger = logging.getLogger(__name__)


@staff_member_required
def diagnostic_page(request):
    """Main diagnostic dashboard page."""
    from core.models import SiteSettings, AIConfig
    from newsletter.models import Subscriber
    from django.contrib.auth.models import User
    from contact.models import ContactMessage
    from articles.models import Article
    from projects.models import Project
    from tips.models import Tip
    from comments.models import Comment
    from reactions.models import Reaction
    from core.models import PageView
    from django.db.models import Sum, Count

    s, _ = SiteSettings.objects.get_or_create(pk=1)

    # Newsletter stats
    total_subs = Subscriber.objects.count()
    active_subs = Subscriber.objects.filter(status='active').count()
    unsub = Subscriber.objects.filter(status='unsubscribed').count()
    confirmed_subs = Subscriber.objects.filter(confirmed=True).count()
    recent_subs = list(
        Subscriber.objects.order_by('-created_at')[:8]
        .values('email', 'status', 'confirmed', 'created_at')
    )

    # Contact messages
    total_contacts = ContactMessage.objects.count()
    recent_contacts = list(
        ContactMessage.objects.order_by('-created_at')[:5]
        .values('name', 'email', 'subject', 'created_at')
    )

    # Email config
    email_config = {
        'host': s.email_host or 'Non configuré',
        'port': s.email_port,
        'use_tls': s.email_use_tls,
        'user': s.email_host_user or '⚠️ Non configuré',
        'contact_email': s.contact_email or '⚠️ Non configuré',
        'password_set': bool(s.email_host_password),
        'password_length': len(s.email_host_password) if s.email_host_password else 0,
        'is_gmail': 'gmail' in (s.email_host or '').lower(),
        'is_configured': bool(s.email_host_user and s.email_host_password),
    }

    # AI config
    active_ai = AIConfig.objects.filter(is_active=True).first()
    ai_configs_count = AIConfig.objects.count()

    # Admin users
    admins = list(User.objects.filter(is_staff=True).values('username', 'email', 'is_superuser', 'last_login', 'is_active'))

    # Site stats
    try:
        from datetime import timedelta
        today = timezone.now().date()
        views_today = PageView.objects.filter(date=today).aggregate(t=Sum('count'))['t'] or 0
        views_7 = PageView.objects.filter(date__gte=today - timedelta(days=7)).aggregate(t=Sum('count'))['t'] or 0
    except Exception:
        views_today = views_7 = 0

    context = {
        'title': 'Diagnostic complet',
        'email_config': email_config,
        'newsletter': {
            'total': total_subs,
            'active': active_subs,
            'unsubscribed': unsub,
            'confirmed': confirmed_subs,
            'recent': recent_subs,
        },
        'contacts': {
            'total': total_contacts,
            'recent': recent_contacts,
        },
        'ai': {
            'active': active_ai,
            'count': ai_configs_count,
            'site_key_set': bool(s.ai_api_key),
            'enabled': s.ai_enabled,
        },
        'stats': {
            'articles': Article.objects.count(),
            'articles_pub': Article.objects.filter(status='published').count(),
            'projects': Project.objects.count(),
            'tips': Tip.objects.count(),
            'comments_pending': Comment.objects.filter(is_approved=False).count(),
            'reactions': Reaction.objects.count(),
            'views_today': views_today,
            'views_7': views_7,
        },
        'admins': admins,
        's': s,
        'opts': {'app_label': 'core'},
    }
    return render(request, 'admin/email_diagnostic.html', context)


@_staff_json_required
@csrf_exempt
@require_POST
def test_smtp_connection(request):
    """Test SMTP connection step by step."""
    from core.models import SiteSettings
    s, _ = SiteSettings.objects.get_or_create(pk=1)

    from newsletter.utils import _resolve_smtp_host
    steps = []
    raw_host = s.email_host or ''
    host = _resolve_smtp_host(raw_host, s.email_host_user)
    host_was_fixed = raw_host and raw_host != host
    port = s.email_port or 587
    use_tls = s.email_use_tls
    user = s.email_host_user
    password = s.email_host_password

    # Check config
    if not user:
        return JsonResponse({'success': False, 'steps': [
            {'step': 'Configuration', 'status': 'error',
             'msg': '❌ Email non configuré — allez dans Admin → Paramètres du site'}
        ]})
    if not password:
        return JsonResponse({'success': False, 'steps': [
            {'step': 'Configuration', 'status': 'error',
             'msg': '❌ Mot de passe non configuré — renseignez votre Mot de Passe d\'Application Gmail'}
        ]})

    config_msg = f'✅ Email: {user} | Hôte: {host}:{port} | TLS: {use_tls}'
    if host_was_fixed:
        config_msg += f' ⚠️ Hôte corrigé automatiquement (était: {raw_host} → {host})'
    steps.append({'step': 'Configuration', 'status': 'ok', 'msg': config_msg})

    # Step 1: TCP connection
    smtp = None
    try:
        smtp = smtplib.SMTP(host, port, timeout=12)
        steps.append({'step': f'Connexion TCP ({host}:{port})', 'status': 'ok',
                      'msg': '✅ Connexion au serveur SMTP établie'})
    except Exception as e:
        steps.append({'step': f'Connexion TCP ({host}:{port})', 'status': 'error',
                      'msg': f'❌ Impossible de se connecter : {str(e)}'})
        return JsonResponse({'success': False, 'steps': steps})

    # Step 2: EHLO
    try:
        code, msg = smtp.ehlo()
        steps.append({'step': 'Identification EHLO', 'status': 'ok',
                      'msg': f'✅ Serveur identifié (code {code})'})
    except Exception as e:
        steps.append({'step': 'Identification EHLO', 'status': 'error',
                      'msg': f'❌ Erreur EHLO : {str(e)}'})
        smtp.quit()
        return JsonResponse({'success': False, 'steps': steps})

    # Step 3: STARTTLS
    if use_tls:
        try:
            ctx = ssl.create_default_context()
            smtp.starttls(context=ctx)
            smtp.ehlo()
            steps.append({'step': 'Chiffrement STARTTLS/TLS', 'status': 'ok',
                          'msg': '✅ Connexion chiffrée TLS active'})
        except ssl.SSLError as e:
            steps.append({'step': 'Chiffrement STARTTLS/TLS', 'status': 'error',
                          'msg': f'❌ Erreur SSL/TLS : {str(e)}'})
            smtp.quit()
            return JsonResponse({'success': False, 'steps': steps})
        except Exception as e:
            steps.append({'step': 'Chiffrement STARTTLS/TLS', 'status': 'error',
                          'msg': f'❌ Erreur TLS : {str(e)}'})
            smtp.quit()
            return JsonResponse({'success': False, 'steps': steps})

    # Step 4: Authentication
    try:
        smtp.login(user, password)
        steps.append({'step': f'Authentification Gmail ({user})', 'status': 'ok',
                      'msg': '✅ Authentification réussie — prêt à envoyer'})
    except smtplib.SMTPAuthenticationError as e:
        error_str = str(e)
        if '535' in error_str or 'Username and Password' in error_str or 'BadCredentials' in error_str:
            tip = ('Le Mot de Passe d\'Application Gmail doit être généré sur '
                   'myaccount.google.com/apppasswords — pas votre mot de passe habituel. '
                   'La vérification en 2 étapes doit être activée.')
        else:
            tip = str(e)
        steps.append({'step': f'Authentification Gmail ({user})', 'status': 'error',
                      'msg': f'❌ Authentification échouée : {tip}'})
        smtp.quit()
        return JsonResponse({'success': False, 'steps': steps})
    except Exception as e:
        steps.append({'step': 'Authentification', 'status': 'error',
                      'msg': f'❌ Erreur : {str(e)}'})
        smtp.quit()
        return JsonResponse({'success': False, 'steps': steps})

    smtp.quit()
    return JsonResponse({'success': True, 'steps': steps})


@_staff_json_required
@csrf_exempt
@require_POST
def send_test_email(request):
    """Send an HTML test email."""
    from core.models import SiteSettings
    from django.core.mail import get_connection, EmailMultiAlternatives

    s, _ = SiteSettings.objects.get_or_create(pk=1)

    if not s.email_host_user or not s.email_host_password:
        return JsonResponse({
            'success': False,
            'msg': '❌ Email ou mot de passe non configuré dans Paramètres du site.'
        })

    try:
        body = json.loads(request.body)
        recipient = body.get('email', '').strip() or s.contact_email or s.email_host_user
    except Exception:
        recipient = s.contact_email or s.email_host_user

    now = timezone.now().strftime('%d/%m/%Y à %H:%M')

    html_body = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="font-family:Inter,Arial,sans-serif;background:#f0f4f8;margin:0;padding:20px;">
<div style="max-width:560px;margin:0 auto;background:white;border-radius:16px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.08);">
  <div style="background:linear-gradient(135deg,#0d6efd,#0dcaf0);padding:30px;text-align:center;">
    <div style="width:56px;height:56px;background:rgba(255,255,255,0.2);border-radius:50%;margin:0 auto 14px;line-height:56px;font-size:28px;">✅</div>
    <h1 style="color:white;margin:0;font-size:22px;font-weight:700;">Configuration email réussie !</h1>
    <p style="color:rgba(255,255,255,0.85);margin:8px 0 0;font-size:14px;">Votre site Landry Net peut envoyer des emails</p>
  </div>
  <div style="padding:28px 30px;">
    <p style="color:#374151;font-size:15px;margin:0 0 20px;">🎉 Félicitations ! Si vous recevez cet email, cela signifie que votre configuration SMTP est parfaitement opérationnelle.</p>
    <div style="background:#f8faff;border:1px solid #e0e7ff;border-radius:10px;padding:18px;margin-bottom:20px;">
      <table style="width:100%;border-collapse:collapse;font-size:13px;color:#374151;">
        <tr><td style="padding:7px 0;font-weight:600;width:45%;">Serveur SMTP :</td><td style="color:#0d6efd;">{s.email_host}:{s.email_port}</td></tr>
        <tr><td style="padding:7px 0;font-weight:600;">Compte expéditeur :</td><td>{s.email_host_user}</td></tr>
        <tr><td style="padding:7px 0;font-weight:600;">Chiffrement :</td><td>{'TLS (STARTTLS) — Sécurisé ✅' if s.email_use_tls else 'Aucun ⚠️'}</td></tr>
        <tr><td style="padding:7px 0;font-weight:600;">Destinataire test :</td><td>{recipient}</td></tr>
        <tr><td style="padding:7px 0;font-weight:600;">Envoyé le :</td><td>{now}</td></tr>
      </table>
    </div>
    <p style="color:#6b7280;font-size:13px;border-top:1px solid #f0f0f0;padding-top:16px;margin:0;">
      Ce mail a été envoyé depuis le panel d\'administration de <strong>Landry Net</strong>.
    </p>
  </div>
</div>
</body></html>"""

    try:
        connection = get_connection(
            backend='django.core.mail.backends.smtp.EmailBackend',
            host=s.email_host or 'smtp.gmail.com',
            port=s.email_port or 587,
            username=s.email_host_user,
            password=s.email_host_password,
            use_tls=bool(s.email_use_tls),
            fail_silently=False,
        )
        msg = EmailMultiAlternatives(
            subject=f'✅ Email de test — Landry Net Admin ({now})',
            body=f'Email de test envoyé depuis le panel Landry Net le {now}.',
            from_email=s.email_host_user,
            to=[recipient],
            connection=connection,
        )
        msg.attach_alternative(html_body, 'text/html')
        msg.send()
        return JsonResponse({
            'success': True,
            'msg': f'✅ Email de test envoyé avec succès à {recipient} — vérifiez votre boîte mail !',
            'recipient': recipient
        })
    except smtplib.SMTPAuthenticationError:
        return JsonResponse({
            'success': False,
            'msg': ('❌ Authentification Gmail échouée.\n\n'
                    'Votre Mot de Passe d\'Application doit être généré sur '
                    'myaccount.google.com/apppasswords\n'
                    '(pas votre mot de passe Gmail habituel).')
        })
    except smtplib.SMTPConnectError:
        return JsonResponse({
            'success': False,
            'msg': f'❌ Impossible de se connecter à {s.email_host}:{s.email_port}. Vérifiez le serveur et le port.'
        })
    except Exception as e:
        logger.error(f"send_test_email error: {e}")
        return JsonResponse({'success': False, 'msg': f'❌ Erreur inattendue : {str(e)}'})


@staff_member_required
def newsletter_management(request):
    """Newsletter management page — compose and send to all active subscribers."""
    from newsletter.models import Subscriber, NewsletterCampaign
    stats = {
        'total': Subscriber.objects.count(),
        'active': Subscriber.objects.filter(status='active').count(),
        'confirmed': Subscriber.objects.filter(status='active', confirmed=True).count(),
        'unsubscribed': Subscriber.objects.filter(status='unsubscribed').count(),
    }
    campaigns = NewsletterCampaign.objects.order_by('-created_at')[:10]
    from core.models import SiteSettings
    site_settings = SiteSettings.objects.first()
    smtp_ok = bool(site_settings and site_settings.email_host_user and site_settings.email_host_password) if site_settings else False
    ctx = {
        'title': 'Gestion Newsletter',
        'stats': stats,
        'campaigns': campaigns,
        'smtp_ok': smtp_ok,
        'site_settings': site_settings,
    }
    return render(request, 'admin/newsletter_management.html', ctx)


@staff_member_required
def send_newsletter_campaign(request):
    """Create and send a newsletter campaign."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    import json
    try:
        body = json.loads(request.body)
        subject = body.get('subject', '').strip()
        content = body.get('content', '').strip()
        send_now = body.get('send_now', False)
    except Exception:
        return JsonResponse({'error': 'JSON invalide'}, status=400)

    if not subject or not content:
        return JsonResponse({'error': 'Sujet et contenu requis'}, status=400)

    from newsletter.models import NewsletterCampaign
    campaign = NewsletterCampaign.objects.create(subject=subject, content=content, status='draft')

    if send_now:
        try:
            from newsletter.utils import send_campaign
            sent, msg = send_campaign(campaign.pk)
            return JsonResponse({'ok': True, 'sent': sent, 'message': msg, 'campaign_id': campaign.pk})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e), 'campaign_id': campaign.pk}, status=500)
    else:
        return JsonResponse({'ok': True, 'sent': 0, 'message': 'Brouillon sauvegardé.', 'campaign_id': campaign.pk})
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone


@staff_member_required
def editorial_calendar(request):
    """Editorial calendar — shows all content by publish date."""
    from articles.models import Article
    from projects.models import Project
    from tips.models import Tip

    events = []

    try:
        for a in Article.objects.only('id', 'title', 'status', 'published_at', 'created_at', 'slug').order_by('-published_at')[:60]:
            date = a.published_at or a.created_at
            if date:
                events.append({
                    'id': f'article-{a.id}',
                    'title': a.title,
                    'date': date.strftime('%Y-%m-%d'),
                    'type': 'article',
                    'status': a.status,
                    'url': f'/admin/articles/article/{a.id}/change/',
                    'view_url': f'/articles/{a.slug}/',
                    'color': '#4f46e5' if a.status == 'published' else '#94a3b8',
                })
    except Exception:
        pass

    try:
        for p in Project.objects.only('id', 'title', 'status', 'published_at', 'created_at', 'slug').order_by('-published_at')[:30]:
            date = p.published_at or p.created_at
            if date:
                events.append({
                    'id': f'project-{p.id}',
                    'title': p.title,
                    'date': date.strftime('%Y-%m-%d'),
                    'type': 'project',
                    'status': p.status,
                    'url': f'/admin/projects/project/{p.id}/change/',
                    'view_url': f'/projets/{p.slug}/',
                    'color': '#0891b2' if p.status == 'published' else '#94a3b8',
                })
    except Exception:
        pass

    try:
        for t in Tip.objects.only('id', 'title', 'status', 'published_at', 'created_at', 'slug').order_by('-published_at')[:30]:
            date = t.published_at or t.created_at
            if date:
                events.append({
                    'id': f'tip-{t.id}',
                    'title': t.title,
                    'date': date.strftime('%Y-%m-%d'),
                    'type': 'tip',
                    'status': t.status,
                    'url': f'/admin/tips/tip/{t.id}/change/',
                    'view_url': f'/astuces/{t.slug}/',
                    'color': '#16a34a' if t.status == 'published' else '#94a3b8',
                })
    except Exception:
        pass

    return render(request, 'admin/editorial_calendar.html', {
        'events_json': json.dumps(events),
        'title': 'Calendrier Éditorial',
    })


# ──────────────────────────────────────────────
# SEO Diagnostic
# ──────────────────────────────────────────────

@staff_member_required
def facebook_diagnostic(request):
    """Page de test de la connexion Facebook."""
    from core.models import SiteSettings
    s, _ = SiteSettings.objects.get_or_create(pk=1)
    return render(request, 'admin/facebook_diagnostic.html', {
        'title': 'Test Facebook',
        's': s,
        'configured': bool(s.facebook_page_id and s.facebook_page_token),
        'auto_post': s.facebook_auto_post,
    })


@_staff_json_required
@csrf_exempt
@require_POST
def facebook_test_connection(request):
    """Vérifie que le token + page_id sont valides via l'API Graph."""
    import urllib.request as ureq
    import urllib.parse
    from core.models import SiteSettings

    s, _ = SiteSettings.objects.get_or_create(pk=1)
    page_id = s.facebook_page_id.strip()
    token = s.facebook_page_token.strip()

    if not page_id or not token:
        return JsonResponse({
            'success': False,
            'steps': [{'step': 'Configuration', 'status': 'error',
                        'msg': '❌ ID de page ou token manquant — remplis les champs dans Paramètres du site.'}]
        })

    steps = []

    # Étape 1 : vérifier le token (me?access_token=...)
    try:
        url = f"https://graph.facebook.com/v19.0/me?access_token={urllib.parse.quote(token)}&fields=id,name,type"
        req = ureq.Request(url, headers={'User-Agent': 'LandryNet/1.0'})
        with ureq.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
            name = data.get('name', '?')
            fb_id = data.get('id', '?')
            steps.append({'step': 'Validation du token', 'status': 'ok',
                           'msg': f'✅ Token valide — Page : <strong>{name}</strong> (ID: {fb_id})'})
    except Exception as e:
        err = str(e)
        if '190' in err or 'Invalid OAuth' in err or 'OAuthException' in err:
            msg = '❌ Token invalide ou expiré — génère un nouveau Page Access Token sur Meta for Developers.'
        elif '400' in err:
            msg = f'❌ Requête invalide : {err}'
        else:
            msg = f'❌ Erreur réseau : {err}'
        return JsonResponse({'success': False, 'steps': [{'step': 'Validation du token', 'status': 'error', 'msg': msg}]})

    # Étape 2 : vérifier les permissions
    try:
        url = f"https://graph.facebook.com/v19.0/me/permissions?access_token={urllib.parse.quote(token)}"
        req = ureq.Request(url, headers={'User-Agent': 'LandryNet/1.0'})
        with ureq.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
            perms = {p['permission']: p['status'] for p in data.get('data', [])}
            needed = ['pages_manage_posts', 'pages_read_engagement']
            granted = [p for p in needed if perms.get(p) == 'granted']
            missing = [p for p in needed if p not in granted]
            if missing:
                steps.append({'step': 'Permissions', 'status': 'warn',
                               'msg': f'⚠️ Permissions manquantes : <code>{", ".join(missing)}</code> — retourne dans Graph API Explorer et coche-les.'})
            else:
                steps.append({'step': 'Permissions', 'status': 'ok',
                               'msg': '✅ Toutes les permissions nécessaires sont accordées (<code>pages_manage_posts</code>, <code>pages_read_engagement</code>)'})
    except Exception as e:
        steps.append({'step': 'Permissions', 'status': 'warn', 'msg': f'⚠️ Impossible de vérifier les permissions : {e}'})

    # Étape 3 : vérifier l'accès à la page
    try:
        url = f"https://graph.facebook.com/v19.0/{urllib.parse.quote(page_id)}?access_token={urllib.parse.quote(token)}&fields=id,name,fan_count"
        req = ureq.Request(url, headers={'User-Agent': 'LandryNet/1.0'})
        with ureq.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
            fans = data.get('fan_count', 'N/A')
            steps.append({'step': "Accès à la Page", 'status': 'ok',
                           'msg': f'✅ Page accessible — <strong>{data.get("name")}</strong> · {fans} abonnés'})
    except Exception as e:
        err = str(e)
        if '100' in err or 'nodes' in err.lower():
            msg = f'❌ Page introuvable avec cet ID ({page_id}) — vérifie l\'ID de ta page.'
        else:
            msg = f'❌ Erreur d\'accès à la page : {err}'
        steps.append({'step': "Accès à la Page", 'status': 'error', 'msg': msg})

    all_ok = all(s['status'] == 'ok' for s in steps)
    return JsonResponse({'success': all_ok, 'steps': steps})


@_staff_json_required
@csrf_exempt
@require_POST
def facebook_test_post(request):
    """Publie un vrai post de test sur la Page Facebook."""
    import urllib.request as ureq
    import urllib.parse
    from core.models import SiteSettings
    from django.conf import settings as django_settings

    s, _ = SiteSettings.objects.get_or_create(pk=1)
    page_id = s.facebook_page_id.strip()
    token = s.facebook_page_token.strip()

    if not page_id or not token:
        return JsonResponse({'success': False, 'msg': '❌ Configuration Facebook manquante.'})

    site_url = getattr(django_settings, 'SITE_URL', '').rstrip('/')
    message = (
        f"🎉 Test de publication automatique depuis Landry Net !\n\n"
        f"Si tu vois ce message, la connexion entre ton site et ta Page Facebook fonctionne parfaitement. "
        f"Les futurs articles, projets et astuces seront publiés automatiquement ici.\n\n"
        f"🌐 {site_url}"
    )

    try:
        data = urllib.parse.urlencode({
            'message': message,
            'access_token': token,
        }).encode('utf-8')
        req = ureq.Request(
            f'https://graph.facebook.com/v19.0/{page_id}/feed',
            data=data, method='POST',
            headers={'User-Agent': 'LandryNet/1.0'},
        )
        with ureq.urlopen(req, timeout=10) as r:
            result = json.loads(r.read().decode())
            post_id = result.get('id', '')
            post_url = f"https://www.facebook.com/{post_id.replace('_', '/posts/')}" if post_id else ''
            return JsonResponse({
                'success': True,
                'msg': f'✅ Post publié avec succès sur ta Page Facebook !',
                'post_id': post_id,
                'post_url': post_url,
            })
    except Exception as e:
        err = str(e)
        if '200' in err or 'permission' in err.lower():
            msg = '❌ Permission refusée — assure-toi que le token est un <strong>Page Access Token</strong> (pas un User Token) avec la permission <code>pages_manage_posts</code>.'
        else:
            msg = f'❌ Erreur lors de la publication : {err}'
        return JsonResponse({'success': False, 'msg': msg})


@staff_member_required
def seo_diagnostic(request):
    """Page de diagnostic SEO : robots.txt, sitemap, IndexNow, pings moteurs.
    Utilise le client Django interne pour éviter les restrictions réseau
    (PythonAnywhere bloque les auto-requêtes HTTP sortantes).
    """
    from django.conf import settings as django_settings
    from django.test import Client as DjangoClient

    site_url = getattr(django_settings, 'SITE_URL', '').rstrip('/')

    def _fetch_internal(path):
        """Appel interne via le client Django — pas de requête réseau, fonctionne partout."""
        try:
            c = DjangoClient(SERVER_NAME='localhost')
            resp = c.get(path, HTTP_USER_AGENT='LandryNet-SEO-Check/1.0')
            body = resp.content.decode('utf-8', errors='replace')
            ok = resp.status_code in (200, 301, 302)
            return {'ok': ok, 'status': resp.status_code, 'body': body, 'error': None}
        except Exception as e:
            return {'ok': False, 'status': None, 'body': '', 'error': str(e)}

    robots_url  = f"{site_url}/robots.txt"  if site_url else ''
    sitemap_url = f"{site_url}/sitemap.xml" if site_url else ''

    robots_result  = _fetch_internal('/robots.txt')  if site_url else {'ok': False, 'status': None, 'body': '', 'error': 'SITE_URL non configuré'}
    sitemap_result = _fetch_internal('/sitemap.xml') if site_url else {'ok': False, 'status': None, 'body': '', 'error': 'SITE_URL non configuré'}

    # Nombre d'URLs dans le sitemap
    sitemap_url_count = 0
    if sitemap_result['ok']:
        sitemap_url_count = sitemap_result['body'].count('<loc>')

    # IndexNow — vérification locale (pas de requête réseau)
    indexnow_key     = None
    indexnow_key_url = None
    indexnow_key_ok  = False
    try:
        from core.indexnow import get_or_create_indexnow_key
        indexnow_key = get_or_create_indexnow_key()
        if indexnow_key and site_url:
            indexnow_key_url = f"{site_url}/{indexnow_key}.txt"
            # Vérification interne sans requête réseau
            key_resp = _fetch_internal(f'/{indexnow_key}.txt')
            indexnow_key_ok = key_resp['ok'] and key_resp['body'].strip() == indexnow_key
    except Exception:
        pass

    context = {
        'title': 'Diagnostic SEO',
        'site_url': site_url,
        'robots_url': robots_url,
        'sitemap_url': sitemap_url,
        'robots': robots_result,
        'sitemap': sitemap_result,
        'sitemap_url_count': sitemap_url_count,
        'indexnow_key': indexnow_key,
        'indexnow_key_url': indexnow_key_url,
        'indexnow_key_ok': indexnow_key_ok,
        'opts': {'app_label': 'core'},
    }
    return render(request, 'admin/seo_diagnostic.html', context)


@_staff_json_required
@csrf_exempt
@require_POST
def seo_ping_now(request):
    """Déclenche manuellement IndexNow + Bing sitemap ping.
    Note: Google a déprécié son endpoint /ping en janvier 2023 (retourne 410 Gone).
    On utilise maintenant IndexNow (Bing, Yandex, Seznam…).
    """
    from django.conf import settings as django_settings
    from django.utils import timezone
    import urllib.request as ureq
    import urllib.error

    site_url = getattr(django_settings, 'SITE_URL', '').rstrip('/')
    if not site_url:
        return JsonResponse({'success': False, 'error': 'SITE_URL non configuré'})

    sitemap_url = f"{site_url}/sitemap.xml"
    results = []

    # 1. IndexNow (Bing + partenaires) — soumettre le sitemap
    try:
        from core.indexnow import get_or_create_indexnow_key
        import json as _json
        key = get_or_create_indexnow_key()
        if key:
            key_location = f"{site_url}/{key}.txt"
            payload = _json.dumps({
                'host': site_url.replace('https://', '').replace('http://', ''),
                'key': key,
                'keyLocation': key_location,
                'urlList': [site_url + '/'],
            }).encode('utf-8')
            req = ureq.Request(
                'https://api.indexnow.org/indexnow',
                data=payload,
                headers={
                    'Content-Type': 'application/json; charset=utf-8',
                    'User-Agent': 'LandryNet-IndexNow/1.0',
                },
                method='POST',
            )
            with ureq.urlopen(req, timeout=8) as r:
                ok = r.status in (200, 202)
                results.append({
                    'engine': 'IndexNow',
                    'status': r.status,
                    'ok': ok,
                    'deprecated': False,
                    'note': 'Soumission aux moteurs partenaires (Bing, Yandex, Seznam…)',
                })
        else:
            results.append({
                'engine': 'IndexNow',
                'status': None,
                'ok': False,
                'deprecated': False,
                'note': '',
                'error': 'Clé IndexNow non disponible',
            })
    except ureq.error.HTTPError as e:
        err_map = {422: 'URL invalide', 429: 'Trop de requêtes', 403: 'Clé invalide ou key file inaccessible'}
        results.append({
            'engine': 'IndexNow',
            'status': e.code,
            'ok': False,
            'deprecated': False,
            'note': '',
            'error': err_map.get(e.code, f'HTTP {e.code}'),
        })
    except Exception as e:
        err_str = str(e)
        if any(w in err_str.lower() for w in ('timed out', 'timeout', 'connection refused', 'name or service', 'nodename', 'network')):
            err_str = 'Connexion bloquée par l\'hébergeur (PythonAnywhere restreint les connexions sortantes). Le ping automatique à la publication fonctionnera depuis un hébergeur sans restriction.'
        results.append({
            'engine': 'IndexNow',
            'status': None,
            'ok': False,
            'deprecated': False,
            'note': '',
            'error': err_str,
        })

    # 2. Bing sitemap ping (toujours actif)
    try:
        req = ureq.Request(
            f'https://www.bing.com/ping?sitemap={sitemap_url}',
            headers={'User-Agent': 'LandryNet-SitemapPing/1.0'}
        )
        with ureq.urlopen(req, timeout=8) as r:
            ok = r.status in (200, 204, 301, 302)
            results.append({
                'engine': 'Bing',
                'status': r.status,
                'ok': ok,
                'deprecated': False,
                'note': 'Bing sitemap ping',
            })
    except ureq.error.HTTPError as e:
        results.append({
            'engine': 'Bing',
            'status': e.code,
            'ok': False,
            'deprecated': False,
            'note': '',
            'error': f'HTTP {e.code}',
        })
    except Exception as e:
        err_str = str(e)
        if any(w in err_str.lower() for w in ('timed out', 'timeout', 'connection refused', 'name or service', 'nodename', 'network')):
            err_str = 'Connexion bloquée par l\'hébergeur. PythonAnywhere restreint les requêtes sortantes — le ping automatique à la publication reste fonctionnel.'
        results.append({
            'engine': 'Bing',
            'status': None,
            'ok': False,
            'deprecated': False,
            'note': '',
            'error': err_str,
        })

    # 3. Google — déprécié, afficher uniquement comme info
    results.append({
        'engine': 'Google',
        'status': 410,
        'ok': False,
        'deprecated': True,
        'warning': True,
        'note': 'Endpoint déprécié par Google en janvier 2023. Utilisez Google Search Console.',
    })

    return JsonResponse({
        'success': True,
        'results': results,
        'sitemap_url': sitemap_url,
        'pinged_at': timezone.now().strftime('%d/%m/%Y à %H:%M:%S'),
    })
