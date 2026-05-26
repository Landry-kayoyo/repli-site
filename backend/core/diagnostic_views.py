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


@staff_member_required
@csrf_exempt
@require_POST
def test_smtp_connection(request):
    """Test SMTP connection step by step."""
    from core.models import SiteSettings
    s, _ = SiteSettings.objects.get_or_create(pk=1)

    steps = []
    host = s.email_host or 'smtp.gmail.com'
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

    steps.append({'step': 'Configuration', 'status': 'ok',
                  'msg': f'✅ Email: {user} | Hôte: {host}:{port} | TLS: {use_tls}'})

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


@staff_member_required
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
