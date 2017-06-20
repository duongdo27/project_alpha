from django.core.management.base import BaseCommand
from soccer.loaders.league_loader import LeagueLoader
import yaml
import os


class Command(BaseCommand):
    def handle(self, *args, **options):
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'leagues.yml')
        with open(path) as f:
            data = yaml.load(f)
        for params in data:
            LeagueLoader(params).run()
