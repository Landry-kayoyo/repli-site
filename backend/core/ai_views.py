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


def _get_ai_credentials():
    """Return (api_key, base_url, model, ai_enabled) — checks AIConfig first, then SiteSettings."""
    from core.models import AIConfig, SiteSettings

    active_config = AIConfig.objects.filter(is_active=True).first()
    if active_config:
        return active_config.api_key, active_config.api_base_url, active_config.model, True

    s, _ = SiteSettings.objects.get_or_create(pk=1)
    return s.ai_api_key, s.ai_api_base_url, s.ai_model, s.ai_enabled


def _get_ai_settings():
    from core.models import SiteSettings
    s, _ = SiteSettings.objects.get_or_create(pk=1)
    return s


def _get_site_context(settings):
    """Build the system prompt with rich site context."""
    from articles.models import Article
    from projects.models import Project
    from tips.models import Tip
    from comments.models import Comment
    from core.models import PageView, Skill, Experience, Education
    from django.db.models import Sum, Count
    from django.utils import timezone
    from datetime import timedelta

    try:
        articles_count = Article.objects.filter(status='published').count()
        articles_draft = Article.objects.filter(status='draft').count()
        projects_count = Project.objects.filter(status='published').count()
        projects_draft = Project.objects.filter(status='draft').count()
        tips_count = Tip.objects.filter(status='published').count()
        tips_draft = Tip.objects.filter(status='draft').count()
        pending_comments = Comment.objects.filter(is_approved=False).count()
        approved_comments = Comment.objects.filter(is_approved=True).count()

        all_articles = list(
            Article.objects.filter(status='published')
            .order_by('-published_at')
            .values('title', 'slug', 'category__name', 'excerpt', 'views_count', 'published_at')
        )
        all_projects = list(
            Project.objects.filter(status='published')
            .order_by('-created_at')
            .values('title', 'slug', 'description', 'views_count')
        )
        all_tips = list(
            Tip.objects.filter(status='published')
            .order_by('-created_at')
            .values('title', 'slug', 'difficulty', 'excerpt', 'views_count')
        )

        try:
            from articles.models import Category
            categories = list(Category.objects.annotate(cnt=Count('article')).values('name', 'cnt'))
            categories_str = ', '.join([f"{c['name']} ({c['cnt']})" for c in categories]) if categories else 'Aucune'
        except Exception:
            categories_str = 'Non défini'

        try:
            from taggit.models import Tag
            top_tags = list(Tag.objects.annotate(cnt=Count('taggit_taggeditem_items')).order_by('-cnt').values_list('name', flat=True)[:20])
            tags_str = ', '.join(top_tags) if top_tags else 'Aucun'
        except Exception:
            tags_str = 'Non défini'

        try:
            skills = list(Skill.objects.all().order_by('category', 'order').values('name', 'level', 'category'))
            skills_by_cat = {}
            for sk in skills:
                cat = sk['category'] or 'Général'
                skills_by_cat.setdefault(cat, []).append(f"{sk['name']} ({sk['level']}%)")
            skills_str = '\n'.join([f"  [{cat}]: {', '.join(items)}" for cat, items in skills_by_cat.items()]) if skills_by_cat else '  Aucune compétence encore ajoutée'
        except Exception:
            skills_str = '  Non défini'

        try:
            experiences = list(Experience.objects.all().order_by('-start_date').values('title', 'company', 'location', 'is_current', 'description')[:6])
            exp_str = '\n'.join([
                f"  - {e['title']} @ {e['company']}{' (Poste actuel)' if e['is_current'] else ''}"
                for e in experiences
            ]) if experiences else '  Aucune expérience encore ajoutée'
        except Exception:
            exp_str = '  Non défini'

        try:
            educations = list(Education.objects.all().order_by('-start_date').values('degree', 'institution', 'is_current')[:4])
            edu_str = '\n'.join([
                f"  - {e['degree']} — {e['institution']}{' (En cours)' if e['is_current'] else ''}"
                for e in educations
            ]) if educations else '  Aucune formation encore ajoutée'
        except Exception:
            edu_str = '  Non défini'

        try:
            from newsletter.models import Subscriber
            subscribers_total = Subscriber.objects.count()
            subscribers_active = Subscriber.objects.filter(status='active').count()
            subscribers_unsub = Subscriber.objects.filter(status='unsubscribed').count()
        except Exception:
            subscribers_total = subscribers_active = subscribers_unsub = 0

        try:
            from reactions.models import Reaction
            total_reactions = Reaction.objects.count()
            top_reactions = list(
                Reaction.objects.values('emoji').annotate(cnt=Count('id')).order_by('-cnt')[:5]
            )
            reactions_str = ', '.join([f"{r['emoji']} ×{r['cnt']}" for r in top_reactions]) if top_reactions else 'Aucune'
        except Exception:
            total_reactions = 0
            reactions_str = 'Non disponible'

        today = timezone.now().date()
        last_7 = today - timedelta(days=7)
        last_30 = today - timedelta(days=30)

        views_today = PageView.objects.filter(date=today).aggregate(t=Sum('count'))['t'] or 0
        views_7 = PageView.objects.filter(date__gte=last_7).aggregate(t=Sum('count'))['t'] or 0
        views_30 = PageView.objects.filter(date__gte=last_30).aggregate(t=Sum('count'))['t'] or 0

        top_pages = list(
            PageView.objects.filter(date__gte=last_30)
            .values('content_type', 'object_title', 'object_slug')
            .annotate(total=Sum('count'))
            .order_by('-total')[:8]
        )
        top_pages_str = '\n'.join([
            f"  - [{p['content_type']}] {p['object_title']} → {p['total']} vues"
            for p in top_pages
        ]) or '  Aucune donnée de visites encore'

    except Exception as e:
        logger.error(f"AI context error: {e}")
        articles_count = projects_count = tips_count = 0
        articles_draft = projects_draft = tips_draft = 0
        pending_comments = approved_comments = 0
        all_articles = all_projects = all_tips = []
        categories_str = tags_str = skills_str = exp_str = edu_str = 'Non défini'
        subscribers_total = subscribers_active = subscribers_unsub = 0
        total_reactions = 0
        reactions_str = 'Non disponible'
        views_today = views_7 = views_30 = 0
        top_pages_str = '  Aucune donnée'

    custom_prompt = settings.ai_system_prompt.strip() if settings.ai_system_prompt else ''
    if custom_prompt:
        return custom_prompt

    articles_list = '\n'.join([
        f"  • [{a.get('category__name', 'Sans catégorie') or 'Sans catégorie'}] {a['title']} — {a.get('views_count', 0)} vues — /articles/{a['slug']}/"
        for a in all_articles
    ]) or '  Aucun article publié'

    projects_list = '\n'.join([
        f"  • {p['title']} — {p.get('views_count', 0)} vues — /projets/{p['slug']}/"
        for p in all_projects
    ]) or '  Aucun projet publié'

    tips_list = '\n'.join([
        f"  • [{t.get('difficulty', '?')}] {t['title']} — {t.get('views_count', 0)} vues — /astuces/{t['slug']}/"
        for t in all_tips
    ]) or '  Aucune astuce publiée'

    return f"""Tu es l'assistant IA expert et omniscient de {settings.site_name or 'Landry Net'}, le site personnel de {settings.author_name or 'Landry'}.
Tu connais TOUT le contenu du site, toutes les statistiques, toutes les données de la base de données.
Tu es intelligent, analytique et toujours pertinent. Tes réponses sont concrètes, précises et immédiatement utilisables.

RÈGLES DE FORMATAGE ABSOLUES :
- Ne jamais utiliser de syntaxe Markdown comme **, *, ##, ###, -, __, etc.
- Utilise des emojis pour structurer et rendre la lecture agréable (ex: 📌 pour les titres, ✅ pour les points)
- Utilise des sauts de ligne pour séparer les sections
- Pour les listes, utilise des tirets simples avec des emojis ou des numéros
- Pour le code, fournis-le directement sans backticks
- Tes réponses doivent être agréables à lire, bien aérées, sans caractères spéciaux de formatage

PROFIL COMPLET DE L'AUTEUR
Nom: {settings.author_name}
Titre: {settings.author_job_title}
Bio: {(settings.author_bio or '')[:500]}
Localisation: {settings.author_location or 'Non défini'}

COMPÉTENCES TECHNIQUES (depuis la BDD)
{skills_str}

EXPÉRIENCES PROFESSIONNELLES (depuis la BDD)
{exp_str}

FORMATIONS (depuis la BDD)
{edu_str}

INVENTAIRE COMPLET DU CONTENU
Publié: {articles_count} articles | {projects_count} projets | {tips_count} astuces
En brouillon: {articles_draft} articles | {projects_draft} projets | {tips_draft} astuces
Commentaires: {approved_comments} approuvés | {pending_comments} en attente de modération
Réactions totales: {total_reactions} ({reactions_str})

Catégories d'articles: {categories_str}
Tags populaires: {tags_str}

TOUS LES ARTICLES PUBLIÉS
{articles_list}

TOUS LES PROJETS PUBLIÉS
{projects_list}

TOUTES LES ASTUCES PUBLIÉES
{tips_list}

NEWSLETTER
Abonnés total: {subscribers_total} | Actifs: {subscribers_active} | Désabonnés: {subscribers_unsub}

ANALYTIQUES SITE
Vues aujourd'hui: {views_today} | 7 jours: {views_7} | 30 jours: {views_30}

Top pages (30 jours):
{top_pages_str}

PARAMÈTRES SITE
Nom: {settings.site_name} | Tagline: {settings.tagline}
Description: {settings.description}

TES MISSIONS

1. CRÉATION DE CONTENU PROFESSIONNEL (article/projet/astuce) :
   Quand on te demande de créer du contenu, génère TOUT le contenu immédiatement, prêt à publier.
   Analyse d'abord les articles existants pour éviter les doublons et t'inspirer du style.

   FORMAT OBLIGATOIRE POUR UN ARTICLE :
   Titre : [titre accrocheur, max 80 chars, sans guillemets]
   Sous-titre : [sous-titre descriptif, max 120 chars]
   Extrait : [2-3 phrases percutantes, max 200 chars, pour le SEO]
   Contenu HTML :
   [HTML COMPLET et professionnel entre balises, 1000-2000 mots minimum]
   Tags : [tag1, tag2, tag3]

   RÈGLES HTML POUR LE CONTENU :
   - Commence par une introduction engageante de 2-3 paragraphes (<p>)
   - Utilise des <h2> pour les sections principales, <h3> pour les sous-sections
   - Inclure au moins 4-6 sections bien développées avec vrais exemples pratiques
   - Pour le code : <pre><code class="language-python"> ... </code></pre>
   - Pour les listes : <ul><li>...</li></ul> ou <ol><li>...</li></ol>
   - Pour les points importants : <blockquote> ou <strong>
   - Termine par une conclusion avec appel à l'action
   - Pas de balises <html>, <body>, <head> — seulement le contenu

   FORMAT POUR UNE ASTUCE :
   Titre : [titre pratique]
   Extrait : [problème + solution en 1 phrase]
   Difficulté : [débutant / intermédiaire / avancé]
   Contenu HTML : [explication claire + exemple de code si nécessaire + résultat attendu]

   FORMAT POUR UN PROJET :
   Titre : [nom du projet]
   Sous-titre : [tagline du projet]
   Description courte : [1-2 phrases pour le SEO]
   Contenu HTML : [présentation + technologies + fonctionnalités + captures d'écran suggérées]
   Technologies : [tech1, tech2, tech3]

2. MODIFIER LES PARAMÈTRES DU SITE :
   Si on te demande de modifier la description, le tagline, etc., indique :
   "Pour modifier [X], allez dans Admin → Paramètres du site → [section]"
   et fournis le nouveau texte prêt à copier.

3. ANALYSE INTELLIGENTE DU SITE :
   - Identifie les lacunes de contenu par rapport aux compétences déclarées
   - Évite absolument les sujets déjà couverts (vérifie la liste ci-dessus)
   - Analyse les pages les plus vues et suggère d'en créer du contenu similaire
   - Propose des titres SEO-optimisés et des angles originaux

4. SEO AVANCÉ :
   - Meta-title : 50-60 chars, inclure le mot-clé principal en premier
   - Meta-description : 140-160 chars, inclure un appel à l'action
   - Excerpt : 150-200 chars, accrocheur et informatif
   - Slug : kebab-case, sans accents, max 60 chars
   - Densité de mots-clés : 1-2% dans le contenu

5. NEWSLETTER :
   - Pour rédiger une newsletter : fournis TOUT le contenu HTML de l'email, professionnel et complet
   - Structure : salutation personnalisée + actualités du site + article vedette + CTA
   - Ton : chaleureux, professionnel, personnel

6. ADMINISTRATION :
   - Compétences: /admin/core/skill/add/
   - Expériences: /admin/core/experience/add/
   - Paramètres: /admin/core/sitesettings/1/change/
   - Commentaires en attente: /admin/comments/comment/?is_approved__exact=0
   - Abonnés newsletter: /admin/newsletter/subscriber/

RÈGLES IMPÉRATIVES
- Réponds TOUJOURS en français
- JAMAIS de Markdown (**, ##, *, _) — utilise des emojis et sauts de ligne à la place
- Pour la création de contenu : fournis ABSOLUMENT TOUT le contenu, complet, prêt à copier-coller et publier immédiatement sans aucune modification
- Le contenu doit être de qualité professionnelle : informatif, bien structuré, original, avec des exemples concrets
- Pour les analyses : base-toi UNIQUEMENT sur les VRAIES données ci-dessus — ne jamais inventer de chiffres
- Sois spécifique, concret et immédiatement actionnable
- Si on te demande "quels articles existent", cite les vrais articles de la liste
- Longueur de réponse : suffisamment longue pour être utile, mais sans rembourrage inutile"""


