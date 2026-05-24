from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.mail import EmailMultiAlternatives, get_connection
from django.conf import settings
from .models import ContactMessage
from .serializers import ContactMessageSerializer
import threading
import logging

logger = logging.getLogger(__name__)


def _base_styles():
    return """
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif; background:#f0f2ff; margin:0; padding:0; }
.wrapper { width:100%; background:#f0f2ff; padding:40px 16px; }
.container { max-width:600px; margin:0 auto; background:#fff; border-radius:20px; overflow:hidden; box-shadow:0 8px 40px rgba(79,70,229,0.12); }
.header { background:linear-gradient(135deg,#4338ca 0%,#6d28d9 100%); padding:40px 40px 32px; text-align:center; }
.logo-circle { display:inline-flex; align-items:center; justify-content:center; width:52px; height:52px; background:rgba(255,255,255,0.18); border-radius:14px; margin-bottom:14px; font-weight:900; font-size:18px; color:#fff; }
.site-name { color:#fff; font-size:24px; font-weight:800; letter-spacing:-0.3px; margin-bottom:4px; }
.header-badge { display:inline-block; background:rgba(255,255,255,0.2); color:#fff; padding:5px 16px; border-radius:50px; font-size:12px; font-weight:700; letter-spacing:0.5px; text-transform:uppercase; margin-top:12px; }
.body { padding:36px 40px 28px; }
.section-title { font-size:20px; font-weight:800; color:#1e1b4b; margin-bottom:6px; }
.section-body { font-size:15px; color:#6b7280; line-height:1.65; margin-bottom:24px; }
.field-row { margin-bottom:16px; }
.field-label { font-size:11px; font-weight:700; color:#9ca3af; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px; }
.field-value { font-size:15px; color:#1e1b4b; font-weight:500; }
.message-box { background:#f8f7ff; border-left:3px solid #4F46E5; border-radius:0 10px 10px 0; padding:18px; font-size:15px; color:#374151; line-height:1.7; white-space:pre-wrap; margin-top:8px; }
.info-card { background:#f0f2ff; border:1px solid #e0e7ff; border-radius:12px; padding:20px 24px; margin:20px 0; }
.info-card .row { display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-bottom:1px solid #e5e7eb; font-size:14px; }
.info-card .row:last-child { border-bottom:none; }
.info-card .label { color:#9ca3af; }
.info-card .value { color:#1e1b4b; font-weight:600; }
.btn { display:inline-block; background:linear-gradient(135deg,#4F46E5,#7C3AED); color:#fff !important; padding:13px 28px; border-radius:10px; text-decoration:none !important; font-weight:700; font-size:14px; margin-top:8px; }
.btn-outline { display:inline-block; border:2px solid #4F46E5; color:#4F46E5 !important; padding:11px 24px; border-radius:10px; text-decoration:none !important; font-weight:700; font-size:14px; }
.check-green { display:inline-flex; align-items:center; justify-content:center; width:60px; height:60px; border-radius:50%; background:linear-gradient(135deg,#10b981,#059669); margin:0 auto 18px; }
.divider { border:none; border-top:1px solid #e5e7eb; margin:24px 0; }
.footer { background:#1e1b4b; padding:24px 40px; text-align:center; }
.footer p { color:rgba(255,255,255,0.5); font-size:13px; line-height:1.6; margin:3px 0; }
.footer a { color:#a5b4fc; text-decoration:none; }
@media(max-width:600px) { .wrapper{padding:12px 8px;} .header,.body,.footer{padding:28px 24px;} .info-card .row{flex-direction:column;align-items:flex-start;gap:2px;} }
"""


def _wrap(content, footer_html=''):
    styles = _base_styles()
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <style>{styles}</style>
</head>
<body>
  <div class="wrapper">
    <div class="container">
      {content}
      <div class="footer">{footer_html}</div>
    </div>
  </div>
