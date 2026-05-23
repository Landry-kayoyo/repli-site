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
    """Build the system prompt with site context."""
    from articles.models import Article
    from projects.models import Project
    from tips.models import Tip
    from portfolio.models import PortfolioItem
    from comments.models import Comment

    articles_count = Article.objects.filter(status='published').count()
    projects_count = Project.objects.filter(status='published').count()
    tips_count = Tip.objects.filter(status='published').count()
    portfolio_count = PortfolioItem.objects.count()
    pending_comments = Comment.objects.filter(is_approved=False).count()

    recent_articles = list(
        Article.objects.filter(status='published')
        .order_by('-published_at')
        .values('title', 'category__name')[:5]
    )
    recent_titles = ', '.join([a['title'] for a in recent_articles]) or 'Aucun'

    custom_prompt = settings.ai_system_prompt.strip()
    if custom_prompt:
        return custom_prompt

    return f"""Tu es l'assistant IA de {settings.site_name or 'Landry Net'}, le site personnel de {settings.author_name or 'Landry'}.

CONTEXTE DU SITE:
- Nom du site: {settings.site_name}
- Description: {settings.description}
- Auteur: {settings.author_name} — {settings.author_job_title}
- Biographie: {settings.author_bio[:200] if settings.author_bio else 'Non défini'}

CONTENU ACTUEL:
- {articles_count} articles publiés
- {projects_count} projets publiés
- {tips_count} astuces publiées
- {portfolio_count} réalisations portfolio
- {pending_comments} commentaires en attente de modération
- Derniers articles: {recent_titles}

TES RÔLES:
1. RÉDACTION: Suggérer des titres accrocheurs, améliorer les descriptions, rédiger des excerpts percutants
2. SEO: Proposer des meta-title (max 60 chars) et meta-description (max 160 chars) optimisés
3. ICÔNES: Suggérer des noms d'icônes Bootstrap Icons (format: bi-nom-icone) selon le contexte
4. CONTENU: Aider à rédiger et structurer des articles, projets, astuces
5. ADMINISTRATION: Guider pour ajouter compétences (Skill), expériences, formations
6. ANALYSE: Analyser et améliorer le site

RÈGLES:
- Réponds TOUJOURS en français
- Sois concis et pratique
- Pour les suggestions de titres: propose 3-5 variantes numérotées
- Pour le SEO: fournis exactement le meta-title ET la meta-description prêts à copier
- Pour les icônes Bootstrap: donne plusieurs options avec leur nom exact (ex: bi-code-slash, bi-cpu-fill)
- Si on te demande d'ajouter une compétence, pose les questions nécessaires: nom, niveau (0-100), icône, catégorie"""


def _call_ai(api_key, base_url, model, messages):
    """Call the AI API using urllib (no external dependencies)."""
    url = f"{base_url.rstrip('/')}/chat/completions"
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "max_tokens": 800,
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
        history = body.get('history', [])  # [{"role": "user/assistant", "content": "..."}]
        context_type = body.get('context', '')  # 'article', 'project', 'tip', 'skill', 'general'
        context_data = body.get('context_data', {})  # Current form data
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not user_message:
        return JsonResponse({'error': 'Message vide'}, status=400)

    settings = _get_ai_settings()
    if not settings.ai_enabled:
        return JsonResponse({'error': "L'assistant IA n'est pas activé. Configurez-le dans Admin → Paramètres du site → Configuration IA."}, status=403)
    if not settings.ai_api_key:
        return JsonResponse({'error': "Clé API manquante. Configurez-la dans Admin → Paramètres du site → Configuration IA."}, status=403)

    system_prompt = _get_site_context(settings)

    # Build context message if we're on a specific form
    if context_type and context_data:
        context_msg = f"\n\nCONTEXTE ACTUEL (formulaire {context_type}):\n"
        for k, v in context_data.items():
            if v:
                context_msg += f"- {k}: {str(v)[:200]}\n"
        system_prompt += context_msg

    # Build messages
    messages = [{"role": "system", "content": system_prompt}]
    # Add history (limit to last 10 exchanges)
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
            return JsonResponse({'error': 'Clé API invalide. Vérifiez votre configuration.'}, status=200)
        elif e.code == 429:
            return JsonResponse({'error': 'Quota API dépassé (30 requêtes/jour). Réessayez demain ou changez de clé.'}, status=200)
        else:
            return JsonResponse({'error': f'Erreur API ({e.code}). Vérifiez l\'URL de base et la clé API.'}, status=200)
    except urllib.error.URLError as e:
        logger.error(f"AI API URL error: {e}")
        return JsonResponse({'error': "Impossible de contacter l'API. Vérifiez l'URL de base."}, status=200)
    except Exception as e:
        logger.error(f"AI unexpected error: {e}")
        return JsonResponse({'error': f'Erreur inattendue: {str(e)}'}, status=200)


@staff_member_required
@csrf_exempt
@require_POST
def ai_suggest(request):
    """Quick suggestion endpoint for form fields."""
    try:
        body = json.loads(request.body)
        action = body.get('action', '')  # 'title', 'seo', 'icon', 'excerpt'
        data = body.get('data', {})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    prompts = {
        'title': f"Propose 5 titres accrocheurs pour un article/astuce sur: '{data.get('topic', '')}'. Numérotés 1 à 5, style punchy et SEO-friendly. Pas d'explication.",
        'seo': f"Pour ce contenu:\nTitre: {data.get('title', '')}\nDescription: {data.get('excerpt', '')}\nPropose:\n1. Meta-title (max 60 chars): ...\n2. Meta-description (max 160 chars): ...\nPrêts à copier-coller.",
        'icon': f"Propose 5 noms d'icônes Bootstrap Icons pour: '{data.get('name', '')}'. Format: bi-nom-icone. Une par ligne, sans explication.",
        'excerpt': f"Écris une description courte (2-3 phrases max, 150 chars) pour cet article:\nTitre: {data.get('title', '')}\nContenu: {data.get('content', '')[:300]}",
    }

    if action not in prompts:
        return JsonResponse({'error': 'Action invalide'}, status=400)

    settings = _get_ai_settings()
    if not settings.ai_enabled or not settings.ai_api_key:
        return JsonResponse({'error': "IA non configurée"}, status=403)

    try:
        reply = _call_ai(
            api_key=settings.ai_api_key,
            base_url=settings.ai_api_base_url or 'https://api.chatanywhere.tech/v1',
            model=settings.ai_model or 'gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": f"Tu es l'assistant de {settings.site_name or 'Landry Net'}. Réponds toujours en français, sois concis."},
                {"role": "user", "content": prompts[action]},
            ],
        )
        return JsonResponse({'reply': reply, 'ok': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=200)
