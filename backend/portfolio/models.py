from django.db import models
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager


class PortfolioCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Catégorie Portfolio'
        verbose_name_plural = 'Catégories Portfolio'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class PortfolioItem(models.Model):
    title = models.CharField(max_length=300, verbose_name='Titre')
    subtitle = models.CharField(max_length=400, blank=True, verbose_name='Sous-titre')
    slug = models.SlugField(unique=True, max_length=350)
    category = models.ForeignKey(PortfolioCategory, on_delete=models.SET_NULL, null=True, blank=True)
    cover_image = models.ImageField(upload_to='portfolio/covers/', verbose_name='Image de couverture')
    images = models.ManyToManyField('PortfolioImage', blank=True)
    description = models.TextField(verbose_name='Description')
    content = RichTextUploadingField(blank=True, verbose_name='Contenu détaillé')
    client = models.CharField(max_length=200, blank=True)
    url = models.URLField(blank=True, verbose_name='Lien du projet')
    github_url = models.URLField(blank=True)
    tags = TaggableManager(blank=True)
    is_featured = models.BooleanField(default=False)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Portfolio'
        verbose_name_plural = 'Portfolio'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/portfolio/{self.slug}"


class PortfolioImage(models.Model):
    image = models.ImageField(upload_to='portfolio/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.caption or str(self.id)
