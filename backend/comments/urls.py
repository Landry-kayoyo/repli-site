from django.urls import path
from .views import CommentListCreateView, CommentLikeView

urlpatterns = [
    path('', CommentListCreateView.as_view(), name='comments'),
    path('<int:pk>/like/', CommentLikeView.as_view(), name='comment_like'),
]
