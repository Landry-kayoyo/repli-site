from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_newsletter_notification(title, excerpt, url, content_type_label, author_name='Landry'):
    from .models import Subscriber
    from core.models import SiteSettings

    site_settings = SiteSettings.objects.first()
    if not site_settings:
        return 0

    if not site_settings.newsletter_send_on_publish:
        return 0

    if not site_settings.email_host_user:
        return 0

    site_settings.apply_email_settings()

    subscribers = Subscriber.objects.filter(status='active')
    if not subscribers.exists():
        return 0

    from_email = f"{site_settings.newsletter_from_name} <{site_settings.email_host_user}>"
    sent_count = 0

    for subscriber in subscribers:
        unsubscribe_url = f"{settings.FRONTEND_URL}/api/newsletter/unsubscribe/?token={subscriber.token}"
        subject = f"[{site_settings.site_name}] Nouveau {content_type_label} : {title}"

        html_message = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f8fafc; margin: 0; padding: 0; }}
    .container {{ max-width: 600px; margin: 40px auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }}
    .header {{ background: linear-gradient(135deg, #4f46e5, #7c3aed); padding: 40px 32px; text-align: center; }}
    .header h1 {{ color: white; margin: 0; font-size: 24px; font-weight: 800; }}
    .header p {{ color: rgba(255,255,255,0.85); margin: 8px 0 0; font-size: 14px; }}
    .badge {{ display: inline-block; background: rgba(255,255,255,0.2); color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; margin-bottom: 12px; }}
    .body {{ padding: 40px 32px; }}
    .intro {{ color: #6b7280; font-size: 16px; line-height: 1.6; margin-bottom: 24px; }}
    .card {{ background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 12px; padding: 24px; margin: 24px 0; }}
    .card h2 {{ color: #111827; font-size: 22px; font-weight: 700; margin: 0 0 8px; }}
    .card p {{ color: #6b7280; font-size: 15px; line-height: 1.6; margin: 0 0 20px; }}
    .btn {{ display: inline-block; background: linear-gradient(135deg, #4f46e5, #7c3aed); color: white; padding: 14px 28px; border-radius: 10px; text-decoration: none; font-weight: 700; font-size: 15px; }}
    .footer {{ background: #f9fafb; padding: 24px 32px; text-align: center; border-top: 1px solid #e5e7eb; }}
    .footer p {{ color: #9ca3af; font-size: 13px; margin: 4px 0; }}
    .footer a {{ color: #6366f1; text-decoration: none; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="badge">✨ Nouvelle publication</div>
      <h1>{site_settings.site_name}</h1>
      <p>{site_settings.tagline}</p>
    </div>
    <div class="body">
      <p class="intro">
        Bonjour {subscriber.name or 'vous'},<br><br>
        {site_settings.newsletter_intro_text}
      </p>
      <div class="card">
        <p style="color:#6366f1; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin:0 0 8px;">{content_type_label}</p>
        <h2>{title}</h2>
        <p>{excerpt or 'Découvrez cette nouvelle publication sur le site.'}</p>
        <a href="{url}" class="btn">Lire maintenant →</a>
      </div>
      <p style="color:#9ca3af; font-size:13px;">Écrit par <strong>{author_name}</strong></p>
    </div>
    <div class="footer">
      <p>Vous recevez cet email car vous êtes abonné(e) à <strong>{site_settings.site_name}</strong>.</p>
      <p><a href="{unsubscribe_url}">Se désabonner</a> · <a href="{settings.FRONTEND_URL}">{settings.FRONTEND_URL}</a></p>
    </div>
  </div>
</body>
</html>
"""
        plain_message = f"{subject}\n\n{site_settings.newsletter_intro_text}\n\n{title}\n{excerpt}\n\nLire : {url}\n\nSe désabonner : {unsubscribe_url}"

        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=from_email,
                recipient_list=[subscriber.email],
                html_message=html_message,
                fail_silently=True,
            )
            sent_count += 1
        except Exception:
            pass

    return sent_count


def send_campaign(campaign_id):
    from .models import Subscriber, NewsletterCampaign
    from django.utils import timezone
    from core.models import SiteSettings

    site_settings = SiteSettings.objects.first()
    if not site_settings or not site_settings.email_host_user:
        return 0, "Email non configuré dans les paramètres du site."

    site_settings.apply_email_settings()

    try:
        campaign = NewsletterCampaign.objects.get(pk=campaign_id)
    except NewsletterCampaign.DoesNotExist:
        return 0, "Campagne introuvable."

    subscribers = Subscriber.objects.filter(status='active')
    from_email = f"{site_settings.newsletter_from_name} <{site_settings.email_host_user}>"
    sent_count = 0

    for subscriber in subscribers:
        unsubscribe_url = f"{settings.FRONTEND_URL}/api/newsletter/unsubscribe/?token={subscriber.token}"
        html_message = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f8fafc; margin: 0; padding: 0; }}
    .container {{ max-width: 600px; margin: 40px auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }}
    .header {{ background: linear-gradient(135deg, #4f46e5, #7c3aed); padding: 40px 32px; text-align: center; }}
    .header h1 {{ color: white; margin: 0; font-size: 24px; font-weight: 800; }}
    .body {{ padding: 40px 32px; color: #374151; font-size: 16px; line-height: 1.7; }}
    .footer {{ background: #f9fafb; padding: 24px 32px; text-align: center; border-top: 1px solid #e5e7eb; }}
    .footer p {{ color: #9ca3af; font-size: 13px; margin: 4px 0; }}
    .footer a {{ color: #6366f1; text-decoration: none; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>{site_settings.site_name}</h1>
    </div>
    <div class="body">
      <p>Bonjour {subscriber.name or 'vous'},</p>
      {campaign.content}
    </div>
    <div class="footer">
      <p>Vous recevez cet email car vous êtes abonné(e) à <strong>{site_settings.site_name}</strong>.</p>
      <p><a href="{unsubscribe_url}">Se désabonner</a></p>
    </div>
  </div>
</body>
</html>
"""
        try:
            send_mail(
                subject=campaign.subject,
                message=strip_tags(campaign.content),
                from_email=from_email,
                recipient_list=[subscriber.email],
                html_message=html_message,
                fail_silently=True,
            )
            sent_count += 1
        except Exception:
            pass

    campaign.status = 'sent'
    campaign.sent_at = timezone.now()
    campaign.save(update_fields=['status', 'sent_at'])

    return sent_count, f"{sent_count} email(s) envoyé(s) avec succès."
