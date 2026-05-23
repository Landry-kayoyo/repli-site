"""
AI Assistant views — admin-only proxy to the configured AI API.
"""
import json
import urllib.request
import urllib.error
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required

logger = logging.getLogger(__name__)


def _get_ai_settings():
    from core.models import SiteSettings
    s, _ = SiteSettings.objects.get_or_create(pk=1)
    return s


def _get_site_context(settings):
    """Build the system prompt with rich site context."""
    from articles.models import Article
    from projects.models import Project
    from tips.models import Tip
    from portfolio.models import PortfolioItem
    from comments.models import Comment

    try:
        articles_count = Article.objects.filter(status='published').count()
        projects_count = Project.objects.filter(status='published').count()
        tips_count = Tip.objects.filter(status='published').count()
        portfolio_count = PortfolioItem.objects.count()
        pending_comments = Comment.objects.filter(is_approved=False).count()

        recent_articles = list(
            Article.objects.filter(status='published')
            .order_by('-published_at')
            .values('title', 'category__name', 'excerpt')[:8]
        )

        recent_projects = list(
            Project.objects.filter(status='published')
            .order_by('-created_at')
            .values('title', 'description')[:5]
        )

        recent_tips = list(
            Tip.objects.filter(status='published')
            .order_by('-created_at')
            .values('title', 'difficulty')[:5]
        )

        # Get categories if possible
        try:
            from articles.models import Category
            categories = list(Category.objects.values_list('name', flat=True)[:10])
            categories_str = ', '.join(categories) if categories else 'Non défini'
        except Exception:
            categories_str = 'Non défini'

    except Exception:
        articles_count = projects_count = tips_count = portfolio_count = pending_comments = 0
        recent_articles = recent_projects = recent_tips = []
        categories_str = 'Non défini'

    custom_prompt = settings.ai_system_prompt.strip() if settings.ai_system_prompt else ''
    if custom_prompt:
        return custom_prompt

    articles_list = '\n'.join([f"  - {a['title']} ({a.get('category__name','') or 'Sans catégorie'})" for a in recent_articles]) or '  Aucun'
    projects_list = '\n'.join([f"  - {p['title']}" for p in recent_projects]) or '  Aucun'
    tips_list = '\n'.join([f"  - {t['title']} [{t.get('difficulty','')}]" for t in recent_tips]) or '  Aucun'

    return f"""Tu es l'assistant IA expert de {settings.site_name or 'Landry Net'}, le site personnel de {settings.author_name or 'Landry'}.

━━━ PROFIL DU SITE ━━━
Nom: {settings.site_name}
Description: {settings.description}
Auteur: {settings.author_name} — {settings.author_job_title}
Biographie: {(settings.author_bio or '')[:300]}
URL admin: /admin/

━━━ STATISTIQUES ACTUELLES ━━━
• {articles_count} articles publiés (catégories: {categories_str})
• {projects_count} projets publiés
• {tips_count} astuces publiées
• {portfolio_count} réalisations portfolio
• {pending_comments} commentaires en attente de modération

━━━ PUBLICATIONS RÉCENTES ━━━
Articles récents:
{articles_list}

Projets récents:
{projects_list}

Astuces récentes:
{tips_list}

━━━ TES MISSIONS ━━━

1. CRÉATION DE PUBLICATIONS:
   - Quand on te demande de créer un article, génère:
     * Titre accrocheur + sous-titre
     * Excerpt (2-3 phrases, max 200 chars)
     * Plan détaillé avec sections H2/H3
     * Contenu introductif complet (500-800 mots)
     * Tags suggérés
     * Meta-title (max 60 chars) et meta-description (max 160 chars)
     * Lien admin pour créer: /admin/articles/article/add/
   
   - Pour un projet:
     * Titre + description courte
     * Technologies utilisées
     * Description longue avec objectifs et fonctionnalités
     * Lien admin: /admin/projects/project/add/
   
   - Pour une astuce:
     * Titre + difficulté (beginner/intermediate/advanced)
     * Contenu structuré avec étapes
     * Lien admin: /admin/tips/tip/add/

2. RÉDACTION & SEO:
   - Titres: propose 5 variantes numérotées
   - SEO: meta-title (≤60 chars) + meta-description (≤160 chars) prêts à copier
   - Excerpts: 2-3 phrases percutantes, max 200 chars

3. ICÔNES BOOTSTRAP ICONS:
   - Format exact: bi-nom-icone
   - Donne 5-8 options avec leur usage suggéré
   - Exemples populaires: bi-code-slash, bi-cpu-fill, bi-lightning-fill, bi-database-fill, bi-cloud-fill

4. ADMINISTRATION:
   - Compétences: /admin/core/skill/add/ (nom, niveau 0-100, icône Bootstrap, catégorie)
   - Expériences: /admin/core/experience/add/
   - Formations: /admin/core/education/add/
   - Paramètres: /admin/core/sitesettings/1/change/
   - Commentaires en attente: /admin/comments/comment/?is_approved__exact=0

5. ANALYSE & AMÉLIORATION:
   - Suggérer des idées de contenu basées sur les tendances
   - Analyser le mix de contenu existant
   - Recommander des améliorations SEO

━━━ RÈGLES IMPORTANTES ━━━
- Réponds TOUJOURS en français
- Sois concis mais complet
- Pour la création de contenu: fournis tout ce qu'il faut pour publier immédiatement
- Pour les icônes: donne le nom exact utilisable dans les templates Django
- Utilise des emojis pour rendre les réponses plus lisibles
- Quand tu crées du contenu, indique le lien admin pour le publier"""


