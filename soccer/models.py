from __future__ import unicode_literals

from django.db import models
from django.db.models import Q, Max


class League(models.Model):
    name = models.CharField(max_length=100)
    year = models.IntegerField()
    parent = models.CharField(max_length=100)
    disposition = models.BooleanField(default=True)

    class Meta:
        unique_together = ("name", "year", "parent")

    def __unicode__(self):
        return "{} {}".format(self.name, self.year)

    def get_league_data(self):
        data = []
        max_round = Match.objects.filter(league=self).aggregate(Max('round'))['round__max']
        for round in range(1, max_round+1):
            data.append((Match.objects.filter(league=self, round=round),
                         Info.objects.filter(league=self, round=round).order_by('rank')))
        return data


class Team(models.Model):
    name = models.CharField(max_length=100)
    parent = models.CharField(max_length=100)

    class Meta:
        unique_together = ("name", "parent")

    def __unicode__(self):
        return self.name

    def get_graph_data(self, league):
        infos = Info.objects.filter(league=league, team=self).order_by('round')

        rounds = []
        points = []
        ranks = []
        for info in infos:
            rounds.append(info.round)
            points.append(info.points)
            ranks.append(info.rank)

        return {'rounds': rounds,
                'points': points,
                'ranks': ranks}


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
