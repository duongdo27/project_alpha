from django.test import TestCase

from ..models import League, Team, Match, Info


class LeagueTest(TestCase):
    def test_str(self):
        league = League.objects.create(name='TestLeague', parent='TestCountry', year=2000)
        self.assertEqual(str(league), 'TestLeague 2000')

    def test_get_league_data(self):
        league = League.objects.create(name='TestLeague', parent='TestCountry', year=2000)
        teamM = Team.objects.create(name='TeamM', parent='TestCountry')
        teamA = Team.objects.create(name='TeamA', parent='TestCountry')
        match1 = Match.objects.create(league=league, home_team=teamM, home_score=8,
                                      away_score=2, away_team=teamA, round=1)
        match2 = Match.objects.create(league=league, home_team=teamA, home_score=0,
                                      away_score=2, away_team=teamM, round=2)
        info1 = Info.objects.create(league=league, team=teamA, round=1, points=0,
                                    home_won=0, home_drawn=0, home_lost=1,
                                    away_won=0, away_drawn=0, away_lost=1, gf=2, ga=10,
                                    gd=-8, rank=2, movement=-1)
        info2 = Info.objects.create(league=league, team=teamM, round=2, points=6,
                                    home_won=1, home_drawn=0, home_lost=1,
                                    away_won=1, away_drawn=0, away_lost=1, gf=10, ga=2,
                                    gd=8, rank=1, movement=1)

        data = league.get_league_data()
        self.assertEqual(data[0][0].first(), match1)
        self.assertEqual(data[0][1].first(), info1)
        self.assertEqual(data[1][0].first(), match2)
        self.assertEqual(data[1][1].first(), info2)


class TeamTest(TestCase):
    def test_str(self):
        team = Team.objects.create(name='TestLeague', parent='TestCountry')
        self.assertEqual(str(team), 'TestLeague')

    def test_get_graph_data(self):
        league = League.objects.create(name='TestLeague', parent='TestCountry', year=2000)
        team = Team.objects.create(name='TeamA', parent='TestCountry')
        info = Info.objects.create(league=league, team=team, round=1, points=0,
                                   home_won=0, home_drawn=0, home_lost=1,
                                   away_won=0, away_drawn=0, away_lost=1, gf=2, ga=10,
                                   gd=-8, rank=2, movement=-1)
        self.assertEqual(team.get_graph_data(league),
                         {u'home_won': 0, u'home_lost': 1, u'away_won': 0, u'away_lost': 1, u'rounds': [1], u'won': 0,
                          u'lost': 2, u'ranks': [2], u'away_drawn': 0, u'home_drawn': 0, u'points': [0], u'drawn': 0})


class MatchTest(TestCase):
    def test_str(self):
        league = League.objects.create(name='TestLeague', parent='TestCountry', year=2000)
        teamM = Team.objects.create(name='TeamM', parent='TestCountry')
        teamA = Team.objects.create(name='TeamA', parent='TestCountry')
        match = Match.objects.create(league=league, home_team=teamM, home_score=8,
                                     away_score=2, away_team=teamA, round=1)
        self.assertEqual(str(match), 'TeamM vs TeamA')