def _call_ai(api_key, base_url, model, messages, max_tokens=2000):
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
    with urllib.request.urlopen(req, timeout=45) as resp:
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

    api_key, base_url, model, ai_enabled = _get_ai_credentials()

    if not ai_enabled:
        return JsonResponse({'error': "L'assistant IA n'est pas activé. Configurez-le dans Admin → Paramètres du site → Configuration IA."}, status=403)
    if not api_key:
        return JsonResponse({'error': "Clé API manquante. Allez dans Admin → Paramètres du site → Configuration IA pour ajouter votre clé API."}, status=403)

    settings = _get_ai_settings()
    system_prompt = _get_site_context(settings)

    if context_type and context_type != 'general' and context_data:
        context_msg = f"\n\nFORMULAIRE EN COURS ({context_type.upper()})\n"
        for k, v in context_data.items():
            if v:
                context_msg += f"• {k}: {str(v)[:300]}\n"
        system_prompt += context_msg

    messages = [{"role": "system", "content": system_prompt}]
    for msg in history[-20:]:
        if msg.get('role') in ('user', 'assistant') and msg.get('content'):
            messages.append({"role": msg['role'], "content": msg['content']})
    messages.append({"role": "user", "content": user_message})

    try:
        reply = _call_ai(
            api_key=api_key,
            base_url=base_url or 'https://api.chatanywhere.tech/v1',
            model=model or 'gpt-3.5-turbo',
            messages=messages,
            max_tokens=2000,
        )
        return JsonResponse({'reply': reply, 'ok': True})
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8', errors='ignore')
        logger.error(f"AI API HTTP error: {e.code} — {error_body}")
        if e.code == 401:
            return JsonResponse({'error': 'Clé API invalide. Vérifiez votre clé dans Paramètres ou Configurations IA.'}, status=200)
        elif e.code == 429:
            return JsonResponse({'error': 'Quota API dépassé. Réessayez plus tard ou activez une autre configuration IA.'}, status=200)
        else:
            return JsonResponse({'error': f'Erreur API ({e.code}). Vérifiez l\'URL de base et la clé API.'}, status=200)
    except urllib.error.URLError as e:
        logger.error(f"AI API URL error: {e}")
        return JsonResponse({'error': "Impossible de contacter l'API. Vérifiez l'URL de base dans les paramètres."}, status=200)
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
        action = body.get('action', '')
        data = body.get('data', {})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    prompts = {
        'title': f"Propose 5 titres accrocheurs et SEO-friendly pour: '{data.get('topic', '')}'. Numérotés 1 à 5, style percutant. Réponds sans Markdown (**, ##). Utilise des emojis et sauts de ligne.",
        'seo': f"Pour:\nTitre: {data.get('title', '')}\nDescription: {data.get('excerpt', '')}\nDonne:\n1. Meta-title (max 60 chars)\n2. Meta-description (max 160 chars)\nPrêts à copier. Sans Markdown.",
        'icon': f"Propose 8 noms d'icônes Bootstrap Icons pour: '{data.get('name', '')}'. Format: bi-nom-icone. Une par ligne avec description courte.",
        'excerpt': f"Écris une description courte (2 phrases max, 180 chars) pour:\nTitre: {data.get('title', '')}\nContenu: {data.get('content', '')[:300]}. Sans Markdown.",
        'tags': f"Propose 8 tags pertinents (mots-clés courts) pour:\nTitre: {data.get('title', '')}\nContenu: {data.get('content', '')[:300]}\nUn tag par ligne, en minuscules, sans #.",
        'improve': f"Améliore ce texte en le rendant plus percutant, clair et SEO-friendly (garde la même longueur). Sans Markdown:\n\n{data.get('content', '')[:500]}",
        'structure': f"Propose un plan détaillé pour un article sur: '{data.get('topic', '')}'. Utilise des emojis et numérotation. Sans Markdown (##, **, *).",
        'full_content': f"Génère un article COMPLET en HTML pour:\nTitre: {data.get('title', '')}\nSujet: {data.get('topic', '')}\n\nFournis: contenu HTML complet (800-1200 mots), structuré avec h2/h3/p/ul/code. Prêt à coller dans l'éditeur.",
        'auto_excerpt': (
            f"À partir de ce contenu, génère un extrait/description courte de 2 phrases maximum (180 caractères max), "
            f"percutante et optimisée SEO. Réponds UNIQUEMENT avec l'extrait, sans guillemets, sans explication.\n\n"
            f"Titre: {data.get('title', '')}\nContenu: {data.get('content', '')[:1200]}"
        ),
        'cover_prompt': (
            f"Pour un contenu intitulé \"{data.get('title', '')}\" (type: {data.get('content_type', 'article')}), "
            f"décris l'image de couverture idéale en 3 phrases (sujet, style, couleurs, ambiance). "
            f"Puis fournis un prompt optimisé pour Midjourney/DALL-E en anglais (1 ligne, après «Prompt IA :»). "
            f"Sans Markdown."
        ),
    }

    if action not in prompts:
        return JsonResponse({'error': 'Action invalide'}, status=400)

    api_key, base_url, model, ai_enabled = _get_ai_credentials()

    if not ai_enabled or not api_key:
        return JsonResponse({'error': "IA non configurée — allez dans Paramètres du site → Configuration IA"}, status=403)

    settings = _get_ai_settings()
    try:
        reply = _call_ai(
            api_key=api_key,
            base_url=base_url or 'https://api.chatanywhere.tech/v1',
            model=model or 'gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": f"Tu es l'assistant expert de {settings.site_name or 'Landry Net'}. Réponds en français, sois concis, direct et fais du contenu de haute qualité. N'utilise JAMAIS de Markdown (**, ##, *, _). Utilise des emojis et sauts de ligne à la place."},
                {"role": "user", "content": prompts[action]},
            ],
            max_tokens=1200,
        )
        return JsonResponse({'reply': reply, 'ok': True})
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return JsonResponse({'error': 'Clé API invalide.'}, status=200)
        elif e.code == 429:
            return JsonResponse({'error': 'Quota API dépassé.'}, status=200)
        return JsonResponse({'error': f'Erreur API ({e.code})'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=200)


@staff_member_required
@csrf_exempt
@require_POST
def ai_generate_content(request):
    """Génère le contenu HTML complet pour CKEditor à partir du titre."""
    try:
        body = json.loads(request.body)
        title = body.get('title', '').strip()
        content_type = body.get('content_type', 'article')
        subtitle = body.get('subtitle', '').strip()
        excerpt = body.get('excerpt', '').strip()
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not title or len(title) < 4:
        return JsonResponse({'error': 'Titre requis (minimum 4 caractères)'}, status=400)

    api_key, base_url, model, ai_enabled = _get_ai_credentials()
    if not ai_enabled or not api_key:
        return JsonResponse({'error': 'IA non configurée'}, status=403)

    settings = _get_ai_settings()

    type_specs = {
        'article': '800-1400 mots — article de blog technique complet',
        'project': '500-800 mots — présentation de projet avec résultats et défis',
        'tip':     '300-600 mots — astuce/tutoriel pratique étape par étape',
    }
    spec = type_specs.get(content_type, type_specs['article'])

    extra = ''
    if subtitle:
        extra += f'\nSous-titre : {subtitle}'
    if excerpt:
        extra += f'\nContexte : {excerpt}'

    prompt = (
        f'Écris un {spec} en HTML pour :\n'
        f'Titre : "{title}"{extra}\n\n'
        f'RÈGLES :\n'
        f'- HTML propre uniquement : <h2>, <h3>, <p>, <ul>, <ol>, <li>, <strong>, <em>, <blockquote>, <pre><code>\n'
        f'- Introduction engageante (1-2 paragraphes)\n'
        f'- 4-6 sections bien développées avec exemples concrets\n'
        f'- Code : <pre><code class="language-...">...</code></pre>\n'
        f'- Conclusion avec appel à l\'action\n'
        f'- JAMAIS de <html>, <body>, <head>\n'
        f'- JAMAIS de Markdown (**, ##, *)\n'
        f'- Réponds UNIQUEMENT avec le HTML, rien d\'autre'
    )

    try:
        reply = _call_ai(
            api_key=api_key,
            base_url=base_url or 'https://api.chatanywhere.tech/v1',
            model=model or 'gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": f"Tu es un expert rédacteur web pour {settings.site_name or 'Landry Net'}. Tu génères du contenu HTML professionnel de haute qualité. Réponds UNIQUEMENT avec le HTML, sans aucun texte avant ou après."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=2500,
        )
        clean = reply.strip()
        for prefix in ('```html\n', '```html', '```\n', '```'):
            if clean.startswith(prefix):
                clean = clean[len(prefix):]
                break
        if clean.endswith('```'):
            clean = clean[:-3]
        return JsonResponse({'content': clean.strip(), 'ok': True})
    except urllib.error.HTTPError as e:
        code_map = {401: 'Clé API invalide.', 429: 'Quota API dépassé.'}
        return JsonResponse({'error': code_map.get(e.code, f'Erreur API ({e.code})')}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=200)


@staff_member_required
@csrf_exempt
@require_POST
def ai_optimize_content(request):
    """Analyse le contenu existant et retourne des suggestions d'optimisation SEO + lisibilité."""
    import re as _re
    try:
        body = json.loads(request.body)
        content = body.get('content', '').strip()
        title = body.get('title', '').strip()
        content_type = body.get('content_type', 'article')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not content or len(content) < 80:
        return JsonResponse({'error': 'Contenu trop court (minimum 80 caractères)'}, status=400)

    api_key, base_url, model, ai_enabled = _get_ai_credentials()
    if not ai_enabled or not api_key:
        return JsonResponse({'error': 'IA non configurée'}, status=403)

    text_only = _re.sub(r'<[^>]+>', ' ', content)
    word_count = len(text_only.split())

    prompt = (
        f'Analyse ce contenu et retourne UNIQUEMENT un JSON valide (sans markdown, sans backticks) :\n\n'
        f'Titre : "{title}"\nType : {content_type}\nMots : {word_count}\n'
        f'Contenu (extrait) : {content[:2000]}\n\n'
        f'Format JSON attendu :\n'
        f'{{\n'
        f'  "seo_score": <0-100>,\n'
        f'  "readability_score": <0-100>,\n'
        f'  "strengths": ["point fort 1", "point fort 2"],\n'
        f'  "improvements": [\n'
        f'    {{"priority": "haute", "suggestion": "...", "reason": "..."}}\n'
        f'  ],\n'
        f'  "missing_keywords": ["mot-clé 1", "mot-clé 2"],\n'
        f'  "structure_issues": ["problème 1"]\n'
        f'}}'
    )

    try:
        reply = _call_ai(
            api_key=api_key,
            base_url=base_url or 'https://api.chatanywhere.tech/v1',
            model=model or 'gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": "Tu es un expert SEO et rédaction web. Tu réponds UNIQUEMENT en JSON valide, sans backticks, sans texte autour."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=900,
        )
        clean = reply.strip()
        if clean.startswith('```'):
            clean = clean.split('\n', 1)[1] if '\n' in clean else clean[3:]
        if clean.endswith('```'):
            clean = clean.rsplit('```', 1)[0]
        data = json.loads(clean.strip())
        data['ok'] = True
        data['word_count'] = word_count
        return JsonResponse(data)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Réponse IA invalide, réessayez.'}, status=200)
    except urllib.error.HTTPError as e:
        code_map = {401: 'Clé API invalide.', 429: 'Quota API dépassé.'}
        return JsonResponse({'error': code_map.get(e.code, f'Erreur API ({e.code})')}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=200)


@staff_member_required
@csrf_exempt
@require_POST
def ai_internal_links(request):
    """Suggère des liens internes pertinents basés sur le contenu en cours de rédaction."""
    import re as _re
    try:
        body = json.loads(request.body)
        title = body.get('title', '').strip()
        content = body.get('content', '').strip()
        content_type = body.get('content_type', 'article')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not title:
        return JsonResponse({'error': 'Titre requis'}, status=400)

    api_key, base_url, model, ai_enabled = _get_ai_credentials()
    if not ai_enabled or not api_key:
        return JsonResponse({'error': 'IA non configurée'}, status=403)

    from articles.models import Article
    from projects.models import Project
    from tips.models import Tip

    try:
        all_content = []
        for a in Article.objects.filter(status='published').values('title', 'slug', 'excerpt')[:25]:
            all_content.append({'type': 'article', 'title': a['title'], 'url': f"/articles/{a['slug']}/", 'hint': (a.get('excerpt') or '')[:60]})
        for p in Project.objects.filter(status='published').values('title', 'slug', 'description')[:20]:
            all_content.append({'type': 'projet', 'title': p['title'], 'url': f"/projets/{p['slug']}/", 'hint': (p.get('description') or '')[:60]})
        for t in Tip.objects.filter(status='published').values('title', 'slug', 'excerpt')[:20]:
            all_content.append({'type': 'astuce', 'title': t['title'], 'url': f"/astuces/{t['slug']}/", 'hint': (t.get('excerpt') or '')[:60]})
    except Exception as e:
        return JsonResponse({'error': f'Erreur DB : {str(e)}'}, status=200)

    if not all_content:
        return JsonResponse({'links': [], 'ok': True, 'message': 'Aucun contenu publié trouvé sur le site.'})

    content_list = '\n'.join([f"- [{c['type']}] {c['title']} → {c['url']}" for c in all_content])
    text_excerpt = _re.sub(r'<[^>]+>', ' ', content)[:400] if content else ''

    prompt = (
        f'Pour ce contenu en cours de rédaction :\n'
        f'Titre : "{title}"\nExtrait : {text_excerpt}\n\n'
        f'Contenu existant sur le site :\n{content_list}\n\n'
        f'Sélectionne 3 à 5 contenus les plus pertinents à lier dans cet article.\n'
        f'Retourne UNIQUEMENT ce JSON (sans markdown) :\n'
        f'[{{"title":"...","url":"...","type":"...","reason":"Pourquoi ce lien enrichit le lecteur (1 phrase)"}}]'
    )

    try:
        reply = _call_ai(
            api_key=api_key,
            base_url=base_url or 'https://api.chatanywhere.tech/v1',
            model=model or 'gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": "Tu es un expert SEO en liens internes. Tu réponds UNIQUEMENT en JSON valide."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=600,
        )
        clean = reply.strip()
        if clean.startswith('```'):
            clean = clean.split('\n', 1)[1] if '\n' in clean else clean[3:]
        if clean.endswith('```'):
            clean = clean.rsplit('```', 1)[0]
        links = json.loads(clean.strip())
        return JsonResponse({'links': links, 'ok': True})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Réponse IA invalide.', 'links': []}, status=200)
    except urllib.error.HTTPError as e:
        code_map = {401: 'Clé API invalide.', 429: 'Quota API dépassé.'}
        return JsonResponse({'error': code_map.get(e.code, f'Erreur API ({e.code})')}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=200)


@staff_member_required
@csrf_exempt
@require_POST
def ai_check_duplicate(request):
    """Vérifie si un contenu similaire existe déjà dans la base de données."""
    import functools
    import operator as _op
    try:
        body = json.loads(request.body)
        title = body.get('title', '').strip()
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not title or len(title) < 4:
        return JsonResponse({'duplicates': [], 'ok': True, 'count': 0})

    from articles.models import Article
    from projects.models import Project
    from tips.models import Tip
    from django.db.models import Q

    # Extract meaningful words (>3 chars)
    words = [w.lower() for w in title.split() if len(w) > 3]
    if not words:
        return JsonResponse({'duplicates': [], 'ok': True, 'count': 0})

    try:
        q = functools.reduce(_op.or_, [Q(title__icontains=w) for w in words])
        duplicates = []
        for a in Article.objects.filter(q)[:6]:
            duplicates.append({'type': 'Article', 'title': a.title, 'url': f'/articles/{a.slug}/', 'status': a.status})
        for p in Project.objects.filter(q)[:4]:
            duplicates.append({'type': 'Projet', 'title': p.title, 'url': f'/projets/{p.slug}/', 'status': p.status})
        for t in Tip.objects.filter(q)[:4]:
            duplicates.append({'type': 'Astuce', 'title': t.title, 'url': f'/astuces/{t.slug}/', 'status': t.status})
        return JsonResponse({'duplicates': duplicates[:8], 'ok': True, 'count': len(duplicates)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=200)


@staff_member_required
@csrf_exempt
@require_POST
def ai_inline_suggest(request):
    """Endpoint suggestions IA en temps réel pour les formulaires admin (article/projet/astuce)."""
    try:
        body = json.loads(request.body)
        title = body.get('title', '').strip()
        content_type = body.get('content_type', 'article')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not title or len(title) < 4:
        return JsonResponse({'error': 'Titre trop court'}, status=400)

    api_key, base_url, model, ai_enabled = _get_ai_credentials()
    if not ai_enabled or not api_key:
        return JsonResponse({'error': 'IA non configurée — allez dans Paramètres du site → Configuration IA'}, status=403)

    settings = _get_ai_settings()

    type_labels = {
        'article': 'article de blog tech',
        'project': 'projet technique',
        'tip': 'astuce / tutoriel pratique',
    }
    type_label = type_labels.get(content_type, 'article de blog')

    excerpt_key = 'excerpt' if content_type in ('article', 'tip') else 'description'
    extra_field = ''
    if content_type == 'tip':
        extra_field = '\n- difficulty: exactement une de ces valeurs: "débutant", "intermédiaire" ou "avancé"'

    prompt = (
        f'Pour un {type_label} intitulé : "{title}"\n\n'
        f'Génère un JSON strict avec exactement ces clés :\n'
        f'- subtitle: sous-titre accrocheur (max 120 caractères)\n'
        f'- {excerpt_key}: description courte percutante (2 phrases, max 180 caractères)\n'
        f'- tags: tableau JSON de 6 tags courts en minuscules sans accents (ex: ["python","django","api"])\n'
        f'- meta_title: titre SEO (max 60 caractères, mot-clé principal en premier)\n'
        f'- meta_description: description SEO avec appel à l\'action (max 160 caractères)'
        f'{extra_field}\n\n'
        f'Réponds UNIQUEMENT avec le JSON brut. Pas de ```json, pas d\'explication, juste le JSON.'
    )

    try:
        reply = _call_ai(
            api_key=api_key,
            base_url=base_url or 'https://api.chatanywhere.tech/v1',
            model=model or 'gpt-3.5-turbo',
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"Tu es un expert SEO et rédacteur pour {settings.site_name or 'Landry Net'}. "
                        "Tu réponds UNIQUEMENT en JSON valide, sans aucun texte autour, sans backticks, sans commentaire."
                    )
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=450,
        )

        clean = reply.strip()
        if clean.startswith('```'):
            clean = clean.split('\n', 1)[1] if '\n' in clean else clean[3:]
        if clean.endswith('```'):
            clean = clean.rsplit('```', 1)[0]
        clean = clean.strip()

        data = json.loads(clean)
        data['ok'] = True
        data['content_type'] = content_type
        data['excerpt_key'] = excerpt_key
        return JsonResponse(data)

    except json.JSONDecodeError as e:
        logger.error(f"ai_inline_suggest JSON parse error: {e} — reply: {reply[:300]}")
        return JsonResponse({'error': 'Réponse IA invalide, réessayez.'}, status=200)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return JsonResponse({'error': 'Clé API invalide.'}, status=200)
        elif e.code == 429:
            return JsonResponse({'error': 'Quota API dépassé. Réessayez dans quelques secondes.'}, status=200)
        return JsonResponse({'error': f'Erreur API ({e.code})'}, status=200)
    except urllib.error.URLError:
        return JsonResponse({'error': "Impossible de contacter l'API IA."}, status=200)
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

    api_key, base_url, model, ai_enabled = _get_ai_credentials()
    if not ai_enabled or not api_key:
        return JsonResponse({'error': "IA non configurée"}, status=403)

    settings = _get_ai_settings()

    from core.models import PageView
    from django.db.models import Sum, Count
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
        articles_data = list(Article.objects.filter(status='published').values('title', 'views_count', 'published_at').order_by('-views_count')[:20])
        projects_titles = list(Project.objects.filter(status='published').values_list('title', flat=True)[:10])
        tips_titles = list(Tip.objects.filter(status='published').values_list('title', flat=True)[:10])

        try:
            from newsletter.models import Subscriber
            active_subs = Subscriber.objects.filter(status='active').count()
        except Exception:
            active_subs = 0

        top_str = '\n'.join([f"- [{p['content_type']}] {p['object_title']}: {p['total']} vues" for p in top_pages]) or 'Aucune donnée'
        articles_str = '\n'.join([f"- {a['title']} ({a.get('views_count', 0)} vues)" for a in articles_data]) or 'Aucun'
    except Exception as e:
        top_str = articles_str = 'Erreur de récupération'
        projects_titles = tips_titles = []
        active_subs = 0

    no_markdown = "Réponds sans Markdown (**, ##, *, _). Utilise des emojis, des numéros et des sauts de ligne pour structurer. Réponds en français."

    if analysis_type == 'content_gaps':
        prompt = f"""Analyse mon contenu et identifie les lacunes CONCRÈTES à combler.

Articles existants:
{articles_str}

Projets: {', '.join(projects_titles[:5]) or 'Aucun'}
Astuces: {', '.join(tips_titles[:5]) or 'Aucune'}

Top pages (30j):
{top_str}

Donne-moi:
1. 5 sujets d'articles qui MANQUENT et que mon audience veut
2. 3 types de projets qui compléteraient le portfolio
3. 3 astuces très demandées à écrire
4. Pour chaque suggestion: titre précis + pourquoi c'est pertinent

{no_markdown}"""

    elif analysis_type == 'seo_audit':
        prompt = f"""Fais un audit SEO concret de {settings.site_name}.

Contenu: {len(articles_data)} articles, {len(projects_titles)} projets, {len(tips_titles)} astuces
Newsletter: {active_subs} abonnés actifs
Top pages: {top_str}

Donne:
1. 3 forces SEO actuelles
2. 5 améliorations prioritaires (avec actions concrètes)
3. 3 stratégies de maillage interne
4. 2 opportunités de contenu evergreen

{no_markdown}"""

    elif analysis_type == 'growth_plan':
        prompt = f"""Plan de croissance 30 jours pour {settings.site_name}.

Situation: {len(articles_data)} articles, {len(projects_titles)} projets, {len(tips_titles)} astuces, {active_subs} abonnés newsletter
Top pages: {top_str}

Plan détaillé:
1. Objectifs SMART réalistes (vues, publications, abonnés)
2. Calendrier éditorial sur 30 jours (8-10 publications)
3. 5 actions SEO prioritaires avec délais
4. 3 stratégies d'acquisition de trafic

{no_markdown}"""
    else:
        return JsonResponse({'error': 'Type invalide'}, status=400)

    try:
        reply = _call_ai(
            api_key=api_key,
            base_url=base_url or 'https://api.chatanywhere.tech/v1',
            model=model or 'gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": f"Tu es l'assistant expert de {settings.site_name or 'Landry Net'}. {no_markdown}"},
                {"role": "user", "content": prompt},
            ],
            max_tokens=2000,
        )
        return JsonResponse({'reply': reply, 'ok': True})
    except Exception as e:
        logger.error(f"AI analyze error: {e}")
        return JsonResponse({'error': str(e)}, status=200)


