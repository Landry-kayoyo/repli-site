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
#bi-search-wrap{margin-top:8px;padding:16px;background:#f8f7ff;border-radius:12px;border:1px solid #e0e7ff;}
#bi-search-input{width:100%;padding:9px 14px;border-radius:8px;border:1.5px solid #c7d2fe;font-size:14px;outline:none;font-family:inherit;box-sizing:border-box;}
#bi-search-input:focus{border-color:#4F46E5;box-shadow:0 0 0 3px rgba(79,70,229,0.1);}
#bi-cat-bar{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 0;}
.bi-cat-btn{display:inline-flex;align-items:center;gap:4px;padding:4px 12px;border-radius:20px;border:1.5px solid #e0e7ff;background:#fff;cursor:pointer;font-size:12px;font-weight:600;color:#6b7280;transition:all 0.15s;white-space:nowrap;}
.bi-cat-btn:hover{border-color:#4F46E5;color:#4F46E5;background:#eef2ff;}
.bi-cat-btn.active{border-color:#4F46E5;background:#4F46E5;color:#fff;}
#bi-search-results{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px;max-height:240px;overflow-y:auto;padding-right:2px;}
#bi-search-results::-webkit-scrollbar{width:4px;}
#bi-search-results::-webkit-scrollbar-track{background:#f0f2ff;border-radius:4px;}
#bi-search-results::-webkit-scrollbar-thumb{background:#c7d2fe;border-radius:4px;}
.bi-search-item{display:inline-flex;flex-direction:column;align-items:center;gap:4px;padding:8px 10px;border-radius:8px;border:1.5px solid #e0e7ff;cursor:pointer;transition:all 0.15s;background:#fff;min-width:68px;max-width:80px;}
.bi-search-item:hover{border-color:#4F46E5;background:#eef2ff;transform:translateY(-1px);}
.bi-search-item i{font-size:1.5rem;color:#4F46E5;}
.bi-search-item span{font-size:10px;color:#6b7280;max-width:72px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;text-align:center;}
#bi-current-preview{display:flex;align-items:center;gap:10px;margin-top:10px;padding:8px 12px;background:#eef2ff;border-radius:8px;font-size:13px;color:#4b5563;}
#bi-current-preview i{font-size:1.8rem;color:#4F46E5;}
#bi-result-count{font-size:11px;color:#9ca3af;margin-top:6px;}
</style>
<div id="bi-search-wrap">
  <b style="font-size:13px;color:#4F46E5;">🔍 Recherche Bootstrap Icons</b>
  <div style="font-size:12px;color:#6b7280;margin:4px 0 8px;">Tapez un mot-clé ou sélectionnez une catégorie ci-dessous</div>
  <input id="bi-search-input" type="text" placeholder="Ex : code, database, cloud, star, person…">
  <div id="bi-cat-bar"></div>
  <div id="bi-current-preview" style="display:none;"></div>
  <div id="bi-result-count"></div>
  <div id="bi-search-results"></div>
</div>
<script>
(function(){
  var CATS={
    'Tout':['bi-code-slash','bi-code-square','bi-code','bi-code-dot','bi-filetype-py','bi-filetype-js','bi-filetype-tsx','bi-filetype-ts','bi-filetype-html','bi-filetype-css','bi-filetype-json','bi-filetype-php','bi-filetype-java','bi-filetype-cs','bi-filetype-rb','bi-filetype-sql','bi-filetype-xml','bi-filetype-go','bi-filetype-sh','bi-filetype-yml','bi-database','bi-database-fill','bi-database-check','bi-database-add','bi-server','bi-hdd-network','bi-hdd-rack','bi-cloud','bi-cloud-fill','bi-cloud-upload','bi-cloud-download','bi-cloud-check','bi-cloud-arrow-up','bi-git','bi-github','bi-gitlab','bi-terminal','bi-terminal-fill','bi-laptop','bi-pc-display','bi-phone','bi-tablet','bi-cpu','bi-cpu-fill','bi-memory','bi-gpu-card','bi-wifi','bi-wifi-off','bi-bluetooth','bi-usb','bi-lock','bi-lock-fill','bi-unlock','bi-shield','bi-shield-check','bi-shield-fill','bi-key','bi-key-fill','bi-gear','bi-gear-fill','bi-gear-wide','bi-tools','bi-wrench','bi-wrench-adjustable','bi-box','bi-boxes','bi-layers','bi-stack','bi-diagram-3','bi-diagram-2','bi-flow','bi-grid','bi-grid-fill','bi-table','bi-list','bi-list-ul','bi-list-check','bi-kanban','bi-kanban-fill','bi-graph-up','bi-graph-down','bi-bar-chart','bi-bar-chart-fill','bi-pie-chart','bi-pie-chart-fill','bi-activity','bi-lightning','bi-lightning-fill','bi-lightning-charge','bi-fire','bi-rocket','bi-rocket-fill','bi-rocket-takeoff','bi-star','bi-star-fill','bi-star-half','bi-heart','bi-heart-fill','bi-bookmark','bi-bookmark-fill','bi-tag','bi-tag-fill','bi-tags','bi-tags-fill','bi-chat','bi-chat-fill','bi-chat-dots','bi-chat-left','bi-envelope','bi-envelope-fill','bi-envelope-open','bi-globe','bi-globe2','bi-link','bi-link-45deg','bi-search','bi-eye','bi-eye-fill','bi-eye-slash','bi-pencil','bi-pencil-fill','bi-pencil-square','bi-trash','bi-trash-fill','bi-trash3','bi-plus','bi-plus-circle','bi-plus-circle-fill','bi-dash','bi-x','bi-x-circle','bi-check','bi-check-circle','bi-check-circle-fill','bi-check2','bi-arrow-right','bi-arrow-left','bi-arrow-up','bi-arrow-down','bi-arrow-right-circle','bi-arrows-expand','bi-chevron-right','bi-chevron-left','bi-download','bi-upload','bi-share','bi-share-fill','bi-person','bi-person-fill','bi-person-circle','bi-people','bi-people-fill','bi-person-badge','bi-building','bi-building-fill','bi-briefcase','bi-briefcase-fill','bi-journal','bi-journal-code','bi-journal-text','bi-book','bi-book-fill','bi-newspaper','bi-newspaper-fill','bi-camera','bi-camera-fill','bi-camera-video','bi-image','bi-image-fill','bi-images','bi-music-note','bi-music-note-beamed','bi-play','bi-play-fill','bi-play-circle','bi-pause','bi-stop','bi-video','bi-video-fill','bi-mic','bi-mic-fill','bi-headphones','bi-speaker','bi-volume-up','bi-currency-bitcoin','bi-currency-ethereum','bi-currency-euro','bi-currency-dollar','bi-currency-pound','bi-paypal','bi-stripe','bi-credit-card','bi-credit-card-fill','bi-wallet','bi-wallet-fill','bi-cash','bi-cash-coin','bi-android2','bi-apple','bi-windows','bi-linux','bi-ubuntu','bi-discord','bi-slack','bi-twitter','bi-twitter-x','bi-linkedin','bi-facebook','bi-instagram','bi-youtube','bi-twitch','bi-whatsapp','bi-telegram','bi-pinterest','bi-reddit','bi-tiktok','bi-wordpress','bi-shopify','bi-google','bi-microsoft','bi-amazon','bi-docker','bi-kubernetes','bi-nginx','bi-apache','bi-trello','bi-github','bi-gitlab','bi-stack-overflow','bi-hash','bi-at','bi-trophy','bi-trophy-fill','bi-award','bi-award-fill','bi-flag','bi-flag-fill','bi-map','bi-map-fill','bi-geo-alt','bi-geo-alt-fill','bi-house','bi-house-fill','bi-shop','bi-cart','bi-cart-fill','bi-bag','bi-bag-fill','bi-box-seam','bi-truck','bi-send','bi-send-fill','bi-bell','bi-bell-fill','bi-alarm','bi-calendar','bi-calendar-fill','bi-calendar-check','bi-clock','bi-clock-fill','bi-hourglass','bi-info-circle','bi-info-circle-fill','bi-question-circle','bi-question-circle-fill','bi-exclamation-triangle','bi-exclamation-circle','bi-moon','bi-sun','bi-brightness-high','bi-toggle-on','bi-toggle-off','bi-sliders','bi-filter','bi-funnel','bi-sort-down','bi-sort-up','bi-layout-sidebar','bi-layout-text-window','bi-display','bi-printer','bi-file-earmark','bi-file-earmark-code','bi-file-earmark-text','bi-file-earmark-pdf','bi-file-earmark-zip','bi-folder','bi-folder-fill','bi-folder-open','bi-clipboard','bi-clipboard-fill','bi-clipboard-check','bi-qr-code','bi-upc','bi-robot','bi-cpu','bi-magic','bi-bezier','bi-bezier2','bi-palette','bi-palette-fill','bi-brush','bi-pen','bi-eraser','bi-scissors','bi-textarea','bi-input-cursor','bi-app','bi-app-indicator','bi-grid-1x2','bi-columns','bi-layout-three-columns','bi-textarea-resize','bi-zoom-in','bi-zoom-out','bi-fullscreen','bi-fullscreen-exit','bi-pip','bi-badge-ad','bi-badge-ar','bi-badge-cc','bi-badge-hd','bi-badge-vr','bi-badge-wc','bi-badge-4k','bi-badge-8k'],
    'Code':['bi-code-slash','bi-code-square','bi-code','bi-code-dot','bi-filetype-py','bi-filetype-js','bi-filetype-tsx','bi-filetype-ts','bi-filetype-html','bi-filetype-css','bi-filetype-json','bi-filetype-php','bi-filetype-java','bi-filetype-cs','bi-filetype-rb','bi-filetype-sql','bi-filetype-xml','bi-filetype-go','bi-filetype-sh','bi-filetype-yml','bi-terminal','bi-terminal-fill','bi-git','bi-github','bi-gitlab','bi-journal-code','bi-file-earmark-code','bi-braces','bi-braces-asterisk','bi-bug','bi-bug-fill','bi-textarea','bi-input-cursor','bi-hash'],
    'Cloud & Data':['bi-database','bi-database-fill','bi-database-check','bi-database-add','bi-server','bi-hdd-network','bi-hdd-rack','bi-cloud','bi-cloud-fill','bi-cloud-upload','bi-cloud-download','bi-cloud-check','bi-cloud-arrow-up','bi-docker','bi-kubernetes','bi-nginx','bi-apache','bi-amazon','bi-google','bi-microsoft','bi-diagram-3','bi-diagram-2','bi-flow','bi-graph-up','bi-graph-down','bi-bar-chart','bi-bar-chart-fill','bi-pie-chart','bi-pie-chart-fill','bi-activity'],
    'UI & Actions':['bi-search','bi-eye','bi-eye-fill','bi-eye-slash','bi-pencil','bi-pencil-fill','bi-pencil-square','bi-trash','bi-trash-fill','bi-trash3','bi-plus','bi-plus-circle','bi-plus-circle-fill','bi-dash','bi-x','bi-x-circle','bi-check','bi-check-circle','bi-check-circle-fill','bi-check2','bi-arrow-right','bi-arrow-left','bi-arrow-up','bi-arrow-down','bi-arrow-right-circle','bi-arrows-expand','bi-chevron-right','bi-chevron-left','bi-download','bi-upload','bi-share','bi-share-fill','bi-filter','bi-funnel','bi-sort-down','bi-sort-up','bi-sliders','bi-gear','bi-gear-fill','bi-gear-wide','bi-grid','bi-grid-fill','bi-list','bi-list-ul','bi-list-check','bi-table','bi-kanban','bi-kanban-fill','bi-layout-sidebar','bi-columns','bi-zoom-in','bi-zoom-out','bi-fullscreen','bi-bell','bi-bell-fill','bi-toggle-on','bi-toggle-off','bi-send','bi-send-fill','bi-bookmark','bi-bookmark-fill','bi-tag','bi-tag-fill','bi-tags','bi-flag','bi-flag-fill','bi-star','bi-star-fill','bi-heart','bi-heart-fill','bi-link','bi-link-45deg','bi-globe','bi-globe2','bi-clipboard','bi-clipboard-fill','bi-clipboard-check','bi-qr-code','bi-display','bi-printer'],
    'Médias':['bi-camera','bi-camera-fill','bi-camera-video','bi-image','bi-image-fill','bi-images','bi-music-note','bi-music-note-beamed','bi-play','bi-play-fill','bi-play-circle','bi-pause','bi-stop','bi-video','bi-video-fill','bi-mic','bi-mic-fill','bi-headphones','bi-speaker','bi-volume-up','bi-youtube','bi-twitch','bi-spotify','bi-file-earmark-pdf','bi-file-earmark-zip','bi-file-earmark-text','bi-file-earmark'],
    'Personnes':['bi-person','bi-person-fill','bi-person-circle','bi-people','bi-people-fill','bi-person-badge','bi-person-check','bi-person-plus','bi-person-x','bi-building','bi-building-fill','bi-briefcase','bi-briefcase-fill','bi-house','bi-house-fill','bi-geo-alt','bi-geo-alt-fill','bi-map','bi-map-fill','bi-award','bi-award-fill','bi-trophy','bi-trophy-fill'],
    'Finance':['bi-currency-bitcoin','bi-currency-ethereum','bi-currency-euro','bi-currency-dollar','bi-currency-pound','bi-paypal','bi-stripe','bi-credit-card','bi-credit-card-fill','bi-wallet','bi-wallet-fill','bi-cash','bi-cash-coin','bi-cart','bi-cart-fill','bi-bag','bi-bag-fill','bi-shop','bi-truck','bi-box-seam'],
    'Réseaux sociaux':['bi-discord','bi-slack','bi-twitter','bi-twitter-x','bi-linkedin','bi-facebook','bi-instagram','bi-youtube','bi-twitch','bi-whatsapp','bi-telegram','bi-pinterest','bi-reddit','bi-tiktok','bi-wordpress','bi-shopify','bi-google','bi-github','bi-gitlab','bi-stack-overflow'],
    'Système':['bi-cpu','bi-cpu-fill','bi-memory','bi-gpu-card','bi-laptop','bi-pc-display','bi-phone','bi-tablet','bi-wifi','bi-wifi-off','bi-bluetooth','bi-lock','bi-lock-fill','bi-unlock','bi-shield','bi-shield-check','bi-shield-fill','bi-key','bi-key-fill','bi-tools','bi-wrench','bi-wrench-adjustable','bi-android2','bi-apple','bi-windows','bi-linux','bi-ubuntu','bi-robot','bi-magic','bi-moon','bi-sun','bi-brightness-high','bi-clock','bi-clock-fill','bi-calendar','bi-calendar-fill','bi-calendar-check','bi-alarm','bi-hourglass','bi-info-circle','bi-question-circle','bi-exclamation-triangle','bi-exclamation-circle']
  };
  var catNames=Object.keys(CATS);
  var activeCat='Tout';
  var catBar=document.getElementById('bi-cat-bar');
  var input=document.getElementById('bi-search-input');
  var results=document.getElementById('bi-search-results');
  var preview=document.getElementById('bi-current-preview');
  var countEl=document.getElementById('bi-result-count');
  var iconField=document.getElementById('id_icon');

  function updatePreview(){
    var val=iconField?iconField.value.trim():'';
    if(val.startsWith('bi-')){
      preview.style.display='flex';
      preview.innerHTML='<i class="bi '+val+'"></i><div><div style="font-size:12px;color:#9ca3af;">Icône sélectionnée</div><code style="font-size:13px;background:#fff;padding:2px 8px;border-radius:4px;color:#4F46E5;font-weight:700;">'+val+'</code></div>';
    } else if(val){
      preview.style.display='flex';
      preview.innerHTML='<span style="font-size:1.8rem;">'+val+'</span><div><div style="font-size:12px;color:#9ca3af;">Emoji sélectionné</div><code style="font-size:13px;background:#fff;padding:2px 8px;border-radius:4px;color:#4F46E5;font-weight:700;">'+val+'</code></div>';
    } else {
      preview.style.display='none';preview.innerHTML='';
    }
  }
  if(iconField){iconField.addEventListener('input',updatePreview);updatePreview();}

  function selectIcon(ic){
    if(iconField)iconField.value=ic;
    input.value='';
    results.innerHTML='';
    countEl.innerHTML='';
    setActiveBtn(activeCat);
    updatePreview();
  }

  function render(list){
    if(!list.length){results.innerHTML='<span style="font-size:12px;color:#9ca3af;padding:8px 0;">Aucun résultat. Essayez un autre mot-clé.</span>';countEl.innerHTML='';return;}
    var shown=list.slice(0,80);
    countEl.innerHTML='<span>'+shown.length+(list.length>80?' / '+list.length:'')+' icône'+(shown.length>1?'s':'')+'</span>';
    results.innerHTML=shown.map(function(ic){
      var label=ic.replace(/^bi-/,'');
      return '<div class="bi-search-item" title="'+ic+'" onclick="(function(){var ic=\''+ic+'\';var f=document.getElementById(\'id_icon\');if(f)f.value=ic;document.getElementById(\'bi-search-input\').value=\'\';document.getElementById(\'bi-search-results\').innerHTML=\'\';document.getElementById(\'bi-result-count\').innerHTML=\'\';var p=document.getElementById(\'bi-current-preview\');p.style.display=\'flex\';p.innerHTML=\'<i class=\\"bi \'+ic+\'\\"></i><div><div style=\\"font-size:12px;color:#9ca3af;\\">Icône sélectionnée</div><code style=\\"font-size:13px;background:#fff;padding:2px 8px;border-radius:4px;color:#4F46E5;font-weight:700;\\">\'+ic+\'</code></div>\';})()"><i class="bi '+ic+'"></i><span>'+label+'</span></div>';
    }).join('');
  }

  function setActiveBtn(cat){
    activeCat=cat;
    document.querySelectorAll('.bi-cat-btn').forEach(function(b){
      b.classList.toggle('active',b.dataset.cat===cat);
    });
    if(!input.value.trim()){render(CATS[cat]);}
  }

  catNames.forEach(function(cat){
    var emojis={'Tout':'✦','Code':'💻','Cloud & Data':'☁️','UI & Actions':'🖱️','Médias':'🎬','Personnes':'👤','Finance':'💰','Réseaux sociaux':'📱','Système':'⚙️'};
    var btn=document.createElement('div');
    btn.className='bi-cat-btn'+(cat==='Tout'?' active':'');
    btn.dataset.cat=cat;
    btn.innerHTML=(emojis[cat]||'📦')+' '+cat;
    btn.onclick=function(){input.value='';setActiveBtn(cat);};
    catBar.appendChild(btn);
  });

  render(CATS['Tout']);

  input.addEventListener('input',function(){
    var q=this.value.toLowerCase().trim();
    if(!q){render(CATS[activeCat]);return;}
    var pool=CATS['Tout'];
    var matches=pool.filter(function(ic){return ic.indexOf(q)>=0;});
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
        return mark_safe(_ICON_SEARCH_JS)
    icon_search_box.short_description = 'Recherche d\'icône'

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
