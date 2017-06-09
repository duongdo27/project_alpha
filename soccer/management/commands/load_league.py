from django.core.management.base import BaseCommand
from soccer.loaders.league_loader import LeagueLoader


class Command(BaseCommand):
    def handle(self, *args, **options):
        LeagueLoader(name="Bundesliga", year=2015, parent="Germany").run()