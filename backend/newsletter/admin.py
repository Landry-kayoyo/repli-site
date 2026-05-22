from django.contrib import admin
from .models import Subscriber, NewsletterCampaign


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'status', 'confirmed', 'created_at']
    list_filter = ['status', 'confirmed', 'created_at']
    search_fields = ['email', 'name']
    readonly_fields = ['token', 'created_at']


@admin.register(NewsletterCampaign)
class NewsletterCampaignAdmin(admin.ModelAdmin):
    list_display = ['subject', 'status', 'sent_at', 'created_at']
    list_filter = ['status']
    search_fields = ['subject']
