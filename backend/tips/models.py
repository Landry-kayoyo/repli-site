from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager


class TipCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, default='#059669')

    class Meta:
        verbose_name = 'Catégorie Astuce'
        verbose_name_plural = 'Catégories Astuces'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tip(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
    ]
    DIFFICULTY_CHOICES = [
        ('beginner', 'Débutant'),
        ('intermediate', 'Intermédiaire'),
        ('advanced', 'Avancé'),
    ]
    title = models.CharField(max_length=300, verbose_name='Titre')
    subtitle = models.CharField(max_length=400, blank=True, verbose_name='Sous-titre')
    slug = models.SlugField(unique=True, max_length=350)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tips')
    category = models.ForeignKey(TipCategory, on_delete=models.SET_NULL, null=True, blank=True)
    cover_image = models.ImageField(upload_to='tips/covers/', blank=True, null=True, verbose_name='Image de couverture')
    excerpt = models.TextField(blank=True, verbose_name='Description courte')
    content = RichTextUploadingField(verbose_name='Contenu')
    tags = TaggableManager(blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    views_count = models.PositiveIntegerField(default=0)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Astuce'
        verbose_name_plural = 'Astuces'
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/astuces/{self.slug}"
