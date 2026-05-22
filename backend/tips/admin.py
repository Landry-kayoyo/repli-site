from django.contrib import admin
from django.utils.html import format_html
from .models import TipCategory, Tip


@admin.register(TipCategory)
class TipCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tip)
class TipAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'difficulty', 'status', 'is_featured', 'views_count', 'cover_preview']
    list_filter = ['status', 'category', 'difficulty', 'is_featured']
    search_fields = ['title', 'excerpt', 'content']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['status', 'is_featured']
    readonly_fields = ['views_count', 'created_at', 'updated_at', 'cover_preview']
    fieldsets = (
        ('Contenu', {
            'fields': ('title', 'subtitle', 'slug', 'author', 'category', 'excerpt', 'content', 'cover_image', 'cover_preview', 'tags')
        }),
        ('Publication', {
            'fields': ('status', 'is_featured', 'difficulty', 'published_at')
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
