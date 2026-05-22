from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactMessage
from .serializers import ContactMessageSerializer


class ContactMessageCreateView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ContactMessageSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ip = request.META.get('REMOTE_ADDR')
        message_obj = ContactMessage.objects.create(
            name=serializer.validated_data['name'],
            email=serializer.validated_data['email'],
            subject=serializer.validated_data['subject'],
            message=serializer.validated_data['message'],
            ip_address=ip
        )
        try:
            from core.models import SiteSettings
            site = SiteSettings.objects.filter(pk=1).first()
            if site:
                site.apply_email_settings()
            recipient = site.contact_email if site and site.contact_email else settings.DEFAULT_FROM_EMAIL
            if recipient:
                send_mail(
                    subject=f"[Landry Net] Nouveau message: {message_obj.subject}",
                    message=f"De: {message_obj.name} ({message_obj.email})\n\n{message_obj.message}",
                    from_email=settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
                    recipient_list=[recipient],
                    fail_silently=True,
                )
        except Exception:
            pass
        return Response({'success': True, 'message': 'Message envoyé avec succès!'}, status=status.HTTP_201_CREATED)
