from django.core.mail import EmailMultiAlternatives, get_connection
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


def _get_site():
    from core.models import SiteSettings
    s = SiteSettings.objects.first()
    return s


def _resolve_smtp_host(host, email_user=''):
    """Auto-resolve the SMTP host.
    If the user accidentally typed their email address as host, fix it."""
    raw = (host or '').strip()
    if not raw or '@' in raw:
        # Derive the domain from host (if it's an email) or from email_user
        domain = raw.split('@')[-1].lower() if '@' in raw else (email_user or '').split('@')[-1].lower()
        smtp_map = {
            'gmail.com': 'smtp.gmail.com',
            'googlemail.com': 'smtp.gmail.com',
            'yahoo.com': 'smtp.mail.yahoo.com',
            'yahoo.fr': 'smtp.mail.yahoo.fr',
            'outlook.com': 'smtp-mail.outlook.com',
            'hotmail.com': 'smtp-mail.outlook.com',
            'hotmail.fr': 'smtp-mail.outlook.com',
            'live.com': 'smtp-mail.outlook.com',
            'live.fr': 'smtp-mail.outlook.com',
            'icloud.com': 'smtp.mail.me.com',
            'me.com': 'smtp.mail.me.com',
        }
        return smtp_map.get(domain, f'smtp.{domain}' if domain else 'smtp.gmail.com')
    return raw


def _build_smtp_connection(s):
    """Build an explicit SMTP connection from SiteSettings (thread-safe)."""
    host = _resolve_smtp_host(s.email_host, s.email_host_user)
    return get_connection(
        backend='django.core.mail.backends.smtp.EmailBackend',
        host=host,
        port=int(s.email_port or 587),
        username=s.email_host_user,
        password=s.email_host_password,
        use_tls=bool(s.email_use_tls),
        fail_silently=False,
    )


def _base_styles():
    return """
/* ── Reset ── */
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; background: #f0f2ff; margin: 0; padding: 0; -webkit-text-size-adjust: 100%; }

/* ── Wrapper ── */
.wrapper { width: 100%; background: #f0f2ff; padding: 40px 16px; }
.container { max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 20px; overflow: hidden; box-shadow: 0 8px 40px rgba(79,70,229,0.15), 0 2px 8px rgba(0,0,0,0.06); }

/* ── Header ── */
.header { background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%); padding: 44px 40px 36px; text-align: center; position: relative; }
.logo-circle { display: inline-flex; align-items: center; justify-content: center; width: 56px; height: 56px; background: rgba(255,255,255,0.18); border-radius: 16px; margin-bottom: 16px; font-weight: 900; font-size: 20px; color: #fff; letter-spacing: -0.5px; }
.site-name { color: #ffffff; font-size: 26px; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 6px; }
.site-tagline { color: rgba(255,255,255,0.75); font-size: 14px; font-weight: 400; }
.header-badge { display: inline-block; background: rgba(255,255,255,0.2); color: #ffffff; padding: 5px 16px; border-radius: 50px; font-size: 12px; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; margin-top: 16px; }

/* ── Body ── */
.body { padding: 40px 40px 32px; }
.greeting { font-size: 17px; color: #374151; line-height: 1.65; margin-bottom: 28px; }
.greeting strong { color: #1e1b4b; }

/* ── Content card ── */
.content-card { background: linear-gradient(145deg, #f8f7ff, #f0f2ff); border: 1px solid #e0e7ff; border-radius: 14px; padding: 28px; margin: 24px 0; position: relative; overflow: hidden; }
.content-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #4F46E5, #7C3AED); }
.content-type { display: inline-flex; align-items: center; gap: 5px; font-size: 11px; font-weight: 800; color: #4F46E5; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 12px; }
.content-title { font-size: 22px; font-weight: 800; color: #1e1b4b; line-height: 1.3; margin-bottom: 12px; }
.content-excerpt { font-size: 15px; color: #6b7280; line-height: 1.65; margin-bottom: 24px; }
.btn-cta { display: inline-block; background: linear-gradient(135deg, #4F46E5, #7C3AED); color: #ffffff !important; padding: 14px 32px; border-radius: 10px; text-decoration: none !important; font-weight: 700; font-size: 15px; letter-spacing: -0.2px; }

/* ── Author ── */
.author-row { display: flex; align-items: center; margin-top: 20px; gap: 12px; }
.author-avatar { width: 38px; height: 38px; border-radius: 10px; background: linear-gradient(135deg, #4F46E5, #7C3AED); display: flex; align-items: center; justify-content: center; color: white; font-weight: 800; font-size: 14px; flex-shrink: 0; }
.author-info { font-size: 13px; color: #9ca3af; }
.author-info strong { color: #4b5563; font-weight: 600; }

/* ── Divider ── */
.divider { border: none; border-top: 1px solid #e5e7eb; margin: 28px 0; }

/* ── Footer ── */
.footer { background: #1e1b4b; padding: 28px 40px; text-align: center; }
.footer p { color: rgba(255,255,255,0.55); font-size: 13px; line-height: 1.6; margin: 4px 0; }
.footer a { color: #a5b4fc; text-decoration: none; font-weight: 500; }
.footer a:hover { color: #c7d2fe; }
.footer .unsub { display: inline-block; margin-top: 12px; padding: 6px 16px; background: rgba(255,255,255,0.08); border-radius: 20px; font-size: 12px; color: rgba(255,255,255,0.5) !important; }

/* ── Welcome email ── */
.check-icon { display: inline-flex; align-items: center; justify-content: center; width: 64px; height: 64px; border-radius: 50%; background: linear-gradient(135deg, #10b981, #059669); margin: 0 auto 20px; }
.section-title { font-size: 20px; font-weight: 700; color: #1e1b4b; margin-bottom: 8px; }
.section-body { font-size: 15px; color: #6b7280; line-height: 1.65; }
.feature-row { display: flex; align-items: flex-start; gap: 12px; padding: 12px 0; border-bottom: 1px solid #f3f4f6; }
.feature-row:last-child { border-bottom: none; }
.feature-icon { width: 36px; height: 36px; border-radius: 9px; display: flex; align-items: center; justify-content: center; font-size: 16px; flex-shrink: 0; }
.feature-text { font-size: 14px; color: #374151; line-height: 1.5; }
.feature-text strong { color: #1e1b4b; display: block; margin-bottom: 2px; }

/* ── Contact ── */
.msg-field { margin-bottom: 16px; }
.msg-label { font-size: 11px; font-weight: 700; color: #9ca3af; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
.msg-value { font-size: 15px; color: #1e1b4b; line-height: 1.6; }
.msg-box { background: #f8f7ff; border-left: 3px solid #4F46E5; border-radius: 0 8px 8px 0; padding: 16px; margin-top: 8px; font-size: 15px; color: #374151; line-height: 1.65; white-space: pre-wrap; }
.ticket-badge { display: inline-block; background: #eef2ff; color: #4F46E5; padding: 3px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; }

@media (max-width: 600px) {
  .wrapper { padding: 16px 8px; }
  .header { padding: 32px 24px 28px; }
  .body { padding: 28px 24px 24px; }
  .footer { padding: 24px; }
  .content-card { padding: 20px; }
  .site-name { font-size: 22px; }
  .content-title { font-size: 19px; }
  .author-row { flex-direction: column; align-items: flex-start; }
}
"""


