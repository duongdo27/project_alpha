from soccer.models import League, Match, Team
import requests
from lxml import html
from fuzzywuzzy import fuzz
from datetime import datetime
import re

ABBREV = {
    "England": "tablese/eng",   # done
    "Italy": "tablesi/ital",    # 'cannot not find match'
    "France": "tablesf/fran",   # 'cannot not find match'
    "Spain": "tabless/span",    # 'cannot not find match'
    "Germany": "tablesd/duit",     # cannot find any match  "- - - - - - - - - - - - - - - - - - - - - - - - - - - -"
    "Netherlands": "tablesn/ned",   # Round does not match
    "Vietnam": "tablesv/viet",     # datetime has problem
    "Portugal": "tablesp/port",
    "Russia": "tablesr/rus",       # cannot split because having scorer name besides the result
}


class LeagueLoader(object):
    def __init__(self, name, year, parent):
        self.name = name
        self.year = year
        self.parent = parent

        self.league, _ = League.objects.get_or_create(name=self.name, year=self.year, parent=self.parent)
        Match.objects.filter(league=self.league).delete()
        self.teams = []
        self.matches = []

        self.round = 0
        self.cache_lookup = {}
        self.current_date = None

    def get_raw_text(self):
        if self.year >= 2010:
            url = "http://www.rsssf.com/{}{}.html".format(ABBREV[self.parent], self.year)
        else:
            url = "http://www.rsssf.com/{}{}.html".format(ABBREV[self.parent], str(self.year)[-2:])
        print url
        res = requests.get(url)
        res.encoding = res.apparent_encoding
        tree = html.fromstring(res.text)
        #import ipdb
        #ipdb.set_trace()
        raw_text = ""
        for text in tree.xpath("//pre[1]/text()"):
            raw_text += text.strip() + "\n"
        return raw_text

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
            result = self.read_round_line(line)
            if result:
                self.round += 1
                print self.round
                wrong_round_ls = [("Eredivisie", 2017), ("Ligue 1", 2010)]
                if (self.name, self.year) in wrong_round_ls:
                    continue
                assert self.round == result["round"], "Round does not match"
                continue
            if self.round == 0:
                result = self.read_team_line(line)
                if result:
                    team, _ = Team.objects.get_or_create(name=result["team"], parent=self.parent)
                    self.teams.append(team)
                continue
            if "Final Table" in line:
                return
            self.read_date_line(line)
            result = self.read_match_line(line)
            if result:
                try:
                    match, _ = Match.objects.get_or_create(
                                league=self.league, home_team=result["home_team"], away_team=result["away_team"],
                                home_score=result["home_score"], away_score=result["away_score"], round=self.round,
                                date=self.current_date)
                    self.matches.append(match)
                except:
                    import ipdb
                    ipdb.set_trace()

    def read_round_line(self, line):
        match_obj = re.match(r" ?R?o?(un?|nu)d (?P<round>\d+)(\s+)\[(?P<month>\w+) (?P<day>\d+)\]", line)
        if match_obj:
            self.save_current_date(match_obj.group("month"), match_obj.group("day"))
            return {"round": int(match_obj.group("round"))}

        match_obj = re.match(r" ?R?o?(un?|nu)d (?P<round>\d+)", line)
        if match_obj:
            return {"round": int(match_obj.group("round"))}


    @staticmethod
    def read_team_line(line):
        match_obj = re.match(r" ?((\d+)\. ?)+(?P<team>.+)(\s+\d+){2}(-(\s*\d+)){2}(\s+\d+)-", line)
        if match_obj:
            return {"team": match_obj.group("team").strip()}
        match_obj = re.match(r" ?((\d+)\. ?)+(?P<team>.+)(\s+\d+){5}-", line)
        if match_obj:
            return {"team": match_obj.group("team").strip()}

    def read_match_line(self, line):
        match_obj = re.match(r"(\d+\.?)?(?P<home_team>\D+)(?P<home_score>\d+)-(?P<away_score>\d+)(\s+)(\d+\.?)?(?P<away_team>\D+)", line)
        if match_obj:
            return {
                "home_team": self.find_team_from_name(match_obj.group("home_team").strip()),
                "home_score": match_obj.group("home_score").strip(),
                "away_score": match_obj.group("away_score").strip(),
                "away_team": self.find_team_from_name(match_obj.group("away_team").strip()),
                }

    def save_current_date(self, month, day):
        raw_date = "{} {}".format(month, day)
        if raw_date == "Feb 29":
            self.current_date = datetime(self.year, 2, 29).date()
        wrong_dates_lookup = {"Sug 24": "Aug 24", "Feb 211": "Feb 11", "Jul 120": "Jul 20"}
        correct_date = wrong_dates_lookup.get(raw_date, raw_date)
        the_date = datetime.strptime(correct_date, "%b %d").date()
        if self.name == "VLeague":
            self.current_date = the_date.replace(year=self.year)
        elif the_date.month >= 7:
            self.current_date = the_date.replace(year=self.year-1)
        else:
            self.current_date = the_date.replace(year=self.year)

    def read_date_line(self, line):
        match_obj = re.match(r"\[(?P<month>\w+) (?P<day>\d+)\]", line)
        if match_obj:
            self.save_current_date(match_obj.group("month"), match_obj.group("day"))

    def run(self):
        raw_text = self.get_raw_text()
        self.process_raw_text(raw_text)
        assert self.matches, "Cannot find any match"
