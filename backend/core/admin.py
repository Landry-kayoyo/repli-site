from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.conf import settings as django_settings
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
.bi-wrap{margin-top:8px;padding:16px;background:#f8f7ff;border-radius:12px;border:1px solid #e0e7ff;}
.bi-inp{width:100%;padding:9px 14px;border-radius:8px;border:1.5px solid #c7d2fe;font-size:14px;outline:none;font-family:inherit;box-sizing:border-box;}
.bi-inp:focus{border-color:#4F46E5;box-shadow:0 0 0 3px rgba(79,70,229,.1);}
.bi-catbar{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 0;}
.bi-cbtn{display:inline-flex;align-items:center;gap:4px;padding:4px 12px;border-radius:20px;border:1.5px solid #e0e7ff;background:#fff;cursor:pointer;font-size:12px;font-weight:600;color:#6b7280;transition:all .15s;white-space:nowrap;user-select:none;}
.bi-cbtn:hover{border-color:#4F46E5;color:#4F46E5;background:#eef2ff;}
.bi-cbtn.on{border-color:#4F46E5;background:#4F46E5;color:#fff;}
.bi-grid{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px;max-height:240px;overflow-y:auto;padding-right:2px;}
.bi-grid::-webkit-scrollbar{width:4px;}
.bi-grid::-webkit-scrollbar-track{background:#f0f2ff;border-radius:4px;}
.bi-grid::-webkit-scrollbar-thumb{background:#c7d2fe;border-radius:4px;}
.bi-item{display:inline-flex;flex-direction:column;align-items:center;gap:4px;padding:8px 10px;border-radius:8px;border:1.5px solid #e0e7ff;cursor:pointer;transition:all .15s;background:#fff;min-width:68px;max-width:80px;}
.bi-item:hover{border-color:#4F46E5;background:#eef2ff;transform:translateY(-1px);}
.bi-item i{font-size:1.5rem;color:#4F46E5;}
.bi-item span{font-size:10px;color:#6b7280;max-width:72px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;text-align:center;}
.bi-prev{display:none;align-items:center;gap:10px;margin-top:10px;padding:8px 12px;background:#eef2ff;border-radius:8px;font-size:13px;color:#4b5563;}
.bi-prev i{font-size:1.8rem;color:#4F46E5;}
.bi-cnt{font-size:11px;color:#9ca3af;margin-top:6px;}
</style>
<div class="bi-wrap" id="biwrap_{uid}">
  <b style="font-size:13px;color:#4F46E5;">&#128269; Recherche Bootstrap Icons</b>
  <div style="font-size:12px;color:#6b7280;margin:4px 0 8px;">Tapez un mot-cl&#233; ou s&#233;lectionnez une cat&#233;gorie</div>
  <input class="bi-inp" type="text" placeholder="Ex: code, database, cloud, person&#8230;" id="biinp_{uid}">
  <div class="bi-catbar" id="bicats_{uid}"></div>
  <div class="bi-prev" id="biprev_{uid}"></div>
  <div class="bi-cnt" id="bicnt_{uid}"></div>
  <div class="bi-grid" id="bigrid_{uid}"></div>
</div>
<script>
(function(){
  var UID='{uid}';
  var CATS={
    'Code':['bi-code-slash','bi-code-square','bi-code','bi-code-dot','bi-filetype-py','bi-filetype-js','bi-filetype-tsx','bi-filetype-ts','bi-filetype-html','bi-filetype-css','bi-filetype-json','bi-filetype-php','bi-filetype-java','bi-filetype-cs','bi-filetype-rb','bi-filetype-sql','bi-filetype-xml','bi-filetype-go','bi-filetype-sh','bi-filetype-yml','bi-terminal','bi-terminal-fill','bi-git','bi-github','bi-gitlab','bi-journal-code','bi-file-earmark-code','bi-braces','bi-braces-asterisk','bi-bug','bi-bug-fill','bi-textarea','bi-input-cursor','bi-hash'],
    'Cloud':['bi-database','bi-database-fill','bi-database-check','bi-database-add','bi-server','bi-hdd-network','bi-hdd-rack','bi-cloud','bi-cloud-fill','bi-cloud-upload','bi-cloud-download','bi-cloud-check','bi-cloud-arrow-up','bi-diagram-3','bi-diagram-2','bi-flow','bi-graph-up','bi-graph-down','bi-bar-chart','bi-bar-chart-fill','bi-pie-chart','bi-pie-chart-fill','bi-activity','bi-layers','bi-stack','bi-boxes','bi-box'],
    'UI':['bi-search','bi-eye','bi-eye-fill','bi-eye-slash','bi-pencil','bi-pencil-fill','bi-pencil-square','bi-trash','bi-trash-fill','bi-trash3','bi-plus','bi-plus-circle','bi-plus-circle-fill','bi-dash','bi-x','bi-x-circle','bi-check','bi-check-circle','bi-check-circle-fill','bi-check2','bi-arrow-right','bi-arrow-left','bi-arrow-up','bi-arrow-down','bi-arrow-right-circle','bi-arrows-expand','bi-chevron-right','bi-chevron-left','bi-download','bi-upload','bi-share','bi-share-fill','bi-filter','bi-funnel','bi-sort-down','bi-sort-up','bi-sliders','bi-gear','bi-gear-fill','bi-gear-wide','bi-grid','bi-grid-fill','bi-list','bi-list-ul','bi-list-check','bi-table','bi-kanban','bi-kanban-fill','bi-layout-sidebar','bi-columns','bi-zoom-in','bi-zoom-out','bi-fullscreen','bi-bell','bi-bell-fill','bi-toggle-on','bi-toggle-off','bi-send','bi-send-fill','bi-bookmark','bi-bookmark-fill','bi-tag','bi-tag-fill','bi-tags','bi-flag','bi-flag-fill','bi-star','bi-star-fill','bi-heart','bi-heart-fill','bi-link','bi-link-45deg','bi-globe','bi-globe2','bi-clipboard','bi-clipboard-fill','bi-clipboard-check','bi-qr-code','bi-display','bi-printer'],
    'Medias':['bi-camera','bi-camera-fill','bi-camera-video','bi-image','bi-image-fill','bi-images','bi-music-note','bi-music-note-beamed','bi-play','bi-play-fill','bi-play-circle','bi-pause','bi-stop','bi-video','bi-video-fill','bi-mic','bi-mic-fill','bi-headphones','bi-speaker','bi-volume-up','bi-file-earmark-pdf','bi-file-earmark-zip','bi-file-earmark-text','bi-file-earmark'],
    'Personnes':['bi-person','bi-person-fill','bi-person-circle','bi-people','bi-people-fill','bi-person-badge','bi-person-check','bi-person-plus','bi-person-x','bi-building','bi-building-fill','bi-briefcase','bi-briefcase-fill','bi-house','bi-house-fill','bi-geo-alt','bi-geo-alt-fill','bi-map','bi-map-fill','bi-award','bi-award-fill','bi-trophy','bi-trophy-fill'],
    'Finance':['bi-currency-bitcoin','bi-currency-ethereum','bi-currency-euro','bi-currency-dollar','bi-currency-pound','bi-credit-card','bi-credit-card-fill','bi-wallet','bi-wallet-fill','bi-cash','bi-cash-coin','bi-cart','bi-cart-fill','bi-bag','bi-bag-fill','bi-shop','bi-truck','bi-box-seam'],
    'Reseaux':['bi-discord','bi-slack','bi-twitter','bi-twitter-x','bi-linkedin','bi-facebook','bi-instagram','bi-youtube','bi-twitch','bi-whatsapp','bi-telegram','bi-pinterest','bi-reddit','bi-tiktok','bi-wordpress','bi-google','bi-github','bi-gitlab','bi-stack-overflow'],
    'Systeme':['bi-cpu','bi-cpu-fill','bi-memory','bi-gpu-card','bi-laptop','bi-pc-display','bi-phone','bi-tablet','bi-wifi','bi-wifi-off','bi-bluetooth','bi-lock','bi-lock-fill','bi-unlock','bi-shield','bi-shield-check','bi-shield-fill','bi-key','bi-key-fill','bi-tools','bi-wrench','bi-wrench-adjustable','bi-android2','bi-apple','bi-windows','bi-linux','bi-ubuntu','bi-robot','bi-magic','bi-moon','bi-sun','bi-brightness-high','bi-clock','bi-clock-fill','bi-calendar','bi-calendar-fill','bi-calendar-check','bi-alarm','bi-hourglass','bi-info-circle','bi-question-circle','bi-exclamation-triangle','bi-exclamation-circle','bi-lightning','bi-lightning-fill','bi-fire','bi-rocket','bi-rocket-fill']
  };
  var LABELS={'Code':'&#128187; Code','Cloud':'&#9729; Cloud & Data','UI':'&#128433; UI','Medias':'&#127916; Medias','Personnes':'&#128100; Personnes','Finance':'&#128176; Finance','Reseaux':'&#128241; Reseaux','Systeme':'&#9881; Systeme'};
  var ALL=[];var seen={};
  Object.values(CATS).forEach(function(arr){arr.forEach(function(ic){if(!seen[ic]){seen[ic]=1;ALL.push(ic);}});});
  var activeCat='';

  function g(id){return document.getElementById(id+'_'+UID);}

  function iconField(){
    return document.querySelector('#biwrap_'+UID).closest('form').querySelector('#id_icon')||document.getElementById('id_icon');
  }

  function updatePreview(){
    try{var f=iconField();var val=f?f.value.trim():'';var p=g('biprev');
    if(val&&val.startsWith('bi-')){p.style.display='flex';p.innerHTML='<i class="bi '+val+'"></i><div><small style="color:#9ca3af">selectionnee</small><br><code style="color:#4F46E5;font-weight:700">'+val+'</code></div>';}
    else if(val){p.style.display='flex';p.innerHTML='<span style="font-size:1.8rem">'+val+'</span><code style="color:#4F46E5;font-weight:700;margin-left:8px">'+val+'</code>';}
    else{p.style.display='none';p.innerHTML='';}}catch(e){}
  }

  function render(list){
    var grid=g('bigrid');var cnt=g('bicnt');
    if(!list||!list.length){grid.innerHTML='<span style="font-size:12px;color:#9ca3af;padding:8px">Aucun resultat.</span>';cnt.innerHTML='';return;}
    var shown=list.slice(0,80);
    cnt.innerHTML=shown.length+(list.length>80?'/'+list.length:'')+' icone'+(shown.length>1?'s':'');
    grid.innerHTML='';
    shown.forEach(function(ic){
      var d=document.createElement('div');d.className='bi-item';d.title=ic;
      d.innerHTML='<i class="bi '+ic+'"></i><span>'+ic.replace(/^bi-/,'')+'</span>';
      d.addEventListener('click',function(){
        try{var f=iconField();if(f){f.value=ic;f.dispatchEvent(new Event('input',{bubbles:true}));}}catch(e){}
        g('biinp').value='';grid.innerHTML='';cnt.innerHTML='';updatePreview();
      });
      grid.appendChild(d);
    });
  }

  function setActive(cat){
    activeCat=cat;
    document.querySelectorAll('#bicats_'+UID+' .bi-cbtn').forEach(function(b){b.classList.toggle('on',b.dataset.cat===cat);});
    var pool=cat?CATS[cat]:ALL;
    var q=g('biinp').value.toLowerCase().trim();
    render(q?pool.filter(function(ic){return ic.indexOf(q)>=0;}):pool);
  }

  function init(){
    var catBar=g('bicats');if(!catBar)return;
    var allBtn=document.createElement('div');allBtn.className='bi-cbtn on';allBtn.dataset.cat='';
    allBtn.innerHTML='&#10022; Tout';
    allBtn.addEventListener('click',function(){g('biinp').value='';setActive('');});
    catBar.appendChild(allBtn);
    Object.keys(CATS).forEach(function(cat){
      var btn=document.createElement('div');btn.className='bi-cbtn';btn.dataset.cat=cat;
      btn.innerHTML=LABELS[cat]||cat;
      btn.addEventListener('click',function(){g('biinp').value='';setActive(cat);});
      catBar.appendChild(btn);
    });
    try{var f=iconField();if(f)f.addEventListener('input',updatePreview);}catch(e){}
    g('biinp').addEventListener('input',function(){
      var q=this.value.toLowerCase().trim();
      var pool=activeCat?CATS[activeCat]:ALL;
      render(q?pool.filter(function(ic){return ic.indexOf(q)>=0;}):pool);
    });
    updatePreview();
    render(ALL);
  }

  if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',init);}else{init();}
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
        import uuid
        uid = uuid.uuid4().hex[:8]
        return mark_safe(_ICON_SEARCH_JS.replace('{uid}', uid))
    icon_search_box.short_description = 'Recherche d\'icône'

    class Media:
        css = {'all': ['https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css']}


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon_preview', 'category', 'level', 'order']
    list_editable = ['order', 'level']
    list_filter = ['category']
    search_fields = ['name']
    readonly_fields = ['icon_preview_large', 'icon_search_box', 'color_swatch']
    fields = ['name', 'icon', 'icon_search_box', 'icon_preview_large', 'color', 'color_swatch', 'category', 'level', 'order']

    def icon_preview(self, obj):
        color = obj.color or '#4F46E5'
        if obj.icon:
            if obj.icon.startswith('bi-'):
                return format_html(
                    '<i class="bi {}" style="font-size:1.3rem;color:{};"></i> <small style="color:#6B7280;">{}</small>',
                    obj.icon, color, obj.icon
                )
            return format_html('<span style="font-size:1.3rem;">{}</span>', obj.icon)
        return '-'
    icon_preview.short_description = 'Icône'

    def icon_preview_large(self, obj):
        color = obj.color or '#4F46E5'
        if obj.icon:
            if obj.icon.startswith('bi-'):
                return format_html(
                    '<i class="bi {}" style="font-size:2.5rem;color:{};"></i>',
                    obj.icon, color
                )
            return format_html('<span style="font-size:2.5rem;">{}</span>', obj.icon)
        return format_html('<span style="color:#9ca3af;">Aucune icône définie</span>')
    icon_preview_large.short_description = 'Aperçu icône actuelle'

    def color_swatch(self, obj):
        color = obj.color or '#4F46E5'
        return format_html(
            '<span style="display:inline-block;width:20px;height:20px;border-radius:5px;background:{};border:1px solid #e5e7eb;vertical-align:middle;"></span> {}',
            color, color
        )
    color_swatch.short_description = 'Aperçu couleur'

    def icon_search_box(self, obj):
        import uuid
        uid = uuid.uuid4().hex[:8]
        return mark_safe(_ICON_SEARCH_JS.replace('{uid}', uid))
    icon_search_box.short_description = 'Recherche d\'icône'

    class Media:
        css = {'all': ['https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css']}


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
            site_url = getattr(django_settings, 'FRONTEND_URL', 'https://landryit.pythonanywhere.com').rstrip('/')
            return format_html('<a href="{}{}" target="_blank">Voir →</a>', site_url, url)
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
