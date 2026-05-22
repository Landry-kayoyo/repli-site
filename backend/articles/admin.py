from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Article


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color', 'order']
    list_editable = ['order']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'is_featured', 'views_count', 'published_at', 'cover_preview']
    list_filter = ['status', 'category', 'is_featured', 'published_at']
    search_fields = ['title', 'excerpt', 'content']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['status', 'is_featured']
    readonly_fields = ['views_count', 'created_at', 'updated_at', 'cover_preview']
    date_hierarchy = 'published_at'
    fieldsets = (
        ('Contenu', {
            'fields': ('title', 'subtitle', 'slug', 'author', 'category', 'excerpt', 'content', 'tags', 'cover_image', 'cover_preview')
        }),
        ('Publication', {
            'fields': ('status', 'is_featured', 'published_at', 'read_time')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Statistiques', {
            'fields': ('views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" height="80" style="border-radius:8px"/>', obj.cover_image.url)
        return '-'
    cover_preview.short_description = 'Aperçu couverture'
