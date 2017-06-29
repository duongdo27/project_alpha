from django.contrib import admin

from .models import League, Team, Match, Info


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "year", "disposition")
    list_filter = ("name", "parent", "year", "disposition")


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "parent")
    search_fields = ("name",)
    list_filter = ("parent",)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("__unicode__", "league", "round")
    search_fields = ("home_team__name", "away_team__name", "round")
    list_filter = ("league__name", "league__year")


@admin.register(Info)
class InfoAdmin(admin.ModelAdmin):
    list_display = ("team", "league", "round", "points", "rank", "movement")
    search_fields = ("team__name", "round")
    list_filter = ("league__name", "league__year")



