from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Project


@receiver(pre_save, sender=Project)
def project_on_publish(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = Project.objects.get(pk=instance.pk)
    except Project.DoesNotExist:
        return

    if old.status != 'published' and instance.status == 'published':
        from django.conf import settings
        url = f"{settings.FRONTEND_URL}/projets/{instance.slug}"
        try:
            from newsletter.utils import send_newsletter_notification
            send_newsletter_notification(
                title=instance.title,
                excerpt=instance.description or '',
                url=url,
                content_type_label='Projet',
                author_name=instance.author.get_full_name() or instance.author.username,
            )
        except Exception:
            pass