def _html_wrapper(content, footer_content=''):
    styles = _base_styles()
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <title>Email</title>
  <style>{styles}</style>
</head>
<body>
  <div class="wrapper">
    <div class="container">
      {content}
      <div class="footer">
        {footer_content}
      </div>
    </div>
  </div>
</body>
</html>"""


def send_newsletter_notification(title, excerpt, url, content_type_label, author_name='Landry'):
    """Send newsletter to all active subscribers when content is published."""
    from .models import Subscriber
    s = _get_site()
    if not s:
        return 0
    if not s.newsletter_send_on_publish:
        return 0
    if not s.email_host_user or not s.email_host_password:
        logger.warning('Newsletter notification not sent: SMTP not configured.')
        return 0

    subscribers = Subscriber.objects.filter(status='active')
    if not subscribers.exists():
        return 0

    type_icons = {'Article': '📝', 'Projet': '🚀', 'Astuce': '💡', 'Portfolio': '🎨'}
    type_colors = {'Article': '#4F46E5', 'Projet': '#10b981', 'Astuce': '#f59e0b', 'Portfolio': '#e11d48'}
    type_icon = type_icons.get(content_type_label, '✨')
    type_color = type_colors.get(content_type_label, '#4F46E5')

    from_email = f"{s.newsletter_from_name or s.site_name} <{s.email_host_user}>"
    sent_count = 0
    author_initial = (author_name[0] if author_name else 'L').upper()
    frontend_url = (settings.FRONTEND_URL or 'https://landryit.pythonanywhere.com').rstrip('/')
    logo_html = f'<img src="{frontend_url}{s.logo.url}" alt="{s.site_name}" style="height:60px;width:60px;border-radius:16px;object-fit:cover;margin-bottom:14px;">' if s.logo else f'<div class="logo-circle">{(s.site_name[:2] if s.site_name else "LN").upper()}</div>'

    for sub in subscribers:
        unsub_url = f"{frontend_url}/api/newsletter/unsubscribe/?token={sub.token}"
        subject = f"✨ {content_type_label} : {title} — {s.site_name}"
        greeting_name = sub.name.split()[0] if sub.name else 'vous'

        body_html = f"""
      <div class="header">
        {logo_html}
        <div class="site-name">{s.site_name}</div>
        <div class="site-tagline">{s.tagline}</div>
        <div class="header-badge">{type_icon} Nouvelle publication</div>
      </div>

      <div class="body">
        <p class="greeting">
          Bonjour <strong>{greeting_name}</strong>,<br><br>
          {s.newsletter_intro_text or 'Une nouvelle publication est disponible sur le site.'}
        </p>

        <div class="content-card">
          <div class="content-type" style="color:{type_color};">{type_icon} {content_type_label}</div>
          <div class="content-title">{title}</div>
          <div class="content-excerpt">{excerpt or 'Découvrez cette nouvelle publication sur le site.'}</div>
          <a href="{url}" class="btn-cta">Lire maintenant &rarr;</a>

          <div class="author-row">
            <div class="author-avatar">{author_initial}</div>
            <div class="author-info">Publié par <strong>{author_name}</strong></div>
          </div>
        </div>

        <hr class="divider">
        <p style="font-size:14px;color:#9ca3af;text-align:center;">
          Merci de nous lire ! Partagez cet article avec votre entourage 🙏
        </p>
      </div>"""

        footer_html = f"""
        <p>Vous recevez cet email car vous êtes abonné(e) à <strong style="color:#c7d2fe;">{s.site_name}</strong>.</p>
        <p><a href="{frontend_url}">{frontend_url}</a></p>
        <a href="{unsub_url}" class="unsub">Se désabonner</a>"""

        html = _html_wrapper(body_html, footer_html)
        plain = f"{subject}\n\n{s.newsletter_intro_text}\n\n{title}\n\n{excerpt}\n\nLire : {url}\n\nSe désabonner : {unsub_url}"

        try:
            conn = _build_smtp_connection(s)
            msg = EmailMultiAlternatives(subject, plain, from_email, [sub.email], connection=conn)
            msg.attach_alternative(html, "text/html")
            msg.send()
            sent_count += 1
        except Exception as e:
            logger.error(f"Failed to send newsletter to {sub.email}: {e}")

    logger.info(f"Newsletter sent to {sent_count} subscribers.")
    return sent_count


def send_welcome_email(subscriber_email, subscriber_name=''):
    """Send a beautiful welcome/confirmation email to a new subscriber."""
    s = _get_site()
    if not s or not s.email_host_user or not s.email_host_password:
        logger.warning('Welcome email not sent: SMTP not configured.')
        return False

    greeting_name = subscriber_name.split()[0] if subscriber_name else 'vous'
    from .models import Subscriber
    frontend_url = (settings.FRONTEND_URL or 'https://landryit.pythonanywhere.com').rstrip('/')
    logo_html = f'<img src="{frontend_url}{s.logo.url}" alt="{s.site_name}" style="height:60px;width:60px;border-radius:16px;object-fit:cover;margin-bottom:14px;">' if s.logo else f'<div class="logo-circle">{(s.site_name[:2] if s.site_name else "LN").upper()}</div>'
    try:
        sub = Subscriber.objects.get(email=subscriber_email)
        unsub_url = f"{frontend_url}/api/newsletter/unsubscribe/?token={sub.token}"
    except Exception:
        unsub_url = f"{frontend_url}/api/newsletter/unsubscribe/"

    from_email = f"{s.newsletter_from_name or s.site_name} <{s.email_host_user}>"
    subject = f"🎉 Bienvenue sur {s.site_name} — Abonnement confirmé !"

    body_html = f"""
      <div class="header">
        {logo_html}
        <div class="site-name">{s.site_name}</div>
        <div class="site-tagline">{s.tagline}</div>
        <div class="header-badge">🎉 Abonnement confirmé</div>
      </div>

      <div class="body">
        <div style="text-align:center;margin-bottom:28px;">
          <div class="check-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
          </div>
          <div class="section-title">Bienvenue {greeting_name} !</div>
          <div class="section-body">Votre abonnement à <strong>{s.site_name}</strong> est confirmé.<br>Vous recevrez une notification à chaque nouvelle publication.</div>
        </div>

        <div class="content-card" style="margin-bottom:24px;">
          <div style="font-size:14px;font-weight:700;color:#4F46E5;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:16px;">📬 Ce que vous allez recevoir</div>
          <div class="feature-row">
            <div class="feature-icon" style="background:#eef2ff;">📝</div>
            <div class="feature-text"><strong>Articles & Tutoriels</strong>Des guides pratiques sur Python, Django, React et plus encore.</div>
          </div>
          <div class="feature-row">
            <div class="feature-icon" style="background:#ecfdf5;">🚀</div>
            <div class="feature-text"><strong>Projets Open Source</strong>Des projets réels avec du code source disponible.</div>
          </div>
          <div class="feature-row">
            <div class="feature-icon" style="background:#fefce8;">💡</div>
            <div class="feature-text"><strong>Astuces de pro</strong>Des raccourcis et bonnes pratiques pour coder plus vite.</div>
          </div>
        </div>

        <div style="text-align:center;margin:28px 0;">
          <a href="{frontend_url}" class="btn-cta">Explorer le site →</a>
        </div>

        <hr class="divider">
        <p style="font-size:13px;color:#9ca3af;text-align:center;">
          Vous vous êtes abonné(e) avec <strong>{subscriber_email}</strong>
        </p>
      </div>"""

    footer_html = f"""
      <p>Merci de votre confiance ! 🙏</p>
      <p><a href="{frontend_url}">{frontend_url}</a></p>
      <a href="{unsub_url}" class="unsub">Se désabonner</a>"""

    html = _html_wrapper(body_html, footer_html)
    plain = f"Bienvenue sur {s.site_name} !\n\nVotre abonnement est confirmé. Vous recevrez les prochaines publications à {subscriber_email}.\n\nVisitez le site : {frontend_url}\nSe désabonner : {unsub_url}"

    try:
        conn = _build_smtp_connection(s)
        msg = EmailMultiAlternatives(subject, plain, from_email, [subscriber_email], connection=conn)
        msg.attach_alternative(html, "text/html")
        msg.send()
        logger.info(f"Welcome email sent to {subscriber_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send welcome email to {subscriber_email}: {e}")
        return False


def send_campaign(campaign_id):
    """Send a manual newsletter campaign to all active subscribers."""
    from .models import Subscriber, NewsletterCampaign
    from django.utils import timezone

    s = _get_site()
    if not s or not s.email_host_user or not s.email_host_password:
        return 0, "Email non configuré dans les paramètres du site."

    try:
        campaign = NewsletterCampaign.objects.get(pk=campaign_id)
    except NewsletterCampaign.DoesNotExist:
        return 0, "Campagne introuvable."

    subscribers = Subscriber.objects.filter(status='active')
    from_email = f"{s.newsletter_from_name or s.site_name} <{s.email_host_user}>"
    sent_count = 0
    frontend_url = (settings.FRONTEND_URL or 'https://landryit.pythonanywhere.com').rstrip('/')
    logo_html = f'<img src="{frontend_url}{s.logo.url}" alt="{s.site_name}" style="height:60px;width:60px;border-radius:16px;object-fit:cover;margin-bottom:14px;">' if s.logo else f'<div class="logo-circle">{(s.site_name[:2] if s.site_name else "LN").upper()}</div>'

    for sub in subscribers:
        unsub_url = f"{frontend_url}/api/newsletter/unsubscribe/?token={sub.token}"
        greeting_name = sub.name.split()[0] if sub.name else 'vous'

        body_html = f"""
      <div class="header">
        {logo_html}
        <div class="site-name">{s.site_name}</div>
        <div class="site-tagline">{s.tagline}</div>
        <div class="header-badge">📣 Newsletter</div>
      </div>

      <div class="body">
        <p class="greeting">Bonjour <strong>{greeting_name}</strong>,</p>
        <div style="font-size:16px;color:#374151;line-height:1.7;margin-top:20px;">
          {campaign.content}
        </div>
      </div>"""

        footer_html = f"""
      <p>Vous recevez cet email car vous êtes abonné(e) à <strong style="color:#c7d2fe;">{s.site_name}</strong>.</p>
      <a href="{unsub_url}" class="unsub">Se désabonner</a>"""

        html = _html_wrapper(body_html, footer_html)
        plain = f"{campaign.subject}\n\nBonjour {greeting_name},\n\n{strip_tags(campaign.content)}\n\nSe désabonner : {unsub_url}"

        try:
            conn = _build_smtp_connection(s)
            msg = EmailMultiAlternatives(campaign.subject, plain, from_email, [sub.email], connection=conn)
            msg.attach_alternative(html, "text/html")
            msg.send()
            sent_count += 1
        except Exception as e:
            logger.error(f"Failed to send campaign to {sub.email}: {e}")

    campaign.status = 'sent'
    campaign.sent_at = timezone.now()
    campaign.save(update_fields=['status', 'sent_at'])
    return sent_count, f"{sent_count} email(s) envoyé(s) avec succès."
