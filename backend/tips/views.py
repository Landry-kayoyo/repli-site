from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import TipCategory, Tip
from .serializers import TipCategorySerializer, TipListSerializer, TipDetailSerializer


class TipCategoryListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = TipCategory.objects.all()
    serializer_class = TipCategorySerializer


class TipListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = TipListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug', 'difficulty', 'status', 'is_featured']
    search_fields = ['title', 'excerpt', 'content']
    ordering = ['-published_at']

    def get_queryset(self):
        return Tip.objects.filter(status='published')


class TipDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = TipDetailSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return Tip.objects.filter(status='published')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
