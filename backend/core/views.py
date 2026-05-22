from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import SiteSettings, Skill, Experience, Education
from .serializers import SiteSettingsSerializer, SkillSerializer, ExperienceSerializer, EducationSerializer
from articles.models import Article
from projects.models import Project
from tips.models import Tip
from portfolio.models import PortfolioItem


class SiteSettingsView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = SiteSettingsSerializer

    def get_object(self):
        obj, _ = SiteSettings.objects.get_or_create(pk=1)
        return obj


class SkillListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer


class ExperienceListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer


class EducationListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Education.objects.all()
    serializer_class = EducationSerializer


class StatsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'articles_count': Article.objects.filter(status='published').count(),
            'projects_count': Project.objects.filter(status='published').count(),
            'tips_count': Tip.objects.filter(status='published').count(),
            'portfolio_count': PortfolioItem.objects.count(),
        })


class SearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        q = request.GET.get('q', '')
        if not q or len(q) < 2:
            return Response({'results': [], 'query': q})

        from articles.serializers import ArticleListSerializer
        from projects.serializers import ProjectListSerializer
        from tips.serializers import TipListSerializer

        articles = Article.objects.filter(status='published', title__icontains=q)[:5]
        projects = Project.objects.filter(status='published', title__icontains=q)[:5]
        tips = Tip.objects.filter(status='published', title__icontains=q)[:5]

        results = []
        for a in articles:
            results.append({'type': 'article', 'title': a.title, 'slug': a.slug, 'excerpt': a.excerpt[:100]})
        for p in projects:
            results.append({'type': 'project', 'title': p.title, 'slug': p.slug, 'excerpt': p.description[:100]})
        for t in tips:
            results.append({'type': 'tip', 'title': t.title, 'slug': t.slug, 'excerpt': t.excerpt[:100]})

        return Response({'results': results, 'query': q, 'total': len(results)})
