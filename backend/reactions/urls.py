from django.urls import path
from .views import ReactionView

urlpatterns = [
    path('', ReactionView.as_view(), name='reactions'),
]
