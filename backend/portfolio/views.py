from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import PortfolioCategory, PortfolioItem
from .serializers import PortfolioCategorySerializer, PortfolioItemSerializer


class PortfolioCategoryListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = PortfolioCategory.objects.all()
    serializer_class = PortfolioCategorySerializer


class PortfolioListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PortfolioItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category__slug', 'is_featured']
    search_fields = ['title', 'description']

    def get_queryset(self):
        return PortfolioItem.objects.all().order_by('order', '-created_at')


class PortfolioDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = PortfolioItemSerializer
    lookup_field = 'slug'
    queryset = PortfolioItem.objects.all()
