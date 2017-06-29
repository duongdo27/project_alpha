from django.core.management.base import BaseCommand
from soccer.loaders.league_processor import LeagueProcessor

from ...models import League


class Command(BaseCommand):
    def handle(self, *args, **options):
        leagues = League.objects.all()
        for league in leagues:
            LeagueProcessor(league).run()
