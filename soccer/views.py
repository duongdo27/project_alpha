from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from .models import League, Match, Team


class LeagueListView(ListView):
    model = League
    template_name = 'leagues.html'

    def get_queryset(self):
        return League.objects.all().values('name', 'parent').distinct()


class LeagueYearListView(ListView):
    model = League
    template_name = 'league_years.html'

    def get_queryset(self):
        return League.objects.filter(parent=self.kwargs['parent'],
                                     name=self.kwargs['name'])


class LeagueDetailView(DetailView):
    model = League
    template_name = 'league_detail.html'
