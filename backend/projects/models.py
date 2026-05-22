from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager


class ProjectCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, default='#4F46E5')

    class Meta:
        verbose_name = 'Catégorie Projet'
        verbose_name_plural = 'Catégories Projets'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Project(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
    ]
    title = models.CharField(max_length=300, verbose_name='Titre')
    subtitle = models.CharField(max_length=400, blank=True, verbose_name='Sous-titre')
    slug = models.SlugField(unique=True, max_length=350)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    category = models.ForeignKey(ProjectCategory, on_delete=models.SET_NULL, null=True, blank=True)
    cover_image = models.ImageField(upload_to='projects/covers/', blank=True, null=True, verbose_name='Image de couverture')
    description = models.TextField(verbose_name='Description courte')
    content = RichTextUploadingField(verbose_name='Contenu / Tutoriel')
    tutorial_steps = RichTextUploadingField(blank=True, verbose_name='Étapes du tutoriel')
    tags = TaggableManager(blank=True)
    technologies = models.CharField(max_length=500, blank=True, verbose_name='Technologies utilisées')
    github_url = models.URLField(blank=True)
    demo_url = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    views_count = models.PositiveIntegerField(default=0)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Projet'
        verbose_name_plural = 'Projets'
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.meta_title:
            self.meta_title = self.title
        if not self.meta_description:
            self.meta_description = self.description[:300] if self.description else ''
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/projets/{self.slug}"
