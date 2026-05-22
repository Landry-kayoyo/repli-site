from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'author_email', 'content_type', 'object_id', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'content_type', 'created_at']
    search_fields = ['author_name', 'author_email', 'content']
    list_editable = ['is_approved']
    readonly_fields = ['created_at', 'updated_at']
