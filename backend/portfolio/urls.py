from django.urls import path
from .views import PortfolioCategoryListView, PortfolioListView, PortfolioDetailView

urlpatterns = [
    path('', PortfolioListView.as_view(), name='portfolio-list'),
    path('categories/', PortfolioCategoryListView.as_view(), name='portfolio-categories'),
    path('<slug:slug>/', PortfolioDetailView.as_view(), name='portfolio-detail'),
]
