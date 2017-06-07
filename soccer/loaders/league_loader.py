from soccer.models import League, Match, Team
import requests
from lxml import html
from fuzzywuzzy import fuzz

ABBREV = {"England": "eng"}


class LeagueLoader(object):
    def __init__(self, name, year, parent):
        self.name = name
        self.year = year
        self.parent = parent

        self.league, _ = League.objects.get_or_create(name=self.name, year=self.year, parent=self.parent)
        self.teams = []

        self.round = 0
        self.cache_lookup = {}
        self.date = None

    def get_raw_text(self):
        url = "http://www.rsssf.com/tablese/{}{}.html".format(ABBREV[self.parent], self.year)
        print url
        res = requests.get(url)
        tree = html.fromstring(res.text)
        return tree.xpath("//pre/text()")[0]

    def create_team_from_line(self, line):
        if len(line) > 2 and line[1].isdigit() and line[2] == ".":
            name = line.split("  ")[0][3:]
            team, _ = Team.objects.get_or_create(name=name, parent=self.parent)
            self.teams.append(team)

    def create_match_from_line(self, line):
        if len(line) > 2 and line[1].isdigit() and line[2] == ".":
            return
        if line.startswith("[") and line.endswith("]"):
            self.date = line[1:-1]
            return
        if '-' in line:
            dash_index = line.index("-")
            if line[dash_index - 1].isdigit() and line[dash_index+1].isdigit():
                ls = line.split()
                for index, value in enumerate(ls):
                    if "-" in value:
                        home_score, away_score = value.split("-")
                        home_team = self.find_team_from_name(" ".join(ls[:index]))
                        away_team = self.find_team_from_name(" ".join(ls[index + 1:]))
                        Match.objects.get_or_create(league=self.league, home_team=home_team, away_team=away_team,
                                                    home_score=home_score, away_score=away_score, round=self.round)

    def find_team_from_name(self, name):
        if name in self.cache_lookup:
            return self.cache_lookup[name]

        best_ratio = 0
        best_team = None
        for team in self.teams:
            ratio = fuzz.ratio(team.name, name)
            if ratio > best_ratio:
                best_ratio = ratio
                best_team = team

        self.cache_lookup[name] = best_team
        return best_team

    def process_raw_text(self, raw_text):
        for line in raw_text.splitlines():
            if line.startswith("Round"):
                self.round += 1
            elif self.round == 0:
                self.create_team_from_line(line)
            else:
                self.create_match_from_line(line)

    def run(self):
        raw_text = self.get_raw_text()
        self.process_raw_text(raw_text)