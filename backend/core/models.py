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
