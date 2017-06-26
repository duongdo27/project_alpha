from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='index'),
    url(r'^leagues$', views.LeagueListView.as_view(),
        name='leagues'),
    url(r'^league_years/(?P<parent>.+)/(?P<name>.+)$', views.LeagueYearListView.as_view(),
        name='league_years'),
    url(r'^league/(?P<pk>\d+)$', views.LeagueDetailView.as_view(),
        name='league_detail'),
]
