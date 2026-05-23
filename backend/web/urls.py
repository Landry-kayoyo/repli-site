from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('articles/', views.articles_list, name='articles_list'),
    path('articles/<slug:slug>/', views.article_detail, name='article_detail'),
    path('projets/', views.projects_list, name='projects_list'),
    path('projets/<slug:slug>/', views.project_detail, name='project_detail'),
    path('astuces/', views.tips_list, name='tips_list'),
    path('astuces/<slug:slug>/', views.tip_detail, name='tip_detail'),

    path('a-propos/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]
