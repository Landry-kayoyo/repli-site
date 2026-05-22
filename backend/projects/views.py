from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import ProjectCategory, Project
from .serializers import ProjectCategorySerializer, ProjectListSerializer, ProjectDetailSerializer


class ProjectCategoryListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = ProjectCategory.objects.all()
    serializer_class = ProjectCategorySerializer


class ProjectListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProjectListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug', 'status', 'is_featured']
    search_fields = ['title', 'description', 'content', 'technologies']
    ordering_fields = ['published_at', 'views_count', 'created_at']
    ordering = ['-published_at']

    def get_queryset(self):
        qs = Project.objects.filter(status='published')
        tag = self.request.query_params.get('tag')
        if tag:
            qs = qs.filter(tags__name__in=[tag])
        return qs


class ProjectDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProjectDetailSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return Project.objects.filter(status='published')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