@staff_member_required
@csrf_exempt
@require_POST
def ai_publish(request):
    """Publish AI-generated content directly to the site."""
    try:
        body = json.loads(request.body)
        content_type = body.get('type', 'article')
        title = body.get('title', '').strip()
        content = body.get('content', '').strip()
        excerpt = body.get('excerpt', '').strip()
        pub_status = body.get('status', 'draft')
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not title:
        return JsonResponse({'error': 'Le titre est requis'}, status=400)
    if not content:
        return JsonResponse({'error': 'Le contenu est requis'}, status=400)

    from django.utils.text import slugify
    import uuid

    def make_unique_slug(model_class, base_slug):
        slug = base_slug or str(uuid.uuid4())[:8]
        counter = 1
        temp = slug
        while model_class.objects.filter(slug=temp).exists():
            temp = f"{slug}-{counter}"
            counter += 1
        return temp

    author_id = body.get('author_id')
    try:
        author_id = int(author_id) if author_id else None
    except (ValueError, TypeError):
        author_id = None
    if not author_id:
        author_id = request.user.id

    try:
        if content_type == 'article':
            from articles.models import Article
            slug = make_unique_slug(Article, slugify(title))
            obj = Article.objects.create(
                title=title,
                content=content,
                excerpt=excerpt[:200] if excerpt else '',
                status=pub_status,
                slug=slug,
                author_id=author_id,
            )
            admin_url = f'/admin/articles/article/{obj.pk}/change/'
            public_url = f'/articles/{obj.slug}/'

        elif content_type == 'project':
            from projects.models import Project
            slug = make_unique_slug(Project, slugify(title))
            obj = Project.objects.create(
                title=title,
                description=excerpt[:300] if excerpt else content[:300],
                status=pub_status,
                slug=slug,
                author_id=author_id,
            )
            admin_url = f'/admin/projects/project/{obj.pk}/change/'
            public_url = f'/projets/{obj.slug}/'

        elif content_type == 'tip':
            from tips.models import Tip
            slug = make_unique_slug(Tip, slugify(title))
            obj = Tip.objects.create(
                title=title,
                content=content,
                excerpt=excerpt[:200] if excerpt else '',
                status=pub_status,
                slug=slug,
                author_id=author_id,
            )
            admin_url = f'/admin/tips/tip/{obj.pk}/change/'
            public_url = f'/astuces/{obj.slug}/'

        else:
            return JsonResponse({'error': 'Type invalide. Utilisez: article, project, tip'}, status=400)

        return JsonResponse({
            'ok': True,
            'id': obj.pk,
            'admin_url': admin_url,
            'public_url': public_url,
            'status': pub_status,
            'type': content_type,
            'title': title,
        })
    except Exception as e:
        logger.error(f"ai_publish error: {e}")
        return JsonResponse({'error': f'Erreur lors de la publication: {str(e)}'}, status=500)