</body>
</html>"""


def _build_smtp_connection(s):
    """Build an explicit SMTP connection from SiteSettings (thread-safe)."""
    return get_connection(
        backend='django.core.mail.backends.smtp.EmailBackend',
        host=s.email_host or 'smtp.gmail.com',
        port=int(s.email_port or 587),
        username=s.email_host_user,
        password=s.email_host_password,
        use_tls=bool(s.email_use_tls),
        fail_silently=False,
    )


def _send_emails(message_obj):
    try:
        from core.models import SiteSettings
        s = SiteSettings.objects.filter(pk=1).first()
        if not s or not s.email_host_user or not s.email_host_password:
            logger.warning('Contact email not sent: SMTP not configured in Site Settings.')
            return

        conn = _build_smtp_connection(s)

        site_name = s.site_name or 'Landry Net'
        frontend_url = settings.FRONTEND_URL or 'http://localhost:5000'
        from_email = f"{site_name} <{s.email_host_user}>"
        ticket = f"MSG-{message_obj.pk:04d}"
        import datetime
        sent_at = datetime.datetime.now().strftime('%d/%m/%Y à %H:%M')

        # ── 1. Admin notification ──────────────────────────────────
        admin_recipient = s.contact_email or s.email_host_user
        if admin_recipient:
            reply_link = f"mailto:{message_obj.email}?subject=Re: {message_obj.subject}&body=Bonjour {message_obj.name},%0A%0A"

            admin_body = f"""
      <div class="header">
        <div class="logo-circle">LN</div>
        <div class="site-name">{site_name}</div>
        <div class="header-badge">📬 Nouveau message de contact</div>
      </div>
      <div class="body">
        <p class="section-title">Nouveau message reçu</p>
        <p class="section-body">Un visiteur vous a envoyé un message via le formulaire de contact.</p>

        <div class="info-card">
          <div class="row"><span class="label">🔖 Référence</span><span class="value">{ticket}</span></div>
          <div class="row"><span class="label">👤 Expéditeur</span><span class="value">{message_obj.name}</span></div>
          <div class="row"><span class="label">📧 Email</span><span class="value">{message_obj.email}</span></div>
          <div class="row"><span class="label">📅 Date</span><span class="value">{sent_at}</span></div>
          <div class="row"><span class="label">🌐 IP</span><span class="value">{message_obj.ip_address or 'Inconnue'}</span></div>
        </div>

        <div class="field-row">
          <div class="field-label">Sujet</div>
          <div class="field-value" style="font-size:17px;font-weight:700;color:#1e1b4b;">{message_obj.subject}</div>
        </div>
        <div class="field-row">
          <div class="field-label">Message</div>
          <div class="message-box">{message_obj.message}</div>
        </div>

        <div style="margin-top:24px;display:flex;gap:12px;flex-wrap:wrap;">
          <a href="{reply_link}" class="btn">↩ Répondre à {message_obj.name}</a>
          <a href="{frontend_url}/admin/contact/contactmessage/{message_obj.pk}/change/" class="btn-outline">Voir dans l'admin</a>
        </div>
      </div>"""

            admin_footer = f"""<p>Message reçu via le formulaire de contact de <strong style="color:#c7d2fe;">{site_name}</strong></p>
      <p><a href="{frontend_url}/admin/">{frontend_url}/admin/</a></p>"""

            admin_html = _wrap(admin_body, admin_footer)
            admin_plain = f"Nouveau message de contact [{ticket}]\n\nDe: {message_obj.name} ({message_obj.email})\nSujet: {message_obj.subject}\nDate: {sent_at}\n\n{message_obj.message}\n\nRépondre: {reply_link}"

            try:
                msg = EmailMultiAlternatives(
                    f"[{site_name}] {ticket} — {message_obj.subject}",
                    admin_plain, from_email, [admin_recipient],
                    reply_to=[message_obj.email],
                    connection=conn,
                )
                msg.attach_alternative(admin_html, "text/html")
                msg.send()
                logger.info(f"Contact admin email sent to {admin_recipient}")
            except Exception as e:
                logger.error(f"Failed to send admin contact email: {e}")

        # ── 2. Confirmation to sender ──────────────────────────────
        confirm_body = f"""
      <div class="header">
        <div class="logo-circle">LN</div>
        <div class="site-name">{site_name}</div>
        <div class="header-badge">✅ Message bien reçu</div>
      </div>
      <div class="body">
        <div style="text-align:center;margin-bottom:24px;">
          <div class="check-green">
            <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
          </div>
          <p class="section-title">Merci {message_obj.name} !</p>
          <p class="section-body">Votre message a bien été reçu. Je vous répondrai dans les meilleurs délais, généralement <strong>sous 24–48h</strong>.</p>
        </div>

        <div class="info-card">
          <div class="row"><span class="label">🔖 Référence</span><span class="value">{ticket}</span></div>
          <div class="row"><span class="label">📅 Reçu le</span><span class="value">{sent_at}</span></div>
          <div class="row"><span class="label">⏱ Délai de réponse</span><span class="value">24 – 48 heures</span></div>
        </div>

        <div class="field-row">
          <div class="field-label">Votre sujet</div>
          <div class="field-value" style="font-size:16px;font-weight:700;">{message_obj.subject}</div>
        </div>
        <div class="field-row">
          <div class="field-label">Votre message</div>
          <div class="message-box">{message_obj.message}</div>
        </div>

        <hr class="divider">
        <p style="font-size:14px;color:#9ca3af;text-align:center;">
          En attendant, explorez les dernières publications sur le site 👇
        </p>
        <div style="text-align:center;margin-top:16px;">
          <a href="{frontend_url}" class="btn">Visiter {site_name} →</a>
        </div>
      </div>"""

        confirm_footer = f"""<p>Vous avez contacté <strong style="color:#c7d2fe;">{site_name}</strong> depuis {message_obj.email}</p>
      <p>Cet email est automatique, merci de ne pas y répondre directement.</p>"""

        confirm_html = _wrap(confirm_body, confirm_footer)
        confirm_plain = f"Merci {message_obj.name} !\n\nVotre message [{ticket}] a bien été reçu.\nRéponse attendue : 24–48h\n\nVotre message :\n{message_obj.message}\n\nVisitez le site : {frontend_url}"

        try:
            conn2 = _build_smtp_connection(s)
            msg = EmailMultiAlternatives(
                f"✅ Message reçu [{ticket}] — {site_name}",
                confirm_plain, from_email, [message_obj.email],
                connection=conn2,
            )
            msg.attach_alternative(confirm_html, "text/html")
            msg.send()
            logger.info(f"Confirmation email sent to {message_obj.email}")
        except Exception as e:
            logger.error(f"Failed to send confirmation email: {e}")

    except Exception as e:
        logger.error(f"_send_emails unexpected error: {e}")


class ContactMessageCreateView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ContactMessageSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
        if ',' in ip:
            ip = ip.split(',')[0].strip()

        message_obj = ContactMessage.objects.create(
            name=serializer.validated_data['name'],
            email=serializer.validated_data['email'],
            subject=serializer.validated_data['subject'],
            message=serializer.validated_data['message'],
            ip_address=ip
        )

        threading.Thread(target=_send_emails, args=(message_obj,), daemon=True).start()

        return Response({'success': True, 'message': 'Message envoyé avec succès ! Vous recevrez une confirmation par email.'}, status=status.HTTP_201_CREATED)
