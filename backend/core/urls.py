from django.urls import path
from .views import SiteSettingsView, SkillListView, ExperienceListView, EducationListView, StatsView, SearchView, MostViewedView, SiteStatsView

urlpatterns = [
    path('settings/', SiteSettingsView.as_view(), name='site-settings'),
    path('skills/', SkillListView.as_view(), name='skills'),
    path('experiences/', ExperienceListView.as_view(), name='experiences'),
    path('educations/', EducationListView.as_view(), name='educations'),
    path('stats/', StatsView.as_view(), name='stats'),
    path('stats/detailed/', SiteStatsView.as_view(), name='site-stats-detailed'),
    path('search/', SearchView.as_view(), name='search'),
    path('most-viewed/', MostViewedView.as_view(), name='most-viewed'),
]
