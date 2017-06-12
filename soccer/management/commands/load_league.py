from django.core.management.base import BaseCommand
from soccer.loaders.league_loader import LeagueLoader


class Command(BaseCommand):
    def handle(self, *args, **options):
        #LeagueLoader(name="Ligue 1", year=2010, parent="France").run()
        #LeagueLoader(name="Russian Premier League", year=2010, parent="Russia").run()
        #LeagueLoader(name="Premier League", year=2014, parent="England").run()
        #LeagueLoader(name="Serie A", year=2010, parent="Italy").run()
        #LeagueLoader(name="Liga BBVA", year=2012, parent="Spain").run()
        #LeagueLoader(name="Eredivisie", year=2017, parent="Netherlands").run()
        #LeagueLoader(name="VLeague", year=2012, parent="Vietnam").run()
        #LeagueLoader(name="Liga ZON Sagres", year=2017, parent="Portugal").run()
        #LeagueLoader(name="Bundesliga", year=2011, parent="Germany").run()
