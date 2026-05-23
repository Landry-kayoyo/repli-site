from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, TextField
from django.utils import timezone
from datetime import timedelta
from .models import SiteSettings, Skill, Experience, Education, PageView
try:
    from ckeditor.widgets import CKEditorWidget
    CKEDITOR_AVAILABLE = True
except ImportError:
    CKEDITOR_AVAILABLE = False


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    formfield_overrides = (
        {TextField: {'widget': CKEditorWidget()}} if CKEDITOR_AVAILABLE else {}
    )
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
        ('Newsletter automatique', {
            'fields': ('newsletter_send_on_publish', 'newsletter_from_name', 'newsletter_intro_text'),
            'description': '⚡ Activez pour envoyer automatiquement un email aux abonnés à chaque nouvelle publication.',
        }),
        ('Page À propos', {
            'fields': ('about_title', 'about_content', 'about_cover')
        }),
        ('SEO & Analytics', {
            'fields': ('meta_keywords', 'google_analytics_id')
        }),
        ('📱 PWA', {
            'fields': ('pwa_theme_color', 'pwa_background_color')
        }),
        ('🤖 Configuration IA', {
            'fields': ('ai_enabled', 'ai_api_key', 'ai_api_base_url', 'ai_model', 'ai_system_prompt'),
            'description': (
                '<div style="background:#eef2ff;border-left:4px solid #4F46E5;border-radius:6px;padding:14px;margin-bottom:10px;">'
                '<b style="color:#4F46E5;">🤖 Guide de configuration de l\'assistant IA</b><br><br>'
                '<b>1.</b> Cochez <em>Activer l\'assistant IA</em><br>'
                '<b>2.</b> Clé API : votre clé ChatAnywhere ou OpenAI<br>'
                '<b>3.</b> URL de base : <code>https://api.chatanywhere.tech/v1</code><br>'
                '<b>4.</b> Modèle : <code>gpt-3.5-turbo</code> ou <code>gpt-4o-mini</code><br>'
                '<b>5.</b> Sauvegardez — le bouton ✨ IA apparaît dans tout l\'admin !'
                '</div>'
            ),
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
    list_display = ['name', 'icon_preview', 'category', 'level', 'order']
    list_editable = ['order', 'level']
    list_filter = ['category']
    search_fields = ['name']

    def icon_preview(self, obj):
        if obj.icon:
            if obj.icon.startswith('bi-'):
                return format_html(
                    '<i class="bi {}" style="font-size:1.3rem;color:#4F46E5;"></i> <small style="color:#6B7280;">{}</small>',
                    obj.icon, obj.icon
                )
            return format_html('<span style="font-size:1.3rem;">{}</span>', obj.icon)
        return '-'
    icon_preview.short_description = 'Icône'


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'start_date', 'end_date', 'is_current', 'order']
    list_editable = ['order']


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['degree', 'institution', 'start_date', 'end_date', 'is_current', 'order']
    list_editable = ['order']


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ['object_title', 'content_type', 'date', 'count', 'view_link']
    list_filter = ['content_type', 'date']
    search_fields = ['object_title', 'object_slug']
    readonly_fields = ['content_type', 'object_id', 'object_title', 'object_slug', 'date', 'count']
    ordering = ['-date', '-count']

    def view_link(self, obj):
        if obj.object_slug and obj.content_type:
            url_map = {
                'article': f'/articles/{obj.object_slug}',
                'project': f'/projets/{obj.object_slug}',
                'tip': f'/astuces/{obj.object_slug}',
                'portfolio': f'/portfolio/{obj.object_slug}',
            }
            url = url_map.get(obj.content_type, '#')
            return format_html('<a href="http://localhost:5000{}" target="_blank">Voir →</a>', url)
        return '-'
    view_link.short_description = 'Lien'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        last_30 = timezone.now().date() - timedelta(days=30)
        last_7 = timezone.now().date() - timedelta(days=7)

        total_30 = PageView.objects.filter(date__gte=last_30).aggregate(t=Sum('count'))['t'] or 0
        total_7 = PageView.objects.filter(date__gte=last_7).aggregate(t=Sum('count'))['t'] or 0
        total_today = PageView.objects.filter(date=timezone.now().date()).aggregate(t=Sum('count'))['t'] or 0

        top_pages = PageView.objects.filter(date__gte=last_30)\
            .values('object_title', 'content_type', 'object_slug')\
            .annotate(total=Sum('count'))\
            .order_by('-total')[:10]

        extra_context['stats_summary'] = {
            'today': total_today,
            'last_7': total_7,
            'last_30': total_30,
            'top_pages': list(top_pages),
        }
        return super().changelist_view(request, extra_context=extra_context)

    def has_add_permission(self, request):
        return False
