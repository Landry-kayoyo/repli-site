from django.urls import path
from .views import CategoryListView, ArticleListView, ArticleDetailView, FeaturedArticlesView

urlpatterns = [
    path('', ArticleListView.as_view(), name='article-list'),
    path('categories/', CategoryListView.as_view(), name='article-categories'),
    path('featured/', FeaturedArticlesView.as_view(), name='featured-articles'),
    path('<slug:slug>/', ArticleDetailView.as_view(), name='article-detail'),
]
