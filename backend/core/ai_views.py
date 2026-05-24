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
    """Build the system prompt with rich site context including analytics."""
    from articles.models import Article
    from projects.models import Project
    from tips.models import Tip
    from comments.models import Comment
    from core.models import PageView
    from django.db.models import Sum
    from django.utils import timezone
    from datetime import timedelta

    try:
        articles_count = Article.objects.filter(status='published').count()
        projects_count = Project.objects.filter(status='published').count()
        tips_count = Tip.objects.filter(status='published').count()
        pending_comments = Comment.objects.filter(is_approved=False).count()

        recent_articles = list(
            Article.objects.filter(status='published')
            .order_by('-published_at')
            .values('title', 'category__name', 'excerpt', 'views_count')[:8]
        )
        recent_projects = list(
            Project.objects.filter(status='published')
            .order_by('-created_at')
            .values('title', 'description', 'views_count')[:5]
        )
        recent_tips = list(
            Tip.objects.filter(status='published')
            .order_by('-created_at')
            .values('title', 'difficulty', 'views_count')[:5]
        )

        try:
            from articles.models import Category
            categories = list(Category.objects.values_list('name', flat=True)[:10])
            categories_str = ', '.join(categories) if categories else 'Non défini'
        except Exception:
            categories_str = 'Non défini'

        # Analytics data
        today = timezone.now().date()
        last_30 = today - timedelta(days=30)
        last_7 = today - timedelta(days=7)

        views_today = PageView.objects.filter(date=today).aggregate(t=Sum('count'))['t'] or 0
        views_7 = PageView.objects.filter(date__gte=last_7).aggregate(t=Sum('count'))['t'] or 0
        views_30 = PageView.objects.filter(date__gte=last_30).aggregate(t=Sum('count'))['t'] or 0

        top_pages = list(
            PageView.objects.filter(date__gte=last_30)
            .values('content_type', 'object_title', 'object_slug')
            .annotate(total=Sum('count'))
            .order_by('-total')[:5]
        )
        top_pages_str = '\n'.join([
            f"  - [{p['content_type']}] {p['object_title']} → {p['total']} vues"
            for p in top_pages
        ]) or '  Aucune donnée de visites encore'

    except Exception as e:
        logger.error(f"Context error: {e}")
        articles_count = projects_count = tips_count = pending_comments = 0
        recent_articles = recent_projects = recent_tips = []
        categories_str = 'Non défini'
        views_today = views_7 = views_30 = 0
        top_pages_str = '  Aucune donnée'

    custom_prompt = settings.ai_system_prompt.strip() if settings.ai_system_prompt else ''
    if custom_prompt:
        return custom_prompt

    articles_list = '\n'.join([
        f"  - {a['title']} ({a.get('category__name','') or 'Sans catégorie'}) — {a.get('views_count',0)} vues"
        for a in recent_articles
    ]) or '  Aucun'
    projects_list = '\n'.join([
        f"  - {p['title']} — {p.get('views_count',0)} vues"
        for p in recent_projects
    ]) or '  Aucun'
    tips_list = '\n'.join([
        f"  - {t['title']} [{t.get('difficulty','')}] — {t.get('views_count',0)} vues"
        for t in recent_tips
    ]) or '  Aucun'

    return f"""Tu es l'assistant IA expert de {settings.site_name or 'Landry Net'}, le site personnel de {settings.author_name or 'Landry'}.

━━━ PROFIL DU SITE ━━━
Nom: {settings.site_name}
Description: {settings.description}
Auteur: {settings.author_name} — {settings.author_job_title}
Biographie: {(settings.author_bio or '')[:300]}

━━━ STATISTIQUES ACTUELLES ━━━
• {articles_count} articles publiés (catégories: {categories_str})
• {projects_count} projets publiés
• {tips_count} astuces publiées
• {pending_comments} commentaires en attente de modération

━━━ ANALYTIQUES (30 derniers jours) ━━━
• Vues aujourd'hui: {views_today}
• Vues 7 jours: {views_7}
• Vues 30 jours: {views_30}

Top pages (30j):
{top_pages_str}

━━━ PUBLICATIONS RÉCENTES ━━━
Articles récents:
{articles_list}

Projets récents:
{projects_list}

Astuces récentes:
{tips_list}

━━━ TES MISSIONS ━━━

1. CRÉATION DE PUBLICATIONS:
   - Article: titre + sous-titre + excerpt (2-3 phrases, max 200 chars) + plan H2/H3 + intro 500-800 mots + tags + meta-title (≤60 chars) + meta-description (≤160 chars) + lien: /admin/articles/article/add/
   - Projet: titre + description courte + technologies + description longue + lien: /admin/projects/project/add/
   - Astuce: titre + difficulté + contenu structuré + lien: /admin/tips/tip/add/

2. RÉDACTION & SEO:
   - Titres: 5 variantes numérotées, percutantes et SEO-friendly
   - SEO: meta-title (≤60 chars) + meta-description (≤160 chars) prêts à copier
   - Excerpts: 2-3 phrases percutantes, max 200 chars

3. ANALYSE & AMÉLIORATION:
   - Analyser les pages les plus vues et suggérer du contenu similaire
   - Identifier les sujets manquants par rapport aux tendances du secteur
   - Recommander des améliorations SEO basées sur les stats réelles
   - Analyser le mix de contenu (articles vs projets vs astuces)

4. ICÔNES BOOTSTRAP ICONS:
   - Format exact: bi-nom-icone
   - 5-8 options avec leur usage suggéré
   - Exemples: bi-code-slash, bi-cpu-fill, bi-lightning-fill, bi-database-fill, bi-cloud-fill

5. ADMINISTRATION:
   - Compétences: /admin/core/skill/add/
   - Expériences: /admin/core/experience/add/
   - Paramètres: /admin/core/sitesettings/1/change/
   - Commentaires en attente: /admin/comments/comment/?is_approved__exact=0

━━━ RÈGLES ━━━
- Réponds TOUJOURS en français
- Sois concis mais complet, utilise des emojis pour structurer
- Pour la création de contenu: fournis tout ce qu'il faut pour publier immédiatement
- Pour les analyses: base-toi sur les vraies données de vues fournies ci-dessus
- Pour les icônes: donne le nom exact utilisable dans les templates Django"""


