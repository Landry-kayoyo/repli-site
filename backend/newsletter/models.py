from django.db import models
import uuid


class Subscriber(models.Model):
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('unsubscribed', 'Désabonné'),
    ]
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Abonné'
        verbose_name_plural = 'Abonnés'
        ordering = ['-created_at']

    def __str__(self):
        return self.email


class NewsletterCampaign(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('sent', 'Envoyée'),
    ]
    subject = models.CharField(max_length=300)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Campagne Newsletter'
        verbose_name_plural = 'Campagnes Newsletter'
        ordering = ['-created_at']

    def __str__(self):
        return self.subject
