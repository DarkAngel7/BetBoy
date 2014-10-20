# -*- coding: utf-8 -*-
"""
 The MIT License (MIT)

Copyright (c) 2014 Jacek Markowski

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from data.sql_core import models
from data.sql_core.models import Team, TeamStats, LastMatches, Series


def create_tables():
    models.db.connect()
    models.db.create_tables([Team, TeamStats,
                             LastMatches, Series], safe=True)


def fill_tables(csv_db):
    put_teams_into_table(csv_db)
    update_team_stats(csv_db)


def get_teams_from_csv(csv_db):
    query_home = csv_db.select(csv_db.team_home)
    query_away = csv_db.select(csv_db.team_away)
    teams_home = set([i.team_home for i in query_home])
    teams_away = set([i.team_away for i in query_away])
    return teams_home | teams_away


def put_teams_into_table(csv_db):
    teams = get_teams_from_csv(csv_db)
    for team in teams:
        t = Team.create(name=team)
        TeamStats.create(team=t)


def update_team_stats(csv_db):
    q = csv_db.select(csv_db.date, csv_db.team_home, csv_db.team_away,
                      csv_db.g_home, csv_db.g_away,
                      csv_db.odds_home, csv_db.odds_draw,
                      csv_db.odds_away).distinct().order_by(csv_db.date.asc())
    for i in q:
        home = Team.get(name=i.team_home)
        away = Team.get(name=i.team_away)
        update_basic_stats(home, away, i.g_home, i.g_away)


def check_result(g_home, g_away):
    if g_home == -1 or g_away == -1:
        result = -1
    elif g_home == g_away:
        result = 0
    elif g_home > g_away:
        result = 1
    elif g_home < g_away:
        result = 2

    return result


def update_basic_stats(home, away, g_home, g_away):
    result = check_result(g_home, g_away)
    if result == 0:
        update_draw(home, g_home, g_away)
        update_draw(away, g_away, g_home)
    if result == 1:
        update_winner(home, g_home, g_away)
        update_loser(away, g_away, g_home)
    if result == 2:
        update_loser(home, g_home, g_away)
        update_winner(away, g_away, g_home)


def update_winner(team, g_scored, g_lost):
    TeamStats.\
        update(wins=TeamStats.wins + 1,
               goals_scored=TeamStats.goals_scored + g_scored,
               goals_lost=TeamStats.goals_lost + g_lost).\
        where(TeamStats.team == team).execute()


def update_draw(team, g_scored, g_lost):
    TeamStats.\
        update(draws=TeamStats.draws + 1,
               goals_scored=TeamStats.goals_scored + g_scored,
               goals_lost=TeamStats.goals_lost + g_lost).\
        where(TeamStats.team == team).execute()


def update_loser(team, g_scored, g_lost):
    TeamStats.\
        update(loses=TeamStats.loses + 1,
               goals_scored=TeamStats.goals_scored + g_scored,
               goals_lost=TeamStats.goals_lost + g_lost).\
        where(TeamStats.team == team).execute()






