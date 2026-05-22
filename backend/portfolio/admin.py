from django.contrib import admin
from django.utils.html import format_html
from .models import PortfolioCategory, PortfolioItem, PortfolioImage


@admin.register(PortfolioCategory)
class PortfolioCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class PortfolioImageInline(admin.TabularInline):
    model = PortfolioItem.images.through
    extra = 3


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'client', 'is_featured', 'order', 'cover_preview']
    list_editable = ['order', 'is_featured']
    list_filter = ['category', 'is_featured']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['cover_preview']
    fieldsets = (
        ('Contenu', {
            'fields': ('title', 'subtitle', 'slug', 'category', 'client', 'description', 'content', 'cover_image', 'cover_preview', 'tags')
        }),
        ('Liens', {
            'fields': ('url', 'github_url')
        }),
        ('Paramètres', {
            'fields': ('is_featured', 'order')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" height="80" style="border-radius:8px"/>', obj.cover_image.url)
        return '-'
    cover_preview.short_description = 'Aperçu couverture'


@admin.register(PortfolioImage)
class PortfolioImageAdmin(admin.ModelAdmin):
    list_display = ['caption', 'order']
