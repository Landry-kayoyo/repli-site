from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Article


@receiver(pre_save, sender=Article)
def article_on_publish(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = Article.objects.get(pk=instance.pk)
    except Article.DoesNotExist:
        return

    if old.status != 'published' and instance.status == 'published':
        from django.conf import settings
        url = f"{settings.FRONTEND_URL}/articles/{instance.slug}"
        try:
            from newsletter.utils import send_newsletter_notification
            send_newsletter_notification(
                title=instance.title,
                excerpt=instance.excerpt or '',
                url=url,
                content_type_label='Article',
                author_name=instance.author.get_full_name() or instance.author.username,
            )
        except Exception:
            pass
