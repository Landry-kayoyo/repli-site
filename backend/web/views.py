from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q
import json

from core.models import SiteSettings, Skill, Experience, Education, Technology
from articles.models import Article, Category as ArticleCategory
from projects.models import Project, ProjectCategory
from tips.models import Tip, TipCategory
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType


def get_settings():
    obj, _ = SiteSettings.objects.get_or_create(pk=1)
    return obj


def home(request):
    settings = get_settings()
    articles = Article.objects.filter(status='published').select_related('category')[:3]
    projects = Project.objects.filter(status='published').select_related('category')[:3]
    tips = Tip.objects.filter(status='published').select_related('category')[:3]
    technologies = Technology.objects.all()
    from newsletter.models import Subscriber
    from reactions.models import Reaction
    from comments.models import Comment
    from django.db.models import Count
    articles_count = Article.objects.filter(status='published').count()
    projects_count = Project.objects.filter(status='published').count()
    tips_count = Tip.objects.filter(status='published').count()
    stats = {
        'articles_count': articles_count,
        'projects_count': projects_count,
        'tips_count': tips_count,
        'subscribers_count': Subscriber.objects.filter(status='active').count(),
        'reactions_count': Reaction.objects.count(),
        'comments_count': Comment.objects.filter(is_approved=True).count(),
    }
    return render(request, 'home.html', {
        'settings': settings,
        'articles': articles,
        'projects': projects,
        'tips': tips,
        'technologies': technologies,
        'stats': stats,
        'page_title': settings.site_name,
        'page_description': settings.description,
    })


def articles_list(request):
    settings = get_settings()
    qs = Article.objects.filter(status='published').select_related('category', 'author')
    categories = ArticleCategory.objects.all()
    search = request.GET.get('q', '')
    cat_slug = request.GET.get('categorie', '')
    tag = request.GET.get('tag', '')
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(excerpt__icontains=search) | Q(content__icontains=search))
    if cat_slug:
        qs = qs.filter(category__slug=cat_slug)
    if tag:
        qs = qs.filter(tags__name__in=[tag])
    paginator = Paginator(qs, 9)
    page_obj = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'articles/list.html', {
        'settings': settings,
        'page_obj': page_obj,
        'categories': categories,
        'search': search,
        'selected_cat': cat_slug,
        'selected_tag': tag,
        'total': paginator.count,
        'page_title': 'Articles & Blog',
        'page_description': 'Explorez tous mes articles sur la technologie et le développement.',
    })


def article_detail(request, slug):
    from core.models import PageView
    settings = get_settings()
    article = get_object_or_404(Article, slug=slug, status='published')
    Article.objects.filter(pk=article.pk).update(views_count=article.views_count + 1)
    PageView.record('article', article.pk, title=article.title, slug=article.slug)
    ct = ContentType.objects.get_for_model(Article)
    comments = Comment.objects.filter(content_type=ct, object_id=article.id, is_approved=True, parent=None).prefetch_related('replies')
    related = Article.objects.filter(status='published', category=article.category).exclude(pk=article.pk)[:3]
    tags = list(article.tags.names())
    return render(request, 'articles/detail.html', {
        'settings': settings,
        'article': article,
        'comments': comments,
        'related': related,
        'tags': tags,
        'content_type': 'articles.article',
        'object_id': article.id,
        'page_title': article.meta_title or article.title,
        'page_description': article.meta_description or article.excerpt,
        'og_image': article.cover_image.url if article.cover_image else None,
    })


def projects_list(request):
    settings = get_settings()
    qs = Project.objects.filter(status='published').select_related('category')
    categories = ProjectCategory.objects.all()
    search = request.GET.get('q', '')
    cat_slug = request.GET.get('categorie', '')
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))
    if cat_slug:
        qs = qs.filter(category__slug=cat_slug)
    paginator = Paginator(qs, 9)
    page_obj = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'projects/list.html', {
        'settings': settings,
        'page_obj': page_obj,
        'categories': categories,
        'search': search,
        'selected_cat': cat_slug,
        'total': paginator.count,
        'page_title': 'Projets & Tutoriels',
        'page_description': 'Des projets réels avec des tutoriels pas à pas pour apprendre en faisant.',
    })


