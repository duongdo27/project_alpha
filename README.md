# Project Alpha
A collection of fun apps I created in my free time. Enjoy!
As simple as other Django apps, after cloning the repo, you can install the required packages with:
```bash
pip install -r requirements.txt
```
And start the app locally with:
```bash
python manage.py runserver
```
It also comes with all the necessary files to be able to host it on Heroku. Here is the [instruction](https://devcenter.heroku.com/articles/deploying-python)

Below are the specific instruction for each component.
# 1. Soccer Leagues
Using raw data from [RSSF website](http://www.rsssf.com), we create an organized structure of soccer leagues from recent years, with detail statistics of each round, as well as overall performance of each team.

The config file of leagues to be loaded is stored in [leagues.yml](soccer/management/commands/leagues.yml). To load leagues into database:
```bash
python manage.py load_league
```
Then to process raw data into useful statistics:
```bash
python manage.py process_league
```
For Heroku, please append `heroku run` in front of each command.
