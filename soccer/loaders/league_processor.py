"""
LEAGUE PROCESSOR
"""
from collections import defaultdict
from soccer.models import Info, Match
from copy import deepcopy


class LeagueProcessor(object):
    def __init__(self, league):
        self.league = league

    @staticmethod
    def compute_info(round_data, match):
        round_data[match.home_team]['round'] = match.round
        round_data[match.away_team]['round'] = match.round

        round_data[match.home_team]['gf'] += match.home_score
        round_data[match.home_team]['ga'] += match.away_score
        round_data[match.home_team]['gd'] += match.home_score - match.away_score

        round_data[match.away_team]['round'] = match.round
        round_data[match.away_team]['ga'] += match.home_score
        round_data[match.away_team]['gf'] += match.away_score
        round_data[match.away_team]['gd'] += match.away_score - match.home_score

        if match.home_score > match.away_score:
            round_data[match.home_team]['home_won'] += 1
            round_data[match.home_team]['points'] += 3
            round_data[match.away_team]['away_lost'] += 1
        elif match.home_score == match.away_score:
            round_data[match.home_team]['home_drawn'] += 1
            round_data[match.away_team]['away_drawn'] += 1
            round_data[match.home_team]['points'] += 1
            round_data[match.away_team]['points'] += 1
        else:
            round_data[match.home_team]['home_lost'] += 1
            round_data[match.away_team]['away_won'] += 1
            round_data[match.away_team]['points'] += 3

    @staticmethod
    def compare_team(a, b):
        if a[1]['points'] < b[1]['points']:
            return 1
        if a[1]['points'] > b[1]['points']:
            return -1
        if a[1]['gd'] < b[1]['gd']:
            return 1
        if a[1]['gd'] > b[1]['gd']:
            return -1

        if a[1]['gf'] < b[1]['gf']:
            return 1
        if a[1]['gf'] > b[1]['gf']:
            return -1

        if a[0] > b[0]:
            return 1
        if a[0] < b[0]:
            return -1
        return 0

    def compute_rank(self, orig_round_data, previous_standing):
        round_data = deepcopy(orig_round_data)
        standing = [(team, info) for team, info in round_data.iteritems()]
        standing.sort(self.compare_team)

        for index, (team, info) in enumerate(standing):
            round_data[team]['rank'] = index + 1

            if index + 1 == previous_standing[team] or previous_standing[team] == 0:
                round_data[team]['movement'] = 0
            elif index + 1 > previous_standing[team]:
                round_data[team]['movement'] = -1
            else:
                round_data[team]['movement'] = 1
            previous_standing[team] = index + 1
        return round_data
    
    def save_data(self, data):
        Info.objects.filter(league=self.league).delete()
        
        for round_data in data:
            for team, info in round_data.iteritems():
                Info.objects.create(league=self.league, team=team, round=info['round'],
                                    points=info['points'], home_won=info['home_won'],
                                    home_drawn=info['home_drawn'], home_lost=info['home_lost'],
                                    away_won=info['away_won'], away_drawn=info['away_drawn'],
                                    away_lost=info['away_lost'], gf=info['gf'], ga=info['ga'],
                                    gd=info['gd'], rank=info['rank'], movement=info['movement'])

    def main_run(self):
        """
        :return: Main function
        """
        print 'Process league {}'.format(self.league)
        matches = Match.objects.filter(league=self.league).order_by('round')

        data = []
        current_round = 1
        round_data = {}
        previous_standing = defaultdict(int)

        for match in matches:
            if match.round != current_round:
                data.append(self.compute_rank(round_data, previous_standing))
                current_round = match.round
            else:
                if match.home_team not in round_data:
                    round_data[match.home_team] = defaultdict(int)
                if match.away_team not in round_data:
                    round_data[match.away_team] = defaultdict(int)
            self.compute_info(round_data, match)

        data.append(self.compute_rank(round_data, previous_standing))
        self.save_data(data)

    def run(self):
        """
        :return: Wrapper
        """
        try:
            self.main_run()
        except Exception as e:
            print e