def _call_ai(api_key, base_url, model, messages):
    """Call the AI API using urllib (no external dependencies)."""
    url = f"{base_url.rstrip('/')}/chat/completions"
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "max_tokens": 1200,
        "temperature": 0.7,
    }).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        },
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        return data['choices'][0]['message']['content']


@staff_member_required
@csrf_exempt
@require_POST
def ai_chat(request):
    """General AI chat endpoint."""
    try:
        body = json.loads(request.body)
        user_message = body.get('message', '').strip()
        history = body.get('history', [])
        context_type = body.get('context', '')
        context_data = body.get('context_data', {})
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not user_message:
        return JsonResponse({'error': 'Message vide'}, status=400)

    settings = _get_ai_settings()
    if not settings.ai_enabled:
        return JsonResponse({'error': "L'assistant IA n'est pas activé. Configurez-le dans Admin → Paramètres du site → Configuration IA."}, status=403)
    if not settings.ai_api_key:
        return JsonResponse({'error': "Clé API manquante. Allez dans Admin → Paramètres du site → Configuration IA pour ajouter votre clé API."}, status=403)

    system_prompt = _get_site_context(settings)

    if context_type and context_type != 'general' and context_data:
        context_msg = f"\n\n━━━ FORMULAIRE ACTUEL ({context_type.upper()}) ━━━\n"
        for k, v in context_data.items():
            if v:
                context_msg += f"• {k}: {str(v)[:200]}\n"
        system_prompt += context_msg

    messages = [{"role": "system", "content": system_prompt}]
    for msg in history[-20:]:
        if msg.get('role') in ('user', 'assistant') and msg.get('content'):
            messages.append({"role": msg['role'], "content": msg['content']})
    messages.append({"role": "user", "content": user_message})

    try:
        reply = _call_ai(
            api_key=settings.ai_api_key,
            base_url=settings.ai_api_base_url or 'https://api.chatanywhere.tech/v1',
            model=settings.ai_model or 'gpt-3.5-turbo',
            messages=messages,
        )
        return JsonResponse({'reply': reply, 'ok': True})
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8', errors='ignore')
        logger.error(f"AI API HTTP error: {e.code} — {error_body}")
        if e.code == 401:
            return JsonResponse({'error': '❌ Clé API invalide. Vérifiez votre clé dans Paramètres → Configuration IA.'}, status=200)
        elif e.code == 429:
            return JsonResponse({'error': '⏳ Quota API dépassé. Réessayez plus tard ou changez de clé API.'}, status=200)
        else:
            return JsonResponse({'error': f'❌ Erreur API ({e.code}). Vérifiez l\'URL de base et la clé API.'}, status=200)
    except urllib.error.URLError as e:
        logger.error(f"AI API URL error: {e}")
        return JsonResponse({'error': "❌ Impossible de contacter l'API. Vérifiez l'URL de base dans les paramètres."}, status=200)
    except Exception as e:
        logger.error(f"AI unexpected error: {e}")
        return JsonResponse({'error': f'❌ Erreur inattendue: {str(e)}'}, status=200)


@staff_member_required
@csrf_exempt
@require_POST
def ai_suggest(request):
    """Quick suggestion endpoint for form fields."""
    try:
        body = json.loads(request.body)
        action = body.get('action', '')
        data = body.get('data', {})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    prompts = {
        'title': f"Propose 5 titres accrocheurs et SEO-friendly pour: '{data.get('topic', '')}'. Numérotés 1 à 5, style percutant. Pas d'explication.",
        'seo': f"Pour:\nTitre: {data.get('title', '')}\nDescription: {data.get('excerpt', '')}\nDonne:\n1. Meta-title (max 60 chars): ...\n2. Meta-description (max 160 chars): ...\nPrêts à copier.",
        'icon': f"Propose 8 noms d'icônes Bootstrap Icons pour: '{data.get('name', '')}'. Format: bi-nom-icone. Une par ligne.",
        'excerpt': f"Écris une description courte (2 phrases max, 180 chars) pour:\nTitre: {data.get('title', '')}\nContenu: {data.get('content', '')[:300]}",
    }

    if action not in prompts:
        return JsonResponse({'error': 'Action invalide'}, status=400)

    settings = _get_ai_settings()
    if not settings.ai_enabled or not settings.ai_api_key:
        return JsonResponse({'error': "IA non configurée — allez dans Paramètres du site → Configuration IA"}, status=403)

    try:
        reply = _call_ai(
            api_key=settings.ai_api_key,
            base_url=settings.ai_api_base_url or 'https://api.chatanywhere.tech/v1',
            model=settings.ai_model or 'gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": f"Tu es l'assistant de {settings.site_name or 'Landry Net'}. Réponds en français, sois concis et direct."},
                {"role": "user", "content": prompts[action]},
            ],
        )
        return JsonResponse({'reply': reply, 'ok': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=200)
