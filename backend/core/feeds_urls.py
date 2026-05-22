from django.urls import path
from .feeds import ArticlesFeed, ProjectsFeed, TipsFeed

urlpatterns = [
    path('articles/', ArticlesFeed(), name='rss-articles'),
    path('projets/', ProjectsFeed(), name='rss-projects'),
    path('astuces/', TipsFeed(), name='rss-tips'),
]
