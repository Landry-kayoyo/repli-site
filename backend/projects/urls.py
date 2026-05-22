from django.urls import path
from .views import ProjectCategoryListView, ProjectListView, ProjectDetailView

urlpatterns = [
    path('', ProjectListView.as_view(), name='project-list'),
    path('categories/', ProjectCategoryListView.as_view(), name='project-categories'),
    path('<slug:slug>/', ProjectDetailView.as_view(), name='project-detail'),
]
