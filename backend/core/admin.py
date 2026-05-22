from django.contrib import admin
from django.utils.html import format_html
from .models import SiteSettings, Skill, Experience, Education


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Identité du site', {
            'fields': ('site_name', 'tagline', 'description', 'logo', 'logo_text', 'favicon', 'primary_color', 'secondary_color')
        }),
        ('Auteur', {
            'fields': ('author_name', 'author_email', 'author_bio', 'author_photo', 'author_location', 'author_job_title', 'cv_file')
        }),
        ('Réseaux sociaux', {
            'fields': ('github_url', 'linkedin_url', 'twitter_url', 'youtube_url', 'facebook_url', 'instagram_url')
        }),
        ('Configuration Email Gmail', {
            'fields': ('email_host', 'email_port', 'email_use_tls', 'email_host_user', 'email_host_password', 'contact_email'),
            'description': 'Pour Gmail: host=smtp.gmail.com, port=587, TLS=Oui. Utilisez un mot de passe d\'application Google.',
        }),
        ('Page À propos', {
            'fields': ('about_title', 'about_content', 'about_cover')
        }),
        ('SEO & Analytics', {
            'fields': ('meta_keywords', 'google_analytics_id')
        }),
        ('PWA', {
            'fields': ('pwa_theme_color', 'pwa_background_color')
        }),
    )

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" height="50"/>', obj.logo.url)
        return '-'
    logo_preview.short_description = 'Aperçu logo'

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'level', 'order']
    list_editable = ['order', 'level']
    list_filter = ['category']
    search_fields = ['name']


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'start_date', 'end_date', 'is_current', 'order']
    list_editable = ['order']


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['degree', 'institution', 'start_date', 'end_date', 'is_current', 'order']
    list_editable = ['order']
