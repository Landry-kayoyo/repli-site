from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.sitemaps import ArticleSitemap, ProjectSitemap, PortfolioSitemap, TipSitemap, StaticViewSitemap

sitemaps = {
    'articles': ArticleSitemap,
    'projects': ProjectSitemap,
    'portfolio': PortfolioSitemap,
    'tips': TipSitemap,
    'static': StaticViewSitemap,
}

handler404 = 'web.views.handler404'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/', include('core.urls')),
    path('api/articles/', include('articles.urls')),
    path('api/portfolio/', include('portfolio.urls')),
    path('api/projects/', include('projects.urls')),
    path('api/tips/', include('tips.urls')),
    path('api/contact/', include('contact.urls')),
    path('api/newsletter/', include('newsletter.urls')),
    path('api/comments/', include('comments.urls')),
    path('api/reactions/', include('reactions.urls')),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('rss/', include('core.feeds_urls')),

    path('', include('web.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
