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
        context['data'] = Match.get_match_data(self.object)

        all_matches = Match.objects.filter(league=self.object)
        context['final_standing'] = Match.get_standing(all_matches)
        return context


class TeamDetailView(DetailView):
    model = Team
    template_name = 'team_detail.html'

    def get_context_data(self, **kwargs):
        context = super(TeamDetailView, self).get_context_data(**kwargs)
        league = get_object_or_404(League, pk=self.kwargs['league_id'])
        context['league'] = league
        context['data'] = json.dumps([
            {'x': 10, 'y': 10},
            {'x': 20, 'y': 12},
            {'x': 30, 'y': 8},
            {'x': 40, 'y': 14},
            {'x': 50, 'y': 6},
            {'x': 60, 'y': 24},
            {'x': 70, 'y': -4},
            {'x': 80, 'y': 10},
        ])
        return context
