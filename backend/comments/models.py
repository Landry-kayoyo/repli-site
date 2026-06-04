from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Comment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    author_name = models.CharField(max_length=200, verbose_name='Nom')
    author_email = models.EmailField(verbose_name='Email')
    content = models.TextField(verbose_name='Commentaire')
    is_approved = models.BooleanField(default=True)
    is_author_reply = models.BooleanField(default=False, verbose_name="Réponse de l'auteur")
    likes_count = models.PositiveIntegerField(default=0, verbose_name='Likes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Commentaire'
        verbose_name_plural = 'Commentaires'
        ordering = ['created_at']

    def __str__(self):
        return f"Commentaire de {self.author_name}"


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    session_key = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('comment', 'session_key')
        verbose_name = 'Like commentaire'
        verbose_name_plural = 'Likes commentaires'
