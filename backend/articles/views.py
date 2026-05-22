from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Article
from .serializers import CategorySerializer, ArticleListSerializer, ArticleDetailSerializer


class CategoryListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ArticleListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ArticleListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug', 'status', 'is_featured']
    search_fields = ['title', 'excerpt', 'content']
    ordering_fields = ['published_at', 'views_count', 'created_at']
    ordering = ['-published_at']

    def get_queryset(self):
        qs = Article.objects.filter(status='published')
        tag = self.request.query_params.get('tag')
        if tag:
            qs = qs.filter(tags__name__in=[tag])
        return qs


class ArticleDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = ArticleDetailSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return Article.objects.filter(status='published')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        from core.models import PageView
        PageView.record('article', instance.id, instance.title, instance.slug)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class FeaturedArticlesView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ArticleListSerializer

    def get_queryset(self):
        return Article.objects.filter(status='published', is_featured=True)[:6]
