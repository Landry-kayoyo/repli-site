from django.urls import path
from .feeds import (
    ArticlesFeed, ArticlesAtomFeed,
    ProjectsFeed, ProjectsAtomFeed,
    TipsFeed, TipsAtomFeed,
    GlobalFeed, GlobalAtomFeed,
)

urlpatterns = [
    path('', GlobalFeed(), name='rss-global'),
    path('atom/', GlobalAtomFeed(), name='rss-global-atom'),
    path('articles/', ArticlesFeed(), name='rss-articles'),
    path('articles/atom/', ArticlesAtomFeed(), name='rss-articles-atom'),
    path('projets/', ProjectsFeed(), name='rss-projects'),
    path('projets/atom/', ProjectsAtomFeed(), name='rss-projects-atom'),
    path('astuces/', TipsFeed(), name='rss-tips'),
    path('astuces/atom/', TipsAtomFeed(), name='rss-tips-atom'),
]
