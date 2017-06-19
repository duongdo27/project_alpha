from __future__ import unicode_literals

from django.db import models


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