def _call_ai(api_key, base_url, model, messages, max_tokens=1500):
    """Call the AI API using urllib (no external dependencies)."""
    url = f"{base_url.rstrip('/')}/chat/completions"
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
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
            max_tokens=1500,
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
        'icon': f"Propose 8 noms d'icônes Bootstrap Icons pour: '{data.get('name', '')}'. Format: bi-nom-icone. Une par ligne avec description courte.",
        'excerpt': f"Écris une description courte (2 phrases max, 180 chars) pour:\nTitre: {data.get('title', '')}\nContenu: {data.get('content', '')[:300]}",
        'tags': f"Propose 8 tags pertinents (mots-clés courts) pour:\nTitre: {data.get('title', '')}\nContenu: {data.get('content', '')[:300]}\nUn tag par ligne, en minuscules, sans #.",
        'improve': f"Améliore ce texte en le rendant plus percutant, clair et SEO-friendly (garde la même longueur):\n\n{data.get('content', '')[:500]}",
        'structure': f"Propose un plan détaillé (H2/H3) pour un article sur: '{data.get('topic', '')}'. Format: ## Section\n### Sous-section",
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
            max_tokens=800,
        )
        return JsonResponse({'reply': reply, 'ok': True})
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return JsonResponse({'error': '❌ Clé API invalide.'}, status=200)
        elif e.code == 429:
            return JsonResponse({'error': '⏳ Quota API dépassé.'}, status=200)
        return JsonResponse({'error': f'❌ Erreur API ({e.code})'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=200)


@staff_member_required
@csrf_exempt
@require_POST
def ai_analyze(request):
    """Analytics-aware AI analysis endpoint."""
    try:
        body = json.loads(request.body)
        analysis_type = body.get('type', '')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    settings = _get_ai_settings()
    if not settings.ai_enabled or not settings.ai_api_key:
        return JsonResponse({'error': "IA non configurée"}, status=403)

    from core.models import PageView
    from django.db.models import Sum
    from django.utils import timezone
    from datetime import timedelta
    from articles.models import Article
    from projects.models import Project
    from tips.models import Tip

    try:
        today = timezone.now().date()
        last_30 = today - timedelta(days=30)
        top_pages = list(
            PageView.objects.filter(date__gte=last_30)
            .values('content_type', 'object_title')
            .annotate(total=Sum('count'))
            .order_by('-total')[:10]
        )
        articles_titles = list(Article.objects.filter(status='published').values_list('title', flat=True)[:20])
        projects_titles = list(Project.objects.filter(status='published').values_list('title', flat=True)[:10])
        tips_titles = list(Tip.objects.filter(status='published').values_list('title', flat=True)[:10])

        top_str = '\n'.join([f"- [{p['content_type']}] {p['object_title']}: {p['total']} vues" for p in top_pages]) or 'Aucune donnée'
    except Exception as e:
        top_str = 'Erreur de récupération des données'
        articles_titles = projects_titles = tips_titles = []

    if analysis_type == 'content_gaps':
        prompt = f"""Analyse mon contenu et identifie les lacunes à combler:

Articles existants: {', '.join(articles_titles[:10]) or 'Aucun'}
Projets existants: {', '.join(projects_titles[:5]) or 'Aucun'}
Astuces existantes: {', '.join(tips_titles[:5]) or 'Aucun'}

Top pages (30j):
{top_str}

Donne-moi:
1. 5 sujets d'articles manquants très pertinents
2. 3 types de projets qui manquent
3. 3 astuces très demandées à écrire
Base-toi sur les pages les plus vues pour identifier les tendances."""
    elif analysis_type == 'seo_audit':
        prompt = f"""Fais un audit SEO rapide de mon site {settings.site_name}:

Contenu: {len(articles_titles)} articles, {len(projects_titles)} projets, {len(tips_titles)} astuces
Top pages: {top_str}

Donne:
1. 3 points forts SEO actuels
2. 5 améliorations prioritaires
3. 3 recommandations de maillage interne
Sois spécifique et actionnable."""
    elif analysis_type == 'growth_plan':
        prompt = f"""Crée un plan de croissance sur 30 jours pour {settings.site_name}:

Situation actuelle:
- {len(articles_titles)} articles, {len(projects_titles)} projets, {len(tips_titles)} astuces publiés
- Top pages: {top_str}

Plan détaillé avec:
1. Objectifs réalistes (vues, publications)
2. Calendrier éditorial (8 publications / 30 jours)
3. Actions SEO prioritaires
4. Stratégie réseaux sociaux"""
    else:
        return JsonResponse({'error': 'Type d\'analyse invalide'}, status=400)

    try:
        reply = _call_ai(
            api_key=settings.ai_api_key,
            base_url=settings.ai_api_base_url or 'https://api.chatanywhere.tech/v1',
            model=settings.ai_model or 'gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": f"Tu es l'expert en croissance digitale de {settings.site_name}. Réponds en français avec des recommandations concrètes basées sur les données."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1800,
        )
        return JsonResponse({'reply': reply, 'ok': True})
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return JsonResponse({'error': '❌ Clé API invalide.'}, status=200)
        elif e.code == 429:
            return JsonResponse({'error': '⏳ Quota API dépassé.'}, status=200)
        return JsonResponse({'error': f'❌ Erreur API ({e.code})'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=200)
