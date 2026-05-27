from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.sitemaps import ArticleSitemap, ProjectSitemap, TipSitemap, StaticViewSitemap

sitemaps = {
    'articles': ArticleSitemap,
    'projects': ProjectSitemap,
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
    path('api/projects/', include('projects.urls')),
    path('api/tips/', include('tips.urls')),
    path('api/contact/', include('contact.urls')),
    path('api/newsletter/', include('newsletter.urls')),
    path('api/comments/', include('comments.urls')),
    path('api/reactions/', include('reactions.urls')),

    path('admin-ai/chat/', __import__('core.ai_views', fromlist=['ai_chat']).ai_chat, name='admin-ai-chat'),
    path('admin-ai/suggest/', __import__('core.ai_views', fromlist=['ai_suggest']).ai_suggest, name='admin-ai-suggest'),
    path('admin-ai/inline-suggest/', __import__('core.ai_views', fromlist=['ai_inline_suggest']).ai_inline_suggest, name='admin-ai-inline-suggest'),
    path('admin-ai/analyze/', __import__('core.ai_views', fromlist=['ai_analyze']).ai_analyze, name='admin-ai-analyze'),
    path('admin-ai/publish/', __import__('core.ai_views', fromlist=['ai_publish']).ai_publish, name='admin-ai-publish'),
    path('admin-ai/diagnostic/', __import__('core.diagnostic_views', fromlist=['diagnostic_page']).diagnostic_page, name='admin-ai-diagnostic'),
    path('admin-ai/test-smtp/', __import__('core.diagnostic_views', fromlist=['test_smtp_connection']).test_smtp_connection, name='admin-ai-test-smtp'),
    path('admin-ai/send-test-email/', __import__('core.diagnostic_views', fromlist=['send_test_email']).send_test_email, name='admin-ai-send-test-email'),
    path('admin-ai/newsletter/', __import__('core.diagnostic_views', fromlist=['newsletter_management']).newsletter_management, name='admin-ai-newsletter'),
    path('admin-ai/newsletter/send/', __import__('core.diagnostic_views', fromlist=['send_newsletter_campaign']).send_newsletter_campaign, name='admin-ai-newsletter-send'),
    path('admin-ai/users/', __import__('core.ai_views', fromlist=['get_admin_users']).get_admin_users, name='admin-ai-users'),
    path('admin-ai/smart-notifications/', __import__('core.ai_views', fromlist=['smart_notifications']).smart_notifications, name='admin-ai-smart-notifications'),
    path('admin-ai/calendar/', __import__('core.diagnostic_views', fromlist=['editorial_calendar']).editorial_calendar, name='admin-ai-calendar'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('rss/', include('core.feeds_urls')),

    path('', include('web.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
