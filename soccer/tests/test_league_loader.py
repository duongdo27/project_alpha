from django.test import TestCase
from datetime import date
import mock

from ..loaders.league_loader import LeagueLoader
from ..models import Team, Match, League

SAMPLE_RAW_TEXT = """
Final Table
 1. Borussia Dortmund            34  24  6  4  82-34  78
 2. Bayer Leverkusen             34  24  6  4  82-34  78

Round 1
[May 1]
Dortmund 2-1 Leverkusen

Round 2
[May 7]
Leverkusen 3-4 Dortmund

Final Table
 1. Borussia Dortmund            34  24  6  4  82-34  78
 2. Bayer Leverkusen             34  24  6  4  82-34  78
"""


class LeagueLoaderTest(TestCase):
    def setUp(self):
        self.a = LeagueLoader({'year': 2000, 'permalink': 'tablesd/duit',
                               'name': 'Bundesliga', 'parent': "Germany", 'matches': 2})
        self.team1 = Team.objects.create(name="Borussia Dortmund", parent="Germany")
        self.team2 = Team.objects.create(name="Bayer Leverkusen", parent="Germany")
        self.a.teams = [self.team1, self.team2]

    def test_find_team_from_name(self):
        self.assertEqual(self.a.find_team_from_name('Dortmund'), self.team1)
        self.assertEqual(self.a.find_team_from_name('Leverkusen'), self.team2)

    def test_read_round_line(self):
        self.assertEqual(self.a.read_round_line('Round 11 [May 8]'),
                         {'round': 11})
        self.assertEqual(self.a.current_date, date(2000, 5, 8))

        self.assertEqual(self.a.read_round_line('Round 11'),
                         {'round': 11})
        self.assertEqual(self.a.read_round_line('Roud 11'),
                         {'round': 11})
        self.assertEqual(self.a.read_round_line('Ronud 11'),
                         {'round': 11})
        self.assertEqual(self.a.read_round_line('ound 11'),
                         {'round': 11})
        self.assertEqual(self.a.read_round_line('Roudn 11'),
                         {'round': 11})

    def test_read_team_line(self):
        line = ' 1.Leicester City          38  23 12  3  68-36  81  Champions'
        self.assertEqual(LeagueLoader.read_team_line(line),
                         {'team': 'Leicester City'})

        line = ' 1.1. Leicester City          38  23 12  3  68-36  81'
        self.assertEqual(LeagueLoader.read_team_line(line),
                         {'team': 'Leicester City'})

        line = '10. Mainz 05          38  23 12  3  68-36  81'
        self.assertEqual(LeagueLoader.read_team_line(line),
                         {'team': 'Mainz 05'})

        line = '10. 1899 Hoffenhem          38  23 12  3  68-36  81'
        self.assertEqual(LeagueLoader.read_team_line(line),
                         {'team': '1899 Hoffenhem'})

        line = ' 2. Bayer Leverkusen      34 20- 8- 6  64-44  68'
        self.assertEqual(LeagueLoader.read_team_line(line),
                         {'team': 'Bayer Leverkusen'})

        line = '13. Werder Bremen         34 10-11-13  47-61  41'
        self.assertEqual(LeagueLoader.read_team_line(line),
                         {'team': 'Werder Bremen'})

    def test_read_match_line(self):
        line = "Borussia Dortmund    0-2  Bayer Leverkusen"
        self.assertEqual(self.a.read_match_line(line),
                         {'home_team': self.team1, 'home_score': '0', 'away_score': '2', 'away_team': self.team2})
        line = "1.Borussia Dortmund    0-2  1.Bayer Leverkusen"
        self.assertEqual(self.a.read_match_line(line),
                         {'home_team': self.team1, 'home_score': '0', 'away_score': '2', 'away_team': self.team2})
        line = u"Borussia Dortmund    0\u20132  Bayer Leverkusen"
        self.assertEqual(self.a.read_match_line(line),
                         {'home_team': self.team1, 'home_score': '0', 'away_score': '2', 'away_team': self.team2})

        line = "Borussia Dortmund    0-2  Bayer Leverkusen  [awarded 0-3"
        self.assertIsNone(self.a.read_match_line(line))
        line = "Borussia Dortmund    0-2  Bayer Leverkusen  [abandoned 0-3"
        self.assertIsNone(self.a.read_match_line(line))
        line = "Borussia Dortmund    0-2  Bayer Leverkusen  [Technical 0-3"
        self.assertIsNone(self.a.read_match_line(line))
        line = "[Test Borussia Dortmund    0-2  Bayer Leverkusen"
        self.assertIsNone(self.a.read_match_line(line))

    def test_read_date_line(self):
        self.a.read_date_line("[Apr 12]")
        self.assertEqual(self.a.current_date, date(2000, 4, 12))

    def test_save_current_date(self):
        self.a.save_current_date("Apr", "12")
        self.assertEqual(self.a.current_date, date(2000, 4, 12))

        self.a.save_current_date("Feb", "29")
        self.assertEqual(self.a.current_date, date(2000, 2, 29))

        self.a.params['wrong_dates'] = {"Feb 112": "Feb 11"}
        self.a.save_current_date("Feb", "112")
        self.assertEqual(self.a.current_date, date(2000, 2, 11))

        self.a.save_current_date("Aug", "12")
        self.assertEqual(self.a.current_date, date(1999, 8, 12))

        self.a.params['within_year'] = True
        self.a.save_current_date("Feb", "11")
        self.assertEqual(self.a.current_date, date(2000, 2, 11))

    def test_process_awarded_matches(self):
        self.assertIsNone(self.a.process_awarded_matches())

        self.a.params['awarded_matches'] = [
            {'round': 4, 'line': 'Dortmund 0-3 Leverkusen', 'current_date': 'Sep 23'}]

        self.a.process_awarded_matches()
        self.assertEqual(self.a.current_date, date(1999, 9, 23))
        self.assertEqual(self.a.matches[-1],
                         {'home_team': self.team1, 'away_team': self.team2,
                          'current_date': date(1999, 9, 23), 'home_score': u'0', 'away_score': u'3', 'round': 4})

    @mock.patch('requests.get')
    def test_get_raw_text(self, mock_get):
        mock_get.return_value.text = """
            <html>
                <h1>Soccer</h1>
                <pre>Hello World</pre>
            </html>
        """
        self.assertEqual(self.a.get_raw_text(), "Hello World\n")

        self.a.params['year'] = 2014
        self.assertEqual(self.a.get_raw_text(), "Hello World\n")

    def test_process_raw_text(self):
        self.a.process_raw_text(SAMPLE_RAW_TEXT)
        self.assertEqual(self.a.round, 2)
        self.assertEqual(self.a.matches[0],
                         {'home_team': self.team1, 'away_team': self.team2, 'current_date': date(2000, 5, 1),
                          'home_score': u'2', 'away_score': u'1', 'round': 1})
        self.assertEqual(self.a.matches[1],
                         {'home_team': self.team2, 'away_team': self.team1, 'current_date': date(2000, 5, 7),
                          'home_score': u'3', 'away_score': u'4', 'round': 2})

        self.a.params['wrong_rounds'] = True
        self.a.process_raw_text(SAMPLE_RAW_TEXT)

    @mock.patch('requests.get')
    def test_run(self, mock_get):
        mock_get.return_value.text = """
            <html>
                <h1>Soccer</h1>
                <pre>{}</pre>
            </html>
        """.format(SAMPLE_RAW_TEXT)
        self.a.run()

        matches = Match.objects.filter(league=self.a.league).order_by('round')
        self.assertEqual(matches[0].home_team, self.team1)
        self.assertEqual(matches[0].away_team, self.team2)
        self.assertEqual(matches[0].home_score, 2)
        self.assertEqual(matches[0].away_score, 1)
        self.assertEqual(matches[0].date, date(2000, 5, 1))
        self.assertEqual(matches[0].round, 1)

        self.assertEqual(matches[1].home_team, self.team2)
        self.assertEqual(matches[1].away_team, self.team1)
        self.assertEqual(matches[1].home_score, 3)
        self.assertEqual(matches[1].away_score, 4)
        self.assertEqual(matches[1].date, date(2000, 5, 7))
        self.assertEqual(matches[1].round, 2)

    def test_run_already_loaded(self):
        self.a.league = League.objects.create(name='Bundesliga', parent="Germany",
                                              year=2000, disposition=True)
        self.a.run()

    def test_run_error(self):
        self.a.params = {}
        self.a.run()