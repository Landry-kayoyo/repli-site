from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, TextField
from django.utils import timezone
from datetime import timedelta
from .models import SiteSettings, Skill, Experience, Education, PageView, Technology, AIConfig
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


_ICON_SEARCH_JS = """
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
<style>
#bi-search-wrap{margin-top:8px;padding:14px;background:#f8f7ff;border-radius:10px;border:1px solid #e0e7ff;}
#bi-search-input{width:100%;padding:8px 12px;border-radius:8px;border:1.5px solid #c7d2fe;font-size:14px;outline:none;font-family:inherit;}
#bi-search-input:focus{border-color:#4F46E5;}
#bi-search-results{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px;max-height:220px;overflow-y:auto;}
.bi-search-item{display:inline-flex;flex-direction:column;align-items:center;gap:4px;padding:8px 10px;border-radius:8px;border:1.5px solid #e0e7ff;cursor:pointer;transition:all 0.15s;background:#fff;min-width:64px;}
.bi-search-item:hover{border-color:#4F46E5;background:#eef2ff;}
.bi-search-item i{font-size:1.4rem;color:#4F46E5;}
.bi-search-item span{font-size:10px;color:#6b7280;max-width:70px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
#bi-current-preview{display:flex;align-items:center;gap:8px;margin-top:8px;font-size:13px;color:#4b5563;}
#bi-current-preview i{font-size:1.6rem;}
</style>
<div id="bi-search-wrap">
  <b style="font-size:13px;color:#4F46E5;">🔍 Recherche Bootstrap Icons</b>
  <div style="font-size:12px;color:#6b7280;margin:4px 0 8px;">Tapez pour chercher une icône (ex: code, database, python, react…)</div>
  <input id="bi-search-input" type="text" placeholder="Rechercher une icône Bootstrap Icons…">
  <div id="bi-current-preview"></div>
  <div id="bi-search-results"></div>
</div>
<script>
(function(){
  var ICONS=['bi-code-slash','bi-code-square','bi-code','bi-code-dot','bi-filetype-py','bi-filetype-js','bi-filetype-tsx','bi-filetype-ts','bi-filetype-html','bi-filetype-css','bi-filetype-json','bi-filetype-php','bi-filetype-java','bi-filetype-cs','bi-filetype-rb','bi-filetype-sql','bi-filetype-xml','bi-filetype-go','bi-filetype-sh','bi-filetype-yml','bi-database','bi-database-fill','bi-database-check','bi-server','bi-hdd-network','bi-hdd-rack','bi-cloud','bi-cloud-fill','bi-cloud-upload','bi-cloud-download','bi-git','bi-github','bi-gitlab','bi-terminal','bi-terminal-fill','bi-laptop','bi-pc-display','bi-phone','bi-tablet','bi-cpu','bi-memory','bi-gpu-card','bi-wifi','bi-lock','bi-shield','bi-shield-check','bi-key','bi-gear','bi-gear-fill','bi-tools','bi-wrench','bi-box','bi-boxes','bi-layers','bi-stack','bi-diagram-3','bi-diagram-2','bi-flow','bi-grid','bi-table','bi-list','bi-kanban','bi-graph-up','bi-bar-chart','bi-pie-chart','bi-activity','bi-lightning','bi-lightning-fill','bi-fire','bi-rocket','bi-rocket-fill','bi-star','bi-star-fill','bi-heart','bi-bookmark','bi-tag','bi-tags','bi-chat','bi-envelope','bi-globe','bi-globe2','bi-link','bi-link-45deg','bi-search','bi-eye','bi-pencil','bi-trash','bi-plus','bi-dash','bi-x','bi-check','bi-arrow-right','bi-arrow-up','bi-download','bi-upload','bi-share','bi-person','bi-people','bi-building','bi-briefcase','bi-journal','bi-book','bi-newspaper','bi-camera','bi-image','bi-music-note','bi-play','bi-video','bi-mic','bi-headphones','bi-currency-bitcoin','bi-currency-euro','bi-currency-dollar','bi-paypal','bi-stripe','bi-android2','bi-apple','bi-windows','bi-linux','bi-ubuntu','bi-discord','bi-slack','bi-twitter','bi-linkedin','bi-facebook','bi-instagram','bi-youtube','bi-twitch','bi-whatsapp','bi-telegram','bi-pinterest','bi-reddit','bi-wordpress','bi-shopify','bi-google','bi-microsoft','bi-amazon','bi-docker','bi-kubernetes','bi-nginx','bi-apache'];
  var input=document.getElementById('bi-search-input');
  var results=document.getElementById('bi-search-results');
  var preview=document.getElementById('bi-current-preview');
  var iconField=document.getElementById('id_icon');
  function updatePreview(){
    var val=iconField?iconField.value.trim():'';
    if(val.startsWith('bi-')){
      preview.innerHTML='<span>Aperçu actuel :</span><i class="bi '+val+'"></i><code style="font-size:12px;background:#eef2ff;padding:2px 8px;border-radius:4px;">'+val+'</code>';
    } else if(val){
      preview.innerHTML='<span>Aperçu actuel :</span><span style="font-size:1.6rem;">'+val+'</span>';
    } else {
      preview.innerHTML='';
    }
  }
  if(iconField){iconField.addEventListener('input',updatePreview);updatePreview();}
  function render(list){
    if(!list.length){results.innerHTML='<span style="font-size:12px;color:#9ca3af;">Aucun résultat. Essayez: code, database, cloud, git, server…</span>';return;}
    results.innerHTML=list.slice(0,60).map(function(ic){
      return '<div class="bi-search-item" onclick="document.getElementById(\'id_icon\').value=\''+ic+'\';document.getElementById(\'bi-search-input\').value=\'\';document.getElementById(\'bi-search-results\').innerHTML=\'\';(function(){var v=\''+ic+'\';var p=document.getElementById(\'bi-current-preview\');p.innerHTML=\'<span>Aperçu actuel :</span><i class="bi \'+v+\'"></i><code style="font-size:12px;background:#eef2ff;padding:2px 8px;border-radius:4px;">\'+v+\'</code>\';})();"><i class="bi '+ic+'"></i><span>'+ic.replace('bi-','')+'</span></div>';
    }).join('');
  }
  input.addEventListener('input',function(){
    var q=this.value.toLowerCase().trim();
    if(!q){results.innerHTML='';return;}
    var matches=ICONS.filter(function(ic){return ic.indexOf(q)>=0;});
    render(matches);
  });
})();
</script>
"""


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ['icon_preview', 'name', 'color_swatch', 'order']
    list_editable = ['order']
    search_fields = ['name']
    readonly_fields = ['icon_preview_large', 'icon_search_box']
    fields = ['name', 'icon', 'icon_search_box', 'icon_preview_large', 'color', 'url', 'order']

    def icon_preview(self, obj):
        if obj.icon:
            if obj.icon.startswith('bi-'):
                return format_html(
                    '<i class="bi {}" style="font-size:1.5rem;color:{};"></i>',
                    obj.icon, obj.color or '#4F46E5'
                )
            return format_html('<span style="font-size:1.5rem;">{}</span>', obj.icon)
        return format_html('<span style="color:#9ca3af;">—</span>')
    icon_preview.short_description = 'Icône'

    def icon_preview_large(self, obj):
        if obj.icon:
            if obj.icon.startswith('bi-'):
                return format_html(
                    '<i class="bi {}" style="font-size:2.5rem;color:{};"></i>',
                    obj.icon, obj.color or '#4F46E5'
                )
            return format_html('<span style="font-size:2.5rem;">{}</span>', obj.icon)
        return format_html('<span style="color:#9ca3af;">Aucune icône définie</span>')
    icon_preview_large.short_description = 'Aperçu icône actuelle'

    def color_swatch(self, obj):
        return format_html(
            '<span style="display:inline-block;width:20px;height:20px;border-radius:5px;background:{};border:1px solid #e5e7eb;vertical-align:middle;"></span> {}',
            obj.color, obj.color
        )
    color_swatch.short_description = 'Couleur'

    def icon_search_box(self, obj):
        return format_html('{}', _ICON_SEARCH_JS)
    icon_search_box.short_description = 'Recherche d\'icône'
    icon_search_box.allow_tags = True

    class Media:
        css = {'all': ['https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css']}


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


@admin.register(AIConfig)
class AIConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'model', 'api_base_url_short', 'is_active', 'updated_at')
    list_display_links = ('name',)
    list_editable = ('is_active',)
    list_filter = ('is_active', 'model')
    search_fields = ('name', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-is_active', '-updated_at')

    fieldsets = (
        ('Identification', {
            'fields': ('name', 'is_active', 'notes'),
            'description': (
                '<div style="background:#eef2ff;border-left:4px solid #4F46E5;border-radius:6px;padding:14px;margin-bottom:10px;">'
                '<b style="color:#4F46E5;">🔑 Gestion multi-API IA</b><br><br>'
                'Créez plusieurs configurations (ChatAnywhere, OpenAI, etc.) '
                'et activez celle que vous voulez utiliser. '
                '<b>Une seule configuration peut être active à la fois.</b>'
                '</div>'
            ),
        }),
        ('Paramètres API', {
            'fields': ('api_key', 'api_base_url', 'model'),
        }),
        ('Informations', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def api_base_url_short(self, obj):
        url = obj.api_base_url or ''
        return url.replace('https://', '').replace('http://', '')[:40]
    api_base_url_short.short_description = 'URL de base'
