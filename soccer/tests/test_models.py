from django.test import TestCase

from ..models import League, Team, Match


class LeagueTest(TestCase):
    def test(self):
        league = League.objects.create(name='TestLeague', parent='TestCountry', year=2000)
        self.assertEqual(str(league), 'TestLeague 2000')


class TeamTest(TestCase):
    def test(self):
        team = Team.objects.create(name='TestLeague', parent='TestCountry')
        self.assertEqual(str(team), 'TestLeague')


class MatchTest(TestCase):
    def setUp(self):
        self.league = League.objects.create(name='TestLeague', parent='TestCountry', year=2000)
        self.teamM = Team.objects.create(name='TeamM', parent='TestCountry')
        self.teamA = Team.objects.create(name='TeamA', parent='TestCountry')

    def test_str(self):
        match = Match.objects.create(league=self.league, home_team=self.teamM, home_score=8,
                                     away_score=2, away_team=self.teamA, round=1)
        self.assertEqual(str(match), 'TeamM vs TeamA')

    def test_compare_team(self):
        a = ["A", {'points': 20}]
        b = ["B", {'points': 25}]
        self.assertEqual(Match.compare_team(a, b), 1)

        a = ["A", {'points': 30}]
        b = ["B", {'points': 25}]
        self.assertEqual(Match.compare_team(a, b), -1)

        a = ["A", {'points': 25, 'gd': 5}]
        b = ["B", {'points': 25, 'gd': 6}]
        self.assertEqual(Match.compare_team(a, b), 1)

        a = ["A", {'points': 25, 'gd': 7}]
        b = ["B", {'points': 25, 'gd': 6}]
        self.assertEqual(Match.compare_team(a, b), -1)

        a = ["A", {'points': 25, 'gd': 5, 'gf': 6}]
        b = ["B", {'points': 25, 'gd': 5, 'gf': 8}]
        self.assertEqual(Match.compare_team(a, b), 1)

        a = ["A", {'points': 25, 'gd': 5, 'gf': 9}]
        b = ["B", {'points': 25, 'gd': 5, 'gf': 8}]
        self.assertEqual(Match.compare_team(a, b), -1)

        a = ["A", {'points': 25, 'gd': 5, 'gf': 8}]
        b = ["B", {'points': 25, 'gd': 5, 'gf': 8}]
        self.assertEqual(Match.compare_team(a, b), -1)

        a = ["C", {'points': 25, 'gd': 5, 'gf': 8}]
        b = ["B", {'points': 25, 'gd': 5, 'gf': 8}]
        self.assertEqual(Match.compare_team(a, b), 1)

        a = ["A", {'points': 25, 'gd': 5, 'gf': 8}]
        b = ["A", {'points': 25, 'gd': 5, 'gf': 8}]
        self.assertEqual(Match.compare_team(a, b), 0)

    def test_compute_movements(self):
        standing = [['A', 10], ['B', 10], ['C', 10]]
        previous_standing = [['C', 10], ['B', 10], ['A', 10]]
        self.assertEqual(Match.compute_movements(standing, previous_standing),
                         [['A', 10, 1], ['B', 10, 0], ['C', 10, -1]])

        self.assertEqual(Match.compute_movements(standing, None),
                         [['A', 10, 0], ['B', 10, 0], ['C', 10, 0]])

    def test_get_standing(self):
        match1 = Match.objects.create(league=self.league, home_team=self.teamM, home_score=8,
                                      away_score=2, away_team=self.teamA, round=4)
        match2 = Match.objects.create(league=self.league, home_team=self.teamA, home_score=4,
                                      away_score=4, away_team=self.teamM, round=5)
        match3 = Match.objects.create(league=self.league, home_team=self.teamA, home_score=1,
                                      away_score=6, away_team=self.teamM, round=38)
        self.assertEqual(Match.get_standing([match1, match2, match3]),
                         [['TeamM', {u'gd': 11, u'won': 2, u'lost': 0, u'gf': 18, u'points': 7, u'ga': 7, u'drawn': 1}],
                          ['TeamA', {u'gd': -11, u'won': 0, u'lost': 2, u'gf': 7, u'points': 1, u'ga': 18, u'drawn': 1}]])

    def test_get_match_data(self):
        match1 = Match.objects.create(league=self.league, home_team=self.teamM, home_score=8,
                                      away_score=2, away_team=self.teamA, round=1)
        match2 = Match.objects.create(league=self.league, home_team=self.teamA, home_score=8,
                                      away_score=2, away_team=self.teamM, round=1)
        match3 = Match.objects.create(league=self.league, home_team=self.teamA, home_score=8,
                                      away_score=2, away_team=self.teamM, round=2)
        match_data = Match.get_match_data(self.league)
        self.assertEqual(len(match_data), 2)
        self.assertEqual(match_data[0][0], [match1, match2])
        self.assertEqual(match_data[0][1],
                         [[u'TeamA', {u'gd': 0, u'won': 1, u'lost': 1, u'gf': 10, u'points': 3, u'ga': 10, u'drawn': 0}, 0],
                          [u'TeamM', {u'gd': 0, u'won': 1, u'lost': 1, u'gf': 10, u'points': 3, u'ga': 10, u'drawn': 0}, 0]])