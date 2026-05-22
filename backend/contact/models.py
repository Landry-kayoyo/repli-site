from django.db import models


class ContactMessage(models.Model):
    STATUS_CHOICES = [
        ('new', 'Nouveau'),
        ('read', 'Lu'),
        ('replied', 'Répondu'),
        ('archived', 'Archivé'),
    ]
    name = models.CharField(max_length=200, verbose_name='Nom')
    email = models.EmailField(verbose_name='Email')
    subject = models.CharField(max_length=300, verbose_name='Sujet')
    message = models.TextField(verbose_name='Message')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Message de contact'
        verbose_name_plural = 'Messages de contact'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"
