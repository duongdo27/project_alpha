"""
LEAGUE LOADER
"""
from soccer.models import League, Match, Team
import requests
from lxml import html
from fuzzywuzzy import fuzz
from datetime import datetime
import re

ABBREV = {
    "England": "tablese/eng",
    "Italy": "tablesi/ital",
    "France": "tablesf/fran",
    "Spain": "tabless/span",
    "Germany": "tablesd/duit",
    "Netherlands": "tablesn/ned",
    "Vietnam": "tablesv/viet",
    "Portugal": "tablesp/port",
    "Russia": "tablesr/rus",
}


class LeagueLoader(object):
    def __init__(self, name, year, parent, force_reload=False):
        # Info
        self.name = name
        self.year = year
        self.parent = parent
        self.force_reload = force_reload

        # Data
        self.league = None
        self.teams = []
        self.matches = []

        # Helper variables
        self.round = 0
        self.cache_lookup = {}
        self.current_date = None

    def get_raw_text(self):
        """
        :return: Get raw text from HTML in RSSSF website
        """
        # Construct URL
        if self.year >= 2010:
            url = "http://www.rsssf.com/{}{}.html".format(ABBREV[self.parent], self.year)
        else:
            url = "http://www.rsssf.com/{}{}.html".format(ABBREV[self.parent], str(self.year)[-2:])
        print url

        # Get html, change encoding, convert to tree
        res = requests.get(url)
        res.encoding = res.apparent_encoding
        tree = html.fromstring(res.text)

        # Find league raw text
        raw_text = ""
        for text in tree.xpath("//pre[1]/text()"):
            raw_text += text.strip() + "\n"
        return raw_text

    def find_team_from_name(self, name):
        """
        :param name:
        :return: Find team from the approximate name
        """
        # Check in cache
        if name in self.cache_lookup:
            return self.cache_lookup[name]

        # Fuzzy match name to find best team
        best_ratio = 0
        best_team = None
        for team in self.teams:
            ratio = fuzz.ratio(team.name, name)
            if ratio > best_ratio:
                best_ratio = ratio
                best_team = team

        # Save cache and return
        self.cache_lookup[name] = best_team
        return best_team

    def process_raw_text(self, raw_text):
        """
        :param raw_text:
        :return: Extract info from raw text
        """
        # Read line by line
        for line in raw_text.splitlines():

            # Check if this is the line for round
            result = self.read_round_line(line)
            if result:
                self.round += 1
                print self.round
                wrong_round_ls = [("Eredivisie", 2017), ("Ligue 1", 2010)]
                if (self.name, self.year) in wrong_round_ls:
                    continue
                assert self.round == result["round"], "Round does not match"
                continue

            # Check if this is the line for team
            if self.round == 0:
                result = self.read_team_line(line)
                if result:
                    team, _ = Team.objects.get_or_create(name=result["team"], parent=self.parent)
                    self.teams.append(team)
                continue

            # Return if done
            if "Final Table" in line:
                return

            # Check if this is the line for date
            self.read_date_line(line)

            # Check if this is the line for match
            result = self.read_match_line(line)
            if result:
                match = Match.objects.create(
                        league=self.league, home_team=result["home_team"], away_team=result["away_team"],
                        home_score=result["home_score"], away_score=result["away_score"], round=self.round,
                        date=self.current_date)
                self.matches.append(match)

    def read_round_line(self, line):
        """
        :param line:
        :return: Find round number, and possible date
        """
        # Round and date
        match_obj = re.match(r" ?R?o?(un?|nu)d (?P<round>\d+)(\s+)\[(?P<month>\w+) (?P<day>\d+)\]", line)
        if match_obj:
            self.save_current_date(match_obj.group("month"), match_obj.group("day"))
            return {"round": int(match_obj.group("round"))}

        # Round only
        match_obj = re.match(r" ?R?o?(un?|nu)d (?P<round>\d+)", line)
        if match_obj:
            return {"round": int(match_obj.group("round"))}

    @staticmethod
    def read_team_line(line):
        """
        :param line:
        :return: Find team name
        """
        # Normal case
        match_obj = re.match(r" ?((\d+)\. ?)+(?P<team>.+)(\s+\d+){2}(-(\s*\d+)){2}(\s+\d+)-", line)
        if match_obj:
            return {"team": match_obj.group("team").strip()}

        # Special case
        match_obj = re.match(r" ?((\d+)\. ?)+(?P<team>.+)(\s+\d+){5}-", line)
        if match_obj:
            return {"team": match_obj.group("team").strip()}

    def read_match_line(self, line):
        """
        :param line:
        :return: Find match info
        """
        match_obj = re.match(r"(\d+\.?)?(?P<home_team>\D+)(?P<home_score>\d+)-(?P<away_score>\d+)(\s+)(\d+\.?)?(?P<away_team>\D+)", line)
        if match_obj:
            return {
                "home_team": self.find_team_from_name(match_obj.group("home_team").strip()),
                "home_score": match_obj.group("home_score").strip(),
                "away_score": match_obj.group("away_score").strip(),
                "away_team": self.find_team_from_name(match_obj.group("away_team").strip()),
                }

    def save_current_date(self, month, day):
        """
        :param month:
        :param day:
        :return: Save current date based on month and day
        """
        raw_date = "{} {}".format(month, day)

        # Leaf year for Feb 29
        if raw_date == "Feb 29":
            self.current_date = datetime(self.year, 2, 29).date()

        # Fix dates
        wrong_dates_lookup = {"Sug 24": "Aug 24", "Feb 211": "Feb 11", "Jul 120": "Jul 20"}
        correct_date = wrong_dates_lookup.get(raw_date, raw_date)
        the_date = datetime.strptime(correct_date, "%b %d").date()

        # Fill in corresponding year
        if self.name == "VLeague":
            self.current_date = the_date.replace(year=self.year)
        elif the_date.month >= 7:
            self.current_date = the_date.replace(year=self.year-1)
        else:
            self.current_date = the_date.replace(year=self.year)

    def read_date_line(self, line):
        """
        :param line:
        :return: Find month and day
        """
        match_obj = re.match(r"\[(?P<month>\w+) (?P<day>\d+)\]", line)
        if match_obj:
            self.save_current_date(match_obj.group("month"), match_obj.group("day"))

    def run(self):
        """
        :return: Main function
        """
        # Get or create league
        self.league = League.objects.filter(name=self.name, year=self.year, parent=self.parent).first()
        if self.league and not self.force_reload:
            return
        else:
            self.league = League.objects.create(name=self.name, year=self.year, parent=self.parent)

        raw_text = self.get_raw_text()
        self.process_raw_text(raw_text)
        assert self.matches, "Cannot find any match"
