from django.core.management.base import BaseCommand
from soccer.loaders.league_loader import LeagueLoader


class Command(BaseCommand):
    def handle(self, *args, **options):
        LeagueLoader(name="Premier League", year=2016, parent="England").run()