import json
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

from .models import League, Match, Team


class HomeView(TemplateView):
    template_name = 'index.html'


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
                                     name=self.kwargs['name']).order_by('-year')

    def get_context_data(self, **kwargs):
        context = super(LeagueYearListView, self).get_context_data(**kwargs)
        context['parent'] = self.kwargs['parent']
        context['name'] = self.kwargs['name']
        return context


class LeagueDetailView(DetailView):
    model = League
    template_name = 'league_detail.html'

    def get_context_data(self, **kwargs):
        context = super(LeagueDetailView, self).get_context_data(**kwargs)
        context['data'] = self.object.get_league_data()
        return context


class TeamDetailView(DetailView):
    model = Team
    template_name = 'team_detail.html'

    def get_context_data(self, **kwargs):
        context = super(TeamDetailView, self).get_context_data(**kwargs)
        league = get_object_or_404(League, pk=self.kwargs['league_id'])
        context['league'] = league
        context['graph_data'] = json.dumps(self.object.get_graph_data(league))
        return context
