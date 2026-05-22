from django.contrib import admin
from django.utils.html import format_html
from .models import ProjectCategory, Project


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'is_featured', 'views_count', 'published_at', 'cover_preview']
    list_filter = ['status', 'category', 'is_featured']
    search_fields = ['title', 'description', 'content']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['status', 'is_featured']
    readonly_fields = ['views_count', 'created_at', 'updated_at', 'cover_preview']
    fieldsets = (
        ('Contenu', {
            'fields': ('title', 'subtitle', 'slug', 'author', 'category', 'description', 'content', 'tutorial_steps', 'cover_image', 'cover_preview', 'tags')
        }),
        ('Liens', {
            'fields': ('github_url', 'demo_url', 'technologies')
        }),
        ('Publication', {
            'fields': ('status', 'is_featured', 'published_at')
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
