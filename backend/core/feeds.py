from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from articles.models import Article
from projects.models import Project
from tips.models import Tip


class ArticlesFeed(Feed):
    title = "Landry Net - Articles"
    link = "/articles/"
    description = "Derniers articles publiés sur Landry Net"

    def items(self):
        return Article.objects.filter(status='published').order_by('-published_at')[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt

    def item_link(self, item):
        return f"/articles/{item.slug}"

    def item_pubdate(self, item):
        return item.published_at


class ProjectsFeed(Feed):
    title = "Landry Net - Projets"
    link = "/projets/"
    description = "Derniers projets publiés sur Landry Net"

    def items(self):
        return Project.objects.filter(status='published').order_by('-published_at')[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_link(self, item):
        return f"/projets/{item.slug}"

    def item_pubdate(self, item):
        return item.published_at


class TipsFeed(Feed):
    title = "Landry Net - Astuces"
    link = "/astuces/"
    description = "Dernières astuces publiées sur Landry Net"

    def items(self):
        return Tip.objects.filter(status='published').order_by('-published_at')[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt

    def item_link(self, item):
        return f"/astuces/{item.slug}"

    def item_pubdate(self, item):
        return item.published_at
