from django.test import TestCase
import mock

from ..loaders.league_processor import LeagueProcessor
from ..models import Team, Match, League, Info


class LeagueProcessorTest(TestCase):
    def setUp(self):
        self.league = League.objects.create(name="Bundesliga", parent='Germany', year=2000)
        self.a = LeagueProcessor(self.league)

        self.team1 = Team.objects.create(name="Borussia Dortmund", parent="Germany")
        self.team2 = Team.objects.create(name="Bayer Leverkusen", parent="Germany")

    def test_compare_team(self):
        a = ["A", {'points': 20}]
        b = ["B", {'points': 25}]
        self.assertEqual(LeagueProcessor.compare_team(a, b), 1)

        a = ["A", {'points': 30}]
        b = ["B", {'points': 25}]
        self.assertEqual(LeagueProcessor.compare_team(a, b), -1)

        a = ["A", {'points': 25, 'gd': 5}]
        b = ["B", {'points': 25, 'gd': 6}]
        self.assertEqual(LeagueProcessor.compare_team(a, b), 1)

        a = ["A", {'points': 25, 'gd': 7}]
        b = ["B", {'points': 25, 'gd': 6}]
        self.assertEqual(LeagueProcessor.compare_team(a, b), -1)

        a = ["A", {'points': 25, 'gd': 5, 'gf': 6}]
        b = ["B", {'points': 25, 'gd': 5, 'gf': 8}]
        self.assertEqual(LeagueProcessor.compare_team(a, b), 1)

        a = ["A", {'points': 25, 'gd': 5, 'gf': 9}]
        b = ["B", {'points': 25, 'gd': 5, 'gf': 8}]
        self.assertEqual(LeagueProcessor.compare_team(a, b), -1)

        a = ["A", {'points': 25, 'gd': 5, 'gf': 8}]
        b = ["B", {'points': 25, 'gd': 5, 'gf': 8}]
        self.assertEqual(LeagueProcessor.compare_team(a, b), -1)

        a = ["C", {'points': 25, 'gd': 5, 'gf': 8}]
        b = ["B", {'points': 25, 'gd': 5, 'gf': 8}]
        self.assertEqual(LeagueProcessor.compare_team(a, b), 1)

        a = ["A", {'points': 25, 'gd': 5, 'gf': 8}]
        b = ["A", {'points': 25, 'gd': 5, 'gf': 8}]
        self.assertEqual(LeagueProcessor.compare_team(a, b), 0)

    def test_compute_info(self):
        round_data = {
            self.team1: {'round': 1, 'points': 1, 'gf': 1, 'ga': 1, 'gd': 1,
                         'home_won': 0, 'home_drawn': 1, 'home_lost': 0,
                         'away_won': 0, 'away_drawn': 0, 'away_lost': 0},
            self.team2: {'round': 1, 'points': 1, 'gf': 1, 'ga': 1, 'gd': 1,
                         'home_won': 0, 'home_drawn': 0, 'home_lost': 0,
                         'away_won': 0, 'away_drawn': 1, 'away_lost': 0}
        }
        match1 = Match.objects.create(league=self.league, home_team=self.team1, home_score=3, away_score=2,
                                      away_team=self.team2, round=2)
        match2 = Match.objects.create(league=self.league, home_team=self.team1, home_score=3, away_score=3,
                                      away_team=self.team2, round=3)
        match3 = Match.objects.create(league=self.league, home_team=self.team1, home_score=1, away_score=2,
                                      away_team=self.team2, round=4)

        LeagueProcessor.compute_info(round_data, match1)
        LeagueProcessor.compute_info(round_data, match2)
        LeagueProcessor.compute_info(round_data, match3)

        self.assertEqual(round_data,
                         {self.team1: {'home_won': 1, 'home_lost': 1, 'gf': 8, 'gd': 1, 'home_drawn': 2, 'ga': 8,
                                       'away_won': 0, 'away_drawn': 0, 'away_lost': 0, 'points': 5, 'round': 4},
                          self.team2: {'home_won': 0, 'home_lost': 0, 'gf': 8, 'gd': 1, 'home_drawn': 0, 'ga': 8,
                                       'away_won': 1, 'away_drawn': 2, 'away_lost': 1, 'points': 5, 'round': 4}})

    def test_compute_rank(self):
        orig_round_data = {
            self.team1: {'round': 1, 'points': 3, 'gf': 1, 'ga': 1, 'gd': 1,
                         'home_won': 0, 'home_drawn': 1, 'home_lost': 0,
                         'away_won': 0, 'away_drawn': 0, 'away_lost': 0},
            self.team2: {'round': 1, 'points': 1, 'gf': 1, 'ga': 1, 'gd': 1,
                         'home_won': 0, 'home_drawn': 0, 'home_lost': 0,
                         'away_won': 0, 'away_drawn': 1, 'away_lost': 0}
        }
        previous_standing = {self.team1: 2, self.team2: 1}
        self.assertEqual(self.a.compute_rank(orig_round_data, previous_standing),
                         {self.team1: {'home_won': 0, 'rank': 1, 'home_lost': 0, 'away_drawn': 0, 'away_won': 0,
                                       'home_drawn': 1, 'gf': 1, 'gd': 1, 'away_lost': 0, 'ga': 1, 'movement': 1,
                                       'round': 1, 'points': 3},
                          self.team2: {'home_won': 0, 'rank': 2, 'home_lost': 0, 'away_drawn': 1, 'away_won': 0,
                                       'home_drawn': 0, 'gf': 1, 'gd': 1, 'away_lost': 0, 'ga': 1, 'movement': -1,
                                       'round': 1, 'points': 1}})
        previous_standing = {self.team1: 1, self.team2: 2}
        self.assertEqual(self.a.compute_rank(orig_round_data, previous_standing),
                         {self.team1: {'home_won': 0, 'rank': 1, 'home_lost': 0, 'away_drawn': 0, 'away_won': 0,
                                       'home_drawn': 1, 'gf': 1, 'gd': 1, 'away_lost': 0, 'ga': 1, 'movement': 0,
                                       'round': 1, 'points': 3},
                          self.team2: {'home_won': 0, 'rank': 2, 'home_lost': 0, 'away_drawn': 1, 'away_won': 0,
                                       'home_drawn': 0, 'gf': 1, 'gd': 1, 'away_lost': 0, 'ga': 1, 'movement': 0,
                                       'round': 1, 'points': 1}})

    def test_save_data(self):
        data = [{
            self.team1: {
                'round': 1, 'points': 1, 'gf': 1, 'ga': 1, 'gd': 1,
                'home_won': 0, 'home_drawn': 1, 'home_lost': 0, 'movement': 1,
                'away_won': 0, 'away_drawn': 0, 'away_lost': 0, 'rank': 1,
            }
        }]
        self.a.save_data(data)
        info = Info.objects.filter(league=self.league).first()
        self.assertEqual(info.round, 1)
        self.assertEqual(info.points, 1)
        self.assertEqual(info.gf, 1)
        self.assertEqual(info.ga, 1)
        self.assertEqual(info.gd, 1)
        self.assertEqual(info.home_won, 0)
        self.assertEqual(info.home_drawn, 1)
        self.assertEqual(info.home_lost, 0)
        self.assertEqual(info.movement, 1)
        self.assertEqual(info.away_won, 0)
        self.assertEqual(info.away_drawn, 0)
        self.assertEqual(info.away_lost, 0)
        self.assertEqual(info.rank, 1)

    def test_run(self):
        team3 = Team.objects.create(name="Hello", parent="Germany")
        team4 = Team.objects.create(name="World", parent="Germany")
        team5 = Team.objects.create(name="Hello2", parent="Germany")
        team6 = Team.objects.create(name="World2", parent="Germany")

        Match.objects.create(league=self.league, home_team=self.team1, home_score=3, away_score=2,
                             away_team=self.team2, round=1)
        Match.objects.create(league=self.league, home_team=team3, home_score=3, away_score=3,
                             away_team=team4, round=2)
        Match.objects.create(league=self.league, home_team=team5, home_score=3, away_score=3,
                             away_team=team6, round=2)
        Match.objects.create(league=self.league, home_team=self.team1, home_score=1, away_score=2,
                             away_team=self.team2, round=3)
        self.a.run()

    def test_run_error(self):
        self.a.league = None
        self.a.run()
