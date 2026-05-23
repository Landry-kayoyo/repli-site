from django.contrib.sitemaps import Sitemap
from articles.models import Article
from projects.models import Project
from tips.models import Tip


class ArticleSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Article.objects.filter(status='published')

    def location(self, obj):
        return f'/articles/{obj.slug}'

    def lastmod(self, obj):
        return obj.updated_at


class ProjectSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.8

    def items(self):
        return Project.objects.filter(status='published')

    def location(self, obj):
        return f'/projets/{obj.slug}'

    def lastmod(self, obj):
        return obj.updated_at


class TipSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Tip.objects.filter(status='published')

    def location(self, obj):
        return f'/astuces/{obj.slug}'

    def lastmod(self, obj):
        return obj.updated_at


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return ['/', '/a-propos', '/articles', '/projets', '/astuces', '/contact']

    def location(self, item):
        return item
