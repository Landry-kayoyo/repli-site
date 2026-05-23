from django.db import models


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default='Landry Net')
    tagline = models.CharField(max_length=200, default='Partager, Apprendre, Innover')
    description = models.TextField(default='Site personnel de Landry')
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    logo_text = models.CharField(max_length=100, default='Landry Net')
    favicon = models.ImageField(upload_to='favicons/', blank=True, null=True)
    author_name = models.CharField(max_length=100, default='Landry')
    author_email = models.EmailField(blank=True)
    author_bio = models.TextField(blank=True)
    author_photo = models.ImageField(upload_to='author/', blank=True, null=True)
    author_location = models.CharField(max_length=100, blank=True)
    author_job_title = models.CharField(max_length=100, blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    email_host = models.CharField(max_length=100, default='smtp.gmail.com')
    email_port = models.IntegerField(default=587)
    email_use_tls = models.BooleanField(default=True)
    email_host_user = models.EmailField(blank=True)
    email_host_password = models.CharField(max_length=200, blank=True)
    contact_email = models.EmailField(blank=True, help_text='Email de réception des messages de contact')
    meta_keywords = models.CharField(max_length=500, blank=True)
    google_analytics_id = models.CharField(max_length=50, blank=True)
    about_title = models.CharField(max_length=200, default='À propos de moi')
    about_content = models.TextField(blank=True)
    about_cover = models.ImageField(upload_to='about/', blank=True, null=True)
    cv_file = models.FileField(upload_to='cv/', blank=True, null=True)
    pwa_theme_color = models.CharField(max_length=7, default='#4F46E5')
    pwa_background_color = models.CharField(max_length=7, default='#ffffff')
    primary_color = models.CharField(max_length=7, default='#4F46E5')
    secondary_color = models.CharField(max_length=7, default='#7C3AED')
    newsletter_send_on_publish = models.BooleanField(
        default=False,
        help_text='Envoyer automatiquement la newsletter aux abonnés à chaque nouvelle publication'
    )
    newsletter_intro_text = models.TextField(
        blank=True,
        default='Bonjour ! Voici une nouvelle publication sur le site.',
        help_text='Texte d\'introduction des emails de newsletter'
    )
    newsletter_from_name = models.CharField(
        max_length=100, blank=True, default='Landry Net',
        help_text='Nom d\'expéditeur de la newsletter'
    )
    # ── IA ──────────────────────────────────────────────────────────────
    ai_enabled = models.BooleanField(
        default=False, verbose_name="Activer l'assistant IA"
    )
    ai_api_key = models.CharField(
        max_length=500, blank=True, verbose_name='Clé API IA',
        help_text='Votre clé API (compatible OpenAI). Ex: sk-...'
    )
    ai_api_base_url = models.CharField(
        max_length=300, blank=True,
        default='https://api.chatanywhere.tech/v1',
        verbose_name='URL de base API',
        help_text='URL de base de votre API. ChatAnywhere: https://api.chatanywhere.tech/v1'
    )
    ai_model = models.CharField(
        max_length=100, blank=True, default='gpt-3.5-turbo',
        verbose_name='Modèle IA',
        help_text='Nom du modèle. Ex: gpt-3.5-turbo, gpt-4, gpt-4o-mini'
    )
    ai_system_prompt = models.TextField(
        blank=True,
        verbose_name='Prompt système personnalisé',
        help_text='Laissez vide pour utiliser le prompt par défaut.'
    )
    google_sitemap_url = models.URLField(
        blank=True,
        verbose_name='URL du Sitemap Google',
        help_text='Lien de votre sitemap à soumettre à Google Search Console. Ex: https://votresite.com/sitemap.xml'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Paramètres du site'
        verbose_name_plural = 'Paramètres du site'

    def __str__(self):
        return self.site_name

    def apply_email_settings(self):
        if self.email_host_user:
            from django.conf import settings as dj_settings
            dj_settings.EMAIL_HOST = self.email_host
            dj_settings.EMAIL_PORT = self.email_port
            dj_settings.EMAIL_USE_TLS = self.email_use_tls
            dj_settings.EMAIL_HOST_USER = self.email_host_user
            dj_settings.EMAIL_HOST_PASSWORD = self.email_host_password
            dj_settings.DEFAULT_FROM_EMAIL = self.email_host_user


class Skill(models.Model):
    name = models.CharField(max_length=100)
    level = models.IntegerField(default=80)
    icon = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Compétence'
        verbose_name_plural = 'Compétences'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Experience(models.Model):
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField()
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Expérience'
        verbose_name_plural = 'Expériences'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.title} @ {self.company}"


class Education(models.Model):
    degree = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    location = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Éducation'
        verbose_name_plural = 'Éducation'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.degree} - {self.institution}"


class PageView(models.Model):
    content_type = models.CharField(max_length=50)
    object_id = models.PositiveIntegerField()
    object_title = models.CharField(max_length=300, blank=True)
    object_slug = models.CharField(max_length=350, blank=True)
    date = models.DateField(auto_now_add=True)
    count = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Vue de page'
        verbose_name_plural = 'Vues de pages'
        unique_together = ('content_type', 'object_id', 'date')
        ordering = ['-date', '-count']

    def __str__(self):
        return f"{self.content_type} #{self.object_id} — {self.date}"

    @classmethod
    def record(cls, content_type, object_id, title='', slug=''):
        from django.utils import timezone
        today = timezone.now().date()
        obj, created = cls.objects.get_or_create(
            content_type=content_type,
            object_id=object_id,
            date=today,
            defaults={'object_title': title, 'object_slug': slug, 'count': 1}
        )
        if not created:
            cls.objects.filter(pk=obj.pk).update(count=models.F('count') + 1)
        return obj
