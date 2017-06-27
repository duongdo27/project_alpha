from django.test import TestCase

from ..models import League, Team, Match


class LeagueTest(TestCase):
    def test(self):
        league = League(name='TestLeague', parent='TestCountry', year=2000)
        self.assertEqual(str(league), 'TestLeague 2000')


class TeamTest(TestCase):
    def test(self):
        team = Team(name='TestLeague', parent='TestCountry')
        self.assertEqual(str(team), 'TestLeague')


class MatchTest(TestCase):
    def test(self):
        league = League(name='TestLeague', parent='TestCountry', year=2000)
        teamM = Team(name='TeamM', parent='TestCountry')
        teamA = Team(name='TeamA', parent='TestCountry')
        match = Match(league=league, home_team=teamM, home_score=8,
                      away_score=2, away_team=teamA)
        self.assertEqual(str(match), 'TeamM vs TeamA')