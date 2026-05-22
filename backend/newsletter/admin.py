from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from .models import Subscriber, NewsletterCampaign
from .utils import send_campaign


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'status', 'confirmed', 'created_at']
    list_filter = ['status', 'confirmed', 'created_at']
    search_fields = ['email', 'name']
    readonly_fields = ['token', 'created_at']
    actions = ['reactivate_subscribers']

    def reactivate_subscribers(self, request, queryset):
        count = queryset.update(status='active')
        self.message_user(request, f"{count} abonné(s) réactivé(s).", messages.SUCCESS)
    reactivate_subscribers.short_description = "Réactiver les abonnés sélectionnés"


@admin.register(NewsletterCampaign)
class NewsletterCampaignAdmin(admin.ModelAdmin):
    list_display = ['subject', 'status', 'subscriber_count', 'sent_at', 'created_at']
    list_filter = ['status']
    search_fields = ['subject']
    actions = ['send_selected_campaign']
    readonly_fields = ['status', 'sent_at', 'created_at']

    def subscriber_count(self, obj):
        count = Subscriber.objects.filter(status='active').count()
        return format_html('<span style="color:#4f46e5;font-weight:600">{} abonnés actifs</span>', count)
    subscriber_count.short_description = 'Destinataires'

    def send_selected_campaign(self, request, queryset):
        for campaign in queryset:
            if campaign.status == 'sent':
                self.message_user(request, f"La campagne '{campaign.subject}' a déjà été envoyée.", messages.WARNING)
                continue
            count, msg = send_campaign(campaign.pk)
            if count > 0:
                self.message_user(request, f"Campagne '{campaign.subject}': {msg}", messages.SUCCESS)
            else:
                self.message_user(request, f"Campagne '{campaign.subject}': {msg}", messages.WARNING)
    send_selected_campaign.short_description = "Envoyer la campagne aux abonnés actifs"