def project_detail(request, slug):
    from core.models import PageView
    settings = get_settings()
    project = get_object_or_404(Project, slug=slug, status='published')
    Project.objects.filter(pk=project.pk).update(views_count=project.views_count + 1)
    PageView.record('project', project.pk, title=project.title, slug=project.slug)
    ct = ContentType.objects.get_for_model(Project)
    comments = Comment.objects.filter(content_type=ct, object_id=project.id, is_approved=True, parent=None).prefetch_related('replies')
    tags = list(project.tags.names())
    technologies = [t.strip() for t in project.technologies.split(',') if t.strip()] if project.technologies else []
    return render(request, 'projects/detail.html', {
        'settings': settings,
        'project': project,
        'comments': comments,
        'tags': tags,
        'technologies': technologies,
        'content_type': 'projects.project',
        'object_id': project.id,
        'page_title': project.meta_title or project.title,
        'page_description': project.meta_description or project.description,
        'og_image': project.cover_image.url if project.cover_image else None,
    })


def tips_list(request):
    settings = get_settings()
    qs = Tip.objects.filter(status='published').select_related('category')
    categories = TipCategory.objects.all()
    search = request.GET.get('q', '')
    cat_slug = request.GET.get('categorie', '')
    difficulty = request.GET.get('difficulte', '')
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(excerpt__icontains=search))
    if cat_slug:
        qs = qs.filter(category__slug=cat_slug)
    if difficulty:
        qs = qs.filter(difficulty=difficulty)
    paginator = Paginator(qs, 9)
    page_obj = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'tips/list.html', {
        'settings': settings,
        'page_obj': page_obj,
        'categories': categories,
        'search': search,
        'selected_cat': cat_slug,
        'selected_difficulty': difficulty,
        'total': paginator.count,
        'page_title': 'Astuces & Conseils',
        'page_description': 'Des astuces pratiques pour améliorer vos compétences.',
    })


def tip_detail(request, slug):
    from core.models import PageView
    settings = get_settings()
    tip = get_object_or_404(Tip, slug=slug, status='published')
    Tip.objects.filter(pk=tip.pk).update(views_count=tip.views_count + 1)
    PageView.record('tip', tip.pk, title=tip.title, slug=tip.slug)
    ct = ContentType.objects.get_for_model(Tip)
    comments = Comment.objects.filter(content_type=ct, object_id=tip.id, is_approved=True, parent=None).prefetch_related('replies')
    tags = list(tip.tags.names())
    return render(request, 'tips/detail.html', {
        'settings': settings,
        'tip': tip,
        'comments': comments,
        'tags': tags,
        'content_type': 'tips.tip',
        'object_id': tip.id,
        'page_title': tip.meta_title or tip.title,
        'page_description': tip.meta_description or tip.excerpt,
        'og_image': tip.cover_image.url if tip.cover_image else None,
    })


def about(request):
    settings = get_settings()
    skills = Skill.objects.all().order_by('order', 'name')
    experiences = Experience.objects.all().order_by('-start_date')
    educations = Education.objects.all().order_by('-start_date')
    skills_by_category = {}
    for skill in skills:
        cat = skill.category or 'Général'
        if cat not in skills_by_category:
            skills_by_category[cat] = []
        skills_by_category[cat].append(skill)
    og_image = None
    if settings.logo:
        og_image = settings.logo.url
    elif settings.author_photo:
        og_image = settings.author_photo.url
    return render(request, 'about.html', {
        'settings': settings,
        'skills_by_category': skills_by_category,
        'experiences': experiences,
        'educations': educations,
        'page_title': settings.about_title or 'À propos',
        'page_description': settings.author_bio or 'En savoir plus sur moi.',
        'og_image': og_image,
    })


def contact(request):
    settings = get_settings()
    return render(request, 'contact.html', {
        'settings': settings,
        'page_title': 'Contact',
        'page_description': 'Contactez-moi pour toute question ou collaboration.',
    })


def handler404(request, exception):
    settings = get_settings()
    return render(request, '404.html', {'settings': settings}, status=404)


def robots_txt(request):
    s = get_settings()
    scheme = 'https' if request.is_secure() else 'http'
    host = request.get_host()
    site_url = f"{scheme}://{host}"
    content = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /admin-ai/
Disallow: /api/
Disallow: /ckeditor/

Sitemap: {site_url}/sitemap.xml
"""
    return HttpResponse(content, content_type='text/plain; charset=utf-8')
