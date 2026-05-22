from django.urls import path
from .views import TipCategoryListView, TipListView, TipDetailView

urlpatterns = [
    path('', TipListView.as_view(), name='tip-list'),
    path('categories/', TipCategoryListView.as_view(), name='tip-categories'),
    path('<slug:slug>/', TipDetailView.as_view(), name='tip-detail'),
]
