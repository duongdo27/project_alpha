from __future__ import unicode_literals

from django.db import models
from django.db.models import Q


class League(models.Model):
    name = models.CharField(max_length=100)
    year = models.IntegerField()
    parent = models.CharField(max_length=100)
    disposition = models.BooleanField(default=True)

    class Meta:
        unique_together = ("name", "year", "parent")

    def __unicode__(self):
        return "{} {}".format(self.name, self.year)


class Team(models.Model):
    name = models.CharField(max_length=100)
    parent = models.CharField(max_length=100)

    class Meta:
        unique_together = ("name", "parent")

    def __unicode__(self):
        return self.name

    def get_graph_data(self, league):
        matches = Match.objects.filter(league=league)\
            .filter(Q(home_team=self) | Q(away_team=self)).order_by('round')

        rounds = []
        points = []
        current_point = 0
        for match in matches:
            rounds.append(match.round)

            if match.home_score == match.away_score:
                current_point += 1
            elif (match.home_score > match.away_score and match.home_team == self) \
                    or (match.home_score < match.away_score and match.away_team == self):
                current_point += 3
            points.append(current_point)

        return {'rounds': rounds, 'points': points}


class Match(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="home_team")
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="away_team")
    home_score = models.IntegerField()
    away_score = models.IntegerField()
    date = models.DateField(null=True)
    round = models.IntegerField()

    class Meta:
        unique_together = ("league", "home_team", "away_team", "round")

    def __unicode__(self):
        return "{} vs {}".format(self.home_team, self.away_team)

    @classmethod
    def get_match_data(cls, league):
        data = []
        matches = cls.objects.filter(league=league).order_by('round')
        current_round = -1
        for index, match in enumerate(matches):
            if match.round != current_round:
                if current_round != -1:
                    data[-1] = [data[-1], cls.get_standing(matches[:index])]
                data.append([match])
                current_round = match.round
            else:
                data[-1].append(match)
        data[-1] = [data[-1], cls.get_standing(matches)]

        for index in range(len(data)):
            if index == 0:
                data[index][1] = cls.compute_movements(data[index][1], None)
            else:
                data[index][1] = cls.compute_movements(data[index][1], data[index-1][1])
        return data

    @staticmethod
    def compute_movements(standing, previous_standing):
        result = []
        ranks = {value[0]: index
                 for index, value in enumerate(standing)}
        if previous_standing:
            previous_ranks = {value[0]: index
                              for index, value in enumerate(previous_standing)}
        else:
            previous_ranks = ranks

        for team, value in standing:
            if ranks[team] > previous_ranks[team]:
                result.append([team, value, -1])
            elif ranks[team] == previous_ranks[team]:
                result.append([team, value, 0])
            else:
                result.append([team, value, 1])
        return result

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

    @classmethod
    def get_standing(cls, matches):
        data = {}
        for match in matches:
            if match.home_team in data:
                data[match.home_team]['gf'] += match.home_score
                data[match.home_team]['ga'] += match.away_score
            else:
                data[match.home_team] = {
                    'gf': match.home_score,
                    'ga': match.away_score,
                    'points': 0,
                    'won': 0,
                    'drawn': 0,
                    'lost': 0,
                }

            if match.away_team in data:
                data[match.away_team]['gf'] += match.away_score
                data[match.away_team]['ga'] += match.home_score
            else:
                data[match.away_team] = {
                    'gf': match.away_score,
                    'ga': match.home_score,
                    'points': 0,
                    'won': 0,
                    'drawn': 0,
                    'lost': 0,
                }

            if match.home_score > match.away_score:
                data[match.home_team]['points'] += 3
                data[match.home_team]['won'] += 1
                data[match.away_team]['lost'] += 1
            elif match.home_score == match.away_score:
                data[match.home_team]['points'] += 1
                data[match.away_team]['points'] += 1
                data[match.home_team]['drawn'] += 1
                data[match.away_team]['drawn'] += 1
            else:
                data[match.away_team]['points'] += 3
                data[match.home_team]['lost'] += 1
                data[match.away_team]['won'] += 1

        standing = []
        for team, value in data.iteritems():
            value['gd'] = value['gf'] - value['ga']
            standing.append([team, value])

        standing.sort(cls.compare_team)
        return standing


class Info(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    round = models.IntegerField()
    points = models.IntegerField()
    home_won = models.IntegerField()
    home_drawn = models.IntegerField()
    home_lost = models.IntegerField()
    away_won = models.IntegerField()
    away_drawn = models.IntegerField()
    away_lost = models.IntegerField()
    gf = models.IntegerField()
    ga = models.IntegerField()
    gd = models.IntegerField()
    rank = models.IntegerField()
    movement = models.IntegerField()

    @property
    def won(self):
        return self.home_won + self.away_won

    @property
    def drawn(self):
        return self.home_drawn + self.away_drawn

    @property
    def lost(self):
        return self.home_lost + self.away_lost
