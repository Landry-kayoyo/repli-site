from rest_framework import serializers
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'parent', 'author_name', 'author_email',
                  'content', 'is_approved', 'is_author_reply', 'likes_count', 'created_at']
        read_only_fields = ['is_approved', 'created_at', 'likes_count']
