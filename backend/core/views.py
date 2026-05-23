from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import SiteSettings, Skill, Experience, Education
from .serializers import SiteSettingsSerializer, SkillSerializer, ExperienceSerializer, EducationSerializer
from articles.models import Article
from projects.models import Project
from tips.models import Tip


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
        })


class SearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        q = request.GET.get('q', '')
        if not q or len(q) < 2:
            return Response({'results': [], 'query': q})

        articles = Article.objects.filter(status='published', title__icontains=q)[:5]
        projects = Project.objects.filter(status='published', title__icontains=q)[:5]
        tips = Tip.objects.filter(status='published', title__icontains=q)[:5]

        results = []
        for a in articles:
            results.append({'type': 'article', 'title': a.title, 'slug': a.slug, 'excerpt': (a.excerpt or '')[:100]})
        for p in projects:
            results.append({'type': 'project', 'title': p.title, 'slug': p.slug, 'excerpt': (p.description or '')[:100]})
        for t in tips:
            results.append({'type': 'tip', 'title': t.title, 'slug': t.slug, 'excerpt': (t.excerpt or '')[:100]})

        return Response({'results': results, 'query': q, 'total': len(results)})


class MostViewedView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        from .models import PageView
        from django.db.models import Sum
        from django.utils import timezone
        from datetime import timedelta

        days = int(request.GET.get('days', 30))
        limit = int(request.GET.get('limit', 10))
        since = timezone.now().date() - timedelta(days=days)

        top = PageView.objects.filter(date__gte=since)\
            .values('content_type', 'object_id', 'object_title', 'object_slug')\
            .annotate(total_views=Sum('count'))\
            .order_by('-total_views')[:limit]

        return Response({
            'period_days': days,
            'results': list(top),
        })


class SiteStatsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        from .models import PageView
        from django.db.models import Sum
        from django.utils import timezone
        from datetime import timedelta

        today = timezone.now().date()
        last_7 = today - timedelta(days=7)
        last_30 = today - timedelta(days=30)

        views_today = PageView.objects.filter(date=today).aggregate(t=Sum('count'))['t'] or 0
        views_7 = PageView.objects.filter(date__gte=last_7).aggregate(t=Sum('count'))['t'] or 0
        views_30 = PageView.objects.filter(date__gte=last_30).aggregate(t=Sum('count'))['t'] or 0

        daily = list(
            PageView.objects.filter(date__gte=last_30)
            .values('date')
            .annotate(views=Sum('count'))
            .order_by('date')
            .values('date', 'views')
        )

        return Response({
            'views_today': views_today,
            'views_last_7_days': views_7,
            'views_last_30_days': views_30,
            'articles_count': Article.objects.filter(status='published').count(),
            'projects_count': Project.objects.filter(status='published').count(),
            'tips_count': Tip.objects.filter(status='published').count(),
            'daily_views': daily,
        })
