from django.test import TestCase, RequestFactory

from ..views import HomeView, LeagueListView, LeagueYearListView, LeagueDetailView, TeamDetailView
from ..models import League, Team, Match, Info


class BaseViewTest(TestCase):
    _view_class = None
    _kwargs = {}

    def setUp(self):
        self.factory = RequestFactory()
        self._initialize()

    def _initialize(self):
        pass

    def _get_response(self, request):
        response = self._view_class.as_view()(request, **self._kwargs)
        response.render()
        return response


class HomeViewTest(BaseViewTest):
    _view_class = HomeView

    def test(self):
        request = self.factory.get('/')
        response = self._get_response(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Welcome to Soccer Leagues!', response.content)


class LeagueListViewTest(BaseViewTest):
    _view_class = LeagueListView

    def _initialize(self):
        League.objects.create(name='TestLeague', parent='TestCountry', year=2000)
        League.objects.create(name='TestLeague2', parent='TestCountry2', year=2000)

    def test(self):
        request = self.factory.get('/leagues')
        response = self._get_response(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('TestLeague2 (TestCountry2)', response.content)
        self.assertIn('TestLeague (TestCountry)', response.content)


class LeagueYearListViewTest(BaseViewTest):
    _view_class = LeagueYearListView
    _kwargs = {'name': 'TestLeague', 'parent': 'TestCountry'}

    def _initialize(self):
        League.objects.create(name='TestLeague', parent='TestCountry', year=2000)
        League.objects.create(name='TestLeague', parent='TestCountry', year=2002)

    def test(self):
        request = self.factory.get('/league_years')
        response = self._get_response(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('TestLeague (TestCountry)', response.content)
        self.assertIn('2000', response.content)
        self.assertIn('2002', response.content)
        self.assertIn('Back', response.content)


class LeagueDetailViewTest(BaseViewTest):
    _view_class = LeagueDetailView

    def _initialize(self):
        league = League.objects.create(name='TestLeague', parent='TestCountry', year=2000)
        teamA = Team.objects.create(name='TeamA', parent='TestCountry')
        teamB = Team.objects.create(name='TeamB', parent='TestCountry')
        Match.objects.create(league=league, home_team=teamA, home_score=1, away_score=0, away_team=teamB, round=1)
        Match.objects.create(league=league, home_team=teamB, home_score=4, away_score=4, away_team=teamA, round=2)
        Info.objects.create(league=league, team=teamA, round=1, points=0,
                            home_won=0, home_drawn=0, home_lost=1,
                            away_won=0, away_drawn=0, away_lost=1, gf=2, ga=10,
                            gd=-8, rank=2, movement=-1)
        Info.objects.create(league=league, team=teamB, round=2, points=6,
                            home_won=1, home_drawn=0, home_lost=1,
                            away_won=1, away_drawn=0, away_lost=1, gf=10, ga=2,
                            gd=8, rank=1, movement=1)
        self._kwargs = {'pk': league.id}

    def test(self):
        request = self.factory.get('/league')
        response = self._get_response(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('TestLeague (TestCountry) 2000', response.content)
        self.assertIn('Round 1', response.content)
        self.assertIn('Round 2', response.content)
        self.assertIn('Matches', response.content)
        self.assertIn('Standing', response.content)
        self.assertIn('TeamA', response.content)
        self.assertIn('TeamB', response.content)
        self.assertIn('Back', response.content)


class TeamDetailViewTest(BaseViewTest):
    _view_class = TeamDetailView

    def _initialize(self):
        league = League.objects.create(name='TestLeague', parent='TestCountry', year=2000)
        team = Team.objects.create(name='TeamA', parent='TestCountry')
        Info.objects.create(league=league, team=team, round=1, points=0,
                            home_won=0, home_drawn=0, home_lost=1,
                            away_won=0, away_drawn=0, away_lost=1, gf=2, ga=10,
                            gd=-8, rank=2, movement=-1)
        self._kwargs = {'league_id': league.id, 'pk': team.id}

    def test(self):
        request = self.factory.get('/team')
        response = self._get_response(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('TestLeague (TestCountry) 2000', response.content)
        self.assertIn('TeamA', response.content)
        self.assertIn('performanceChart', response.content)
        self.assertIn('winChart', response.content)
        self.assertIn('Back', response.content)
