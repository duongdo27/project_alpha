"""
LEAGUE LOADER
"""
from soccer.models import League, Match, Team
import requests
from lxml import html
from fuzzywuzzy import fuzz
from datetime import datetime
import re


class LeagueLoader(object):
    def __init__(self, params):
        self.params = params

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
        if self.params["year"] >= 2010:
            url = "http://www.rsssf.com/{}{}.html".format(self.params["permalink"], self.params["year"])
        else:
            url = "http://www.rsssf.com/{}{}.html".format(self.params["permalink"], str(self.params["year"])[-2:])
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
            ratio = fuzz.ratio(team.name, name) + 50 * int(name in team.name)
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
                if 'wrong_rounds' in self.params:
                    continue    # pragma: no cover
                assert self.round == result["round"], "Round {} does not match".format(self.round)
                continue    # pragma: no cover

            # Check if this is the line for team
            result = self.read_team_line(line)
            if result:
                if self.round == 0:
                    team, _ = Team.objects.get_or_create(name=result["team"], parent=self.params["parent"])
                    self.teams.append(team)
                continue    # pragma: no cover

            # Return if done
            if "Final Table" in line and self.round > 0:
                return

            # Check if this is the line for date
            self.read_date_line(line)

            # Check if this is the line for match
            result = self.read_match_line(line)
            if result:
                result["round"] = self.round
                result["current_date"] = self.current_date
                self.matches.append(result)

    def read_round_line(self, line):
        """
        :param line:
        :return: Find round number, and possible date
        """
        # Round and date
        match_obj = re.match(r" ?(Roudn|Ronud|R?o?un?d) (?P<round>\d+)(\s+)\[(?P<month>\w+) (?P<day>\d+)\]", line)
        if match_obj:
            self.save_current_date(match_obj.group("month"), match_obj.group("day"))
            return {"round": int(match_obj.group("round"))}

        # Round only
        match_obj = re.match(r" ?(Roudn|Ronud|R?o?un?d) (?P<round>\d+)", line)
        if match_obj:
            return {"round": int(match_obj.group("round"))}

    @staticmethod
    def read_team_line(line):
        """
        :param line:
        :return: Find team name
        """
        # Special case
        match_obj = re.match(r" ?(\d+\. ?)+(?P<team>.+)(\s+\d+){2}(-(\s*\d+)){2}(\s+\d+)-", line)
        if match_obj:
            return {"team": match_obj.group("team").strip()}

        # Normal case
        match_obj = re.match(r" ?(\d+\. ?)+(?P<team>.+)(\s+\d+){5}-", line)
        if match_obj:
            return {"team": match_obj.group("team").strip()}

    def read_match_line(self, line):
        """
        :param line:
        :return: Find match info
        """
        if '[abandoned' in line.lower() or '[awarded' in line.lower() or '[technical' in line.lower():
            return
        if line.strip().startswith('['):
            return
        line = line.replace('1.', '').replace(u'\u2013', '-').strip()

        match_obj = re.match(r"(?P<home_team>.+)(\s+)(?P<home_score>\d+)-"
                             r"(?P<away_score>\d+)(\s+)(?P<away_team>.+)", line)
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
            self.current_date = datetime(self.params["year"], 2, 29).date()
            return

        # Fix dates
        if 'wrong_dates' in self.params:
            correct_date = self.params['wrong_dates'].get(raw_date, raw_date)
        else:
            correct_date = raw_date
        the_date = datetime.strptime(correct_date, "%b %d").date()

        # Fill in corresponding year
        if 'within_year' in self.params:
            self.current_date = the_date.replace(year=self.params["year"])
        elif the_date.month >= 7:
            self.current_date = the_date.replace(year=self.params["year"]-1)
        else:
            self.current_date = the_date.replace(year=self.params["year"])

    def read_date_line(self, line):
        """
        :param line:
        :return: Find month and day
        """
        match_obj = re.match(r"\[(?P<month>\w+) (?P<day>\d+)\]", line)
        if match_obj:
            self.save_current_date(match_obj.group("month"), match_obj.group("day"))

    def process_awarded_matches(self):
        """
        :return: Process awarded matches
        """
        if 'awarded_matches' not in self.params:
            return
        for award_match in self.params['awarded_matches']:
            result = self.read_match_line(award_match['line'])
            result["round"] = award_match['round']
            self.read_date_line("[{}]".format(award_match['current_date']))
            result["current_date"] = self.current_date
            self.matches.append(result)

    def main_run(self):
        """
        :return: Main function
        """
        # Get or create league
        self.league = League.objects.filter(name=self.params["name"], year=self.params["year"],
                                            parent=self.params["parent"]).first()
        if self.league:
            if self.league.disposition:
                print 'League {} {} is already loaded'.format(self.params["name"], self.params["year"])
                return
        else:
            self.league = League.objects.create(name=self.params["name"], year=self.params["year"],
                                                parent=self.params["parent"], disposition=False)

        # Process raw text
        raw_text = self.get_raw_text()
        self.process_raw_text(raw_text)
        self.process_awarded_matches()

        # Decide result
        assert len(self.matches) > 0, 'League {} {} has no match'.format(self.params["name"], self.params["year"])
        assert len(self.matches) == self.params["matches"], 'League {} {} has incorrect number of matches'\
            .format(self.params["name"], self.params["year"])
        Match.objects.filter(league=self.league).delete()
        for result in self.matches:
            Match.objects.create(
                league=self.league, home_team=result["home_team"], away_team=result["away_team"],
                home_score=result["home_score"], away_score=result["away_score"], round=result["round"],
                date=result["current_date"])

        print 'League {} {} load successfully'.format(self.params["name"], self.params["year"])
        self.league.disposition = True
        self.league.save()

    def run(self):
        """
        :return: Wrapper
        """
        try:
            self.main_run()
        except Exception as e:
            print e