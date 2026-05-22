from django.contrib import admin
from .models import Reaction


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ['reaction_type', 'content_type', 'object_id', 'session_key', 'created_at']
    list_filter = ['reaction_type', 'content_type']
    readonly_fields = ['created_at']
