from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Reaction(models.Model):
    REACTION_CHOICES = [
        ('like', '👍 J\'aime'),
        ('love', '❤️ J\'adore'),
        ('wow', '😮 Wow'),
        ('clap', '👏 Bravo'),
        ('fire', '🔥 Incroyable'),
        ('bookmark', '🔖 Sauvegarder'),
    ]
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    reaction_type = models.CharField(max_length=20, choices=REACTION_CHOICES)
    session_key = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Réaction'
        verbose_name_plural = 'Réactions'
        unique_together = ('content_type', 'object_id', 'reaction_type', 'session_key')

    def __str__(self):
        return f"{self.reaction_type} on {self.content_object}"