@staff_member_required
def get_admin_users(request):
    """Return list of staff users for author selector."""
    from django.contrib.auth.models import User
    users = list(
        User.objects.filter(is_staff=True).order_by('username')
        .values('id', 'username', 'first_name', 'last_name')
    )
    for u in users:
        u['display'] = (f"{u['first_name']} {u['last_name']}".strip()) or u['username']
    return JsonResponse({'users': users})


@staff_member_required
def smart_notifications(request):
    """Rule-based + AI smart notifications for admin bell."""
    from django.contrib.auth.models import User
    from articles.models import Article
    from projects.models import Project
    from tips.models import Tip
    from comments.models import Comment
    from django.utils import timezone
    from datetime import timedelta

    notifications = []

    # 1. Pending comments
    try:
        pending = Comment.objects.filter(is_approved=False).count()
        recent_pending = Comment.objects.filter(is_approved=False).order_by('-created_at')[:3]
        for c in recent_pending:
            notifications.append({
                'type': 'comment',
                'icon': '💬',
                'level': 'warning',
                'title': 'Commentaire en attente de modération',
                'detail': f"{c.author_name or 'Anonyme'} — {(c.content or '')[:50]}...",
                'url': f'/admin/comments/comment/{c.id}/change/',
                'time': c.created_at.strftime('%d/%m %H:%M') if c.created_at else '',
            })
    except Exception:
        pass

    # 2. Published articles missing SEO fields
    try:
        no_seo = Article.objects.filter(status='published').filter(
            meta_description=''
        )[:3]
        for a in no_seo:
            notifications.append({
                'type': 'seo',
                'icon': '🔍',
                'level': 'info',
                'title': f'SEO manquant : {a.title[:40]}',
                'detail': 'Meta description vide — ajoutez-en une pour améliorer le référencement',
                'url': f'/admin/articles/article/{a.id}/change/',
                'time': '',
            })
    except Exception:
        pass

    # 3. Published articles missing cover image
    try:
        no_cover = Article.objects.filter(status='published', cover_image='')[:2]
        for a in no_cover:
            notifications.append({
                'type': 'image',
                'icon': '🖼️',
                'level': 'info',
                'title': f'Image manquante : {a.title[:40]}',
                'detail': 'Ajoutez une image de couverture pour capter l\'attention',
                'url': f'/admin/articles/article/{a.id}/change/',
                'time': '',
            })
    except Exception:
        pass

    # 4. Articles with very short content (< 150 chars in content)
    try:
        short_articles = []
        for a in Article.objects.filter(status='published').only('id', 'title', 'content'):
            clean = (a.content or '').replace('<', ' <').replace('>', '> ')
            import re
            text = re.sub(r'<[^>]+>', '', clean).strip()
            if len(text) < 200:
                short_articles.append(a)
        for a in short_articles[:2]:
            notifications.append({
                'type': 'quality',
                'icon': '📝',
                'level': 'warning',
                'title': f'Contenu trop court : {a.title[:40]}',
                'detail': 'Cet article a moins de 200 mots — enrichissez-le pour le SEO',
                'url': f'/admin/articles/article/{a.id}/change/',
                'time': '',
            })
    except Exception:
        pass

    # 5. Old drafts (> 7 days not updated)
    try:
        old_draft_threshold = timezone.now() - timedelta(days=7)
        old_drafts = Article.objects.filter(
            status='draft', updated_at__lt=old_draft_threshold
        ).order_by('updated_at')[:2]
        for a in old_drafts:
            days = (timezone.now() - a.updated_at).days
            notifications.append({
                'type': 'draft',
                'icon': '📋',
                'level': 'info',
                'title': f'Brouillon abandonné : {a.title[:35]}',
                'detail': f'Non modifié depuis {days} jours — terminez ou supprimez-le',
                'url': f'/admin/articles/article/{a.id}/change/',
                'time': a.updated_at.strftime('%d/%m') if a.updated_at else '',
            })
    except Exception:
        pass

    # 6. Site settings not filled
    try:
        from core.models import SiteSettings
        s = SiteSettings.objects.first()
        if s:
            if not s.meta_keywords:
                notifications.append({
                    'type': 'seo', 'icon': '🏷️', 'level': 'info',
                    'title': 'Mots-clés SEO non définis',
                    'detail': 'Ajoutez des mots-clés dans Admin → Paramètres du site',
                    'url': '/admin/core/sitesettings/1/change/', 'time': '',
                })
            if not s.author_job_title:
                notifications.append({
                    'type': 'profile', 'icon': '👤', 'level': 'info',
                    'title': 'Titre professionnel manquant',
                    'detail': 'Ajoutez votre titre (ex: Développeur Full Stack) dans les paramètres',
                    'url': '/admin/core/sitesettings/1/change/', 'time': '',
                })
            if not s.email_host_user:
                notifications.append({
                    'type': 'email', 'icon': '✉️', 'level': 'warning',
                    'title': 'Email non configuré',
                    'detail': 'Configurez votre Gmail pour recevoir les messages de contact',
                    'url': '/admin-ai/diagnostic/', 'time': '',
                })
    except Exception:
        pass

    return JsonResponse({
        'count': len(notifications),
        'notifications': notifications,
    })
